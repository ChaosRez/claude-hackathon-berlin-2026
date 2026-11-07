# Labeling Guide

**Status: DRAFT — not final.**
This is a starting point for Tasks 2 and 3.
The team changes it, then marks it **FINAL** here.
Until then, don't run the extractor on the full dataset.

This guide is our definition of a correct graph.
People and the extractor both follow it.

The full definitions live in two files:

- `entity_definition.yaml`: entity types, segmentation, flags (Task 2).
- `relation.yaml`: relation types and graph rules (Task 3).

This guide is the short version for labelling.
If this guide and the YAML files disagree, tell the team.

## 1. What is one entity

An entity is **one idea with one role** in the reasoning.

- Usually one sentence.
- **Split** a sentence when its parts have different roles.
  Split points are usually words like: but, however, although, because, since, so, therefore, if, unless, except.
  "Index funds are cheap, but they can't beat the market." → a `reason` and a `counterpoint`.
- **Don't split** a long sentence with one role.
  Don't split a list of items that together play one role ("low fees, broad diversification and simplicity").
- In a bulleted or "Label: text" list, each item is its own entity.
- Keep the text of each entity exactly as written (copy it, don't rewrite it).

**Coverage rule:** every word of the answer belongs to exactly one entity.
Entities do not overlap and do not leave gaps.
Only whitespace and punctuation between entities may stay unassigned.
Joining the entity texts in order must give back the original answer.

## 2. Entity types

| Type | Question it answers | Example |
|---|---|---|
| `claim` | Is the writer taking a position here? | "Index funds are a good choice for most savers." |
| `reason` | Does this answer "why?" for another entity, in general terms? | "Their fees are low, so more of your return stays with you." |
| `evidence` | Is this a concrete detail that could be checked or told as a story? | "A 0.1% fee on $10,000 is only $10 a year." |
| `counterpoint` | Does this speak against something else in the text? | "However, you can't beat the market with an index fund." |
| `rebuttal` | Does this push back against a counterpoint? | "Most active funds don't beat the market either." |
| `condition` | Does this limit the scope of another entity? | "If you invest for more than 10 years, ..." |
| `recommendation` | Does this ask the reader to act? | "So put most of your savings in a broad index fund." |
| `caveat` | Is this a generic "be careful" that would fit almost any answer on the topic? | "It is important to remember that all investments carry some risk." |
| `background` | Could I delete this without weakening or strengthening any position? | "An index fund is a fund that buys all the stocks in a market index." |
| `filler` | Does this say nothing about the topic? | "Great question!" |
| `other` | Did every other test question fail? | (last resort, needs a note) |

Notes:

- `evidence` has a `kind`: `fact`, `example`, `personal` or `source`.
- `caveat` is a candidate type.
  Keep it only if hand labelling shows it is needed.
- `filler` is labelled but is **not a graph node**.
  It is counted separately, so we can compare how much filler humans and LLMs write.
- `other` is a graph node, flagged for review, with a required `note`.
  If more than about 5% of hand-labelled entities are `other`, the list is not enough:
  read them and propose a new type to the team.

**When unsure,** ask the test questions in this order and take the first "yes":
`filler`, `recommendation`, `condition`, `rebuttal`, `counterpoint`, `caveat`, `evidence`, `reason`, `claim`, `background`, `other`.

Hints:

- `reason` vs `evidence`: general statements are `reason`; specific facts, numbers or cases are `evidence`.
- `claim` vs `recommendation`: if it tells the reader to act, it is `recommendation`.
- `counterpoint` vs `caveat`: a risk of the specific option is `counterpoint`; a generic warning is `caveat`.

## 3. Flags on entities

Flags are added to an entity; they are not types.

- `main`: the main claim, the writer's overall answer. **Exactly one per text.**
  Pick the entity that answers the question most directly.
  If none does, pick the "overall / in summary" entity.
  If there is none, set `implicit_main` on the text instead of inventing one.
- `hedged`: the entity softens its own strength.
  Markers: "may", "might", "can", "generally", "usually", "in most cases", "it depends", "probably".

## 4. Relation types

**Direction rule:** every edge goes **from an entity to the entity it is about.**
Read it as a sentence: "A *supports* B".

| Relation | Meaning | Typical from → to |
|---|---|---|
| `supports` | A gives a reason or evidence to believe or follow B | reason → claim, evidence → reason |
| `attacks` | A gives a reason to believe or follow B less | counterpoint → claim |
| `refutes` | A weakens or answers an attack B (an attack on an attack) | rebuttal → counterpoint |
| `qualifies` | A limits when, for whom, or how strongly B holds | condition → claim, caveat → claim |
| `explains` | A helps the reader understand B, without making B more believable | background → claim |
| `elaborates` | A adds detail to B, without a new reason for it | list item → the sentence that opens the list |
| `summarizes` | A repeats B in shorter or more general form, with nothing new | "Overall, ..." → main claim |
| `concludes` | A is a new step drawn from B: "B, so A" | recommendation → claim |
| `conflicts` | A and B contradict each other, and the text leaves it unresolved | later entity → earlier entity |

**When unsure,** ask the test questions in this order and take the first "yes":
`refutes`, `attacks`, `qualifies`, `summarizes`, `concludes`, `supports`, `explains`, `elaborates`.

Dropped relations:
`illustrates` is merged into `supports` (the `evidence` type already says it is an example).
`answers` is renamed to `refutes`.

## 5. Graph rules

- Every edge is directed.
- **Every entity except the main claim and filler has at least one outgoing edge.**
  An entity may have several outgoing and incoming edges.
  The main claim may have outgoing edges, but does not need any.
- **Exactly one outgoing edge per entity is `primary: true`**: the link to the entity it is most about.
  The primary edges form a tree rooted at the main claim.
  Depth and tree edit distance use this tree; everything else uses the full graph.
- `conflicts` edges are never primary.
- Add an edge only when the text clearly makes the link
  (a pronoun, a repeated term, a connective like "so", "but", "because").
  Same topic alone is not enough.
- At most one edge from A to B.
- No self-loops.
- Cycles are allowed but should be rare.
  Count them; don't remove them.
- Filler has no edges.
- An edge can point to an earlier or a later entity.
- The "typical from → to" column is a guide, not a rule.
  If the text clearly does something else, label what the text does.

## 6. How to label a text

1. Read the whole answer once.
2. Find the **main claim** first.
3. Cut the whole text into entities (section 1), leaving nothing out.
   Give each a type (section 2) and flags (section 3).
4. For each entity, ask: "What is this one mostly about?"
   Draw the primary edge there and pick the relation (section 4).
5. Add extra edges only where the text clearly makes another link.
6. Check: one main claim, every non-filler entity except the main has exactly one primary edge, filler has no edges.

## 7. Worked example

Question: *Should I pay off my mortgage early or invest?*

Answer (made up for this guide):

> Good question!
> In most cases, investing is the better choice.
> Stocks have historically returned more than typical mortgage rates.
> However, paying off the loan is a risk-free return.
> That matters less when your rate is low.
> If your rate is above 6%, paying it off can make sense.
> So check your rate before you decide.

| id | type | text | flags |
|---|---|---|---|
| 0 | filler | Good question! | |
| 1 | claim | In most cases, investing is the better choice. | main, hedged |
| 2 | reason | Stocks have historically returned more than typical mortgage rates. | |
| 3 | counterpoint | However, paying off the loan is a risk-free return. | |
| 4 | rebuttal | That matters less when your rate is low. | |
| 5 | condition | If your rate is above 6%, paying it off can make sense. | |
| 6 | recommendation | So check your rate before you decide. | |

Edges (all primary):

- 2 `supports` 1
- 3 `attacks` 1
- 4 `refutes` 3
- 5 `qualifies` 1
- 6 `concludes` 5

```
            [1 claim: investing is better]  (main)
             ^          ^              ^
     supports|   attacks|     qualifies|
  [2 reason]  [3 counterpoint]  [5 condition]
                    ^                  ^
             refutes|         concludes|
              [4 rebuttal]   [6 recommendation]

  [0 filler]  (not a node, counted only)
```

## 8. JSON format

Nodes are listed in text order.

```json
{
  "id": "finance_0012_human",
  "source": "human",
  "question": "Should I pay off my mortgage early or invest?",
  "nodes": [
    {"id": 0, "type": "filler", "text": "Good question!"},
    {"id": 1, "type": "claim", "text": "In most cases, investing is the better choice.", "main": true, "hedged": true},
    {"id": 2, "type": "reason", "text": "Stocks have historically returned more than typical mortgage rates."}
  ],
  "edges": [
    {"from": 2, "to": 1, "type": "supports", "primary": true}
  ]
}
```

`src/measure.py` (`check`) rejects a graph when:

- a node `type` is not one of the 11 entity types
- an edge `type` is not one of the 9 relation types
- node ids are duplicated
- an edge points to a missing node, or to itself
- there is more than one edge between the same pair
- an edge touches a filler node
- a `conflicts` edge is primary
- the number of main claims is not exactly 1
- a non-filler, non-main node has no outgoing edge, or not exactly 1 primary edge
- the primary edges do not form a tree rooted at the main claim

Invalid graphs are counted and listed, never silently dropped.

## 9. Open questions (decide before marking FINAL)

- Do we keep `caveat` as its own type?
  Keep it only if hand labelling shows it is needed.
- Do we add `assumption` (an unstated belief the argument needs)?
  It is interesting but hard to label, because it is not in the text.
- Is the difference between `elaborates`, `summarizes` and `concludes` clear enough for two people to agree?
- The coverage check (entity texts rebuild the answer) is described in `entity_definition.yaml`
  but not yet in `src/measure.py`.

## 10. Change log

Record every change here, with the date and who agreed.

- 2026-11-07: First draft.
- 2026-11-07: Synced with `entity_definition.yaml` v0.1 and `relation.yaml` v0.1
  (11 entity types, 9 relation types, primary edges instead of one-edge trees, `hedged` flag, coverage rule).
  Proposed by Farehe; **not yet agreed by the team.**
