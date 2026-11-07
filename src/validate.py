"""Step 3 check: is the graph JSON correct by GUIDE.md section 6?

TODO (Task 4): implement all rules from GUIDE.md section 6.
Contract: return a list of error strings. Empty list = valid.
"""


def validate(graph: dict) -> list[str]:
    errors = []
    ids = {n["id"] for n in graph.get("nodes", [])}
    for e in graph.get("edges", []):
        if e["from"] not in ids or e["to"] not in ids:
            errors.append(f"edge {e} points to a missing node")
    if sum(1 for n in graph.get("nodes", []) if n.get("main")) != 1:
        errors.append("graph must have exactly one main claim")
    return errors
