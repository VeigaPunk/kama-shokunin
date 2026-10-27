# R13TimeoutBoundary — Round 59

**Axes:** operability; calibration. **Verdict:** no actionable counter defect found in the tested C1 child timeout/return boundary. This is a scoped falsification, not a judgment/admission.

## Evidence

Target: `tools/round59-c1-counter.py` at `aca8d0067ea25627c5015c2193c843965148bc8e`; the scratch clone resolved to that exact tip. The counter launches the outcome checker once per named case with `timeout=90` (lines 102–105). `subprocess.TimeoutExpired` is recorded as verdict `error`, exit `124` (106–108). Child return codes map strictly as `0 -> accept`, `1 -> reject`, every other code -> `error` (109); `errors` counts these results and `met` requires zero errors alongside the genuine/benign/no-op predicates (111–117). Thus a timeout or abnormal nonzero exit cannot satisfy the frozen predicate.

**Crash probe (executed):** scratch-only checker `/fast/scratch/hyaku/kama-r59/R13TimeoutBoundary/crash.py` contains `sys.exit(2)`. Command:

```sh
export TMPDIR=/fast/scratch/hyaku/kama-r59/R13TimeoutBoundary/tmp
python3 /fast/scratch/hyaku/kama-r59/R13TimeoutBoundary/lane-c1/tools/round59-c1-counter.py --repo /fast/scratch/hyaku/kama-r59/R13TimeoutBoundary/lane-c1 --tip aca8d0067ea25627c5015c2193c843965148bc8e --work /fast/scratch/hyaku/kama-r59/R13TimeoutBoundary/tmp --checker /fast/scratch/hyaku/kama-r59/R13TimeoutBoundary/crash.py
```

Observed: exit **1**; `genuine=0/1 benign=0/3 noop_rejected=0/16 errors=20 met=False`; each of 20 checker invocations was `error exit=2`. This directly tests the external-checker override path and shows a crashed checker is not reported as a pass.

**Timeout probe:** not executed. The timeout classification above is established by the counter's explicit `TimeoutExpired` handler, not represented as a run result. Do not interpret it as an exercised timeout.

## Residual risk and verification gaps

- The timeout branch was inspected but not forced in a run; behavior after an actual timeout remains unobserved.
- The checker’s own subprocess handling is separate: `tools/round59-battery-outcome-check.py` lines 174–180 starts its `--child` process with `timeout=60`, but does not catch `TimeoutExpired` locally. The outer counter catches timeout of the checker process; it does not catch an uncaught `TimeoutExpired` inside that checker. That child failure should therefore return nonzero and be counted as an evaluation error by the outer mapping, but this inner-timeout path was not exercised.
- `lsp` was unavailable in this environment (`xd://lsp` returned “No such tool”); source references were inspected directly and are not semantic LSP evidence.
- No source, frozen fixture, counter, or lane file was changed. No install performed.
