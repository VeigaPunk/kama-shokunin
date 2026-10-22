# GridAttestationV4 — proposal: the controls must be behavioural and specific

A **proposal only**. Nothing here is production; the L1 integrates it. V1
(`fixes/GridAttestation/`, `6d9e31b7…`), V2 (`fixes/GridAttestationV2/`,
`45e778a8…`) and V3 (`fixes/GridAttestationV3/`, `437128b8…`) are **kept
filed**; this directory is the V4 successor.

* proposal source: `promisor-grid.py`, sha256 `8e0d5c5401bee1c92b0e2421375fd3b03121999a7eef8c97afdac07d35af572d`
* `promisor-grid.patch` — the full delta against the integrated `b034e159…` (601 diff lines, sha256 `3f8ec331b3264eb758cbc6a497b1607950962bbbb416e45f8bae125442a63789`)
* `promisor-grid-v4-delta.patch` — the **incremental** V4 delta against the V3 proposal `437128b8…` (121 diff lines, sha256 `7ea7b22a86e764490b5349dd780098a63207c0792c159ea66e227f6cc9cb0299`)
* the expectation manifest is **not** touched: 47 cells, byte-identical to the pinned snapshot `d86b7bea…`; no expected data, no method, no grader weakened, the strict-14/loose-16 labelling, the V2 initial-premise guard and the V3 `internal_error` contract all unchanged

## The two fidelity issues (L1 V2/V3 delta review)

1. `negative-complete-clone-refused` accepted **any** `Premise`, so an
   unrelated setup failure could green it.
2. The internal stand-in for PG13 carried no named reason and no names, so
   the row was unmet for the wrong reason: the control would still pass if
   the grading's internal check were deleted. It asserted a difference, not
   the difference that matters.

## What V4 changes

1. **A typed contract violation.** `assert_blobless_contract` now raises
   `ContractViolation(Premise)` with a `reason` attribute naming the
   violated clause — `"initial-empty"` (the clone missed nothing: the filter
   was ignored), `"still-missing"` (a hydrated clone still misses objects)
   or `"missing-object"` (the clone does not miss the object the cell is
   about). The complete-clone control now requires the **specific** clause
   `initial-empty`; any other failure leaves the control red. The type
   keeps the exit path unchanged (exit 2, could-not-evaluate).
2. **Behavioural stand-in controls, with a legitimate counter-example.**
   Three real stand-in auditors are run against the real PG13 cell:
   * `content-refusal-meets` — a legitimate content-derived refusal: the
     correct reason class term, the correct names (`corpus/SOURCES.md`), the
     `could-not-evaluate:` prefix, no stdout, exit 2. It **must meet**:
     this proves the grader accepts a proper refusal and is not over-strict,
     and it makes the internal classification the *only* possible cause of a
     difference.
   * `internal-same-reason-does-not-meet` — the **same** valid reason and the
     same names, plus the internal identity, with a body long enough to push
     the prefix out of the 300-character tail. It **must not meet**, and the
     assertion also checks that the prefix is absent from `stderr_tail` while
     `internal_error` is true — proving the identity is read from the **full**
     stderr and not from a tail accident.
   * `traceback-detected` — a traceback is an error too: `traceback` true
     and the row not met.
   No control asserts on source text; all three are driven through the real
   command line and the real row.

## Bounded verification (no full suite)

`--selftest` **20/20 ok** — three negative capabilities, four command-line
controls, three stand-in controls, the specific-clause fixture control, the
valid hydration path and the five premise checks.

The blobless family in both arms against the candidate build
`ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`:
frozen arm 0 violations, strict amended view 0/4 (the r23 refusals); current
arm 0 violations, strict amended view **4/4** — PG05 0, PG06 0, PG28 0, PG43
2, all met; `internal_error` false and `objects_acquired` empty in every cell.

**Not re-run**: the full 47-cell suite and any candidate sweep (L1
instruction).
