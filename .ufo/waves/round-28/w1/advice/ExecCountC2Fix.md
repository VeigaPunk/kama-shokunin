# ExecCountC2Fix — round-28 wave 1, routed repair 1

**Item:** repair, routed defect 1 of the round-27 verifier spot-check
(`corpus/lessons/round-27-verifier-spotcheck.md:258-287`; open since
round-25 defect 5 and round-26 defect 8). **Not a claim.** Lane tree read
only; the lane file `.ufo/waves/round-25/count-c2.py` was not edited.

**Inputs read.** `.ufo/waves/round-28/preregistration.json` (C1 and the
repair routing), `.ufo/waves/round-25/count-c2.py`,
`.ufo/waves/round-25/preregistration-amendment-2.json` (C2 `command_rule`:
"kv_pool_n_ctx integer that matches **a captured** `llama_context: n_ctx`
log line"), amendments 3 and 4, `tools/kama-context-capacity.py` (the
receipt schema and its extraction rules), `SKILL.md:677-700` (the round-25
decision rows) and `corpus/QUALITY.md:203` (KQ36: a registered command
must be re-runnable and its output pasted at a landed tip).

## Defect

`count-c2.py` (`:170-183` before this patch) bound the receipt to the raw
file hashes (`raw_bound`) but took **every cell value from the receipt**:
`props_n_ctx`, `total_slots`, `slots_n_ctx`, `models_n_ctx_train`,
`kv_pool_n_ctx`, `log_lines`, and the load-cell `requests`. `cell_ok`
compared the receipt's `kv_pool_n_ctx` with the receipt's own `log_lines`,
so a receipt that edited the scalar **and** the log line it was compared
with passed every check. Amendment-2 says the pool must match *a captured*
log line; before this patch "captured" meant "whatever the receipt says".

## Change (patched file, unified diff)

`../../out/ExecCountC2Fix/count-c2.py` (sha256
`5aa64a370196f352435bdf2cee2526019a3eac2737eb194496c5126d5759fa2a`), diff at
`../../out/ExecCountC2Fix/count-c2.diff`
(`f75468c8e219ceb27b8e8b21e8b41c151958b7519dba919146dea18b51cd6872`;
lane input `2f952dca58a4ff2efe55cbb9f2afcae1b8ae4efd41a3ee8461522699d77d760b`;
297 diff lines, 217 added and 25 removed; `patch -p1 --dry-run` applies it).

Per-cell values are now recomputed from the raw bytes the cell's `raw`
hashes bind, mirroring `tools/kama-context-capacity.py` exactly:

| value | recomputed from |
|---|---|
| `props_n_ctx`, `total_slots` | `<id>.props.body`: `default_generation_settings.n_ctx`, `total_slots` |
| `slots_n_ctx` (per-slot value) | `<id>.slots.body`: every entry `n_ctx` |
| `models_n_ctx_train` | `<id>.models.body`: `data[0].meta.n_ctx_train` |
| `kv_pool_candidates`, `kv_pool_n_ctx` | `<id>.server.log`: every `llama_context: n_ctx = N`, last wins |
| `log_lines` | `<id>.server.log`: the claim-named line set (`LOG_KEEP`) |
| request outcomes | `<id>.server.log`: `new prompt … task.n_tokens = N` (prompt tokens, start order); `srv send_error: task id = N` (HTTP 500, message text); `slot release … n_tokens = M, truncated = F` (HTTP 200, truncated flag); concurrent iff the second request starts before the first ends |

A cell is **observed** only when its `raw` hashes still match the files,
every derived value equals the receipt cell, and the existing structural
checks pass. `bound` additionally requires every cell to agree with its raw
bytes. Output line unchanged:
`registered N observed M bound B missing [...]`. No CLI change; the raw
directory stays `<script dir>/final/raw`, so the patched file must be placed
at `.ufo/waves/round-25/count-c2.py` in a tree holding `final/raw` (the out
copy run in place prints `observed 0` — intended fail-closed).

Not recoverable from the committed bytes: absolute request timestamps and
launch `argv`. They remain receipt-internal consistency checks; the
receipt's overlap must equal the raw-derived mode, and `n_predict` is the
registered request constant.

## Acceptance — exact commands and outputs

Setup (scratch, `/fast/scratch/hyaku/kama-r28/w1/ExecCountC2Fix`, lane
untouched): copy `.ufo/waves/round-25/final` to
`tree/.ufo/waves/round-25/final`, place the lane counter as
`count-c2-before.py` and the patched bytes as `count-c2-after.py` at
`tree/.ufo/waves/round-25/`, run from `tree`. Reproduced end to end by
`bash ../../out/ExecCountC2Fix/run-demo.sh` (transcript
`../../out/ExecCountC2Fix/demo-run-all.out`).

```
lane counter sha256: 2f952dca58a4ff2efe55cbb9f2afcae1b8ae4efd41a3ee8461522699d77d760b
patched counter sha256: 5aa64a370196f352435bdf2cee2526019a3eac2737eb194496c5126d5759fa2a
committed receipt sha256: 78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c
```

**(a) unchanged committed receipt — same result as today**

```
$ python3 .ufo/waves/round-25/count-c2-before.py
registered 14 observed 14 bound True missing []
$ python3 .ufo/waves/round-25/count-c2-after.py
registered 14 observed 14 bound True missing []
```

**(b) forged receipt cell values, raw files untouched**

