"""Embed data/entity_graphs.json into the viewer template so the page works as one file.

Usage:
    python scripts/build_viewer.py viewer/language_sails.template.html data/entity_graphs.json viewer/language_sails.html
"""
import json
import sys
from pathlib import Path

template, data, out = sys.argv[1:4]
payload = json.dumps(json.loads(Path(data).read_text(encoding="utf-8")), ensure_ascii=False, separators=(",", ":"))
payload = payload.replace("</", "<\\/")  # keep any "</script>" inside text from closing the tag
html = Path(template).read_text(encoding="utf-8").replace("/*DATA*/", payload, 1)
Path(out).write_text(html, encoding="utf-8")
print(f"wrote {out} ({len(html) // 1024} KB)")
