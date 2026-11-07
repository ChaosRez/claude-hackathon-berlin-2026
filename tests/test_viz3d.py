"""3D layout (after Mind Graft): word position, depth, opposition, line styles."""
from pathlib import Path

from src.schema import load_schema, read_yaml
from src.viz3d import LINE_STYLE, answer_layout, render_html

DOC = read_yaml(Path(__file__).parent / "fixtures" / "example_graph.yaml")


def test_every_relation_has_a_line_style():
    assert set(load_schema().relation_types) <= set(LINE_STYLE)


def test_layout_axes():
    lay = answer_layout(DOC)
    by_id = {e["id"]: e for e in lay["ents"]}
    assert 1 not in by_id  # filler is not drawn
    assert lay["words"] == len(DOC["answer"].split())  # filler words still count on z
    assert by_id[2]["mid"] > 2  # claim starts after "Good question!"
    assert by_id[2]["depth"] == 1 and by_id[3]["depth"] == 2 and by_id[4]["depth"] == 3  # evidence -> reason -> claim
    assert by_id[5]["x"] == -1.0 and by_id[6]["x"] == 0.5 and by_id[7]["x"] == -0.5
    assert sum(1 for l in lay["links"] if l["to"] == -1) == 1  # main claim builds on the question


def test_render_embeds_data_safely():
    page = render_html("Q </script>?", {"human": DOC, "chatgpt": DOC})
    assert "/*DATA*/" not in page and "Q <\\/script>?" in page
