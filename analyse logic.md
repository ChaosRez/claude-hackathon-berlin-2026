# Analysis Logic: Human vs. ChatGPT Financial Reasoning Graph Comparison

> **Status: brainstorm.**
> The current draft plan is `criteria.yaml`, computed by `src/measure.py`.
> Node and edge types here (for example Company, Forecast, `causes`, `predicts`) are ideas only.
> The types we use are in `entity_definition.yaml`, `relation.yaml` and `GUIDE.md`.

## 1. Objective and Core Hypotheses

### 1.1 Core Objective
This task is not simply a comparison of who is “more correct,” but the construction of a dynamic, iterative, and extensible graph-analysis framework for quantifying how humans and ChatGPT differ in financial reasoning. The goal is to evaluate how each system extracts, organizes, revises, and deploys evidence chains from raw text and to compare the structural logic of their reasoning graphs.

Each reasoning process is modeled as a graph composed of Nodes and Edges:
- Nodes represent entities, claims, facts, events, indicators, companies, time points, and other reasoning units.
- Edges represent support, attack, qualification, conclusion, causality, comparison, and inference relations.

The framework focuses on four key dimensions of difference:
- Structural differences: whether the reasoning contains clear hierarchy, central nodes, and evidence-to-conclusion chains.
- Topological differences: whether the graph contains dense hubs, cross-layer propagation paths, and multi-branch decision structures.
- Dynamic logical differences: whether reasoning is progressively revised and converges under new evidence, or remains highly linear and one-directional.
- Representation-evolution differences: whether the graph changes systematically as evidence accumulates and conclusion stability develops over time.

This analysis therefore moves beyond final-answer accuracy and examines the deeper structure of financial reasoning itself.

### 1.2 Core Hypotheses
The study is grounded in the following hypotheses:
- ChatGPT tends to produce linear, compliant, one-directional support trees with relatively centralized claims and sparse evidence.
- Human reasoning contains a higher density of qualifications, attacks, deeper evidence chains, and reflective closed loops.
- In financial analysis, valuable reasoning is not merely the final conclusion, but the capacity to construct multi-branch argumentation under uncertainty and to identify key risks and assumptions.
- Graph-level noise and local overfitting can obscure true capability differences; therefore, a Human-vs-Human baseline is required to separate natural annotation variance from model-specific structural bias.
- Structural consistency over time is more meaningful than superficial output similarity, because robust reasoning must remain stable under changing evidence, complexity, and conflict.

### 1.3 Research Questions
This framework addresses the following testable questions:
1. Do humans and ChatGPT differ systematically in node composition at the entity and claim levels?
2. Do the distributions of relation types differ across support, attack, qualification, and conclusion edges?
3. Are human reasoning graphs more likely to contain refutation loops, risk conditions, and iterative correction mechanisms?
4. Does ChatGPT exhibit stronger single-point convergence, while humans produce more multi-source support and branching correction?
5. Do anomalous nodes such as ungrounded claims, excessive confidence, and inconsistent conclusions reveal meaningful cognitive bias?

### 1.4 Analytical Paradigm
The framework adopts a three-part paradigm:
- Graph-driven analysis: reasoning is represented through entities and relations in context.
- Baseline calibration: Human-vs-Human serves as the natural noise floor and annotation variance reference.
- Open pattern discovery: the framework remains expandable so it can accommodate unknown reasoning structures without hard-coding a single task-specific schema.

This means the script and graph representation must remain schema-agnostic and compatible with future node and edge types, rather than being limited to a fixed label system.

---

## 2. Human-vs-Human Baseline and Noise Floor

### 2.1 Why the Baseline Matters
A comparison of Human vs. ChatGPT alone is insufficient to determine whether the observed differences are meaningful. Even two human annotators may disagree on entity boundaries, claim extraction, relation labeling, and conclusion phrasing. Without a baseline, natural variation may be mistaken for model failure.

The baseline in this task comes from 10 paired blind-review annotation sets in Task 7. This provides:
- a tolerance interval for normal disagreement;
- a reference boundary for statistically meaningful differences;
- a way to distinguish annotation noise from true reasoning divergence.

### 2.2 Core Metrics
We recommend the following core metrics:

1. Graph Edit Distance (GED)
   - Measures overall structural difference in node and edge additions, deletions, and substitutions.
   - Useful for estimating global structural deviation.

2. Node F1 (Entity Span Overlap)
   - Evaluates the consistency of node extraction, including entity boundaries, event names, indicator labels, and company names.
   - Captures differences in extraction granularity and compression.

3. Relation Agreement Rate
   - Measures agreement on edges such as support, attack, qualify, and conclude.
   - Suitable for evaluating structural reasoning agreement beyond answer correctness.

Additional metrics may include:
- Node Type Consistency
- Claim-path Overlap
- Topological Similarity
- Temporal Order Agreement

