# R07DuplicateLabel — C1 label-cardinality falsification

Axes: operability; calibration (7, lowest assigned).

## Finding

**Actionable: the advertised N15 control does not contain the assigned duplicate-label mutation at the measured tip.** `tests/round59-battery-variants/N15-duplicate-leg-label.py` at the lane worktree has three distinct `ROSTER` keys (lines 15–19) and its three `run()` calls use `base-old-counter`, `round56-counter`, and `m-drop-ldaudit` (lines 69–82). Thus it neither duplicates a roster label nor omits another while retaining three calls. The C1 counter enumerates N15 as an enumerated no-op (`tools/round59-c1-counter.py`, `NEW_NOOPS` and fixture materialization); its rejection cannot establish the assigned mutation is detected.

The checker’s label-set test is `set(by_label) == set(LABELS) and len(frames) == len(expected_labels)` in `tools/round59-battery-outcome-check.py`. A duplicate label among three profiled `run` calls would yield fewer distinct frame labels (and fail `names_ok`), provided the checker observes all three calls. But the current N15 file does not exercise that condition.

## Commands / evidence

- `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --work /fast/scratch/hyaku/kama-r59/R07DuplicateLabel` (with `TMPDIR` set to that scratch directory): exit 0; output `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`, including `N15-duplicate-leg-label reject exit=1`.
- Read `tests/round59-battery-variants/N15-duplicate-leg-label.py`: 3 distinct roster labels, 3 calls, no duplicate-label mutation. **The assigned duplicate/omit mutant was not run through the counter**, so it is not passed. The measured baseline result is not evidence against this specific mutation.

No install performed. Scratch contents were removed on command exit. No lane source or fixture was changed.