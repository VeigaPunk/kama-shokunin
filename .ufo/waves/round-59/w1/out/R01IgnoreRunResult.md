# R01IgnoreRunResult — C1 return-value dependency

**Axis:** operability (8); calibration (7, lowest assigned). **Claim attacked:** frozen C1-r59 outcome-binding predicate requires each named battery leg's own result to determine its pass/fail; a leg discarding its result must not meet.

## Variant
The frozen measured tip already contains the applicable no-op control, `tests/round59-battery-variants/N12-ignore-leg-result.py`. Its `main()` calls `run("round56-counter", NEW, "detected", OUT / "build-c1.out")` at line 71 without retaining or checking the returned boolean, while preserving the rest of the results list, including the comparator, baseline, and mutant checks. Thus the call's boolean is discarded and the result is not appended to `results`. I used this exact frozen variant; no fixture or counter was changed.

## Command and result

```text
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --work /fast/scratch/hyaku/kama-r59/R01IgnoreRunResult/work
```

`TMPDIR=/fast/scratch/hyaku/kama-r59/R01IgnoreRunResult/tmp`; scratch was removed before yield.

```text
tip=aca8d0067ea25627c5015c2193c843965148bc8e
predicate=C1-r59 outcome-binding checker accepts genuine+3/3 benign and rejects 16/16 no-ops, errors=0
genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True
detail: genuine accept exit=0
detail: B1-rename-comment accept exit=0
detail: B2-helper-leg accept exit=0
detail: B3-concat-labels accept exit=0
detail: N01-calls-removed reject exit=1
detail: N02-if-false reject exit=1
detail: N03-unused-function reject exit=1
detail: N04-early-return reject exit=1
detail: N05-env-guard reject exit=1
detail: N06-run-body-noop reject exit=1
detail: N07-mutant-assert-noop reject exit=1
detail: N08-main-not-invoked reject exit=1
detail: N09-empty-loop reject exit=1
detail: N10-run-rebound reject exit=1
detail: N11-try-else reject exit=1
detail: N12-ignore-leg-result reject exit=1
detail: N13-wrong-leg-expected reject exit=1
detail: N14-ignore-mutant-result reject exit=1
detail: N15-duplicate-leg-label reject exit=1
detail: N16-decoy-counter-call reject exit=1
```

Counter process exit: **0** (`met=True`). The targeted result-discard mutant is **rejected** (checker exit 1), so this control supports the frozen C1 return-value-dependency claim for this variant. This is a scoped falsification result, not a claim of external S517/S518 discernment progress.
