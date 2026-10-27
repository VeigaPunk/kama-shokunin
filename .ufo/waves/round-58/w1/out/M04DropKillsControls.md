# M04DropKillsControls — Round 58 mutation probe

Axes: operability (C1 checker behavior); calibration (not assessed by this C1 probe).

- **Target:** C1 frozen counter `tools/round58-c1-counter.py`, running against the committed build tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a` and its genuine/benign/no-op fixture set.
- **Mutant:** Removed only the `kills == 1 and controls == 2` conjunct from checker `met` computation; remaining condition was `match and executed`.
- **Expected detector:** Frozen C1 counter predicate should fail if this mutation allows a behaviorally invalid checker through.
- **Baseline command:** `TMPDIR=/fast/scratch/hyaku/kama-r58/M04DropKillsControls python counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a --checker check.py --out baseline.out` (absolute scratch paths substituted in actual invocation). Output: `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`, with genuine and all three benign accepted, all eleven no-ops rejected. Exit 0.
- **Mutated command:** Same counter invocation against mutated `check.py`, output path `mutated.out`. Actual output was identical: `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`; all per-variant outcomes remained the same. Exit 0.
- **Verdict: SURVIVED.** This specific conjunct-drop mutant passes the bounded detector. The counter fixtures do not exercise a roster with an incorrect number of kill/control designations; therefore their pass does not establish detection of this changed count constraint. This is a coverage finding only, not a change to the frozen predicate.
- **Restoration evidence:** Pristine checker SHA-256 `89ad4e5d5c15c883eacf39126c6d1a0859382c54142976b4ed8539680832eec5`; restored scratch copy SHA-256 identical. Git blob at build tip is `02616f0ff3d6566c878bd4185a77b26b81062f6e`. Scratch was removed after copying receipts; no lane production files were changed.
