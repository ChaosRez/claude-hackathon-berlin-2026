You label the pieces of one answer to a question.
The answer is already split into numbered pieces; keep that split exactly.
In this step you only give each piece a type and flags.
A later step adds the links between pieces.

Follow the entity schema below exactly, and use only the types it lists.

<entity_schema>
{entity_schema}
</entity_schema>

How to work:

1. Read the whole answer once.
2. Give every piece one entity type, using its number as `id`.
   When unsure, ask the test questions in `decision_order` and take the first "yes".
3. Set the flags:
   - `main: true` on exactly one piece, following `flags.main`.
     If no piece answers the question, set every `main` to false and `implicit_main` to true.
   - `hedged: true` when the piece softens its own strength (`flags.hedged`).
4. Set the attributes:
   - `kind` is required for `evidence` (one of fact, example, personal, source) and must be null for every other type.
   - `note` is required for `other` (say why no type fits) and must be null for every other type.
5. Return one node per piece, in the given order, with the same numbers.
