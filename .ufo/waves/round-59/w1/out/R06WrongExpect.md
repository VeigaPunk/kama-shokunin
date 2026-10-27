# R06WrongExpect — round 59 kama — seat R06WrongExpect (round56 positive-control wrong-expect falsification)

Axes: operability (C1) and calibration (C2). This seat attacks the C1 operability claim's
positive-control leg: the checker must reject a battery whose positive-control leg asserts
the wrong expected value, and the counter must not count that mismatched flag as correct.
Calibration counter (C2) is not this seat's item and was not exercised.

## 0. Frozen inputs verified before any run

- Lane working-copy blobs equal the frozen measured tips, so invoking `tools/*.py` from the
  working copy executes the frozen bytes:
  - `tools/round59-c1-counter.py` = `a766c871255712f23517a2e4e846ab2ec35e6224` at lane HEAD
    `4a541190b6d494a4e99116249632e99aab80adcc` and at frozen C1 tip `aca8d0067ea25627c5015c2193c843965148bc8e`.
  - `tools/round59-battery-outcome-check.py` = `64e91f64c05f057f7ae97c50b784aca642f63e59` at both.
  - `tools/round59-c2-counter.py` = `3b80c25845236348a17260883ab60a6093f2ec6c` at lane HEAD and at
    frozen C2 tip `2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35` (not run).
- Frozen baseline control `.ufo/waves/round-59/controls/c1-candidate-final.out` (exit 0,
  `met=True`, tip aca8d00, N13 rejected at exit 1).

## 1. The mutation (exact, single line)

Target: `tools/round56-env-leg-battery.py` line 71 — leg `round56-counter`, which the battery's
own ROSTER designates `"designation": "positive-control", "expected": "detected"`.

```
--- tools/round56-env-leg-battery.py @ aca8d0067ea25627c5015c2193c843965148bc8e (pristine)
+++ tools/round56-env-leg-battery.py (wrong-expect mutation)
@@ -71 +71 @@
-    results.append(run("round56-counter", NEW, "detected", OUT / "build-c1.out"))
+    results.append(run("round56-counter", NEW, "missed", OUT / "build-c1.out"))
```

- Only the expected value changed: one line, one token (`detected` → `missed`). ROSTER, leg
  labels, counter paths and every other byte unchanged (evidence: R06WrongExpect-evidence/mutation.diff).
- The independently constructed mutant is **byte-identical** to the frozen control
  `tests/round59-battery-variants/N13-wrong-leg-expected.py` (`diff` empty; command in §3 step 5).
  The mutation class is canonical; this seat adds the checker-level attribution the counter alone
  does not record.
- Purity check: frozen `tests/round58-battery-variants/genuine.py` was verified byte-identical to
  the pristine battery before any slot substitution (R06WrongExpect-evidence/genuine-eq-pristine.txt).

## 2. Verdicts (every verdict names the attacked clause; commands + exits in §3)

- **V1 — "frozen checker rejects genuine/benign appropriately": MET.** The checker accepts the
  genuine battery (exit 0, 5/5 rows pass, all four legs `returned_true`, every single-leg fault
  propagates to exit 1 with exactly the faulted leg returning False) and rejects the wrong-expect
  mutant (exit 1, 0/5 rows pass). No collateral: benign 3/3 accept and 16/16 no-op reject are
  unchanged in both counter runs (V4 vs V3).
- **V2 — "counter does not count mismatched flag as correct": MET.** With the mismatched-expectation
  battery occupying the genuine slot of an otherwise-frozen tip, the frozen C1 counter reports
  `genuine=0/1 ... met=False`, exit 1, and the detail line is `detail: genuine reject exit=1`. The
  verdict derives from the checker's exit (0→accept, 1→reject), so a battery whose positive-control
  leg asserts an unmet expectation lands in the reject bucket, never in the accept tally; the kill
  rule "any genuine leg rejected -> claim not met" fires.

## 3. Evidence — exact commands, outputs, exits

All scratch under `/fast/scratch/hyaku/kama-r59/R06WrongExpect/` (TMPDIR set explicitly; fixture
git commands used `git -C "$D"` with `rev-parse --show-toplevel` asserted equal to `$D` before each
commit; identity `kama-r59-r06 <kama-r59-r06@invalid>` only inside those fixture dirs). Raw outputs
copied to `.ufo/waves/round-59/w1/out/R06WrongExpect-evidence/` (paths below relative to lane root).

