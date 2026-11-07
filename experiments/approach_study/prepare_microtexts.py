"""Convert arg-microtexts (Peldszus & Stede) English XML into a gold JSONL.

Usage:
    python3 -I prepare_microtexts.py <corpus/en dir> <out_dir>

Each output record holds ADU nodes (reading order), the central claim,
and one primary parent edge per non-central node (a tree).
Mapping: sup/exa -> support, reb -> attack (parent = target ADU);
und -> attack, parent = source node of the targeted edge;
add (linked premise) -> same parent and label as the partner node
(the source of the edge it targets).
The data is CC BY-NC-SA 4.0: keep outputs local, never commit them.
"""

import json
import random
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ARG_TYPES = {"sup", "exa", "reb", "und", "add"}
LABEL = {"sup": "support", "exa": "support", "reb": "attack", "und": "attack"}


class Invalid(Exception):
    pass


def parse_file(path):
    root = ET.parse(path).getroot()
    if root.tag != "arggraph":
        raise Invalid(f"root tag is {root.tag}")
    tid = root.get("id")
    edus = {e.get("id"): e.text or "" for e in root.findall("edu")}
    edu_order = {eid: i for i, eid in enumerate(edus)}
    adus = {a.get("id"): a.get("type") for a in root.findall("adu")}
    edges = {e.get("id"): (e.get("src"), e.get("trg"), e.get("type")) for e in root.findall("edge")}

    seg = {}
    for src, trg, typ in edges.values():
        if typ == "seg":
            if src not in edus or trg not in adus:
                raise Invalid(f"bad seg edge {src}->{trg}")
            seg.setdefault(trg, []).append(src)
        elif typ not in ARG_TYPES:
            raise Invalid(f"unknown edge type {typ}")
    for a in adus:
        if a not in seg:
            raise Invalid(f"ADU {a} has no EDU")
        if adus[a] not in ("pro", "opp"):
            raise Invalid(f"ADU {a} has role {adus[a]}")

    # outgoing argumentative edge per ADU
    out = {}
    for eid, (src, trg, typ) in edges.items():
        if typ in ARG_TYPES:
            if src not in adus:
                raise Invalid(f"arg edge {eid} source {src} is not an ADU")
            out.setdefault(src, []).append(eid)
    multi = [a for a, es in out.items() if len(es) > 1]
    if multi:
        raise Invalid(f"ADU(s) with >1 outgoing arg edge: {multi}")
    central = [a for a in adus if a not in out]
    if len(central) != 1:
        raise Invalid(f"{len(central)} ADUs with no outgoing edge: {central}")
    central = central[0]

    def resolve(adu, seen=()):
        """Return (parent_adu, label) for a non-central ADU."""
        if adu in seen:
            raise Invalid(f"cycle while resolving {adu}")
        eid = out[adu][0]
        _, trg, typ = edges[eid]
        if typ in ("sup", "exa", "reb"):
            if trg not in adus:
                raise Invalid(f"{typ} edge {eid} targets non-ADU {trg}")
            return trg, LABEL[typ]
        if typ == "und":
            if trg not in edges or edges[trg][2] not in ARG_TYPES:
                raise Invalid(f"und edge {eid} targets non-arg-edge {trg}")
            return edges[trg][0], "attack"
        # add: join the partner node (source of targeted edge, or the node itself)
        if trg in edges:
            partner = edges[trg][0]
        elif trg in adus:
            partner = trg
        else:
            raise Invalid(f"add edge {eid} has unknown target {trg}")
        if partner == central:
            raise Invalid(f"add edge {eid} joins the central claim")
        return resolve(partner, seen + (adu,))

    order = sorted(adus, key=lambda a: min(edu_order[e] for e in seg[a]))
    num = {a: i + 1 for i, a in enumerate(order)}
    nodes = []
    for a in order:
        txt = " ".join(edus[e] for e in sorted(seg[a], key=edu_order.get))
        nodes.append({"id": num[a], "text": txt, "role": adus[a]})

    parent = {}
    out_edges = []
    for a in order:
        if a == central:
            continue
        p, lab = resolve(a)
        if p == a:
            raise Invalid(f"{a} resolves to itself")
        parent[a] = p
        out_edges.append({"from": num[a], "to": num[p], "label": lab,
                          "gold_type": edges[out[a][0]][2]})
    # tree check: every node reaches the central claim without cycles
    for a in parent:
        cur, steps = a, 0
        while cur != central:
            cur = parent[cur]
            steps += 1
            if steps > len(adus):
                raise Invalid(f"cycle from {a}")

    topic = root.get("topic_id")
    question = topic.replace("_", " ") + "?" if topic else ""
    return {
        "id": tid,
        "question": question,
        "text": " ".join(n["text"] for n in nodes),
        "nodes": nodes,
        "central": num[central],
        "edges": out_edges,
    }


def main():
    src_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    files = sorted(src_dir.glob("*.xml"))
    valid, excluded = {}, {}
    for f in files:
        try:
            rec = parse_file(f)
            valid[rec["id"]] = rec
        except (Invalid, ET.ParseError) as exc:
            excluded[f.stem] = str(exc)
    print(f"english xml files: {len(files)}; valid: {len(valid)}; excluded: {len(excluded)}")
    for k, v in excluded.items():
        print(f"  EXCLUDED {k}: {v}")

    def dump(ids, path):
        with open(path, "w", encoding="utf-8") as fh:
            for i in sorted(ids):
                fh.write(json.dumps(valid[i], ensure_ascii=False) + "\n")

    sample = random.Random(2026).sample(sorted(valid), 20)
    dump(valid, out_dir / "argmicro_en_all.jsonl")
    dump(sample, out_dir / "argmicro_en_sample20.jsonl")

    for name, ids in (("all", list(valid)), ("sample20", sample)):
        recs = [valid[i] for i in ids]
        labels = Counter(e["label"] for r in recs for e in r["edges"])
        gtypes = Counter(e["gold_type"] for r in recs for e in r["edges"])
        roles = Counter(n["role"] for r in recs for n in r["nodes"])
        n_nodes = sum(len(r["nodes"]) for r in recs)
        print(f"[{name}] texts={len(recs)} nodes={n_nodes} avg_nodes={n_nodes / len(recs):.2f} "
              f"labels={dict(labels)} gold_types={dict(gtypes)} roles={dict(roles)}")
    print("sample ids:", sorted(sample))


if __name__ == "__main__":
    main()
