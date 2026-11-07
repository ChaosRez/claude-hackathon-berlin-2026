"""Prepare the built-in datasets for the Language Analyser app.

- HC3 Reddit ELI5: the 100 rows already segmented and hand-labelled (data/work/segments.json + data/labels).
- HC3 Finance and HC3 Wiki CSAI: first rows (max 100) where human and ChatGPT answers differ by < 10 words.
  These are segmented here but not labelled; the app labels them (rule-based at once, Claude on request).

Also writes plug-in example CSVs (question, human_answer, chatgpt_answer) and a per-answer
entity type count table for the labelled ELI5 set.

Usage:
    python scripts/build_analyser_data.py
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from segment_answers import clean, segment  # noqa: E402
from build_entity_graphs import parse_labels, build_answer, TYPE_NAMES  # noqa: E402

MAX_DIFF, LIMIT = 10, 100


def pick(source: str) -> list[dict]:
    out = []
    for line in open(ROOT / "data/raw/HC3_all.jsonl", encoding="utf-8"):
        r = json.loads(line)
        if r.get("source") != source:
            continue
        h = [a for a in r.get("human_answers") or [] if a and a.strip()]
        c = [a for a in r.get("chatgpt_answers") or [] if a and a.strip()]
        if h and c and abs(len(h[0].split()) - len(c[0].split())) < MAX_DIFF:
            out.append({"question": r["question"], "human_answer": h[0], "chatgpt_answer": c[0]})
            if len(out) >= LIMIT:
                break
    return out


def write_csv(rows: list[dict], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["question", "human_answer", "chatgpt_answer"])
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    datasets = []
    # ELI5, hand-labelled
    seg = json.loads((ROOT / "data/work/segments.json").read_text(encoding="utf-8"))
    labels = parse_labels(ROOT / "data/labels")
    eli5 = []
    count_rows = []
    for r in seg:
        eli5.append({"q": r["question"], "h": r["H"], "l": r["L"], "ht": labels[(r["row"], "H")], "lt": labels[(r["row"], "L")]})
        for side, name in (("H", "human"), ("L", "chatgpt")):
            ents = build_answer(r[side], labels[(r["row"], side)], f"row {r['row']} {side}")
            n = len(ents)
            rec = {"row": r["row"], "answer": name, "entities": n}
            for code, tname in TYPE_NAMES.items():
                k = sum(1 for e in ents if e["type"] == code)
                rec[tname] = k
                rec[tname + " %"] = round(100 * k / n, 1)
            count_rows.append(rec)
    datasets.append({"id": "hc3-eli5", "name": "HC3 Reddit ELI5", "method": "claude-manual", "rows": eli5})
    with open(ROOT / "data/entity_type_counts.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(count_rows[0].keys()))
        w.writeheader()
        w.writerows(count_rows)

    for source, did, name in (("finance", "hc3-finance", "HC3 Finance"), ("wiki_csai", "hc3-csai", "HC3 Wiki CSAI")):
        rows = pick(source)
        write_csv(rows, ROOT / f"data/{did}.csv")
        datasets.append({"id": did, "name": name, "method": "unlabelled",
                         "rows": [{"q": clean(r["question"]), "h": segment(r["human_answer"]), "l": segment(r["chatgpt_answer"])} for r in rows]})
        print(f"{name}: {len(rows)} rows")

    out = ROOT / "data/analyser_builtin.json"
    out.write_text(json.dumps(datasets, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {out.name} ({out.stat().st_size // 1024} KB) and data/entity_type_counts.csv")


if __name__ == "__main__":
    main()
