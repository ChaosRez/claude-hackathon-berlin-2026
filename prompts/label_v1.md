You label the reasoning structure of one answer to a question.
The answer is already split into numbered pieces; keep that split exactly.
You give each piece a type and flags, and add the edges between pieces.

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
2. Give every piece one entity type, using its number as `id`.
   When unsure, ask the entity test questions in `decision_order` and take the first "yes".
3. Set the flags:
   - `main: true` on exactly one piece, following `flags.main`.
     If no piece answers the question, set every `main` to false and `implicit_main` to true.
   - `hedged: true` when the piece softens its own strength (`flags.hedged`).
4. Set the attributes:
   - `kind` is required for `evidence` (one of fact, example, personal, source) and must be null for every other type.
   - `note` is required for `other` (say why no type fits) and must be null for every other type.
5. Add the edges, following the relation schema `rules`.
   - Every piece except the main claim and filler needs at least one outgoing edge.
   - Add an edge only when the text clearly makes the link (`explicit_only`).
     A piece may have several outgoing edges.
   - Mark exactly one outgoing edge per piece `primary: true`: the link to the piece it is most about.
     Following primary edges from any piece must lead to the main claim.
     The main claim has no primary edge, and `conflicts` edges are never primary.
   - At most one edge per pair of pieces, no self loops, and no edge starts or ends at filler.
   - When unsure which relation fits, ask the relation test questions in the relation `decision_order`.
6. Return one node per piece, in the given order, with the same numbers.
