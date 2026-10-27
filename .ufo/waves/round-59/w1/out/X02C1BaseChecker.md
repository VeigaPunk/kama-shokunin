# X02C1BaseChecker — Round 59 C1 falsification (base checker override)

Axes: operability; calibration (assigned lowest: 7). Attacked claim/clause: frozen C1-r59
predicate — "each round-56 battery leg is accepted only when its own named expected outcome is
tied to that leg's actual observed field/value and exit; genuine leg coverage=3/3, enumerated
negative controls fail, 0 evaluation errors", and the before-state that the prior r58 checker
does not cover leg-outcome mutants.

Measured tip: `aca8d0067ea25627c5015c2193c843965148bc8e` (lane HEAD is `4a541190`; the three
artifacts and all variants under test are byte-identical at the tip):

| artifact | sha256 |
|---|---|
| tools/round59-c1-counter.py | c1e75c21016a6763a25c7c80c10963e34072aa3690da5b3ea9a259cedcaf3c3a |
| tools/round59-battery-outcome-check.py | d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d |
| tools/round58-battery-exec-check.py (base) | ce2674c232f8a9b679607a32c49a424aee641e718329f7c63638b1e83d44f925 |
| N12-ignore-leg-result.py | 8fd240a6442120d060830f79009ef2b7d6a37a40b0a4024567ebc2a457bedced |
| N13-wrong-leg-expected.py | d770fd3f88148f0e0718cc05693e637e21a43de510f3d5a164a6b117abb90d6e |
| N14-ignore-mutant-result.py | 958dbff24980aa7c0fcd39efeacbff87b072961d1bb9390ba472aab2980652d4 |
| N15-duplicate-leg-label.py | 3bd4f3c6df5d5f78f1e29e1ef962d69daba1b6da292775a3020a013905eec80c |
| N16-decoy-counter-call.py | 0463c5726d8f0f492f9bc15666a47a1739fc55eb82f451cd200d4544b62931a8 |

## 1. Frozen counter as written (new r59 checker from the tip) — reproduces the pre-data receipt

```sh
TMPDIR=/fast/scratch/hyaku/kama-r59/X02C1BaseChecker python3 \
  /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip aca8d0067ea25627c5015c2193c843965148bc8e \
  --work /fast/scratch/hyaku/kama-r59/X02C1BaseChecker/frozen/work \
  --out /fast/scratch/hyaku/kama-r59/X02C1BaseChecker/frozen/out.txt
```
exit 0 — `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`; genuine accept 0,
B1/B2/B3 accept 0, N01–N16 reject 1 (including N12/N14/N16). Identical to
`.ufo/waves/round-59/controls/c1-candidate-final.out` (met=True) at the same tip, reproduced
independently from scratch fixtures.

## 2. Base checker override (prior r58 checker) — base checker FAILS the target

```sh
TMPDIR=/fast/scratch/hyaku/kama-r59/X02C1BaseChecker python3 \
  /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip aca8d0067ea25627c5015c2193c843965148bc8e \
  --work /fast/scratch/hyaku/kama-r59/X02C1BaseChecker/work-frozen \
  --checker /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round58-battery-exec-check.py
```
exit 1 — `genuine=1/1 benign=3/3 noop_rejected=13/16 errors=0 met=False`. Byte-identical
verdict to `.ufo/waves/round-59/controls/c1-oldchecker-final.out` (met=False).

**Accepted new no-ops under the base r58 checker: N12, N14, N16.**
- `N12-ignore-leg-result` accept exit=0 — `run("round56-counter", ...)` result discarded, so no
  per-leg outcome is asserted.
- `N14-ignore-mutant-result` accept exit=0 — `assert_mutant_breaks_detection(...)` return
  discarded and `results.append(True)` substituted.
- `N16-decoy-counter-call` accept exit=0 — `run` issues a second
  `subprocess.run(["python3", "other-script", "--counter", ..., "--expect", ...])` alongside the
  real call; routed argv to another script is accepted as coverage.

N13 (swapped `--expect`) and N15 (duplicate leg label) were already rejected by the base checker
(exit 1 each: `executed=0 legs=2/3 met=False`), so the base gap is exactly result-discard and
decoy-call, not label/expect identity.

