"""Score the approach study (see PLAN.md). Deterministic; no model calls.

Usage:
  uv run --no-project --python 3.13 --with pyyaml python experiments/approach_study/analyze.py

Reads data/approach_study/ and data/external/argmicro_en_sample20.jsonl.
Writes experiments/approach_study/results/ (scores only, no text from HC3 or microtexts):
  summary.yaml      every table below, with 95% bootstrap intervals over texts
  per_text.csv      one row per text, approach and measure
Prints the tables as markdown.
"""
import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.validate import _norm  # noqa: E402

DATA = ROOT / "data" / "approach_study"
GOLD = ROOT / "data" / "external" / "argmicro_en_sample20.jsonl"
RES = Path(__file__).resolve().parent / "results"
APPROACHES = ["A", "A-son", "S", "V", "P"]
BASELINES = ["B1", "B2"]
ATTACK = {"attacks", "refutes", "conflicts"}  # everything else counts as support in the microtext mapping
BOOT, SEED = 2000, 2026


def load(dataset, approach, rep):
    d = DATA / dataset / approach / f"rep{rep}"
    return {f.stem: yaml.safe_load(f.read_text()) for f in sorted(d.glob("*.yaml"))} if d.exists() else {}


def spans(nodes):
    """Character span of each node in the answer, ignoring whitespace and punctuation."""
    out, pos = {}, 0
    for n in nodes:
        k = len(_norm(n["text"]))
        out[n["id"]] = (pos, pos + k)
        pos += k
    return out


def align(ref_nodes, other_nodes):
    """Map each reference node id to the other node id that overlaps it most (None if no overlap)."""
    rs, os_ = spans(ref_nodes), spans(other_nodes)
    m = {}
    for r, (a, b) in rs.items():
        best, best_ov = None, 0
        for o, (c, d) in os_.items():
            ov = min(b, d) - max(a, c)
            if ov > best_ov:
                best, best_ov = o, ov
        m[r] = best
    return m


def primary_parent(rec):
    return {e["from"]: (e["to"], e["type"]) for e in rec.get("edges", []) if e.get("primary")}


def main_id(rec):
    return next((n["id"] for n in rec.get("nodes", []) if n.get("main")), None)


def boot_ci(values, stat=lambda v: sum(v) / len(v)):
    """95% percentile bootstrap interval over texts (seeded)."""
    if not values:
        return None, None
    rng = random.Random(SEED)
    stats = sorted(stat([rng.choice(values) for _ in values]) for _ in range(BOOT))
    return round(stats[int(0.025 * BOOT)], 3), round(stats[int(0.975 * BOOT) - 1], 3)


def mean(v):
    return round(sum(v) / len(v), 3) if v else None


def summarize(per_text_values):
    """per_text_values: list of (numerator, denominator) per text -> pooled rate + CI over texts."""
    num = sum(a for a, _ in per_text_values)
    den = sum(b for _, b in per_text_values)
    if not den:
        return {"value": None, "ci95": [None, None], "n": 0}
    pooled = lambda v: sum(a for a, _ in v) / max(1, sum(b for _, b in v))  # noqa: E731
    lo, hi = boot_ci(per_text_values, pooled)
    return {"value": round(num / den, 3), "ci95": [lo, hi], "n": den}


def kappa(pairs):
    """Cohen's kappa for a list of (label1, label2)."""
    if not pairs:
        return None
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    c1, c2 = defaultdict(int), defaultdict(int)
    for a, b in pairs:
        c1[a] += 1
        c2[b] += 1
    pe = sum(c1[k] * c2[k] for k in set(c1) | set(c2)) / n / n
    return round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0


# --------------------------------------------------------------------------- microtexts: accuracy


def baseline_record(kind, gold_nodes, main):
    n = len(gold_nodes)
    edges = []
    for i in range(1, n + 1):
        if i == main:
            continue
        p = main if kind == "B2" else (i - 1 if i > 1 else 2)
        edges.append({"from": i, "to": p, "type": "supports", "primary": True})
    nodes = [{**g, "type": "claim", "main": g["id"] == main} for g in gold_nodes]
    return {"status": "valid", "nodes": nodes, "edges": edges}


