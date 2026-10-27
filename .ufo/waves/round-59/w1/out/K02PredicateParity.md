# K02PredicateParity — Round 59 C1

**Axes:** operability; calibration (lowest assigned, 7). Scope: wording/code/label parity only; this is a falsification review, not a seat verdict.

## Counterexample and evidence

Freeze `controls/freeze.txt` lines 5–8 defines the decisive condition as: each named leg's own `--expect` maps to that leg's returned `ld_audit` value and declared exit; only its predicate determines pass/fail; mutant assertion specifically observes `missed` against `detected` with exit 1. It explicitly requires 3/3 genuine leg coverage, negative controls rejected, and zero evaluation errors.

The executed checker `tools/round59-battery-outcome-check.py` does not establish that full condition:

- `result_for` (lines 30–34) synthesizes `detected`/`missed` from parsing the counter source's `BAD_ENV` declaration; this is not an observed `ld_audit` field returned by the leg's actual process result.
- `fake_run` (59–76) records argv and fabricates `stdout`/exit from its `--expect` argument and synthetic observation. It does not parse the returned stdout/exit of an actual `ld_audit` invocation; its return code is simply `expected == observed`.
- Baseline checking (191–194) only requires one call containing both flags and a `True` return per label. It never binds that call's actual `--expect` argument to a particular expected value or verifies the returned field/value and declared exit correspond to it. Fault checking (196–198) only checks that one leg's returned bool is false and top-level exit is 1; it does not require the mutant leg's observation to be specifically `missed` versus `detected`.
- The report says `runs=5`, while the freeze's genuine leg coverage is `3/3`; this is a terminology/summary mismatch unless explicitly described as 1 baseline plus four one-leg fault-injection runs. Counter summary (counter lines 24, 69–70, 111–120) reports genuine + benign variants + no-op rejections, a different population from checker runs, and outputs only verdict/exit—not the underlying expected/observed values despite the freeze's outcome-binding description.

Recorded output `controls/c1-candidate-final.out` lines 2–3 claims `genuine=1/1`, `benign=3/3`, `noop_rejected=16/16`, `errors=0`, `met=True`; detail lines 4–23 list exit classifications only. These are observed classifications under this harness, not evidence of the frozen field/value/declared-exit binding. This counterexample is supported by the harness code itself; no claim is made that the frozen counter was rerun here.

## Impact and smallest safe correction

**Impacted axes:** operability (the checker can report a pass while not measuring the declared process-outcome behavior) and calibration (summary labels/populations can be read as stronger evidence than the checker actually produced).

Smallest safe correction: treat the current C1 pass as **not demonstrated against the frozen predicate** unless a pre-frozen measurement can establish the stronger contract. For future checker design, retain named-leg provenance and assert each leg's concrete expected value against parsed returned `ld_audit` and exit, with the mutant specifically asserting `missed`/`detected`/exit 1; report three genuine legs separately from the four-run fault battery and distinguish checker-run totals from counter fixture counts. Do not change frozen targets, fixtures, or counter after seeing results.

Commands/output: no counter or test command run for this scoped static review. Inspected `controls/freeze.txt`, `tools/round59-battery-outcome-check.py`, `tools/round59-c1-counter.py`, and `controls/c1-candidate-final.out` via file reads. No installs.
