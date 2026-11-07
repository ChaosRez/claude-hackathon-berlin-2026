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
  The draft list is in `entity_definition.yaml` (Task 2), summarised in `GUIDE.md`.
- **Relations** between entities are drafted in `relation.yaml` (Task 3), summarised in `GUIDE.md`.
- **How to analyse** is drafted in `criteria.yaml` (Task 6) and computed by `src/measure.py`.
- All three are drafts until the team marks `GUIDE.md` FINAL.

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

## Entities: what the nodes are (Task 2, draft)

Instead of one node per sentence, nodes are the **parts of the reasoning**.
Full definitions, test questions and examples are in `entity_definition.yaml`.

| Entity | Meaning |
|---|---|
| `claim` | a position the writer wants us to accept |
| `reason` | a general statement explaining why another entity is true |
| `evidence` | a specific fact, number, case, story or source (`kind`: fact, example, personal, source) |
| `counterpoint` | a point against a claim, reason or recommendation |
| `rebuttal` | the writer's reply to a counterpoint |
| `condition` | when or for whom another entity holds ("it depends") |
| `recommendation` | advice telling the reader what to do |
| `caveat` | a generic warning not tied to a specific entity (candidate) |
| `background` | neutral context, such as a definition |
| `filler` | no content about the question; counted, not a node |
| `other` | last resort, with a note; flagged for review |

Every word of the answer belongs to exactly one entity.
Each entity can carry two flags: `main` (exactly one per text) and `hedged`.

## Relations between entities (Task 3, draft)

Full definitions and graph rules are in `relation.yaml`.

| Relation | Meaning |
|---|---|
| `supports` | A gives a reason or evidence to believe or follow B |
| `attacks` | A gives a reason to believe or follow B less |
| `refutes` | A answers an attack B |
| `qualifies` | A limits when, for whom, or how strongly B holds |
| `explains` | A helps understand B, without making it more believable |
| `elaborates` | A adds detail to B, without a new reason |
| `summarizes` | A repeats B in shorter form |
| `concludes` | A is a new step drawn from B ("B, so A") |
| `conflicts` | A and B contradict, unresolved |

An entity may have several edges.
Exactly one outgoing edge per entity is `primary`;
the primary edges form a tree rooted at the main claim.

Good relations should capture the **shape of the thinking**:
does the writer consider the other side? Do they give conditions? Do they end with a conclusion?

## Step-by-step plan

### Step 1: Get the data (Task 1)

- Load HC3 `finance`.
- Keep pairs where the human and ChatGPT answers differ by **at most 15 words**.
- Take **100 questions**. If fewer exist, write down how many.
- `scripts/get_data.py` saves them to `data/finance-filtered.jsonl` (see Setup).

### Step 2: Agree on entities and relations (Tasks 2 and 3)

- Review the drafts in `entity_definition.yaml` and `relation.yaml`.
- Agree on them in `GUIDE.md`, with one example each.
- Two people each label the same 2 texts by hand.
  Compare.
  Fix the rules until you mostly agree.

### Step 3: Build and draw the graph (Tasks 4 and 5)

- `src/extract.py` (done): sends a text, `entity_definition.yaml` and `relation.yaml` to Claude, gets entities and relations back, and saves one YAML graph per answer (format below).
  If a graph breaks a rule, it asks Claude once more with the errors.
- Validation (done): `src/validate.py` holds the rules.
  The extractor and `src/measure.py` both use it, so there is one set of rules.
- `src/draw.py` (done): turns a graph into a Graphviz drawing, with one color per family of entity types and labeled arrows.
  The Streamlit app (`app.py`) shows it.
  Saving a PNG is still open.

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

### Step 5: Define the analysis (Task 6, draft)

`criteria.yaml` defines the per-graph measures, in four groups:

- **Size:** nodes, edges, filler, edges per node, share of non-primary edges.
- **Shape:** longest path, depth to the main claim, leaves, links into the main claim, branching, cycles, position of the main claim.
- **Dialectic:** attacks, share of counterpoints that get answered, qualifies, conflicts, share of hedged entities.
- **Composition:** share of each entity type and each relation type.

`src/measure.py` computes all of them from node and edge types only.
`analyse logic.md` holds a wider brainstorm of ideas beyond this list.