def score_micro():
    gold = {r["id"]: r for r in map(json.loads, GOLD.read_text().splitlines()) if r}
    recs = {a: load("micro", a, 1) for a in APPROACHES}
    s_main = {tid: main_id(r) for tid, r in recs["S"].items()}
    for b in BASELINES:  # baselines take the main claim chosen by S (see PLAN.md)
        recs[b] = {tid: baseline_record(b, g["nodes"], s_main.get(tid) or 1) for tid, g in gold.items()}
    rows, table = [], {}
    for a in APPROACHES + BASELINES:
        main_v, att_v, lab_v, opp = [], [], [], {"tp": 0, "fp": 0, "fn": 0}
        status = defaultdict(int)
        for tid, g in gold.items():
            rec = recs[a].get(tid)
            status[rec["status"] if rec else "missing"] += 1
            non_central = [e for e in g["edges"]]
            if not rec or rec["status"] == "error" or not rec.get("nodes"):
                main_v.append((0, 1))
                att_v.append((0, len(non_central)))
                lab_v.append((0, len(non_central)))
                opp["fn"] += sum(n["role"] == "opp" for n in g["nodes"])
                rows.append({"dataset": "micro", "approach": a, "id": tid, "main_correct": 0, "attach_correct": 0,
                             "labelled_correct": 0, "n_attach": len(non_central), "n_pred_nodes": 0,
                             "n_gold_nodes": len(g["nodes"])})
                continue
            m = align(g["nodes"], rec["nodes"])
            pp = primary_parent(rec)
            types = {n["id"]: n["type"] for n in rec["nodes"]}
            main_ok = int(main_id(rec) is not None and main_id(rec) == m[g["central"]])
            att = lab = 0
            for e in non_central:
                child, parent = m[e["from"]], m[e["to"]]
                got = pp.get(child)
                if got and child != parent and got[0] == parent:
                    att += 1
                    fam = "attack" if got[1] in ATTACK else "support"
                    lab += fam == e["label"]
            for n in g["nodes"]:
                pred_opp = types.get(m[n["id"]]) == "counterpoint"
                gold_opp = n["role"] == "opp"
                opp["tp"] += pred_opp and gold_opp
                opp["fp"] += pred_opp and not gold_opp
                opp["fn"] += gold_opp and not pred_opp
            main_v.append((main_ok, 1))
            att_v.append((att, len(non_central)))
            lab_v.append((lab, len(non_central)))
            rows.append({"dataset": "micro", "approach": a, "id": tid, "main_correct": main_ok,
                         "attach_correct": att, "labelled_correct": lab, "n_attach": len(non_central),
                         "n_pred_nodes": len(rec["nodes"]), "n_gold_nodes": len(g["nodes"])})
        p = opp["tp"] / max(1, opp["tp"] + opp["fp"])
        r = opp["tp"] / max(1, opp["tp"] + opp["fn"])
        table[a] = {"status": dict(status), "main_claim": summarize(main_v), "attachment": summarize(att_v),
                    "labelled_attachment": summarize(lab_v),
                    "opponent_f1": round(2 * p * r / (p + r), 3) if p + r else 0.0}
    return table, rows


# --------------------------------------------------------------------------- HC3: stability, validity, cost, shape


def seg_costs():
    out = {}
    for f in (DATA / "hc3" / "segments").glob("*.yaml"):
        r = yaml.safe_load(f.read_text())
        out[f.stem] = sum(c.get("cost_usd", 0) or 0 for c in r.get("calls", []))
    return out


