# GuardRepair — R1 duplicate-corpus guard repair

seat: KamaR15.GuardRepair-3 (leaf executor)
scope: `.ufo/waves/round-14/measure.py` only

## Change

`corpus_problems` (measure.py:350–364 after edit) previously tested only
`unique < MINIMUM_UNIQUE_CASES`; a duplicate-containing corpus with ≥16
distinct stripped names passed the guard and reached child spawns, despite
the module docstring (:13–14) and `LIMITS[3]` (:77) both promising that
"duplicated corpora fail before any child runs". Inserted two lines before
the preserved minimum check:

```python
if len(declared) != unique:
    problems.append("duplicate case names")
```

`declared` already holds only non-empty stripped `name` strings, so
`len(declared) != unique` fires exactly when a declared name repeats —
including the ≥16-unique duplicate-corpus control the old guard missed.
Non-string or blank/whitespace names are undeclared (unchanged policy) and
the per-fixture `case_problems` path still covers fixture-level shape.

## Behavior

- Any duplicate declared name → `corpus` problems non-empty → `run()` takes
  the corpus branch (:377–380), writes `unmeasured_record` for every case,
  sets `result["error"] = "corpus: duplicate case names"` (plus the minimum
  line if also <16 unique), exits 1 — all before `measure_case`/`subprocess`.
- Valid corpus (all declared names distinct, ≥16 unique) → unchanged:
  minimum check passes, corpus empty, children measure as before.
- CLI schema, `SCHEMA`, `LIMITS` text, and all classification/measurement
  code untouched. No unrelated validation added.

## Correspondence to R1

R1 (corpus/lessons/round-14-verifier-spotcheck.md §142) routes exactly this
repair. Docstring and LIMITS already asserted the behavior, so no prose
correction inside measure.py was needed; the receipt/lesson correction is
owned elsewhere per L1 routing (R2/other seats). Fixture schema note:
`tests/ollama-corpus-guard/*.json` harness controls with ≥16 distinct names
plus a repeated declared name now exercise the reject path.

## Evidence / limitations

- Edited lines verified by read-back: measure.py:356–364 shows the guard in
  place with the minimum check preserved verbatim.
- No builds, tests, linters, or runner executions performed — verification
  is the L1 post-integration gate. [INFERENCE] static reasoning only: the
  guard is evaluated before the child-spawning `elif tool_present` branch.
- Suggest L1 checks: run measure.py against a ≥16-unique duplicate-name
  fixture JSON (expect exit 1, `corpus: duplicate case names`) and against
  the real 51/51-unique corpus (expect unchanged pass path).

## Tools installed

None.

Report: .ufo/waves/round-15/build/advice/GuardRepair.md
