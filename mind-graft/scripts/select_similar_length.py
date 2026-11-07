"""Select HC3 entries where the human and ChatGPT answers have similar word counts.

For each row, compares the first human answer with the first ChatGPT answer.
Word count = number of whitespace-separated tokens. Keeps rows where
|human_words - chatgpt_words| < MAX_DIFF, in file order, until LIMIT rows are found.

Usage:
    python scripts/select_similar_length.py data/raw/HC3_all.jsonl data/hc3_similar_length_100
"""
import csv
import json
import sys
from pathlib import Path

MAX_DIFF = 10  # strictly less than
LIMIT = 100


def word_count(text: str) -> int:
    return len(text.split())


def main(src: str, out_stem: str) -> None:
    selected = []
    scanned = 0
    with open(src, encoding="utf-8") as f:
        for line_no, line in enumerate(f):
            row = json.loads(line)
            scanned += 1
            humans = [a for a in row.get("human_answers") or [] if a and a.strip()]
            bots = [a for a in row.get("chatgpt_answers") or [] if a and a.strip()]
            if not humans or not bots:
                continue
            h, c = humans[0], bots[0]
            hw, cw = word_count(h), word_count(c)
            if abs(hw - cw) < MAX_DIFF:
                selected.append({
                    "row_index": line_no,
                    "source": row.get("source", ""),
                    "question": row["question"],
                    "human_answer": h,
                    "chatgpt_answer": c,
                    "human_words": hw,
                    "chatgpt_words": cw,
                    "word_diff": abs(hw - cw),
                })
                if len(selected) >= LIMIT:
                    break

    out = Path(out_stem)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out.with_suffix(".jsonl"), "w", encoding="utf-8") as f:
        for r in selected:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(out.with_suffix(".csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(selected[0].keys()))
        w.writeheader()
        w.writerows(selected)

    print(f"Scanned {scanned} rows, selected {len(selected)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
