import copy
import json
from pathlib import Path

import pytest

from src import measure

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
    "implicit_main": False,
    "edges": [
        {"from": 2, "to": 1, "type": "supports", "primary": True},
        {"from": 3, "to": 1, "type": "attacks", "primary": True},
        {"from": 4, "to": 3, "type": "refutes", "primary": True},
        {"from": 5, "to": 1, "type": "qualifies", "primary": True},
        {"from": 6, "to": 5, "type": "concludes", "primary": True},
    ],
}
EXAMPLE["answer"] = " ".join(n["text"] for n in EXAMPLE["nodes"])


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
    (lambda g: g["nodes"][1].pop("main"), "exactly one main"),
    (lambda g: g["edges"].pop(0), "outgoing edge"),
    (lambda g: g["edges"][0].update(type="illustrates"), "unknown type"),
    (lambda g: g["edges"][0].update(primary=False), "primary"),
    (lambda g: g["edges"].append({"from": 0, "to": 1, "type": "supports", "primary": False}), "filler"),
    (lambda g: g["nodes"][2].update(text="Stocks returned more."), "coverage"),
    (lambda g: g.pop("answer"), "no `answer`"),
    (lambda g: g.update(implicit_main=True) or g["nodes"][1].update(main=False)
     or g["edges"].append({"from": 1, "to": 2, "type": "concludes", "primary": True}), "implicit_main"),
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


def test_types_come_from_yaml_definitions():
    yaml = pytest.importorskip("yaml")
    root = Path(__file__).resolve().parents[1]
    entities = yaml.safe_load((root / "entity_definition.yaml").read_text())["entities"]
    relations = yaml.safe_load((root / "relation.yaml").read_text())["relations"]
    assert measure.GRAPH_TYPES == [t for t in entities if t != "filler"]
    assert measure.RELATION_TYPES == list(relations)


def test_extractor_output_is_measurable(tmp_path):
    """A graph in the extractor's YAML format (extra keys, ids from 1) is checked and measured."""
    from src.schema import write_yaml

    g = copy.deepcopy(EXAMPLE)
    for n in g["nodes"]:
        n["id"] += 1
        n.setdefault("main", False)
        n.setdefault("hedged", False)
        n.update(kind=None, note=None)
    for e in g["edges"]:
        e["from"] += 1
        e["to"] += 1
    g.update(pair=0, status="valid", errors=[], attempts=[])
    write_yaml(tmp_path / "finance_0000_human.yaml", g)
    table, invalid = measure.load(tmp_path)
    assert invalid == []
    assert table.loc[0, "depth"] == 2
