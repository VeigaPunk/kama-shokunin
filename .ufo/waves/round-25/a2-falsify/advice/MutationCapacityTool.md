# MutationCapacityTool — round 25 C2, attempt 2, wave 2 (falsify)

**Verdict: defect found.** The committed counter (`count-c2.py`) catches 3 of 5 tool mutants
(M1, M2, M4). Two mutants survive (M3 drop-teardown-gate, M5 fixed-status), and the
survivors expose real gaps: the counter never reads a cell's `observed` flag, never reads
the `teardown` record, never binds the receipt to the tool bytes, and never checks that the
recorded HTTP status agrees with the recorded error text. The last gap is the one that
matters for the C2 claim, because the L1 cell's whole content is the fact that the two
concurrent requests failed.

## Scope and method

- Target: `tools/kama-context-capacity.py` at lane tip `fa3b62ae6475d111eb466d79af616aeebb08bbb9`.
- Clone: `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin` into
  `/fast/scratch/hyaku/kama-r25a2w2/MutationCapacityTool/clone`, checked out at `fa3b62ae`.
- Mutant sources: `clone/tools/kama-context-capacity-mutants/*.py`, each a **single-line**
  change from the committed file (diffs are byte-exact, shown in "Mutant definitions").
- Detector: the committed counter bytes
  `git show fa3b62ae:.ufo/waves/round-25/count-c2.py`
  (sha256 `7bf3f9cdcdf32ea36b5a44d3f9566b90216ee179dc1c7b03386b435e39574d5d`, verified
  identical to the clone copy and to the lane working tree).
- Port range 47460-47479, 127.0.0.1 only, one child at a time, every child killed and
  every port confirmed closed (`all_ports_closed: true` in every receipt). No port in
  47460-47479 was occupied afterwards; `pgrep -x llama-server` returns nothing.
- No tool was installed or upgraded by this seat.

## Baseline (pristine bytes)

Two independent pristine runs were made in the clone:

| run | command | tool exit | counter output | counter exit |
|---|---|---|---|---|
| full 14 cells | `python3 clone/tools/kama-context-capacity.py --port-range 47460-47479 --scratch ./scratch --out ./receipts/base-all.json` | 0 | `registered 14 observed 14 bound True missing []` | 0 |
| committed receipt (untouched) | `python3 .ufo/waves/round-25/count-c2.py .ufo/waves/round-25/final/context-capacity-receipt.json` | — | `registered 14 observed 14 bound True missing []` | 0 |

The full 14-cell pristine run reproduces every value of the committed receipt
(`.ufo/waves/round-25/final/context-capacity-receipt.json`, sha256
`78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c`) field for field:
`props_n_ctx`, `total_slots`, `slots_n_ctx`, `models_n_ctx_train`, `kv_pool_n_ctx`,
`request_mode` and per-request statuses are equal for all 14 cells, and
`server_version` and `model_sha256` are equal. So the baseline is a faithful stand-in for
the committed receipt, and every mutant delta below is attributable to the mutation, not to
run-to-run noise.

## Mutant table

Every mutant was run twice: once on the cells it affects (`--only`) and once over all 14
cells. The table below reports the **full 14-cell run**, so every row is a like-for-like
comparison against the pristine baseline `registered 14 observed 14 bound True missing []`.
The `--only` runs are also given, because the assignment asked for the affected-cell runs
and because the `--only` runs are what establish the per-cell attribution.

| # | change | cells affected (from `--only` runs) | counter output on the full 14-cell mutant receipt | caught |
|---|---|---|---|---|
| M1 | take the **first** pool line instead of the last | `X1` | `registered 14 observed 13 bound True missing ['X1']` | **yes** |
| M2 | drop `-v` from the server argv | all 14 | `registered 14 observed 0 bound True missing ['K1','K2','K3','K4','K5','K6','K7','K8','X1','X2','X3','L1','L2','L3']` | **yes** |
| M3 | drop the teardown gate from the `observed` computation | all 14 | `registered 14 observed 14 bound True missing []` | **NO** |
| M4 | send requests sequentially in concurrent mode | `L1,L2` | `registered 14 observed 12 bound True missing ['L1','L2']` | **yes** |
| M5 | record a fixed status (200) instead of the real one | `L1,L2,L3` | `registered 14 observed 14 bound True missing []` | **NO** |

