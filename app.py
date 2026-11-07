"""Streamlit UI. Run from the repo root: uv run streamlit run app.py"""
import hashlib
import random

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src import pipeline
from src.draw import highlight_html, legend_html
from src.viz3d import render_html
from src.extract import load_items
from src.schema import ROOT
from src.settings import get_settings

KEY_MEASURES = ["n_nodes", "n_edges", "n_filler", "depth", "longest_path", "main_position",
                "n_attacks", "answered_attack_share", "n_qualifies", "n_conflicts", "hedged_share"]

settings = get_settings()
st.set_page_config(page_title="Argument graphs", layout="wide")
st.title("Do LLMs argue like humans?")


@st.cache_data
def count_pairs(path: str) -> int:
    with open(path) as f:
        return sum(1 for line in f if line.strip())


# ---- 1. Input ---------------------------------------------------------------
with st.sidebar:
    mode = st.radio("Input", ["Dataset", "Own text"])
    force = st.checkbox("Re-extract", help="Saved graphs are reused to save API credit. Tick to call Claude again.")
    st.caption(f"Extractor: `{settings.backend}` · `{settings.model}` · effort `{settings.effort}`  \n"
               f"Prompt: `{settings.prompt_path.name}` · saved to `{settings.output_dir.relative_to(ROOT)}/graphs/`")

if mode == "Dataset":
    if not settings.data_path.exists():
        st.error(f"Dataset not found: `{settings.data_path}`. Run `uv run scripts/get_data.py`.")
        st.stop()
    n = count_pairs(str(settings.data_path))
    with st.sidebar:
        if st.button("🎲 Random pair"):
            st.session_state.pair = random.randrange(n)
        pair = st.number_input(f"Pair (0–{n - 1})", 0, n - 1, key="pair")
    items = load_items(settings.data_path, [int(pair)], ["human", "chatgpt"])
else:
    question = st.text_input("Question")
    answer = st.text_area("Answer", height=180)
    uid = hashlib.sha1(f"{question}\n{answer}".encode()).hexdigest()[:10]
    items = [{"id": f"user_{uid}", "pair": None, "source": "user", "question": question, "answer": answer}]
    if not (question and answer):
        st.info("Type a question and an answer.")
        st.stop()

st.subheader(items[0]["question"])

# ---- 2-5. Extract -> YAML -> graph -> draw ----------------------------------
# Saved YAML is drawn at once (free). Calling Claude needs a click.
saved = all(pipeline.graph_path(it["id"], settings).exists() for it in items)
if force or not saved:
    if not st.button("Extract and draw (calls Claude)", type="primary"):
        for col, it in zip(st.columns(len(items)), items):
            col.markdown(f"**{it['source']}** · {len(it['answer'].split())} words")
            col.write(it["answer"])
        st.stop()

with st.spinner(f"Extracting with {settings.model}… (about 1 minute per answer)"):
    results = pipeline.run(items, settings, force=force)

tab3d, tab2d = st.tabs(["3D shape (Mind Graft view)", "2D graph"])
with tab3d:  # both answers in one space: z = words, y = depth, x = opposition
    if any(r.graph.number_of_nodes() for r in results):
        components.html(render_html(items[0]["question"], {it["source"]: r.doc for it, r in zip(items, results)}), height=680)
    else:
        st.info("No graph to draw yet.")
with tab2d:
    st.markdown(legend_html(), unsafe_allow_html=True)
    cols2d = st.columns(len(items))
for col, it, r in zip(cols2d, items, results):
    with col:
        doc = r.doc
        st.markdown(f"#### {it['source']} · {len(it['answer'].split())} words")
        if doc["status"] == "valid":
            st.success(f"valid · {r.graph.number_of_nodes()} nodes · {r.graph.number_of_edges()} edges · "
                       f"{sum(n['type'] == 'filler' for n in doc['nodes'])} filler")
        else:
            st.error(f"{doc['status']}: " + "; ".join(doc["errors"])[:500])
        if r.graph.number_of_nodes():
            st.graphviz_chart(r.dot, width="stretch")
        with st.expander("Answer, split into entities"):
            st.markdown(highlight_html(doc), unsafe_allow_html=True)
        with st.expander("Graph YAML (extractor output)"):
            text = r.path.read_text()
            st.download_button("Download", text, file_name=r.path.name, key=f"dl_{it['id']}")
            st.code(text, language="yaml")

# ---- Measures (src/measure.py) ----------------------------------------------
table = {it["source"]: r.measures for it, r in zip(items, results) if r.measures}
if table:
    st.markdown("#### Measures")
    st.caption("One pair only: for inspecting the extractor, not a finding (CLAUDE.md: baseline + hand check first).")
    st.dataframe(pd.DataFrame(table).loc[KEY_MEASURES], width="stretch")
for it, r in zip(items, results):
    if r.measure_errors and r.doc.get("nodes"):
        st.warning(f"{it['source']}: measure.py skipped this graph: " + "; ".join(r.measure_errors))
