# Comparing small typed argument graphs: human vs LLM (HC3)

Scope: per-graph measures, motifs, whole-graph similarity, paired statistics, and pitfalls.
Setting: about 200 HC3 questions, each with one ChatGPT answer and one or more human answers.
Each answer becomes a directed graph of 5–20 sentence nodes.
Nodes carry a role (main claim or not, position).
Edges carry one type from `GUIDE.md` (supports / attacks / explains / example / restates).
Comparisons use roles and edge types only, never sentence text.
Library versions were checked on PyPI and GitHub on 2026-11-07.
Items marked **(unverified)** come from background knowledge, not a source fetched for this note.

## Per-graph descriptive measures and size confounding

### Takeaway
Use a small fixed set of interpretable measures: depth, width, branching, leaf ratio, main-claim position, relation-type shares, chain-ness, tree-ness, and component counts.
Almost all raw structural counts grow with node count, so report them normalized by node count (or by n−1 edges), and also check them with node count as a covariate.

### Cited Findings
- NetworkX 3.7 is the current release (2026-09-21) and needs Python ≥3.12 — [PyPI networkx JSON](https://pypi.org/pypi/networkx/json).
- Threads of Subtlety noted that its human and machine texts were not paired and differed in length. It did not explicitly control for length. Instead it used average shortest path length, which the authors describe as less sensitive to graph size, and it normalized motif counts by each document's total motif count — [Kim et al. 2024, arXiv 2402.10586v2](https://arxiv.org/html/2402.10586v2).
- Kim et al. report that human formality correlates with hyperedge frequency (r ≈ 0.39) but machine formality does not (r ≈ 0.08). So surface style can move structural counts — [arXiv 2402.10586v2](https://arxiv.org/html/2402.10586v2).
- In argument summary graph parsing, all systems got worse as graph depth grew. Depth is therefore the measure an extractor is most likely to get wrong — [search summary of arXiv 2606.01736](https://arxiv.org/pdf/2606.01736.pdf) (snippet only, full paper not read).
- A preprint on "argument collapse" reports that LLMs follow a more fixed structural arc. Vanilla LLMs moved from support to proposal 29.4% of the time on NYT, against 12.3% for humans. This suggests that sequence and transition statistics of relation types are worth measuring — [arXiv 2603.21228](https://arxiv.org/html/2603.21228v1) (search snippet; not read in full).

### Inferences
Recommended measures, with networkx pointers (APIs are standard; check them against nx 3.7 when coding):

| Measure | Definition / code | Size-confounded? | Normalization |
|---|---|---|---|
| n nodes, m edges | `G.number_of_nodes()`, `number_of_edges()` | is the confounder | report it; use as covariate |
| Is tree / forest | `nx.is_arborescence(G.reverse())` if edges point child→parent; `nx.is_forest(G.to_undirected())` | weakly | binary; report the share per group |
| Weak components, isolates | `nx.number_weakly_connected_components`, `list(nx.isolates(G))` | yes (more nodes, more chances) | isolates / n; components − 1 |
| Depth | longest path to the main claim: `nx.dag_longest_path_length` (DAG) or BFS depth from the root on the reversed graph | yes, upper bound n−1 | depth / (n−1); also compare to the expected depth of a random recursive tree of the same n (≈ ln n) **(unverified)** |
| Width | max number of nodes at one BFS level | yes | width / n |
| Branching factor | mean in-degree of non-leaf nodes (children per parent) | mild | already a ratio; also report the max |
| Leaf ratio | nodes with no incoming support/explain edges / n | mild | already normalized; a path has ≈ 1/n, a star has (n−1)/n |
| Chain-ness (linearity) | depth/(n−1) for trees (1 = pure chain, ~1/(n−1) = star); or share of nodes whose parent is the immediately preceding sentence | normalized form OK | — |
| Main-claim position | index of the main-claim sentence / (n−1) ∈ [0,1]; also "first sentence" yes/no | relative position is OK | use the relative form, never the raw index |
| Relation-type shares | count per edge type / m; a 5-dim compositional vector | shares OK, counts not | compare shares; for compositions consider centered log-ratio with pseudo-count **(unverified best practice)** |
| Backward vs forward links | share of edges whose target comes earlier in the text | OK | — |
| Link distance | mean abs(index(source) − index(target)) | yes (bounded by n) | divide by n−1 |
| Centralization | Freeman in-degree centralization: Σ(max_indeg − indeg_i) / ((n−1)²−(n−1))... use the version normalized to the star graph **(unverified formula; implement and test on star = 1, path ≈ 0)** | normalized by design | — |
| Avg shortest path (undirected) | `nx.average_shortest_path_length(G.to_undirected())` per component | yes | Kim et al. use it as a less size-sensitive measure |

- Degeneracies to expect at n = 5–20: a single-claim star gives depth 1 and leaf ratio (n−1)/n. A forced tree makes tree-ness constant at 1. Isolates are always 0 when the extractor is forced to link every sentence. Drop any measure that is constant in both groups, and say that you dropped it.
- If the extractor schema forces "each sentence links to exactly one earlier sentence", then the graph is a tree by construction. Then m = n−1, tree-ness tells nothing, and relation-type shares and shape (depth, width, branching) carry all the signal.
- Normalized ratios still correlate with n (for example, a leaf ratio near 1/n is impossible for large stars). Always add one check: regress each measure on group + log(n), or stratify by n bins, and report whether the group effect survives.

### Gaps
- No source fetched gives a standard "argument graph descriptive metric" catalogue for short QA answers. The table above is a synthesis, not a cited standard.
- The exact Freeman centralization normalization for directed in-degree was not verified against a source.

## Motif / subgraph counting for typed small graphs

### Takeaway
At this scale (≤20 nodes, ≤20 edges), you can enumerate typed motifs exactly with networkx isomorphism or a simple path enumeration.
Specialized tools (ORCA, graph-tool motifs) are unlabeled or undirected and add nothing here.
Use descriptive "motif rate per edge" with paired tests, rather than per-graph z-scores against a null model.

### Cited Findings
- Threads of Subtlety (ACL 2024) parsed texts into RST trees with the DMRST parser and converted them into recursive hypergraphs and then extended Levi graphs. It built motifs from triads: 69 single-triads, 592 double-triads, and 2,394 triple-triads. It hashed subgraphs with Weisfeiler-Lehman and scored motifs with MF-IDF = (motif count / all motif counts in the graph) × log((1+|G|)/(1+#graphs with the motif)). It kept 207 motifs that scored at least 1 SD above the mean. HC3-English was one of its datasets — [arXiv 2402.10586v2](https://arxiv.org/html/2402.10586v2); [code](https://github.com/minnesotanlp/threads-of-subtlety).
- Their reported differences: machine text had more Background relations (DeepfakeTextDetect). In long stories, machine text had more Elaboration and Temporal motifs, and human text had more Joint motifs — [arXiv 2402.10586v2](https://arxiv.org/html/2402.10586v2).
- `networkx.weisfeiler_lehman_graph_hash(G, edge_attr=None, node_attr=None, iterations=3, digest_size=16)` hashes both node and edge attributes. Hashes for directed graphs changed in v3.5: older versions did not tell incoming from outgoing edges. So pin nx ≥3.5 and never compare hashes across versions. `weisfeiler_lehman_subgraph_hashes` also exists — [networkx docs](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.graph_hashing.weisfeiler_lehman_graph_hash.html).
- The networkx docs claim that non-isomorphic graphs get different WL hashes "strongly guaranteed". This is too strong: 1-WL cannot distinguish some non-isomorphic graphs, for example regular graphs **(unverified against a source here; standard WL theory)**. For typed trees, WL is exact for isomorphism of trees **(unverified)** — [networkx docs](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.graph_hashing.weisfeiler_lehman_graph_hash.html).
- DotMotif 0.18.0 (2026-07-27, repo pushed 2026-11-05, Python ≥3.10, networkx ≥3.1) writes motifs as directed edge lines with edge attribute filters, for example `B -> C [type = "inhibitory"]`. It has `ignore_direction`, `exclude_automorphisms`, and `enforce_inequality` options, and runs on networkx via `GrandIsoExecutor`. The README does not say whether matches are induced — [GitHub aplbrain/dotmotif](https://github.com/aplbrain/dotmotif); [PyPI](https://pypi.org/pypi/dotmotif/json).
- ORCA counts undirected graphlets of 4 or 5 nodes (15 or 73 node orbits) by solving linear equations instead of enumerating them. No source was found that shows support for directed or labeled graphs — [ORCA page](https://file.biolab.si/biolab/supp/orca/orca.html); [Hočevar & Demšar, arXiv 1601.06834](https://arxiv.org/pdf/1601.06834).
- graph-tool 2.11 is on PyPI, but with no Python requirement metadata. It is usually installed through conda or Homebrew **(install route unverified)** — [PyPI graph-tool JSON](https://pypi.org/pypi/graph-tool/json).

### Inferences
- Recommended implementation, about 30 lines and without extra libraries:
  - Typed 2-paths (the "example → reason → claim" family): `for v in G: for u in G.predecessors(v): for w in G.successors(v): count[(G[u][v]['type'], G[v][w]['type'], role(w))] += 1`. With 5 types this gives 25 typed 2-paths, plus role of the endpoint.
  - "Attack then rebuttal": an attack edge u→v, followed by a support/attack edge x→u that defends v **(the defining pattern must follow `GUIDE.md`)**.
  - Typed sibling pairs (two children of one parent): an unordered pair of edge types.
  - Typed in-stars at the main claim: the multiset of edge types into the main claim.
  - For arbitrary k-node typed motifs, use `nx.algorithms.isomorphism.DiGraphMatcher(G, M, node_match=nx.isomorphism.categorical_node_match('role', None), edge_match=nx.isomorphism.categorical_edge_match('type', None))` with `.subgraph_isomorphisms_iter()` (induced) or `.subgraph_monomorphisms_iter()` (non-induced). Divide by the motif's automorphism count. These are standard networkx APIs **(unverified against 3.7 docs in this note)**.
  - As an alternative, enumerate all connected k-node induced subgraphs (k = 3) and key them by `weisfeiler_lehman_graph_hash(sub, node_attr='role', edge_attr='type')`. This is the Threads-of-Subtlety approach, scaled down.
- Normalize motif counts by the number of edges or 2-paths in the graph (a rate), not as raw counts. Raw counts grow with n.
- Null models: classic motif z-scores against degree-preserving rewiring are poorly defined on trees with 5–20 nodes. Rewiring breaks the tree property and the "link to an earlier sentence" rule, and the null distributions are tiny and discrete. Better options are a **type-shuffle null** (keep the topology fixed, permute edge-type labels within the graph) to ask "is this type sequence over-represented given this graph's type mix?", and to pool motif rates per group and compare them with paired tests (section 4). If you use a null, generate it with the same constraints as the extractor (a tree linking to earlier sentences).
- Expect many motifs to be zero in most graphs. Keep only motifs present in at least ~10% of graphs (in either group) before testing. Pre-register the list, or the multiple-testing burden explodes.

### Gaps
- No prior work was found that does typed motif analysis on argument-mining graphs (as opposed to RST) for human-vs-LLM text. The search returned only RST (Threads of Subtlety) and argument-content homogeneity studies.
- The induced vs non-induced semantics of DotMotif were not confirmed.

## Whole-graph similarity

### Takeaway
For trees: use tree edit distance (APTED or zss), which is exact and fast.
For DAGs: networkx GED is only practical with a timeout or `upper_bound`. In a local test it did not finish within 20 s at ≥12 nodes.
For distribution-level comparison: use a WL subtree kernel on edge-labeled graphs, via GraKeL after moving edge types into nodes, or via networkx WL subgraph hashes as features.
Avoid Graph2Vec (karateclub): its dependency pins clash with current scipy and networkx, and it is unmaintained.

### Cited Findings
- `nx.graph_edit_distance(G1, G2, node_match, edge_match, node_subst_cost, …, roots=None, upper_bound=None, timeout=None)` is exact. On timeout it "returns the current best GED", which may not be optimal. `roots=(r1, r2)` forces the two roots to match (useful: match the two main claims). Both graphs must be the same type — [networkx docs](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.similarity.graph_edit_distance.html).
- `nx.optimize_graph_edit_distance(...)` is a generator of consecutive approximations. Default costs are substitution 0 and insert/delete 1. `node_subst_cost` overrides `node_match` — [networkx docs](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.similarity.optimize_graph_edit_distance.html).
- **Local timing test** (this note; networkx 3.2.1, Python 3.9, Apple Silicon Mac; one random pair of typed recursive trees per size; node_match on role, edge_match on type; script in the session scratchpad, not the repository). Exact GED with `timeout=20`: n=8 took 0.07 s, n=10 took 3.4 s, and n=12, 15 and 20 all hit the 20 s timeout (so the values are not proven optimal). One n=6 pair took 13.5 s, which shows that runtime varies widely. The first approximation from `optimize_graph_edit_distance` came in ≤0.004 s but was 10–60% above the best value found (for example 31 vs 27 at n=20). This is a single anecdotal run per size, not a benchmark.
- APTED 1.0.3 (released 2017-11-08, repo last pushed 2017) gives tree edit distance with a custom `Config` (override `rename` and `children`) or `PerEditOperationConfig(...)` weights. Usage: `APTED(t1, t2, cfg).compute_edit_distance()`, and `.compute_edit_mapping()` — [PyPI apted](https://pypi.org/project/apted/); [repo API](https://api.github.com/repos/JoaoFelipe/apted).
- zss 1.2.0 (Zhang–Shasha tree edit distance) was released 2018-03-12 — [PyPI zss JSON](https://pypi.org/pypi/zss/json).
- GraKeL 0.1.11 (2026-08-24) requires **Python ≥3.9 and <3.13**, and has wheels up to cp312 — [PyPI grakel JSON](https://pypi.org/pypi/grakel/json). Its GitHub README says Python ≥3.10 and <3.15, which conflicts with PyPI; trust the PyPI metadata for what installs today — [GitHub ysig/GraKeL](https://github.com/ysig/GraKeL). It ships 16 kernels, including vertex/edge histogram, shortest path, graphlet sampling, random walk, neighborhood hash, NSPDK, propagation, pyramid match, subgraph matching, and WL optimal assignment, plus the WL and Core frameworks — [GitHub ysig/GraKeL](https://github.com/ysig/GraKeL).
- **Version conflict:** networkx 3.7 needs Python ≥3.12 and GraKeL 0.1.11 needs Python <3.13. So **Python 3.12 is the only version that runs both at their latest releases** — [PyPI networkx](https://pypi.org/pypi/networkx/json); [PyPI grakel](https://pypi.org/pypi/grakel/json).
- The GraKeL WL framework relabels vertices using **discrete node labels**. The docs do not mention edge labels — [GraKeL WL docs](https://ysig.github.io/GraKeL/0.1a8/kernels/weisfeiler_lehman.html).
- karateclub on PyPI is 1.3.3 (2022-10-22). The GitHub master `setup.py` pins `scipy<1.13` and `decorator==5.1.*`, and the repo was last pushed 2024-07-17. This conflicts with networkx 3.7's default extra (`scipy>=1.15`) — [PyPI karateclub JSON](https://pypi.org/pypi/karateclub/json); [setup.py](https://raw.githubusercontent.com/benedekrozemberczki/karateclub/master/setup.py); [PyPI networkx](https://pypi.org/pypi/networkx/json).
- Threads of Subtlety used WL hashing of discourse subgraphs, not whole-graph GED, for human-vs-machine discourse comparison — [arXiv 2402.10586v2](https://arxiv.org/html/2402.10586v2).

### Inferences
- **Cost design for GED/TED.** Node substitution costs 0 if the roles match, else 1. Edge substitution costs 0 if the types match, else 1 (or 0.5 for related types, for example supports↔explains, only if `GUIDE.md` agrees). Insert/delete costs 1. Always also report **normalized distance** = GED / (n1 + m1 + n2 + m2) or TED / (n1 + n2). Raw edit distance grows with size difference.
- **Trees → TED.** Convert each tree into a rooted ordered or unordered tree with the main claim as root. Put the edge type into the child node's label (label = `role|type_to_parent`), so that TED captures edge types. APTED and zss compute **ordered** TED, so child order matters. Order children by sentence position (this is meaningful for text). Unordered TED is NP-hard in general **(unverified)**.
- **DAGs → GED with guards.** Use `graph_edit_distance(..., roots=(claim1, claim2), timeout=5)` and log whether each pair timed out. Report the timed-out share by group, and do not drop those pairs (CLAUDE.md rule). Or switch to WL-kernel distance.
- **WL kernel with edge types.** Either (a) build a Levi graph: replace each typed edge u→v with u→e→v, where node e has label = type, then run GraKeL `WeisfeilerLehman(n_iter=2..3, base_graph_kernel=VertexHistogram, normalize=True)`. GraKeL parameter names are **unverified**: the docs page calls the base parameter `base_kernel`. Or (b) skip GraKeL. Compute `nx.weisfeiler_lehman_subgraph_hashes(G, node_attr='role', edge_attr='type', iterations=2)`, build a bag-of-hashes count vector per graph, and use cosine or normalized dot product. Option (b) avoids the Python-version conflict. It is close to a WL subtree kernel with directed edge-labeled refinement **(equivalence unverified)**.
- Converting directed graphs to the GraKeL input format may lose direction **(GraKeL directed support was not confirmed)**. Option (b) keeps direction (nx ≥3.5).
- **Graph2Vec**: not recommended. It needs training on a corpus, results vary across seeds, it is hard to explain to a mixed team, and its dependencies clash with the current stack. Hand-built feature vectors (the section 1 measures + motif rates) plus WL bag-of-hashes give the same "embedding" role and stay interpretable.
- Shortest-path and graphlet kernels: shortest-path is fine on tiny graphs. Graphlet kernels on 5–20 node trees are almost degenerate (trees contain only path and star graphlets).

### Gaps
- GraKeL's handling of directed graphs and edge labels in the WL kernel was not confirmed from docs. Test it on a toy example before use.
- No source was found that applies GED, TED, or graph kernels to compare argument graphs of human vs LLM text. Only RST motif work (Threads of Subtlety) exists in the sources found.
- The runtime figures come from one local run on networkx 3.2.1, not 3.7.

## Statistics for the paired design

### Takeaway
Use the question as the unit of analysis.
For each measure, compare LLM vs human on the same question with a Wilcoxon signed-rank test or a paired permutation test, and report effect sizes with bootstrap CIs over questions.
For distances, test whether d(human, LLM) exceeds d(human, human) within the same question.
Correct across measures with Benjamini–Hochberg.
Use MMD with a WL kernel as one global two-sample check, with kernel settings fixed in advance.

### Cited Findings
- `scipy.stats.wilcoxon(x, y=None, zero_method='wilcox', correction=False, alternative='two-sided', method='auto', ...)`: the default `'wilcox'` **discards zero differences**. `'zsplit'` and `'pratt'` keep them. `method='auto'` is exact only when len(d) ≤ 50, and with ties/zeros only when len(d) ≤ 13. The docs recommend passing a `PermutationMethod` when there are ties or zeros. They also recommend rounding x−y before testing, to avoid float noise — [SciPy docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html).
- `scipy.stats.false_discovery_control(ps, method='bh'|'by')`: BH is valid for independent or positively dependent p-values. BY is valid under any dependence but is more conservative — [SciPy docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.false_discovery_control.html).
- SciPy 1.18.1 (2026-08-21) needs Python ≥3.12 — [PyPI scipy JSON](https://pypi.org/pypi/scipy/json).
- O'Bray et al. (ICLR 2022) show that MMD results for graph distributions depend strongly on the kernel, descriptor and hyperparameters (for example the Gaussian σ), so model rankings can be arbitrary. Some kernels used in prior work (TV-distance-based) are not positive definite, which breaks MMD's guarantees. They recommend choosing descriptors, kernels and parameters with reference data, independently of the models being compared — [arXiv 2106.01098](https://arxiv.org/abs/2106.01098); [Rieck blog summary](https://bastian.rieck.me/blog/2022/watchmen/) (details from search summaries, full paper not read).
- GraphRNN-style evaluation uses MMD over degree, clustering and orbit-count (ORCA) distributions **(unverified, from background knowledge; You et al. 2018, arXiv 1802.08773)**.

### Inferences
- **Unit and pairing.** One row per question. If a question has several human answers, average the human-side measure over them, or pick one human at random with a fixed seed. Do not treat every human answer as an independent pair, because that inflates n.
- **Per-measure test.** d_q = measure(LLM_q) − measure(human_q). Use `wilcoxon(d, zero_method='zsplit', method=PermutationMethod(n_resamples=9999))` or a sign-flip permutation on the mean of d (`scipy.stats.permutation_test(..., permutation_type='samples')`). Many measures here are discrete (depth, counts), so ties and zeros will be common, and the default `'wilcox'` silently shrinks n. Report n_used.
- **Effect sizes** (CLAUDE.md wants them next to baselines): median paired difference with a 95% bootstrap CI (resample questions, B = 10,000, percentile or BCa via `scipy.stats.bootstrap`), plus the matched-pairs rank-biserial correlation r_rb = (W+ − W−)/(W+ + W−) **(standard formula, unverified here)**. For binary measures (main claim first: yes/no), use McNemar's test on the discordant pairs **(unverified API: `statsmodels.stats.contingency_tables.mcnemar`)**.
- **Human–human baseline for measures.** On questions with ≥2 human answers, compute the same paired difference between human_a and human_b (random order, fixed seed). The claim is "|LLM−human| differences are larger than |human−human| differences". Show both distributions side by side. If only a subset of questions has 2+ humans, run the LLM-vs-human test on that same subset as well, so the comparison is fair.
- **Distance-based test (the core comparison).** For question q with humans h1, h2 and LLM L: Δ_q = mean(d(L, h1), d(L, h2)) − d(h1, h2). Test whether median Δ > 0 with a one-sided Wilcoxon or sign-flip permutation over questions. With a single human per question, you cannot form a within-question baseline. Use a **cross-question** baseline instead: d(human_q, human_q′) for random q′, against d(LLM_q, LLM_q′) and d(human_q, LLM_q′). That gives an "LLMs are more homogeneous than humans" test. The extractor confound applies here too.
- **Size-matched distance.** Since edit distances grow with |n1 − n2|, also report the test restricted to pairs with |n1 − n2| ≤ 2. Or regress Δ on |Δn|.
- **MMD.** Use a WL kernel (positive definite) on the LLM graph set vs the human graph set. MMD² is unbiased U-statistic. For the p-value, use a **paired** permutation that swaps the LLM/human labels within each question (not free shuffling), which respects the pairing. Fix n_iter and normalization **before** looking at results, and also report one alternative setting as a sensitivity check (O'Bray et al.). Run the same MMD for human-set-A vs human-set-B as the baseline.
- **Multiple comparisons.** Group the tests into families: (a) ~10 descriptive measures, (b) relation-type shares, (c) motif rates, (d) global distance tests. Apply BH within each family. Name one or two pre-registered primary outcomes (for example normalized TED Δ and the relation-type share vector), and do not correct those against the exploratory ones.
- **Power with n ≈ 100–200 pairs.** A paired test at 80% power and α = 0.05 detects roughly a standardized paired effect of d_z ≈ 0.2–0.28 (n = 200 to 100) **(rule of thumb, unverified; compute exactly with a power tool if needed)**. Smaller effects are not resolvable, so report the CIs rather than "no difference".

### Gaps
- No source fetched covers MMD-with-pairing for paired graph samples. The within-question label-swap permutation is a design recommendation from standard permutation-test logic, not taken from a cited paper.
- The full text of O'Bray et al. was not read, so the specific kernel recommendations (for example which σ-selection procedure) are not detailed here.

## Pitfalls: length confounding, extractor bias, degenerate metrics

### Takeaway
The three biggest threats are text length, extractor bias, and degeneracy.
More sentences means bigger graphs.
The LLM extractor may parse ChatGPT's tidy prose into cleaner trees.
Tiny forced trees make many metrics constant.
Each needs an explicit check in the results table.

### Cited Findings
- Threads of Subtlety did not pair human and machine texts and did not explicitly control for length. Its detection improved with longer generations. So structure-based signals change with length — [arXiv 2402.10586v2](https://arxiv.org/html/2402.10586v2).
- Argument graph parsers get worse with graph depth — [search summary of arXiv 2606.01736](https://arxiv.org/pdf/2606.01736.pdf).
- networkx WL hashes for directed graphs changed in v3.5. Hashes computed under different networkx versions are not comparable — [networkx docs](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.graph_hashing.weisfeiler_lehman_graph_hash.html).
- SciPy's default Wilcoxon `zero_method='wilcox'` drops zero differences, which changes the effective n without warning — [SciPy docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html).
- MMD conclusions can flip with the kernel or parameter choice — [arXiv 2106.01098](https://arxiv.org/abs/2106.01098).

### Inferences
- **Length.** Report n (sentences) per group with a paired test first. Then (1) use the normalized measures from section 1, (2) add a model: measure ~ group + log(n) + (1|question) (`statsmodels` MixedLM, or simply a paired regression of d_measure on d_log_n), and (3) run a length-matched subset analysis (pairs with |n_LLM − n_human| ≤ 2). If an effect disappears under (2) or (3), report it as length-driven.
- **Extractor bias** (required by CLAUDE.md). Compute extractor-vs-hand-label agreement separately for human and LLM texts: edge-type accuracy, attachment (parent) accuracy, main-claim accuracy, and normalized TED between the extracted and gold graph. If agreement is lower on human text, then human graphs carry more extractor noise. Noise usually inflates distance-based diversity (human–human distances grow), which can fake an "LLMs are more uniform" finding. Mitigation: show the main results on the hand-labelled subset too, and run the same distance test on gold graphs.
- **Degenerate metrics.** Before testing, print for each measure the share of graphs at the min/max value and the number of unique values per group. Drop measures that are constant or nearly constant (for example >90% at one value), and list them.
- **Forced structure.** If the prompt forces each sentence to attach to one earlier sentence, then tree-ness, isolate counts and m are fixed. A "chain" default (attach to the previous sentence) is a likely extractor shortcut. Measure the share of "attach to the immediately previous sentence" per group and per extractor-vs-gold.
- **Failed graphs.** Count graphs that fail validation (cycles, unknown types, missing main claim) per group, and keep them in denominators (CLAUDE.md). Failure rates may differ by group and are themselves a finding.
- **Multiple human answers.** Questions with more humans should not get more weight. Aggregate per question.
- **Text-free rule.** Every measure above uses only `role`, position index, and edge `type`. Do not use embedding-based node labels.
- **Environment.** Pin Python 3.12 (the only version that runs both networkx 3.7 and grakel 0.1.11). Avoid karateclub. Record networkx and scipy versions in `JOURNAL.md`, because WL hashes and test methods depend on them.

### Gaps
- No published baseline for extractor reliability on HC3 human vs ChatGPT text was found. It has to be measured in this project from `annotations/`.
- The size of the length effect on these specific graph measures is unknown until it is computed on the project data.