def stability(r1, r2):
    """Agreement between two runs of one approach on one text."""
    ok = r1 and r2 and r1["status"] != "error" and r2["status"] != "error" and r1["nodes"] and r2["nodes"]
    graph1 = [n for n in (r1 or {}).get("nodes", []) if n["type"] != "filler"]
    if not ok:
        return {"main": (0, 1), "type_pairs": [], "attach": (0, max(1, len(graph1) - 1)), "jaccard": 0.0,
                "type": (0, max(1, len(graph1)))}
    m = align(r1["nodes"], r2["nodes"])
    t2 = {n["id"]: n["type"] for n in r2["nodes"]}
    pairs = [(n["type"], t2.get(m[n["id"]])) for n in r1["nodes"]]
    p1, p2 = primary_parent(r1), primary_parent(r2)
    att = [int(m[c] is not None and m[c] in p2 and p2[m[c]][0] == m[p]) for c, (p, _) in p1.items()]
    e1 = {(m[e["from"]], m[e["to"]], e["type"]) for e in r1["edges"]}
    e2 = {(e["from"], e["to"], e["type"]) for e in r2["edges"]}
    jac = len(e1 & e2) / len(e1 | e2) if e1 | e2 else 1.0
    return {"main": (int(main_id(r1) is not None and m[main_id(r1)] == main_id(r2)), 1),
            "type_pairs": pairs, "type": (sum(a == b for a, b in pairs), len(pairs)),
            "attach": (sum(att), len(att)), "jaccard": jac}


def depth(rec):
    pp, main, best = primary_parent(rec), main_id(rec), 0
    for c in pp:
        d, cur, seen = 0, c, set()
        while cur in pp and cur not in seen:
            seen.add(cur)
            cur, d = pp[cur][0], d + 1
        best = max(best, d)
    return best


def score_hc3():
    segc = seg_costs()
    table, rows = {}, []
    for a in APPROACHES:
        r1, r2 = load("hc3", a, 1), load("hc3", a, 2)
        ids = sorted(set(r1) | set(r2))
        res = {}
        for src in ("all", "human", "chatgpt"):
            sel = [t for t in ids if src == "all" or t.endswith("_" + src)]
            st = [stability(r1.get(t), r2.get(t)) for t in sel]
            recs = [r for t in sel for r in (r1.get(t), r2.get(t)) if r]
            costs = [r["cost_usd"] + (segc.get(r["id"], 0) if a in ("S", "V", "P") else 0) for r in recs]
            valid = [(int(r["status"] == "valid"), 1) for r in recs]
            ok = [r for r in recs if r["status"] != "error"]
            res[src] = {
                "texts": len(sel), "runs": len(recs),
                "valid": summarize(valid),
                "main_agreement": summarize([s["main"] for s in st]),
                "type_agreement": summarize([s["type"] for s in st]),
                "type_kappa": kappa([p for s in st for p in s["type_pairs"]]),
                "attach_agreement": summarize([s["attach"] for s in st]),
                "edge_jaccard": {"value": mean([s["jaccard"] for s in st]),
                                 "ci95": list(boot_ci([s["jaccard"] for s in st]))},
                "cost_per_text_usd": mean(costs),
                "nodes_per_text": mean([len(r["nodes"]) for r in ok]),
                "edges_per_text": mean([len(r["edges"]) for r in ok]),
                "tree_depth": mean([depth(r) for r in ok]),
                "counterpoint_share": mean([sum(n["type"] == "counterpoint" for n in r["nodes"]) / len(r["nodes"])
                                            for r in ok if r["nodes"]]),
            }
            if src == "all":
                for t, s in zip(sel, st):
                    rows.append({"dataset": "hc3", "approach": a, "id": t, "main_agree": s["main"][0],
                                 "attach_agree": s["attach"][0], "n_attach": s["attach"][1],
                                 "edge_jaccard": round(s["jaccard"], 3)})
        table[a] = res
    return table, rows


def paired(rows, dataset, metric, a, b, denom=None):
    """Mean per-text difference a - b, with a 95% paired bootstrap interval over texts."""
    by = defaultdict(dict)
    for r in rows:
        if r["dataset"] == dataset:
            v = float(r[metric]) / (float(r[denom]) if denom and float(r[denom]) else 1)
            by[r["id"]][r["approach"]] = v
    diffs = [d[a] - d[b] for d in by.values() if a in d and b in d]
    lo, hi = boot_ci(diffs)
    return {"a": a, "b": b, "metric": metric, "mean_diff": mean(diffs), "ci95": [lo, hi], "n_texts": len(diffs)}


