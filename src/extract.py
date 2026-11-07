"""Extract entities and relations from HC3 answers, using the YAML schemas and Claude.

Usage:
  uv run python -m src.extract --limit 2
  uv run python -m src.extract --pairs 0,5,9 --sources human
  uv run python -m src.extract --limit 2 --approach one-pass

Approaches (chosen in docs/adr/0001-extraction-approach.md):
  voted     (default) split the answer once, label the fixed pieces --votes times,
            then keep the majority types and the primary-edge tree with the most votes.
  one-pass  split, type and link in one call (prompts/extract_v2.md).

Writes to results/extraction/<run_id>/:
  graphs/<id>.yaml   one file per answer: nodes (entities), edges (relations), check result
  run.yaml           settings, prompt and schema versions, counts

Backends:
  api  Anthropic SDK; needs ANTHROPIC_API_KEY (read from the environment or .env).
  cli  The `claude` command line tool, using your Claude Code login.
  auto api if ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN is set, otherwise cli.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import yaml

from src.schema import DEFAULT_ENTITIES, DEFAULT_RELATIONS, ROOT, Schema, load_schema, write_yaml
from src.validate import coverage_errors, validate
from src.voting import aggregate

SOURCES = {"human": "human_answers", "chatgpt": "chatgpt_answers"}
# CLAUDE.md: until GUIDE.md is final, don't run the extractor on the full dataset.
MAX_PAIRS_WHILE_DRAFT = 10


def load_dotenv(path: Path = ROOT / ".env") -> None:
    """Read KEY=VALUE lines from .env into the environment (existing variables win)."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def guide_is_final() -> bool:
    guide = ROOT / "GUIDE.md"
    return guide.exists() and "status: final" in guide.read_text().lower()


def build_system_prompt(template_path: Path, schema: Schema) -> str:
    return (
        template_path.read_text()
        .replace("{entity_schema}", schema.entity_text.strip())
        .replace("{relation_schema}", schema.relation_text.strip())
    )


def build_user_prompt(question: str, answer: str) -> str:
    return f"<question>\n{question}\n</question>\n\n<answer>\n{answer}\n</answer>"


def retry_prompt(user: str, previous: dict, errors: list[str]) -> str:
    return (
        f"{user}\n\nYour previous labelling of this answer broke these rules:\n"
        + "\n".join(f"- {e}" for e in errors)
        + f"\n\nPrevious output:\n{yaml.safe_dump(previous, sort_keys=False, allow_unicode=True)}\n"
        "Produce a corrected, complete labelling of the whole answer."
    )


# --------------------------------------------------------------------------- backends


def call_api(system: str, user: str, json_schema: dict, model: str, effort: str) -> tuple[dict, dict]:
    import anthropic

    client = anthropic.Anthropic()
    with client.beta.messages.stream(
        model=model,
        max_tokens=64000,
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user}],
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": json_schema}},
        # Re-run on a fallback model if a safety classifier declines the request.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason != "end_turn":
        raise RuntimeError(f"stop_reason={msg.stop_reason} id={msg.id}")
    text = next(b.text for b in msg.content if b.type == "text")
    meta = {"model": msg.model, "message_id": msg.id,
            "input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens}
    return json.loads(text), meta


def call_cli(system: str, user: str, json_schema: dict, model: str, effort: str) -> tuple[dict, dict]:
    cmd = [
        "claude", "-p", "--model", model, "--effort", effort,
        "--output-format", "json", "--json-schema", json.dumps(json_schema),
        "--system-prompt", system,
        "--tools", "", "--strict-mcp-config", "--setting-sources", "",
        "--no-session-persistence", "--disable-slash-commands",
    ]
    # Run outside the repo so the project's CLAUDE.md is not added to the prompt.
    with tempfile.TemporaryDirectory() as cwd:
        proc = subprocess.run(cmd, input=user, capture_output=True, text=True, cwd=cwd, timeout=900)
    if proc.returncode != 0:
        raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr.strip()[:500] or proc.stdout[:500]}")
    out = json.loads(proc.stdout)
    if out.get("is_error") or "structured_output" not in out:
        raise RuntimeError(f"claude returned no structured output: {str(out.get('result'))[:500]}")
    usage = out.get("usage", {})
    meta = {"model": model, "session_id": out.get("session_id"), "cost_usd": out.get("total_cost_usd"),
            "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens")}
    return out["structured_output"], meta


BACKENDS = {"api": call_api, "cli": call_cli}


# --------------------------------------------------------------------------- one text


def new_record(item: dict, approach: str) -> dict:
    return {**item, "approach": approach, "status": "error", "attempts": [], "nodes": [], "edges": [],
            "implicit_main": False, "errors": [], "diagnostics": {}}


