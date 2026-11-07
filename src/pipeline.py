"""The whole flow for one text: extract -> validate -> build_graph -> draw.

No Streamlit here, so a batch script can reuse it for all 100 pairs later.
"""

from dataclasses import dataclass, field

import networkx as nx
from matplotlib.figure import Figure

from src.build_graph import build_graph
from src.draw import draw
from src.extract import extract
from src.settings import Settings
from src.validate import validate


@dataclass
class Result:
    source: str  # "human" | "chatgpt" | "user"
    graph_json: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    graph: nx.DiGraph | None = None
    figure: Figure | None = None


def run(question: str, text: str, source: str, settings: Settings) -> Result:
    result = Result(source=source)
    try:
        result.graph_json = extract(question, text, settings)
    except Exception as exc:  # show the failure in the UI, don't hide it
        result.errors = [f"extract failed: {exc}"]
        return result

    result.errors = validate(result.graph_json)
    try:
        result.graph = build_graph(result.graph_json)
        result.figure = draw(result.graph, title=source)
    except Exception as exc:
        result.errors.append(f"build/draw failed: {exc}")
    return result
