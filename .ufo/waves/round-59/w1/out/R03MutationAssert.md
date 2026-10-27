# R03MutationAssert — Round 59 C1 falsification

Axes: operability and calibration. Targeted clause: each named leg’s own predicate must bind its expected observation and exit; specifically `assert_mutant_breaks_detection` must assert `missed` and exit 1 for the mutant’s `detected` expectation.

Mutation performed only in scratch: inserted unconditional `return True` at the start of `assert_mutant_breaks_detection` in a scratch copy of `tools/round56-env-leg-battery.py` (`/fast/scratch/hyaku/kama-r59/R03MutationAssert/round56-env-leg-battery.py`). Lane source was not changed. The frozen C1 counter sources all tested battery bytes and variants from committed blobs at its exact `--tip`; it has no option to substitute a battery. Therefore it did not score this mutated battery. Do not interpret its pass as mutation survival or mutation rejection.

Command run:

```sh
TMPDIR=/fast/scratch/hyaku/kama-r59/R03MutationAssert python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --work /fast/scratch/hyaku/kama-r59/R03MutationAssert
```

Observed exit: 0. Output: `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`; genuine and all three benign controls accepted; N01–N16 all rejected (exit 1). This is the unmutated frozen battery scoring and is not evidence on the requested mutation. Frozen counter implementation reads `tools/round56-env-leg-battery.py` and every variant from `git show <tip>:<path>`; it cannot consume the scratch copy without changing counter behavior or the frozen input.

**Verdict:** requested mutant battery result is unscored / not established; no claim that the battery passes under this mutation. Calibration/discernment progress is not claimed. No installs.
