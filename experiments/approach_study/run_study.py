"""Run the extraction approach study described in PLAN.md.

Usage (networkx needs Python 3.13 here, see JOURNAL.md):
  uv run --no-project --python 3.13 --with anthropic,pyyaml,networkx \
      python experiments/approach_study/run_study.py [--budget 60] [--pilot 2]

Outputs go to data/approach_study/ (git-ignored: they hold HC3 and microtext text).
Finished outputs are reused, so the script can be stopped and resumed.
"""
import argparse
import hashlib
import json
import random
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import anthropic
import networkx as nx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.extract import build_system_prompt, build_user_prompt, load_dotenv, retry_prompt  # noqa: E402
from src.schema import load_schema, read_yaml, write_yaml  # noqa: E402
from src.validate import coverage_errors, validate  # noqa: E402

OUT = ROOT / "data" / "approach_study"
PROMPTS = ROOT / "prompts"
HC3_FILE = ROOT / "data" / "finance-filtered.jsonl"
MICRO_FILE = ROOT / "data" / "external" / "argmicro_en_sample20.jsonl"
SEED = 2026
OPUS, SONNET = "claude-opus-5-5", "claude-sonnet-5-5"
EFFORT = "high"
N_VOTES = 5
# $ per million tokens: input, output, cache read, cache write.
PRICES = {OPUS: (4.0, 20.0, 0.20, 5.0), SONNET: (2.0, 10.0, 0.20, 2.5)}

SCHEMA = load_schema()


# --------------------------------------------------------------------------- budget and calls


class BudgetExceeded(Exception):
    pass


class Budget:
    def __init__(self, cap: float):
        self.cap, self.spent, self.lock = cap, 0.0, threading.Lock()

    def check(self):
        with self.lock:
            if self.spent >= self.cap:
                raise BudgetExceeded(f"budget ${self.cap:.2f} reached")

    def add(self, cost: float):
        with self.lock:
            self.spent += cost


BUDGET = Budget(60.0)
_client = None


def client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(max_retries=6)
    return _client


def cost_of(model: str, u) -> float:
    p_in, p_out, p_cr, p_cw = PRICES.get(model, PRICES[OPUS])
    return ((u.input_tokens or 0) * p_in + (u.output_tokens or 0) * p_out
            + (u.cache_read_input_tokens or 0) * p_cr + (u.cache_creation_input_tokens or 0) * p_cw) / 1e6


def call(system: str, user: str, json_schema: dict, model: str) -> tuple[dict, dict]:
    """One structured-output call. Returns (parsed output, usage record). Raises on failure."""
    BUDGET.check()
    t0 = time.time()
    with client().beta.messages.stream(
        model=model,
        max_tokens=64000,
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user}],
        output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": json_schema}},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    ) as stream:
        msg = stream.get_final_message()
    u = msg.usage
    cost = cost_of(msg.model, u)
    BUDGET.add(cost)
    usage = {"model": msg.model, "message_id": msg.id, "stop_reason": msg.stop_reason,
             "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
             "cache_read": u.cache_read_input_tokens, "cache_write": u.cache_creation_input_tokens,
             "cost_usd": round(cost, 5), "seconds": round(time.time() - t0, 1)}
    if msg.stop_reason != "end_turn":
        raise RuntimeError(f"stop_reason={msg.stop_reason} ({msg.id})")
    text = next(b.text for b in msg.content if b.type == "text")
    return json.loads(text), usage


# --------------------------------------------------------------------------- prompts and output schemas


def fill(template: str) -> str:
    return build_system_prompt(PROMPTS / template, SCHEMA)


SYS = {name: fill(f"{name}.md") for name in ["extract_v2", "segment_v1", "label_v1", "type_v1", "link_v1"]}

FULL_SCHEMA = SCHEMA.output_json_schema()
_node = json.loads(json.dumps(FULL_SCHEMA["properties"]["nodes"]["items"]))
_node["properties"].pop("text")
_node["required"].remove("text")
_edge = FULL_SCHEMA["properties"]["edges"]["items"]


