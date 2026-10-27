# R16CheckerTamper — C1 checker mutation findings

Axes: operability; calibration (lowest assigned axis). Scope: frozen C1 tip `aca8d0067ea25627c5015c2193c843965148bc8e`; claim tested is the frozen leg-specific outcome binding predicate in `controls/freeze.txt`.

## Receipts

Baseline command:

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --work /fast/scratch/hyaku/kama-r59/R16CheckerTamper
```

Exit 0: `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`.

For each mutation below, a scratch-only copy of the checker was passed using the counter's `--checker` option; each run used the same frozen lane/tip and work root. Exit code and counter summary are stated. These are checker-condition mutations, not changes to frozen fixtures or counter rules.

| Condition mutated | Exact mutation | Counter result | Assessment |
|---|---|---|---|
| label set | Replace `names_ok = set(by_label) == expected_labels and len(frames) == len(expected_labels)` with `names_ok = True` | exit 0; `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True` | **Survives.** Label-set/duplicate-frame condition is not load-bearing against this fixture set. |
| call count | Remove `len(calls) == 1` from the per-label call predicate, retaining `--counter` and `--expect` checks | exit 1; `noop_rejected=15/16`, `met=False`; `N16-decoy-counter-call accept exit=0` | Killed by decoy-counter-call control. |
| return result | Replace `returns_ok[label] = frame.get("returned") is True` with `returns_ok[label] = True` | exit 1; genuine rejected; `met=False` | Killed by genuine expected-return check/fault cases. |
| fault propagation | Remove the requirement that the faulted leg's return be false (`and not returns_ok.get(fault, False)` → `and True`) | exit 0; `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True` | **Survives.** Frozen controls do not make this specific faulted-leg return assertion load-bearing. |
| timeout | Change checker subprocess timeout from 60 seconds to 0.000001 seconds | exit 1; genuine rejected; `met=False` | Killed; this deliberately immediate timeout is not evidence about timeout boundary adequacy. |

Observed mutant fixture exits in the call-count case included `N16-decoy-counter-call accept exit=0`; all other shown N12–N16 controls rejected except as indicated. No checker mutation altered the frozen counter or its fixture set.

## Residual risk / verification gaps

The label-set survivor means duplicate/missing/extra returned labels are not independently discriminated by the frozen battery as presently enumerated, despite the claim requiring exact per-leg labels. The fault-propagation survivor specifically concerns the checker assertion that the faulted leg did not return true; report it as a checker calibration gap, not proof of a runtime defect. Timeout was tested only with an effectively zero timeout; no boundary or overlong-child case was exercised. No external S517/S518 spot-check is recorded or claimed. No source changes, installs, or commits were made.
