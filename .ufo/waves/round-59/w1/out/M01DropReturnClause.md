# M01DropReturnClause — round 59 mutation receipt

Axes: operability and calibration. Target: frozen C1-r59 leg-outcome binding predicate; mutation replaces `returns_ok[label] = frame.get("returned") is True` with `returns_ok[label] = True`, causing checker to ignore the `run` return bool.

Expected detector: frozen C1 counter rejects the mutant (exit 1); pristine/restored counter passes (exit 0).

Commands (executed from Python driver; explicit lane and scratch paths):
```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --work /fast/scratch/hyaku/kama-r59/M01DropReturnClause
# mutated run adds: --checker /fast/scratch/hyaku/kama-r59/M01DropReturnClause/mutated-checker.py
```

Observed outcomes: pristine: exit 0, `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`; mutant: exit 1, `genuine=0/1 benign=0/3 noop_rejected=16/16 errors=0 met=False`; restored: exit 0, `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`. For pristine and restored, genuine and all three benign variants were accepted; all 16 no-op variants rejected. For mutant, genuine and all three benign variants were rejected, all 16 no-ops remained rejected. All stderr outputs were empty.

Verdict: KILLED. The counter fails on the return-bool-ignored mutant. Its failure is not baseline-inconclusive because the pristine detector passed before mutation, and restored detector passed afterward.

Restoration evidence: lane checker was never modified; mutant existed only at the scratch `--checker` path. Pristine checker SHA-256 before probe: `d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d`. Mutated checker SHA-256: `1da8c7eb365ee224bb12606531c29bf901a0bbe9eeabffc1c4f8182fb32b52a5`. Restored run used the unchanged frozen lane checker, and scratch was removed before completion. No installs.
