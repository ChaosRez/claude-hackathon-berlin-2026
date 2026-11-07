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
    """Return a list of rule violations; empty means valid. Rules follow relation.yaml."""
    errors: list[str] = []
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    implicit_main = bool(graph.get("implicit_main", False))

    if not nodes:
        return ["no nodes"]

    # GUIDE.md section 8: nodes are listed in text order. Ids must be unique and increase.
    ids = [n["id"] for n in nodes]
    if any(b <= a for a, b in zip(ids, ids[1:])):
        errors.append(f"node ids must be unique and increase in reading order, got {ids}")
    by_id = {n["id"]: n for n in nodes}

    errors += coverage_errors(answer, [n["text"] for n in nodes])

    for n in nodes:
        t = n["type"]
        if t not in schema.entity_types:
            errors.append(f"node {n['id']}: unknown type '{t}'")
        if not n["text"].strip():
            errors.append(f"node {n['id']}: empty text")
        if t == "evidence" and n.get("kind") not in schema.evidence_kinds:
            errors.append(f"node {n['id']}: evidence needs kind in {list(schema.evidence_kinds)}")
        if t != "evidence" and n.get("kind") is not None:
            errors.append(f"node {n['id']}: kind is only for evidence")
        if t == "other" and not (n.get("note") or "").strip():
            errors.append(f"node {n['id']}: other needs a note")
        if t != "other" and n.get("note") is not None:
            errors.append(f"node {n['id']}: note is only for other")

    mains = [n for n in nodes if n.get("main")]
    if implicit_main:
        if mains:
            errors.append("implicit_main is set, but a node is also marked main")
    elif len(mains) != 1:
        errors.append(f"exactly one main node required, got {len(mains)}")
    for m in mains:
        if m["type"] in schema.non_node_types:
            errors.append(f"node {m['id']}: main node cannot be {m['type']}")

    seen_pairs: set[tuple[int, int]] = set()
    primary_to: dict[int, list[int]] = {}
    out_count: Counter[int] = Counter()
    for e in edges:
        a, b = e["from"], e["to"]
        label = f"edge {a}->{b}"
        if e["type"] not in schema.relation_types:
            errors.append(f"{label}: unknown type '{e['type']}'")
        if a not in by_id or b not in by_id:
            errors.append(f"{label}: points to a missing node")
            continue
        if a == b:
            errors.append(f"{label}: self loop")
        if (a, b) in seen_pairs:
            errors.append(f"{label}: more than one edge between the same pair")
        seen_pairs.add((a, b))
        for end in (a, b):
            if by_id[end]["type"] in schema.non_node_types:
                errors.append(f"{label}: touches {by_id[end]['type']} node {end}")
        if e.get("primary"):
            if e["type"] in schema.never_primary:
                errors.append(f"{label}: {e['type']} edge cannot be primary")
            primary_to.setdefault(a, []).append(b)
        out_count[a] += 1

    for n in nodes:
        if n["type"] in schema.non_node_types:
            continue
        k, n_primary = n["id"], len(primary_to.get(n["id"], []))
        if n.get("main"):
            if n_primary:
                errors.append(f"node {k}: main node cannot have a primary edge")
            continue
        if not out_count[k]:
            errors.append(f"node {k} ({n['type']}): needs at least one outgoing edge")
        elif n_primary != 1:
            errors.append(f"node {k} ({n['type']}): needs exactly 1 primary edge, has {n_primary}")

    # Primary edges must form a tree rooted at the main node: following them always reaches main.
    if mains and not errors:
        root = mains[0]["id"]
        for n in nodes:
            if n["type"] in schema.non_node_types or n["id"] == root:
                continue
            seen, cur = set(), n["id"]
            while cur != root and cur not in seen:
                seen.add(cur)
                cur = primary_to[cur][0]
            if cur != root:
                errors.append(f"node {n['id']}: primary edges loop and never reach the main node")
                break

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