def extract_one_pass(item: dict, prompts: dict, schema: Schema, args) -> dict:
    """Split, type and link in one call; retry with the validator's errors."""
    call = BACKENDS[args.backend]
    system, json_schema = prompts["one-pass"], schema.output_json_schema()
    user = build_user_prompt(item["question"], item["answer"])
    record = new_record(item, "one-pass")
    prompt = user
    for attempt in range(args.retries + 1):
        try:
            out, meta = call(system, prompt, json_schema, args.model, args.effort)
        except Exception as exc:  # recorded, never dropped
            record["attempts"].append({"attempt": attempt, "error": f"{type(exc).__name__}: {exc}"})
            record["errors"] = [f"{type(exc).__name__}: {exc}"]
            continue
        errors = validate(out, item["answer"], schema)
        record["attempts"].append({"attempt": attempt, **meta, "errors": errors})
        record.update(nodes=out["nodes"], edges=out["edges"],
                      implicit_main=out["implicit_main"], errors=errors,
                      status="valid" if not errors else "invalid")
        if not errors:
            break
        prompt = retry_prompt(user, out, errors)
    return record


def pieces_prompt(item: dict, segments: list[str]) -> str:
    numbered = "\n".join(f"{i}. {s}" for i, s in enumerate(segments, 1))
    return build_user_prompt(item["question"], item["answer"]) + f"\n\n<pieces>\n{numbered}\n</pieces>"


def split(item: dict, prompts: dict, schema: Schema, args, record: dict) -> list[str] | None:
    """Stage 1: cut the answer into pieces once; retry with the coverage errors."""
    call = BACKENDS[args.backend]
    user = build_user_prompt(item["question"], item["answer"])
    prompt = user
    for attempt in range(args.retries + 1):
        try:
            out, meta = call(prompts["split"], prompt, schema.segment_json_schema(), args.model, args.effort)
        except Exception as exc:  # recorded, never dropped
            record["attempts"].append({"step": "split", "attempt": attempt, "error": f"{type(exc).__name__}: {exc}"})
            record["errors"] = [f"split failed: {type(exc).__name__}: {exc}"]
            continue
        segs = out["segments"]
        errors = coverage_errors(item["answer"], segs) + (["empty piece"] if any(not x.strip() for x in segs) else [])
        record["attempts"].append({"step": "split", "attempt": attempt, **meta, "errors": errors})
        if not errors:
            return segs
        record["errors"] = [f"split: {e}" for e in errors]
        prompt = (f"{user}\n\nYour previous split broke these rules:\n" + "\n".join(f"- {e}" for e in errors)
                  + f"\n\nPrevious split:\n{json.dumps(segs, ensure_ascii=False)}\n\nSplit the whole answer again.")
    return None


def extract_voted(item: dict, prompts: dict, schema: Schema, args) -> dict:
    """Split once, label the fixed pieces args.votes times, and combine the votes."""
    call = BACKENDS[args.backend]
    record = new_record(item, "voted")
    segs = split(item, prompts, schema, args, record)
    if segs is None:
        return record
    user = pieces_prompt(item, segs)
    samples = []
    for vote in range(args.votes):
        try:
            out, meta = call(prompts["label"], user, schema.label_json_schema(), args.model, args.effort)
        except Exception as exc:  # recorded, never dropped
            record["attempts"].append({"step": "label", "vote": vote, "error": f"{type(exc).__name__}: {exc}"})
            continue
        nodes = [{**x, "text": segs[x["id"] - 1] if 1 <= x["id"] <= len(segs) else ""} for x in out["nodes"]]
        sample = {"nodes": nodes, "edges": out["edges"], "implicit_main": out["implicit_main"]}
        errors = validate(sample, item["answer"], schema)
        record["attempts"].append({"step": "label", "vote": vote, **meta, "errors": errors})
        samples.append(sample)
    if not samples:
        record["errors"] = ["no label sample returned"]
        return record
    graph, diag = aggregate(samples, segs, schema)
    diag["samples_valid"] = sum(not a.get("errors") for a in record["attempts"] if a.get("step") == "label" and "error" not in a)
    errors = validate(graph, item["answer"], schema)
    record.update(nodes=graph["nodes"], edges=graph["edges"], implicit_main=graph["implicit_main"],
                  errors=errors, diagnostics=diag, status="valid" if not errors else "invalid")
    return record


EXTRACTORS = {"voted": extract_voted, "one-pass": extract_one_pass}


# --------------------------------------------------------------------------- run


def load_items(data_path: Path, pair_ids: list[int], sources: list[str]) -> list[dict]:
    rows = [json.loads(line) for line in data_path.read_text().splitlines() if line.strip()]
    items = []
    for i in pair_ids:
        if not 0 <= i < len(rows):
            sys.exit(f"pair {i} out of range (file has {len(rows)} pairs)")
        for src in sources:
            items.append({"id": f"finance_{i:04d}_{src}", "pair": i, "source": src,
                          "question": rows[i]["question"], "answer": rows[i][SOURCES[src]][0]})
    return items


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


GRAPH_KEYS = ["id", "pair", "source", "question", "approach", "status", "errors", "implicit_main",
              "nodes", "edges", "diagnostics", "answer", "attempts"]
ENTITY_KEYS = ["id", "type", "main", "hedged", "kind", "note", "text"]


