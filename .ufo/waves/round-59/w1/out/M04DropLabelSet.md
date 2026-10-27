# M04DropLabelSet — scoped findings

- Axes: operability and calibration (calibration assigned floor: 7).
- Mutant: removed only `and len(frames) == len(expected_labels)` from the outcome-checker's `names_ok` predicate, leaving set equality intact. Challenged clause: reject extra duplicate frame records even when the set of labels remains exact.
- Frozen detector command, executed pristine, mutated, restored: `python3 <copy>/round59-battery-outcome-check.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e` (run from checker copies under `/fast/scratch/hyaku/kama-r59/M04DropLabelSet`; `TMPDIR` set to that scratch directory).
- Pristine output: exit 0, `runs=5 passed=5/5 errors=0 met=True`; baseline and all four fault cases reported `passed:true`.
- Mutated output: exit 0, identical `runs=5 passed=5/5 errors=0 met=True`; all five cases still passed. Verdict: **survived**. This is a coverage finding: the current detector exercises per-leg outcome faults but its fixture set does not falsify dropping the cardinality term (including duplicate-label behavior).
- Restored output: exit 0, `runs=5 passed=5/5 errors=0 met=True`.
- Hashes: pristine `d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d`; mutated `279a3e3d3245c1c6a76bc8643b2c25fe167ab04cb3404ebb31802cd405c121e2`; restored `d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d` (exact byte restoration). Lane source was not modified; no tools installed.
