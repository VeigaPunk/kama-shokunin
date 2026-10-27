# X06NoopSubsetC — Round 59 C1 no-op subset C (N12–N16)

**Axes:** operability; calibration (assigned lowest: 7). Advisory executor: this is a falsification, not a judge verdict. Item: rerun N12–N16 variants; verify intended mutation by diff and record exit.

## Attacked claim / clause

Frozen C1-r59 predicate (`controls/freeze.txt` lines 5–8), negative-control clause: a leg that "discards its result, reuses another leg's result/label, swaps `--expect`, emits a decoy `--counter`, or routes its argv to `python3 other-script --counter` **must not meet**."

Concretely attacked: `tools/round59-c1-counter.py` summary `noop_rejected=16/16 errors=0 met=True` at the frozen tip — for the five round-59 variants `N12`–`N16`. Kill rule applied: any of these controls accepted → claim not met.

## Frozen inputs actually used

- Tip: `git -C kama-shokunin rev-parse 'aca8d0067ea25627c5015c2193c843965148bc8e^{commit}'` → `aca8d0067ea25627c5015c2193c843965148bc8e` (exit 0).
- Checker bytes taken from that tip, not from the working tree: `git show aca8d006…:tools/round59-battery-outcome-check.py`, sha256 `d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d`.
- Genuine battery: `tests/round58-battery-variants/genuine.py`; variants: `tests/round59-battery-variants/N1{2..6}-*.py`. All exist at the frozen tip (`git ls-tree` exit 0).
- No target, counter, kill rule, or fixture was altered after seeing results. No installs.

## Method (isolated per-variant fixture, explicit git -C)

Driver: `/fast/scratch/hyaku/kama-r59/X06NoopSubsetC/rerun.sh` (scratch only). For each case:

```sh
TIP=aca8d0067ea25627c5015c2193c843965148bc8e
D=/fast/scratch/hyaku/kama-r59/X06NoopSubsetC/fx/<case>
# materialize at TIP: preregistration.json, round56-env-leg-test.py,
# round54-replay-code-audit.py, round56-replay-code-audit.py,
# and the case's battery as tools/round56-env-leg-battery.py
git -C "$D" init -q && git -C "$D" add -A
test "$(git -C "$D" rev-parse --show-toplevel)" = "$(realpath "$D")"   # asserted true every case
git -C "$D" -c user.name=kama-r59-x06 -c user.email=kama-r59@invalid commit -qm fixture
TMPDIR=/fast/scratch/hyaku/kama-r59/X06NoopSubsetC/tmp \
  python3 /fast/scratch/hyaku/kama-r59/X06NoopSubsetC/checker-frozen.py --repo "$D" --tip HEAD --out …/<case>.out
```

Toplevel assertions recorded per case in `run.log`; commits: genuine `1170638e…`, N12 `01b9b0fe…`, N13 `f4915ed0…`, N14 `bc24f951…`, N15 `b0caec3b…`, N16 `2ebd5901…` (each inside its own fixture D; no throwaway identity outside D).

## Results — recorded exits

| Case | Intended | Checker exit | Observed verdict | Decisive sub-check |
|---|---|---|---|---|
| genuine | accept | **0** | `runs=5 passed=5/5 errors=0 met=True` | all four labels return True at baseline |
| N12-ignore-leg-result | reject | **1** | `passed=4/5 met=False` | fault `round56-counter`: top-level `exit=0` (required 1); run frame did return False but result was discarded |
| N13-wrong-leg-expected | reject | **1** | `passed=0/5 met=False` | baseline `exit=1` and `round56-counter returned_true=false`: swapped `--expect` breaks its own detected leg |
| N14-ignore-mutant-result | reject | **1** | `passed=4/5 met=False` | fault `mutant-assert`: top-level `exit=0` (required 1); assert result replaced by `results.append(True)` |
| N15-duplicate-leg-label | reject | **1** | `passed=0/5 met=False` | `labels=false`; `round56-counter` frame absent (call=false), label collides on `base-old-counter` |
| N16-decoy-counter-call | reject | **1** | `passed=0/5 met=False` | `call=false` for all three `run` legs: two subprocess argv per leg (`calls_ok` requires exactly one) |