### 2.3 Statistical Criteria and Significance Thresholds
To keep conclusions scientifically valid, Human-vs-Human and Human-vs-ChatGPT must be compared directly:
- If Human-vs-ChatGPT differences are lower than the Human-vs-Human natural variance range, they should not be interpreted as a meaningful model gap.
- If differences exceed the Human-vs-Human noise floor across multiple metrics, the divergence is likely systematic and meaningful.
- Significance thresholds should consider effect size, variance, and multiple-comparison correction.

Recommended methods:
- Permutation Test
- Mann-Whitney U Test
- Graph embedding clustering

### 2.4 Interpretation of the Noise Floor
The noise floor does not mean “acceptable model difference.” Rather, it clarifies that:
- many structural differences are natural and not necessarily errors;
- graph extraction is inherently uncertain;
- different annotators may disagree on entity granularity, causal classification, and qualification framing;
- real differences typically appear in topology, evidence revision efficiency, and argument depth, not merely in wording differences.

Hence, the Human-vs-Human baseline is not only a control condition but also the credibility anchor of the entire analytical framework.

---

## 3. Core Node and Edge Analysis

The foundation of graph analysis is to distinguish the minimal reasoning units: Nodes and Edges. In financial reasoning, nodes are not simply named entities; they can include evidence, claims, assumptions, and decisions.

### 3.1 Node-Level Dimensions

#### 3.1.1 Type Distribution Spectrum
Nodes may be categorized as:
- Fact / Data / Indicator / Metric
- Event / Announcement / Policy / Market Shock
- Company / Sector / Country / Person / Asset
- Claim / Sub-Claim / Recommendation / Forecast
- Qualification / Risk / Constraint / Assumption
- Conclusion / Final Judgment / Decision

Key analytical questions:
- Are there systematic differences in node-type distributions between human and ChatGPT reasoning?
- Does ChatGPT favor conclusion nodes at the expense of conditional or evidence nodes?
- Do humans insert more qualification and risk nodes before final judgment?

#### 3.1.2 Span Length and Token Compression
Node size and granularity reflect extraction strategy:
- Long nodes usually carry more complete facts or claims.
- Short nodes enable dense extraction but may lose context.
- Compressed nodes reduce redundancy but can discard key evidence.

We examine:
- whether ChatGPT compresses facts too aggressively;
- whether humans preserve more granular evidence and conditions;
- whether distributional differences indicate a trade-off between abstraction and evidential fidelity.

#### 3.1.3 Ungrounded Claims and Hallucination Risk
A critical signal in graph analysis is the presence of ungrounded nodes:
- nodes that appear in the graph but lack clear evidence support;
- claims not tied to a factual or qualified antecedent;
- conclusions unsupported by relevant evidence edges.

This captures:
- overconfident reasoning;
- unsupported inference;
- missing support links for conclusion nodes.

We define metrics such as Ungrounded Claims Rate and Unsupported Conclusion Rate.

### 3.2 Edge-Level Dimensions

#### 3.2.1 Relation Spectrum
Edges should be categorized by relation type, such as:
- supports
- attacks
- qualifies
- concludes
- causes
- compares
- predicts

Comparative differences may be substantial:
- ChatGPT may produce many support edges, creating a more one-directional structure.
- Human reasoning may include more attack and qualify edges, reflecting deeper analytical friction and correction.
- Whether conclusions appear early or are supported by layered evidence is itself a structural feature.

#### 3.2.2 In/Out-Degree Centrality and Hub Nodes
In graph theory, hubs indicate highly influential reasoning units:
- high in-degree nodes are strongly supported or referenced;
- high out-degree nodes branch into many downstream claims or predictions;
- centrality concentration reveals whether reasoning converges or diversifies.

Comparing degree distributions helps determine:
- whether ChatGPT tends toward summary-style convergence;
- whether humans rely on multiple bridge nodes to support complex revision and differentiation.

#### 3.2.3 Reasoning Chain Length and Graph Diameter
Reasoning depth signals the complexity of argumentation:
- short chains suggest fast conclusion-driven reasoning;
- longer chains suggest progressive inductive or comparative reasoning;
- larger graph diameter implies greater branching depth and multi-layered structure.

This helps differentiate:
- “open-the-door-and-summarize” reasoning from
- “layer-by-layer derivation and correction” reasoning.

### 3.3 Motif Analysis

#### 3.3.1 Evidence Chain
Typical motif:
- Fact / Data -> Sub-Claim -> Main Claim

This captures the transformation of raw evidence into intermediate claims and final judgment.

#### 3.3.2 Refutation Loop
Typical motif:
- Claim <- Attack <- Condition

This reflects the process of posing a thesis, introducing a limiting condition or counterevidence, and then revising the claim.

#### 3.3.3 Divergent Decision Tree
Typical motif:
- Premise -> Recommendation A / B / C

This captures multi-path decision-making under uncertainty, a common requirement in financial analysis.