1. Build wrong-expect fixture `8b401c63c6916ac91996d54ecf423fd4aa8b6314` (frozen tree, battery
   mutated), genuine accept fixture `7bc23b185edd3d2b024a04fad2f313a6973e6b40`, slot repo
   `5b05aed24e2fb89b056178029f7a90ea451f5ccb` (frozen tip tree with exactly one blob changed:
   `tests/round58-battery-variants/genuine.py` 1f4ebff0→96eb259c; `git ls-tree -r` diff of 32791
   entries shows only that line — command `diff <(git -C lane ls-tree -r aca8d00…) <(git -C slot ls-tree -r HEAD)`
   output at R06WrongExpect-evidence/tips.txt context, delta quoted in §1).
2. `python3 tools/round59-battery-outcome-check.py --repo <wrong-expect fixture> --tip HEAD` →
   **exit 1**, `runs=5 passed=0/5 errors=0 met=False`. Baseline row: `labels=true`, every leg
   `call=true` (`--counter` and `--expect` still in argv), `round56-counter returned_true=false`,
   other three legs `returned_true=true`, battery `exit=1`. Diagnostic row: with
   `--fault round56-counter` (observation inverted to `missed`) the mutated leg returns True and
   the battery exits 0 — the leg only passes when the observed world is wrong, confirming the
   defect is the expectation binding, not observation. R06WrongExpect-evidence/checker-wrongexpect.out.
3. `python3 tools/round59-battery-outcome-check.py --repo <genuine fixture> --tip HEAD` →
   **exit 0**, `runs=5 passed=5/5 errors=0 met=True`; each fault row exit 1 with exactly the
   faulted leg `returned_true=false`. R06WrongExpect-evidence/checker-genuine.out.
4. `python3 tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --work <scratch>` →
   **exit 0**, `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`; output
   **byte-identical** to frozen `.ufo/waves/round-59/controls/c1-candidate-final.out`
   (`diff` empty). R06WrongExpect-evidence/c1-base-repro.out.
5. `python3 tools/round59-c1-counter.py --repo <slot repo> --tip 5b05aed24e2fb89b056178029f7a90ea451f5ccb --work <scratch>` →
   **exit 1**, `genuine=0/1 benign=3/3 noop_rejected=16/16 errors=0 met=False`,
   `detail: genuine reject exit=1`, benign and all 16 no-ops identical to run 4.
   R06WrongExpect-evidence/c1-wrongexpect-genuine-slot.out.
6. `diff <(git -C <slot repo> show HEAD:tests/round58-battery-variants/genuine.py) <(git -C lane show HEAD:tests/round59-battery-variants/N13-wrong-leg-expected.py)` →
   empty (`BYTE_IDENTICAL_TO_N13`).

## 4. Findings by severity

- **No defect found in the frozen checker or counter.** Both behaved exactly per the frozen
  predicate on the wrong-expect mutation and on all unchanged controls.
- Note (informational): the checker's fault-injection rows assume a correct baseline; on the
  mutant, the `--fault round56-counter` row is unsatisfiable (`passed=false`) because the inverted
  observation coincidentally satisfies the mutated expectation. This does not weaken V1/V2 —
  rejection is already forced by the baseline row — but anyone reading fault rows of a rejected
  battery should attribute via the baseline row first.
- Note (informational): this seat's mutation is byte-identical to frozen control N13, so the
  frozen counter battery already covers this class; the new evidence here is the checker-level
  per-leg attribution (V1) and the accept-control contrast (V3 vs V4).

## 5. Residual risk and verification gaps

- C2 calibration counter (tip 2c7443ab) not exercised — different axis, different seat.
- External S517/S518 spot-check remains unrecorded; no discernment progress is claimed here.
- Lane working copy carries 45 dirty entries (other seats' outputs); irrelevant to these runs
  because every executed tool blob was verified identical to the frozen measured tips and all
  fixture content came from committed blobs (`git show tip:path`).
- No tool installs were needed (host `python3` only); nothing to record under the tooling
  directive. pacman paused; no packages touched.
- Scratch `/fast/scratch/hyaku/kama-r59/R06WrongExpect/` removed before yield, per bounds.

Report: .ufo/waves/round-59/w1/out/R06WrongExpect.md
Evidence: .ufo/waves/round-59/w1/out/R06WrongExpect-evidence/mutation.diff
Evidence: .ufo/waves/round-59/w1/out/R06WrongExpect-evidence/genuine-eq-pristine.txt
Evidence: .ufo/waves/round-59/w1/out/R06WrongExpect-evidence/checker-wrongexpect.out
Evidence: .ufo/waves/round-59/w1/out/R06WrongExpect-evidence/checker-genuine.out
Evidence: .ufo/waves/round-59/w1/out/R06WrongExpect-evidence/c1-base-repro.out
Evidence: .ufo/waves/round-59/w1/out/R06WrongExpect-evidence/c1-wrongexpect-genuine-slot.out
Evidence: .ufo/waves/round-59/w1/out/R06WrongExpect-evidence/tips.txt
