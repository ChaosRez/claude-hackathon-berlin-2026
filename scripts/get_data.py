#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Download HC3 finance and filter it to length-matched pairs.

Usage: uv run scripts/get_data.py [filter options]
Writes data/finance.jsonl (raw) and data/finance-filtered.jsonl.
Extra options go to filter_jsonl.py, e.g. --max-diff 15 --limit 100.
"""
import subprocess
import sys
import urllib.request
from pathlib import Path

URL = "https://huggingface.co/datasets/Hello-SimpleAI/HC3/resolve/main/finance.jsonl"
SCRIPTS = Path(__file__).resolve().parent
RAW = SCRIPTS.parent / "data" / "finance.jsonl"


def main() -> None:
    if RAW.exists():
        print(f"Using existing {RAW}")
    else:
        RAW.parent.mkdir(exist_ok=True)
        print(f"Downloading {URL}")
        urllib.request.urlretrieve(URL, RAW)
    subprocess.run([sys.executable, SCRIPTS / "filter_jsonl.py", RAW, *sys.argv[1:]], check=True)


if __name__ == "__main__":
    main()