Full stdout for each case retained as `N1?.stdout` / `genuine.stdout`; driver exit 0; all stderr empty.

## Intended-mutation verification by diff

`diff -u` of each variant against the committed genuine battery at the same tip. Each is exactly **one hunk**:

```diff
# N12-ignore-leg-result  (hunks=1)
-    results.append(run("round56-counter", NEW, "detected", OUT / "build-c1.out"))
+    run("round56-counter", NEW, "detected", OUT / "build-c1.out")

# N13-wrong-leg-expected  (hunks=1)
-    results.append(run("round56-counter", NEW, "detected", OUT / "build-c1.out"))
+    results.append(run("round56-counter", NEW, "missed", OUT / "build-c1.out"))

# N14-ignore-mutant-result  (hunks=1)
-        results.append(assert_mutant_breaks_detection(
-            mutant, OUT / "m-drop-ldaudit-target-fails.out"))
+        assert_mutant_breaks_detection(mutant, OUT / "m-drop-ldaudit-target-fails.out")
+        results.append(True)

# N15-duplicate-leg-label  (hunks=1)
-    results.append(run("round56-counter", NEW, "detected", OUT / "build-c1.out"))
+    results.append(run("base-old-counter", NEW, "detected", OUT / "build-c1.out"))

# N16-decoy-counter-call  (hunks=1)
     p = subprocess.run(["python3", str(TEST), "--counter", str(counter), "--expect", expected],
                        capture_output=True, text=True)
+    subprocess.run(["python3", "other-script", "--counter", str(counter), "--expect", expected])
```

Raw diffs retained as `N1?.diff`. Behavior matching: each rejection's decisive sub-check corresponds to the mutation (discarded return → unpropagated fault; swapped expect → own leg false; ignored assert → unpropagated mutant fault; duplicate label → missing label; extra argv → call-count failure).

## Frozen-counter cross-check

```sh
TMPDIR=/fast/scratch/hyaku/kama-r59/X06NoopSubsetC/tmp \
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip aca8d0067ea25627c5015c2193c843965148bc8e \
  --work /fast/scratch/hyaku/kama-r59/X06NoopSubsetC/c1work \
  --out …/c1-counter.out
```

Exit **0**; `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`; detail lines `N12…N16 reject exit=1`. Retained as `c1-counter.out` (sha256 `84856a06…`).

## What this establishes — and its limits

- Within this harness at the frozen tip, all five subset-C mutants are rejected and the genuine battery is accepted; the rejections are attributable to the intended mutations, verified by single-hunk diffs and by the failing sub-check matching each mutation.
- **Bound:** the checker intercepts `subprocess.run` and synthesizes `ld_audit` from the counter source's `BAD_ENV` declaration (`result_for`, `fake_run`); these rejections are harness-level fault-injection results, not observed real-process output. N13 is rejected already at baseline, so its rejection proves a broken positive control as much as fault sensitivity. The decoy call in N16 is intercepted, not actually spawned.
- No claim beyond N12–N16 at this tip; no unenumerated-mutant coverage claimed; no external S517/S518 spot-check recorded, so no discernment progress claimed.

## Operability / calibration notes

- Per-variant rerun is deterministic and cheap: 6 fixtures, driver wall time 1.34 s; the frozen 21-fixture counter run 4.25 s.
- Checker identity must be pinned by blob at the measured tip: the lane working tree (HEAD `4a541190…`) is newer than the measured tip, so materializing all inputs from `aca8d006…` avoids drift.
- N16's `python3 other-script` decoy cannot be distinguished by label alone if `calls_ok` ever loosened; the current exactly-one-call rule is the only thing rejecting it here.

## Files changed

- Wrote only: `.ufo/waves/round-59/w1/out/X06NoopSubsetC.md` (this report) and evidence artifacts under `.ufo/waves/round-59/w1/out/X06NoopSubsetC/` (per-case `.stdout`/`.diff`, `c1-counter.out`, `run.log`, `SHA256SUMS`).
- No lane source edits, no commits/push, no installs, no writes outside the seat output dir and scratch (`/fast/scratch/hyaku/kama-r59/X06NoopSubsetC`, removed before yield).