`--only` runs, same counter, for per-cell attribution:

| # | `--only` cells | counter output on that receipt | tool exit | note |
|---|---|---|---|---|
| M1 | `X1` | `registered 14 observed 0 bound True missing [all 14]` | 0 | only X1 is present; X1 itself fails the counter, the other 13 are simply absent from the receipt |
| M2 | all 14 | `registered 14 observed 0 bound True missing [all 14]` | 1 | every cell fails |
| M3 | all 14 | `registered 14 observed 14 bound True missing []` | 0 | survives |
| M4 | `L1,L2` | `registered 14 observed 0 bound True missing [all 14]` | 0 | L1 and L2 themselves fail the counter |
| M5 | `L1,L2,L3` | `registered 14 observed 3 bound True missing ['K1','K2','K3','K4','K5','K6','K7','K8','X1','X2','X3']` | 0 | L1, L2, L3 all pass the counter despite the fabricated status |

The M2 tool exit is 1: the mutant tool itself reports `observed 0` and
`"all_ports_closed": true`, because without `-v` the server prints no
`llama_context: n_ctx` line at all. The M1, M3, M4 and M5 tools exit 0.

## Mutant definitions (exact diffs, one line each)

M1 — `clone/tools/kama-context-capacity-mutants/m1-first-pool.py` line 386:

```diff
-    record['kv_pool_n_ctx'] = pool_candidates[-1] if pool_candidates else None
+    record['kv_pool_n_ctx'] = pool_candidates[0] if pool_candidates else None
```

M2 — `m2-drop-v.py` line 295:

```diff
-        '--no-webui', '--offline', '-v',
+        '--no-webui', '--offline',
```

M3 — `m3-drop-teardown.py` lines 396-400:

```diff
     record['observed'] = bool(
         record['error'] is None
-        and record['teardown'].get('child_returncode') is not None
-        and record['teardown'].get('port_closed') is True
         and isinstance(record['props_n_ctx'], int)
```

M4 — `m4-sequential-concurrent.py` line 454:

```diff
-    if kind == 'load-sequential':
+    if kind in ('load-sequential', 'load-concurrent'):
```

M5 — `m5-fixed-status.py` line 523:

```diff
-        'status': res.get('status'),
+        'status': 200,
```

## Why each mutant is caught or not

**M1 caught** by the counter's last-pool-line rule. X1 is the only cell with more than one
`llama_context: n_ctx` line (candidates `[2048, 8192, 8192]` — the fit probe logs 2048
first, then the serving pool 8192 twice). The mutant records `kv_pool_n_ctx = 2048`; the
counter re-derives the pools from `log_lines` and compares the **last** one (`8192`) to the
recorded value, so X1 fails `pools[-1] == c["kv_pool_n_ctx"]`. Isolated probe
`receipts/probe-X1-first-pool.json` (X1's `kv_pool_n_ctx` set to its first candidate,
everything else pristine): `registered 14 observed 13 bound True missing ['X1']`. All other
13 cells are unaffected: their candidate lists have first == last, confirmed by running
M1 over all 14 cells and diffing (`m1-all.json`).

**M2 caught** twice over. The counter's `LAUNCH` list requires `-v` in `argv`
(`count-c2.py` line 54, `LAUNCH = ["--host", "127.0.0.1", "--no-webui", "--offline", "-v"]`),
so the missing flag alone fails every cell. Independently, without `-v` the server prints no
`llama_context: n_ctx` line, so `kv_pool_candidates` is empty and `kv_pool_n_ctx` is
`None` — which also fails `pos(c.get("kv_pool_n_ctx"))`. The mutant receipt shows
`kv_pool_n_ctx None`, `candidates []`, `log_lines` count 1. Isolated probe
`receipts/probe-argv-no-v.json` (only `-v` removed from argv, all raw fields pristine):
`registered 14 observed 0 bound True missing [all 14]`.