PAIRS = [("micro", "attach_correct", "n_attach", ("S", "A")), ("micro", "attach_correct", "n_attach", ("V", "S")),
         ("micro", "attach_correct", "n_attach", ("P", "S")), ("micro", "attach_correct", "n_attach", ("A", "A-son")),
         ("micro", "attach_correct", "n_attach", ("S", "B2")),
         ("hc3", "edge_jaccard", None, ("V", "S")), ("hc3", "edge_jaccard", None, ("P", "S")),
         ("hc3", "edge_jaccard", None, ("S", "A")), ("hc3", "edge_jaccard", None, ("A", "A-son")),
         ("hc3", "attach_agree", "n_attach", ("V", "S"))]


def micro_costs():
    out = {}
    for a in APPROACHES:
        recs = load("micro", a, 1).values()
        out[a] = mean([r["cost_usd"] for r in recs])
    return out


def fmt(x):
    if isinstance(x, dict):
        v, (lo, hi) = x["value"], x["ci95"]
        return "–" if v is None else f"{v:.2f} [{lo:.2f}–{hi:.2f}]"
    return "–" if x is None else f"{x:.2f}" if isinstance(x, float) else str(x)


def main():
    RES.mkdir(exist_ok=True)
    micro, micro_rows = score_micro()
    hc3, hc3_rows = score_hc3()
    mc = micro_costs()
    pairs = [paired(micro_rows + hc3_rows, ds, m, x, y, den) for ds, m, den, (x, y) in PAIRS]
    summary = {"microtexts_accuracy": micro, "microtexts_cost_per_text_usd": mc, "hc3": hc3, "paired": pairs,
               "notes": ["Intervals are 95% percentile bootstrap over texts (2000 resamples, seed 2026).",
                         "Errored and invalid runs stay in every denominator.",
                         "HC3 has no hand labels: HC3 numbers are stability, validity, cost and shape, not accuracy.",
                         "Baselines B1/B2 use the main claim chosen by S."]}
    (RES / "summary.yaml").write_text(yaml.safe_dump(summary, sort_keys=False, width=10**9))
    with (RES / "per_text.csv").open("w", newline="") as f:
        keys = sorted({k for r in micro_rows + hc3_rows for k in r})
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(micro_rows + hc3_rows)

    print("## Accuracy on arg-microtexts (20 texts, gold graphs)\n")
    print("| Approach | Main claim | Attachment | Labelled attachment | Opponent F1 | $/text | Status |")
    print("|---|---|---|---|---|---|---|")
    for a in APPROACHES + BASELINES:
        t = micro[a]
        print(f"| {a} | {fmt(t['main_claim'])} | {fmt(t['attachment'])} | {fmt(t['labelled_attachment'])} | "
              f"{t['opponent_f1']:.2f} | {fmt(mc.get(a, 0.0))} | {t['status']} |")
    print("\n## Paired differences (per text, a - b, 95% paired bootstrap)\n")
    print("| Data | Measure | a − b | Mean difference | 95% interval | Texts |")
    print("|---|---|---|---|---|---|")
    for q in pairs:
        print(f"| {q['metric'].startswith('edge') and 'HC3' or ('HC3' if q['metric'] == 'attach_agree' else 'micro')} | "
              f"{q['metric']} | {q['a']} − {q['b']} | {q['mean_diff']:+.3f} | {q['ci95'][0]:+.3f} to {q['ci95'][1]:+.3f} | "
              f"{q['n_texts']} |")
    for src in ("all", "human", "chatgpt"):
        print(f"\n## HC3 stability, two runs ({src})\n")
        print("| Approach | Valid | Main agree | Type agree | Type κ | Attach agree | Edge Jaccard | $/text | Nodes | Edges | Depth |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        for a in APPROACHES:
            t = hc3[a][src]
            print(f"| {a} | {fmt(t['valid'])} | {fmt(t['main_agreement'])} | {fmt(t['type_agreement'])} | "
                  f"{fmt(t['type_kappa'])} | {fmt(t['attach_agreement'])} | {fmt(t['edge_jaccard'])} | "
                  f"{fmt(t['cost_per_text_usd'])} | {fmt(t['nodes_per_text'])} | {fmt(t['edges_per_text'])} | "
                  f"{fmt(t['tree_depth'])} |")


if __name__ == "__main__":
    main()
