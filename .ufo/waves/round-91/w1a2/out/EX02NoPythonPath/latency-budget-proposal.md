# R4 latency-budget pin — concrete, persistable proposal (EX02NoPythonPath, r91 w1a2)

Status: proposal only (prose). Nothing was written to `tests/` or `tools/`; the L1 integrates.
Carries r89 R3 → r90 R4 → r91 R4, which records that no budget pin has ever entered `tests/` or
`tools/` (`SCORECARD.md:78`, r90 lesson R4) and that the r90 wave-1 EX02 line
(`.ufo/waves/round-90/w1/EX02HarmLatency.md:64-77`, M/base ratio on `latency.py`) was proposed but
never persisted.

## Why the r90 ratio line did not persist, and what to pin instead

The r90 line gates **M against a base probe** (median ≤ 1.5×, p90 ≤ 2.0×) using a 20-run
README-style harness. Persisting it needs (a) a copy of the base probe kept alive forever as
fixture, and (b) ~40 probe runs per gate. A frozen rule should not carry a dead revision's bytes as
a fixture.

The class the pin must catch is **superlinear work in the served-id list**, which round 91 removed:
a `$(normalize_id …)` fork per id, `${s##*/}` and `${C_SERVED%,}` over multi-MB strings. That class
needs no old probe to detect: it is visible as a **scaling ratio measured in one session** on
synthetic stubs.

## Line A — scaling + bound (recommended; new file `tests/latency-budget.sh`)

Command (the exact gate a future round can run unaided):

```
bash tests/latency-budget.sh            # exit 0 iff holds=1
KAMA_LATENCY_BUDGET=5.0 bash tests/latency-budget.sh
```

Three lane-owned stub cells, each `check --expect good --json`, python3 present (the same fixture
style `tools/test-snapshot.sh:41-71` already uses; no new dependency):

| cell | stub `/v1/models` body | purpose |
|---|---|---|
| `L1` | 1 000 ids, last one `good` | per-call constant work |
| `L2` | 200 000 ids, last one `good` | the fork-per-id class (T1 shape) |
| `L3` | one 3 900 000-byte id, then `good` | the `${s##*/}` quadratic class (T4 shape) |

Pinned line the test prints and gates on (one line, machine-parseable):

```
LATENCY_BUDGET l1=<s> l2=<s> l3=<s> ratio_l2_l1=<r> max=<s> budget=5.0 load1=<loadavg1> holds=<0|1>
```

Bound: `ratio_l2_l1 <= 3.0` AND `max(l1,l2,l3) <= 5.0` AND every cell verdict `MODEL_OK`/`matched`.
`load1` is reported next to the numbers; above `load1 > 32` (half the 64-thread box, i.e. the load
regime this round's timing cells run in) the absolute half is reported as `holds=report-only` and
only the ratio gates — a ratio of two runs in the same session cancels a load multiplier, an
absolute bound does not.

Measured on this host (2026-11-06, load 22–41 on 32 cores), M `3decfa36…` probe sha256
`0aa43573…`, python3 present, `tools/round91-answer-time.py --rev 3decfa36…`:

- T1 (200 000 ids) 1.77 s, P1 (1 id) 0.11 s → ratio 16 at 200 000 ids **already violates** a 3.0
  ratio if used naively — the ratio must be `L2/L1` with **L1 = 1 000 ids**, not 1 id; measured
  L1-shape cost is ~0.1 s (probe constant + curl), so a 1 000-id L1 is ~0.12 s and M's 200 000-id
  cell is 1.77 s → ratio ≈ 15 … see next paragraph.
- Correction, and the reason the ratio must be `per-id`, not per-cell: the cell time is dominated
  by a **constant** (~0.09–0.11 s: process start + two curl GETs + JSON emit), not by the id scan.
  M's marginal cost over the constant is ~1.66 s for 200 000 ids (8.3 µs/id, i.e. the awk pass) vs
  base's fork path > 120 s. So the honest scaling pin is on the **residual**:
  `(L2 - L1) / (L2_ids - L1_ids) <= 50 µs/id` AND `max <= 5.0 s`. M measures ≈ 8.3 µs/id, base is
  > 600 µs/id (T1 killed at 120 s) — a 60× margin, and the constant cancels instead of poisoning
  the ratio.
- `L3` measured M: 1.51 s (T4) / 1.65 s (T4 on the python-free path) vs a 5.0 s bound; base kills at
  120 s.

So the persisted line becomes:

```
LATENCY_BUDGET l1=<s> l2=<s> l3=<s> us_per_id_l2=<x> max=<s> budget_s=5.0 budget_us_per_id=50 load1=<l> holds=<0|1>
```

and `holds=1` iff `us_per_id_l2 <= 50` AND `max <= 5.0` (absolute half report-only when
`load1 > 32`) AND all three cells graded `MODEL_OK matched` (a fast wrong answer must not pass).

## Line B — zero-new-fixture variant (harm suite, cheapest to land)

If the L1 will not add a stub harness, the frozen counter already produces the numbers; a wrapper
test needs only to parse them:

```
python3 tools/round91-answer-time.py --repo . --rev HEAD --work "$TMPDIR" | tee "$TMPDIR/at.out"
awk '/^ANSWER_TIME_CELL/ { for (i=1;i<=NF;i++) if ($i ~ /^seconds=/) { split($i,a,"="); if (a[2]+0>m) m=a[2]+0 } }
     END { printf "LATENCY_BUDGET max_seconds=%.3f budget_s=5.0 holds=%d\n", m, (m<=5.0) }' "$TMPDIR/at.out"
```

Bound: `max_seconds <= 5.0`, exit 0 elsewhere as today. Measured max over the 12 cells: 2.05 s
(python path, frozen receipt `measured/c1.out`) and 1.65 s (python-free path, this seat's
`out/EX02NoPythonPath/m-nopy.out`) — 2.4× headroom against a 5.0 s bound, 10× against the frozen
20 s cell budget. Base max is a kill (120 s), so the line is failing-before.

Line B is weaker than A (it grades the counter's own cells, so a future successor counter could
change the cells; the claim's K3 already forbids that for this round) but it costs one `awk` line
in an existing receipt and no new fixture.

## Explicit non-goals

- Do **not** pin operator `127.0.0.1:1234` latency: the contract allows GET only and the r90
  receipts show 0.33–0.37 s with router-state variance. Report-only, never a gate (r90 line already
  said this).
- Do **not** pin wall time of `tools/test-snapshot.sh` / `tests/probe-verdicts/check.py`: those
  measure the harness, not the probe (see the w1a2 report — they are load-sensitive and moved
  <2 % between B and M).
- Do **not** derive the bound from this host's absolute numbers without the `load1` field: at
  load 41 the same 200 000-id cell that takes 0.76 s idle takes 1.77 s; that is why the ratio/
  residual half exists.
