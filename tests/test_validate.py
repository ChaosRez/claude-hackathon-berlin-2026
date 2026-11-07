import copy

import pytest

from src.schema import load_schema
from src.validate import validate

SCHEMA = load_schema()
ANSWER = ("Great question! In most cases, investing is the better choice. "
          "Stocks have returned more than mortgage rates. However, paying off the loan is risk-free.")


def ent(i, t, text, main=False, kind=None, note=None):
    return {"id": i, "type": t, "text": text, "main": main, "hedged": False, "kind": kind, "note": note}


GOOD = {
    "implicit_main": False,
    "entities": [
        ent(1, "filler", "Great question!"),
        ent(2, "claim", "In most cases, investing is the better choice.", main=True),
        ent(3, "reason", "Stocks have returned more than mortgage rates."),
        ent(4, "counterpoint", "However, paying off the loan is risk-free."),
    ],
    "relations": [{"from": 3, "to": 2, "type": "supports"}, {"from": 4, "to": 2, "type": "attacks"}],
}


def mutate(fn):
    g = copy.deepcopy(GOOD)
    fn(g)
    return validate(g, ANSWER, SCHEMA)


def test_schema_loads_types_from_yaml():
    assert "counterpoint" in SCHEMA.entity_types and "refutation" not in SCHEMA.entity_types
    assert SCHEMA.non_node_types == {"filler"}
    assert set(SCHEMA.relation_types) == {"supports", "illustrates", "attacks", "answers", "qualifies", "concludes"}
    assert SCHEMA.evidence_kinds == ("fact", "example", "personal", "source")


def test_good_graph_is_valid():
    assert validate(GOOD, ANSWER, SCHEMA) == []


def test_punctuation_and_spacing_differences_are_ignored():
    assert validate(GOOD, ANSWER.replace("! ", "!\n\n"), SCHEMA) == []


@pytest.mark.parametrize("fn, expected", [
    (lambda g: g["entities"].pop(), "coverage"),
    (lambda g: g["entities"][2].update(text="Stocks returned more."), "coverage"),
    (lambda g: g["entities"][1].update(main=False), "exactly one main"),
    (lambda g: g["entities"][2].update(main=True), "exactly one main"),
    (lambda g: g["entities"][2].update(type="refutation"), "unknown type"),
    (lambda g: g["relations"].pop(), "exactly one outgoing edge"),
    (lambda g: g["relations"].append({"from": 2, "to": 3, "type": "supports"}), "main entity must have no"),
    (lambda g: g["relations"].append({"from": 1, "to": 2, "type": "supports"}), "not a graph node"),
    (lambda g: g["relations"].append({"from": 3, "to": 9, "type": "supports"}), "missing entity"),
    (lambda g: g["relations"][0].update(type="contradicts"), "unknown type"),
    (lambda g: g["entities"][2].update(type="evidence"), "evidence needs kind"),
    (lambda g: g["entities"][2].update(kind="fact"), "kind is only for evidence"),
    (lambda g: g["entities"][3].update(type="other"), "other needs a note"),
    (lambda g: g["entities"][1].update(id=7), "entity ids"),
])
def test_rule_violations_are_reported(fn, expected):
    errors = mutate(fn)
    assert any(expected in e for e in errors), errors


def test_edge_optional_types_may_have_no_edge():
    def fn(g):
        g["entities"][3].update(type="background")
        g["relations"].pop()
    assert mutate(fn) == []


def test_implicit_main_allows_no_main():
    def fn(g):
        g["implicit_main"] = True
        g["entities"][1].update(main=False)
        g["relations"].append({"from": 2, "to": 3, "type": "concludes"})
    assert mutate(fn) == []


def test_build_graph_skips_filler():
    try:
        from src.build_graph import build_graph
    except Exception as exc:  # networkx fails to import on Python 3.14.1 (dataclass slots bug)
        pytest.skip(f"networkx does not import here: {exc!r}")
    g = build_graph({**GOOD, "id": "x", "source": "human", "status": "valid"}, SCHEMA)
    assert sorted(g.nodes) == [2, 3, 4]
    assert g.graph["non_node_counts"] == {"filler": 1}
    assert g.edges[3, 2]["type"] == "supports"
