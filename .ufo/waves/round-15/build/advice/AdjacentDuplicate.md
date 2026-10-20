# AdjacentDuplicate — scoped findings

## File written

- `tests/ollama-corpus-guard/AdjacentDuplicate.json` (new, 1389 bytes)

## Matrix contents

Four literal scenarios, shared schema `{name, names, envelope, expected_rejected}`,
ids prefixed `AdjacentDuplicate`:

1. `AdjacentDuplicate-array` — 17 entries, `n05` duplicated adjacent (positions
   6-7), `envelope: "array"`, `expected_rejected: true`. 16 distinct stripped
   names, so the pre-repair minimum-unique-only guard cannot catch it; only the
   `len(declared) != unique` duplicate check rejects it.
2. `AdjacentDuplicate-object` — identical `names`, `envelope: "object"`,
   `expected_rejected: true`. Proves the guard fires before any child process
   for both document envelopes.
3. `AdjacentDuplicate-valid-unique-array` — the duplicate removed; 16 distinct
   names, `expected_rejected: false`. Retains valid-corpus measurement coverage.
4. `AdjacentDuplicate-valid-unique-object` — same 16 distinct names under
   `envelope: "object"`, `expected_rejected: false`.

## Grounding

- Guard semantics confirmed in `.ufo/waves/round-14/measure.py`
  `corpus_problems`: names canonicalized via `str.strip()`, duplicate detection
  is `len(declared) != unique`, minimum is `unique < MINIMUM_UNIQUE_CASES`
  (16). All invalid rows carry exactly 16 distinct stripped names, so each
  exercises only the duplicate policy, never malformed-schema or under-count
  scope.
- Shape mirrors sibling fixtures `PrependDuplicate.json` /
  `ObjectEnvelope.json` in the same directory (field order varies slightly in
  ObjectEnvelope; I used the PrependDuplicate order `name, names, envelope,
  expected_rejected` for consistency within this file).

## Limitations / risks

- No verification commands run per lane bounds; JSON validity is structural
  only (written by hand, not parsed).
- Overlap note: `ObjectEnvelope.json` already contains an adjacent duplicate
  (`ObjectEnvelope_duplicate_n14_adjacent`, duplicating n14 in an object
  envelope). My object row duplicates n05 adjacently — same policy, different
  position and seed; both are in-scope for their assigned files.
- Harness contract assumed: clones first passing case in
  `tests/ollama-evidence/cases.json`, replaces `name` per `names` item, wraps
  in the declared envelope. No generator or execution here.
