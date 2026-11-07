import itertools
import random

import pytest

from src.schema import load_schema
from src.validate import validate
from src.voting import aggregate, max_arborescence

SCHEMA = load_schema()


def brute_force_best(nodes, root, weight):
    """Highest total weight over every parent choice that forms a tree rooted at root."""
    others = [v for v in nodes if v != root]
    best = None
    for parents in itertools.product(nodes, repeat=len(others)):
        tree = dict(zip(others, parents))
        if any(c == p or (p, c) not in weight for c, p in tree.items()):
            continue
        if all(reaches_root(tree, v, root) for v in others):
            t = sum(weight[(p, c)] for c, p in tree.items())
            best = t if best is None else max(best, t)
    return best


def reaches_root(tree, v, root):
    seen = set()
    while v != root:
        if v in seen:
            return False
        seen.add(v)
        v = tree[v]
    return True


def total(tree, weight):
    return sum(weight[(p, c)] for c, p in tree.items())


@pytest.mark.parametrize("seed", range(200))
def test_max_arborescence_matches_brute_force(seed):
    rng = random.Random(seed)
    n = rng.randint(2, 6)
    nodes = list(range(1, n + 1))
    root = rng.choice(nodes)
    weight = {(u, v): rng.randint(0, 5) + rng.random() / 10 for u in nodes for v in nodes
              if u != v and v != root and rng.random() < 0.8}
    for v in nodes:  # keep it solvable: the root can always reach every node
        if v != root:
            weight.setdefault((root, v), 0.0)
    tree = max_arborescence(nodes, root, weight)
    assert set(tree) == set(nodes) - {root}
    assert all(reaches_root(tree, v, root) for v in tree)
    assert total(tree, weight) == pytest.approx(brute_force_best(nodes, root, weight))


def test_max_arborescence_matches_networkx():
    try:
        import networkx as nx
    except Exception as exc:  # networkx fails to import on Python 3.14.1
        pytest.skip(f"networkx does not import here: {exc!r}")
    rng = random.Random(7)
    for _ in range(50):
        nodes = list(range(1, rng.randint(3, 15)))
        root = nodes[0]
        weight = {(u, v): float(rng.randint(0, 5)) + rng.random() for u in nodes for v in nodes if u != v and v != root}
        g = nx.DiGraph()
        g.add_weighted_edges_from((u, v, w) for (u, v), w in weight.items())
        ours = total(max_arborescence(nodes, root, weight), weight)
        theirs = nx.maximum_spanning_arborescence(g).size(weight="weight")
        assert ours == pytest.approx(theirs)


def node(i, t, main=False, kind=None):
    return {"id": i, "type": t, "main": main, "hedged": False, "kind": kind, "note": None}


def edge(a, b, t, primary=True):
    return {"from": a, "to": b, "type": t, "primary": primary}


SEGS = ["Great question!", "Index funds are a good choice.", "Their fees are low.", "A 0.1% fee on $10,000 is $10."]
ANSWER = " ".join(SEGS)


def sample(evidence_parent, fee_type="reason", rel="supports"):
    return {"nodes": [node(1, "filler"), node(2, "claim", main=True), node(3, fee_type),
                      node(4, "evidence", kind="fact")],
            "edges": [edge(3, 2, rel), edge(4, evidence_parent, "supports")], "implicit_main": False}


def test_aggregate_takes_majority_and_is_valid():
    samples = [sample(3), sample(3), sample(2, fee_type="claim", rel="elaborates"), sample(3), sample(2)]
    graph, diag = aggregate(samples, SEGS, SCHEMA)
    types = {n["id"]: n["type"] for n in graph["nodes"]}
    assert types == {1: "filler", 2: "claim", 3: "reason", 4: "evidence"}
    primary = {e["from"]: (e["to"], e["type"]) for e in graph["edges"] if e["primary"]}
    assert primary == {3: (2, "supports"), 4: (3, "supports")}
    assert diag["parent_share"] == {3: 1.0, 4: 0.6}
    assert diag["zero_vote_edges"] == 0
    assert validate(graph, ANSWER, SCHEMA) == []


def test_aggregate_breaks_vote_cycles_into_a_tree():
    # Every sample votes 3 -> 4 and 4 -> 3 (a cycle); the tree must still reach the main claim.
    s = {"nodes": [node(1, "filler"), node(2, "claim", main=True), node(3, "reason"), node(4, "reason")],
         "edges": [edge(3, 4, "supports"), edge(4, 3, "supports")], "implicit_main": False}
    graph, diag = aggregate([s, s, s], SEGS, SCHEMA)
    assert validate(graph, ANSWER, SCHEMA) == []
    assert diag["zero_vote_edges"] == 1
