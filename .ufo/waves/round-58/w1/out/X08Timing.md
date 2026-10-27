# X08Timing — wall-time of the round-58 C1 checker and C1 counter

Seat: X08Timing (advisory leaf, no verdict). Measured tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`
(frozen build tip). Python 3.14.8. Host: 32 cores, loadavg 7.41–9.72 during runs (shared), scratch
on `/fast`. Checker/counter bytes taken from the tip blob (sha256 89ad4e5d…/32f615d8…, copied into the
output dir); env built with the frozen checker's own `clean_env()`, `TMPDIR` set to the seat scratch.
No lane-tree write, no git mutation outside throwaway fixtures owned by the frozen counter.

## Exact command (5 runs each + 15 per-variant probes)
```
python3 $S/timeit.py                    # A: whole checker 5x, B: harness child 5x, C: whole counter 5x
  A: python3 checker-tip.py --repo <lane> --tip e4891d8a --work $S/wkA<i> --out $S/A<i>.out
  B: python3 checker-tip.py --repo <lane> --tip e4891d8a --harness battery-tip.py --harness-out …
  C: python3 counter-tip.py --repo <lane> --tip e4891d8a \
       --checker-blob e4891d8a:tools/round58-battery-exec-check.py --work $S/wkC<i>
python3 counter-tip.py … --checker $S/shim.py      # shim logs 15 per-variant checker walls
```
Every A run: `present=1 roster_match=1 kills=1 controls=2 executed=1 legs=3/3 mutant_assert=1 met=True`, rc=0.
Every C run: `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`, rc=0. No timeout on any run.

## Results (wall seconds)
| measurement | n | min | median | max |
|---|---|---|---|---|
| A whole checker (1 earlier batch: 0.081/0.083/0.087) | 5 | 0.081 | 0.083 | 0.087 |
| B harness child only — the span `TIMEOUT = 60` bounds (earlier batch 0.049/0.051/0.054) | 5 | 0.052 | 0.053 | 0.059 |
| C whole frozen counter = 15 fixtured checker runs (earlier batch 1.116/1.211/1.216) | 5 | 1.119 | 1.174 | 1.228 |
| per-variant checker invocation inside C (via shim, +1 process spawn ≈ upper bound) | 15 | 0.0624 | 0.0674 | 0.0834 |
Sanity cross-check with bash `time` on the plain checker: real 0.095 s / 0.097 s / 0.090 s.

## 60 s timeout: margin is ~3 orders of magnitude, positive
- `TIMEOUT = 60` (checker line 36, applied at line 194) wraps exactly one subprocess: the harness child. Slowest child
  0.059 s → **1017× headroom**; even charging the whole checker run to the timeout gives 690×.
- The counter's own bound is `timeout=120` per variant; slowest measured variant 0.0834 s → **1439×**.
- Worst-case path is fail-safe, not false-met: an overrun yields `could-not-evaluate: harness timeout`
  → rc=2, which the counter scores as `error`, so `met` would go False rather than True.
- Arithmetic headroom: the bounded child does one `git ls-tree -r` (32 372 paths) + one `git show` per
  `read_text` call (battery has 1 such site, line 74) against a 35.26 MiB pack. A 100× slowdown still
  leaves ~10× margin.

## What this attacks (evidence only, no judgement)
- C1 frozen predicate / `tools/round58-battery-exec-check.py`: `met=True` is not a timing artifact — the
  run completes in 0.09 s wall with 0 evaluation errors, so the counter's `errors=0` is genuine work.
- `tools/round58-c1-counter.py`: 15 sequential variants finish in ~1.2 s, 100× under its per-variant
  `timeout=120`; no variant was near any bound. `TIMEOUT = 60` is 1000× oversize here — not a hidden gate.

## Limits / risks (reported, not fixed; outside seat scope)
1. The checker's own git calls (`rev-parse`, `show prereg`, `show battery`) carry **no timeout**; only the
   harness child is bounded. A hung git or stalled fs would hang the checker unbounded instead of failing
   closed. Not observable here (each such call ≈ 5–10 ms).
2. The counter's unbounded component is fixture setup: `git init` + 5 blob `git show`s + `add -A` + commit,
   measured at ~0.0119 s per variant (1.174 s total − 1.0212 s of variant checker work). On a cold or very
   slow filesystem this is the first part to inflate; `timeout=120` does not cover it.
3. Numbers are hot-page-cache on a loaded shared host (loadavg up to 9.72): per-run medians, not a
   worst-case bound; no run was cold-cache, and no variant/battery mutation was timed. `TIMEOUT` has no
   CLI override, so a pathological host degrades to rc=2 rather than a configurable budget.

## Retained evidence (in this seat's output dir)
`timing.json` (all 24 timed runs, per-run loadavg), `timeit.py`, `shim.py`, `S.log` (15 per-variant walls),
`A0-4.out`, `C0-4.out`, `S.out`, `sanity1-3.out`, `frames/wkB*-result.json`, `commands.txt`, tip blobs used.
