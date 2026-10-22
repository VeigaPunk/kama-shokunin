# ExecSharedPool8192 — wave-2 falsification advice (round 25, attempt 2)

**Verdict: the C2 statement holds on this fixture, and the confound it named is closed — one correction is still needed to the sentence that states the rule.**

The assigned cell `-c 8192 -np 4 --kv-unified` with the L1 request pair behaves
exactly like L2: on three fresh servers both concurrent requests returned
HTTP 200 with 600 tokens each and `truncated: false`, while the KV pool was
8192 and the served per-slot ceiling was 2048. A shared (unified) pool of
8192 therefore does **not** reproduce the L1 failure, so the L1 failure is not
caused by the unified layout. It is caused by the pool total.

The correction: `corpus/knowledge/context-capacity.md` says "The limit is the
pool total, not a full per-slot context". As written that reads as if the
pool total is always the binding limit. It is the smaller of the pool total
(shared across concurrent sequences) and the per-slot ceiling. One more
unregistered cell shows the per-slot ceiling binding first while the pool
total is 8192. Smallest correction is one clause in that sentence plus the
deletion of the two now-closed "was not run" statements.

---

## 1. What was run

Fixture and binary, unchanged from the committed C2 receipt:

- `~/.cache/kama-shokunin/models/stories260K.gguf`, sha256
  `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`
- `~/.local/bin/llama-server` → `/home/vgpnk/.local/opt/llama-b11755/llama-server`,
  `--version` contains `build 11755`
- ports 47420-47439 on 127.0.0.1 only, one child at a time, each child
  reaped (SIGTERM, `child_returncode` 0) and each port confirmed closed
  (`port_closed: true`, `ss_listen_lines_after: []`) before the next child

The request code is the committed tool's code, imported by file path, not
re-implemented: `tools/kama-context-capacity.py` `run_cell` and
`_run_load_requests`. The request pair is the L1 pair: two concurrent
`POST /completion`, each a 1000-token prompt given as one flat list of token
ids, `n_predict` 600, `ignore_eos` true, `cache_prompt` false, `stream` false,
both started behind a barrier (`CONCURRENT_WINDOW_S` 0.050 s).

Commands and exit codes:

```
python3 /fast/scratch/hyaku/kama-r25a2w2/ExecSharedPool8192/run_shared_pool_8192.py
  -> {"all_ports_closed": true, "observed": 3, "ports_used": [47420, 47421, 47422], "runs": 3}
  exit 0
python3 /fast/scratch/hyaku/kama-r25a2w2/ExecSharedPool8192/run_dose_response.py
  -> {"all_ports_closed": true, "observed": 3, "ports_used": [47420, 47421, 47422], "runs": 3}
  exit 0
python3 /fast/scratch/hyaku/kama-r25a2w2/ExecSharedPool8192/run_perslot_bound.py
  -> {"all_ports_closed": true, "observed": 1, "ports_used": [47420], "runs": 1}
  exit 0
```

The three scripts are copies of the ones in the scratch dir; they are in the
artifact dir too (`run_shared_pool_8192.py`, `run_dose_response.py`,
`run_perslot_bound.py`).

## 2. Per-run table

Full table with all columns: `.ufo/waves/round-25/a2-falsify/out/ExecSharedPool8192/per-run-table.md`.

### Assigned cell — `-c 8192 -np 4 --kv-unified` (unregistered; not in the 14-cell count)

| run | port | KV pool (last `llama_context: n_ctx`) | /props n_ctx | slots | /slots n_ctx | statuses | tokens predicted | truncated | error | start gap ms | overlap s | port closed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 47420 | 8192 | 2048 | 4 | 2048 ×4 | 200, 200 | 600, 600 | false, false | — | 0.126 | 0.2133 | yes |
| S2 | 47421 | 8192 | 2048 | 4 | 2048 ×4 | 200, 200 | 600, 600 | false, false | — | 0.096 | 0.2099 | yes |
| S3 | 47422 | 8192 | 2048 | 4 | 2048 ×4 | 200, 200 | 600, 600 | false, false | — | 0.090 | 0.2047 | yes |

3 of 3 runs: both concurrent requests HTTP 200, 600 tokens each, not truncated,
start gap ≤ 0.13 ms, request overlap ≈ 0.21 s (the whole generation window),
so the two requests were genuinely open at the same time.

Server-log evidence, run S1
(`.ufo/waves/round-25/a2-falsify/out/ExecSharedPool8192/S1.server.log`):

- line 283: `llama_context: n_ctx                 = 8192`
- line 284: `llama_context: n_ctx_seq             = 8192`
- line 289: `llama_context: kv_unified            = true`
- line 304: `llama_kv_cache: size =    5.00 MiB (  8192 cells,   5 layers,  4/1 seqs)`
- line 1084: `load_model: initializing, n_slots = 4, n_ctx_slot = 2048, kv_unified = 'true'`
- lines 1268, 1272: the two requests landed on slot 0 (task 3) and slot 1
  (task 2), each `n_ctx_slot = 2048, task.n_tokens = 1000`
