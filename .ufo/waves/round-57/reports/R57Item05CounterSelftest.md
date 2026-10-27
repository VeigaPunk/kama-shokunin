# R57Item05CounterSelftest — runnable counter controls

## Axes

- **Operability:** a do-nothing control must not be accepted as a successful measurement.
- **Calibration:** a changed/stale measured value must be checked against an independently derived expectation, not accepted because its summary says `met=True`.

## Control design and case-26 result

Case 26 was run independently using a scratch-only Python driver (removed by an EXIT trap after its receipt was copied). The driver runs the frozen counter against the frozen base tip, then runs the supplied no-op and checks each observed result. The driver fails unless the real base remains red and the no-op's claimed green is identified as a false green. Exact commands, stdout, and exit codes are in `R57Item05CounterSelftest-case26.out`.

Runnable control pattern:

```python
base = run([python, "tools/round42-selfdesc-reconcile.py", "--repo", repo, "--tip", frozen_tip])
assert base.exit == 1 and "mismatches=1" in base.stdout and "met=False" in base.stdout
noop = run([python, ".ufo/waves/round-57/controls/c1-noop.py"])
assert noop.exit == 0 and "mismatches=0" in noop.stdout and "met=True" in noop.stdout
assert not accept(noop)  # no-op has no data reads or execution; its own green is the attack
```

The `accept` oracle must be grounded in observed execution/content evidence, not the output summary: this no-op only prints a literal and reads no inputs. For the repaired calibration measurement, independently calculate the named run fact and compare exact stdout to the frozen expected value; do not treat the counter's `maxN` as that fact.

## Evidence and interpretation

- Frozen counter invocation: `r41=1 ... mismatches=1 maxN=56 met=False`, exit 1. Detail identifies the `verifier-spotcheck` count check (expected literal `42`).
- Direct execution of the named count command in the current lane tree: stdout `43`, exit 0. This supports the pre-data freeze amendment's stated stale-count defect (42 vs 43).
- No-op invocation: stdout `mismatches=0 maxN=46 met=True`, exit 0, despite no input inspection. The output alone is not a passing control.
- `maxN=56` is the counter's derived greatest `## Round N` heading, not the verifier-spotcheck count. The assigned prompt's `expected 46` conflates that counter field with the no-op's fabricated literal. The controlling amendment specifies repairing the stale expected count to 43; do not alter the `maxN` derivation to 46 based on this evidence.

This is control design and falsification evidence, not a claim that the shared counter has been repaired. No shared source/tool was edited.

## Tooling

No installs; system Python 3 was used.

## Artifacts

- Report: .ufo/waves/round-57/reports/R57Item05CounterSelftest.md
- Separate case-26 evidence: .ufo/waves/round-57/reports/R57Item05CounterSelftest-case26.md
- Raw case-26 receipt: .ufo/waves/round-57/reports/R57Item05CounterSelftest-case26.out