**M3 survived.** The mutant drops the two teardown conditions from `observed`, but on this
run every child was reaped and every port closed, so the mutant's receipts are
counter-indistinguishable from pristine: the only differing fields are `log_lines` (timestamps)
and `requests` (timestamps). **The counter cannot catch M3 from the receipt at all**, because
`count-c2.py` never reads the `observed` flag or the `teardown` record — `grep -c teardown
count-c2.py` is `0`, `grep -c observed` hits only the docstring and the local list variable
(`observed = []`, `observed.append(cid)`), never `c.get("observed")`. Two probes confirm this:

- `receipts/probe-observed-false.json`: K1's `observed` set to `false`, everything else
  pristine → `registered 14 observed 14 bound True missing []`. The counter overrides the
  tool's own verdict with its own field-by-field recomputation, so the tool's `observed`
  flag is decorative.
- `receipts/probe-teardown-failed-observed-true.json`: K1's `teardown` shows
  `port_closed: false`, `child_returncode: null`, and `observed: true` — exactly the state
  the M3 mutant would produce if a teardown had failed → `registered 14 observed 14 bound
  True missing []`. The counter accepts a cell whose server was never proven to have shut
  down and whose port was never proven closed.

**M4 caught** by the counter's overlap rule. The mutant makes the `load-concurrent` cells
send their two requests back to back. The counter computes
`overlap = max(t_start) < min(t_end)` and requires `overlap == (want == "concurrent")`; with
sequential sends the intervals do not overlap, so L1 and L2 fail. The full 14-cell mutant
receipt scores `registered 14 observed 12 bound True missing ['L1','L2']`. Isolated probe
`receipts/probe-L1-no-overlap.json` (L1's second request shifted to start after the first
ends): `registered 14 observed 13 bound True missing ['L1']`. M4 also changes the observed
**outcome**, which is the substantive part: pristine L1 returns `500` for both requests,
while M4's L1 returns `200` for both — matching L3's sequential result. That is direct
confirmation that the L1 failure is caused by concurrency and not by request size, which is
the C2 amendment-2 L1/L3 prediction. The counter catches the timing artifact; it does not
catch the changed outcome, because it never compares statuses against the prediction.

**M5 survived.** The mutant hardcodes `'status': 200` in `_completion`. The counter's load
rule only requires `is_int(q.get("status"))` and `100 <= status <= 599`, so a fabricated
200 passes. The mutant receipt is internally contradictory: L1 records `status 200` next to
`error "Context size has been exceeded."` and `tokens_predicted None`. The counter accepts
the full 14-cell mutant receipt: `registered 14 observed 14 bound True missing []`. Two
further probes show the gap is not about the mutant but about the counter:

- `receipts/probe-L1-status-200.json`: the committed receipt with L1's statuses flipped
  `500 -> 200` and errors cleared → `registered 14 observed 14 bound True missing []`.
  **A receipt asserting that the concurrent requests succeeded scores exactly the same as
  one asserting that they failed.** The counter cannot distinguish "the concurrency limit
  was observed" from "it was not".
- `receipts/probe-L1-outcome-flipped.json`: same flip keeping the error text →
  `registered 14 observed 14 bound True missing []`.

Two further counter blind spots, both probed and both relevant to trusting the receipt:

- `receipts/probe-receipt-error.json` (receipt-level `exit_code: 1`, `error:
  "simulated-run-failure"`) → `registered 14 observed 14 bound True missing []`. The
  counter ignores the receipt's own `exit_code` and `error`; `grep -c exit_code` is `0`.
- `receipts/probe-tool-sha.json` (`tool.sha256` set to zeros) → `registered 14 observed 14
  bound True missing []`. The counter never binds the receipt to the tool bytes that
  produced it, so a receipt from an edited tool is indistinguishable from one from the
  committed tool. The receipt *does* carry `tool.sha256`; nothing reads it.

## Smallest corrections, and what each kills

Proposed counters are in
`.ufo/waves/round-25/a2-falsify/out/MutationCapacityTool/proposed-counters/`. Each is the
committed counter plus one added rule; none changes the claim value
(`registered 14 observed 14 bound True missing []` still holds on the pristine receipt).