- lines 12688, 12699: `slot release: id 0 | task 3 | stop processing: n_tokens = 1599, truncated = 0`
  and the same for id 1 — both finished with 1600 cells each, no error anywhere
  in the log (grep for `Context size has been exceeded` returns nothing)

### Supplementary cells (unregistered; layout held fixed, pool total varied)

| run | args | port | KV pool | /props n_ctx | /slots n_ctx | statuses | tokens | error |
|---|---|---|---|---|---|---|---|---|
| D2048 | `-c 2048 -np 4 --kv-unified` | 47420 | 2048 | 2048 | 2048 ×4 | 500, 500 | — | `Context size has been exceeded.` |
| D3072 | `-c 3072 -np 4 --kv-unified` | 47421 | 3072 | 2048 | 2048 ×4 | 500, 500 | — | `Context size has been exceeded.` |
| D4096 | `-c 4096 -np 4 --kv-unified` | 47422 | 4096 | 2048 | 2048 ×4 | 200, 200 | 600, 600 | — |
| D8192PS512 | `-c 8192 -np 4 --kv-unified --kv-unified-per-slot 512` | 47420 | 8192 | 512 | 512 ×4 | 400, 400 | — | `request (1000 tokens) exceeds the available context size (512 tokens), try increasing it` |

The failure point moves with the pool total and nothing else, because
`/props`, `/slots` and the number of slots are identical in D2048, D3072 and
D4096:

- D2048 `…/D2048.server.log:1847` `decode: Context size has been exceeded. off = 0, n_batch = 1, ret = 1`;
  lines 1851 and 1862: `slot release … n_tokens = 1025` for both requests
  (2 × 1025 = 2050 > 2048).
- D3072 `…/D3072.server.log:11588` the same error; lines 11592 and 11606:
  `slot release … n_tokens = 1537` for both (2 × 1537 = 3074 > 3072).
- D4096 `…/D4096.server.log:12684,12695`: `slot release … n_tokens = 1599` for
  both, no error (2 × 1600 = 3200 ≤ 4096).
- D8192PS512 `…/D8192PS512.server.log:1269,1280`: `send_error: task id = 2 …
  request (1000 tokens) exceeds the available context size (512 tokens)`;
  line 1084: `n_ctx_slot = 512`. Both requests are rejected before any
  generation although the pool holds 8192.

## 3. The named attack

