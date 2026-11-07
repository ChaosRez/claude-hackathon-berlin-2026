"""Step 1 output -> one record per question: {question, human, chatgpt}."""

from pathlib import Path

import pandas as pd

TEXT_COLUMNS = ("human", "chatgpt")


def _first(value) -> str:
    """HC3 stores answers as lists; a CSV stores plain strings."""
    if isinstance(value, (list, tuple)) or hasattr(value, "tolist"):
        value = list(value)
        return str(value[0]) if value else ""
    return "" if pd.isna(value) else str(value)


def load_pairs(path: Path) -> list[dict]:
    """Load .jsonl or .csv and return [{"id", "question", "human", "chatgpt"}, ...]."""
    path = Path(path)
    df = pd.read_csv(path) if path.suffix == ".csv" else pd.read_json(path, lines=True)
    human_col = "human_answers" if "human_answers" in df else "human"
    gpt_col = "chatgpt_answers" if "chatgpt_answers" in df else "chatgpt"
    return [
        {
            "id": f"finance_{i:04d}",
            "question": str(row["question"]),
            "human": _first(row[human_col]),
            "chatgpt": _first(row[gpt_col]),
        }
        for i, row in df.iterrows()
    ]
