# R57Item25CounterSelftest — no-op control evidence

Axes: operability + calibration. Read-only investigation; no source, shared counter, or frozen-control files changed. Tooling rules were read; no installs performed.

## Runnable predicate and observed result

A valid operability control must reject a matching green summary when the candidate executes zero canonical-table reads. The frozen fixture `controls/c1-noop.py` was run with `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-57/controls/c1-noop.py` and emits `mismatches=0 maxN=46 met=True`; frozen receipt `controls/noop-c1.out` records `canonical_table_reads=0`, `self_description_reads=0`, same summary, `exit=0`. Thus the no-op is accepted and the control predicate detects a false-green (expected defect-detection result: fail/reject candidate), rather than trusting printed `met=True`.

Runnable scratch control: execute that fixture, capture its exit/stdout, and count any canonical-table/self-description reads. Mark false-green when exit is 0, summary has `mismatches=0` and `met=True`, and reads are 0. This is the frozen control's observed case; it detects rather than prevents the no-op. Scratch driver was removed by its exit trap.

## Calibration/maxN cross-check

The C1 frozen base receipt is `controls/base-c1.out`: `mismatches=1 maxN=56 met=False`, exit 1. `controls/freeze.txt` states pre-output mismatch 1; amendment distinguishes the operative calibration row-count correction from the maxN behavior and says this seat evidence is not a target change. The current working counter against `HEAD` was also invoked and returned `mismatches=0 maxN=56 met=True`, exit 0; this is not substituted for the frozen-tip result.

No counter/scorecard files were edited. No commits, pushes, git/jj mutations, or tool installs were performed.