def obj(props: dict) -> dict:
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


OUT_SCHEMA = {
    "extract": FULL_SCHEMA,
    "segment": obj({"segments": {"type": "array", "items": {"type": "string"}}}),
    "label": obj({"nodes": {"type": "array", "items": _node}, "edges": {"type": "array", "items": _edge},
                  "implicit_main": {"type": "boolean"}}),
    "type": obj({"nodes": {"type": "array", "items": _node}, "implicit_main": {"type": "boolean"}}),
    "link": obj({"edges": {"type": "array", "items": _edge}}),
}


def pieces_prompt(item: dict, segments: list[str], nodes: list[dict] | None = None) -> str:
    lines = []
    for i, s in enumerate(segments, 1):
        tag = ""
        if nodes:
            n = next((x for x in nodes if x["id"] == i), None)
            if n:
                tag = f"[{n['type']}{', MAIN' if n.get('main') else ''}] "
        lines.append(f"{i}. {tag}{s}")
    return build_user_prompt(item["question"], item["text"]) + "\n\n<pieces>\n" + "\n".join(lines) + "\n</pieces>"


def with_text(nodes: list[dict], segments: list[str]) -> list[dict]:
    """Put each piece's text back on its node (the label calls return no text)."""
    out = []
    for n in nodes:
        i = n["id"]
        out.append({**n, "text": segments[i - 1] if isinstance(i, int) and 1 <= i <= len(segments) else ""})
    return out


# --------------------------------------------------------------------------- data


def hc3_items() -> list[dict]:
    rows = [json.loads(line) for line in HC3_FILE.read_text().splitlines() if line.strip()]
    pairs = sorted(random.Random(SEED).sample(range(len(rows)), 10))
    items = []
    for i in pairs:
        for src, key in (("human", "human_answers"), ("chatgpt", "chatgpt_answers")):
            items.append({"id": f"finance_{i:04d}_{src}", "dataset": "hc3", "source": src, "pair": i,
                          "question": rows[i]["question"], "text": rows[i][key][0]})
    return items


def micro_items() -> list[dict]:
    items = []
    for line in MICRO_FILE.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            items.append({"id": r["id"], "dataset": "micro", "source": "micro", "question": r["question"],
                          "text": r["text"], "gold_segments": [n["text"] for n in r["nodes"]]})
    return items


# --------------------------------------------------------------------------- stage 1: segmentation (shared by S, V, P)


