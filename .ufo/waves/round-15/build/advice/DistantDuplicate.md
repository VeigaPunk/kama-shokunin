# DistantDuplicate — corpus guard fixture matrix

## Files changed
- `tests/ollama-corpus-guard/DistantDuplicate.json` — new literal shared-schema fixture (created parent directory; the file is the only content under this lane's ownership).

## Behavior
Three literal scenarios, no generator, no execution:

1. `DistantDuplicate.Array32FirstRepeatedAtEnd` — 32 distinct stripped names (`n00`…`n31`) plus a literal repeat of `n00` appended at the end (33 declared, 32 unique), `envelope: "array"`, `expected_rejected: true`. Exercises the distant-duplicate policy path where the repeated name is far from its first occurrence and the old `unique >= 16` minimum guard cannot catch it.
2. `DistantDuplicate.Object16FirstRepeatedAtEnd` — 16 distinct stripped names (`m00`…`m15`) plus `m00` appended (17 declared, 16 unique), `envelope: "object"`, `expected_rejected: true`. Same distant-duplicate policy at exactly the 16-unique floor under the object envelope.
3. `DistantDuplicate.ValidArray32Unique` — the first scenario with the duplicate removed: 32 distinct stripped names, `envelope: "array"`, `expected_rejected: false`. Retains valid unique-corpus measurement coverage.

All scenarios keep case payloads identical except names/envelope, so every config exercises the actual duplicate policy rather than malformed-schema scope. All ids are prefixed `DistantDuplicate`.

## Retained evidence
- Frozen guard source: `.ufo/waves/round-15/frozen/measure-before.py` `corpus_problems` (lines 350–362) collects `name.strip()` values and rejects only when `unique < 16` — confirming the duplicate gap these fixtures must catch after the GuardRepair cutover.
- Shared schema from round-15 spec context: `{name, names, envelope: 'array'|'object', expected_rejected}`; invalid controls require ≥16 distinct stripped names; valid controls ≥16 all-distinct names.

## Risks / limitations
- Fixture asserts only `expected_rejected`; the exact rejection reason string (`"duplicate case names"`) is owned by GuardRepair/check.py and not re-encoded here.
- No verification run performed per lane bounds (no tests/builds/linters); JSON is hand-checked literal — no expressions, no trailing duplicates beyond the deliberate ones.
- `DistantDuplicate.ValidArray32Unique` overlaps ValidBoundaries' 32-unique control conceptually; retained intentionally as the duplicate-removed counterpart required by the assignment.

## Blockers
None.

Report: .ufo/waves/round-15/build/advice/DistantDuplicate.md