The structural question is whether ChatGPT over-converges to a single path while humans maintain richer branching and trade-off structures.

---

## 4. Open-Ended and Adaptive Framework

### 4.1 Adaptive Pattern and Subgraph Discovery
To avoid locking the analysis to pre-defined patterns, the framework should include adaptive pattern discovery:
- beyond the preset motifs, perform frequent subgraph mining;
- automatically detect repeated unknown reasoning structures;
- treat newly emerging motifs as candidates for future schema expansion.

This allows the framework to remain open to the discovery of new reasoning patterns rather than assuming a fixed list of graph forms.

### 4.2 Schema-Agnostic Architecture
The analysis pipeline should operate on generic graph calculations rather than a fixed set of node and edge labels. It should support:
- future Task 2 and Task 3 extensions;
- new relation labels such as hedges, mitigates, contradicts, dependsOn;
- new node classes without rewriting the full analysis script.

### 4.3 Graph Embedding and Incremental Learning
The framework should support graph embeddings and incremental learning:
- Node2Vec / Graph2Vec
- GNN-based representation learning
- Topological drift analysis across tasks and samples

This transforms the analysis from static metrics into a dynamic model of structural evolution.

### 4.4 Temporal Dynamics of Text-to-Graph Reasoning
Reasoning should be tracked in time order:
- when nodes first appear;
- how later evidence revises earlier claims;
- the relative timing of conclusion formation and correction.

This distinguishes:
- conclusion-first reasoning from
- stepwise derivation and evidence accumulation.

### 4.5 Extractor Uncertainty and Error Attribution
No graph extractor is perfect. We must explicitly separate:
1. Extractor Error: caused by entity recognition, edge extraction, or relation misclassification.
2. Model Reasoning Flaw: caused by genuine reasoning defects, even if extraction is correct.

The framework should therefore include:
- extraction confidence scoring;
- per-node and per-edge uncertainty estimation;
- attribution of observed differences to either noise or true reasoning error.

### 4.6 Open Iterative Loop
The full pipeline should operate in a continuous cycle:
- extract graph;
- compute structural metrics;
- compare to the Human-vs-Human baseline;
- detect anomalies and new motifs;
- update schema and analytic strategy;
- iterate on new data.

This transforms the analysis from a one-off script into an evolving research system.

---

## 5. Implementation Roadmap (Pipeline: src/analyze.py Specs)

### 5.1 Step 1: Data Loading and Preprocessing
The goal is to standardize raw annotation data into a common graph representation.

Implementation should include:
- loading raw samples and annotations;
- normalizing node fields such as id, type, span, text, confidence, and source;
- normalizing edge fields such as source, target, relation type, weight, and evidence span;
- unifying graph representations across formats;
- preserving provenance so each node and edge can be traced to source text.

### 5.2 Step 2: Multi-Level Feature Extraction
This step should proceed through three levels:

Micro-level:
- node type distribution;
- span length distribution;
- relation type distribution;
- in/out-degree distribution;
- unsupported conclusion rate.

Meso-level:
- motif mining;
- evidence chain frequency;
- refutation loop detection;
- divergent decision tree detection.

Macro-level:
- graph diameter;
- graph density;
- clustering coefficient;
- centrality statistics;
- reasoning path depth;
- key route detection.

### 5.3 Step 3: Baseline Comparison and Hypothesis Testing
The pipeline should compare Human-vs-Human and Human-vs-ChatGPT using:
- permutation tests;
- Mann-Whitney U tests;
- graph embedding clustering;
- bootstrap confidence intervals.

Outputs should include:
- effect size;
- p-values;
- confidence intervals;
- distinction between natural variance and true structural deviation.

### 5.4 Step 4: Visualization and Suspicious Case Selection
The analysis should export results to a `results/` directory with:
- graph visualizations;
- metric summaries;
- statistical comparisons;
- suspicious sample rankings aligned with Task 10's strongest divergence examples.

This supports manual review of cases where human reasoning is clearly more qualified, more iterative, or more evidence-rich than ChatGPT output.

---

## 6. Summary: Why This Framework Matters
This research is valuable not because it seeks to prove “who is smarter,” but because it provides a sustained method for detecting and explaining structural differences in reasoning graphs.

Its main strengths are:
1. Structural focus: it prioritizes graph organization rather than surface answer accuracy.
2. Baseline calibration: it uses Human-vs-Human as a noise floor and credibility anchor.
3. Open extensibility: it supports new node and edge types without major rework.
4. Dynamic evolution: it can capture temporal change and topological drift.
5. Explainable error analysis: it separates extraction noise from genuine reasoning defects.

Ultimately, the framework addresses the central question:

Is the difference between humans and ChatGPT merely that they produce different answers, or do they exhibit fundamentally different mechanisms of evidence extraction, qualification, contradiction handling, and conclusion formation?

That is the core analytical question of this task.
