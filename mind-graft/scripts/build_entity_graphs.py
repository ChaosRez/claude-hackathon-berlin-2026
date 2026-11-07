"""Combine segments and entity labels into one graph data file for all 100 rows.

Reads data/work/segments.json and every data/labels/*.txt file (format in docs/entity_codebook.md),
validates them, and writes data/entity_graphs.json plus a per-answer summary CSV.

Usage:
    python scripts/build_entity_graphs.py data/work/segments.json data/labels data/entity_graphs.json data/entity_summary.csv
"""
import csv
import json
import re
import sys
from pathlib import Path

X_BY_TYPE = {"O": -1.0, "H": -0.5, "B": 0.5}
TYPE_NAMES = {
    "C": "Claim", "R": "Reason", "E": "Elaboration", "X": "Example / evidence", "D": "Definition / background",
    "O": "Opposing view", "H": "Hedge / concession", "B": "Rebuttal", "S": "Restatement",
    "K": "Conclusion", "V": "Advice", "T": "Aside",
}
TOKEN = re.compile(r"^([A-Z])(\d+)?((?:\^\d+)*)$")


def parse_labels(folder: Path) -> dict:
    labels = {}
    for f in sorted(folder.glob("*.txt")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            m = re.match(r"^(\d+)\s+([HL]):\s*(.*)$", line.strip())
            if not m:
                raise ValueError(f"{f.name}:{n}: bad line {line!r}")
            key = (int(m.group(1)), m.group(2))
            if key in labels:
                raise ValueError(f"{f.name}:{n}: duplicate labels for {key}")
            labels[key] = m.group(3).split()
    return labels


def build_answer(segs: list[str], tokens: list[str], where: str) -> list[dict]:
    if len(segs) != len(tokens):
        raise ValueError(f"{where}: {len(segs)} segments but {len(tokens)} tokens")
    if tokens[0] == "+":
        raise ValueError(f"{where}: first token cannot be '+'")
    ents, seg_to_ent, word = [], {}, 0
    for i, (seg, tok) in enumerate(zip(segs, tokens), start=1):
        n = len(seg.split())
        if tok == "+":
            e = ents[-1]
            e["text"] += " " + seg
            e["w1"] = word + n
        else:
            m = TOKEN.match(tok)
            if not m or m.group(1) not in TYPE_NAMES:
                raise ValueError(f"{where}: bad token {tok!r} at segment {i}")
            parent = int(m.group(2)) if m.group(2) is not None else None
            rets = [int(r) for r in m.group(3).split("^") if r]
            for ref in ([parent] if parent else []) + [r for r in rets if r]:
                if ref >= i:
                    raise ValueError(f"{where}: segment {i} refers forward to {ref}")
            ents.append({"type": m.group(1), "text": seg, "w0": word, "w1": word + n,
                         "_parent": parent, "_rets": rets})
        seg_to_ent[i] = len(ents) - 1
        word += n

    def ref(s):  # segment number -> entity index (-1 = question)
        return -1 if s == 0 else seg_to_ent[s]

    for k, e in enumerate(ents):
        p, rets = e.pop("_parent"), e.pop("_rets")
        e["parent"] = ref(p) if p is not None else None
        e["returns"] = sorted({ref(r) for r in rets})
        if e["parent"] is not None and e["parent"] >= k:
            raise ValueError(f"{where}: entity {k} parent is not earlier")
        if e["parent"] is not None:
            e["depth"] = 1 + (0 if e["parent"] == -1 else ents[e["parent"]]["depth"])
        elif e["returns"]:
            e["depth"] = min(0 if r == -1 else ents[r]["depth"] for r in e["returns"])
        else:
            e["depth"] = 1
        e["x"] = X_BY_TYPE.get(e["type"], 0.0)
        e["mid"] = (e["w0"] + e["w1"]) / 2
    return ents


def summary(ents: list[dict], words: int) -> dict:
    return {
        "entities": len(ents),
        "words": words,
        "max_depth": max(e["depth"] for e in ents),
        "mean_depth": round(sum(e["depth"] for e in ents) / len(ents), 2),
        "opposing_entities": sum(1 for e in ents if e["x"] < 0),
        "rebuttals": sum(1 for e in ents if e["type"] == "B"),
        "returns": sum(1 for e in ents if e["returns"]),
        "width": max(e["x"] for e in ents) - min(e["x"] for e in ents),
    }


def main(seg_path: str, label_dir: str, out_json: str, out_csv: str) -> None:
    rows = json.loads(Path(seg_path).read_text(encoding="utf-8"))
    labels = parse_labels(Path(label_dir))
    out, table, errors = [], [], []
    for r in rows:
        rec = {"row": r["row"], "row_index": r["row_index"], "question": r["question"]}
        for side in "HL":
            key = (r["row"], side)
            if key not in labels:
                errors.append(f"row {r['row']} {side}: no labels")
                continue
            try:
                ents = build_answer(r[side], labels[key], f"row {r['row']} {side}")
            except ValueError as e:
                errors.append(str(e))
                continue
            words = sum(len(s.split()) for s in r[side])
            rec[side] = {"words": words, "entities": ents, "summary": summary(ents, words)}
            table.append({"row": r["row"], "answer": "human" if side == "H" else "chatgpt", **rec[side]["summary"]})
        out.append(rec)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    meta = {"types": TYPE_NAMES, "x_by_type": X_BY_TYPE}
    Path(out_json).write_text(json.dumps({"meta": meta, "rows": out}, ensure_ascii=False), encoding="utf-8")
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(table[0].keys()))
        w.writeheader()
        w.writerows(table)
    for side in ("human", "chatgpt"):
        t = [x for x in table if x["answer"] == side]
        avg = lambda k: sum(x[k] for x in t) / len(t)
        print(f"{side:8} entities {avg('entities'):.1f}  max depth {avg('max_depth'):.2f}  mean depth {avg('mean_depth'):.2f}  "
              f"opposing {avg('opposing_entities'):.2f}  returns {avg('returns'):.2f}  "
              f"answers with opposing idea {sum(1 for x in t if x['opposing_entities'])}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
