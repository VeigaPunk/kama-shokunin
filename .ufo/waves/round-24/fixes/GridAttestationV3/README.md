# GridAttestationV3 — proposal: an internal error is an error, not a refusal

A **proposal only**. Nothing here is production; the L1 integrates it. V1
(`fixes/GridAttestation/`, `6d9e31b7…`) and V2 (`fixes/GridAttestationV2/`,
`45e778a8…`) are **kept filed**; this directory is the V3 successor.

* proposal source: `promisor-grid.py`, sha256 `437128b820a4c49882dc985c4f3ac0e89fd2805000dac93c3b3085f6bb5e102c`
* `promisor-grid.patch` — the full delta against the integrated `b034e159…` (558 diff lines)
* `promisor-grid-v3-delta.patch` — the **incremental** V3 delta against the V2 proposal `45e778a8…` (52 diff lines, sha256 `d4ad1fb3…`), for a surgical composition
* the expectation manifest is **not** touched: 47 cells, byte-identical to the pinned snapshot `d86b7bea…`; no expectation changed, no grader weakened, the strict-14/loose-16 method, the V2 initial-premise guard, the reachable origins and the `--no-lazy` forensic probes are all unchanged

## The gap (DocQualityF1)

The auditor's catch-all prints `could-not-evaluate: internal: <Type>: <exc>`
— an *unanticipated* failure, which the auditor's own contract says is never a
verdict. The grid kept only `stderr_tail` (the last 300 characters), so the
identity could be truncated away, and nothing classified such a row as an
error: an exit 2 carrying that identity could be scored as a legitimate
content refusal and earn a mutant kill.

## What V3 changes

1. **The internal-error identity is captured from the FULL stderr** as a
   boolean row field `internal_error` (`"could-not-evaluate: internal:" in
   stderr`), alongside the existing `traceback`, `timed_out` and `leaked`
   flags. The 300-character tail is kept as it was.
2. **It is graded as an error, not a legitimate refusal.** A row whose
   observation carries `internal_error` is never `met`: the grading adds the
   problem "the auditor reported an internal error, which is not a refusal",
   so the cell counts as unmet and appears in the arm's `violating_cases`.
   No expectation was changed and no rule was weakened; a refusal that is
   only an accident of an unhandled exception can no longer pass as a
   content-derived refusal.
3. **Bounded actual stand-in controls.** The selftest writes two real
   stand-in auditors — one that emits `could-not-evaluate: internal: …` and
   one that emits a Python traceback — runs the grid against them as a
   subprocess, and asserts that the identity is detected
   (`internal_error` / `traceback` true) **and** that the row is not `met`.
   The control is end to end: a real fixture, a real subprocess, a real row.

**Field contract for the mutation runner.** The exact row field is
`internal_error` (boolean, per row, in `doc["arms"][<arm>]["rows"]`); the
existing `traceback`, `timed_out` and `leaked` booleans are unchanged. A row
with `internal_error` true or `traceback` true is an error, not a verdict,
and a mutation runner must treat it as a could-not-evaluate (exit 2, zero
kills) rather than as a kill. The grid's own exit code stays 1 for it (the
row is unmet), so the two contracts do not need to agree: the mutation
runner's rule is the stricter one.

## Bounded verification (no full suite)

`--selftest` **19/19 ok** — three negative capabilities, four command-line
controls, two stand-in controls (`stand-in-internal-detected`,
`stand-in-traceback-detected`), the negative fixture control, the valid
hydration path and the five premise checks.

Direct measurement of the stand-in: a stand-in auditor that prints
`could-not-evaluate: internal: ValueError: boom` and exits 2 yields the row
`{"exit": 2, "met": false, "internal_error": true, "traceback": false,
"timed_out": false, "leaked": false}`, and the arm reports the cell in
`violating_cases`.

**Not re-run**: the full suite and any candidate sweep (L1 instruction).
