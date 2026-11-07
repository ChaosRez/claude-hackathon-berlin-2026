"""Streamlit UI. Run: uv run streamlit run app.py"""

import random

import streamlit as st

from src import pipeline
from src.data import TEXT_COLUMNS, load_pairs
from src.settings import get_settings

settings = get_settings()
st.set_page_config(page_title="Argument Graphs", layout="wide")
st.title("Do LLMs argue like humans?")


@st.cache_data
def cached_pairs(path: str) -> list[dict]:
    return load_pairs(path)


@st.cache_resource(show_spinner=False)
def cached_extract(question: str, text: str, source: str, model: str, prompt_version: str):
    # model + prompt_version are in the cache key, so a new prompt means a new API call.
    return pipeline.run(question, text, source, settings)


# ---- 1. Input -------------------------------------------------------------
with st.sidebar:
    st.caption(f"Model: `{settings.claude_model}` · prompt `{settings.prompt_version}`"
               + (" · **MOCK**" if settings.mock_llm else ""))
    mode = st.radio("Input", ["From dataset", "Own text"])

if mode == "From dataset":
    try:
        pairs = cached_pairs(str(settings.data_path))
    except FileNotFoundError:
        st.error(f"Dataset not found: `{settings.data_path}`. Set DATA_PATH in .env.")
        st.stop()
    with st.sidebar:
        if st.button("🎲 Random question"):
            st.session_state.idx = random.randrange(len(pairs))
        idx = st.number_input("Row", 0, len(pairs) - 1, key="idx")
    record = pairs[idx]
    question = record["question"]
    texts = {col: record[col] for col in TEXT_COLUMNS}
else:
    question = st.text_input("Question")
    texts = {"user": st.text_area("Answer", height=200)}

st.subheader(question or "—")
cols = st.columns(len(texts))
for col, (source, text) in zip(cols, texts.items()):
    col.markdown(f"**{source}** ({len(text.split())} words)")
    col.write(text)

# ---- 2-4. Extract -> validate -> graph -> draw ----------------------------
if st.button("Build graphs", type="primary", disabled=not all(texts.values())):
    cols = st.columns(len(texts))
    for col, (source, text) in zip(cols, texts.items()):
        with col, st.spinner(f"Extracting {source}..."):
            r = cached_extract(question, text, source, settings.claude_model, settings.prompt_version)
            if r.errors:
                st.warning("\n".join(f"- {e}" for e in r.errors))
            else:
                st.success("Graph is valid")
            if r.figure:
                st.pyplot(r.figure)
            with st.expander("Graph JSON"):
                st.json({k: v for k, v in r.graph_json.items() if k != "raw"})