### Step 6: Compare

Simplest first:

1. **Numbers:** for each question, ChatGPT minus human, then average over questions (`src/measure.py`).
   Test with Wilcoxon signed-rank, report effect size and number of pairs, correct with Holm.
2. **Small patterns:** count shapes like "evidence → reason → main claim" or "counterpoint that gets answered".
3. **Whole graphs:** graph edit distance on the primary tree, using labels only, not words.

Always compare against a **baseline**: human vs human.
If human-vs-LLM looks like human-vs-human, there is no real difference.

The baseline method is still open:

- `criteria.yaml` and `src/measure.py` use a split-half baseline over the human graphs (1,000 shuffles, 95% range).
- `data_exploration.ipynb` section 11 found a second human answer in FiQA (the source of HC3 `finance`) for 61.9% of questions.
  After its filters, 68 questions have two human answers, which would allow a same-question baseline.

For the biggest difference you find, **read 3 real pairs** to make sure it's real and not a script error.

### Step 7: Write up (about 30 min)

In `results/RESULTS.md` and `JOURNAL.md`:

- the rules we used
- how well the script matched people (Step 4)
- the main result, with the baseline next to it
- limits (one dataset, one LLM, one extractor)

## Graph format (JSON or YAML)

Nodes are listed in text order, with ids that increase.
Full rules are in `GUIDE.md` section 8 and `src/validate.py`.
The `answer` field holds the original text, so the coverage rule can be checked;
`src/measure.py` rejects graphs without it.
The extractor writes the same fields as YAML, plus its run log.

```json
{
  "id": "finance_0012_human",
  "source": "human",
  "question": "Should I pay off my mortgage early?",
  "answer": "It depends on your interest rate. If the rate is low, investing usually earns more.",
  "implicit_main": false,
  "nodes": [
    {"id": 1, "type": "claim", "text": "It depends on your interest rate.", "main": true, "hedged": true},
    {"id": 2, "type": "condition", "text": "If the rate is low, investing usually earns more."}
  ],
  "edges": [
    {"from": 2, "to": 1, "type": "qualifies", "primary": true}
  ]
}
```

## Folders

```
GUIDE.md                 labelling guide (draft until marked FINAL)
entity_definition.yaml   entity types (Task 2 draft)
relation.yaml            relation types and graph rules (Task 3 draft)
criteria.yaml            measures and comparison method (Task 6 draft)
analyse logic.md         wider analysis brainstorm
data_exploration.ipynb   HC3 audit and checks for this project
scripts/                 get_data.py, filter_jsonl.py
prompts/                 extractor prompts, versioned (extract_v1.md, extract_v2.md)
src/extract.py           text -> graph YAML, using Claude
src/validate.py          the graph rules, used by the extractor and by measure.py
src/measure.py           computes measures, compares human vs ChatGPT
src/draw.py              graph -> Graphviz drawing
src/pipeline.py          extract -> graph -> drawing -> measures, for one answer
app.py                   Streamlit app on top of src/pipeline.py
tests/                   tests for src/
data/                    HC3 data, not in git (rebuild with scripts/get_data.py)
```

Planned, not created yet:

