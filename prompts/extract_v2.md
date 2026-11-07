You label the reasoning structure of one answer to a personal-finance question.
You turn the answer into a graph: entities are the nodes, relations are the edges.

Follow the two schemas below exactly.
They are the team's definition of a correct graph.
Use only the entity types and relation types they list.

<entity_schema>
{entity_schema}
</entity_schema>

<relation_schema>
{relation_schema}
</relation_schema>

How to work:

1. Read the whole answer once.
2. Find the main claim: the entity that answers the question most directly.
3. Cut the whole answer into entities, in reading order, following `segmentation`.
   Every word belongs to exactly one entity, including filler.
   Copy each entity's text exactly as it appears in the answer, character for character.
   Do not fix typos, do not drop words, do not add words, do not reorder.
4. Give each entity one type.
   When unsure, ask the entity test questions in `decision_order` and take the first "yes".
5. Set the flags:
   - `main: true` on exactly one entity, following `flags.main`.
     If no entity answers the question, set every `main` to false and `implicit_main` to true.
   - `hedged: true` when the entity softens its own strength (`flags.hedged`).
6. Set the attributes:
   - `kind` is required for `evidence` (one of fact, example, personal, source) and must be null for every other type.
   - `note` is required for `other` (say why no type fits) and must be null for every other type.
7. Add the edges, following the relation schema `rules`.
   - Every entity except the main claim and filler needs at least one outgoing edge.
   - Add an edge only when the text clearly makes the link (`explicit_only`).
     An entity may have several outgoing edges.
   - Mark exactly one outgoing edge per entity `primary: true`: the link to the entity it is most about.
     Following primary edges from any entity must lead to the main claim.
     The main claim has no primary edge, and `conflicts` edges are never primary.
   - At most one edge per pair of entities, no self loops, and no edge starts or ends at filler.
   - When unsure which relation fits, ask the relation test questions in the relation `decision_order`.
8. Check before answering: one main claim, every required edge present, one primary edge per entity, no edge touches filler, the texts joined in order give back the whole answer.

Number entities 1, 2, 3, ... in reading order.
Edges refer to entities by these numbers.
