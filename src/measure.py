"""Compute the graph measures defined in criteria.yaml and compare human vs ChatGPT.

Usage:
    uv run python -m src.measure GRAPH_DIR [--out results/measures.csv] [--seed 0]

GRAPH_DIR holds one JSON or YAML graph per file (format in GUIDE.md section 8).
Each graph must carry the original `answer`, so the coverage rule can be checked.
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

from src.schema import load_schema
from src.validate import validate

# Types come from entity_definition.yaml and relation.yaml, the same source the extractor uses.
SCHEMA = load_schema()
NON_NODE_TYPES = SCHEMA.non_node_types  # labelled but not graph nodes (filler)
GRAPH_TYPES = [t for t in SCHEMA.entity_types if t not in NON_NODE_TYPES]
RELATION_TYPES = list(SCHEMA.relation_types)

SCALAR_MEASURES = [
    "n_nodes", "n_edges", "n_filler", "edges_per_node", "extra_edge_share",
    "longest_path", "depth", "n_leaves", "main_in_degree", "mean_branching",
    "avg_degree", "max_degree", "max_in_degree", "has_cycle", "n_cycles", "main_position", "n_attacks", "answered_attack_share",
    "n_qualifies", "n_conflicts", "hedged_share",
]

IMPLICIT_MAIN_ERROR = (
    "implicit_main: no main claim, so depth, main_position and main_in_degree are undefined "
    "(how to measure these graphs is not decided yet)"
)


def check(graph):
    """Return a list of problems; an empty list means the graph can be measured.

    The rules are those of src/validate.py, which the extractor also uses.
    Graphs with `implicit_main` pass validation but are not measured yet.
    """
    answer = graph.get("answer")
    if not isinstance(answer, str):
        return ["no `answer` text: the coverage rule cannot be checked"]
    errors = validate(graph, answer, SCHEMA)
    if not errors and graph.get("implicit_main"):
        errors.append(IMPLICIT_MAIN_ERROR)
    return errors


def _full_graph(graph):
    g = nx.DiGraph()
    for n in graph["nodes"]:
        if n["type"] not in NON_NODE_TYPES:
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
    nodes = [n for n in graph["nodes"] if n["type"] not in NON_NODE_TYPES]
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
        "n_filler": sum(n["type"] in NON_NODE_TYPES for n in graph["nodes"]),
        "edges_per_node": n_edges / n_nodes,
        "extra_edge_share": (
            sum(not d["primary"] for _, _, d in g.edges(data=True)) / n_edges if n_edges else 0.0
        ),
        "longest_path": _longest_path(g),
        "depth": max(nx.shortest_path_length(tree, target=main).values()),
        "n_leaves": sum(d == 0 for _, d in g.in_degree()),
        "main_in_degree": g.in_degree(main),
        "mean_branching": sum(in_deg) / len(in_deg) if in_deg else 0.0,
        "avg_degree": 2 * n_edges / n_nodes,
        "max_degree": max(d for _, d in g.degree()),
        "max_in_degree": max(d for _, d in g.in_degree()),
        "has_cycle": int(not nx.is_directed_acyclic_graph(g)),
        "n_cycles": sum(1 for _ in nx.simple_cycles(g)),
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
        except (json.JSONDecodeError, yaml.YAMLError, KeyError, TypeError, AttributeError) as exc:
            graph, errors = {}, [f"unreadable: {exc!r}"]
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