Fixture `../../out/ExecCountC2Fix/forged-cells.receipt.json`
(`8007fb24…5a03`), built by `make-fixtures.py`: K2 `props_n_ctx` 1024→512,
`slots_n_ctx` [1024,1024]→[512,512], `kv_pool_n_ctx` and
`kv_pool_candidates` 2048→1024, with the receipt's own `log_lines` pool
lines rewritten to 1024 to keep the old check green; K4 `total_slots` 1→2
with `slots_n_ctx` [1024,1024]; L1 both request records
500/`Context size has been exceeded.`→200/null error/600 predicted.

```
$ python3 .ufo/waves/round-25/count-c2-before.py fixtures/forged-cells.receipt.json
registered 14 observed 14 bound True missing []
$ python3 .ufo/waves/round-25/count-c2-after.py fixtures/forged-cells.receipt.json
registered 14 observed 11 bound False missing ['K2', 'K4', 'L1']
```

Before: every forged cell still observed and the receipt still bound.
After: per-slot value + KV pool (K2), slot count (K4) and request outcomes
(L1) are each refused against the untouched raw bytes.

**(c1) forged raw file, committed receipt — existing hash check**

`forged-K3.props.body` (`5e03cd80…6311`, `default_generation_settings.n_ctx`
2048→512) replaces `final/raw/K3.props.body`; the receipt still binds
`94408c44…2bf1`.

```
$ python3 .ufo/waves/round-25/count-c2-before.py
registered 14 observed 14 bound False missing []
$ python3 .ufo/waves/round-25/count-c2-after.py
registered 14 observed 13 bound False missing ['K3']
```

**(c2) forged raw file AND receipt raw hash rebound to it — the hole the hash check cannot see**

Same forged raw file, receipt `forged-raw-receipt.json`
(`59e770ea…e07f`) with K3 `raw_props` rebound to `5e03cd80…6311`; the
committed receipt cell still says `props_n_ctx` 2048.

```
$ python3 .ufo/waves/round-25/count-c2-before.py fixtures/forged-raw-receipt.json
registered 14 observed 14 bound True missing []
$ python3 .ufo/waves/round-25/count-c2-after.py fixtures/forged-raw-receipt.json
registered 14 observed 13 bound False missing ['K3']
```

Before: a fully forged raw file with a rebound hash is accepted as bound
evidence. After: the derived value 512 disagrees with the receipt's 2048 and
K3 is refused. This is the defect the round-27 spot-check named.

**Parity and fail-closed checks** (`../../out/ExecCountC2Fix/demo-parity.out`)

```
duplicate K1 id        before: registered 14 observed 13 bound True missing ['K1']
                       after:  registered 14 observed 13 bound True missing ['K1']
extra unregistered cell before: registered 14 observed 14 bound False missing []
                       after:  registered 14 observed 14 bound False missing []
no final/raw dir       before: registered 14 observed 14 bound False missing []
                       after:  registered 14 observed 0 bound False missing ['K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'X1', 'X2', 'X3', 'L1', 'L2', 'L3']
out copy in place      after:  registered 14 observed 0 bound False missing ['K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'X1', 'X2', 'X3', 'L1', 'L2', 'L3']
```

The first two preserve the old verdicts; the third and fourth are the new
fail-closed behavior when the counter cannot see the bytes it is supposed
to measure.

## Evidence retained

- `../../out/ExecCountC2Fix/count-c2.py` — patched counter (5aa64a37…)
- `../../out/ExecCountC2Fix/count-c2.diff` — unified diff (f75468c8…)
- `../../out/ExecCountC2Fix/forged-cells.receipt.json`,
  `forged-raw-receipt.json`, `forged-K3.props.body` — forged fixtures
- `../../out/ExecCountC2Fix/make-fixtures.py`, `run-demo.sh` — reproduction
- `../../out/ExecCountC2Fix/demo-run-all.out`, `demo-b-forged-cells.out`,
  `demo-c-forged-raw.out`, `demo-parity.out`, `README.md`
- Scratch tree: `/fast/scratch/hyaku/kama-r28/w1/ExecCountC2Fix{,-demo}`

## Risks

1. **Triple-forgery boundary.** The counter binds receipt→raw. A forgery
   that rewrites a raw file, its receipt hash and the matching cell fields
   together cannot be distinguished without an external anchor (lane git
   history or a fresh live run). Stated in the patched docstring and
   README; not closable inside this counter.
2. **Derivation is format-bound to b11755.** The request-outcome rules match
   the exact log spellings above (`new prompt`, `send_error`, `release`).
   A different build's log wording yields no outcomes → cells refuse (fail
   closed), not false acceptance. The derivation mirrors
   `tools/kama-context-capacity.py`'s extraction rules; if that tool's
   `LOG_KEEP`/`KV_POOL_RE` changes, this counter must change with it (two
   copies of the same rule — a real maintenance coupling, named here).
3. **Timestamps and argv remain receipt self-report.** Only their internal
   consistency and the overlap↔mode agreement are checked.
4. **Placement.** The patched file must land at
   `.ufo/waves/round-25/count-c2.py`; a copy run from the out directory
   resolves no `final/raw` and reports `observed 0`.
5. **KQ36.** Once integrated, any round that reruns this command must paste
   the new output; the unchanged committed receipt still prints
   `registered 14 observed 14 bound True missing []`, so the historical C2
   value is unchanged, now measured from bytes rather than self-report.
6. **No SKILL registration change proposed.** The counter is the round-25
   C2 claim's registered command, not a SKILL instrument-table row; this
   repair does not add one.

## Blockers

None. No llama-server was started (no port used), no lane or fleet write
outside the assigned out dir and this advice file, no subagent, no tool
install (pacman transactions stay paused; nothing was needed).
