# Do LLMs Argue Like Humans?

Team 2: graph theory and graph reasoning.

A research loop developed for the Claude Impact Lab Berlin 2026 (co-hosted by Foresight Institute).

## The question

Do LLMs build arguments the same way humans do?

We don't look at *which words* are used.
We look at *how the text is built*:
which idea supports which,
where counterpoints appear,
and how deep the reasoning goes.

## The idea in 3 steps

1. Take human and ChatGPT answers to the **same questions**, with almost the same length.
2. Turn each answer into a **graph**: the parts of the reasoning (claims, reasons, refutations, ...) are nodes, and links show how they relate.
3. Compare the graphs. Are LLM graphs deeper, flatter, more one-sided?

## Decisions so far

- **Data:** 100 questions from HC3 `finance`.
  For each, one human answer and one ChatGPT answer whose lengths differ by **at most 15 words** (10 or less preferred).
  We use the ChatGPT answers already in HC3; we don't generate new ones for now.
- **Nodes are "entities" of reasoning,** not just sentences.
  Which entities to use (argument, reason, claim, refutation, or better ones) is decided by the team in Task 2 and written in `GUIDE.md`.
- **Relations** between entities are decided in Task 3 and written in `GUIDE.md`.
- **How to analyse** is brainstormed in Task 6, after we can build and draw graphs.

See `TASKS.md` for the current tasks and owners.

## Dataset

**HC3 (Human ChatGPT Comparison Corpus)**

- Hugging Face: https://huggingface.co/datasets/Hello-SimpleAI/HC3
- GitHub: https://github.com/Hello-SimpleAI/chatgpt-comparison-detection
- Paper: https://arxiv.org/abs/2301.07597

It has questions with both human and ChatGPT answers.
We use the `finance` subset and keep only pairs with almost equal length (see Decisions).

Average answer length in words (from the HC3 paper):

| Subset | Human | ChatGPT |
|---|---|---|
| finance | 202 | 226 |
| wiki_csai | 229 | 208 |
| reddit_eli5 | 134 | 195 |
| medicine | 93 | 210 |
| open_qa | 35 | 132 |

- **We use `finance`**: human and ChatGPT answers have similar length there on average.
  We still filter each pair to a length difference of at most 15 words.
- **Prefer opinion questions** ("Should I...", "Is it better to...").
  Pure explanations ("Why is the sky blue?") have no real argument.
- **License:** HC3 is CC BY-SA 4.0 (some sources may be stricter).
  Share-alike means any data we derive from it (for example annotated graphs) must also be CC BY-SA 4.0.
  Name this in the submission issue.

## Entities: what the nodes are (Task 2, to brainstorm)

Instead of one node per sentence, nodes are the **parts of the reasoning**.
Candidate entities:

| Entity | Meaning | Example |
|---|---|---|
| `claim` | a statement the writer wants us to accept | "Index funds are a good choice." |
| `reason` | why a claim is true | "Their fees are low." |
| `evidence` / `example` | a fact, number or case backing a reason | "A 0.1% fee on $10,000 is $10 a year." |
| `refutation` | an argument against a claim | "But you can't beat the market with them." |
| `rebuttal` | an answer to a refutation | "Most active funds don't beat it either." |
| `condition` | when a claim holds ("it depends") | "If you invest for over 10 years..." |
| `recommendation` | what the reader should do | "So put most of your savings in one." |

Questions for the team:

- Which of these are really useful for comparing human and LLM thinking? Keep the list short.
- Are there better entities? For example `assumption` (an unstated belief), or `hedge` ("it may", "generally").
- How big is one entity: a sentence, a clause, or any span of text?
- Is there always one **main claim**?

## Relations between entities (Task 3, to brainstorm)

Starter list.
Change it as a team, then freeze it in `GUIDE.md`.

| Relation | Meaning |
|---|---|
| `supports` | A gives a reason for B |
| `attacks` | A argues against B |
| `answers` | A replies to a refutation B |
| `illustrates` | A is an example or evidence for B |
| `qualifies` | A limits when B holds |
| `concludes` | A is drawn from B (B leads to A) |

Good relations should capture the **shape of the thinking**:
does the writer consider the other side? Do they give conditions? Do they end with a conclusion?

**Keep both lists short.**
More types means more disagreement between people.

## Step-by-step plan

### Step 1: Get the data (Task 1)

- Load HC3 `finance`.
- Keep pairs where the human and ChatGPT answers differ by **at most 15 words**.
- Take **100 questions**. If fewer exist, write down how many.
- Save to `data/pairs.jsonl`, plus a small script that rebuilds it.

### Step 2: Agree on entities and relations (Tasks 2 and 3)

- Brainstorm the entities and relations above.
- Write them in `GUIDE.md`, with one example each.
- Two people each label the same 2 texts by hand.
  Compare.
  Fix the rules until you mostly agree.

### Step 3: Build and draw the graph (Tasks 4 and 5)

