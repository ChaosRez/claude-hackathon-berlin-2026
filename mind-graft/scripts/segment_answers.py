"""Split each human and ChatGPT answer into candidate segments for entity labelling.

Segments are sentences, further split at clause boundaries such as "; " and ", but".
Labellers can merge segments back together with "+" in the label file.

Usage:
    python scripts/segment_answers.py data/hc3_similar_length_100.jsonl data/work/segments.json data/work/segments.txt
"""
import json
import re
import sys
from pathlib import Path

CLAUSE_SPLIT = re.compile(r"(?<=[,;])\s+(?=(?:but|however|although|though|whereas|yet)\b)|(?<=;)\s+", re.I)


def clean(text: str) -> str:
    # HC3 human answers put spaces around punctuation; tidy it for reading.
    t = re.sub(r"\s+([.,!?;:)\]])", r"\1", text)
    t = re.sub(r"([(\[])\s+", r"\1", t)
    t = re.sub(r"\s+n't\b", "n't", t)
    t = re.sub(r"\s+('s|'re|'ve|'m|'ll|'d)\b", r"\1", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[\"'*(]?[A-Z0-9])", text)
    out = []
    for p in parts:
        # Keep list markers like "1." attached to the following sentence.
        if out and re.fullmatch(r"\(?\d{1,2}[.)]", out[-1].strip()):
            out[-1] = out[-1] + " " + p
        else:
            out.append(p)
    return [s for s in out if s.strip()]


def segment(text: str) -> list[str]:
    segs = []
    for s in sentences(clean(text)):
        segs.extend(x.strip() for x in CLAUSE_SPLIT.split(s) if x.strip())
    return segs


def main(src: str, out_json: str, out_txt: str) -> None:
    rows = [json.loads(l) for l in open(src, encoding="utf-8")]
    data = []
    lines = []
    for k, r in enumerate(rows, start=1):
        h, l = segment(r["human_answer"]), segment(r["chatgpt_answer"])
        q = clean(r["question"])
        data.append({"row": k, "row_index": r["row_index"], "question": q, "H": h, "L": l})
        lines.append(f"### {k} | Q: {q}")
        lines += [f"H{i} {s}" for i, s in enumerate(h, 1)]
        lines += [f"L{i} {s}" for i, s in enumerate(l, 1)]
        lines.append("")
    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(out_json).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    Path(out_txt).write_text("\n".join(lines), encoding="utf-8")
    n = sum(len(d["H"]) + len(d["L"]) for d in data)
    print(f"{len(data)} rows, {n} segments")


if __name__ == "__main__":
    main(*sys.argv[1:4])
