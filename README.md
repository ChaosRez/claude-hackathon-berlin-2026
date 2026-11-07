# Do LLMs Argue Like Humans?

Team 2: graph theory and graph reasoning.

A research loop developed for the Claude Impact Lab Berlin 2026 (co-hosted by Foresight Institute).

## The question

Do LLMs build arguments the same way humans do?

We don't look at *which words* are used.
We look at *how the text is built*:
which sentence supports which,
where counterpoints appear,
and how deep the reasoning goes.

## The idea in 3 steps

1. Take human and LLM answers to the **same questions**.
2. Turn each answer into a **graph**: each sentence is a node, and links show how sentences relate.
3. Compare the graphs. Are LLM graphs deeper, flatter, more one-sided?

## Dataset

**HC3 (Human ChatGPT Comparison Corpus)**

- Hugging Face: https://huggingface.co/datasets/Hello-SimpleAI/HC3
- GitHub: https://github.com/Hello-SimpleAI/chatgpt-comparison-detection
- Paper: https://arxiv.org/abs/2301.07597

It has questions with both human and ChatGPT answers.
We also generate **new answers with a current LLM** (for example Claude) for the same questions.

Average answer length in words (from the HC3 paper):

| Subset | Human | ChatGPT |
|---|---|---|
| finance | 202 | 226 |
| wiki_csai | 229 | 208 |
| reddit_eli5 | 134 | 195 |
| medicine | 93 | 210 |
| open_qa | 35 | 132 |

- **Use `finance` or `wiki_csai`**: human and LLM answers have similar length there.
- **Pick opinion questions** ("Should I...", "Is it better to...").
  Pure explanations ("Why is the sky blue?") have no real argument.
- **License:** HC3 is CC BY-SA 4.0 (some sources may be stricter).
  Share-alike means any data we derive from it (for example annotated graphs) must also be CC BY-SA 4.0.
  Name this in the submission issue.

## How we chunk the text

**One sentence = one node.**
Simple and easy to check by hand.

Edge cases to agree on (brainstorm):

- A sentence with two ideas ("X is cheap, but Y is faster"): keep as one node, or split?
- Very short sentences ("Yes.", "Good question."): drop, or keep?
- Lists and bullet points: is each bullet one node?

Write the decisions in `GUIDE.md` (see Step 1).

## Relations between sentences (draft, to brainstorm)

Starter list.
Change it as a team, then freeze it in `GUIDE.md`.

| Relation | Meaning | Example |
|---|---|---|
| `supports` | B gives a reason for A | A: "Index funds are a good choice." B: "Their fees are low." |
| `attacks` | B argues against A | B: "But you can't beat the market with them." |
| `explains` | B clarifies or adds detail to A | B: "A fee is what you pay each year to the fund." |
| `example` | B is a concrete case of A | B: "For example, a 0.1% fee on $10,000 is $10." |
| `restates` | B says A again in other words | B: "In short, they are cheap." |
| `none` | no clear link to any earlier sentence | filler, greetings |

Open questions for the brainstorm:

- Does each sentence link to **only one** earlier sentence (a tree, easier) or **several** (a general graph)?
- Can a sentence link **forward** (to a later sentence), or only backward?
- How do we pick the **main claim**?
  Rule idea: the sentence that most others support, directly or indirectly.

**Keep the list short.**
More relations means more disagreement between people.

## Step-by-step plan

### Step 1: Agree on the rules (about 1 hour)

- Decide the chunking rules and relations above.
- Write them in `GUIDE.md`, with one example per relation.
- Two people each label the same 2 texts by hand.
  Compare.
  Fix the rules until you mostly agree.

### Step 2: Get the data (about 30 min)

- Load HC3 (`finance` or `wiki_csai`).
- Pick **50 questions** with human answers of 100–300 words.
- For each question, ask an LLM to answer at a similar length.
- Remove giveaway lines like "As an AI...".
- Save to `data/pairs.jsonl`.

### Step 3: Build the extractor (about 1 hour)

- Split each text into sentences (`src/split.py`).
- Send numbered sentences and `GUIDE.md` to Claude.
  Ask for JSON (format below).
- Check the JSON with code (`src/validate.py`):
  every link points to a real sentence,
  and every relation is in the allowed list.

### Step 4: Check the extractor by hand (about 1 hour) — most important

- Pick **10 texts** (5 human, 5 LLM).
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

### Step 5: Measure (about 30 min)

For each graph:

- number of nodes
- depth (longest chain of links to the main claim)
- branching (average links into a node)
- share of `attacks`, `example`, `restates`, and so on
- position of the main claim (start, middle, end)

### Step 6: Compare (about 1 hour)

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
    {"id": 1, "text": "It depends on your interest rate.", "main": true},
    {"id": 2, "text": "If the rate is low, investing usually earns more."}
  ],
  "edges": [
    {"from": 2, "to": 1, "type": "supports"}
  ]
}
```

## Planned folders

```
GUIDE.md           labeling rules (chunking + relations), written in Step 1
data/              raw and paired texts
prompts/           extractor prompts, versioned (extract_v1.txt, ...)
src/               split, extract, validate, measure, compare
annotations/       hand-made graphs for checking the extractor
results/           numbers, plots, RESULTS.md
```

## What "done" looks like by evening

- A script that turns text into a sentence graph.
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
full sentence graphs with support and attack links,
graph shape measures,
and an extractor checked by hand.

## Structure & Conventions

- **`CLAUDE.md`**: Project conventions, evidence chain rules, and constraints for AI agents.
- **`JOURNAL.md`**: Append-only ledger recording research hypotheses, experiment runs, and evidence audits.
- **`TASKS.md`**: Active task ledger and milestones for the team and agents.
- **`.claude/skills/judge-submissions/`**: Submission evaluator skill based on the official hackathon rubric.

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
