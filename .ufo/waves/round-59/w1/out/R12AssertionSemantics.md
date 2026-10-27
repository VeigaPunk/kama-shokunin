# R12AssertionSemantics — Round 59 falsification

Axes: operability and calibration (calibration 7; no score/admission claim). Scope: mutant-assert expected-observed-exit behavior in frozen C1 claim.

## Result
The frozen C1 counter passed at the assigned tip and rejected the mutant-assert no-op control. This supports the narrow assertion that the detector responds to a no-op assertion; it does not establish that independently flipping each assertion predicate term changes the detector, so that requested term-by-term sensitivity remains unproven.

Command (with scratch/TMPDIR explicitly set):
`python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --work /fast/scratch/hyaku/kama-r59/R12AssertionSemantics`

Observed exit: 0. Output: `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`; specifically `N07-mutant-assert-noop reject exit=1`. The observed genuine predicate is described by the frozen counter as accepting genuine + 3/3 benign and rejecting 16/16 no-ops.

Relevant fixture evidence: `tests/round58-battery-variants/N07-mutant-assert-noop.py` returns `True` immediately from `assert_mutant_breaks_detection`, bypassing the subprocess/result checks; the control counter still reports that fixture rejected with exit 1. The genuine battery's assertion at lines 52-60 invokes the counter with `--expect detected` and defines success as `returncode == 1` AND observed `ld_audit == missed`; thus the expected/missed/exit-1 contract is explicitly present in the committed source.

## Sensitivity gap
No separate experiments were run flipping only the expected field comparison, only the observed field comparison, or only the exit comparison. The aggregate N07 control proves rejection of the combined no-op mutation, not which detector term caused rejection. Per assignment, no assertion-term sensitivity claim is made. No external S517/S518 spot-check or discernment progress is claimed.

No installs. Fleet-root HEAD observed during inspection was `0f99f606120d0c884656c6e7a290f0e8f33c2181`, differing from assignment's stated `3f3dd97345ef1aedfdaec818c9e58675d4f41e3f`; this seat did not run C2 or use fleet state as evidence.
