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
   When unsure, ask the test questions in `decision_order` and take the first "yes".
5. Set the flags:
   - `main: true` on exactly one entity, following `flags.main`.
     If no entity answers the question, set every `main` to false and `implicit_main` to true.
   - `hedged: true` when the entity softens its own strength (`flags.hedged`).
6. Set the attributes:
   - `kind` is required for `evidence` (one of fact, example, personal, source) and must be null for every other type.
   - `note` is required for `other` (say why no type fits) and must be null for every other type.
7. Add the relations, following `relation_schema`.
   For each graph node except the main claim, ask "What is this one mostly about?" and draw one edge there.
   `filler` entities are not graph nodes: no edge starts or ends at them.
   Types listed in `edge_optional` may have no edge when none of the relations fits.
8. Check before answering: one main claim, every required edge present, no edge touches filler, the texts joined in order give back the whole answer.

Number entities 1, 2, 3, ... in reading order.
Relations refer to entities by these numbers.
