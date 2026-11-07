"""Turn an extracted graph JSON into a networkx DiGraph.

Filler entities are not nodes; they are kept as a count on the graph.
"""
from pathlib import Path

import networkx as nx

from src.schema import Schema, load_schema, read_yaml


def build_graph(record: dict, schema: Schema | None = None) -> nx.DiGraph:
    schema = schema or load_schema()
    g = nx.DiGraph(id=record["id"], source=record["source"], status=record["status"],
                   implicit_main=record["implicit_main"])
    g.graph["non_node_counts"] = {t: 0 for t in schema.non_node_types}
    for e in record["nodes"]:
        if e["type"] in schema.non_node_types:
            g.graph["non_node_counts"][e["type"]] += 1
            continue
        g.add_node(e["id"], type=e["type"], main=e["main"], hedged=e["hedged"], kind=e["kind"], text=e["text"])
    for r in record["edges"]:
        g.add_edge(r["from"], r["to"], type=r["type"], primary=r["primary"])
    return g


def load_graph(path: Path) -> nx.DiGraph:
    return build_graph(read_yaml(path))
