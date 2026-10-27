# X04NoopSubsetA — round 59, wave w1 (kama)

Seat: leaf executor, advisory only. Axes: operability (8) and calibration (7, lowest assigned);
this item measures C1 operability only — no score, no discernment progress claimed.
L1 planner seat is not mine; nothing here judges the claim.

Frozen inputs (read-only, unmodified):
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-59/controls/freeze.txt`
(base `8f7f58cd`, control commit `5d957d24`). C1 measured tip `aca8d0067ea25627c5015c2193c843965148bc8e`.
Lane `/home/vgpnk/Projects/shokunin/kama-shokunin` was not written: only this report file.

## Assignment and what was actually run

Assigned: rerun the N01–N05 no-op variants of the round-56 battery against the round-59
outcome-binding checker and the C1 counter, one fixture tree per variant, exact statuses.

Executed:

- Checker: `python3 <lane>/tools/round59-battery-outcome-check.py --repo <fixture> --tip HEAD --out <scratch>/evidence/<variant>.out`
  (one dedicated git fixture tree per variant, committed `HEAD`, all other inputs read from the
  measured tip `aca8d006`).
- Counter: `python3 tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --work /fast/scratch/hyaku/kama-r59/X04NoopSubsetA/c1work`
- Environment: `TMPDIR=/fast/scratch/hyaku/kama-r59/X04NoopSubsetA/tmp` for every child;
  scratch removed before yield. Python 3.14.8, git 2.56.0. No installs or upgrades (none needed).
- Fixture discipline: each tree built at `/fast/scratch/hyaku/kama-r59/X04NoopSubsetA/fixture/<variant>`,
  `git -C "$D" init -q`, blobs via `git -C "$lane" show <tip>:<path>`, `git -C "$D" add -A`,
  then `[ "$(readlink -f "$(git -C "$D" rev-parse --show-toplevel)")" = "$(readlink -f "$D")" ]`
  asserted before `git -C "$D" -c user.name=kama-r59-x04 -c user.email=kama-r59-x04@invalid commit`.
  Identity was passed per-commit inside `$D` only; no throwaway identity outside the fixture.

Measured artifacts (sha256 of the blob at tip `aca8d006`):

```
d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d  tools/round59-battery-outcome-check.py
c1e75c21016a6763a25c7c80c10963e34072aa3690da5b3ea9a259cedcaf3c3a  tools/round59-c1-counter.py
69b77a6a64f2667757842c2471ddc256d12ceb5ccca6df0a57b88bbe17ab51c5  tools/round56-env-leg-battery.py   (genuine battery)
8df3bd061ef2ccbb79d2a65f1833b94237471ccb6c82c9bca6a7b806dab744e1  tests/round58-battery-variants/N01-calls-removed.py
e21de813b6557fbf7c4e63d9bb562e7316eb2c9da22e1f2436e4f256578c381c  tests/round58-battery-variants/N02-if-false.py
952fa3c9d8bf65bc6070ef1e134b45a45720fb6cc1155a9974e9aa578f851b76  tests/round58-battery-variants/N03-unused-function.py
fc0b15326fc3b0fb1a7bcb995b376cccaa0e7f507f37e7f9372175675f42ed0b  tests/round58-battery-variants/N04-early-return.py
c2ec719a7dc8237e0343c772566f4b13826397b07b1f28a345a0b23c9c7e4088  tests/round58-battery-variants/N05-env-guard.py
8fd240a6442120d060830f79009ef2b7d6a37a40b0a4024567ebc2a457bedced  tests/round59-battery-variants/N12-ignore-leg-result.py   (contrast probe only)
```

## Exact statuses — checker, one fixture tree per variant

Attacked clause: C1-r59, “any outcome-unbound control accepted … -> claim not met”. Each
tree substitutes only `tools/round56-env-leg-battery.py`; prereg and the three side files are
the measured-tip blobs. `met=False` = the checker rejected that tree (exit 1 = reject).

| variant | fixture HEAD | checker exit | runs passed | labels | met | per-leg returned_true |
|---|---|---|---|---|---|---|
| genuine | `18380533948585a933eb6a12f330d968efcecb2b` | 0 (accept) | 5/5 | true | True | all 4 legs true |
| N01-calls-removed | `7c2378cdddfc31fa6ffc27f01df30664811f9252` | 1 (reject) | 0/5 | false | False | all false |
| N02-if-false | `c806be93a48991bb3a3bd55fa05475bd404ddc9d` | 1 (reject) | 0/5 | false | False | all false |
| N03-unused-function | `bd3e6d4adbdb7a96c3c825f5ca40f412921128ab` | 1 (reject) | 0/5 | false | False | all false |
| N04-early-return | `fd57b1d715e9ddfd058c3736172f2baa9d69f324` | 1 (reject) | 0/5 | false | False | all false |
| N05-env-guard | `9a9496630cb139d6d830b69920df6d6112576a91` | 1 (reject) | 0/5 | false | False | all false |

Exit codes are the checker's own return value (`0` accept / `1` reject / `2` could-not-evaluate).
No `could-not-evaluate` occurred and stderr was empty (0 bytes) for all six trees.

Exact stdout for a representative no-op (N01; N02–N05 are byte-identical apart from `tip=`):

```
tip=7c2378cdddfc31fa6ffc27f01df30664811f9252
predicate=C1-r59 each named leg returns a bound expected outcome; one-leg faults propagate
runs=5 passed=0/5 errors=0 met=False
{"error": null, "exit": 0, "fault": "baseline", "labels": false, "passed": false, "per_leg": {"base-old-counter": {"call": false, "returned_true": false}, "m-drop-ldaudit": {"call": false, "returned_true": false}, "mutant-assert": {"call": false, "returned_true": false}, "round56-counter": {"call": false, "returned_true": false}}}
… (all five fault rows identical: labels=false, passed=false, exit=0)
```

Genuine tree stdout (positive control, truncated to the discriminating rows):

```
tip=18380533948585a933eb6a12f330d968efcecb2b
predicate=C1-r59 each named leg returns a bound expected outcome; one-leg faults propagate
runs=5 passed=5/5 errors=0 met=True
{"error": null, "exit": 0, "fault": "baseline", "labels": true, "passed": true, … "returned_true": true ×4}
{"error": null, "exit": 1, "fault": "base-old-counter", …, "base-old-counter": {"call": true, "returned_true": false}, …}
{"error": null, "exit": 1, "fault": "round56-counter",  …, "round56-counter":  {"call": true, "returned_true": false}, …}
{"error": null, "exit": 1, "fault": "m-drop-ldaudit",    …, "m-drop-ldaudit":    {"call": true, "returned_true": false}, …}
{"error": null, "exit": 1, "fault": "mutant-assert",     …, "mutant-assert":     {"call": true, "returned_true": false}, …}
```

The genuine positive control passing 5/5 in the same harness rules out “harness rejects
everything” as the explanation for the five rejections.

## Exact statuses — C1 counter (measured artifact, one run)

`python3 tools/round59-c1-counter.py --repo <lane> --tip aca8d006… --work <scratch>/c1work` → exit 0

```
tip=aca8d0067ea25627c5015c2193c843965148bc8e
predicate=C1-r59 outcome-binding checker accepts genuine+3/3 benign and rejects 16/16 no-ops, errors=0
genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True
detail: N01-calls-removed reject exit=1
detail: N02-if-false reject exit=1
detail: N03-unused-function reject exit=1
detail: N04-early-return reject exit=1
detail: N05-env-guard reject exit=1
(detail rows for B1–B3 accept and N06–N16 reject also present; all exit=0/1, errors=0)
```

The counter's own N01–N05 verdicts (reject) agree with my independently built fixture trees,
so the subset result is not an artifact of my tree construction.

## Calibration observation (advisory, not a claim adjustment)

All five N01–N05 rejections come from the *same* mechanism: `labels=false` — the checker's
profile never sees a completed `run`/`assert_mutant_breaks_detection` frame with a bound
`--expect`, so `names_ok` fails before any per-leg field comparison. These five controls
therefore demonstrate detection of **structurally absent legs**, not of a leg that keeps its
call and discards the outcome. That the outcome-binding clause itself is exercised is only
shown by the distinct N12-style control.

Secondary contrast probe (explicitly outside the assigned N01–N05 set, run once to size this):
N12-ignore-leg-result fixture `0163de7369791324b6f3485b21786b6c9df7e865`, checker exit 1,
`runs=5 passed=4/5 met=False` — baseline passes (all four labels called, every `run()` returns
True even though one return value is discarded); rejection appears only on the injected
`round56-counter` fault row (`exit: 0`, `passed: false`) because the discarded result cannot
propagate to the battery exit. So N12 is caught by the fault-propagation clause, not by the
per-leg outcome-binding clause.

Consequence for calibration (7, lowest assigned): the cheap subset I own cannot separate
“binding” from “presence”. Uniform `0/5, labels=false` signatures mean these five statuses
carry no discriminating information about outcome-value binding, and any citation of this
subset as evidence for the C1 sentence would overstate it. Reported as measured; the frozen
predicate was not altered and no control was added.

## Risks / limits

- Advisory leaf result; the claim decision belongs to L1/the judge, and no seat consensus is asserted.
- External S517/S518 spot-check is not recorded for this round, so no discernment progress is claimed.
- The checker's `--child` harness virtualizes `pathlib` and `subprocess`; the statuses above describe
  the checker's model of the battery, not a live subprocess run of `round56-env-leg-test.py`
  (that is the checker's designed semantics, not a defect I am asserting).
- Fixture trees and all scratch under `/fast/scratch/hyaku/kama-r59/X04NoopSubsetA/` were removed
  after evidence extraction; their commits were scratch-only and cannot be re-inspected from the lane.
- No blockers.

## Reproduction (scratch-local, deleted after use)

The harness that produced every status above was a single bash driver: per variant it built the
tree, asserted toplevel equality, committed with fixture-local identity, then invoked the checker
with `TMPDIR` set to scratch; it then ran the counter once. Commands and exit codes are quoted
verbatim in the sections above.
