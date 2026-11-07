"""The app's extract step calls the team's extractor correctly. No API calls: the backend is faked.

This test fails if src/extract.py changes its entry points, so the app breaks in CI, not on screen.
"""
from pathlib import Path

import pytest

from src import extract, pipeline
from src.schema import read_yaml
from src.settings import get_settings

FIXTURE = read_yaml(Path(__file__).parent / "fixtures" / "example_graph.yaml")


def fake_call(system, user, json_schema, model, effort):
    """Answer like the model would: pieces for the split step, labels for the label step, full graph for one-pass."""
    props = json_schema["properties"]
    meta = {"model": "fake"}
    if "segments" in props:
        return {"segments": [n["text"] for n in FIXTURE["nodes"]]}, meta
    with_text = "text" in props["nodes"]["items"]["properties"]
    nodes = [{k: v for k, v in n.items() if with_text or k != "text"} for n in FIXTURE["nodes"]]
    return {"nodes": nodes, "edges": FIXTURE["edges"], "implicit_main": False}, meta


@pytest.mark.parametrize("approach", ["voted", "one-pass"])
def test_extract_to_yaml_with_fake_backend(approach, tmp_path, monkeypatch):
    monkeypatch.setitem(extract.BACKENDS, "fake", fake_call)
    base = get_settings()
    settings = base.__class__(**{**base.__dict__, "backend": "fake", "approach": approach, "votes": 2,
                                 "output_dir": tmp_path})
    item = {"id": "example_human", "pair": None, "source": "human",
            "question": FIXTURE["question"], "answer": FIXTURE["answer"]}
    path = pipeline.extract_to_yaml(item, settings)
    result = pipeline.load_result(path)
    assert result.doc["status"] == "valid", result.doc["errors"]
    assert result.doc["approach"] == approach
    assert result.graph.number_of_nodes() == 7 and result.measures is not None
