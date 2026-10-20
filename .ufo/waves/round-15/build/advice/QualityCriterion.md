# Round 15 — QualityCriterion (KQ18)

Scope: owned file `corpus/QUALITY.md` only, append-only. No tests, classifier,
selftest, measure harness, guard fixture, census or network executed. No
historical lesson, receipt, verifier spotcheck, frozen source or source file
edited. No tool installed or updated.

## Change

`corpus/QUALITY.md`: appended a new section `## Criteria added — round 15
(2026-10-20, author-appended; no outside review yet)` with one row
`| KQ18 | ...` (line 87) after the intact KQ17 row (line 72). Edit-tool result
shows lines 1–72 unchanged; the append added lines 73–87 (11 lines) at the file
tail, so no existing line anchor moved and the `(supersedes ...)` KQ14 cell and
all KQ1–KQ17 rows are byte-untouched.

No criterion is superseded. The preamble explicitly carries forward KQ13's
available/loaded/identity/readiness separation, KQ14's semantic-human
boundary, KQ16's finding-ID/exit correction and KQ17's verdict/count,
fixed-precedence and fail-closed classifier obligations; it also records that
the R2 partial-output provenance clarification in `lessons/round-15.md` is
append-only history adding no criterion (R2 clarification itself is owned by
another seat).

## KQ18 obligations written

1. **Independent conjuncts.** Minimum unique-name cardinality and name
   injectivity over stripped names are separate obligations; a guard must
   enforce both. The motivating defect: `corpus_problems()` in
   `.ufo/waves/round-14/measure.py:350–362` tests only `unique <
   MINIMUM_UNIQUE_CASES`, never `len(declared) != unique`, so ≥16 distinct
   names plus a duplicate satisfies the floor while violating uniqueness —
   contradicting the docstring `measure.py:13–14` and `LIMITS[3]` promise that
   "duplicated corpora fail before any child is spawned" / "before any child
   runs".
2. **Discriminating red/green through the actual runner CLI.** The duplicate
   corpus expectation must be red against the frozen original runner (it
   measures instead of rejecting) and green against the repaired runner, where
   rejection lands before any classifier child is spawned — zero child
   invocations. An all-distinct-name corpus of at least the minimum size must
   still measure through (valid unique corpus measurement retained).
3. **Frozen control integrity.** The frozen original stays byte-intact as the
   red control (`.ufo/waves/round-15/frozen/measure-before.py` per the shared
   fixture contract); only the guard changes; classifier policy and the
   committed corpus untouched.
4. **Historical receipt validity.** The outside-recounted 51/51 unique-name
   corpus and its recorded round-14 results remain valid on the fixed
   repertoire actually measured; a more general later-discovered promise being
   false does not retract them (spotcheck R1 and round-15 Gate row 3 agree).

## Retained evidence (static reads only)

- `corpus/QUALITY.md`: full read before edit; KQ1–KQ17 rows, section headers
  and review-boundary prose unchanged; append confirmed by the edit diff.
- `corpus/lessons/round-15.md`: Gate rows C1 (admit conditional on measured
  red/green), injective-name reject, 51/51-validity reject; §Mistakes vacuous
  row naming the KQ17 gap KQ18 now records; §Named historical correction R1.
- `corpus/lessons/round-14-verifier-spotcheck.md` routed defect R1 (line 142):
  the false duplicate-name promise at `measure.py:13–14,77` versus the
  unique-count-only check at `corpus_problems():350–362`; the child tool
  selftest independently checks duplicates at `tools/kama-ollama-evidence.py:359–365`.
- `.ufo/waves/round-14/measure.py`: read `corpus_problems`/`run` directly;
  confirmed the guard rejects only `unique < 16`, that `corpus` problems
  produce `unmeasured_record`s with zero child spawns when they fire, and that
  names are canonicalized via `str.strip()`.
- `.ufo/waves/round-15/frozen/measure-before.py` and `manifest.json` exist per
  the frozen-before-source contract (listed, not diffed).

## Limits

- No execution evidence: the repaired guard, the fixture harness, the frozen
  red control and any child CLI were not run by this seat. KQ18 is a written
  quality bar, not a measured round-15 pass; red/green demonstration belongs
  to the executor seats and L1's single verification.
- The exact guard implementation, fixture file names and report details are
  sibling-owned; KQ18 constrains the shape (both conjuncts, pre-child
  rejection, red control retained), not the diff.
- "Red before" is expressed as red through the actual runner CLI (the runner
  measuring rather than rejecting); the zero-child-invocation property applies
  to the repaired runner's rejection path.
- Round 15 has no outside review; discovery credit stays with the round-14
  non-author verifier (R1). This append claims no C1/axis credit; calibration
  remains 7 → 7, delta 0, per the lesson.

## Routing

No cross-file concerns: `lessons/round-15.md` already names KQ18 as the
criterion recording the vacuous-guard gap, so the lesson↔criterion link is
consistent. R2 clarification is explicitly noted as non-criterion history so no
sibling supersedes or duplicates it. Nothing routed to peers.