Cause, from `tools/round58-battery-exec-check.py` (base checker, unmodified): the verdict only
requires, per roster label, *some* `run` frame whose argv carried `--counter` and an `--expect`
equal to the preregistered expected value, and that `assert_mutant_breaks_detection` was invoked
with at least one subprocess — never that the leg's return value or the process exit was
consequential (`ran = {f["label"] for f in frames if f["fn"] == "run" and want.get(...) in f.get("expects", [])}`,
`assert_ok = ... all(f["sub"] >= 1 ...)`). That is the r58 `counter-controls-blind-to-mutants` /
`unlisted-noop-survivors` gap, now measured at this tip.

## 3. Direct per-variant confirmation (both checkers, isolated fixtures)

Each variant committed into its own scratch fixture (`git -C "$D" init/add/commit`, toplevel
verified `== $D`, identity passed as `-c` on the commit inside `$D`); checker run as
`python3 <checker> --repo <fixture> --tip HEAD`:

| variant | r58 base | r59 new |
|---|---|---|
| genuine | met=True exit 0 | met=True 5/5 exit 0 |
| N12 | **met=True exit 0** | met=False 4/5 exit 1 (fault `round56-counter` exit 0, `returned_true=false`) |
| N13 | met=False exit 1 | met=False 0/5 exit 1 |
| N14 | **met=True exit 0** | met=False 4/5 exit 1 (fault `mutant-assert` exit 0) |
| N15 | met=False exit 1 | met=False 0/5 exit 1 (`labels:false`) |
| N16 | **met=True exit 0** | met=False 0/5 exit 1 (per-leg `call:false`, two invocations per `run` frame) |
| B1 benign | met=True exit 0 | met=True 5/5 exit 0 |

So the new checker rejects all three base-checker survivors for substantive reasons (fault
propagation / one-call-per-leg), not by accident of fixture naming.

## 4. Operability / fail-closed probes of the frozen counter

- Control commit before the checker landed:
  `--tip 5d957d24` → exit 2, `could-not-evaluate: missing committed blob tools/round59-battery-outcome-check.py`.
  The counter refuses to score before-data state instead of accepting it.
- Missing override: `--checker <absent path>` → exit 2, `could-not-evaluate: checker file absent`.
- Repeat run of §1 gave the same `met=True` receipt (fresh mkdtemp per run, no state reuse).

## 5. Calibration caveat — unlisted split-binding survivors (scratch-only, not lane fixtures)

Private probe variants (built only under `/fast/scratch/hyaku/kama-r59/X02C1BaseChecker/private`,
never written to the lane) drop one conjunct from the battery's own predicate:

- P1-mutant-exit-only: `assert_mutant_breaks_detection` keeps `p.returncode == 1`, drops
  `fields["ld_audit"] == "missed"`.
- P2-mutant-field-only: keeps the field test, drops exit 1.
- P3-run-field-only: `run` keeps the field test, drops `p.returncode == 0`.
- P4-run-exit-only: `run` keeps exit 0, drops the field test.

All four are **accepted** by the new r59 checker (`runs=5 passed=5/5 errors=0 met=True`, exit 0)
and by the r58 base checker (met=True exit 0). The frozen predicate sentence demands both the
leg's `ld_audit` value *and* its declared exit, and specifically the mutant's `missed` against
`detected` *and* exit 1; the checker only establishes that each leg's aggregate return value
flips when the harness flips that leg's observed value. It therefore cannot distinguish a
field∧exit conjunction from either conjunct alone.

Consequence for the claim, stated narrowly: the **enumerated** C1-r59 controls (N12–N16) all
fail under the frozen counter and the enumerated predicate is met at this tip (met=True), but
the sentence's field+exit binding is not demonstrated for unenumerated combinations — the
enumeration is missing split-binding controls. This is an unlisted-survivor calibration finding,
not a frozen-control violation: the kill rule names only the enumerated controls, and none of
them was accepted.

## 6. Bounds

No score increase or capability acquisition is asserted. No external S517/S518 spot-check was
performed or claimed; no discernment progress is claimed. The harness is hermetic (canned
subprocess results, guarded writes), so this measures checker discrimination, not live battery
operability or endpoint health. Frozen target, counters, kill rules and fixtures were not
altered; the lane was read-only; the only write is this report.

Installs/updates: none. Scratch root `/fast/scratch/hyaku/kama-r59/X02C1BaseChecker/` (TMPDIR
set explicitly on every invocation, no `/tmp` use) removed after the receipts above were taken.
