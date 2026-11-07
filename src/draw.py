"""Step 3: networkx graph -> matplotlib Figure.

TODO (Task 5): nicer layout and legend. Contract: take a DiGraph, return a Figure.
"""

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.figure import Figure

COLORS = {
    "claim": "#2a78d6",
    "reason": "#3aa655",
    "evidence": "#8fc97a",
    "refutation": "#d64545",
    "rebuttal": "#eb6834",
    "condition": "#9b6bd6",
    "recommendation": "#e0b400",
}


def draw(g: nx.DiGraph, title: str = "") -> Figure:
    fig, ax = plt.subplots(figsize=(6, 5))
    pos = nx.spring_layout(g, seed=0)
    colors = [COLORS.get(g.nodes[n]["type"], "#999999") for n in g]
    sizes = [1400 if g.nodes[n]["main"] else 800 for n in g]
    labels = {n: f"{n}\n{g.nodes[n]['type']}" for n in g}
    nx.draw_networkx(g, pos, ax=ax, node_color=colors, node_size=sizes, labels=labels,
                     font_size=7, arrowsize=15)
    nx.draw_networkx_edge_labels(g, pos, ax=ax, font_size=7,
                                 edge_labels={(u, v): d["type"] for u, v, d in g.edges(data=True)})
    ax.set_title(title)
    ax.axis("off")
    return fig
