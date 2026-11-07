"""Audit checks for the approach study (see PLAN.md, "Audit before findings"). Deterministic; no model calls.

Usage:
  uv run --no-project --python 3.13 --with pyyaml python experiments/approach_study/audit.py

Prints only ids, counts and short excerpts; nothing is written.
"""
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data" / "approach_study"
GOLD = {r["id"]: r for r in map(json.loads, (ROOT / "data/external/argmicro_en_sample20.jsonl").read_text().splitlines())}


def recs(dataset, approach, rep):
    return {f.name: yaml.safe_load(f.read_text()) for f in sorted((D / dataset / approach / rep).glob("*.yaml"))}


def texts(rec):
    return [n["text"] for n in rec["nodes"]]


def main_text(rec):
    return next((n["text"] for n in rec["nodes"] if n["main"]), "")


print("== Microtexts: main-claim misses (gold split approaches compare ids, A compares text)")
for a in ["A", "A-son", "S", "V", "P"]:
    for r in recs("micro", a, "rep1").values():
        g = GOLD[r["id"]]
        gold_text = g["nodes"][g["central"] - 1]["text"]
        mt = main_text(r)
        if gold_text[:30] not in mt and mt[:30] not in gold_text:
            print(f"  {a:<6} {r['id']}: predicted '{mt[:50]}' | gold '{gold_text[:50]}'")

print("== Microtexts: does one-pass find the gold split? (node count difference, pred - gold)")
for a in ["A", "A-son"]:
    diffs = [len(r["nodes"]) - len(GOLD[r["id"]]["nodes"]) for r in recs("micro", a, "rep1").values()]
    print(f"  {a:<6} same count {sum(d == 0 for d in diffs)}/20, differences {diffs}")

print("== HC3: one-pass re-split stability (identical split in rep1 and rep2)")
for a in ["A", "A-son"]:
    r1, r2 = recs("hc3", a, "rep1"), recs("hc3", a, "rep2")
    same = sum(texts(r1[k]) == texts(r2[k]) for k in r1 if k in r2)
    print(f"  {a:<6} {same}/{len(r1)} texts split identically")

print("== HC3: one-pass split vs the shared stage-1 split")
seg = {f.name: yaml.safe_load(f.read_text()) for f in (D / "hc3" / "segments").glob("*.yaml")}
for a in ["A", "A-son"]:
    r1 = recs("hc3", a, "rep1")
    same = sum(texts(r) == seg[k]["segments"] for k, r in r1.items())
    print(f"  {a:<6} rep1 equals stage-1 split in {same}/{len(r1)} texts")
print(f"  stage-1 split status: {sorted({s['status'] for s in seg.values()})}, "
      f"retries used: {sum(len(s['calls']) > 1 for s in seg.values())}")

print("== Invalid or errored runs")
for a in ["A", "A-son", "S", "V", "P"]:
    for ds in ["micro", "hc3"]:
        for rep in ["rep1", "rep2"]:
            for r in recs(ds, a, rep).values():
                if r["status"] != "valid":
                    print(f"  {a} {ds} {rep} {r['id']}: {r['status']}: {r['errors'][:2]}")

print("== Voting diagnostics (HC3 and microtexts)")
for ds in ["hc3", "micro"]:
    zero = valid = total = 0
    for rep in ["rep1", "rep2"]:
        for r in recs(ds, "V", rep).values():
            d = r["diagnostics"]
            zero += d.get("zero_vote_primary_edges", 0)
            valid += d.get("samples_valid", 0)
            total += d.get("samples", 0)
    print(f"  {ds}: primary edges no sample chose: {zero}; valid samples {valid}/{total}")

print("== Retries used (runs needing more than the minimum number of calls)")
minimum = {"A": 1, "A-son": 1, "S": 1, "P": 2, "V": 5}
for a, m in minimum.items():
    n = sum(r["n_calls"] > m for ds in ["micro", "hc3"] for rep in ["rep1", "rep2"] for r in recs(ds, a, rep).values())
    print(f"  {a:<6} {n}")
