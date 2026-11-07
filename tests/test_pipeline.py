"""App wiring: extractor YAML -> graph -> drawing -> measures. No API calls."""
from pathlib import Path

from src import pipeline
from src.draw import NODE_STYLE, to_dot
from src.schema import load_schema, read_yaml
from src.validate import validate

FIXTURE = Path(__file__).parent / "fixtures" / "example_graph.yaml"


def test_fixture_is_a_valid_extractor_output():
    doc = read_yaml(FIXTURE)
    assert validate(doc, doc["answer"], load_schema()) == []


def test_load_result_end_to_end():
    r = pipeline.load_result(FIXTURE)
    assert r.graph.number_of_nodes() == 7  # filler is not a node
    assert r.measure_errors == []
    assert r.measures["n_attacks"] == 1
    assert r.dot.startswith("digraph") and "peripheries=2" in r.dot  # main claim marked


def test_families_share_colors():
    assert NODE_STYLE["claim"] == NODE_STYLE["recommendation"]
    assert NODE_STYLE["reason"] == NODE_STYLE["evidence"]
    assert NODE_STYLE["claim"] != NODE_STYLE["counterpoint"]


def test_extra_edges_do_not_shape_the_layout():
    dot = to_dot(pipeline.load_result(FIXTURE).graph)
    assert "8 -> 2" in dot and "constraint=false" in dot


def test_run_reuses_saved_yaml(tmp_path, monkeypatch):
    from src.settings import get_settings
    settings = get_settings().__class__(**{**get_settings().__dict__, "output_dir": tmp_path})
    target = pipeline.graph_path("example_human", settings)
    target.parent.mkdir(parents=True)
    target.write_text(FIXTURE.read_text())
    monkeypatch.setattr(pipeline, "extract_to_yaml", lambda *a: (_ for _ in ()).throw(AssertionError("API called")))
    [r] = pipeline.run([{"id": "example_human"}], settings)
    assert r.doc["status"] == "valid"
