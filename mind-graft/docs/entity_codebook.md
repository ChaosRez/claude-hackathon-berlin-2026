# Entity codebook

Each answer is broken into **entities**: chunks of words that carry one unit of value
(a claim, a reason, an example...). `scripts/segment_answers.py` proposes segments
(sentences and clauses); the labeller assigns one token per segment.

## Label file format

One line per answer, in `data/labels/*.txt`:

```
12 H: C0 R1 + X2 O1 B4 S^1
12 L: S0^0 R1 D2 ...
```

- `12` is the row number (1–100) in `data/hc3_similar_length_100.jsonl`; `H` = human, `L` = ChatGPT.
- One token per segment, in order. `+` merges the segment into the previous entity.
- Token = `TYPE` + optional parent + optional returns:
  - **parent**: segment number (as printed in `data/work/segments.txt`, e.g. `3` for H3) of the
    entity this one builds on; `0` = the question. An entity is referred to by its first segment.
  - **returns** `^n`: this entity restates / comes back to the entity starting at segment `n` (`^0` = the question).

## Types

| Code | Type | Opposition (x) |
|---|---|---|
| C | Claim / direct answer | 0 |
| R | Reason (why the claim holds) | 0 |
| E | Elaboration / explanation of mechanism | 0 |
| X | Example, evidence or fact | 0 |
| D | Definition / background | 0 |
| O | Opposing view (states the other side) | −1 |
| H | Hedge, concession or uncertainty | −0.5 |
| B | Rebuttal of an opposing view | +0.5 |
| S | Restatement of an earlier entity | 0 |
| K | Conclusion / summary | 0 |
| V | Advice or recommendation | 0 |
| T | Aside / tangent / personal note | 0 |

## Axes

- **Length (z)**: word position of the entity's midpoint within the answer.
- **Opposition (x)**: taken from the type, as above. Wide = spread across x.
- **Depth (vertical)**: steps of building. Question = 0; an entity with a parent sits at
  parent depth + 1; an entity with no parent but returns sits at the depth of the
  shallowest entity it returns to; neither = depth 1.

## Judgement rules

- Prefer the most specific parent: an example of a reason builds on the reason, not the claim.
- A list item of the same kind as its sibling shares the sibling's parent (a branch, not a chain).
- Mark `^` only when the entity substantially repeats an earlier point, not just a shared word.
- Opening sentences that echo the question's wording get `^0`.
- These labels are one labeller's reading (Claude Opus 5.5, Nov 2026). Check agreement on a sample before drawing strong conclusions.
