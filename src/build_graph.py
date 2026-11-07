"""Step 3: graph JSON -> networkx.DiGraph.

TODO (Task 4): extend if needed. Contract: node attrs `type`, `text`, `main`; edge attr `type`.
"""

import networkx as nx


def build_graph(graph: dict) -> nx.DiGraph:
    g = nx.DiGraph()
    for n in graph["nodes"]:
        g.add_node(n["id"], type=n["type"], text=n["text"], main=n.get("main", False))
    for e in graph["edges"]:
        g.add_edge(e["from"], e["to"], type=e["type"])
    return g
