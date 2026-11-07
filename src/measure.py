"""Compute the graph measures defined in criteria.yaml and compare human vs ChatGPT.

Usage:
    python src/measure.py GRAPH_DIR [--out results/measures.csv] [--seed 0]

GRAPH_DIR holds one JSON or YAML graph per file (format in GUIDE.md / relation.yaml).
Invalid graphs are counted and listed, never silently dropped.
"""

import argparse
import json
import random
import sys
from pathlib import Path

import networkx as nx
import pandas as pd
import yaml

# Must match entity_definition.yaml and relation.yaml (checked by tests/test_measure.py).
ENTITY_TYPES = [
    "claim", "reason", "evidence", "counterpoint", "rebuttal", "condition",
    "recommendation", "caveat", "background", "filler", "other",
]
RELATION_TYPES = [
    "supports", "attacks", "refutes", "qualifies", "explains",
    "elaborates", "summarizes", "concludes", "conflicts",
]
GRAPH_TYPES = [t for t in ENTITY_TYPES if t != "filler"]

SCALAR_MEASURES = [
    "n_nodes", "n_edges", "n_filler", "edges_per_node", "extra_edge_share",
    "longest_path", "depth", "n_leaves", "main_in_degree", "mean_branching",
    "has_cycle", "main_position", "n_attacks", "answered_attack_share",
    "n_qualifies", "n_conflicts", "hedged_share",
]


def check(graph):
    """Return a list of problems; an empty list means the graph is valid."""
    errors = []
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    ids = [n["id"] for n in nodes]
    if len(ids) != len(set(ids)):
        errors.append("duplicate node ids")
    by_id = {n["id"]: n for n in nodes}
    for n in nodes:
        if n.get("type") not in ENTITY_TYPES:
            errors.append(f"node {n['id']}: unknown type {n.get('type')!r}")
    mains = [n["id"] for n in nodes if n.get("main")]
    if len(mains) != 1:
        errors.append(f"{len(mains)} main claims (need exactly 1)")
    seen_pairs = set()
    for e in edges:
        a, b = e.get("from"), e.get("to")
        if e.get("type") not in RELATION_TYPES:
            errors.append(f"edge {a}->{b}: unknown type {e.get('type')!r}")
        if a not in by_id or b not in by_id:
            errors.append(f"edge {a}->{b}: points to a missing node")
            continue
        if a == b:
            errors.append(f"edge {a}->{b}: self loop")
        if (a, b) in seen_pairs:
            errors.append(f"edge {a}->{b}: more than one edge between the same pair")
        seen_pairs.add((a, b))
        if "filler" in (by_id[a]["type"], by_id[b]["type"]):
            errors.append(f"edge {a}->{b}: touches filler")
        if e.get("type") == "conflicts" and e.get("primary"):
            errors.append(f"edge {a}->{b}: conflicts edge cannot be primary")
    for n in nodes:
        if n["type"] == "filler" or n.get("main"):
            continue
        out = [e for e in edges if e.get("from") == n["id"]]
        if not out:
            errors.append(f"node {n['id']}: no outgoing edge")
        elif sum(bool(e.get("primary")) for e in out) != 1:
            errors.append(f"node {n['id']}: needs exactly 1 primary edge")
    if not errors:
        tree = _primary_tree(graph)
        if not nx.is_tree(tree.to_undirected()) or any(
            not nx.has_path(tree, v, mains[0]) for v in tree.nodes
        ):
            errors.append("primary edges do not form a tree rooted at the main claim")
    return errors


def _full_graph(graph):
    g = nx.DiGraph()
    for n in graph["nodes"]:
        if n["type"] != "filler":
            g.add_node(n["id"], type=n["type"])
    for e in graph["edges"]:
        g.add_edge(e["from"], e["to"], type=e["type"], primary=bool(e.get("primary")))
    return g


def _primary_tree(graph):
    g = _full_graph(graph)
    tree = nx.DiGraph()
    tree.add_nodes_from(g.nodes)
    tree.add_edges_from((a, b) for a, b, d in g.edges(data=True) if d["primary"])
    return tree


def _longest_path(g):
    """Longest directed path in edges; cycles are merged into single nodes first."""
    if g.number_of_nodes() == 0:
        return 0
    if nx.is_directed_acyclic_graph(g):
        return nx.dag_longest_path_length(g)
    return nx.dag_longest_path_length(nx.condensation(g))


