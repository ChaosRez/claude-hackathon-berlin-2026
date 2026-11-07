"""Copy the shared schema files FROM the hackathon group repo INTO Mind Graft. One way only.

Nothing is ever written to the group repo. The files land in upstream/group-repo/, unchanged,
next to a SOURCE.md that records which commit they came from. Run it again to pull the team's
latest version; review the diff before committing.

Usage:
    python -I scripts/sync_group_schema.py            # latest commit on the group repo's main
    python -I scripts/sync_group_schema.py <commit>   # a specific commit
"""
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = "ChaosRez/claude-hackathon-berlin-2026"
FILES = [
    "entity_definition.yaml",  # entity types (nodes)
    "relation.yaml",           # relation types (edges)
    "criteria.yaml",           # graph measures for comparing human and LLM
    "GUIDE.md",                # the team's summary; marked as the source of truth once FINAL
    "LICENSE",                 # Apache-2.0 (code)
    "LICENSE-docs",            # CC BY 4.0 (docs)
]
OUT = Path(__file__).resolve().parent.parent / "upstream" / "group-repo"


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "mind-graft-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main() -> None:
    ref = sys.argv[1] if len(sys.argv) > 1 else "main"
    sha = json.loads(get(f"https://api.github.com/repos/{REPO}/commits/{ref}"))["sha"]
    OUT.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        (OUT / name).write_bytes(get(f"https://raw.githubusercontent.com/{REPO}/{sha}/{name}"))
        print(f"copied {name}")
    (OUT / "SOURCE.md").write_text(
        "# Copied from the hackathon group repo\n\n"
        f"- Repository: https://github.com/{REPO}\n"
        f"- Commit: {sha}\n"
        f"- Copied: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by `scripts/sync_group_schema.py`\n\n"
        "These files are copies, kept unchanged. Do not edit them here; change them in the group repo\n"
        "and run the sync script again. Code is Apache-2.0 (LICENSE), docs are CC BY 4.0 (LICENSE-docs),\n"
        "both by the group repo's authors.\n",
        encoding="utf-8")
    print(f"commit {sha}")


if __name__ == "__main__":
    main()
