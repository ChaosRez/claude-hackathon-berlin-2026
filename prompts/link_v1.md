You link the pieces of one answer to a question into a reasoning graph.
The answer is already split into numbered pieces, and each piece already has a type.
The main claim is marked.
Keep the pieces, types and main claim as given; in this step you only add edges.

Follow the relation schema below exactly, and use only the relation types it lists.
The entity schema is included so you know what each type means.

<entity_schema>
{entity_schema}
</entity_schema>

<relation_schema>
{relation_schema}
</relation_schema>

Rules:

- Every piece except the main claim and filler needs at least one outgoing edge.
- Add an edge only when the text clearly makes the link (`explicit_only`).
  A piece may have several outgoing edges.
- Mark exactly one outgoing edge per piece `primary: true`: the link to the piece it is most about.
  Following primary edges from any piece must lead to the main claim.
  The main claim has no primary edge, and `conflicts` edges are never primary.
- At most one edge per pair of pieces, no self loops, and no edge starts or ends at filler.
- When unsure which relation fits, ask the relation test questions in the relation `decision_order`.