- `src/extract.py`: send a text and `GUIDE.md` to Claude, get entities and relations back as JSON (format below).
- `src/validate.py`: check every link points to a real entity and every type is allowed.
- `src/build_graph.py`: turn the JSON into a `networkx` graph.
- `src/draw.py`: draw a graph as an image, with one color per entity type and labeled arrows.

### Step 4: Check the extractor by hand (about 1 hour) — most important

- Pick **10 texts** (5 human, 5 ChatGPT).
  Hide which is which.
- Two people label them by hand using `GUIDE.md`.
  Save in `annotations/`.
- Compare with the script: same main claim? Same links?
  Give a simple score (for example "70% of links match").
- Compare the two people with each other too.
  If they disagree a lot, the rules are unclear.
- **Fairness:** is the script equally accurate on human and LLM texts?
- **Stability:** run the script twice on 20 texts.
  Graphs should mostly match.

### Step 5: Brainstorm the analysis (Task 6)

Ideas to start from:

For each graph:

- number of nodes
- depth (longest chain of links to the main claim)
- branching (average links into a node)
- share of each entity and relation type (for example: how often is there a refutation?)
- position of the main claim (start, middle, end)

### Step 6: Compare

Simplest first:

1. **Numbers:** compare human vs LLM averages from Step 5.
2. **Small patterns:** count shapes like "example → reason → main claim" or "counterpoint that gets answered".
3. **Whole graphs:** graph edit distance (`networkx`), using labels only, not words.

Always compare against a **baseline**: human vs human.
If human-vs-LLM looks like human-vs-human, there is no real difference.

For the biggest difference you find, **read 3 real pairs** to make sure it's real and not a script error.

### Step 7: Write up (about 30 min)

In `results/RESULTS.md` and `JOURNAL.md`:

- the rules we used
- how well the script matched people (Step 4)
- the main result, with the baseline next to it
- limits (one dataset, one LLM, one extractor)

## Graph format (JSON)

```json
{
  "id": "finance_0012_human",
  "source": "human",
  "question": "Should I pay off my mortgage early?",
  "nodes": [
    {"id": 1, "type": "claim", "text": "It depends on your interest rate.", "main": true},
    {"id": 2, "type": "condition", "text": "If the rate is low, investing usually earns more."}
  ],
  "edges": [
    {"from": 2, "to": 1, "type": "qualifies"}
  ]
}
```

## Planned folders

```
GUIDE.md           entities and relations, agreed in Tasks 2 and 3
data/              raw and paired texts
prompts/           extractor prompts, versioned (extract_v1.txt, ...)
src/               extract, validate, build_graph, draw, measure, compare
annotations/       hand-made graphs for checking the extractor
results/           numbers, plots, RESULTS.md
```

## What "done" looks like by evening

- A script that turns text into a reasoning graph, and draws it.
- A check showing how well it matches people on 10 texts.
- One clear finding, or a clear "no difference found".
  Both are useful.

## Related work

- **Argument Collapse: LLMs Flatten Long-Form Public Debate** (2026).
  LLMs use a narrower set of arguments than humans.
  Uses lists, not graphs.
  https://arxiv.org/abs/2606.01736
- **Threads of Subtlety** (ACL 2024).
  LLM text has less varied discourse structure.
  Goal is detection.
  https://arxiv.org/abs/2402.10586

What we add:
reasoning graphs with typed entities and links,
graph shape measures,
and an extractor checked by hand.

## Structure & Conventions

- **`CLAUDE.md`**: Project conventions, evidence chain rules, and constraints for AI agents.
- **`JOURNAL.md`**: Append-only ledger recording research hypotheses, experiment runs, and evidence audits.
- **`TASKS.md`**: Active task ledger and milestones for the team and agents.
- **`.claude/skills/judge-submissions/`**: Submission evaluator skill based on the official hackathon rubric.

## Setup

Install [uv](https://docs.astral.sh/uv/), then install the dependencies:

```bash
uv sync
```

To get the data:

```bash
uv run scripts/get_data.py
```

It downloads HC3 `finance` to `data/finance.jsonl`,
then runs `scripts/filter_jsonl.py` to write `data/finance-filtered.jsonl`.
Filter options pass through, for example `--max-diff 15`.

To re-run the data exploration:

```bash
uv run --with nbconvert jupyter nbconvert --to notebook --execute --inplace data_exploration.ipynb
```

It needs internet access to download HC3 and FiQA.

## Working with Claude Code

To run Claude Code with your research loop:

```bash
# Goal-directed loop: runs until condition is met
/goal src/validate.py passes on every graph in results/graphs/, and the extractor-vs-hand score from annotations/ is recorded in JOURNAL.md

# Scheduled loop: periodically monitors and records progress
/loop 10m check extractor output and log new results to JOURNAL.md

# Self-evaluate project against the hackathon rubric
/judge-submissions
```

## Licenses

This project is dual-licensed:

- **Code**: [Apache License 2.0](LICENSE)
- **Documentation & Written Materials**: [Creative Commons Attribution 4.0 International](LICENSE-docs)
- **Data derived from HC3**: CC BY-SA 4.0, following the HC3 license.