The C2 entry (`corpus/knowledge/context-capacity.md`, section "A shared pool
limits concurrent requests by its total size") states:

> "The limit is the pool total, not a full per-slot context: each L1 request
> failed at about half of its 2048 per-slot ceiling. L1 and L2 report the same
> endpoints (per slot 2048, 4 slots); L2's pool is four times larger. L2
> changes the pool size and the cache layout together, so it does not separate
> the two; a shared pool of 8192 was not run."

and, under "Does not establish":

> "A shared pool of the same total size as L2 (`-c 8192 -np 4 --kv-unified`), a
> split cache under concurrent load with small per-slot streams, and the `-c 0`
> split case: none was run."

What the new runs show:

1. **The missing shared-8192 cell behaves like L2.** Three of three fresh
   servers: both concurrent requests HTTP 200, 600 tokens each, not truncated
   (`shared-pool-8192-receipt.json`, runs S1-S3). A shared pool of 8192 does
   not reproduce the L1 failure, so the unified layout is not the cause of
   L1's failure.
2. **The pool total alone flips the outcome when the layout and the served
   endpoints are held constant.** D2048 / D3072 / D4096 have identical
   `/props` (2048), identical `/slots` (4 × 2048) and the same unified layout;
   only the pool total changes (2048 / 3072 / 4096) and the outcome flips from
   500 to 500 to 200. This is the separation L2 could not give, because here
   pool size is the only variable — L2 changed pool size and layout together,
   whereas D4096 changes only the pool.
3. **The threshold is where the pool total says it should be.** The pair needs
   2 × (1000 prompt + 600 generated) = 3200 cells at once. A pool of 3072
   fails, a pool of 4096 passes; and in each failing run both requests were
   released at about half the pool (1025 of 2048, 1537 of 3072), the
   signature of one shared pool divided between concurrent sequences.
4. **One qualification the entry does not yet state.** D8192PS512 keeps the
   pool at 8192 and lowers the per-slot ceiling to 512; both requests are
   rejected with HTTP 400 `exceed_context_size_error` before any token is
   generated. So the pool total is not the only bound: the served limit is the
   smaller of the pool total shared across concurrent sequences and the
   per-slot ceiling. The L1/L2 comparison in the entry is unaffected (there
   the per-slot ceiling, 2048, was never the binding bound, since each
   request needed 1600 cells), but the sentence as written over-claims.

One more detail the runs add to the entry's table, from
`…/S1.server.log:284,304` against the committed `final/raw/L2.server.log:284,303`:
with a unified cache the pool is not divided into per-slot streams
(`n_ctx_seq = 8192`, `8192 cells, 4/1 seqs`), while the split cache of L2 has
`n_ctx_seq = 2048`, `2048 cells, 4/4 seqs`. Both hold the same total memory
(5.00 MiB) and the same pool total (8192). The served per-slot ceiling stays
at the training context (2048) in the unified cell, so the two numbers the
entry names really are two different numbers there.

## 4. Smallest correction I recommend to the L1

All three edits are in `corpus/knowledge/context-capacity.md`; nothing else in
the lane needs to change, and no counter output changes.

1. Section "A shared pool limits concurrent requests by its total size":
   replace "The limit is the pool total, not a full per-slot context" with a
   statement that the limit is the smaller of the pool total shared across
   concurrent sequences and the per-slot ceiling, and that for the L-cell
   request shape the pool total is the one that binds. Add the two new
   measurements: pool 2048 → both fail at 1025 tokens each; pool 3072 → both
   fail at 1537 tokens each; pool 4096 → both pass with 600 tokens each,
   with the endpoints unchanged at 2048 per slot and 4 slots in all three.
2. Same section: the sentence "L2 changes the pool size and the cache layout
   together, so it does not separate the two; a shared pool of 8192 was not
   run" can be replaced by the measured result: the shared 8192 pool was run
   three times and behaves like L2, and the separation is now done by holding
   the layout fixed and varying only the pool total.
3. "Does not establish": drop the first item ("A shared pool of the same
   total size as L2 … none was run"). Keep the other two items as they are
   (a split cache under concurrent load with small per-slot streams, and the
   `-c 0` split case were still not run). Add the fixture scope: build 11755,
   this model, one request pair of 1000 + 600 tokens, unregistered loopback
   ports, and the fact that these are unregistered supporting cells that do
   not enter the 14-cell claim count.

If the L1 prefers a single line instead of three, the minimum that removes the
over-claim is: "the limit is the pool total shared across concurrent
sequences, or the per-slot ceiling if that is smaller".

## 5. Limits of this attack

- Unregistered cells on the lane fixture only. They are not part of the 14-cell
  count; `python3 .ufo/waves/round-25/count-c2.py` over the committed receipt
  is unaffected. Verified by me after the runs: it printed
  `registered 14 observed 14 bound True missing []`, exit 0.
- Build 11755 (commit 704366d76) only, this model, CPU only, one request pair
  shape (1000 prompt tokens + 600 predicted), `cache_prompt` false, no context
  shift. No registered consumer was probed and no consumer port was touched.
- The "smaller of the two" rule is shown in one direction only (per-slot
  ceiling binding first with a large pool). The opposite corner — a pool
  smaller than one request — was not run here.
- Whether the same numbers hold for a different request count, size or
  `cache_prompt` setting is not established by these runs.
- [INFERENCE] The reading that the failure point (1025 of 2048, 1537 of 3072)
  is the pool being divided between the two concurrent sequences is an
  inference from the release token counts plus the single shared KV cache
  (`8192 cells, 4/1 seqs`); I did not open the llama.cpp source in this seat.

## 6. Files I wrote

In the lane (`/home/vgpnk/Projects/shokunin/kama-shokunin`):

- `.ufo/waves/round-25/a2-falsify/advice/ExecSharedPool8192.md` (this report)
- `.ufo/waves/round-25/a2-falsify/out/ExecSharedPool8192/per-run-table.md`
- `.ufo/waves/round-25/a2-falsify/out/ExecSharedPool8192/shared-pool-8192-receipt.json`
- `.ufo/waves/round-25/a2-falsify/out/ExecSharedPool8192/shared-pool-dose-receipt.json`
- `.ufo/waves/round-25/a2-falsify/out/ExecSharedPool8192/shared-pool-perslot-receipt.json`
- `.ufo/waves/round-25/a2-falsify/out/ExecSharedPool8192/S1.server.log`,
  `S2.server.log`, `S3.server.log`
- `.ufo/waves/round-25/a2-falsify/out/ExecSharedPool8192/D2048.server.log`,
  `D3072.server.log`, `D4096.server.log`, `D8192PS512.server.log`
- `.ufo/waves/round-25/a2-falsify/out/ExecSharedPool8192/S1.props.body`,
  `S1.slots.body`, `S2.props.body`, `S2.slots.body`, `S3.props.body`,
  `S3.slots.body`
- `.ufo/waves/round-25/a2-falsify/out/ExecSharedPool8192/run_shared_pool_8192.py`,
  `run_dose_response.py`, `run_perslot_bound.py`

Scratch (heavy, outside the lane):
`/fast/scratch/hyaku/kama-r25a2w2/ExecSharedPool8192/` (the three scripts, the
per-cell server logs under `raw/`, and the three run outputs).

No production file, counter, corpus entry, SOURCES row or skill file was
edited by this seat; no commit, no push, no jj command, no change outside the
lane and my scratch dir. No tool was installed or upgraded in this seat.
