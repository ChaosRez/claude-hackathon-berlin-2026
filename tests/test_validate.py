import copy

import pytest

from src.schema import load_schema
from src.validate import validate

SCHEMA = load_schema()
ANSWER = ("Great question! In most cases, investing is the better choice. "
          "Stocks have returned more than mortgage rates. However, paying off the loan is risk-free.")


def node(i, t, text, main=False, kind=None, note=None):
    return {"id": i, "type": t, "text": text, "main": main, "hedged": False, "kind": kind, "note": note}


def edge(a, b, t, primary=True):
    return {"from": a, "to": b, "type": t, "primary": primary}


GOOD = {
    "implicit_main": False,
    "nodes": [
        node(1, "filler", "Great question!"),
        node(2, "claim", "In most cases, investing is the better choice.", main=True),
        node(3, "reason", "Stocks have returned more than mortgage rates."),
        node(4, "counterpoint", "However, paying off the loan is risk-free."),
    ],
    "edges": [edge(3, 2, "supports"), edge(4, 2, "attacks")],
}


def mutate(fn):
    g = copy.deepcopy(GOOD)
    fn(g)
    return validate(g, ANSWER, SCHEMA)


def test_schema_loads_types_from_yaml():
    assert "counterpoint" in SCHEMA.entity_types and "refutation" not in SCHEMA.entity_types
    assert SCHEMA.non_node_types == {"filler"}
    assert set(SCHEMA.relation_types) == {"supports", "attacks", "refutes", "qualifies", "explains",
                                          "elaborates", "summarizes", "concludes", "conflicts"}
    assert SCHEMA.never_primary == {"conflicts"}
    assert SCHEMA.evidence_kinds == ("fact", "example", "personal", "source")


def test_good_graph_is_valid():
    assert validate(GOOD, ANSWER, SCHEMA) == []


def test_punctuation_and_spacing_differences_are_ignored():
    assert validate(GOOD, ANSWER.replace("! ", "!\n\n"), SCHEMA) == []


def test_extra_non_primary_edges_are_allowed():
    def fn(g):
        g["edges"].append(edge(4, 3, "attacks", primary=False))
        g["edges"].append(edge(2, 4, "conflicts", primary=False))  # main may have non-primary edges
    assert mutate(fn) == []


@pytest.mark.parametrize("fn, expected", [
    (lambda g: g["nodes"].pop(), "coverage"),
    (lambda g: g["nodes"][2].update(text="Stocks returned more."), "coverage"),
    (lambda g: g["nodes"][1].update(main=False), "exactly one main"),
    (lambda g: g["nodes"][2].update(main=True), "exactly one main"),
    (lambda g: g["nodes"][2].update(type="refutation"), "unknown type"),
    (lambda g: g["edges"].pop(), "at least one outgoing edge"),
    (lambda g: g["edges"][0].update(primary=False), "exactly 1 primary edge"),
    (lambda g: g["edges"].append(edge(3, 4, "supports")), "exactly 1 primary edge"),
    (lambda g: g["edges"].append(edge(2, 3, "concludes")), "main node cannot have a primary edge"),
    (lambda g: g["edges"].append(edge(3, 2, "explains", primary=False)), "same pair"),
    (lambda g: g["edges"].append(edge(3, 3, "supports", primary=False)), "self loop"),
    (lambda g: g["edges"].append(edge(1, 2, "supports")), "touches filler"),
    (lambda g: g["edges"].append(edge(3, 9, "supports", primary=False)), "missing node"),
    (lambda g: g["edges"][0].update(type="illustrates"), "unknown type"),
    (lambda g: g["edges"][1].update(type="conflicts"), "cannot be primary"),
    (lambda g: g["edges"].__setitem__(slice(None), [edge(3, 4, "supports"), edge(4, 3, "attacks")]), "never reach the main"),
    (lambda g: g["nodes"][2].update(type="evidence"), "evidence needs kind"),
    (lambda g: g["nodes"][2].update(kind="fact"), "kind is only for evidence"),
    (lambda g: g["nodes"][3].update(type="other"), "other needs a note"),
    (lambda g: g["nodes"][1].update(id=7), "node ids"),
    (lambda g: g["nodes"][2].update(id=2), "node ids"),
])
def test_rule_violations_are_reported(fn, expected):
    errors = mutate(fn)
    assert any(expected in e for e in errors), errors


def test_implicit_main_allows_no_main():
    def fn(g):
        g["implicit_main"] = True
        g["nodes"][1].update(main=False)
        g["edges"].append(edge(2, 3, "concludes"))
    assert not any("main" in e for e in mutate(fn))


def test_build_graph_skips_filler():
    try:
        from src.build_graph import build_graph
    except Exception as exc:  # networkx fails to import on Python 3.14.1 (dataclass slots bug)
        pytest.skip(f"networkx does not import here: {exc!r}")
    g = build_graph({**GOOD, "id": "x", "source": "human", "status": "valid"}, SCHEMA)
    assert sorted(g.nodes) == [2, 3, 4]
    assert g.graph["non_node_counts"] == {"filler": 1}
    assert g.edges[3, 2]["type"] == "supports"
