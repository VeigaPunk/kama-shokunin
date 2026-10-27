# C01SiblingPattern — sibling pattern scan

## Axes
- **Operability:** whether executable checks bind a test invocation's own observed outcome to that invocation's assertion, rather than mere entry/call coverage.
- **Calibration:** whether pass claims are bounded to what the recorded result actually establishes.

## Finding: fit, with caveat
Reusable pattern: record a per-invocation frame containing its own subprocess argv and return value, then require both the expected invocation and its correct returned assertion result in the checker. The most direct precedent is the round-59 outcome checker itself, supported by the round-56 test's explicit expected-outcome interface. This is a pattern to preserve/reuse, not evidence that every return is correctly matched: the current checker has an ambiguous frame identity scheme described below.

### Exact evidence
- `tools/round56-env-leg-test.py` is invoked per leg by `tools/round56-env-leg-battery.py:70-82`; the positive control is explicitly run with expected `detected` (`:71`), and mutant's ordinary roster leg with `missed` (`:80`). The separate assertion `assert_mutant_breaks_detection` documents that it must fail the positive expected-detected assertion (`round56-env-leg-battery.py:48-52`). This establishes meaningful expected behavior at the caller boundary, not just that a function ran.
- Historical sibling falsification demonstrates the value of consuming the result: `.ufo/waves/round-56/w1/out/R04C1Mutation.md:19-22` records exact stdout and exit for old counter/matching `missed` (0), new counter/matching `detected` (0), mutant matching `missed` (0), and mutant expected `detected` (1). `:28-34` explicitly distinguishes the battery's ordinary mutant leg from the separate expected-detected falsification; do not conflate them.
- `tools/round59-battery-outcome-check.py:106-117` profiles calls and returns for `run` / `assert_mutant_breaks_detection`, recording a frame with label, calls, and returned value. `:182-198` consumes those recorded fields: it requires exactly the expected labels/frames, one subprocess call with both `--counter` and `--expect` for every label, and `returned is True` for baseline; per-fault controls require the fault leg not return true while all other legs do. The return value, not just function entry, participates in the verdict.
- Specific counterexample boundary: `:110-115` matches return frames using the string label (and maps every assertion call to `mutant-assert`); `:184-198` rejects duplicate frame counts, but `by_label` is a dict built from frames. Nested/repeated same-label calls or exceptions can therefore risk misattribution; I did not run an isolated probe here, so this is a static risk, not an observed false green. The exact return stack discipline is visible at `:106-117`.

## Fit / no-fit
**Fit:** the transferable pattern is per-leg invocation → capture its own subprocess arguments/observation → capture that invocation's return → independently require the named expected result and return semantics. Round 56's direct `--expect` test supplies the behavioral precedent; round 59's outcome checker attempts to make that dependency machine-checked.

**No-fit as proof of complete correctness:** the present profile checker should not be cited as proof against every nested/repeated-call or exceptional-return case solely from these lines. Its profile stack pairs by labels rather than frame identity, and the test code was not run in this read-only sibling scan.

## Evidence limits
Read-only scan only; no campaign counters, tests, or fixture variants run. No scratch created. No installs or updates. No external S517/S518 spot-check or discernment progress claimed. This finding neither judges the frozen C1 result nor proposes changing its target, fixtures, counters, or kill rules.