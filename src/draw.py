"""Draw a reasoning graph as Graphviz DOT. Streamlit renders it with st.graphviz_chart.

Design:
- One color per FAMILY of entity types, so related roles look alike.
- The main claim sits at the top. Primary edges (the tree) set the layout and are solid;
  extra edges are dashed and do not move the layout.
- Main claim: double border. Hedged entity: dashed border.
"""
import html
import textwrap

import networkx as nx

# family: (fill, border, entity types)
FAMILIES = {
    "position": ("#dbe8fb", "#2a78d6", ("claim", "recommendation")),
    "support": ("#dcf1e0", "#2e9b4a", ("reason", "evidence")),
    "debate": ("#fde2dc", "#d6453d", ("counterpoint", "rebuttal")),
    "scope": ("#ece2f9", "#8a5cd0", ("condition", "caveat")),
    "context": ("#ececea", "#7a7a75", ("background", "other")),
}
NODE_STYLE = {t: (fill, border) for fill, border, types in FAMILIES.values() for t in types}
DEFAULT_STYLE = ("#ffffff", "#999999")

# relation: color. Same idea: relations with the same effect share a color.
EDGE_COLORS = {
    "supports": "#2e9b4a", "concludes": "#2e9b4a",
    "attacks": "#d6453d", "conflicts": "#8b0000",
    "refutes": "#eb6834",
    "qualifies": "#8a5cd0",
    "summarizes": "#2a78d6",
    "explains": "#7a7a75", "elaborates": "#7a7a75",
}


def _esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _label(nid, d: dict, width: int = 28, max_lines: int = 4) -> str:
    head = f"#{nid} {d['type']}" + (f" ({d['kind']})" if d.get("kind") else "") + ("  ★ MAIN" if d.get("main") else "")
    lines = textwrap.wrap(d.get("text", ""), width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] += " …"
    return _esc(head + "\n" + "\n".join(lines))


def to_dot(g: nx.DiGraph) -> str:
    out = [
        "digraph G {",
        '  rankdir=BT; bgcolor="transparent"; nodesep=0.35; ranksep=0.55;',
        '  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=13, margin="0.14,0.08"];',
        '  edge [fontname="Helvetica", fontsize=11, arrowsize=0.8];',
    ]
    for nid, d in sorted(g.nodes(data=True)):
        fill, border = NODE_STYLE.get(d["type"], DEFAULT_STYLE)
        style = "rounded,filled" + (",dashed" if d.get("hedged") else "")
        extra = ", peripheries=2, penwidth=2.2" if d.get("main") else ", penwidth=1.3"
        out.append(f'  {nid} [label="{_label(nid, d)}", fillcolor="{fill}", color="{border}", '
                   f'style="{style}", tooltip="{_esc(d.get("text", ""))}"{extra}];')
    for a, b, d in g.edges(data=True):
        color = EDGE_COLORS.get(d["type"], "#555555")
        if d.get("primary"):
            look = "penwidth=1.6"
        else:  # extra edge: shown, but does not shape the tree
            look = 'style="dotted", penwidth=1.2' if d["type"] == "conflicts" else 'style="dashed", constraint=false'
        out.append(f'  {a} -> {b} [label=" {d["type"]}", color="{color}", fontcolor="{color}", {look}];')
    out.append("}")
    return "\n".join(out)


def legend_html() -> str:
    chip = ('<span style="display:inline-block;margin:2px 10px 2px 0;padding:1px 8px;border-radius:6px;'
            'background:{fill};border:1.5px solid {border};font-size:0.8em">{text}</span>')
    nodes = "".join(chip.format(fill=f, border=b, text=f"<b>{name}</b>: {', '.join(t)}")
                    for name, (f, b, t) in FAMILIES.items())
    by_color: dict[str, list[str]] = {}
    for rel, c in EDGE_COLORS.items():
        by_color.setdefault(c, []).append(rel)
    edges = "".join(f'<span style="color:{c};margin-right:12px;font-size:0.8em">━ {", ".join(r)}</span>'
                    for c, r in by_color.items())
    marks = ('<span style="font-size:0.8em;color:#666">double border = main claim · dashed border = hedged · '
             'solid arrow = primary edge (tree) · dashed arrow = extra edge</span>')
    return f"<div>{nodes}</div><div>{edges}</div><div>{marks}</div>"


def highlight_html(doc: dict) -> str:
    """The answer, split into its entities, colored like the graph. Filler is grey italic."""
    parts = []
    for n in doc.get("nodes", []):
        text = html.escape(n["text"])
        if n["type"] == "filler":
            parts.append(f'<span style="color:#999;font-style:italic">{text}</span>')
            continue
        fill, border = NODE_STYLE.get(n["type"], DEFAULT_STYLE)
        weight = "font-weight:600;" if n.get("main") else ""
        parts.append(f'<span title="#{n["id"]} {n["type"]}" style="background:{fill};border-bottom:2px solid '
                     f'{border};{weight}padding:1px 2px;border-radius:3px"><sup>{n["id"]}</sup>{text}</span>')
    return '<div style="line-height:1.9">' + " ".join(parts) + "</div>"