def segment(item: dict) -> dict:
    path = OUT / item["dataset"] / "segments" / f"{item['id']}.yaml"
    if path.exists():
        return read_yaml(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if "gold_segments" in item:
        rec = {"id": item["id"], "status": "gold", "segments": item["gold_segments"], "calls": []}
        write_yaml(path, rec)
        return rec
    user = build_user_prompt(item["question"], item["text"])
    rec = {"id": item["id"], "status": "error", "segments": [], "calls": [], "errors": []}
    prompt = user
    for _ in range(2):
        try:
            out, usage = call(SYS["segment_v1"], prompt, OUT_SCHEMA["segment"], OPUS)
        except BudgetExceeded:
            raise
        except Exception as exc:
            rec["calls"].append({"error": f"{type(exc).__name__}: {exc}"})
            continue
        rec["calls"].append(usage)
        segs = out["segments"]
        errs = coverage_errors(item["text"], segs) + (["empty piece"] if any(not s.strip() for s in segs) else [])
        rec.update(segments=segs, errors=errs, status="valid" if not errs else "invalid")
        if not errs:
            break
        prompt = (f"{user}\n\nYour previous split broke these rules:\n" + "\n".join(f"- {e}" for e in errs)
                  + f"\n\nPrevious split:\n{json.dumps(segs, ensure_ascii=False)}\n\nSplit the whole answer again.")
    path.parent.mkdir(parents=True, exist_ok=True)
    write_yaml(path, rec)
    return rec


# --------------------------------------------------------------------------- approaches


def run_A(item, model):
    """One pass: split, type and link in one call; one retry with validator feedback."""
    calls, out, errs = [], None, ["not run"]
    user = build_user_prompt(item["question"], item["text"])
    prompt = user
    for _ in range(2):
        try:
            out, usage = call(SYS["extract_v2"], prompt, OUT_SCHEMA["extract"], model)
        except BudgetExceeded:
            raise
        except Exception as exc:
            calls.append({"error": f"{type(exc).__name__}: {exc}"})
            continue
        calls.append(usage)
        errs = validate(out, item["text"], SCHEMA)
        if not errs:
            break
        prompt = retry_prompt(user, out, errs)
    return out, errs, calls


def label_once(item, segs, retries):
    calls, graph, errs = [], None, ["not run"]
    user = pieces_prompt(item, segs)
    prompt = user
    for _ in range(retries + 1):
        try:
            out, usage = call(SYS["label_v1"], prompt, OUT_SCHEMA["label"], OPUS)
        except BudgetExceeded:
            raise
        except Exception as exc:
            calls.append({"error": f"{type(exc).__name__}: {exc}"})
            continue
        calls.append(usage)
        graph = {"nodes": with_text(out["nodes"], segs), "edges": out["edges"], "implicit_main": out["implicit_main"]}
        errs = validate(graph, item["text"], SCHEMA)
        if not errs:
            break
        prompt = retry_prompt(user, out, errs)
    return graph, errs, calls


def run_S(item, segs):
    """Two stages: fixed split, then type and link in one call; one retry."""
    return label_once(item, segs, retries=1)


def run_P(item, segs):
    """Step by step: fixed split, then a type call, then a link call; one retry of the link call."""
    calls = []
    try:
        typed, usage = call(SYS["type_v1"], pieces_prompt(item, segs), OUT_SCHEMA["type"], OPUS)
    except BudgetExceeded:
        raise
    except Exception as exc:
        return None, [f"{type(exc).__name__}: {exc}"], [{"error": str(exc)}]
    calls.append(usage)
    nodes = with_text(typed["nodes"], segs)
    user = pieces_prompt(item, segs, nodes)
    prompt, graph, errs = user, None, ["not run"]
    for _ in range(2):
        try:
            out, usage = call(SYS["link_v1"], prompt, OUT_SCHEMA["link"], OPUS)
        except BudgetExceeded:
            raise
        except Exception as exc:
            calls.append({"error": f"{type(exc).__name__}: {exc}"})
            continue
        calls.append(usage)
        graph = {"nodes": nodes, "edges": out["edges"], "implicit_main": typed["implicit_main"]}
        errs = validate(graph, item["text"], SCHEMA)
        if not errs:
            break
        prompt = retry_prompt(user, out, errs)
    return graph, errs, calls


def majority(values, default=None):
    """Most common value; ties go to the value seen first."""
    if not values:
        return default
    counts = Counter(values)
    best = max(counts.values())
    return next(v for v in values if counts[v] == best)


def aggregate(samples: list[dict], segs: list[str]) -> tuple[dict, dict]:
    """Combine label samples: majority type and main, then the best primary tree from parent votes."""
    n = len(segs)
    ids = list(range(1, n + 1))
    nodes_by = [{x["id"]: x for x in s["nodes"]} for s in samples]
    main = majority([next((x["id"] for x in s["nodes"] if x.get("main")), None) for s in samples])
    nodes = []
    for i in ids:
        cands = [nb[i] for nb in nodes_by if i in nb]
        t = majority([c["type"] for c in cands], "other")
        same = [c for c in cands if c["type"] == t]
        nodes.append({"id": i, "type": t, "main": i == main, "hedged": majority([c["hedged"] for c in cands], False),
                      "kind": majority([c["kind"] for c in same]) if t == "evidence" else None,
                      "note": next((c["note"] for c in same if c.get("note")), "majority vote of samples")
                      if t == "other" else None,
                      "text": segs[i - 1]})
    if main is None:
        return {"nodes": nodes, "edges": [], "implicit_main": True}, {"no_main": True}
    graph_ids = [x["id"] for x in nodes if x["type"] not in SCHEMA.non_node_types]
    parent_votes = defaultdict(Counter)   # child -> parent -> votes (primary edges)
    edge_votes = defaultdict(Counter)     # (from, to) -> relation -> votes (any edge)
    for s in samples:
        for e in s["edges"]:
            edge_votes[(e["from"], e["to"])][e["type"]] += 1
            if e.get("primary"):
                parent_votes[e["from"]][e["to"]] += 1
    g = nx.DiGraph()
    g.add_nodes_from(graph_ids)
    for c in graph_ids:
        if c == main:
            continue
        for p in graph_ids:
            if p != c:
                # Small bonus for the main claim keeps zero-vote fallbacks short; votes dominate.
                g.add_edge(p, c, weight=parent_votes[c][p] + (1e-3 if p == main else 1e-6))
    tree = nx.maximum_spanning_arborescence(g, attr="weight", preserve_attrs=True)
    edges, zero_vote, confidence = [], 0, {}
    for p, c in tree.edges:
        votes = parent_votes[c][p]
        zero_vote += votes == 0
        confidence[c] = votes / len(samples)
        rels = [r for r in edge_votes[(c, p)].elements() if r not in SCHEMA.never_primary]
        if not rels:  # no sample drew this edge: use the child's most common primary relation
            rels = [e["type"] for s in samples for e in s["edges"]
                    if e["from"] == c and e.get("primary") and e["type"] not in SCHEMA.never_primary] or ["supports"]
        edges.append({"from": c, "to": p, "type": majority(rels), "primary": True})
    chosen = {(e["from"], e["to"]) for e in edges}
    need = len(samples) // 2 + 1
    for (a, b), rels in edge_votes.items():
        if (a, b) in chosen or a not in graph_ids or b not in graph_ids or a == b:
            continue
        if sum(rels.values()) >= need:
            edges.append({"from": a, "to": b, "type": majority(list(rels.elements())), "primary": False})
    edges.sort(key=lambda e: (e["from"], not e["primary"], e["to"]))
    diag = {"zero_vote_primary_edges": zero_vote, "parent_confidence": confidence}
    return {"nodes": nodes, "edges": edges, "implicit_main": False}, diag


def run_V(item, segs):
    """Two stages with voting: fixed split, N label samples, majority types, best tree from votes."""
    samples, calls, sample_valid = [], [], 0
    for _ in range(N_VOTES):
        graph, errs, c = label_once(item, segs, retries=0)
        calls += c
        if graph is not None:
            samples.append(graph)
            sample_valid += not errs
    if not samples:
        return None, ["no sample returned"], calls, {}
    graph, diag = aggregate(samples, segs)
    diag.update(samples=len(samples), samples_valid=sample_valid)
    return graph, validate(graph, item["text"], SCHEMA), calls, diag


# --------------------------------------------------------------------------- task runner


def run_task(item, approach, rep, seg_rec):
    path = OUT / item["dataset"] / approach / f"rep{rep}" / f"{item['id']}.yaml"
    if path.exists():
        return read_yaml(path)
    diag = {}
    segs = seg_rec["segments"] if seg_rec else None
    if approach in ("S", "V", "P") and (not seg_rec or seg_rec["status"] not in ("valid", "gold")):
        graph, errs, calls = None, ["stage-1 split failed"], []
    elif approach == "A":
        graph, errs, calls = run_A(item, OPUS)
    elif approach == "A-son":
        graph, errs, calls = run_A(item, SONNET)
    elif approach == "S":
        graph, errs, calls = run_S(item, segs)
    elif approach == "P":
        graph, errs, calls = run_P(item, segs)
    elif approach == "V":
        graph, errs, calls, diag = run_V(item, segs)
    else:
        raise ValueError(approach)
    status = "error" if graph is None else ("valid" if not errs else "invalid")
    rec = {"id": item["id"], "dataset": item["dataset"], "source": item["source"], "approach": approach, "rep": rep,
           "status": status, "errors": errs, "cost_usd": round(sum(c.get("cost_usd", 0) for c in calls), 5),
           "n_calls": len(calls), "implicit_main": (graph or {}).get("implicit_main", False),
           "nodes": (graph or {}).get("nodes", []), "edges": (graph or {}).get("edges", []),
           "diagnostics": diag, "calls": calls}
    path.parent.mkdir(parents=True, exist_ok=True)
    write_yaml(path, rec)
    return rec


def spent_so_far() -> float:
    """Total cost of every call saved so far, so the cap covers the whole study, not one session."""
    total = 0.0
    for f in OUT.rglob("*.yaml"):
        if f.name.startswith("manifest"):
            continue
        for c in (read_yaml(f) or {}).get("calls", []):
            total += c.get("cost_usd", 0) or 0
    return total


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=60.0)
    ap.add_argument("--pilot", type=int, default=0, help="only the first N items of each dataset")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--hc3-reps", type=int, default=2)
    args = ap.parse_args()
    load_dotenv()
    BUDGET.cap = args.budget
    BUDGET.spent = spent_so_far()
    print(f"Already spent in earlier sessions: ${BUDGET.spent:.2f} of ${args.budget:.2f}")

    hc3, micro = hc3_items(), micro_items()
    if args.pilot:
        hc3, micro = hc3[:args.pilot], micro[:args.pilot]
    approaches = ["A", "A-son", "S", "V", "P"]

    print(f"Stage 1: splitting {len(hc3)} HC3 texts; microtexts use the gold split")
    seg = {}
    with ThreadPoolExecutor(args.workers) as pool:
        for rec in pool.map(segment, hc3 + micro):
            seg[rec["id"]] = rec
    print(f"  split status: {Counter(r['status'] for r in seg.values())}  spent ${BUDGET.spent:.2f}")

    # Order: microtexts (accuracy) and HC3 rep 1 first, so a budget stop still leaves complete comparisons.
    tasks = [(it, a, 1) for it in micro for a in approaches]
    tasks += [(it, a, r) for r in range(1, args.hc3_reps + 1) for it in hc3 for a in approaches]
    done, stopped = Counter(), 0
    with ThreadPoolExecutor(args.workers) as pool:
        futs = {pool.submit(run_task, it, a, r, seg.get(it["id"])): (it["id"], a, r) for it, a, r in tasks}
        for fut in as_completed(futs):
            key = futs[fut]
            try:
                rec = fut.result()
                done[(key[1], rec["status"])] += 1
            except BudgetExceeded:
                stopped += 1
            except Exception as exc:  # a bug, not a model failure: report it loudly
                print(f"  CRASH {key}: {type(exc).__name__}: {exc}")
                done[(key[1], "crash")] += 1
            n = sum(done.values()) + stopped
            if n % 10 == 0 or n == len(tasks):
                print(f"  {n}/{len(tasks)} tasks, spent ${BUDGET.spent:.2f}")
    print("Results by approach and status:")
    for (a, s), k in sorted(done.items()):
        print(f"  {a:<6} {s:<8} {k}")
    if stopped:
        print(f"  {stopped} tasks not run: budget reached (rerun with a higher --budget to resume)")
    manifest = {"seed": SEED, "effort": EFFORT, "n_votes": N_VOTES, "models": {"main": OPUS, "cheap": SONNET},
                "budget_usd": args.budget, "spent_total_usd": round(BUDGET.spent, 4),
                "prompts": {p.name: sha(p) for p in sorted(PROMPTS.glob("*.md"))},
                "schemas": {"entity_definition.yaml": sha(ROOT / "entity_definition.yaml"),
                            "relation.yaml": sha(ROOT / "relation.yaml")},
                "hc3_ids": [it["id"] for it in hc3], "micro_ids": [it["id"] for it in micro],
                "tasks_not_run_budget": stopped}
    write_yaml(OUT / f"manifest_{time.strftime('%Y%m%dT%H%M%S')}.yaml", manifest)


if __name__ == "__main__":
    main()
