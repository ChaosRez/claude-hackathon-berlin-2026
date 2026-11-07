# Applications and evaluation design for HC3 argument graphs

Scope: what can the team do with ~400 typed argument graphs (human vs ChatGPT, maybe Claude)?
Focus: predicting authorship from graph structure alone on a held-out set, plus other demo options.
Status as of 2026-11-07.
Numbers marked "unverified" come from search snippets or secondary summaries, not from the paper text.

## Q1. Structure-only AI-text detection: prior results and realistic accuracy

### Takeaway
Pure structure features are weak detectors on HC3.
The closest prior work (RST discourse motifs, Threads of Subtlety) reached only F1 0.55 with a Random Forest on motifs alone, versus 0.97–0.99 for a text model.
Expect roughly 0.55–0.75 accuracy from ~10 graph features with n≈400, and treat anything near 0.9 as a probable leak (length, sentence count, or extractor artefacts).

### Cited Findings
- HC3 RoBERTa detector, trained and tested on full English answers: F1 99.82 (raw-full → raw-full); GLTR (logistic regression on token-rank features) 98.26 — [HC3 paper, Table 4](https://arxiv.org/html/2301.07597)
- Same RoBERTa trained on full answers drops to F1 81.89 when tested on single sentences — [HC3 paper, Table 4](https://arxiv.org/html/2301.07597)
- Per-subset RoBERTa F1 (trained filtered-full, tested full): finance 99.34 human / 99.28 ChatGPT; wiki_csai 96.59 / 96.37. The paper calls wiki_csai the harder subset — [HC3 paper, Table 7](https://arxiv.org/html/2301.07597)
- Sentence-level GLTR on wiki_csai: F1 39.24 for human sentences vs 76.94 for ChatGPT sentences — an example of strongly asymmetric per-class errors — [HC3 paper, Table 7](https://arxiv.org/html/2301.07597)
- Average answer length (words): finance human 202.07 vs ChatGPT 226.01; wiki_csai human 229.34 vs ChatGPT 208.33. Over all English HC3: 142.50 vs 198.14 — [HC3 paper, Table 3](https://arxiv.org/html/2301.07597)
- HC3 qualitative finding: ChatGPT "usually defines the core concept, explains step by step, and ends with a summary"; humans digress more, are more colloquial, and use more exclamation/question marks. ChatGPT uses connectives like "In general" and "On the other hand" — [HC3 paper](https://arxiv.org/html/2301.07597). (This "define → explain → summarise" arc is exactly what a typed graph could capture, e.g. a trailing `restates` node.)
- Threads of Subtlety (Kim et al., ACL 2024): RST parse → recursive hypergraph → discourse motifs. F1 on HC3 test: RF on 207 filtered motifs 0.55; RF on all 3,055 motifs 0.55; GAT 0.67; GAT+motifs 0.73; Longformer 0.97; Longformer+motifs 0.98 — [arXiv 2402.10586v2, Table 3](https://arxiv.org/html/2402.10586v2)
- Same paper: on DeepfakeTextDetect OOD, Longformer 0.74 → 0.82 with motifs, so structure helps most as an add-on under distribution shift, not as a standalone detector — [arXiv 2402.10586v2](https://arxiv.org/html/2402.10586v2)
- Same paper: human texts show more structural variability; machine texts use more Elaboration and Temporal relations as length grows; humans use more Joint relations — [arXiv 2402.10586v2](https://arxiv.org/html/2402.10586v2)
- CoCo (Liu et al., EMNLP 2023): entity-coherence graph + supervised contrastive learning for low-resource detection; reports beating SOTA on 2 public + 2 own datasets, and that newer-LM text is easier to detect. Exact numbers not checked — [ACL Anthology 2023.emnlp-main.1005](https://aclanthology.org/2023.emnlp-main.1005); [arXiv 2212.10341](https://arxiv.org/html/2212.10341v2). Note: CoCo combines the graph with a RoBERTa text encoder, so it is not structure-only (from my reading of the method; unverified in this session).
- "AI Argues Differently" (Dönmez, Maurer, Lapesa, Falenska; EMNLP 2025): 301 linguistic + 27 argument-quality features on r/ChangeMyView vs GPT-3.5/LLaMA2-7B/Mistral-7B replies; reported >98% accuracy with a lightweight interpretable classifier (accuracy from search snippet, unverified). Features include text content cues, so it is not structure-only — [ACL Anthology 2025.emnlp-main.1755](https://aclanthology.org/2025.emnlp-main.1755)
- LLM arguments there are described as "textbook-style": cogent, justified, respectful, positive — [ACL Anthology 2025.emnlp-main.1755](https://aclanthology.org/2025.emnlp-main.1755) (secondary summary, unverified wording)
- GPT-who (Venkatraman, Uchendu, Lee; Findings NAACL 2024): Uniform-Information-Density features (a small hand-crafted feature set) reportedly beat GLTR, GPTZero, DetectGPT, OpenAI detector by >20% across four benchmarks. These features use token probabilities, so they are not structure-only — [arXiv 2310.06202](https://arxiv.org/abs/2310.06202)
- Length-matched HC3 benchmark (Baidya et al., arXiv 2603.17522, preprint): after ±20% word-count matching, a 22-feature classical set still gets in-distribution AUROC 0.888 (LogReg) / 0.977 (RF), dropping to 0.74 / 0.78 for HC3→ELI5 and 0.74 / 0.63 for ELI5→HC3. RoBERTa: 0.9994 in-dist., 0.974 HC3→ELI5 — [arXiv 2603.17522](https://arxiv.org/html/2603.17522v1)
- Same benchmark: "no detector generalizes robustly across both LLM sources and domains at once"; it does not report a length-only baseline — [arXiv 2603.17522](https://arxiv.org/html/2603.17522v1)
- RACE (ACL 2026) uses an RST "logic graph" plus EDU-level style features for a 4-way human/LLM/humanized/polished task; details not checked — [ACL 2026.acl-long.235](https://aclanthology.org/2026.acl-long.235.pdf)

### Inferences
- The project's graphs are coarser than RST trees (5 relation types, ~5–15 nodes).
  Threads of Subtlety's RF-on-motifs result (F1 0.55 on HC3, thousands of training texts) is the most comparable reference point.
  So a structure-only classifier at 0.55–0.70 would be consistent with literature; it would not be a failure.
- The gap to a text classifier (~0.99) is the headline: "argument structure carries little / some authorship signal compared with wording."
  That is a clean, honest result either way.
- Statistical resolution with small n (computed with a deterministic script, Wilson 95% intervals):
  - n=80 held-out texts: accuracy 0.75 has CI ≈ [0.65, 0.83]; 0.60 has CI ≈ [0.49, 0.70] (not distinguishable from chance).
  - n=400 (pooled cross-validation predictions): 0.60 → [0.55, 0.65]; 0.75 → [0.71, 0.79].
  - One-sided binomial test vs 0.5 (p<0.05) needs ≥0.60 on n=80, ≥0.565 on n=200, ≥0.5425 on n=400.
  - Pooled CV predictions are not fully independent (paired answers share a question), so these intervals are optimistic; a permutation test with question-grouped shuffling is safer.
- Finance is a domain where ChatGPT is ~12% longer than humans; wiki_csai is reversed (humans ~10% longer).
  Any length-driven classifier trained on finance should flip sign on wiki_csai — a useful leakage diagnostic.
- ChatGPT's "define → explain → summarise" pattern predicts specific features: a final `restates` edge back to the root, more `explains` edges, fewer `attacks` edges, lower depth variance.
  These are concrete, pre-registerable hypotheses.

### Gaps
- No published result found for a detector using only an LLM-extracted argument graph (claim/premise roles + support/attack edges) without text. This is a genuine gap — and a selling point.
- CoCo, GPT-who and DeTeCtive exact HC3 numbers were not verified; DeTeCtive (NeurIPS 2024, contrastive multi-level text embeddings) was not checked at all and is text-based anyway.
- "AI Argues Differently" per-feature-set accuracies (argument-quality-only vs linguistic) not obtained; PDF text was not readable in this session.

## Q2. Proper evaluation design

### Takeaway
Use question-grouped cross-validation, report every result next to trivial baselines (length, sentence count) and a human-vs-human control, and run a cross-domain test (finance ↔ wiki_csai).
The main risk is that the classifier learns graph size, not argument shape.

### Cited Findings
- Length is a known shortcut in HC3; the 2026 benchmark length-matched pairs (±20% words) explicitly to "neutralise" it — [arXiv 2603.17522](https://arxiv.org/html/2603.17522v1)
- Cross-domain is where feature classifiers break: RF 22 features drops from AUROC 0.977 (HC3→HC3) to 0.634 (ELI5→HC3) — [arXiv 2603.17522](https://arxiv.org/html/2603.17522v1)
- HC3 authors tested robustness to "indicator words" by filtering them; RoBERTa lost only 0.03 F1 points on English full — [HC3 paper](https://arxiv.org/abs/2301.07597) (via search snippet). Giveaway phrases are therefore a known HC3 concern.
- HC3 limited diversity (one generator, simple prompts) is criticised in the Wu et al. survey (Computational Linguistics 2025) — [arXiv 2310.14724](https://arxiv.org/abs/2310.14724)
- HC3 ChatGPT answers sometimes refuse ("beyond my knowledge") — [HC3 paper](https://arxiv.org/html/2301.07597). A refusal sentence becomes a distinctive node and a structural giveaway.
- Grouped splitting: scikit-learn `GroupKFold` / `StratifiedGroupKFold` keep all samples of one group in the same fold — [scikit-learn docs](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html) (standard API; page not fetched in this session)

### Inferences
Recommended protocol (concrete, 1-day feasible):
1. **Unit and groups.** One row per answer. Group id = HC3 question id. Human and ChatGPT answers to the same question always fall in the same fold.
2. **Splits.** 5-fold `StratifiedGroupKFold`, repeated 10× with different seeds; report mean ± sd and pooled predictions. Optionally freeze a 20% question-level hold-out first and touch it once (the "validation set" from the whiteboard).
3. **Paired framing (strongest design).** Because each question has one human and one ChatGPT answer, also run a *pairwise* task: given two graphs for the same question, which one is the LLM? Chance = 50%, and length/topic are controlled within the pair. Report a sign test.
4. **Feature sets (ladder of baselines), same classifier (logistic regression, small RF):**
   - B0: majority class (= 50% if balanced).
   - B1: sentence count only (= node count; the graph's size).
   - B2: word count only (from text — allowed for a baseline, not for the main model).
   - B3: bag of relation types (counts of supports/attacks/explains/example/restates).
   - M1: ~10 structural features normalised by node count (edge-type proportions, depth, branching, share of leaves, root position, presence of trailing `restates`, number of components).
   - M2: M1 + B1 (does structure add over size?).
   - T: text classifier (TF-IDF + LogReg is enough; the HC3 RoBERTa checkpoint is the ceiling — note it was trained on all of HC3, so evaluating it on HC3 is leaked).
   The key claim is M1 vs B1, and M2 vs B1, not M1 vs chance.
5. **Size control.** Also report results on a length-matched subset (pairs within ±20% sentences), following the 2603.17522 recipe.
6. **Human-vs-human baseline (project rule).** HC3 has several human answers for some questions. Train the same classifier to separate human answer #1 vs human answer #2 (random labels within question). It should sit at ~50%. Also report graph-distance distributions human–human vs human–LLM.
7. **Cross-domain.** Train on finance, test on wiki_csai and the reverse. Because the length direction flips between subsets, a size-driven model should collapse here.
8. **Cross-model.** Train on HC3 ChatGPT (GPT-3.5, early 2023), test on fresh Claude answers to the same questions. Caveat: fresh answers differ in era *and* model *and* prompt; label it "generation shift", not "model difference".
9. **Extractor audit, per class (project rule).** Report extractor agreement with `annotations/` separately for human and LLM texts. If the extractor is less accurate on human text, part of any "human graphs are messier" finding is extractor noise. One test: train the detector to predict *whether the extractor made an error*; if that is predictable from class, flag it.
10. **Leakage checklist.**
    - Extractor sees text: it may "recognise" ChatGPT style and impose a cleaner template. Mitigation: the hand-label check above; optionally strip giveaway phrases ("In summary", "As an AI") before extraction and see if the result survives.
    - Refusal/disclaimer sentences: count how many LLM graphs contain them; rerun without them.
    - Sentence splitting differences (lists, bullet points in ChatGPT answers) inflate node count.
    - Do not tune features on the held-out set; fix the feature list in `JOURNAL.md` before running.
    - Count graphs that fail validation and report them per class (a class-imbalanced failure rate is itself a leak).
11. **Significance.** Permutation test with labels shuffled within question pairs (1,000 permutations) for M1 and for M1−B1 difference; bootstrap over questions for CIs.

Expected outcome (my estimate, not sourced): B1 alone ≈ 0.55–0.65 on finance; M1 ≈ 0.6–0.75; pairwise task somewhat higher; cross-domain near chance for size-driven models.

### Gaps
- No source found giving a structure-only HC3 result with question-grouped splits; most papers use random splits, so their numbers may be optimistic for our design.
- Whether HC3 finance/wiki_csai questions have multiple human answers (needed for the human-vs-human control) was not checked here; verify in the data.

## Q3. Other applications worth a hackathon demo

### Takeaway
The strongest add-on stories are (a) "argument homogenisation" — do LLM graphs look more alike than human graphs? — and (b) "did structure change from GPT-3.5 (2023) to Claude (2026)?".
Both use the same graphs and fit the structure-only rule.

### Cited Findings
- "Argument Collapse: LLMs Flatten Long-Form Public Debate" (arXiv 2606.01736, June 2026 preprint): 65.3% of human main arguments unique within a debate vs 3.4% of LLM ones; among essays sharing a main argument, sub-argument uniqueness 41.0% human vs 9.1% vanilla LLM; LLM essays follow a fixed arc (direct claim → proposals) — [arXiv 2606.01736](https://arxiv.org/html/2606.01736) (search snippet; unverified)
- Inoshita et al. (arXiv 2603.21228, preprint): 6,875 essays; AI essays reach comparable *structural complexity* to human essays but much lower *claim rarity*; prompt specificity can reverse homogenisation — [arXiv 2603.21228](https://arxiv.org/abs/2603.21228) (snippet; unverified)
- Threads of Subtlety: human texts show more structural variability across domains — [arXiv 2402.10586v2](https://arxiv.org/html/2402.10586v2)
- CoCo: text from newer LMs was easier to detect than from older ones — [arXiv 2212.10341](https://arxiv.org/html/2212.10341v2)
- "AI Argues Differently": LLM counter-arguments align more with the original post's style/quality than human replies do — [ACL 2025.emnlp-main.1755](https://aclanthology.org/2025.emnlp-main.1755) (secondary summary)

### Inferences
Ranked by value-to-effort for one day:
1. **Structural homogenisation (low effort, high value).** Compute pairwise graph distances (e.g. edit distance on role/edge-type labels, or distance between feature vectors) within the human set and within the LLM set. Prediction from literature: LLM–LLM distances are smaller. Directly echoes "argument collapse", but at structure level, which Inoshita et al. suggest may *not* collapse — so either outcome is interesting.
2. **GPT-3.5 (HC3) vs current Claude (medium effort).** Generate Claude answers to the same ~200 questions; compare feature distributions three ways (human, ChatGPT-2023, Claude-2026) with the human–human baseline. Watch for length change: modern models may answer much longer, so normalise by node count.
3. **Interactive graph explorer (low–medium effort, best demo).** Side-by-side human vs LLM graph for the same question, colour by edge type, with the detector's probability. Judges grasp it in seconds. Must not be the only result.
4. **Structural "fingerprint" card.** Per class: mean depth, % `attacks`, % `example`, trailing `restates` rate. A small table that is easy to defend.
5. **Argument-quality / tutoring feedback (higher risk).** E.g. flag "no support for main claim" or "no counter-argument considered". Needs a quality ground truth that the team does not have; present only as a sketch.
6. **Authorship prediction on held-out set (the whiteboard idea).** Feasible and clean if framed as "how much does structure alone tell us?", with the baselines ladder from Q2.

### Gaps
- No source found on argument-graph differences between GPT-3.5-era and 2025–2026 models specifically.
- Argument-quality literature (e.g. IBM ArgQ, Wachsmuth taxonomy) was not researched in this session.

## Q4. What makes a convincing 1-day result

### Takeaway
A pre-registered, baseline-controlled null or small effect is more convincing than a large unexplained accuracy.
Show the size baseline, the human-vs-human control and the extractor audit on one slide.

### Cited Findings
- The literature reference point to beat is small: structure-only motifs F1 0.55 on HC3 — [arXiv 2402.10586v2](https://arxiv.org/html/2402.10586v2); text detectors ≈ 0.99 — [HC3 paper](https://arxiv.org/html/2301.07597).
- Detectors that look near-perfect in-distribution degrade sharply cross-domain, so in-distribution numbers alone persuade little — [arXiv 2603.17522](https://arxiv.org/html/2603.17522v1)

### Inferences
- Pre-register hypotheses and the feature list in `JOURNAL.md` before running (timestamped). Report everything, including failed graphs.
- Lead with one figure: accuracy bars for B1 (size), M1 (structure), M2, T (text), human-vs-human control, each with a CI, for in-domain and cross-domain.
- Show 3 real example pairs with the graphs, as the project rules require; judges value seeing the data.
- One command reproduces the numbers (`make results` or a single script) with fixed seeds.
- Acceptable headline formats:
  - "Argument structure alone identifies ChatGPT answers at X% (CI), Y points above a size-only baseline; text gets 99%."
  - or "Once size is controlled, structure carries no reliable signal (X%, CI includes 50%)." Both are defensible.
- Red flags to pre-empt: accuracy > 0.9 from structure only; large gap in extractor accuracy between classes; effect vanishes on length-matched subset.

### Gaps
- No published hackathon-judging criteria for the Claude Impact Lab Berlin event were researched; check `hackathon_agenda/` in the repo.
