# Split reasoning into roles, voices and relations

**Summary.**
Yes: philosophy, linguistics and cognitive science each offer well-studied schemas of reasoning.
They agree on a small core.
There is a main claim, reasons that support it, opposing views, and attacks on claims or on reasons.
The most natural and easiest system for step 3 is the Peldszus–Stede "microtext" scheme, which comes from Freeman's argument theory.
It is the only scheme built for short texts that reached high agreement among trained annotators (κ = .83 on the full label set).
Its best design idea is that it splits one question into small, separate ones.
It asks what role a sentence plays, whose view it states, and what it does to the sentence it links to.
We suggest wrapping it in two ideas from linguistics.
First, a coarse **polarity** level (positive, negative, neutral) on top of the edge types, taken from the Cognitive approach to Coherence Relations (CCR), where polarity was the most reliable judgement even for untrained people (κ = .73).
Second, a PDTB-style dotted hierarchy (`attacks.rebut`), so subtypes can be added or merged without breaking old results.
The proposed starter schema has three node roles (`main_claim`, `unit`, `filler`), a node `voice` (`author` or `opposing`), and four edge types (`supports`, `elaborates`, `attacks`, `none`) grouped by polarity, each with optional subtypes and an `other` slot.
The user's four types map only partly.
Claim and Reason fit well.
Argument is a structure, not a sentence role.
Refutation mixes two things that every framework keeps apart: the opposing view and the answer to it.
The category most likely to show a human-vs-LLM difference is exactly that pair: whether a text raises the other side, and whether it then answers it.
All schema choices below are suggestions for the team to decide in `GUIDE.md`, which does not exist yet.

## Three fields agree on a small core, and only one scheme was built for short texts

Each field asks a different question.
Philosophy and logic ask what makes a conclusion follow.
Linguistics asks how sentences hang together.
Cognitive science and education ask which moves people make, and which ones skilled reasoners add.
The table compares the main frameworks as annotation schemes for our use: Claude labels sentence nodes and edges in HC3 answers of 5–20 sentences.