All rows below are computed on **full 14-cell receipts** (every mutant was also run over
all 14 cells, not just its affected subset, so the basis is uniform and no splicing is
needed for this table). The number is the counter's `observed` count.

| receipt | committed | A | B | C | D | combined |
|---|---|---|---|---|---|---|
| base-all (pristine) | 14 | 14 | 14 | 14 | 14 | 14 |
| M1 first-pool | 13 | 13 | 13 | 13 | **0** | 13 |
| M2 drop -v | 0 | 0 | 0 | 0 | 0 | 0 |
| M3 drop-teardown | **14** | **14** | **14** | **14** | **0** | **14** |
| M4 sequential-in-concurrent | 12 | 12 | 12 | 12 | **0** | 12 |
| M5 fixed-status | **14** | **14** | **13** | **13** | **0** | **13** |
| probe-L1-status-200 | **14** | 14 | 14 | **13** | 14 | **13** |
| probe-L1-outcome-flipped | **14** | 14 | 14 | **13** | 14 | **13** |
| probe-observed-false | **14** | **13** | 14 | 14 | 14 | **13** |
| probe-teardown-failed | **14** | **13** | 14 | 14 | 14 | **13** |
| probe-teardown-failed-observed-true | **14** | **13** | 14 | 14 | 14 | **13** |
| probe-receipt-error | 14 | 14 | 14 | 14 | 14 | 14 |
| probe-tool-sha | 14 | 14 | 14 | 14 | **0** | 14 |

Reading of the table:

- **Correction C is the one that protects the C2 claim.** It is what distinguishes a
  receipt that observed the L1 concurrency failure from one that did not: it drops
  `probe-L1-status-200` and `probe-L1-outcome-flipped` to 13, and it catches the M5
  fixed-status mutant. It is strictly additive: the pristine receipt still scores
  `registered 14 observed 14 bound True missing []`.
- **Correction A is what makes the teardown gate in the tool meaningful.** It drops every
  probe in which the tool failed to prove its server shut down
  (`probe-observed-false`, `probe-teardown-failed`, `probe-teardown-failed-observed-true`)
  to 13. Without it, the tool's own teardown gate (added for the round-25 sentinel
  finding) has no effect on the registered score, because the counter recomputes
  `observed` from field values and never consults the flag or the teardown record.
- **Correction D is the strongest single rule for mutation coverage**: it drops every
  mutant to 0 in one line, because any edit to the tool changes its sha256 and the receipt
  records it. It does not substitute for A/B/C — it binds the receipt to the tool but says
  nothing about whether the tool's fields are honest, and it leaves both load-outcome
  probes at 14.
- **A gap D also leaves open:** `probe-receipt-error` (receipt-level `exit_code: 1` and
  `error: "simulated-run-failure"`) still scores 14 under every proposed counter,
  including the combined one. The counter ignores the receipt's own `exit_code` and
  `error` fields. A fifth rule would close this: require `d["exit_code"] == 0` and
  `d["error"] is None`.

Minimal recommended change to the counter: add the C rules (status/error agreement and
2xx-must-predict-tokens), the A rules (require `observed is True` and a proven teardown),
and optionally D (bind the receipt to the committed tool bytes). Together A + C kill every
probe that shows a false observation, and D kills every tool mutation.

## Byte restoration evidence

The lane production tree was never written to by this seat.

- Committed tool bytes, from git, before and after the whole exercise:
  `589841cd4d4890eeb22a5582f78b2bb4c7dcc961253c465fbc9e6d899adc4c27`
  (`git -C /home/vgpnk/Projects/shokunin/kama-shokunin show fa3b62ae:tools/kama-context-capacity.py | sha256sum`).
- The clone's `tools/kama-context-capacity.py` after all runs: same sha256
  `589841cd4d4890eeb22a5582f78b2bb4c7dcc961253c465fbc9e6d899adc4c27`. The mutants live in
  separate files under `clone/tools/kama-context-capacity-mutants/`; the committed file was
  never edited in place.
