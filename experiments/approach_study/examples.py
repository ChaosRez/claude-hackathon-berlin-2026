"""Show the 3 HC3 texts where S (one labelling call) was least stable, and what V (5 votes) did there.

Usage:
  uv run --no-project --python 3.13 --with pyyaml python experiments/approach_study/examples.py

Prints to the terminal only (HC3 text excerpts stay out of the repository).
"""
import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data" / "approach_study" / "hc3"
rows = list(csv.DictReader((Path(__file__).parent / "results" / "per_text.csv").open()))
s_rows = sorted((r for r in rows if r["dataset"] == "hc3" and r["approach"] == "S"), key=lambda r: float(r["edge_jaccard"]))


def show(rec, label):
    nodes = {n["id"]: n for n in rec["nodes"]}
    print(f"  {label}: " + ", ".join(f"{e['from']}-{e['type']}->{e['to']}{'*' if e['primary'] else ''}"
                                     for e in rec["edges"]))
    return nodes


for r in s_rows[:3]:
    tid = r["id"]
    print(f"\n=== {tid}  S edge Jaccard {r['edge_jaccard']}")
    s1, s2 = (yaml.safe_load((D / "S" / rep / f"{tid}.yaml").read_text()) for rep in ("rep1", "rep2"))
    v1, v2 = (yaml.safe_load((D / "V" / rep / f"{tid}.yaml").read_text()) for rep in ("rep1", "rep2"))
    for n in s1["nodes"]:
        t2 = next(x["type"] for x in s2["nodes"] if x["id"] == n["id"])
        tv = next(x["type"] for x in v1["nodes"] if x["id"] == n["id"])
        flag = "  <-- type differs" if len({n["type"], t2, tv}) > 1 else ""
        print(f"  {n['id']:>2} S1={n['type']:<14} S2={t2:<14} V1={tv:<14} {n['text'][:60]}{flag}")
    show(s1, "S rep1")
    show(s2, "S rep2")
    show(v1, "V rep1")
    show(v2, "V rep2")
    e = lambda rec: {(x["from"], x["to"], x["type"]) for x in rec["edges"]}  # noqa: E731
    print(f"  S: {len(e(s1) ^ e(s2))} edges differ; V: {len(e(v1) ^ e(v2))} edges differ")
    conf = v1["diagnostics"]["parent_confidence"]
    print(f"  V rep1 parent vote shares: {dict(sorted(conf.items()))}")
