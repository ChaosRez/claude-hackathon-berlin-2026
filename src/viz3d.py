"""3D view of one answer pair, after Mind Graft's Language Analyser (single-row view).

Source of the idea and the WebGL code: mind-graft/viewer/language_analyser.template.html.
Axes, as in Mind Graft:
  z = word position of the entity in the answer (filler takes words but is not drawn)
  y = depth: steps from the question. Main claim = 1; others = 1 + depth of their primary target.
  x = opposition, from the entity type (X_BY_TYPE).
Encodings, as in Mind Graft: colour = who wrote it, 3D shape = entity type, line style = relation.

Our schema has more types and relations than Mind Graft's codebook, so two maps adapt them.
They are a design choice, not part of the team's schema: change them here if the team disagrees.
"""
import json
from pathlib import Path

TEMPLATE = Path(__file__).with_name("viz3d.template.html")

# Mind Graft: opposing view -1, hedge -0.5, rebuttal +0.5, everything else 0.
X_BY_TYPE = {"counterpoint": -1.0, "condition": -0.5, "caveat": -0.5, "rebuttal": 0.5}

# Our 9 relations -> Mind Graft's 4 line styles.
LINE_STYLE = {
    "supports": "supports", "concludes": "supports", "explains": "supports", "elaborates": "supports",
    "attacks": "disagrees", "refutes": "disagrees", "conflicts": "disagrees",
    "qualifies": "qualifies",
    "summarizes": "reinforces",
}


def answer_layout(doc: dict) -> dict:
    """One extractor YAML document -> entities with (mid word, depth, x) and links."""
    nodes, edges = doc.get("nodes", []), doc.get("edges", [])
    ents, index, word = [], {}, 0
    for n in nodes:
        n_words = len(n["text"].split())
        if n["type"] != "filler":
            index[n["id"]] = len(ents)
            ents.append({"id": n["id"], "type": n["type"], "text": n["text"], "main": bool(n.get("main")),
                         "hedged": bool(n.get("hedged")), "mid": word + n_words / 2,
                         "x": X_BY_TYPE.get(n["type"], 0.0)})
        word += n_words

    primary = {e["from"]: e["to"] for e in edges if e.get("primary")}

    def depth(nid: int, seen: frozenset = frozenset()) -> int:
        target = primary.get(nid)
        if target is None or target not in index or target in seen:
            return 1  # main claim, or no primary edge: builds on the question directly
        return 1 + depth(target, seen | {nid})

    for e in ents:
        e["depth"] = depth(e["id"])

    links = [{"from": index[e["from"]], "to": index[e["to"]], "type": e["type"],
              "style": LINE_STYLE.get(e["type"], "supports"), "primary": bool(e.get("primary"))}
             for e in edges if e["from"] in index and e["to"] in index]
    links += [{"from": k, "to": -1, "type": "answers the question", "style": "supports", "primary": True}
              for k, e in enumerate(ents) if e["main"]]  # -1 = the question node
    return {"words": word, "ents": ents, "links": links}


def render_html(question: str, docs: dict[str, dict]) -> str:
    """docs: {"human": yaml_doc, "chatgpt": yaml_doc} (or {"user": ...}). Returns one self-contained page."""
    data = {"question": question,
            "sides": [{"name": side, **answer_layout(doc)} for side, doc in docs.items() if doc.get("nodes")]}
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return TEMPLATE.read_text(encoding="utf-8").replace("/*DATA*/", payload, 1)
