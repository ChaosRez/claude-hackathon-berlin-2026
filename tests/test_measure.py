import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import measure  # noqa: E402

# The worked example from GUIDE.md section 5, using the draft types.
EXAMPLE = {
    "id": "example_human",
    "source": "human",
    "question": "Should I pay off my mortgage early or invest?",
    "nodes": [
        {"id": 0, "type": "filler", "text": "Good question!"},
        {"id": 1, "type": "claim", "text": "In most cases, investing is the better choice.",
         "main": True, "hedged": True},
        {"id": 2, "type": "reason", "text": "Stocks have historically returned more."},
        {"id": 3, "type": "counterpoint", "text": "However, paying off the loan is risk-free."},
        {"id": 4, "type": "rebuttal", "text": "That matters less when your rate is low."},
        {"id": 5, "type": "condition", "text": "If your rate is above 6%, paying it off can make sense."},
        {"id": 6, "type": "recommendation", "text": "So check your rate before you decide."},
    ],
    "edges": [
        {"from": 2, "to": 1, "type": "supports", "primary": True},
        {"from": 3, "to": 1, "type": "attacks", "primary": True},
        {"from": 4, "to": 3, "type": "refutes", "primary": True},
        {"from": 5, "to": 1, "type": "qualifies", "primary": True},
        {"from": 6, "to": 5, "type": "concludes", "primary": True},
    ],
}


def test_example_is_valid():
    assert measure.check(EXAMPLE) == []


def test_example_measures():
    m = measure.measures(EXAMPLE)
    assert m["n_nodes"] == 6
    assert m["n_edges"] == 5
    assert m["n_filler"] == 1
    assert m["depth"] == 2
    assert m["longest_path"] == 2
    assert m["main_in_degree"] == 3
    assert m["n_leaves"] == 3
    assert m["main_position"] == 0.0
    assert m["answered_attack_share"] == 1.0
    assert m["has_cycle"] == 0
    assert m["extra_edge_share"] == 0.0
    assert m["hedged_share"] == pytest.approx(1 / 6)


def test_extra_edge_lengthens_longest_path_but_not_depth():
    g = copy.deepcopy(EXAMPLE)
    # The recommendation also follows from the rebuttal: 6 -> 4 -> 3 -> 1.
    g["edges"].append({"from": 6, "to": 4, "type": "concludes", "primary": False})
    assert measure.check(g) == []
    m = measure.measures(g)
    assert m["longest_path"] == 3
    assert m["depth"] == 2
    assert m["extra_edge_share"] == pytest.approx(1 / 6)


def test_cycle_is_counted_not_dropped():
    g = copy.deepcopy(EXAMPLE)
    g["edges"].append({"from": 1, "to": 2, "type": "elaborates", "primary": False})
    assert measure.check(g) == []
    m = measure.measures(g)
    assert m["has_cycle"] == 1
    assert m["longest_path"] == 2  # cycle {1,2} merged: 4 -> 3 -> {1,2}


@pytest.mark.parametrize("change, message", [
    (lambda g: g["nodes"][1].pop("main"), "main claims"),
    (lambda g: g["edges"].pop(0), "no outgoing edge"),
    (lambda g: g["edges"][0].update(type="illustrates"), "unknown type"),
    (lambda g: g["edges"][0].update(primary=False), "primary"),
    (lambda g: g["edges"].append({"from": 0, "to": 1, "type": "supports"}), "filler"),
])
def test_invalid_graphs_are_caught(change, message):
    g = copy.deepcopy(EXAMPLE)
    change(g)
    assert any(message in e for e in measure.check(g))


def test_load_counts_invalid_graphs(tmp_path):
    (tmp_path / "ok.json").write_text(json.dumps(EXAMPLE))
    bad = copy.deepcopy(EXAMPLE)
    bad["edges"] = []
    (tmp_path / "bad.json").write_text(json.dumps(bad))
    table, invalid = measure.load(tmp_path)
    assert len(table) == 1
    assert [name for name, _, _ in invalid] == ["bad.json"]


def test_types_match_yaml_definitions():
    yaml = pytest.importorskip("yaml")
    entities = yaml.safe_load((ROOT / "entity_definition.yaml").read_text())["entities"]
    relations = yaml.safe_load((ROOT / "relation.yaml").read_text())["relations"]
    assert list(entities) == measure.ENTITY_TYPES
    assert list(relations) == measure.RELATION_TYPES
