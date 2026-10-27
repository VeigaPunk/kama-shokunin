# M02DropFaultPropagation — Round 59 probe

Axes: operability; calibration (7, lowest assigned). Scope: falsification only.

- **Attacked claim/clause:** C1-r59 `tools/round59-battery-outcome-check.py` must require a one-leg injected fault to propagate to main exit 1 (counter predicate: “one-leg faults propagate”).
- **Mutant:** removed `and outcome.get("exit") == 1` from the per-label fault acceptance condition at the measured checker line 196. This allows a fault case to satisfy the checker without requiring its main exit to flip.
- **Expected detector:** frozen C1 counter at `aca8d0067ea25627c5015c2193c843965148bc8e`, command `python3 .../tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --checker <scratch checker.py> --work <scratch work>`; expected nonzero with the N12/N14 no-op mutants exposed.

## Runs and evidence

- Pristine checker SHA-256: `d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d`. Output: `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`; exit 0.
- Mutant checker SHA-256: `7179eb7ed99ede2e80645c49e8b6b7f7085e5bb41c8837266a90e382396b4c8c`. Output: `genuine=1/1 benign=3/3 noop_rejected=14/16 errors=0 met=False`; exit 1. N12-ignore-leg-result and N14-ignore-mutant-result were accepted (exit 0); all other no-ops rejected (exit 1).
- Restored checker SHA-256: `d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d`, identical to pristine. Restored counter output returned to `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`; exit 0.
- **Verdict:** KILLED. The frozen counter rejected this plausible fault-propagation defect. No baseline failure or evaluation error.
- Scratch lived under `/fast/scratch/hyaku/kama-r59/M02DropFaultPropagation/`, `TMPDIR` was set explicitly, and it was removed before completion. No installations or lane-source edits.
