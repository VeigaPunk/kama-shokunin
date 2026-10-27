# M06DropAssertReturn — round 59, kama, wave 1 (mutation probe)

Axes: operability, calibration. Leaf member; no subagent dispatch. Seat work is a falsification probe, not a judgment.

## Attacked claim / clause
Frozen C1-r59 predicate (`controls/freeze.txt`, sourced on S517): "C1-r59 outcome-binding checker accepts genuine+3/3 benign and rejects 16/16 no-ops, errors=0", specifically the clause: *"`assert_mutant_breaks_detection` must specifically assert the mutant's `missed` observation against `detected` and observe exit 1"* within "each named `run`/mutant leg is accepted only when its own named expected outcome is tied to that leg's actual observed field/value and exit".

## Mutant (one plausible defect, smallest behavior-bearing point)
Isolated scratch copy: `/fast/scratch/hyaku/kama-r59/M06DropAssertReturn/clone` (git clone of kama-shokunin @ HEAD 4a541190; frozen tip aca8d0067ea25627c5015c2193c843965148bc8e present, blob of target identical to clone working bytes).

Single edit to `tests/round58-battery-variants/genuine.py` — remove the outcome binding of the mutant-assert leg **only** (all other legs byte-identical):

```diff
-        results.append(assert_mutant_breaks_detection(
-            mutant, OUT / "m-drop-ldaudit-target-fails.out"))
+        assert_mutant_breaks_detection(
+            mutant, OUT / "m-drop-ldaudit-target-fails.out")
```

Distinct from enumerated `N14-ignore-mutant-result` (which substitutes `results.append(True)`) and `N07-mutant-assert-noop` (which stubs the function to `return True`): here the leg still runs and returns, but its returned outcome is never bound into the battery's `all(results)` gate. Committed in the scratch clone only: tip `ab63e8dd578c8adccfbbd97e8e8ac17c8e179c15`, blob `76aa6ee13d9feabb08d62ff6289f98abbcff7aa7`. No lane tree, sibling, or fleet bytes touched.

## Detector runs (same bounded detector, exact commands)
`TMPDIR=<scratch>/work python3 <clone>/tools/round59-c1-counter.py --repo <clone> --tip <tip> --work <scratch>/work` (frozen C1 command form, frozen tip on pristine/restored runs).

1. **Pristine baseline** (`--tip aca8d0067…`): exit **0**; `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`; `detail: genuine accept exit=0`; all 16 no-ops `reject exit=1`. Baseline passed → probe is conclusive (not inconclusive).
2. **Mutated** (`--tip ab63e8dd578c8adccfbbd97e8e8ac17c8e179c15`): exit **1**; `genuine=0/1 benign=3/3 noop_rejected=16/16 errors=0 met=False`; `detail: genuine reject exit=1`; every enumerated benign/no-op verdict unchanged (3/3 accept, 16/16 reject).
3. **Restored** (`--tip aca8d0067…` after byte restoration): exit **0**; `met=True` — identical to baseline.

Kill mechanism (observed, from checker verdict logic): the checker fault-injects label `mutant-assert` (flips the leg's observed `missed`→`detected` so `assert_mutant_breaks_detection` returns False) and requires the battery exit to flip to 1. With the binding dropped, `all(results)` over the remaining legs stays True → exit 0 → fault case fails → checker rejects the genuine fixture → counter `genuine=0/1` → `met=False`.

## Verdict
**KILLED.** The C1 counter rejects the drop-mutant-assert-outcome-binding mutant; the frozen claim's coverage holds for this defect on this clause. No surviving-mutant coverage finding. No score or discernment claim is made (S517/S518 external spot-check remains unrecorded and untouched).

## Hashes
| state | sha256(genuine.py) | git blob |
|---|---|---|
| before (pristine) | `69b77a6a64f2667757842c2471ddc256d12ceb5ccca6df0a57b88bbe17ab51c5` | `1f4ebff0a62cc9e09d90c6a2f44b613c7027235b` |
| after mutation | `1cacd8006dba30dd568dfd3bb6f1dbadf90488a264614313caf3173a253cb6b0` | `76aa6ee13d9feabb08d62ff6289f98abbcff7aa7` |
| after restoration | `69b77a6a64f2667757842c2471ddc256d12ceb5ccca6df0a57b88bbe17ab51c5` | `1f4ebff0a62cc9e09d90c6a2f44b613c7027235b` |

Restoration is byte-exact (sha256 and blob id match pristine) and was verified before scratch removal, even though the detector never failed.

## Bounds / tooling record
- Lane tree read-only; the only lane write is this report at `.ufo/waves/round-59/w1/out/M06DropAssertReturn.md`. Fleet root and shokuknow untouched; no commits/push outside the disposable scratch clone.
- Scratch `/fast/scratch/hyaku/kama-r59/M06DropAssertReturn/` with `TMPDIR` set explicitly on every detector run; `/tmp` unused; scratch removed after evidence capture. Fixture commits used explicit `git -C <dir>` with toplevel asserted equal to that dir; identity only via `-c` inside the scratch clone.
- No tools installed or updated (python3/git preexisting); nothing to record per RULES.md channel order.
- Single-mutant scope per role: this probe covers one defect class (mutant-assert outcome binding dropped); other clauses were not attacked here.
