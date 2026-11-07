"""Check extracted graphs against the schema rules.

Usage: uv run python -m src.validate results/extraction/<run>/graphs
Prints one line per invalid graph and a count. Exit code 1 if any graph is invalid.
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

from src.schema import Schema, load_schema, read_yaml

_DROP = re.compile(r"[\W_]+")  # whitespace and punctuation


def _norm(text: str) -> str:
    return _DROP.sub("", text)


def coverage_errors(answer: str, entity_texts: list[str]) -> list[str]:
    """Joining entity texts in order must give back the answer, ignoring whitespace and punctuation."""
    want, got = _norm(answer), _norm("".join(entity_texts))
    if want == got:
        return []
    i = next((k for k, (a, b) in enumerate(zip(want, got)) if a != b), min(len(want), len(got)))
    return [
        "coverage: entity texts do not rebuild the answer "
        f"(answer {len(want)} chars, entities {len(got)} chars, first difference at char {i}: "
        f"answer '...{want[max(0, i - 20):i + 20]}...' vs entities '...{got[max(0, i - 20):i + 20]}...')"
    ]


def validate(graph: dict, answer: str, schema: Schema) -> list[str]:
    """Return a list of rule violations; empty means valid."""
    errors: list[str] = []
    entities = graph.get("entities", [])
    relations = graph.get("relations", [])
    implicit_main = bool(graph.get("implicit_main", False))

    if not entities:
        return ["no entities"]

    ids = [e["id"] for e in entities]
    if ids != list(range(1, len(ids) + 1)):
        errors.append(f"entity ids must be 1..{len(ids)} in reading order, got {ids}")
    by_id = {e["id"]: e for e in entities}

    errors += coverage_errors(answer, [e["text"] for e in entities])

    for e in entities:
        t = e["type"]
        if t not in schema.entity_types:
            errors.append(f"entity {e['id']}: unknown type '{t}'")
        if not e["text"].strip():
            errors.append(f"entity {e['id']}: empty text")
        if t == "evidence" and e.get("kind") not in schema.evidence_kinds:
            errors.append(f"entity {e['id']}: evidence needs kind in {list(schema.evidence_kinds)}")
        if t != "evidence" and e.get("kind") is not None:
            errors.append(f"entity {e['id']}: kind is only for evidence")
        if t == "other" and not (e.get("note") or "").strip():
            errors.append(f"entity {e['id']}: other needs a note")
        if t != "other" and e.get("note") is not None:
            errors.append(f"entity {e['id']}: note is only for other")

    mains = [e for e in entities if e.get("main")]
    if implicit_main:
        if mains:
            errors.append("implicit_main is set, but an entity is also marked main")
    elif len(mains) != 1:
        errors.append(f"exactly one main entity required, got {len(mains)}")
    for m in mains:
        if m["type"] in schema.non_node_types:
            errors.append(f"entity {m['id']}: main entity cannot be {m['type']}")

    out_count: Counter[int] = Counter()
    for r in relations:
        label = f"relation {r['from']}->{r['to']}"
        if r["type"] not in schema.relation_types:
            errors.append(f"{label}: unknown type '{r['type']}'")
        if r["from"] not in by_id or r["to"] not in by_id:
            errors.append(f"{label}: points to a missing entity")
            continue
        if r["from"] == r["to"]:
            errors.append(f"{label}: points to itself")
        for end in (r["from"], r["to"]):
            if by_id[end]["type"] in schema.non_node_types:
                errors.append(f"{label}: touches {by_id[end]['type']} entity {end}, which is not a graph node")
        out_count[r["from"]] += 1

    for e in entities:
        t, n = e["type"], out_count[e["id"]]
        if t in schema.non_node_types:
            continue
        if e.get("main"):
            if n:
                errors.append(f"entity {e['id']}: main entity must have no outgoing edge, has {n}")
        elif t in schema.edge_optional:
            if n > 1:
                errors.append(f"entity {e['id']} ({t}): at most one outgoing edge, has {n}")
        elif n != 1:
            errors.append(f"entity {e['id']} ({t}): exactly one outgoing edge required, has {n}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("graph_dir", type=Path)
    args = parser.parse_args()
    schema = load_schema()
    files = sorted(args.graph_dir.glob("*.yaml"))
    bad = 0
    for f in files:
        rec = read_yaml(f)
        errs = validate(rec, rec["answer"], schema)
        if errs:
            bad += 1
            print(f"INVALID {f.name}: " + "; ".join(errs))
    print(f"{len(files) - bad}/{len(files)} graphs valid, {bad} invalid")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
