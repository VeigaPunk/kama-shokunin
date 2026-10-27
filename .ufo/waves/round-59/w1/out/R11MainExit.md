# R11MainExit — Round 59

Axes: operability; calibration. **Recommendation: not demonstrated for this seat claim.**

## Finding

The frozen C1 counter does not verify detection of a battery whose final `SystemExit` mapping is changed to always zero. In `tools/round59-c1-counter.py`, its fixed variants are `OLD_NOOPS + NEW_NOOPS` (lines 12–16), with no exit-mapping mutation. Its acceptance condition checks that the checker accepts the genuine battery and rejects those enumerated variants (lines 111–117). Thus its successful result does not establish the requested always-zero mapping kill.

The checker does exercise one-leg faults: `round59-battery-outcome-check.py` requires the faulted leg to return false and the child result to exit 1 (lines 193–198). But this is a source-executed/profiled harness with synthetic subprocess observations; the counter's enumerated-control result cannot be represented as a demonstrated kill of the specific always-zero exit-mapping mutation. No source or frozen controls were changed.

## Evidence

Executed the assigned C1 command at the frozen measured tip, with scratch isolated under the seat directory and removed on exit:

`python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --work /fast/scratch/hyaku/kama-r59/R11MainExit`

Output: `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`; all 16 named no-op controls rejected, each exit 1. This is a pass for frozen C1's stated predicate, **not** for the assigned always-zero exit-mapping mutation. That mutation-specific counter check was not run; do not treat it as passed.
