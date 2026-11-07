# Language Sails

How do human and LLM answers to the same question differ in the *shape* of their reasoning?

Language Sails breaks answers into **entities**: claims, reasons, examples, hedges, rebuttals, restatements and other units of meaning. It links them by how they relate to each other, then draws every answer as a 3D graph. Lay 100 answers around a shared axis and they form a "sail" you can orbit. Do the same for each domain (ELI5, Finance, Computer Science and so on) and you get one cone per domain to compare.

Built for the Berlin Claude Community hackathon, November 2026.

## The question we're testing

> LLM reasoning tends to be circular and repetitive: it keeps coming back to its starting point. Human reasoning tends to move forward and doesn't keep returning to where it began.

On 100 hand-labelled HC3 Reddit ELI5 pairs, there is evidence for this:

| Per answer (average) | Human | ChatGPT |
|---|---|---|
| Max depth | 4.5 | 3.7 |
| Reinforces an earlier point or the question | 0.63 | 1.32 |
| Answers whose shape is a **circle** | 7% | 21% |
| Answers whose shape is a **line** | 33% | 17% |
| Answers that explore an opposing idea | 42% | 38% |

ChatGPT also gives about twice as much advice and restates points about twice as often. Humans use more examples and hedges.

*Caveat:* one reader (Claude) labelled these entities using the codebook. Check how often a second reader agrees before treating them as findings.

## The 3D graph

| Axis | Meaning | Vocabulary |
|---|---|---|
| **z** | Length: word position in the answer | timeline |
| **y** | Depth: how many steps of building an entity sits on | deep / shallow |
| **x** | Opposition: 0 is the main line, −1 an opposing view, −0.5 a hedge, +0.5 a rebuttal | narrow / wide |

- **Colour = who wrote it.** Orange is human, purple is LLM.
- **3D shape = entity type.** There are 12 shapes, one per type in the codebook.
- **Line style = relationship.** Continuous means *supports*, dashed *disagrees*, dash-dot *qualifies*, dotted *reinforces*.
- **Sails** are translucent surfaces joining neighbouring answers of the same colour.

Each answer is classified as a **line, tree, hub and spoke, circle, spiral, zigzag** or **wandering** shape. The rules are in [docs/entity_codebook.md](docs/entity_codebook.md) and in the app.

## Where an entity starts and ends

1. Split into sentences at `.` `!` or `?` followed by a capital letter or number.
2. Split again at a semicolon, or at a comma followed by *but, however, although, though, whereas* or *yet*.
3. A list number such as "2." stays with the sentence after it.
4. The labeller may merge a piece into the previous entity when it doesn't carry a unit of meaning of its own.

## The app: Language Analyser

A single-page web app built with three.js. With it you can:

- Orbit, zoom and pan across one cone per dataset.
- Switch between all rows and a single row, or show human answers only, LLM answers only, or both.
- Slide the human and LLM graphs apart to compare their elevations.
- Click a node to see its type, its text and its relationships.
- See entity type counts and percentages per answer, graph-typology tables and written insights.
- **Import any CSV** with a question column, a human answer column and an LLM answer column. Each import becomes a new cone.

## Data

[HC3 (Hello-SimpleAI)](https://huggingface.co/datasets/Hello-SimpleAI/HC3) pairs human and ChatGPT answers to the same questions. Each domain set holds the first rows where the two answers differ by **fewer than 10 words**:

| Set | Rows | Labels |
|---|---|---|
| Reddit ELI5 | 100 | by hand, using the codebook |
| Finance | 100 | rule-based; Claude labelling in the app |
| Wiki CSAI | 41 (all that pass the filter) | rule-based; Claude labelling in the app |

HC3 is released under CC BY-SA 4.0.

## Project layout

```
scripts/   data preparation, segmentation, label validation, viewer builds (Python 3.12, standard library only)
data/      filtered datasets, entity labels, summaries (data/raw/ is not committed)
docs/      entity codebook
viewer/    web app templates and built single-file pages
```

## Roadmap

- **Version 1 (this repo):** single question-and-answer pairs, human against LLM.
- **Version 2:** multi-turn conversations, with relationships between entities across turns.
