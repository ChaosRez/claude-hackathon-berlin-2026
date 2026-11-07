"""Connect the steps for one answer:

    answer --extract--> graphs/<id>.yaml --build_graph--> networkx --draw--> DOT
                                         --measure-->     numbers

Step 2 is the team's extractor (src/extract.py), unchanged. Its YAML output is the
single hand-over point: the graph and the measures are always read from that file.
No Streamlit here, so scripts can reuse it.
"""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import networkx as nx

from src import extract
from src.build_graph import load_graph
from src.draw import to_dot
from src.measure import check, measures
from src.schema import load_schema, read_yaml, write_yaml
from src.settings import Settings


@dataclass
class Result:
    path: Path
    doc: dict  # the YAML file's content
    graph: nx.DiGraph
    dot: str
    measures: dict | None  # None when src.measure.check finds problems
    measure_errors: list[str]


def graph_path(item_id: str, settings: Settings) -> Path:
    return settings.output_dir / "graphs" / f"{item_id}.yaml"


def extract_to_yaml(item: dict, settings: Settings) -> Path:
    """Step 2: run the team's extractor on one answer and save its output as YAML."""
    schema = load_schema()
    prompts = {"one-pass": extract.build_system_prompt(settings.prompt_path, schema),
               "split": extract.build_system_prompt(settings.split_prompt, schema),
               "label": extract.build_system_prompt(settings.label_prompt, schema)}
    args = SimpleNamespace(backend=settings.backend, model=settings.model, effort=settings.effort,
                           retries=settings.retries, votes=settings.votes)
    record = extract.EXTRACTORS[settings.approach](item, prompts, schema, args)
    path = graph_path(item["id"], settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_yaml(path, extract.graph_document(record))
    return path


def load_result(path: Path) -> Result:
    """Steps 3-5: YAML file -> graph -> drawing + measures."""
    doc = read_yaml(path)
    g = load_graph(path)
    errors = check(doc) if doc.get("nodes") else ["no nodes"]
    return Result(path, doc, g, to_dot(g), None if errors else measures(doc), errors)


def run(items: list[dict], settings: Settings, force: bool = False) -> list[Result]:
    """Extract the items that have no saved YAML yet (all of them if force), in parallel."""
    todo = [it for it in items if force or not graph_path(it["id"], settings).exists()]
    if todo:
        with ThreadPoolExecutor(max_workers=len(todo)) as pool:
            list(pool.map(lambda it: extract_to_yaml(it, settings), todo))
    return [load_result(graph_path(it["id"], settings)) for it in items]