- Counter bytes: `7bf3f9cdcdf32ea36b5a44d3f9566b90216ee179dc1c7b03386b435e39574d5d` in both
  the clone and the lane working tree; the counter was not modified.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain tools/kama-context-capacity.py .ufo/waves/round-25/count-c2.py`
  is empty — both production files are untouched in the lane working tree.
- No commit, no `git add`, no `jj` command was run. All writes went to the clone under
  `/fast/scratch/hyaku/kama-r25a2w2/MutationCapacityTool/` and to this seat's output
  directory under the lane.

## Files written by this seat

Lane (`.ufo/waves/round-25/a2-falsify/out/MutationCapacityTool/`):

- `mutant-run.log` — the full driver transcript (tool exits, counter outputs, exit codes)
- `run-mutants.sh` — the driver script
- `receipts/base-all.json` — pristine 14-cell baseline
- `receipts/m1-all.json`, `receipts/m2-drop-v.json`, `receipts/m3-drop-teardown.json`,
  `receipts/m4-sequential-concurrent-all.json`, `receipts/m5-fixed-status-all.json` —
  full 14-cell mutant receipts (the basis of the mutant table)
- `receipts/m1-first-pool.json`, `receipts/m4-sequential-concurrent.json`,
  `receipts/m5-fixed-status.json` — the `--only` subset runs
- `receipts/m1-first-pool-spliced.json`, `receipts/m2-drop-v-spliced.json`,
  `receipts/m3-drop-teardown-spliced.json`, `receipts/m4-sequential-concurrent-spliced.json`,
  `receipts/m5-fixed-status-spliced.json` — pristine receipts with mutated cells spliced in
- `receipts/probe-argv-no-v.json`, `receipts/probe-X1-first-pool.json`,
  `receipts/probe-L1-no-overlap.json`, `receipts/probe-L1-status-200.json`,
  `receipts/probe-L1-outcome-flipped.json`, `receipts/probe-observed-false.json`,
  `receipts/probe-teardown-failed.json`,
  `receipts/probe-teardown-failed-observed-true.json`,
  `receipts/probe-receipt-error.json`, `receipts/probe-tool-sha.json`,
  `receipts/probe-wrong-tool-sha.json` — isolation probes
- `proposed-counters/count-c2-A-teardown.py`, `count-c2-B-status-consistency.py`,
  `count-c2-C-status-and-tokens.py`, `count-c2-D-tool-sha.py`, `count-c2-combined.py`
- `kama-context-capacity-mutants/m1-first-pool.py`, `m2-drop-v.py`, `m3-drop-teardown.py`,
  `m4-sequential-concurrent.py`, `m5-fixed-status.py` — the five mutant sources, each a
  one-line change from the committed tool

Scratch (`/fast/scratch/hyaku/kama-r25a2w2/MutationCapacityTool/`): the clone, the mutant
sources, all receipts including the raw server logs under `scratch/` and `receipts/raw/`.

Advice report: `.ufo/waves/round-25/a2-falsify/advice/MutationCapacityTool.md`.

## What this changes for the C2 claim

The claim value itself is not in question: the committed receipt scores
`registered 14 observed 14 bound True missing []` under the committed counter, and this
seat's independent pristine run reproduces that receipt field for field on a different port
range. The defect is in the **instrument**, not the number:

1. The C2 amendment-2 L1 prediction — "the shared 2048 pool cannot hold 2 x 1600 cells, so
   at least one request ends with an error" — is recorded in the receipt as two `500`
   statuses with `error "Context size has been exceeded."`. The committed counter never
   checks that. A receipt with L1's statuses flipped to `200` and the errors cleared scores
   identically (`probe-L1-status-200.json`: `registered 14 observed 14 bound True missing []`).
   The claim's most interesting observation is therefore unprotected.
2. The tool's teardown gate — the round-25 sentinel finding that a cell whose port did not
   close is never an observation — has no effect on the registered score. The counter
   recomputes `observed` itself and never reads the flag or the teardown record, so the
   score cannot distinguish a clean run from a leaked server.
3. The receipt is not bound to the tool that produced it (`tool.sha256` is recorded but
   unread), so tool drift is invisible to the counter.

Correction C closes gap 1; correction A closes gap 2; correction D closes gap 3. All three
are additive and leave the pristine score at `registered 14 observed 14 bound True missing []`.
