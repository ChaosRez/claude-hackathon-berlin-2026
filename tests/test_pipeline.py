from src import pipeline
from src.data import load_pairs
from src.settings import Settings


def test_mock_pipeline_end_to_end():
    r = pipeline.run("Q?", "Some answer.", "human", Settings(mock_llm=True))
    assert r.errors == []
    assert r.graph.number_of_nodes() == 6
    assert r.figure is not None


def test_load_csv(tmp_path):
    p = tmp_path / "pairs.csv"
    p.write_text("question,human,chatgpt\nQ?,h text,c text\n")
    assert load_pairs(p)[0] == {"id": "finance_0000", "question": "Q?", "human": "h text", "chatgpt": "c text"}