def graph_document(rec: dict) -> dict:
    """Fixed key order, so the YAML files read top to bottom: result first, raw answer and log last."""
    doc = {k: rec[k] for k in GRAPH_KEYS}
    doc["nodes"] = [{k: n[k] for k in ENTITY_KEYS} for n in rec["nodes"]]
    doc["edges"] = [{"from": e["from"], "type": e["type"], "to": e["to"], "primary": e["primary"]}
                    for e in rec["edges"]]
    return doc


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", type=Path, default=ROOT / "data" / "finance-filtered.jsonl")
    sel = p.add_mutually_exclusive_group(required=True)
    sel.add_argument("--limit", type=int, help="use the first N pairs")
    sel.add_argument("--pairs", help="comma-separated pair indexes (0-based line numbers)")
    sel.add_argument("--all", action="store_true", help="every pair (only when GUIDE.md is final)")
    p.add_argument("--sources", default="human,chatgpt")
    p.add_argument("--entities", type=Path, default=DEFAULT_ENTITIES)
    p.add_argument("--relations", type=Path, default=DEFAULT_RELATIONS)
    p.add_argument("--approach", choices=list(EXTRACTORS), default="voted")
    p.add_argument("--votes", type=int, default=5, help="label samples per answer (voted approach)")
    p.add_argument("--prompt", type=Path, default=ROOT / "prompts" / "extract_v2.md", help="one-pass prompt")
    p.add_argument("--split-prompt", type=Path, default=ROOT / "prompts" / "segment_v1.md")
    p.add_argument("--label-prompt", type=Path, default=ROOT / "prompts" / "label_v1.md")
    p.add_argument("--backend", choices=["auto", "api", "cli"], default="auto")
    p.add_argument("--model", default="claude-opus-5-5")
    p.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    p.add_argument("--retries", type=int, default=1, help="re-asks when a split or one-pass output breaks a rule")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--out", type=Path, help="output dir (default results/extraction/<timestamp>)")
    args = p.parse_args()

    load_dotenv()
    if args.backend == "auto":
        has_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
        args.backend = "api" if has_key else "cli"

    n_rows = sum(1 for line in args.data.read_text().splitlines() if line.strip())
    if args.all:
        pair_ids = list(range(n_rows))
    elif args.limit is not None:
        pair_ids = list(range(min(args.limit, n_rows)))
    else:
        pair_ids = [int(x) for x in args.pairs.split(",")]
    if len(pair_ids) > MAX_PAIRS_WHILE_DRAFT and not guide_is_final():
        sys.exit(f"GUIDE.md is not marked final, so at most {MAX_PAIRS_WHILE_DRAFT} pairs may be run "
                 f"(asked for {len(pair_ids)}). See CLAUDE.md.")
    sources = [s.strip() for s in args.sources.split(",")]
    if bad := set(sources) - set(SOURCES):
        sys.exit(f"unknown sources {bad}")

    schema = load_schema(args.entities, args.relations)
    prompts = {"one-pass": build_system_prompt(args.prompt, schema),
               "split": build_system_prompt(args.split_prompt, schema),
               "label": build_system_prompt(args.label_prompt, schema)}
    extract = EXTRACTORS[args.approach]
    items = load_items(args.data, pair_ids, sources)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.out or ROOT / "results" / "extraction" / run_id
    (out_dir / "graphs").mkdir(parents=True, exist_ok=True)
    print(f"Extracting {len(items)} texts ({args.approach}) with {args.backend}/{args.model} -> {out_dir}")

    records = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(extract, it, prompts, schema, args): it for it in items}
        for fut in as_completed(futures):
            rec = fut.result()
            records.append(rec)
            write_yaml(out_dir / "graphs" / f"{rec['id']}.yaml", graph_document(rec))
            print(f"  {rec['id']}: {rec['status']} ({len(rec['nodes'])} nodes, "
                  f"{len(rec['edges'])} edges, {len(rec['attempts'])} call(s))")
    records.sort(key=lambda r: r["id"])

    counts = {s: sum(r["status"] == s for r in records) for s in ("valid", "invalid", "error")}
    manifest = {
        "run_id": run_id, "approach": args.approach, "votes": args.votes if args.approach == "voted" else None,
        "backend": args.backend, "model": args.model, "effort": args.effort,
        "retries": args.retries, "data": str(args.data), "pairs": pair_ids, "sources": sources,
        "prompts": {str(q.relative_to(ROOT)): sha(q) for q in
                    ([args.split_prompt, args.label_prompt] if args.approach == "voted" else [args.prompt])},
        "entity_schema": {"path": str(args.entities), "sha256_12": sha(args.entities)},
        "relation_schema": {"path": str(args.relations), "sha256_12": sha(args.relations)},
        "guide_final": guide_is_final(), "texts": len(records), "counts": counts,
        "license": "Derived from HC3 (CC BY-SA 4.0); this output is CC BY-SA 4.0.",
    }
    write_yaml(out_dir / "run.yaml", manifest)
    print(f"Done: {counts['valid']} valid, {counts['invalid']} invalid, {counts['error']} errored, "
          f"out of {len(records)} texts. Output: {out_dir}")


if __name__ == "__main__":
    main()
