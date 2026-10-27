# M11CatchExceptions — round 59, wave 1 (mutation probe)

- Seat: M11CatchExceptions (mutation-tester, leaf; no subagents used)
- Item: "Mutate exception branch to report success/exit zero; use crashing battery control."
- Axes: operability, calibration. Advisory only; no claim admitted or narrowed by this seat.
- Attacked claim/clause: C1-r59 (frozen in `controls/freeze.txt`, base 8f7f58cd). The checker clause that a battery crash during evaluation must surface as an eval error and fail the fixture — the C1 kill rule "any eval error -> claim not met" depends on it. Behavior-bearing point: `tools/round59-battery-outcome-check.py`, `child()`'s `except BaseException` branch (lines 125-126).
- Tooling: host python 3.14.8. **No installs or updates performed** (pacman paused; nothing needed).

## Mutant (scratch copy only; lane bytes never modified)

File: `tools/round59-battery-outcome-check.py` @ tip `aca8d0067ea25627c5015c2193c843965148bc8e`

```diff
     except BaseException as exc:
-        return {"error": f"{type(exc).__name__}: {exc}", "exit": 2, "frames": frames}
+        pass
```

Semantics: a non-`SystemExit` battery crash is swallowed; the child falls through to the success path, writes the outcome JSON with `exit_code` unchanged (0) and returns exit 0 — the exception branch reports success/exit zero. `child_main` then returns 0, so the missing-outcome-file guard never fires. Mutant sha256 `2fd8c320d27cba59e6e953b106fd11838dbed7ba6a988643fb727c6a22c66cbb`; pristine sha256 `d7deae2f3d0d45ce7fbe06294ce67890c93bb02a1500911ed32a25d453dadc0d`.

## Detectors (same bounded behavioral detector on pristine, mutated, and pristine-restored bytes)

1. Frozen enumerated C1 counter: `TMPDIR=<seat-scratch>/tmp python3 tools/round59-c1-counter.py --repo <lane> --tip aca8d0067ea25627c5015c2193c843965148bc8e --work <seat-scratch>/work/{pristine|mutant} [--checker <mutant copy>]`
2. Crashing battery control: disposable scratch fixture `crash-fixture` (git `b36fc4d167eb9dae7ab0688a5b1b00a391202c85`, toplevel verified before commit, throwaway identity used only inside the fixture dir). Battery = frozen `tests/round58-battery-variants/genuine.py` blob with only its tail changed to raise a non-`SystemExit` exception when all legs pass:

```diff
-    return 0 if all(results) else 1
+    if all(results):
+        raise RuntimeError("crash-on-success control M11CatchExceptions")
+    return 1
```

All four genuine legs run unmodified first, so frames/labels/calls are perfect; only the final crash distinguishes. Detector invocation: `TMPDIR=<seat-scratch>/tmp python3 <checker> --repo <fixture> --tip HEAD`.

## Outputs and verdicts

Detector 1 (enumerated controls) — pristine: `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`, exit **0** (identical verdict lines to frozen `controls/c1-candidate-final.out`). Mutant: `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`, exit **0**, per-fixture verdicts byte-identical to pristine → **SURVIVED** the frozen enumerated control set.

Detector 2 (crashing battery control) — pristine: `runs=5 passed=4/5 errors=1 met=False`, exit **1**; baseline run recorded `{"error": "child failed", "exit": 2, "passed": false}` (crash surfaced as eval error → fixture rejected). Mutant: `runs=5 passed=5/5 errors=0 met=True`, exit **0**; baseline recorded `{"error": null, "exit": 0, "passed": true}` with all four legs `returned_true` (crash masked as success → fixture **accepted**). All four one-leg fault runs behaved identically under both checkers (exit 1, faulted leg `returned_true: false`), so the crash path is the only flipped behavior → **KILLED** by the crashing battery control.

## Finding (coverage, not contract change)

The frozen enumerated fixtures never reach the checker's `except BaseException` branch: N11-try-else's `RuntimeError` is caught battery-side before any leg runs, and every other `raise` in the fixture set is `SystemExit`, handled by the inner `except SystemExit` — never the eval-error branch. A checker that reports crashes as success/exit zero therefore passes the C1 counter unchanged, and the claim's own kill rule ("any eval error") would silently stop firing on crash-type deviations. If a future wave wants this branch covered, a crash-on-success battery fixture (as constructed above, added only before data per the freeze rule) is the minimal enumerated control; adding it is outside this seat's authority and was not done.

## Restoration and bounds evidence

- Lane tree never written: `round59-battery-outcome-check.py` sha256 `d7deae2f…`, `round59-c1-counter.py` sha256 `c1e75c21016a6763a25c7c80c10963e34072aa3690da5b3ea9a259cedcaf3c3a`, `genuine.py` sha256 `69b77a6a…` — identical before and after all runs (no in-place mutation ever existed; the mutant lived only in scratch).
- All scratch under `/fast/scratch/hyaku/kama-r59/M11CatchExceptions/` with `TMPDIR` set explicitly on every invocation; no `/tmp` use; scratch tree removed before yield (disposable by construction — fixture commit included).
- No fleet-root tracked files, no PATH dirs, no sibling lanes touched; only this report written inside the lane tree.
