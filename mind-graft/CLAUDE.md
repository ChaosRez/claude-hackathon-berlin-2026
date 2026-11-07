# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this is

Language Sails compares the reasoning structure of human and LLM answers. Answers are cut into **entities**. Each entity gets a type, a parent it builds on and any earlier points it repeats. The results are drawn as 3D graphs: z = length in words, y = depth, x = opposition. The web app is called **Language Analyser**.

## Commands

All scripts use only the Python 3.12 standard library. Run them with `python -I` from the repo root.

```bash
# 1. Filter HC3 to rows where the human and ChatGPT answers differ by < 10 words
python -I scripts/select_similar_length.py data/raw/HC3_all.jsonl data/hc3_similar_length_100

# 2. Split answers into candidate segments
python -I scripts/segment_answers.py data/hc3_similar_length_100.jsonl data/work/segments.json data/work/segments.txt

# 3. Validate labels and build graph data and summaries
python -I scripts/build_entity_graphs.py data/work/segments.json data/labels data/entity_graphs.json data/entity_summary.csv

# 4. Build the app's built-in datasets (ELI5 hand labels, plus Finance and CSAI segmented)
python -I scripts/build_analyser_data.py

# 5. Embed data into the single-file web pages
python -I scripts/build_viewer.py viewer/language_analyser.template.html data/analyser_builtin.json viewer/language_analyser.html
python -I scripts/build_viewer.py viewer/language_sails.template.html data/entity_graphs.json viewer/language_sails.html
```

`data/raw/HC3_all.jsonl` (74 MB) is not committed. Download it from
`https://huggingface.co/datasets/Hello-SimpleAI/HC3/resolve/main/all.jsonl`.

## Rules

- **Edit the templates, never the built pages.** Change `viewer/*.template.html`, then rebuild with `build_viewer.py`. The built `.html` files are generated.
- **The codebook is the contract.** Labels live in `data/labels/*.txt` in the format described in `docs/entity_codebook.md`. If you change the entity types, the token grammar or the segmentation rules, update all three of these together:
  - the Python in `scripts/segment_answers.py` and `scripts/build_entity_graphs.py`
  - the JavaScript copies inside `viewer/language_analyser.template.html` (`segment`, `buildAnswer`, `heuristic`, `typology`, `CODEBOOK`)
  - `docs/entity_codebook.md` and the README
- **Keep the meaning of the visual encodings.** Orange is human and purple is LLM. Each entity type has its own 3D shape. Each relationship has its own line style: supports is continuous, disagrees dashed, qualifies dash-dot and reinforces dotted.
- **Say how a dataset was labelled.** Hand, Claude in app or rule-based. Don't compare a rule-based dataset with a Claude-labelled one without saying so.
- **Validate after changing labels.** `build_entity_graphs.py` must exit cleanly: token counts must match segments, and references must point backwards.

## Git workflow

- Start each piece of work on its own branch off `main`, and merge through a pull request.
- Don't commit `data/raw/` or other large raw downloads.

## The hackathon group repo (one way only)

- Mind Graft takes files FROM `ChaosRez/claude-hackathon-berlin-2026`. Nothing from this repo goes into the group repo: no pushes, pull requests, issues or edits there.
- Copies live in `upstream/group-repo/`, unchanged, with `SOURCE.md` recording the commit they came from. Refresh them only with `python -I scripts/sync_group_schema.py`, and review the diff before committing.
- Never edit files under `upstream/`. Adapt to them in Mind Graft's own code instead, for example by mapping our entity codebook onto their `entity_definition.yaml` and `relation.yaml`.
