# Persisted probe latency budget — proposal for r90 routed R4 (r89 R3)

Status: proposal only. Nothing here is landed; the seat is read-only in the lane.
Scope: one pinned line a test can grade, in the shape r89 R3 asked for ("a pinned latency/step
budget to a harm suite so a future slowdown is caught by a frozen rule"), with the r90 R4 addendum
("<= 10 % latency measured").

## The test

`tests/probe-latency-budget.sh` (new, ~120 lines, python3 for the stub only — the probe itself is
graded in both modes):

1. `D=$(mktemp -d "${TMPDIR:-/tmp}/kama-latency.XXXXXX")`; start ONE python3 stub on 127.0.0.1:0
   serving `/v1/models` from a generated body (200 000 ids `x000000`..`x199999` + `good`,
   compact JSON, 1.6 MB — under the round-90 4 MiB cap). No operator endpoint, no network.
2. For each row of `tests/latency-budget.tsv`, run the row's argv n=5 times, DISCARD the first
   (warm-up), take the median of 4, print exactly one line:

   `LATENCY cell=<c> runs=5 median_ms=<m> max_ms=<x> bound_ms=<b> baseline_ms=<bl> ratio=<m/bl> load1=<l> ok=<0|1>`

   and exit 1 if any row is `ok=0`, 0 otherwise. Exit 2 on a missing dependency or a stub that
   never answers (mirrors the round counters).
3. Rules the test enforces (all four are the "budget"):
   - **R-abs**: `median_ms <= bound_ms`. `bound_ms = 4 x median at pinned_rev`, rounded up to the
     next 1000 ms (next 100 ms below 1000) — 1335 -> 6000, 698 -> 3000, 114 -> 500. The suite rows
     use 2x instead of 4x because their median is dominated by per-row process start-up. A bound
     that is a multiple of the measured value, not a round number chosen by taste, so the recorded
     derivation can be re-checked by hand.
   - **R-rel** (the r90 <=10 % rule): when `load1 <= 8`, run base and candidate alternately in one
     session and fail if `median_ms > 1.10 * median_ms(base)`. Applied only to cells whose median
     is >= 500 ms: below that, process start-up dominates and the ratio is noise (see P1 below:
     138 ms at B vs 114 ms at M, a 17 % swing on a cell where nothing got slower).
   - **R-load**: one over-budget run when `load1 > 8` is re-run once; only a second over-budget
     run fails. Never fail a cell on a single sample under load — the host is shared and this seat
     measured 23-41 load1 while doing nothing but timing.
   - **R-nopy**: the 200 000-id cell is also run with `PATH` pointing at a scratch dir of symlinks
     with `python3` removed; the probe must still answer within `bound_ms` (it does at M: 698 ms,
     see below). Without this row the frozen C1 counter's python-free path is graded by nothing —
     `tests/probe-verdicts/check.py` and `tools/test-snapshot.sh` both hard-require python3
     (`FAIL missing dependency: python3`, exit 1).

## The pinned lines (proposed, tab-separated, header first)

`tests/latency-budget.tsv`:

```
cell	argv	bound_ms	baseline_ms	pinned_rev	host	recorded
probe-check-200k	check --port {stub} --expect good --json --timeout 5 --connect-timeout 2	6000	1335	3decfa36b0eba7e5197c034dd1547146bca1568a	X1 32c load1 28-29	2026-11-06
probe-check-200k-nopy	(python3 hidden from PATH)	3000	698	3decfa36b0eba7e5197c034dd1547146bca1568a	X1 32c load1 28-29	2026-11-06
probe-check-plain	check --port {stub} --expect good --json --timeout 5 --connect-timeout 2	500	114	3decfa36b0eba7e5197c034dd1547146bca1568a	X1 32c load1 28-29	2026-11-06
```

## Numbers this proposal is derived from (all measured 2026-11-06 by this seat)

Host: 32 cores, load1 28-29 for the budget rows (load1 36-41 for the suite rows), `uptime` recorded
next to each receipt in `budget-M.out`, `budget-B-P1.out`, `snapshot-timing.out`.

| cell | rev | mode | runs | median | max | source |
|---|---|---|---|---|---|---|
| 200 000 ids + good (1.6 MB) | B `c06838c5` | python3 | killed at 120 000 ms | - | - | `b-nopy.out` (python-free) / `controls/c1-base.out` (python3) |
| 200 000 ids + good (1.6 MB) | M `3decfa36` | python3 | 5 (4 kept) | **1335 ms** | 1408 | `budget-M.out` |
| 200 000 ids + good (1.6 MB) | M `3decfa36` | python3 hidden | 5 (4 kept) | **698 ms** | 703 | `budget-M.out` |
| single id `good` | B `c06838c5` | python3 | 5 (4 kept) | 138 ms | 144 | `budget-B-P1.out` |
| single id `good` | M `3decfa36` | python3 | 5 (4 kept) | 114 ms | 121 | `budget-M.out` |
| single id `good` | B `c06838c5` | python3 hidden | 5 (4 kept) | 43 ms | 44 | `budget-B-P1.out` |
| single id `good` | M `3decfa36` | python3 hidden | 5 (4 kept) | 41 ms | 42 | `budget-M.out` |

Base cannot be timed on the 200 000-id cell: it is killed at the counter's 120 s limit in BOTH
modes, which is exactly the free pass the budget closes. The 200k cell is therefore the only one
that discriminates a linear-time probe from a quadratic one; the plain cell exists to catch a
constant-factor regression (start-up, an extra fork per run) that the 200k cell would hide inside
its own noise.

Whole-suite wall time (the r89 D3 "1.8x" class of change) lands in the same file as two extra rows
so a future slowdown is caught by the same frozen rule, not by a wave seat:

```
probe-suite-verdicts	bash tests/probe-verdicts/check.py	90600	45300	3decfa36…	X1 32c load1 23-34	2026-11-06
probe-suite-snapshot	bash tools/test-snapshot.sh	4300	2109	3decfa36…	X1 32c load1 36-41	2026-11-06
```

Measured: `check.py` 77/77 in B median 45.30 s (45.53 45.30 42.86) vs M median 43.03 s
(45.97 43.03 43.01), ratio 0.95; `test-snapshot.sh` 30/0 in B median 1949 ms vs M median 2109 ms,
ratio 1.08 at load1 36-41. Neither moves outside the 10 % band; both are dominated by per-row
process start-up, which is why their bound is 2x the measured median rather than the 4x used for
the probe cell.

## Why not a counter

The round counters are frozen with a claims file and cannot be edited after the freeze; a latency
budget has to be updatable by the round that re-pins it. A `tests/` script with a checked-in TSV
keeps the number reviewable in the diff and gradable by `pre-report-gate.py` as one more arm.