def measures(graph):
    """All per-graph measures from criteria.yaml, as a flat dict."""
    g = _full_graph(graph)
    tree = _primary_tree(graph)
    nodes = [n for n in graph["nodes"] if n["type"] != "filler"]
    main = next(n["id"] for n in nodes if n.get("main"))
    n_nodes, n_edges = g.number_of_nodes(), g.number_of_edges()
    edge_types = [d["type"] for _, _, d in g.edges(data=True)]
    in_deg = [d for _, d in g.in_degree() if d > 0]
    counterpoints = [n["id"] for n in nodes if n["type"] == "counterpoint"]
    answered = [
        c for c in counterpoints
        if any(d["type"] == "refutes" for _, _, d in g.in_edges(c, data=True))
    ]
    order = [n["id"] for n in nodes]  # node list is in text order

    m = {
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "n_filler": sum(n["type"] == "filler" for n in graph["nodes"]),
        "edges_per_node": n_edges / n_nodes,
        "extra_edge_share": (
            sum(not d["primary"] for _, _, d in g.edges(data=True)) / n_edges if n_edges else 0.0
        ),
        "longest_path": _longest_path(g),
        "depth": max(nx.shortest_path_length(tree, target=main).values()),
        "n_leaves": sum(d == 0 for _, d in g.in_degree()),
        "main_in_degree": g.in_degree(main),
        "mean_branching": sum(in_deg) / len(in_deg) if in_deg else 0.0,
        "has_cycle": int(not nx.is_directed_acyclic_graph(g)),
        "main_position": order.index(main) / (len(order) - 1) if len(order) > 1 else None,
        "n_attacks": edge_types.count("attacks"),
        "answered_attack_share": len(answered) / len(counterpoints) if counterpoints else None,
        "n_qualifies": edge_types.count("qualifies"),
        "n_conflicts": edge_types.count("conflicts"),
        "hedged_share": sum(bool(n.get("hedged")) for n in nodes) / n_nodes,
    }
    for t in GRAPH_TYPES:
        m[f"entity_share_{t}"] = sum(n["type"] == t for n in nodes) / n_nodes
    for t in RELATION_TYPES:
        m[f"relation_share_{t}"] = edge_types.count(t) / n_edges if n_edges else 0.0
    return m


def load(graph_dir):
    """Return (table of measures for valid graphs, list of (file, errors) for invalid ones)."""
    rows, invalid = [], []
    paths = sorted([*Path(graph_dir).glob("*.json"), *Path(graph_dir).glob("*.yaml")])
    for path in paths:
        try:
            text = path.read_text()
            graph = yaml.safe_load(text) if path.suffix == ".yaml" else json.loads(text)
            errors = check(graph)
        except (json.JSONDecodeError, yaml.YAMLError, KeyError, TypeError) as exc:
            graph, errors = {}, [f"unreadable: {exc}"]
        if errors:
            invalid.append((path.name, graph.get("source"), errors))
            continue
        rows.append({"file": path.name, "id": graph["id"], "source": graph["source"],
                     "question": graph["question"], **measures(graph)})
    return pd.DataFrame(rows), invalid


def split_half_baseline(values, n_repeats=1000, seed=0):
    """95% range of mean differences between two random halves of one group."""
    values = [v for v in values if v is not None and not pd.isna(v)]
    if len(values) < 4:
        return None
    rng = random.Random(seed)
    diffs = []
    for _ in range(n_repeats):
        shuffled = values[:]
        rng.shuffle(shuffled)
        half = len(shuffled) // 2
        a, b = shuffled[:half], shuffled[half:2 * half]
        diffs.append(sum(a) / len(a) - sum(b) / len(b))
    diffs.sort()
    return diffs[int(0.025 * n_repeats)], diffs[int(0.975 * n_repeats) - 1]


def compare(table, seed=0):
    """Per-measure summary: means per source, paired difference, human split-half baseline."""
    out = []
    for m in SCALAR_MEASURES:
        human = table[table.source == "human"]
        llm = table[table.source != "human"]
        paired = human[["question", m]].merge(llm[["question", m]], on="question",
                                              suffixes=("_human", "_llm")).dropna()
        diff = paired[f"{m}_llm"] - paired[f"{m}_human"]
        base = split_half_baseline(human[m].tolist(), seed=seed)
        out.append({
            "measure": m,
            "n_human": human[m].notna().sum(),
            "mean_human": human[m].mean(),
            "n_llm": llm[m].notna().sum(),
            "mean_llm": llm[m].mean(),
            "n_pairs": len(paired),
            "mean_paired_diff_llm_minus_human": diff.mean() if len(paired) else None,
            "human_vs_human_95pct_low": base[0] if base else None,
            "human_vs_human_95pct_high": base[1] if base else None,
        })
    return pd.DataFrame(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("graph_dir")
    parser.add_argument("--out", help="write per-graph measures to this CSV")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)

    table, invalid = load(args.graph_dir)
    print(f"valid graphs: {len(table)}  invalid graphs: {len(invalid)}")
    if len(table):
        print(table.groupby("source").size().rename("valid per source").to_string())
    for name, source, errors in invalid:
        print(f"  INVALID {name} ({source}): {'; '.join(errors)}")
    if table.empty:
        print("No valid graphs: result INCONCLUSIVE.")
        return 1
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(args.out, index=False)
    with pd.option_context("display.width", 200, "display.max_columns", None):
        print(compare(table, seed=args.seed).round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