| Field | Framework | Units and relations | Measured agreement | Fit for our step 3 |
|---|---|---|---|---|
| Philosophy | Toulmin, as modified by Habernal & Gurevych | claim, premise, backing, rebuttal, refutation (warrant and qualifier dropped) | α_U: claim .54, premise .62, backing .31, rebuttal .08, refutation .17; joint .60 on comments and forums, .09 on articles and blogs ([ar5iv 1601.02403](https://ar5iv.labs.arxiv.org/html/1601.02403)) | Poor beyond claim and premise |
| Philosophy | Freeman / Peldszus–Stede microtexts | central claim; proponent vs opponent; support, rebut, undercut; linked support | Naive students κ .38 full, .52 role, .58 support vs attack; 3 experts κ .83 full, .95 support vs attack, perfect on role ([Peldszus 2014](https://2014.aclweb.org/W14-21/pdf/W14-2112.pdf)) | Best fit |
| Philosophy | Stab & Gurevych essays | major claim, claim, premise; support, attack | α_U major claim .810, claim .524, premise .824 ([arXiv 1604.07370](https://arxiv.org/pdf/1604.07370)) | Middle "claim" role is weak |
| Philosophy | Walton argument schemes | 60–96 patterns of inference, with critical questions | Trained κ .723 ([Visser et al. 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7888437/)); minimally trained Fleiss κ 0.1, 0.307 after training; 0.364–0.848 on 3 collapsed schemes (as cited there) | Too fine; an edge property at most |
| Logic | Dung, ASPIC+, Pollock | arguments and attacks; rebut, undercut, undermine | Not an annotation scheme ([SEP: Defeasible Reasoning](https://plato.stanford.edu/entries/reasoning-defeasible/)) | Gives clean attack definitions |
| Logic | Argument Interchange Format (AIF) | information nodes; inference, conflict and preference nodes | Storage format, no agreement figure ([AIF Spec](https://arg-tech.org/wp-content/uploads/2011/09/aif-spec.pdf)) | Model for how to extend |
| Philosophy | Pragma-dialectics; IBIS | standpoints and structure types; issue, position, pro/con (unverified) | None found | Not tested on text |
| Linguistics | PDTB discourse senses | 3-level hierarchy, 36 senses | 94% class, 84% type, 80% subtype ([Prasad et al. 2008](https://aclanthology.org/L08-1093.pdf)); implicit relations expert κ .47–.58 (as cited in [Yung et al. 2024](https://arxiv.org/pdf/2402.04918)) | Model for the hierarchy |
| Linguistics | CCR primitives | polarity, basic operation, order, source of coherence | 40 untrained annotators κ: polarity .73, order .47, operation .42, source .31 ([Scholman et al. 2016](https://aclanthology.org/2016.dnd-7.7.pdf)) | Model for the coarse level |
| Linguistics | RST; DISRPT unified 17 labels | nucleus/satellite trees; cross-framework label set | "Significant levels of annotator disagreement" (snippet) ([Ignatev et al. 2025](https://aclanthology.org/2025.scil-1.2.pdf)); RST-DT κ ≈ 0.6 (unverified) | Discourse layer, not argument |
| Cognitive science | Kuhn's skills of argument | theory, evidence, alternative theory, counterargument, rebuttal | No κ retrieved ([Cambridge](https://www.cambridge.org/core/books/skills-of-argument/rebuttals/572661C088DA05E759FE09B8D8A8D7F4)) | Points to the key signal |
| Education | TAP levels (Erduran, Simon & Osborne) | quality levels graded mainly by rebuttals | No κ retrieved ([Bristol record](https://research-information.bris.ac.uk/en/publications/tapping-into-argumentation-developments-in-the-application-of-tou/)) | Graph-level metric idea |
| Education | Nussbaum integration | refute, weigh, design claim | No κ retrieved ([Springer 2024](https://link.springer.com/article/10.1007/s10212-024-00890-x)) | Later subtype candidates |
| Cognitive science | Argument mapping (Rationale) | claim, reason, objection, rebuttal (unverified vocabulary) | No inter-rater figure; learning gains of about 0.8–0.89 SD ([ter Berg & van Gelder 2015](https://www.reasoninglab.com/wp-content/uploads/2013/10/TvG-Using-argument-mapping-to-improve-critical-thinking-skills-2015.pdf)) | Shows the core is teachable |
| Cognitive science | Thagard's explanatory coherence | explains, contradicts | Computational model ([Thagard 1989](https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/abs/explanatory-coherence/E05CB61CD64C26138E794BC601CC9D7A)) | Supports an "explains" edge |

The core shows up in every row that has nodes and edges.
A main thesis is called claim, central claim, standpoint or position.
A reason is called data, premise or argument.
An opposing consideration is called rebuttal, opponent unit or con.
Philosophy adds one more useful split: an attack can hit a claim (**rebut**) or the link between a reason and a claim (**undercut**) ([SEP: Defeasible Reasoning](https://plato.stanford.edu/entries/reasoning-defeasible/)).
Cognitive science confirms this core is natural.
Almost everyone makes claims and gives reasons without being taught.
Counterarguments and rebuttals are rare, and education research has to teach them explicitly.
In one secondary report of Kuhn's sample, only 22 of 160 people built refutations ([Informal Logic paper citing Kuhn](https://law-journals-books.vlex.com/vid/rebuttals-refutations-argumentative-69270782)); this was not checked against the book.

The low-agreement items also share a pattern.
They are implicit (Toulmin's warrant), adverbial and inside a sentence (the qualifier), or a fine split of the same surface (rebuttal vs refutation, linked vs convergent, scheme types).
Habernal & Gurevych dropped the warrant because "data are appealed to explicitly, warrants implicitly", and dropped the qualifier because authors rarely state it ([ar5iv 1601.02403](https://ar5iv.labs.arxiv.org/html/1601.02403)).
Neither can be a one-sentence node, so neither belongs in our schema.

Two warnings come from the numbers.
First, training matters a lot.
On the same 23 microtexts, κ rose from .38 for untrained students to .83 for experts ([Peldszus 2014](https://2014.aclweb.org/W14-21/pdf/W14-2112.pdf)).
Our hand labellers need a short practice round.
Second, genre matters.
Joint agreement for modified Toulmin was .60 on comments and forum posts but .09 on articles and blogs ([ar5iv 1601.02403](https://ar5iv.labs.arxiv.org/html/1601.02403)).
HC3 answers are mostly explanatory, not argumentative, so we should expect agreement near the low end.
No study was found that annotates HC3-like question-answer text with any of these schemes.

## Linguistics shows how to make the schema coarse first and fine later

Linguistics adds the tools for change, not new argument roles.
PDTB arranges its senses in a tree and reports agreement at each level: 94% at class, 84% at type, 80% at subtype ([Prasad et al. 2008](https://aclanthology.org/L08-1093.pdf)).
One annotation gives both a coarse and a fine result.
CCR goes another way.
It describes each relation by a few separate yes/no-style features.
The **polarity** feature (does B go along with A, or against it?) was the most reliable, κ .73 among untrained annotators and .86 against the expert gold ([Scholman et al. 2016](https://aclanthology.org/2016.dnd-7.7.pdf)).
The **source of coherence** feature was the least reliable, κ .31.
That feature is exactly the split between "B explains why A happens" and "B gives a reason to believe A".
In our draft that is `explains` vs `supports`.
So the team's hardest decision is predictable, and it needs a written rule.
The same study found that substitution tests help: "Could you insert *because* here? *for example*? *in other words*? *but*?" ([Scholman et al. 2016](https://aclanthology.org/2016.dnd-7.7.pdf)).

Discourse structure and argument structure overlap only partly.
On the 112 microtexts, RST trees and argument graphs share 60% of their unlabelled edges.
The RST core matches the central claim in 85% of texts.
But 72% of rebuts have no RST counterpart ([Peldszus & Stede 2016](https://aclanthology.org/W16-2812.pdf)).
So discourse labels like `explains` and `restates` are useful, but they cannot replace an argument layer.
Attacks especially need explicit guidance in the prompt.
The same study found that claims restated later in a text caused central-claim disagreement in 4 texts.
HC3 ChatGPT answers often end with a summary, so we need a rule: the main claim is the first full statement of the thesis, and a later paraphrase is `restates`.

LLMs also do better at coarse levels.
GPT-4 on implicit PDTB-3 relations reached 50.03% accuracy at the 4-way top level but 36.84% at the 14-way second level ([Yung et al. 2024](https://arxiv.org/pdf/2402.04918)).
ChatGPT on explicit relations, with in-context examples, reached 85.97% top-level accuracy ([Chan et al. 2023](https://arxiv.org/pdf/2304.14827)).
Asking for the top level and the second level together helped ([Chan et al. 2023](https://arxiv.org/pdf/2304.14827)).
These are newswire numbers for older OpenAI models.
No published number exists for current Claude models, so the team must measure it.

## Claim and Reason fit, Argument is a structure, and Refutation hides two moves

The user's four types are a good start, and two of them map cleanly.

**Claim** maps to the central claim, standpoint or position in every framework.
It should be a node role.
One caution: keep one main claim and avoid a middle "sub-claim" role.
In the Stab & Gurevych essays, the middle claim role had the weakest agreement (α_U .524) ([arXiv 1604.07370](https://arxiv.org/pdf/1604.07370)).

**Reason** maps to premise or data.
But a reason is defined by what it does to another sentence.
So it is best stored as a `supports` edge, not as a node role.
A sentence can support one claim and be supported by another.

**Argument** is not a sentence role in any framework checked.
In Dung's theory it is a whole unit with its inside hidden ([SEP](https://plato.stanford.edu/entries/reasoning-defeasible/)).
In AIF it is a small subgraph: premises, an inference node and a conclusion ([AIF Spec](https://arg-tech.org/wp-content/uploads/2011/09/aif-spec.pdf)).
For us, an argument is a claim node plus its incoming `supports` edges.
We should compute it from the graph, not ask Claude to label it.

**Refutation** is the most conflated type.
It bundles two things.
One is the opposing view the author mentions ("Some say index funds are boring").
The other is the author's answer to it ("But boring is the point").
Habernal & Gurevych split these into rebuttal and refutation, and agreement on both was very low (α_U .08 and .17 overall) ([ar5iv 1601.02403](https://ar5iv.labs.arxiv.org/html/1601.02403)).
Peldszus & Stede solve this by using two separate labels.
The node gets a role: proponent or opponent.
The edge gets a function: support, rebut or undercut ([Peldszus 2014](https://2014.aclweb.org/W14-21/pdf/W14-2112.pdf)).
Experts agreed perfectly on proponent vs opponent.
Under this split, a refutation is not a new label.
It is a pattern: an author sentence that attacks an opposing sentence.
Refutation also hides the rebut vs undercut split, which is useful but can wait as a subtype.

Three things are missing from the four types.
First, a role for **non-argumentative sentences**: greetings, sign-offs and refusals.
They are common in HC3.
Second, a way to mark **explanation and elaboration**.
wiki_csai prompts are all "Please explain what is X", so most links there are not reasons at all.
Thagard's model also treats "explains" as its own basic relation ([Thagard 1989](https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/abs/explanatory-coherence/E05CB61CD64C26138E794BC601CC9D7A)).
Third, the **whose-view** dimension, which is what makes "mentions the other side" separate from "answers it".

## A starter schema with a coarse core and optional subtypes

This is a proposal for the team.
It is not decided, and it must not go into `GUIDE.md` without team agreement.

The idea is three levels for edges.
Level 0 is polarity: positive, negative or neutral.
Level 1 is the edge type: `supports`, `elaborates`, `attacks` or `none`.
Level 2 is an optional subtype, written after a dot, such as `attacks.rebut`.
Headline comparisons use node roles, voice and level-1 edge types.
Level 2 is exploratory.
Level 0 is the fallback if level-1 agreement is too low.
Each node gets one outgoing edge to one parent sentence, so the graph is a tree rooted at the main claim, as the earlier report suggested.

```yaml
# schema/schema_v0.1.yaml  (proposal for the team, not decided)
version: 0.1.0
node:
  role:                 # exactly one per sentence
    main_claim: "The answer's central thesis. Exactly one per text."
    unit:       "Any other content sentence."
    filler:     "Greeting, sign-off, 'Hope this helps', refusal."
    other:      "Nothing fits. Add a short note."
  voice:                # whose view the sentence states
    author:     "The writer's own view or information."
    opposing:   "A view the writer reports in order to weigh or reject it."
edge:                   # child -> parent; main_claim has no parent
  positive:
    supports:   {subtypes: [reason, evidence, other]}
    elaborates: {subtypes: [explains, example, restates, other]}
  negative:
    attacks:    {subtypes: [rebut, undercut, other]}
  neutral:
    none:       {subtypes: []}
maps_from:
  readme_draft:         # the relation list in README.md
    supports: supports
    attacks:  attacks
    explains: elaborates.explains
    example:  elaborates.example
    restates: elaborates.restates
    none:     none
```

Some choices need a short reason.
`supports` means "B gives a reason to believe A".
`elaborates` means "B adds detail to A, without arguing for it".
This is the source-of-coherence split, the least reliable judgement in CCR, so it needs a substitution test in the guide: if "because" fits, use `supports`; if "for example", "that is" or "in other words" fits, use `elaborates`.
`example` sits under `elaborates` because in HC3 most examples illustrate rather than prove.
The microtexts treat example as a kind of support, but it was only 1.8% of their relations ([DFKI-SLT/argmicro](https://huggingface.co/datasets/DFKI-SLT/argmicro/blob/refs%2Fpr%2F1/README.md)).
An example given as proof of a disputed claim would be `supports.evidence`.
The team may prefer the other placement; the mapping table keeps both readable.
Linked vs convergent support is left out.
It needs several parents per node, and no agreement figure was found for it.

With `voice` and `attacks`, the user's types become derived patterns.
An opposing view is a node with `voice: opposing`.
A refutation is an `author` node that `attacks` an `opposing` node.
An unanswered concession is an `opposing` node that no author node attacks.

**Where this agrees with and departs from the earlier report.**
It agrees on the microtext style, one main claim, the `filler` role, a tree, and merging rebut and undercut at the level used for headline results.
It departs in four ways.
It groups `explains`, `example` and `restates` under one `elaborates` type, which shrinks the headline label set from six to four.
It keeps rebut and undercut as optional subtypes instead of discarding the split.
It adds a polarity level as a fallback.
And it adds the `voice` attribute, which the earlier report did not have.
The README's six labels can still be recovered from level 2, so nothing from the earlier plan is lost.

## Evolve the schema by versioning one data file and projecting old labels

The schema will change, so make change cheap.
Keep one YAML file as the single source.
A short Python script turns it into the Pydantic model, the label block of the prompt, the validator's allowed values, and the hand-labelling template.
Then the guide, prompt and validator cannot drift apart.
AIF was built on the same idea: keep the core "as basic as possible" and add new types below it, because the core "will change over time" ([AIF Spec](https://arg-tech.org/wp-content/uploads/2011/09/aif-spec.pdf)).

Version the file in three steps.
A PATCH changes wording or examples only.
A MINOR change adds, merges or tightens a subtype; old data stays valid at levels 0 and 1.
A MAJOR change alters the roles, voices or level-1 edge types; old results are then no longer comparable and must be kept apart.
Stamp `schema_version` and `prompt_version` into every graph file and every hand-label file.
Save each new prompt as a new file in `prompts/`, as CLAUDE.md requires, and re-run the hand check after each change.

Keep a mapping table for each change, for example `mappings/v0.1_to_v0.2.csv` with columns `old, new, lossless`.
Merges are lossless: old labels are projected onto new ones with no human work.
Splits are not lossless: only the edges with the split label need relabelling, not whole texts.
Because every subtype has one parent, every old edge always has a defined level-1 and level-0 label.

The `other` slot is how the team discovers missing types.
Each level allows `other` plus a short note.
Count `other` per version and per side.
If one recurring note passes a threshold (the tooling notes suggest about 5% of edges), propose a new subtype to the team.
Never promote it to a level-1 type without a team decision, since that would be a MAJOR change.
Do not drop texts with many `other` labels; report the count.

Later subtypes already have a source in the literature.
Nussbaum's three ways to handle an opposing view (refute, weigh, design a fix) could become subtypes of an author-to-opposing attack ([Springer 2024](https://link.springer.com/article/10.1007/s10212-024-00890-x)).
A coarse 3-way Walton scheme on `supports` edges (policy, causal, sample) is the only tractable form of scheme labels ([Visser et al. 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7888437/)).
Both are optional and later.

## Extract with structured outputs, a strict validator and a blind gold set

**Claude structured outputs.**
Structured outputs are now stable.
The JSON schema goes in `output_config.format`, and the Python SDK's `client.messages.parse()` accepts a Pydantic model ([Claude docs: Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)).
The feature has limits that shape the design.
It does not allow recursive schemas, numeric minimum or maximum, or length limits.
Enums must be plain values, and their letter case is not guaranteed, so compare case-insensitively.
Asking for step-by-step reasoning inside a field can trigger a refusal, so ask for a short rationale instead.
So keep the output flat: one object per sentence, such as `{"i": 3, "role": "unit", "voice": "author", "parent": 1, "edge": "supports", "subtype": "reason", "note": "", "rationale": "..."}`.
Ask for polarity, edge type and subtype together, coarse first.
Send pre-split, numbered sentences, and do not let Claude re-segment.
Put one fully labelled human answer and one ChatGPT answer in the prompt as few-shot examples, as the earlier report advised.

**The validator.**
Python checks what the schema cannot.
Every sentence has exactly one node, with indices 1 to n.
Every value is in the allowed list.
Every parent points to a real sentence, and no node points to itself.
There is exactly one main claim, and the graph is a tree.
Each subtype belongs to its stated edge type.
Count every failure per side (human vs LLM) and per version, and keep failed graphs in the denominators.
An unequal failure rate between sides is itself a finding.

**Runs and cost.**
Run the extractor 3 times per text and report run-to-run agreement per side.
Batch API prices are $1 in and $5 out per million tokens for Sonnet 5.5, and $2 and $10 for Opus 5.5 ([Claude docs: Pricing](https://platform.claude.com/docs/en/about-claude/pricing)).
A script in the tooling notes estimated about $28 (Sonnet) or $55 (Opus) for 800 texts × 3 runs, under assumed token counts.
Cost is not the constraint, so choose the model by accuracy on the gold set.

**A gold set made blind to LLM output.**
The hand labels in `annotations/` judge the extractor, so they must not be made by correcting Claude's graphs.
People who review AI suggestions tend to accept them.
In one study of 2,784 participants, errors that needed knowledge of the labelling rules were caught only 31% of the time ([Bias in the Loop, arXiv 2509.08514](https://arxiv.org/html/2509.08514v1)).
Argument labels are exactly that kind of rule-based judgement.
So two people label the README's 10 texts (5 human, 5 LLM, source hidden) without seeing any extractor output.
Aim for κ ≥ 0.6 on level-1 edge types before calling the labels gold, as the earlier report suggested.
Report agreement at each level (role, voice, level 0, level 1, level 2), separately for human and LLM texts, and next to the human-human agreement.
Report precision as well as recall.
A 2026 conference abstract found that an LLM coder found more arguments than human coders did ([AERA 2026](https://convention2.allacademic.com/one/aera/aera26/online_program_direct_link/view_paper/2273636/)), so Claude may over-label.

## Raising the other side and answering it is the likeliest difference

Cognitive science gives a clear lead on where to look.
Across Kuhn, TAP, Wolfe & Britt and Nussbaum, the marker of skilled reasoning is the same.
Skilled reasoners consider the other side and then answer it.
TAP grades argument quality mainly by rebuttals ([secondary teaching document](https://edisciplinas.usp.br/mod/resource/view.php?id=5385)).
Myside bias is defined by what is left out: other-side information missing from an essay ([Wolfe & Britt 2008](https://iphils.uj.edu.pl/~a.trybus/classes/logic/cs/16.Wolfe.Locus.Of.Myside.pdf)).
Nussbaum treats integrating the counterargument as a separate skill beyond just mentioning it ([Springer 2024](https://link.springer.com/article/10.1007/s10212-024-00890-x)).

These ideas become graph measures that use only roles, voice and edge types.
The first is the share of texts with at least one `opposing` node.
The second is the share of `opposing` nodes that an author node attacks (counterargument plus rebuttal integration).
The third is the share left unanswered.
The fourth is rebuttal depth: whether an attack is itself attacked, and how many times (TAP level 4 vs level 5, unverified level wording).
Other candidates come from prior work on LLM style, covered in the earlier report: a trailing `elaborates.restates` node pointing back to the main claim, an early main claim, and a higher share of `elaborates`.

The direction of the voice effect is open.
The argumentative theory of Mercier & Sperber predicts that people writing one-off answers will be one-sided ([Dogramaci 2020](https://philarchive.org/rec/DOGWIT)).
HC3 human answers are mostly monologues, so few opposing nodes is the expected human baseline.
ChatGPT is tuned to be balanced, so it may raise the other side more often, but perhaps in a formulaic "However, …" without answering it.
That is a guess, not a measurement.
The `voice` attribute is what lets the schema tell these cases apart.
Without it, a balanced-but-unanswered LLM text and a refuting human text would get the same labels.

Three risks qualify any result.
First, the extractor may read ChatGPT's explicit connectives more easily than implicit links in forum posts, so hand-label accuracy must be reported per side.
Second, finance human answers sometimes reply to other answers; an `opposing` node there has no ChatGPT counterpart.
Third, the difference may be small.
One preprint found AI essays matched human structure while their claims were about one-fifth as rare (0.037 vs 0.170) ([arXiv 2602.01560](https://arxiv.org/abs/2602.01560v2)).
The team should write the possible null result into `JOURNAL.md` before running.
And attacks will be rare: even in the argumentative microtexts, rebut and undercut together were only 34.4% of relations ([DFKI-SLT/argmicro](https://huggingface.co/datasets/DFKI-SLT/argmicro/blob/refs%2Fpr%2F1/README.md)), and HC3 is mostly explanatory.
A pilot count on the hand-labelled texts should check whether opposing nodes occur often enough to measure.

## Conclusion

The literature does not offer one schema to copy.
It offers a design principle.
The reliable parts of reasoning are few and coarse, and each hard label becomes easier when it is split into small, separate questions: role, voice, polarity, then type.
That principle also solves the evolution problem.
A schema built from separate dimensions and a label tree can grow without breaking earlier comparisons, because every new label has a defined coarse parent.

For this project, the most interesting change is in what "Refutation" means.
It is not a box to fill in.
It is a pattern in the graph: an opposing voice, followed by the author's answer.
That pattern is the skill education research cares most about, and no study was found that measures it in ChatGPT versus human answers.
If the team adds only one thing beyond the README's draft, it should be the `voice` attribute, since it turns the most debated question about LLM "balance" into something the graph can count.