```
annotations/   hand-made graphs for checking the extractor
results/       graphs, numbers, plots, RESULTS.md
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
- **`.claude/skills/judge-submissions/`**: the organizers' skill for judging submissions, from the event template.
  It reads GitHub issues labelled `submission` and commits assessments, so it does not check this repository by itself.

## Setup

Install [uv](https://docs.astral.sh/uv/), then install the dependencies:

```bash
uv sync
```

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Then put your Anthropic API key in `.env`.
Git ignores `.env`, so your key stays local.

To get the data:

```bash
uv run scripts/get_data.py
```

It downloads HC3 `finance` to `data/finance.jsonl`,
then runs `scripts/filter_jsonl.py` to write `data/finance-filtered.jsonl`.
Filter options pass through:

| Option | Default | Meaning |
|---|---|---|
| `--max-diff` | 10 | max word-count difference between the human and ChatGPT answer |
| `--min-total` | 150 | min combined word count of the pair |
| `--max-total` | 500 | max combined word count of the pair |
| `--limit` | 100 | max pairs to keep |

The default `--max-diff 10` is the preferred value; the project allows up to 15.
The script does not yet prefer opinion questions.

To extract graphs (at most 10 pairs while `GUIDE.md` is a draft):

```bash
uv run python -m src.extract --limit 2
```

It writes one YAML graph per answer to `results/extraction/<run id>/graphs/`,
and the settings, prompt and schema versions and counts to `run.yaml`.
It uses the API key in `.env`, or your Claude Code login if there is none (`--backend cli`).

To check a folder of graphs against the rules:

```bash
uv run python -m src.validate results/extraction/<run id>/graphs
```

To compute the measures on a folder of graph JSON or YAML files:

```bash
uv run python -m src.measure results/extraction/<run id>/graphs --out results/measures.csv
```

It prints how many graphs are valid and invalid per source,
lists every invalid graph with its errors,
and prints the human vs ChatGPT comparison with the split-half baseline.
Graphs with `implicit_main` (no main claim) are counted as invalid for now,
because the measures that need a main claim are not defined for them.

To explore single answers in a browser (extract, draw, measure):

```bash
uv run streamlit run app.py
```

To run the tests:

```bash
uv run pytest tests
```

To re-run the data exploration:

```bash
uv run --with nbconvert jupyter nbconvert --to notebook --execute --inplace data_exploration.ipynb
```

It needs internet access to download HC3 and FiQA.

## Run the Streamlit app

The app turns an answer into a reasoning graph and draws it.

Before you start, make sure you have:

1. **Dependencies:** run `uv sync` (see Setup).
2. **Claude API access:** an Anthropic API key with credit, from the [Claude Console](https://console.anthropic.com/).
   API usage is billed separately from a Claude Pro or Max subscription.
   Put the key in `.env` as `ANTHROPIC_API_KEY=...`.
3. **Data:** run `uv run scripts/get_data.py`.
   You only need this for the `Dataset` input, not for `Own text`.

Then start the app from the repo root:

```bash
uv run streamlit run app.py
```

Streamlit prints a local URL. Open it in your browser.

Each new extraction calls Claude and uses API credit.
Saved graphs in `results/app/graphs/` are reused, unless you tick `Re-extract`.

If no API key is set, the app falls back to your Claude Code login (`EXTRACT_BACKEND=cli`).
`.env.example` lists the other optional settings.

## Run the 3D Language Sails / Analyser (Mind Graft)

Language Sails is an interactive 3D Three.js visualizer located in `mind-graft/`. It models argumentation topology as orbits and "sails" across human and LLM answers.

It requires **no API keys** and has zero external dependencies (pure Three.js and Python standard library):

```bash
# Option 1: Open directly in your browser
open mind-graft/viewer/language_analyser.html
# Or for the sails view:
open mind-graft/viewer/language_sails.html

# Option 2: Serve via local HTTP server
python3 -m http.server 8000 --directory mind-graft/viewer
# Visit http://localhost:8000/language_analyser.html in your browser
```

## Working with Claude Code

To run Claude Code with your research loop:

```bash
# Goal-directed loop: runs until condition is met
/goal src/measure.py reports no invalid graphs in results/graphs/, and the extractor-vs-hand score from annotations/ is recorded in JOURNAL.md

# Scheduled loop: periodically monitors and records progress
/loop 10m check extractor output and log new results to JOURNAL.md
```

## Licenses

- **Code**: [Apache License 2.0](LICENSE)
- **Documentation & Written Materials**: [Creative Commons Attribution 4.0 International](LICENSE-docs)
- **Data derived from HC3 and FiQA**: [Creative Commons Attribution-ShareAlike 4.0 International](LICENSE-data),
  following the HC3 license.

CC BY-SA 4.0 covers everything that contains or is derived from HC3 or FiQA text:

- `data/`: downloaded and filtered HC3 (not in git)
- `annotations/`: hand-made graphs
- `results/`: extracted graphs, measures and plots
- `data_exploration.ipynb`: the whole notebook, because its outputs contain HC3 and FiQA text

HC3: Guo et al., [How Close is ChatGPT to Human Experts?](https://arxiv.org/abs/2301.07597) (2023), CC BY-SA 4.0.
