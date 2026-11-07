# Philosophical and logical frameworks for argument structure, judged as an annotation/extraction schema

Scope: frameworks from philosophy, informal logic and formal argumentation that define units and relations of reasoning.
Judged for one use: Claude labels sentence-nodes and edges in short HC3 answers (~5–20 sentences), checked against hand labels, compared by node roles and edge types only.
Earlier report already recommends a Peldszus–Stede microtext-style scheme; this file does not redo that, it gives the theory behind it and the alternatives.

Verification legend:
items with a [Source](URL) were read in this session (page or PDF text).
Items marked **(UNVERIFIED — background knowledge)** were not checked against a source in this session; treat them as leads.

## Q1. What does each framework define, and how well does it fit short everyday texts, non-expert annotators and LLMs?

### Takeaway
Only three frameworks have been used as text-annotation schemes with measured agreement: modified Toulmin (Habernal & Gurevych), Freeman-based microtext (Peldszus & Stede), and Walton schemes (Visser et al.).
Of these, the Freeman/Peldszus–Stede scheme gets the highest agreement on short texts once annotators are trained (κ=.83 full label set), while modified Toulmin on web text is low for all but claim/premise, and Walton schemes need trained experts.

### Cited Findings

**Toulmin model (claim, data/grounds, warrant, backing, qualifier, rebuttal)**
- Habernal & Gurevych (Computational Linguistics 43(1), 2017) annotated 340 web documents (84,673 tokens; 216 comments, 73 forum posts, 46 blog posts, 5 articles) with a "modified Toulmin's model": claim, premise, backing, rebuttal, refutation; only the claim is mandatory and it may be implicit — [arXiv 1601.02403 via ar5iv](https://ar5iv.labs.arxiv.org/html/1601.02403)
- They dropped the **warrant** because warrants are almost never explicit; they quote Toulmin: "data are appealed to explicitly, warrants implicitly", and note the warrant/grounds distinction only works cleanly in Toulmin's own examples — [ar5iv 1601.02403, §4.4.2](https://ar5iv.labs.arxiv.org/html/1601.02403)
- They dropped the **qualifier** because "authors do not state the degree of cogency" in the data — [ar5iv 1601.02403, §4.4.2](https://ar5iv.labs.arxiv.org/html/1601.02403)
- Their "refutation" is an extra element added to Toulmin: a counter-attack on the rebuttal (author attacks the opposing view) — [ar5iv 1601.02403, §4.4.3](https://ar5iv.labs.arxiv.org/html/1601.02403) (the exact definition wording was summarised by the fetch tool; check §4.4.3 before quoting).

**Freeman's macrostructure (linked vs convergent; proponent/opponent dialectic; rebuttals and counter-rebuttals)**
- Peldszus & Stede's scheme is based on Freeman's theory of argument macrostructure, modelling argument as an exchange between a proponent and an opponent; it separates linked support (several units jointly justify) from basic support, and rebutting from undercutting attacks (undercut targets the premise–claim link, not the claim) — [Peldszus & Stede, CORE PDF (search snippet)](https://core.ac.uk/download/196238773.pdf)
- Peldszus states the theory "aims to integrate the ideas of Toulmin (1958) into the argument diagraming techniques of the informal logic tradition (Beardsley, 1950; Thomas, 1974) in a systematic and compositional way" — [Peldszus 2014, ArgMining W14-2112](https://2014.aclweb.org/W14-21/pdf/W14-2112.pdf)
- Microtexts: 112 short German texts (later professionally translated to English), each about five argumentative units — [Stab & Gurevych 2016, arXiv 1604.07370 (search snippet)](https://arxiv.org/pdf/1604.07370); [argmicro dataset card](https://huggingface.co/datasets/DFKI-SLT/argmicro)
- The full-corpus structure markup was done by one expert annotator; agreement comes from separate studies (dataset card; not checked against the primary paper) — [argmicro dataset card (search snippet)](https://huggingface.co/datasets/DFKI-SLT/argmicro/blob/refs%2Fpr%2F1/README.md)

**Informal-logic diagramming (Beardsley, Thomas)**
- SEP "Informal Logic" describes diagrams that show convergent premises ("three independent 'convergent' premises that provide three separate reasons") and linked premises that support the conclusion "(only) when combined"; it notes diagramming dates back to Whately 1826 and Wigmore 1913 and names tools Rationale, Araucaria, Argunet — [SEP: Informal Logic](https://plato.stanford.edu/entries/logic-informal/)
- The SEP entry does not discuss how to tell linked from convergent in practice — [SEP: Informal Logic](https://plato.stanford.edu/entries/logic-informal/)
- Beardsley (1950) introduced serial, convergent and divergent structures; Thomas (1974) added linked. **(UNVERIFIED — background knowledge)**

**Walton argumentation schemes + critical questions**
- Schemes are "recurring patterns of reasoning"; Walton, Reed & Macagno (2008) give "a compendium of 96 schemes"; schemes are paired with "critical questions" (e.g. Argument from Authority) — [SEP: Informal Logic](https://plato.stanford.edu/entries/logic-informal/)
- Visser et al. (2020, *Argumentation*) annotated all 505 inferences in a US 2016 TV debate with Walton's 60 schemes using a dichotomous Argument Scheme Key (ASK); 491/505 got a scheme, 14 "default inference"; most frequent: argument from example (81), cause to effect (48), practical reasoning (45) — [Visser et al. 2020, PMC7888437](https://pmc.ncbi.nlm.nih.gov/articles/PMC7888437/)
- Annotators confused practical reasoning vs argument from values; some relations were unclassifiable because the underlying structure was not built with schemes in mind — [Visser et al. 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7888437/)
- Hansen & Walton (2013): six coders, 256 arguments, 14 schemes + "none of the above"; difficulty traced to the "open texture" of scheme key terms (no κ given in Visser's summary) — [Visser et al. 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7888437/)
- Wagemans' Periodic Table of Arguments (PTA) is an alternative scheme typology, decomposed into three sub-decisions (fact/value/policy; first/second order; predicate/subject) aggregated into 36 types — [Visser et al. 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7888437/)

**Dung abstract argumentation; bipolar; ASPIC+**
- Dung defines "an argument structure as an ordered pair": a set of arguments and a binary "attacks" relation; Dung's framework does not distinguish kinds of attack; extensions (admissible, preferred, stable, grounded) are defined on it — [SEP: Defeasible Reasoning §4.4](https://plato.stanford.edu/entries/reasoning-defeasible/)
- ASPIC+ (Prakken) uses three attack forms: rebutting (conclusions contradict), undermining (conclusion contradicts a premise), undercutting (doubts the premises→conclusion inference) — [SEP: Defeasible Reasoning §4.4](https://plato.stanford.edu/entries/reasoning-defeasible/)
- Bipolar argumentation frameworks (Cayrol & Lagasquie-Schiex, ~2005) add a support relation next to attack. **(UNVERIFIED — background knowledge)**

**Pollock's defeaters**
- Rebutting defeaters "give one a prima facie reason for believing the denial of the original conclusion"; undercutting defeaters "give one a reason for doubting that the usual relationship between the premises and the conclusion hold in the given case" — [SEP: Defeasible Reasoning §1.1](https://plato.stanford.edu/entries/reasoning-defeasible/)

**Pragma-dialectics (van Eemeren & Grootendorst)**
- Fallacies are "violations of the pragma-dialectical rules that govern critical discussions"; it includes an account of indirect speech acts for reconstructing arguments — [SEP: Informal Logic](https://plato.stanford.edu/entries/logic-informal/)
- Its model has four discussion stages (confrontation, opening, argumentation, concluding), standpoints, and argument structures single / multiple / coordinative / subordinative. **(UNVERIFIED — background knowledge)** Multiple ≈ convergent, coordinative ≈ linked, subordinative ≈ serial.
- Walton & Krabbe dialogue typology (seven types, e.g. persuasion, inquiry, eristic) is related dialogue-level theory — [SEP: Informal Logic](https://plato.stanford.edu/entries/logic-informal/)

**Argument Interchange Format (AIF)**
- AIF core ontology has two halves: the Upper Ontology (node and edge "syntax") and the Forms Ontology (schemes, premises, exceptions: the "semantics") — [AIF Specification, Dundee 2011](https://arg-tech.org/wp-content/uploads/2011/09/aif-spec.pdf)
- Nodes: information nodes (I-nodes) and scheme nodes (S-nodes): RA (inference), CA (conflict), PA (preference) — [AIF Spec](https://arg-tech.org/wp-content/uploads/2011/09/aif-spec.pdf)
- Graph rules: edges never go directly I-node→I-node ("there must be a scheme that expresses the rationale behind the relation"); an RA-node has ≥1 premise predecessor and exactly one conclusion successor; a CA-node has exactly one conflicting and one conflicted element; S-nodes may connect to S-nodes directly (so an attack can target an inference = undercut) — [AIF Spec, Def. 1.1](https://arg-tech.org/wp-content/uploads/2011/09/aif-spec.pdf)
- Inference schemes split into deductive and defeasible subsets; schemes can carry premises, conclusion, presumptions and exceptions (example: Argument from Expert Opinion) — [AIF Spec §1.3.1](https://arg-tech.org/wp-content/uploads/2011/09/aif-spec.pdf)
- MA-nodes (rephrase/default reformulation) and the dialogue extension AIF+ with L-nodes, TA/YA (illocutionary anchoring, used in Inference Anchoring Theory) are later additions; not in the 2011 spec text read here. **(UNVERIFIED — background knowledge)**

**IBIS (Kunz & Rittel, 1970)**
- Units: Issue (question), Position (answer), Argument (pro/con a position); relations such as responds-to, supports, objects-to. **(UNVERIFIED — background knowledge; no source fetched this session)** Designed for design deliberation, not for monologue answers.

### Inferences
- Fit for HC3 answers (one answer to a question, monologue, 5–20 sentences): the question itself is an IBIS-like Issue and the answer's main thesis a Position/central claim; within the answer, Freeman/microtext roles fit best because microtexts are the same genre size (~5 units, one central claim).
- Toulmin does not fit sentence-level annotation well: warrant and qualifier are mostly implicit or adverbial (inside a sentence), so they cannot be one-sentence nodes.
- Walton schemes are a *property of an inference* (edge label), not a node role; 60 classes on ~10 edges per text is too sparse for graph comparison and too hard for non-experts. A coarse 3-class version (Song et al.: policy/causal/sample) is the only tractable form.
- Dung/ASPIC+/Pollock give the clean semantics of attack types (rebut / undercut / undermine), but Dung's units are whole arguments, not sentences, so they are a target for evaluation, not an annotation scheme.
- AIF is a container format, not an annotation guideline; it tells you *how* to store any of the above.

### Gaps
- Exact Habernal & Gurevych definitions of "refutation" and "backing" were summarised by a tool, not read verbatim.
- No primary source read this session for IBIS, pragma-dialectical structure types, Beardsley/Thomas originals, bipolar AF, or AIF+ MA/YA nodes.
- No study found that annotates HC3-like Q&A answers with any of these schemes.

## Q2. Which concepts recur (a "core"), and which are hard to annotate reliably?

### Takeaway
A clear core recurs: a main thesis (claim/standpoint/position), supporting reasons (premise/data), an opposing consideration (rebuttal/opponent), and two attack types (against the claim vs against the inference).
Reliable: claim, premise, support vs attack, proponent vs opponent. Unreliable: warrant, backing, rebuttal/refutation in free web text, linked-vs-convergent, fine-grained scheme labels.

### Cited Findings
- Habernal & Gurevych α_U (all registers): claim 0.54, premise 0.62, backing 0.31, rebuttal 0.08, refutation 0.17, joint 0.48; on comments+forum posts: claim 0.59, premise 0.69, backing 0.48, rebuttal 0.37, refutation 0.08, joint 0.60; on articles+blogs joint only 0.09 — [ar5iv 1601.02403, Table 4](https://ar5iv.labs.arxiv.org/html/1601.02403)
- Joint α_U varies strongly by topic: 0.08 (mainstreaming) to 0.68 (prayer in schools) — [ar5iv 1601.02403, Table 4c](https://ar5iv.labs.arxiv.org/html/1601.02403)
- Their persuasive vs non-persuasive document label: Fleiss κ = 0.59, 3 annotators, 990 documents — [ar5iv 1601.02403, §4.3.1](https://ar5iv.labs.arxiv.org/html/1601.02403)
- Peldszus & Stede, 26 naive untrained students, 23 microtexts, one 90-min session: Fleiss κ=.52 proponent vs opponent, κ=.58 support vs attack, κ=.38 full label set — [Peldszus 2014, W14-2112](https://2014.aclweb.org/W14-21/pdf/W14-2112.pdf)
- Same 23 texts, 3 expert annotators: κ=.83 full label set, κ=.95 support vs attack, perfect agreement on proponent vs opponent — [Peldszus 2014, W14-2112](https://2014.aclweb.org/W14-21/pdf/W14-2112.pdf)
- Naive annotators clustered: subgroups performed much better than average — [Peldszus 2014, W14-2112](https://2014.aclweb.org/W14-21/pdf/W14-2112.pdf)
- Persuasive essays (Stab & Gurevych): claim αU .524 weakest, major claim .810, premise .824 (as cited in the earlier team report) — [arXiv 1604.07370](https://arxiv.org/pdf/1604.07370)
- Walton schemes: Visser et al. Cohen's κ=0.723 on ~10% sample with trained annotators (underlying structure κ 0.610, CASS 0.752); PTA aggregated κ=0.689 — [Visser et al. 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7888437/)
- Prior scheme studies: Musi et al. 2016 Fleiss κ 0.1 with minimally trained non-experts, 0.307 after training; Song et al. 2014 κ 0.364–0.848 on 3 collapsed schemes; Duschl 2007 only % agreement; Lindahl et al. low agreement — [Visser et al. 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7888437/)
- A W16-2810 essay study: re-annotating the 10 lowest-agreement essays with refined guidelines and trained annotators significantly improved agreement, suggesting scheme annotation needs highly trained annotators — [search snippet, W16-2810](https://preview.aclanthology.org/fix_video/W16-2810.pdf) (not read in full)

Core concept crosswalk (built from the sources above; equivalences marked ≈ are my mapping):

| Core concept | Toulmin | Freeman / microtext | Pragma-dialectics | IBIS | Dung / ASPIC+ / Pollock | AIF |
|---|---|---|---|---|---|---|
| Main thesis | claim | central claim (proponent) | standpoint | position | conclusion of argument | I-node (conclusion of RA) |
| Reason | data/grounds | premise, support | argument | argument (pro) | premise | I-node → RA → I-node |
| Inference licence | warrant (+ backing) | link (implicit) | (unexpressed premise) | — | defeasible rule | RA-node + scheme (Form) |
| Joint reasons | — | linked support | coordinative | — | multi-premise rule | RA with ≥2 premises |
| Independent reasons | — | convergent (separate supports) | multiple | several args | separate arguments | separate RA-nodes |
| Chain | — | serial | subordinative | — | sub-argument | RA → I → RA |
| Counter-consideration | rebuttal (exception) | opponent unit | (antagonist) | argument (con) | attacking argument | I-node → CA |
| Attack on claim | rebuttal | rebut | — | objects-to | rebut | CA → I-node |
| Attack on inference | (rebuttal, loosely) | undercut | — | — | undercut | CA → RA-node |
| Attack on premise | — | rebut of a premise | — | — | undermine | CA → premise I-node |
| Answer to attack | (Habernal: refutation) | counter-rebuttal (proponent attacks opponent unit) | — | — | reinstatement / defence | CA → CA chain |
| Strength / hedge | qualifier | — | — | — | preference | PA-node |

### Inferences
- Robust core for an LLM extractor on sentence nodes: {central claim, premise/support, opponent/counter-view, rebut, undercut} — this is exactly the Peldszus–Stede set and it is the one with the best measured agreement.
- Low agreement concentrates where a concept is implicit (warrant), adverbial (qualifier), or a fine distinction over the same surface (linked vs convergent, rebuttal vs refutation, scheme types).
- Agreement depends heavily on genre: texts that were written to argue (microtexts, essays, comments) score much higher than articles/blogs. HC3 finance/wiki_csai answers are often expository, so expect agreement nearer the low end; many sentences will be non-argumentative.
- The naive-vs-expert gap (κ .38 → .83) suggests the hand-label check in this project needs a short training round, and LLM agreement should be compared to a trained-annotator ceiling.

### Gaps
- No agreement figure found for linked vs convergent specifically (only full-label κ).
- No agreement study found for IBIS or pragma-dialectical structure-type annotation on text.
- Stab & Gurevych relation-level agreement was not re-checked this session.

## Q3. How do these map to the user's Argument / Claim / Reason / Refutation, and where does that set conflate things?

### Takeaway
"Claim" and "Reason" map cleanly to the core.
"Argument" is a structure (claim + its reasons + inference), not a sentence role, in every framework checked; "Refutation" mixes a node role (opposing view) with an edge type (attack) and also hides the rebut/undercut distinction.

### Cited Findings
- In Dung's framework the unit "argument" is a node whose internal structure is abstracted away, with only an attack relation between arguments — [SEP: Defeasible Reasoning §4.4](https://plato.stanford.edu/entries/reasoning-defeasible/)
- In AIF an argument is a subgraph: I-nodes linked via an RA-node; conflict is its own node type (CA) that can target an I-node or an S-node — [AIF Spec, Def. 1.1](https://arg-tech.org/wp-content/uploads/2011/09/aif-spec.pdf)
- Habernal & Gurevych separate rebuttal (opposing view the author mentions) from refutation (author's counter-attack on the rebuttal), and refutation had very low agreement (α_U 0.17 overall) — [ar5iv 1601.02403](https://ar5iv.labs.arxiv.org/html/1601.02403)
- Peldszus & Stede encode the same idea as two orthogonal dimensions: role (proponent/opponent) on the node, and function (support/rebut/undercut) on the edge — [Peldszus 2014](https://2014.aclweb.org/W14-21/pdf/W14-2112.pdf); [CORE snippet](https://core.ac.uk/download/196238773.pdf)
- Pollock/ASPIC+ distinguish attacks on the conclusion (rebut), on the inference (undercut) and on a premise (undermine) — [SEP: Defeasible Reasoning](https://plato.stanford.edu/entries/reasoning-defeasible/)

### Inferences
- Mapping: Claim → central claim / standpoint (node role); Reason → premise (node role) + support (edge type); Argument → derived structure (a claim node plus its incoming support edges), so compute it, do not label it; Refutation → split into node role `opponent` (sentence states a view the author opposes) and edge types `rebut` / `undercut` (what is attacked); the author's answer to that view is an attack edge from a proponent node to an opponent node (Freeman's counter-rebuttal), not a new node type.
- Missing from the user's set relative to the core: the attack target (claim vs inference), linked vs convergent support, and a "non-argumentative / background" role, which will be common in expository HC3 answers.
- The project rule "compare by node roles and edge types only" favours the Peldszus–Stede split: role and edge are separate labels, so each can be compared and agreement-checked separately.

### Gaps
- No source compares "argument as unit" vs "argument as structure" annotation agreement directly.

## Q4. Which frameworks are designed for extension or coarsening?

### Takeaway
AIF is explicitly built for extension: a minimal fixed upper ontology plus an open Forms ontology where new schemes are added as subclasses.
The Peldszus–Stede scheme is explicitly hierarchical and is evaluated at several coarsening levels, which makes it the most practical to coarsen.

### Cited Findings
- AIF: the core ontology "should be kept as basic as possible"; the authors expect it "will change over time"; inference, conflict and preference are treated as genera of one abstract class of schemes, which "greatly simplifies" adding new ones; new elements (presumptions, exceptions) can be defined in the Forms Ontology "if desired" — [AIF Spec §1, §1.3](https://arg-tech.org/wp-content/uploads/2011/09/aif-spec.pdf)
- AIF acts as an interlingua so n formats need n translation functions instead of n² — [AIF Spec §1](https://arg-tech.org/wp-content/uploads/2011/09/aif-spec.pdf)
- Peldszus evaluates classifiers at several granularity levels of the same scheme: role, type, comb(ined), target, role+type, role+type+comb+target — [Peldszus 2014](https://2014.aclweb.org/W14-21/pdf/W14-2112.pdf)
- A hierarchically weighted agreement measure gave slightly better results than flat κ on the microtext scheme — [Peldszus & Stede LAW 2013 slides (search snippet)](https://peldszus.github.io/files/law2013-slides.pdf)
- Walton schemes can be coarsened: Song et al. collapsed to 3 schemes (policy, causal, sample); Duschl collapsed classes to improve agreement; Visser's ASK is a decision key; PTA splits scheme choice into three binary/ternary sub-decisions — [Visser et al. 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7888437/)

### Inferences
- Practical design: keep a small fixed top level (AIF-like: information node vs relation; relation genus = support / attack), and put fine types below as subtypes (support → {basic, linked, example}; attack → {rebut, undercut}; optionally scheme labels on support edges later).
  Every fine label then has a deterministic parent, so results can always be reported at a coarse level that stays comparable across schema versions.
- Decomposing a hard label into independent small decisions (PTA style, Peldszus role × function × target) raises agreement and suits LLM prompting (one question per dimension).
- Toulmin and Walton are not hierarchical by design; Walton's catalogue is a flat list that later work had to group.

### Gaps
- No published hierarchy of Walton schemes was read this session (only described as collapsed in specific studies).
- No study found that measures LLM extraction agreement per granularity level of the microtext scheme.
