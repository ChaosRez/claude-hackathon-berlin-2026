"""Combine several labellings of the same fixed pieces into one graph.

Chosen in docs/adr/0001-extraction-approach.md:
majority type per piece, majority main claim, and the primary-edge tree with the most votes
(a maximum spanning arborescence rooted at the main claim).
Pure Python, so it runs where networkx does not import.
"""
from collections import Counter, defaultdict

from src.schema import Schema


def max_arborescence(nodes: list, root, weight: dict) -> dict:
    """Chu-Liu/Edmonds: the tree rooted at `root` with the largest total weight.

    nodes: node ids; weight: {(parent, child): float} for every allowed edge.
    Returns {child: parent} for every node except the root.
    Ties go to the parent that comes first in `nodes`.
    """
    best = {}
    for v in nodes:
        if v == root:
            continue
        top = None
        for u in nodes:
            if u != v and (u, v) in weight and (top is None or weight[(u, v)] > weight[(top, v)]):
                top = u
        if top is None:
            raise ValueError(f"node {v!r} has no incoming edge")
        best[v] = top

    cycle = _find_cycle(best, root)
    if not cycle:
        return best

    c = ("cycle", len(nodes), id(cycle))  # a fresh node id for the contracted cycle
    in_cycle = set(cycle)
    new_nodes = [n for n in nodes if n not in in_cycle] + [c]
    new_w, enters, leaves = {}, {}, {}
    for (u, v), w in weight.items():
        if u in in_cycle and v in in_cycle:
            continue
        if v in in_cycle:  # edge into the cycle: replaces the cycle edge into v
            gain = w - weight[(best[v], v)]
            if (u, c) not in new_w or gain > new_w[(u, c)]:
                new_w[(u, c)], enters[u] = gain, v
        elif u in in_cycle:  # edge out of the cycle: keep the best one per target
            if (c, v) not in new_w or w > new_w[(c, v)]:
                new_w[(c, v)], leaves[v] = w, u
        else:
            new_w[(u, v)] = w

    sub = max_arborescence(new_nodes, root, new_w)
    parent = {}
    for v, u in sub.items():
        if v == c:
            continue
        parent[v] = leaves[v] if u == c else u
    entry_parent = sub[c]
    entry_node = enters[entry_parent]
    for v in cycle:
        parent[v] = entry_parent if v == entry_node else best[v]
    return parent


def _find_cycle(parent: dict, root):
    for start in parent:
        path, v = [], start
        while v in parent and v not in path:
            path.append(v)
            v = parent[v]
        if v in path:
            return path[path.index(v):]
    return None


def majority(values, default=None):
    """Most common value; ties go to the value seen first."""
    if not values:
        return default
    counts = Counter(values)
    top = max(counts.values())
    return next(v for v in values if counts[v] == top)


def aggregate(samples: list[dict], segments: list[str], schema: Schema) -> tuple[dict, dict]:
    """Combine label samples (each {"nodes", "edges"}) over the same numbered pieces.

    Returns (graph, diagnostics). diagnostics["parent_share"][id] is the share of samples
    that chose the same primary parent as the final graph.
    """
    n = len(segments)
    by_sample = [{x["id"]: x for x in s["nodes"]} for s in samples]
    main = majority([next((x["id"] for x in s["nodes"] if x.get("main")), None) for s in samples])
    nodes = []
    for i in range(1, n + 1):
        cands = [nb[i] for nb in by_sample if i in nb]
        t = majority([c["type"] for c in cands], "other")
        same = [c for c in cands if c["type"] == t]
        nodes.append({
            "id": i, "type": t, "main": i == main,
            "hedged": majority([c["hedged"] for c in cands], False),
            "kind": majority([c["kind"] for c in same]) if t == "evidence" else None,
            "note": next((c["note"] for c in same if c.get("note")), "majority vote of samples") if t == "other" else None,
            "text": segments[i - 1],
        })
    diag = {"samples": len(samples), "parent_share": {}, "zero_vote_edges": 0}
    if main is None:
        return {"nodes": nodes, "edges": [], "implicit_main": True}, diag

    graph_ids = [x["id"] for x in nodes if x["type"] not in schema.non_node_types]
    parent_votes: dict = defaultdict(Counter)  # child -> parent -> votes (primary edges)
    edge_votes: dict = defaultdict(Counter)    # (from, to) -> relation -> votes (any edge)
    for s in samples:
        for e in s["edges"]:
            edge_votes[(e["from"], e["to"])][e["type"]] += 1
            if e.get("primary"):
                parent_votes[e["from"]][e["to"]] += 1

    # Every pair is allowed; votes decide. A tiny bonus for the main claim keeps zero-vote fallbacks short.
    weight = {(p, c): parent_votes[c][p] + (1e-3 if p == main else 1e-6)
              for c in graph_ids if c != main for p in graph_ids if p != c}
    tree = max_arborescence(graph_ids, main, weight) if len(graph_ids) > 1 else {}

    edges = []
    for c, p in sorted(tree.items()):
        votes = parent_votes[c][p]
        diag["zero_vote_edges"] += votes == 0
        diag["parent_share"][c] = round(votes / len(samples), 3)
        rels = [r for r in edge_votes[(c, p)].elements() if r not in schema.never_primary]
        if not rels:  # no sample drew this edge: use the child's most common primary relation
            rels = [e["type"] for s in samples for e in s["edges"]
                    if e["from"] == c and e.get("primary") and e["type"] not in schema.never_primary] or ["supports"]
        edges.append({"from": c, "to": p, "type": majority(rels), "primary": True})

    # Extra (non-primary) edges that most samples drew.
    chosen = set(tree.items())
    need = len(samples) // 2 + 1
    for (a, b), rels in edge_votes.items():
        if (a, b) in chosen or a not in graph_ids or b not in graph_ids or a == b:
            continue
        if sum(rels.values()) >= need:
            edges.append({"from": a, "to": b, "type": majority(list(rels.elements())), "primary": False})
    edges.sort(key=lambda e: (e["from"], not e["primary"], e["to"]))
    return {"nodes": nodes, "edges": edges, "implicit_main": False}, diag
