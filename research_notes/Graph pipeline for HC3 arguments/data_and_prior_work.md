# HC3 data, second-topic choice, and prior work on human vs LLM text structure

Research date: 2026-11-07.
HC3 numbers below come from a deterministic Python script run on the raw files
`finance.jsonl` and `wiki_csai.jsonl`, downloaded from
https://huggingface.co/datasets/Hello-SimpleAI/HC3 (scripts in the session scratchpad, not in the repo).
The regex question categories are rough heuristics, not hand labels.

## Q1. HC3 facts: subsets, counts, lengths, format, quality problems

### Takeaway
Finance has 3,933 questions and wiki_csai has 842.
Each has exactly 1 human answer per question.
Finance has 1–2 ChatGPT answers per question.
The biggest pipeline risk: in about 90% of finance ChatGPT answers, sentences are glued together with no space (for example `contacts.Consider`).
Line breaks were removed.
A naive sentence splitter will under-count ChatGPT sentences, so it will under-count ChatGPT nodes.
Only about 7% (277) of finance questions look like advice or opinion questions.
wiki_csai questions are all "Please explain what is X", so they invite definitions, not arguments.

### Cited Findings
- HF configs: `all`, `finance`, `medicine`, `open_qa`, `reddit_eli5`, `wiki_csai`. Each has one `train` split. Row counts: all 24,322; reddit_eli5 17,112; finance 3,933; medicine 1,248; open_qa 1,187; wiki_csai 842. — [HF datasets-server /size](https://datasets-server.huggingface.co/size?dataset=Hello-SimpleAI/HC3)
- Format: JSONL, one question per line. Fields: `question` (str), `human_answers` (list[str]), `chatgpt_answers` (list[str]). The `all` config has 5 columns, probably adding a source field (I did not check). — [HF files](https://huggingface.co/datasets/Hello-SimpleAI/HC3), own script
- Human-answer sources per the authors' README: reddit_eli5 ← ELI5 (BSD), open_qa ← WikiQA, wiki_csai ← Wikipedia (CC-BY-SA), medicine ← Medical Dialog (license unknown), finance ← FiQA (license "Unknown", "Asking by 📧"). The corpus follows CC-BY-SA unless a source license is stricter. — [GitHub README](https://github.com/Hello-SimpleAI/chatgpt-comparison-detection)
- ChatGPT answers were collected from 2022-12-11 onward, so they come from the Dec-2022 ChatGPT (GPT-3.5). — [GitHub README](https://github.com/Hello-SimpleAI/chatgpt-comparison-detection)
- The HC3 paper (arXiv 2301.07597, v1 only, 18 Jan 2023, no venue listed) describes "tens of thousands" of paired answers across open-domain, financial, medical, legal and psychological questions. It also reports human evaluations, linguistic analyses, and three detectors. — [arXiv](https://arxiv.org/abs/2301.07597)
- **Finance (own script):**
  - 3,933 questions, all with 1 human answer. 3,363 questions have 1 ChatGPT answer, and 570 have 2. That gives 4,503 ChatGPT answers.
  - Human words: mean 175.6, median 129, p10 40, p90 357.
  - ChatGPT words: mean 203.8, median 205, p10 124, p90 280.
  - So human answers vary much more in length.
  - Median per-question ChatGPT/human word ratio is 1.52. Only 1,286 of 3,933 questions (33%) fall within a ratio of 0.67–1.5.
  - Naive sentence split (`[.!?]` followed by whitespace): human mean 9.0 / median 7; ChatGPT mean 5.7 / median 6. The ChatGPT figure is wrong because of the glued-sentence artifact below.
- **Finance artifacts (own script):**
  - 4,069 of 4,503 ChatGPT answers (90.4%) contain a sentence end with no following space (`[a-z0-9][.:!?][A-Z]`). Only 31 of 3,933 human answers do.
  - 2,286 human answers contain double spaces, probably where line breaks were collapsed. Only 2 ChatGPT answers do.
  - 262 human answers contain `http` links. 2 human answers contain HTML-like tags.
  - No duplicate questions. 41 duplicate ChatGPT answer strings. No duplicate human answers.
- **Finance ChatGPT giveaway phrases (count of answers that contain the phrase, human vs ChatGPT):**

  | Phrase | Human | ChatGPT |
  |---|---|---|
  | "It's important to" | 15 | 1,573 |
  | "It is important to" | 11 | 979 |
  | "consult" | 68 | 902 |
  | "Overall" | 76 | 778 |
  | "However," | 363 | 1,200 |
  | "I'm sorry" | 3 | 68 |
  | "I'm sorry, but" | – | 55 |

  The "I'm sorry, but" answers are likely refusals or "I can't access …" answers.
  68 ChatGPT answers begin with "It depends" or "It is difficult" or similar.
- **Finance question types (own regex heuristic):**
  - 213 questions contain "should" (for example "Should I buy a house with a friend?").
  - Union advice/opinion regex (should I/we, is it worth/a good idea/better to, recommend, advice): 277 of 3,933 (~7%).
  - 1,513 questions start with a wh-word. 712 start with an auxiliary verb (can/do/is …).
- Sample finance human answers are informal forum posts. They reply to other answers ("Realize this is almost a year old, but I just wanted to comment on … Dynas' answer above"), give personal experience ("As I have worked for H&R Block …"), and contain typos. — own sample
- **wiki_csai (own script):**
  - 842 questions, 1 human and 1 ChatGPT answer each.
  - Human words: mean 195.5, median 166, p10 61, p90 369. ChatGPT words: mean 185.3, median 187.5, p10 119, p90 243.
  - Median per-question length ratio is 1.12, and 338 of 842 (40%) fall within 0.67–1.5.
  - Naive sentence counts are similar: human mean 8.1, ChatGPT 7.7.
  - Only 20 ChatGPT answers have the glued-sentence artifact.
  - All 842 questions follow the template "Please explain what is \"X\"". 0 match the advice regex.
  - 62 groups of identical human answers (71 extra copies): different question titles map to the same Wikipedia lead (for example the "classification" text appears 4 times).
  - 208 human answers contain `[`, likely leftover citation or bracket markup. 11 ChatGPT answers contain "I'm sorry".

### Inferences
- Before sentence splitting, insert a space at `([a-z0-9][.!?])([A-Z])` for both sources. Re-check the result by hand, because abbreviations and tickers like "U.S." can break. Without this fix, ChatGPT finance graphs will look artificially small.
- In finance, a human answer often replies to another human answer. That is a different discourse situation from ChatGPT answering the question directly. Edges like "attacks another answer" have no ChatGPT counterpart.
- Exclude or flag ChatGPT refusals ("I'm sorry, but …", ~55–68 in finance). Count them in the denominator; do not drop them silently.
- Finance: use only the first ChatGPT answer per question, or keep the second one as a ChatGPT-vs-ChatGPT baseline for 570 questions. HC3 has only 1 human answer per question, so it has no human-vs-human baseline on the same question. The project rules require one: it must come from different questions, a second human source, or another dataset.
- wiki_csai deduplication: drop questions whose human answer duplicates another one, or treat them as one item.

### Gaps
- I did not verify whether the HC3 paper describes extra cleaning, such as removing newlines. The cause of the glued sentences is inferred, not documented.
- I did not compute statistics for medicine, open_qa or reddit_eli5. The CLAUDE.md claim about unequal lengths in those subsets is not re-verified here.
- The FiQA license for finance human answers is still listed as "Unknown" by the HC3 authors. This affects the CC BY-SA assumption.
- The 7% advice share comes from a regex. A hand-labelled sample would be more reliable.

## Q2. Which second topic is best for argument structure?

### Takeaway
wiki_csai is length-balanced and clean, but it is definitional encyclopedia text with almost no argumentation.
Graphs will be mostly "explains/elaborates" chains on both sides.
That makes it a useful **low-argument control**, not a second argument domain.
For real argument structure, the best paired same-prompt source is r/ChangeMyView.
Options include MAGE/DeepfakeTextDetect's `cmv` domain, the Counterfire corpus, and the CMV data of Dönmez et al.
The project rules currently allow only finance or wiki_csai, so using CMV is a rule change for the team to decide.

### Cited Findings
- wiki_csai human answers are Wikipedia leads (source Wikipedia, CC-BY-SA). — [GitHub README](https://github.com/Hello-SimpleAI/chatgpt-comparison-detection); all 842 prompts are "Please explain what is X" (own script).
- MAGE (DeepfakeTextDetect) has 10 source domains: CMV, ELI5, HellaSwag, ROC, SciGen, SQuAD, TLDR, WP, XSum, Yelp. — secondary listing via [search result](https://arxiv.org/pdf/2608.10459) (not checked against the MAGE paper)
- Threads of Subtlety used DeepfakeTextDetect's yelp, wp, cmv, xsum and sci_gen domains together with HC3. — [arXiv 2402.10586v2](https://arxiv.org/html/2402.10586v2)
- RAID covers 8 domains: abstracts, books, news, poetry, recipes, Reddit, reviews, Wiki. It has about 2,000 human documents per domain, and machine text is generated from a templated prompt built from each human document's title. — [RAID arXiv 2405.07940](https://arxiv.org/pdf/2405.07940)
- Counterfire: about 32,000 counter-arguments to CMV posts, generated by GPT-3.5 Turbo, Koala, PaLM 2 and fine-tuned variants. In human evaluation, human-written arguments were judged most persuasive. — via [search summary](https://www.catalyzex.com/paper/auditing-counterfire-evaluating-advanced) (secondary; not verified at primary source)
- Dönmez et al. (EMNLP 2025) compare CMV counter-arguments written by humans and by 3 LLMs to the same posts. — [ACL Anthology](https://aclanthology.org/2025.emnlp-main.1755/)
- Argument Collapse uses NYT debates (1,039 human responses, 195 debates) and Boston Review forums (448 responses, 61 forums), with 23,381 LLM essays on the same prompts. — [arXiv 2606.01736](https://arxiv.org/abs/2606.01736). I did not check whether the data is released.
- Herbold et al. (Sci. Reports 2023) compare human vs ChatGPT argumentative student essays on the same prompts. ChatGPT essays are "highly structured", and all their concluding sections begin identically. — [Nature](https://www.nature.com/articles/s41598-023-45644-9)

### Inferences
- **Recommended setup (team decides):**
  - Finance, filtered to advice/opinion questions plus length-matched explanatory ones, as the "argumentative" topic.
  - wiki_csai as the "definitional" control.
  - If the team wants a second real argument domain, CMV paired data (MAGE `cmv` or Dönmez et al.) fits best, but it needs a rule change and a licence check.
- Only ~277 finance questions are advice-style. Sampling 100 of them is feasible, but stratify: for example, 50 advice and 50 explanatory questions.
- **Length matching:**
  - Restrict to questions whose ChatGPT/human word ratio is within 0.67–1.5. That leaves 1,286 finance and 338 wiki_csai questions, which is enough for 100 each.
  - Alternatively, report graph metrics normalised by node count, and also compare within length bins.
  - Finance human length varies a lot (p10 40 words), so short human answers (<~60 words) give tiny graphs. Consider a minimum length.
- **Fresh answers from a current model (e.g. Claude):** generate on the same questions with a length instruction. Dec-2022 ChatGPT style ("It's important to … consult") may not represent current LLMs.
- **Second topic, other HC3 subsets:**
  - reddit_eli5 is explanatory and ELI5-style, and CLAUDE.md says its lengths are unequal (not re-verified here).
  - open_qa and medicine are excluded by the project rule.

### Gaps
- I did not verify MAGE's licence, its exact CMV pair counts, or whether it keeps prompt-to-human pairing per item.
- I did not verify M4's domains or pairing. Search results did not confirm them.
- I did not check Ghostbuster, persuade-corpus or the ArgumentAnnotatedEssays datasets for paired same-prompt LLM text.

## Q3. Prior work on structural differences between human and LLM text

### Takeaway
Prior work shows three things.
LLM texts have less varied discourse structure (RST motifs).
LLM arguments converge on few main arguments and on a fixed essay arc.
LLM arguments look "textbook" and two-sided.
None of the papers I found builds typed argument graphs (support/attack/example/restate) for human and LLM answers to the same questions and then compares them with graph metrics against a human-vs-human baseline.
That gap is open for this project.

### Cited Findings
- **Threads of Subtlety** (Kim, Lee, Zhu, Raheja, Kang; ACL 2024 main; arXiv 2402.10586)
  - Method: parse texts with RST using the DMRST parser, convert the trees to recursive hypergraphs, then count network motifs (3,055 motifs; 207 selected by MF-IDF).
  - Data: **HC3-English**, DeepfakeTextDetect (yelp, wp, cmv, xsum, sci_gen), and the new TenPageStories dataset.
  - F1 on the HC3 test set:

    | Model | F1 |
    |---|---|
    | Random Forest on motifs only | 0.55 |
    | Graph Attention Network (GAT) | 0.67 |
    | GAT + motifs | 0.73 |
    | Longformer | 0.97 |
    | Longformer + motifs | 0.98 |

  - Out-of-distribution F1: Longformer 0.74 → Longformer + motifs 0.82.
  - Humans show "more structural variability", but no number is given for it. Pearson r between formality and hyperedge frequency: 0.08 for machine text vs 0.39 for human text.
  - Open for this project: they use RST discourse relations, not argument relations. Their goal is detection, not description. They do not compare the same question side by side with a human baseline.
  - Sources: [arXiv](https://arxiv.org/abs/2402.10586), [full text](https://arxiv.org/html/2402.10586v2). The ACL Anthology ID appears to be 2024.acl-long.298 per a [preview link](https://preview.aclanthology.org/add_acl24_videos/2024.acl-long.298), not verified.
  - Note: 2024.acl-long.270 is a different paper (RelayAttention). — [ACL Anthology](https://aclanthology.org/2024.acl-long.270/)
- **Argument Collapse: LLMs Flatten Long-Form Public Debate** (Kim, Chang, Pham, Iyyer; arXiv 2606.01736, v1 1 Jun 2026, v4 2 Sep 2026)
  - Data: NYT debates and Boston Review forums vs 23,381 LLM essays.
  - Main arguments unique within a debate: 65.3% for humans vs 3.4% for LLMs.
  - Sub-arguments unique among essays with the same main argument: 41.0% for humans vs 9.1% for LLMs.
  - Prompting for diversity recovers only about half of the distinct human main arguments.
  - LLM essays follow a fixed arc: a direct claim first, then proposals.
  - Preference judges favour both the common arguments and the LLM essays.
  - A search snippet also gives 76.1% of human vs 63.4% of vanilla LLM essays taking a strong stance. **Unverified.**
  - Open for this project: it measures diversity of *content* across essays, not the internal graph topology of each answer. The page does not describe the extraction procedure.
  - Source: [arXiv](https://arxiv.org/abs/2606.01736)
- **AI Argues Differently** (Dönmez, Maurer, Lapesa, Falenska; EMNLP 2025)
  - Data: CMV, with human vs 3-LLM counter-arguments.
  - LLM counter-arguments have lower type-token and lemma-token ratios and higher emotional intensity (anticipation, trust).
  - They are more "textbook" (cogent, justified, respectful) and closer to the original post's style.
  - An interpretable classifier works well, but the abstract gives no numbers.
  - Open for this project: they use feature-level quality scores, not argument graphs.
  - Source: [ACL Anthology](https://aclanthology.org/2025.emnlp-main.1755/)
- **Herbold et al. 2023** (Sci. Reports)
  - Data: argumentative essays.
  - ChatGPT essays are highly structured, with identical openings of the concluding section. They use fewer discourse markers because the arguments are split into paragraphs.
  - Human raters scored ChatGPT-4 essays about 1 point higher than human essays.
  - Source: [Nature](https://www.nature.com/articles/s41598-023-45644-9)
- **GPT-4o vs L2 learner essays (Toulmin coding)**
  - GPT-4o mostly gives two-sided complete arguments. Learners are mostly one-sided.
  - GPT-4o uses more hedges, boosters and attitude markers. Learners use more self-mentions.
  - Source: [AJAL](https://caes.hku.hk/ajal/index.php/ajal/article/view/1554) (from search snippet; not read in full)
- **DeTeCtive** (Guo et al., NeurIPS 2024, arXiv 2410.20964)
  - Method: multi-level contrastive learning of writing style plus retrieval-based detection.
  - Results: claims state of the art, with large out-of-distribution zero-shot gains.
  - Relevance: a stylistic detector with no explicit structure or graph. Useful only as a contrast.
  - Source: [NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2024/hash/a117a3cd54b7affad04618c77c2fb18b-Abstract.html)
- **CoCo** (arXiv 2212.10341): an entity-coherence graph (Centering Theory) encoded for low-resource detection. I did not confirm whether it uses HC3. — [arXiv](https://arxiv.org/html/2212.10341v2)
- **LLM-based argument mining** (arXiv 2605.13793): extracts premises and conclusions, labels support/attack/undercut relations, and builds DAGs. It does not split results by human vs LLM text. Usable as an extractor design reference. — [arXiv](https://arxiv.org/html/2605.13793v2)
- **Argument schemes** (Findings ACL 2025, 2025.findings-acl.702): LLMs classify argument schemes better on generated arguments than on human ones. This matches the project rule that the extractor may read LLM text more easily. — [PDF](https://aclanthology.org/2025.findings-acl.702.pdf) (search summary; not read in full)

### Inferences
- Positioning: "We build typed argument graphs (not RST trees) per answer, on the same questions, compare topology (depth, branching, attack edges, example and restatement rates), and calibrate against a human-vs-human baseline and hand-checked extraction accuracy."
  Threads of Subtlety is the closest prior work and already used HC3, so cite it and contrast with it explicitly.
- Prior findings give testable hypotheses:
  - LLM graphs are more uniform across questions (lower variance in shape).
  - LLM graphs have fewer attack/concession edges outside formulaic "However," patterns, or more two-sided ones (Toulmin study).
  - LLM graphs have more "restates/summary" nodes, given 778 "Overall" answers in finance ChatGPT.
- The Findings ACL 2025 result supports the rule of measuring extractor accuracy separately on human and LLM text.

### Gaps
- I found no paper that compares claim/premise argument graphs of human vs LLM answers to the same questions. This is a "not found", not proof that none exists.
- I did not verify the Argument Collapse extraction method or whether its data is released.
- I did not verify the Dönmez et al. numbers or the dataset release.

## Q4. Existing graph analysis on HC3 specifically

### Takeaway
Threads of Subtlety (ACL 2024) applied RST-tree-derived hypergraph motif analysis and a Graph Attention Network to HC3-English.
It reports F1 of 0.67 for GAT alone and 0.73 with motifs.
I found no work that applies argument graphs to HC3.

### Cited Findings
- Threads of Subtlety uses the HC3-English test set with RST hypergraph motifs and GAT. — [arXiv 2402.10586v2](https://arxiv.org/html/2402.10586v2)
- A search for coherence or entity graphs on HC3 found CoCo and IDEATE (LREC 2024; entity graph plus external knowledge graph). Neither was confirmed to use HC3. — [IDEATE](https://aclanthology.org/2024.lrec-main.751.pdf), [CoCo](https://arxiv.org/html/2212.10341v2)

### Inferences
- The project should cite Threads of Subtlety as "graph analysis on HC3, discourse level, detection-oriented". Its own contribution is "argument level, descriptive, baseline-calibrated".

### Gaps
- I did not check whether Threads of Subtlety used all HC3 subsets or only some, or which HC3 test split it used.
