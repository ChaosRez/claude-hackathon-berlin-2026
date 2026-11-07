# Labeling Guide

**Status: DRAFT — not final.**
This is a starting point for Tasks 2 and 3.
The team changes it, then marks it **FINAL** here.
Until then, don't run the extractor on the full dataset.

This guide is our definition of a correct graph.
People and the extractor both follow it.

## 1. What is one entity

An entity is **one idea with one role** in the reasoning.

- Usually one sentence.
- **Split** a sentence when its parts have different roles.
  "Index funds are cheap, but they can't beat the market." → a `reason` and a `refutation`.
- **Don't split** a sentence just because it is long, if it has one role.
- **Skip filler**: greetings, "Good question", "I hope this helps", "As an AI...".
  Filler is not an entity.
- Keep the text of each entity exactly as written (copy it, don't rewrite it).

## 2. Entity types

| Type | Question it answers | Example |
|---|---|---|
| `claim` | What does the writer want us to accept? | "Paying off your mortgage early is usually not the best move." |
| `reason` | Why is a claim true? | "Your money can earn more if you invest it." |
| `evidence` | What fact, number or case backs it? | "Stocks have returned about 7% a year on average." |
| `refutation` | What speaks against a claim? | "But paying it off is a guaranteed return." |
| `rebuttal` | How does the writer answer a refutation? | "That return is only as high as your interest rate." |
| `condition` | When does a claim hold? | "If your rate is above 6%..." |
| `recommendation` | What should the reader do? | "So invest first, and pay extra only if your rate is high." |

Rules:

- **Exactly one entity is the main claim** (`"main": true`).
  It is the writer's overall answer to the question.
  It is usually a `claim` or a `recommendation`.
- If you hesitate between `reason` and `evidence`:
  general statements are `reason`, specific facts, numbers or cases are `evidence`.
- If you hesitate between `claim` and `recommendation`:
  if it tells the reader to act, it is `recommendation`.

## 3. Relation types

**Direction rule:** every edge goes **from an entity to the entity it is about.**
Read it as a sentence: "A *supports* B".

| Relation | Meaning | Typical from → to |
|---|---|---|
| `supports` | A gives a reason for B | reason → claim |
| `illustrates` | A is a fact or case backing B | evidence → reason or claim |
| `attacks` | A argues against B | refutation → claim |
| `answers` | A replies to the objection B | rebuttal → refutation |
| `qualifies` | A limits when B holds | condition → claim or recommendation |
| `concludes` | A is drawn from B | recommendation → reason |

Rules:

- **Every entity except the main claim has exactly one outgoing edge**: to the one entity it is most about.
  This makes each graph a tree, which is easier to label and compare.
- An edge can point to an earlier or a later entity.
- The "typical from → to" column is a guide, not a rule.
  If the text clearly does something else, label what the text does.

## 4. How to label a text

1. Read the whole answer once.
2. Find the **main claim** first.
3. Cut the text into entities (section 1) and give each a type (section 2).
4. For each entity, ask: "What is this one mostly about?"
   Draw one edge there and pick the relation (section 3).
5. Check: one main claim, every other entity has one outgoing edge, no filler left.

## 5. Worked example

Question: *Should I pay off my mortgage early or invest?*

Answer (made up for this guide):

> Good question!
> In most cases, investing is the better choice.
> Stocks have historically returned more than typical mortgage rates.
> However, paying off the loan is a risk-free return.
> That matters less when your rate is low.
> If your rate is above 6%, paying it off can make sense.
> So check your rate before you decide.

| id | type | text | main |
|---|---|---|---|
| — | (filler, skipped) | Good question! | |
| 1 | claim | In most cases, investing is the better choice. | yes |
| 2 | reason | Stocks have historically returned more than typical mortgage rates. | |
| 3 | refutation | However, paying off the loan is a risk-free return. | |
| 4 | rebuttal | That matters less when your rate is low. | |
| 5 | condition | If your rate is above 6%, paying it off can make sense. | |
| 6 | recommendation | So check your rate before you decide. | |

Edges:

- 2 `supports` 1
- 3 `attacks` 1
- 4 `answers` 3
- 5 `qualifies` 1
- 6 `concludes` 5

```
            [1 claim: investing is better]  (main)
             ^          ^              ^
     supports|   attacks|     qualifies|
  [2 reason]   [3 refutation]   [5 condition]
                    ^                  ^
             answers|         concludes|
              [4 rebuttal]   [6 recommendation]
```

## 6. JSON format

```json
{
  "id": "finance_0012_human",
  "source": "human",
  "question": "Should I pay off my mortgage early or invest?",
  "nodes": [
    {"id": 1, "type": "claim", "text": "In most cases, investing is the better choice.", "main": true},
    {"id": 2, "type": "reason", "text": "Stocks have historically returned more than typical mortgage rates."}
  ],
  "edges": [
    {"from": 2, "to": 1, "type": "supports"}
  ]
}
```

`src/validate.py` checks:

- every node `type` is one of the 7 entity types
- every edge `type` is one of the 6 relation types
- every edge points to existing node ids, and no edge points to itself
- exactly one node has `"main": true`
- every node except the main claim has exactly one outgoing edge
- the main claim has no outgoing edge

## 7. Open questions (decide before marking FINAL)

- Do we add `assumption` (an unstated belief the argument needs)?
  It is interesting but hard to label, because it is not in the text.
- Do we add `hedge` ("generally", "it may", "in most cases")?
  LLMs may hedge more than humans.
  It could be an entity, or a yes/no flag on each entity.
- Is "one outgoing edge" too strict?
  It loses cases where one reason supports two claims.
  We could allow extra edges later for the graph-theory stretch tasks.
- Is `concludes` clear enough, or should we drop it and use `supports` instead?

## 8. Change log

Record every change here, with the date and who agreed.

- 2026-11-07: First draft.
