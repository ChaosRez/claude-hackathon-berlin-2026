You split one answer to a question into the pieces of its reasoning.
This is stage 1 of a reasoning-graph extraction: later stages give each piece a type and link the pieces.
Here you only split.

The team's entity schema below defines what one piece is (`segmentation`, `coverage`) and which roles pieces can have.
Split so that each piece has exactly one role from that schema.

<entity_schema>
{entity_schema}
</entity_schema>

Rules:

1. Cut the whole answer into pieces, in reading order, following `segmentation`.
2. Every word belongs to exactly one piece, including greetings and other filler.
3. Copy each piece exactly as it appears in the answer, character for character.
   Do not fix typos, do not drop words, do not add words, do not reorder.
4. Check before answering: the pieces joined in order give back the whole answer.
