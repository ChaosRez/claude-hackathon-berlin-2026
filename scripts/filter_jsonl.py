#!/usr/bin/env python3
"""Filter an HC3-style JSONL file to entries whose human and LLM answers have similar length.

Usage: python filter_jsonl.py data/finance.jsonl
Writes data/finance-filtered.jsonl next to the input file.
"""
import argparse
import json
from pathlib import Path


def word_count(text: str) -> int:
    return len(text.split())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("filename", type=Path, help="input .jsonl file")
    parser.add_argument("--limit", type=int, default=100, help="max entries to keep (default 100)")
    parser.add_argument("--max-diff", type=int, default=10, help="max word-count difference (default 10)")
    parser.add_argument("--min-total", type=int, default=150, help="min combined word count (default 150)")
    parser.add_argument("--max-total", type=int, default=500, help="max combined word count (default 500)")
    args = parser.parse_args()

    out_path = args.filename.with_name(f"{args.filename.stem}-filtered.jsonl")
    kept = 0
    with args.filename.open() as src, out_path.open("w") as dst:
        for line in src:
            if not line.strip():
                continue
            entry = json.loads(line)
            if not entry.get("human_answers") or not entry.get("chatgpt_answers"):
                continue
            human = word_count(entry["human_answers"][0])
            llm = word_count(entry["chatgpt_answers"][0])
            if abs(human - llm) <= args.max_diff and args.min_total <= human + llm <= args.max_total:
                dst.write(line if line.endswith("\n") else line + "\n")
                kept += 1
                if kept >= args.limit:
                    break

    print(f"Wrote {kept} entries to {out_path}")


if __name__ == "__main__":
    main()
