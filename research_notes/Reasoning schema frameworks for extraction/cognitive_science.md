# Cognitive-science and education frameworks for reasoning structure, judged as an extraction schema

Scope: frameworks from psychology, cognitive science and education research that define categories of reasoning moves.
Judged for one use: a sentence-level node/edge schema for HC3 human vs ChatGPT answers (finance, wiki_csai), extracted by Claude and compared by node roles and edge types only.
Marking convention: "[UNVERIFIED]" means the point comes from background knowledge and was not confirmed against a source in this session.
Research budget note: several primary full texts (Erduran et al. 2004 Table 2; Felton & Kuhn 2001; Kuhn 1991 prevalence tables) could not be fetched (403/503 or paywall).
So level definitions and percentages below rely on abstracts and secondary sources, flagged where so.

## Which categories are most cognitively "natural" (used spontaneously, teachable to novices quickly)?

### Takeaway
Claim and supporting reason/evidence are produced spontaneously by almost everyone.
Counterarguments, alternative explanations and rebuttals are rarely produced unprompted, even by adults, and are the moves education research has to teach explicitly.
So a schema built from Claim + Support (+ Attack/Rebuttal) matches how people naturally reason; finer Toulmin roles (warrant, backing, qualifier) are not natural and are hard to code.

### Cited Findings
- Mercier & Sperber's argumentative theory: the function of reasoning is "to devise and evaluate arguments intended to persuade" — reasoning evolved for producing reasons for one's own view and evaluating others' reasons, not for solitary truth-finding — [Dogramaci 2020, Episteme, summarising Mercier & Sperber 2011 BBS](https://philarchive.org/rec/DOGWIT).
- In that theory, "myside bias" is the tendency to look for reasons for our own ideas and against ideas we oppose; it replaces the label "confirmation bias" — [Dogramaci 2020](https://philarchive.org/archive/DOGWIT).
- Critique: the theory does not explain confirmation bias outside the reasoning domain — [Michel & Peters 2020](https://faculty.sites.uci.edu/cnclab/files/2020/10/Michel-Peters2020_Article_ConfirmationBiasWithoutRhymeOr.pdf); and its evolutionary premise is contested — [Dogramaci 2020](https://philarchive.org/rec/DOGWIT).
- Kuhn's *The Skills of Argument* (1991) interviewed people about causal theories and coded: causal theory (claim), supporting evidence, alternative theories, counterarguments, rebuttals. The book has separate chapters on counterarguments and rebuttals with prevalence data — [Cambridge chapter: Counterarguments](https://www.cambridge.org/core/books/skills-of-argument/counterarguments/11ECBD49902FEA29D60F5C6C7990DBB4); [Cambridge chapter: Rebuttals](https://www.cambridge.org/core/books/skills-of-argument/rebuttals/572661C088DA05E759FE09B8D8A8D7F4).
- Secondary report of Kuhn's sample: of 160 participants, only 22 developed refutations, and many gave no evidence for them — [Informal Logic paper citing Kuhn (vLex)](https://law-journals-books.vlex.com/vid/rebuttals-refutations-argumentative-69270782). Not checked against the book.
- Baron's review of Kuhn (1991): many subjects (fewer among college-educated) failed or only partly succeeded at generating alternative theories; some never attempted counterarguments or denied one was possible — [Baron review, Informal Logic](https://distantreader.org/stacks/journals/il/il-2526.pdf).
- Myside bias in writing: Wolfe & Britt (2008, *Thinking & Reasoning* 14(1)) define it as omitting other-side information from essays; people who think good arguments are those "proved by facts" show more of it; their notes, not their search behaviour, predicted the bias — [Wolfe & Britt 2008 PDF](https://iphils.uj.edu.pl/~a.trybus/classes/logic/cs/16.Wolfe.Locus.Of.Myside.pdf); [PhilPapers record](https://api.philpapers.org/rec/BRITLO-2).
- When other-side material does appear in student essays, its purpose is mostly rebuttal — [Wolfe & Britt 2008](https://iphils.uj.edu.pl/~a.trybus/classes/logic/cs/16.Wolfe.Locus.Of.Myside.pdf).
- Wolfe & Britt trace the bias to under-developed "argumentation schemata" — i.e., a missing concept of what an argument should contain, not a reasoning defect — [Wolfe & Britt 2008](https://iphils.uj.edu.pl/~a.trybus/classes/logic/cs/16.Wolfe.Locus.Of.Myside.pdf).
- Teachability: a brief written tutorial improved undergraduate argumentative essays and reduced myside bias; a web-based counterargument tutor taught students to identify counterarguments and classify whether they were rebutted, dismissed or conceded — [search summary of Wolfe et al. papers; Bohrium record of the tutor paper](https://www.bohrium.com/paper-details/the-efficacy-of-a-web-based-counterargument-tutor/811843936837435393-12238).
- But an intervention reduced myside bias in high-ability participants and increased it in low-ability ones — [Wolfe & Britt 2008](https://iphils.uj.edu.pl/~a.trybus/classes/logic/cs/16.Wolfe.Locus.Of.Myside.pdf). (Attribution to this exact paper is from a search summary; treat as needing check.)
- Argument mapping (box-and-arrow claim/reason/objection diagrams) is teachable to novices in one semester: van Gelder's Reason!Able/Rationale courses reported CCTST gains of about 0.8–0.89 SD over 12 weeks; Twardy's partial replication kept ~90% of the gain after controlling for teacher effect — [LessWrong summary of Twardy](https://www.lesswrong.com/posts/NJ8k2RTwy3ELmwYZT/argument-maps-improve-critical-thinking); [Twardy paper, PhilArchive](https://philarchive.org/archive/TWAAMIv1); [ter Berg & van Gelder 2015](https://www.reasoninglab.com/wp-content/uploads/2013/10/TvG-Using-argument-mapping-to-improve-critical-thinking-skills-2015.pdf).
- Pencil-and-paper mapping also improved critical thinking (Harrell) — [Davies, PhilArchive](https://philarchive.org/archive/DAVCAM-3).
- Rationale-style maps use a small vocabulary: claim, reason (support), objection (attack), and rebuttal (objection to an objection) [UNVERIFIED — from knowledge of the tool; see [Critical Thinking with Rationale](https://issuu.com/reasoninglab/docs/critical_thinking_with_rationale)].
- Concept maps (Novak) and causal maps are a separate cognitive graph tradition: nodes are concepts, edges are labelled propositions ("causes", "is a"). [UNVERIFIED — not searched this session.] They represent knowledge, not argument, so their nodes are not sentences.
- Mental models (Johnson-Laird) and dual-process theory describe how inferences are computed, not which moves appear in text. [UNVERIFIED — not searched this session.] They give no annotation categories.

### Inferences
- The natural core is two node roles (Claim, Reason/Evidence) and two edge types (supports, attacks). Every framework above shares this core.
- Rationale's "objection" and "rebuttal" map cleanly to an attack edge and an attack-on-an-attack. This is a structural pattern, so it can be detected from edge types alone. That fits the project rule "compare roles and edge types only".
- Toulmin's warrant/backing/qualifier are not natural categories for novices (see reliability section). Avoid them as node roles for this project.
- Mental models, dual-process, Bayesian argument strength and concept maps add little as node/edge labels. They are useful as interpretation lenses, not as schema categories.

### Gaps
- Exact Kuhn (1991) prevalence percentages per category and age group: not retrieved; book is paywalled.
- No source found on how fast novices learn each specific category in a labelling task (as opposed to producing it).

## Which categories differ between skilled and unskilled reasoners, and are so likely sensitive to human vs LLM differences?

### Takeaway
The robust skill marker across Kuhn, TAP, Wolfe & Britt and Nussbaum is the same: considering the other side (counterargument / alternative) and then answering it (rebuttal) or integrating it (weighing, design claim).
For LLMs, the expected direction is unclear: ChatGPT often adds balanced "however" clauses and concessions, but early evidence suggests LLM text reproduces argumentative form well while being less original.
So counterargument and rebuttal edges are the best candidate signal, but the schema must separate "mentions the other side" from "answers it".

### Cited Findings
- TAP (Toulmin Argument Pattern) in science education: Erduran, Simon & Osborne (2004, *Science Education* 88(6): 915–933) built a 5-level hierarchy of argument quality for dialogic argumentation — [Bristol research record](https://research-information.bris.ac.uk/en/publications/tapping-into-argumentation-developments-in-the-application-of-tou/).
- In that hierarchy, an argument with a clearly identifiable rebuttal against the grounds of an opposing claim is Level 4 — [secondary teaching document](https://edisciplinas.usp.br/mod/resource/view.php?id=5385). Single secondary source.
- Level definitions as commonly cited [UNVERIFIED — from memory, check against Table 2 of the 2004 paper]: L1 claim vs counter-claim or claim vs claim; L2 claims with data, warrants or backings but no rebuttals; L3 series of claims/counter-claims with data, warrants or backings plus an occasional weak rebuttal; L4 claim with one clearly identifiable rebuttal; L5 extended argument with more than one rebuttal. So the scale is graded mainly by presence and number of rebuttals.
- Students rarely reach the rebuttal levels: one report gives 97.25% of students at levels 0–3, with rebuttal the hardest component — [search summary, Indonesian education studies](https://journal.unpas.ac.id/index.php/pendas/article/download/46350/27901). (Exact source of the 97.25% figure not pinned; verify.)
- Shirley Simon discusses limitations as well as advantages of TAP for analysing school science argument — [Simon 2008, UCL](https://discovery-pp.ucl.ac.uk/10000651/1/Simon2008Using277.pdf) (fetch blocked; content per search snippet).
- Felton & Kuhn (2001, *Discourse Processes* 32(2&3): 135–153) coded peer dialogues on capital punishment. Teens were "more preoccupied with producing the dialogue and less able to behave strategically" than young adults — [Benjamins record](https://benjamins.com/online/ebop/publications/14745); [full text, not fetched (503)](https://www.educationforthinking.org/sites/default/files/pdf/07-04DevelopmentOfArgumentiveDiscourseSkill.pdf).
- Felton (2004) reports that adults and adolescents differed on nine discourse strategies from that coding system — [Felton 2004 via Scribd](https://www.scribd.com/document/723015477/felton2004). Commonly cited: adults used more counter-critiques (attacking the partner's argument) and fewer mere expositions [UNVERIFIED].
- Nussbaum & Schraw (2007): good argumentation weighs and combines arguments and counterarguments into a final conclusion. Three integration strategies: refutation, weighing, design claim (synthesis) — [UNLV thesis citing Nussbaum](https://digitalscholarship.unlv.edu/thesesdissertations/943); [core.ac.uk](https://core.ac.uk/works/10099987).
- Weighing = one side's reasons are stronger. Design claim = concede the counterargument, then propose a solution that mitigates it. Nussbaum (2021) argues both are also refutational: they reduce a counterargument's force, not its truth — [Springer 2024, Eur J Psychol Educ](https://link.springer.com/article/10.1007/s10212-024-00890-x).
- Weighing took more mental effort than design claims, even controlling for argument complexity — [Springer 2024](https://link.springer.com/article/10.1007/s10212-024-00890-x).
- Nussbaum & Schraw's argumentation vee diagram (AVD) is a graphic organizer: arguments on one side, counterarguments on the other, integration at the bottom — [Springer 2024](https://link.springer.com/article/10.1007/s10212-024-00890-x); [Critical Integrative Argumentation, UNLV](https://digitalscholarship.unlv.edu/edpsych_fac_articles/279).
- Thagard's explanatory coherence (ECHO): propositions are network units; "explains" relations become excitatory links and "contradicts" relations inhibitory links; a hypothesis is accepted if it coheres better than competitors. Seven principles, of which explanation is the most important — [Thagard 1989, BBS](https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/abs/explanatory-coherence/E05CB61CD64C26138E794BC601CC9D7A); [PDF](https://Www.Gwern.net/doc/philosophy/epistemology/1989-thagard.pdf).
- Hahn & Oaksford (2007, *Psychological Review*): classic fallacies (argument from ignorance, circularity, slippery slope) vary in strength with content; people's strength judgments track Bayesian predictions — [Cardiff ORCA record](https://orca.cardiff.ac.uk/id/eprint/3308/); [Hahn & Oaksford, Normative Theory of Argument Strength](https://distantreader.org/stacks/journals/il/il-428.pdf).
- LLM vs human essays: Herbold et al. (2023, *Scientific Reports*) found ChatGPT argumentative essays rated higher than student essays by teachers; AI text used fewer discourse markers and more nominalizations — [paperswithcode](https://cs.paperswithcode.com/paper/ai-write-an-essay-for-me-a-large-scale); [DOAJ](https://doaj.org/article/e7968bb9653c429abb439c08c376647c).
- AROA preprint (Inoshita et al., arXiv 2602.01560): 1,375 human vs 1,000 AI essays; AI quality Q = 0.998 but claim rarity about one-fifth of human (0.037 vs 0.170); quality and claim rarity correlate r = −0.67; authors conclude LLMs "can reproduce argumentative structure but not semantic originality". No counterargument/rebuttal coding was described on the abstract page — [arXiv abs](https://arxiv.org/abs/2602.01560v2).
- Counterfire audit (arXiv 2402.08498): human-written counterarguments showed greater argumentative richness and diversity; humans still rated human counterarguments most persuasive — [arXiv](https://arxiv.org/abs/2402.08498v2).
- An AERA 2026 abstract: an LLM coder for critical-thinking tasks found consistently more arguments than human coders — [AERA 2026 program](https://convention2.allacademic.com/one/aera/aera26/online_program_direct_link/view_paper/2273636/). Conference abstract only.
- LLM reasoning-structure work (chain of thought, not argument text): Xiong et al. (arXiv 2505.13890) cluster CoT into steps, build directed reasoning graphs, and find exploration density, branching and convergence ratios correlate with accuracy; prompting reshapes the structure — [arXiv](https://arxiv.org/html/2505.13890v1).
- Li et al. (arXiv 2512.19135) use persistent homology on reasoning steps: more topological complexity in the full exploration graph goes with higher accuracy, but successful final paths are simpler, with fewer redundant cycles — [arXiv](https://arxiv.org/html/2512.19135).
- ROSCOE (Golovneva et al., ICLR 2023) scores step-by-step reasoning on semantic consistency, logicality, informativeness, fluency, factuality, using a taxonomy of reasoning errors — [arXiv 2212.07919](https://arxiv.org/abs/2212.07919). A 2025 survey proposes four top-level criteria: factuality, validity, coherence, utility — [arXiv 2502.12289](https://arxiv.org/html/2502.12289v3).

### Inferences
- Candidate sensitive features, derived from the frameworks, computed from roles/edges only:
  (a) presence of any Counterclaim/Alternative node (Kuhn, Wolfe & Britt myside);
  (b) whether each attack is itself attacked, i.e. a rebuttal chain (TAP L4/L5, Rationale);
  (c) integration type: refute vs weigh vs concede-and-mitigate (Nussbaum);
  (d) attack depth (number of rebuttals; TAP L5 needs more than one).
- Mercier & Sperber predict humans writing one-off answers (HC3 is Reddit/ELI5-style, Q&A) will be one-sided: they produce reasons for their view, and evaluate others' only in dialogue. HC3 human answers are monologic, so low counterargument rates are the expected human baseline.
- ChatGPT is trained to be balanced. It may show *more* counterarguments/concessions than humans, but they may be listed without rebuttal ("on the other hand…"). That is a Nussbaum "no integration" pattern. The schema needs a Concession role or a concede edge, else balanced-but-unintegrated LLM text and refuting human text get the same label.
- Thagard's explain/contradict is close to support/attack, but adds a distinction between *explaining* (cause→effect, hypothesis→observation) and *justifying* (reason→claim). wiki_csai answers are often explanatory, not argumentative. A schema with only Claim/Reason may force explanations into argument roles. Consider an Explanation/elaboration edge type, if GUIDE.md permits (the team must decide).
- Hahn & Oaksford argue strength is content-dependent. So a structure-only comparison cannot judge argument quality. Results should be framed as "structure differs", not "arguments are better/worse".
- The CoT-graph papers analyse model reasoning traces, not final answers. HC3 ChatGPT answers are not CoT traces. Their metrics (branching, convergence, cycles) are reusable graph metrics, but their findings do not transfer directly.
- AROA and Herbold suggest LLMs match human structure while differing in content. Structure-only comparison may therefore find small human–LLM differences. Pre-register this possible null.

### Gaps
- No study found that codes ChatGPT output with Kuhn or TAP schemes and compares it to human text at the level of counterargument/rebuttal frequency. This is the closest gap to the project's question.
- TAP level wording not verified from the primary table.
- Felton & Kuhn (2001) category names and adult-vs-teen counts not verified (full text unavailable).
- ROSCOE's exact step-error taxonomy not retrieved.

## Reported reliability of these coding schemes

### Takeaway
Reliability numbers for the education schemes could not be confirmed in this session.
The consistent qualitative message is that coders agree on claims and on whether a rebuttal exists, but struggle to separate data, warrant and backing in Toulmin coding.
Automated tagging of claims, counterclaims and rebuttals in learner essays reaches about F1 0.74.

### Cited Findings
- A study of 1,643 English-learner essays annotated for claims, counter-claims, rebuttals and related moves reported overall F1 = 0.743 for pre-trained language models — [EMNLP 2025 main 1755](https://aclanthology.org/anthology-files/pdf/emnlp/2025.emnlp-main.1755.pdf) (per search summary; check which paper/dataset the number belongs to).
- Erduran et al. (2004) moved to a rebuttal-based level scale partly because distinguishing data, warrants and backings in oral discourse was unreliable [UNVERIFIED — widely cited rationale; not confirmed from the paper this session].
- Simon (2008) discusses TAP limitations for analysing argument — [UCL PDF](https://discovery-pp.ucl.ac.uk/10000651/1/Simon2008Using277.pdf) (not fetched; 403).
- Argument mapping studies report learning gains, but no inter-rater reliability for novice-built maps was found — [ter Berg & van Gelder 2015](https://www.reasoninglab.com/wp-content/uploads/2013/10/TvG-Using-argument-mapping-to-improve-critical-thinking-skills-2015.pdf); evidence comes mostly from the Rationale community — [LessWrong summary](https://www.lesswrong.com/posts/NJ8k2RTwy3ELmwYZT/argument-maps-improve-critical-thinking).
- LLM coders find more arguments than human coders on a known-argument task — [AERA 2026 abstract](https://convention2.allacademic.com/one/aera/aera26/online_program_direct_link/view_paper/2273636/). This is a warning for the project: the extractor may over-label.

### Inferences
- Use coarse categories whose existence coders agree on (claim, support, attack, rebuttal-of-attack), not Toulmin's fine roles.
- The AERA finding (LLM coder over-produces arguments) matches the project's CLAUDE.md worry that the extractor reads LLM text differently. Report extractor precision, not only recall, against hand labels, separately for human and LLM texts.

### Gaps
- Inter-rater kappa for Kuhn (1991) interview coding, Felton & Kuhn (2001) dialogue coding, TAP levels, Wolfe & Britt essay coding, and Nussbaum integration coding: none retrieved. Primary texts needed.

## What these frameworks add to, or say against, a philosophy/linguistics-based schema

### Takeaway
They add a developmental, skill-graded view: the interesting signal is not the number of claims but whether the other side is considered and answered.
They argue against fine-grained Toulmin roles and against judging quality from structure alone.

### Cited Findings
- TAP grades quality by rebuttals, not by Toulmin component counts — [Bristol record](https://research-information.bris.ac.uk/en/publications/tapping-into-argumentation-developments-in-the-application-of-tou/); [secondary on Level 4](https://edisciplinas.usp.br/mod/resource/view.php?id=5385).
- Myside bias is a property of what is *left out*, measured as absence of other-side information — [Wolfe & Britt 2008](https://iphils.uj.edu.pl/~a.trybus/classes/logic/cs/16.Wolfe.Locus.Of.Myside.pdf).
- Integration (refute / weigh / design claim) is a separate skill beyond merely including counterarguments — [Springer 2024](https://link.springer.com/article/10.1007/s10212-024-00890-x).
- Argument strength is content-dependent (Bayesian) — [Hahn & Oaksford 2007](https://orca.cardiff.ac.uk/id/eprint/3308/).
- Explanatory coherence treats explain and contradict as the two basic relations — [Thagard 1989](https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/abs/explanatory-coherence/E05CB61CD64C26138E794BC601CC9D7A).

### Inferences
- Mapping to the user's draft (Argument, Claim, Reason, Refutation): Claim and Reason are well supported. "Refutation" bundles two things the literature separates: the counterargument (other side) and the rebuttal (answer to it). Split them, or derive rebuttal structurally as an attack on an attack. "Argument" is a unit (claim + reasons), not a sentence role; it is better as a derived subgraph than a node label.
- Candidate additions to propose to the team (not to put into GUIDE.md unilaterally): Counterclaim/Alternative role; Concession role or concede edge; possibly an explanation edge for wiki_csai. All are graph-level, role-only features.
- Graph-level metrics suggested by these frameworks: proportion of texts with ≥1 attack edge; proportion of attacks that are themselves attacked; max rebuttal depth (TAP L4 vs L5 analogue); share of concessions left unanswered.

### Gaps
- No direct evidence on whether HC3 human answers (Reddit/ELI5-style, monologic) contain enough counterarguments to make these features non-zero. Needs a pilot count on the hand-labelled set.
