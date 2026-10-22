# Round 25 attempt 2 — C2 capacity tool executor advice (ExecCapacityTool)

Verdict: delivered — the capability tool runs all 14 registered cells (K1-K8,
X1-X3, L1-L3) and the committed receipt scores `registered 14 observed 14
bound True missing []` (exit 0); every child was killed and its port proven
closed.

## Files written (all inside the assigned paths)

- `kama-shokunin/.ufo/waves/round-25/a2-build/out/ExecCapacityTool/kama-context-capacity.py`
  (the tool; sha256 `a35f1b4352778239a65af2dd4b4f796938795d3918b05298ed02c3abb550ba61`
  as recorded in the receipt).
- `kama-shokunin/.ufo/waves/round-25/a2-build/out/ExecCapacityTool/receipt/context-capacity-receipt.json`
  (the receipt the counter accepts; run `2026-10-22T09:35:30.194Z` to
  `09:35:38.322Z`, 14 cells, all observed, all ports closed).
- `kama-shokunin/.ufo/waves/round-25/a2-build/out/ExecCapacityTool/receipt/raw/`
  (70 raw files: per cell `/health`, `/props`, `/slots`, `/v1/models` bodies
  and the full server log; every sha256 in the receipt matched the file bytes,
  verified post-run).
- `kama-shokunin/.ufo/waves/round-25/a2-build/advice/ExecCapacityTool.md`
  (this report).
- Scratch copies under `/fast/scratch/hyaku/kama-r25a2/ExecCapacityTool/`
  (per-cell temp logs, smoke-test receipt).

The attempt-1 partial tool (`build/out/ExecCapacityTool/kama-context-capacity.py`)
was re-read but not reused: it lacked the `-v` launch flag, kv_pool_n_ctx, the
load cells, raw-body files, and its field names do not match `count-c2.py`
(`props_default_generation_settings_n_ctx` vs required `props_n_ctx`), so a
fresh tool was written.

## Tool behavior

- Cells and args are byte-for-byte `count-c2.py` CELLS; the tool imports
  `count-c2.py` at run time and aborts (exit 2) on any drift (`cells_drift []
` in the receipt).
- Launch rule per amendment 2: `~/.local/bin/llama-server -m
  ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port <free
  port> --no-webui --offline -v <args>` — `-v` added, never part of the
  registered args.
- Port safety reuses `tools/kama-llamacpp-live.py` by import: `refused_ports()`
  (registry + hard pins 8080/34113), `pick_port(refused, requested)`, `ss -ltn`
  pre-check, and `verify_live` listener-ownership proof after readiness. Ports
  47400-47413 were used (range 47400-47419), one child at a time, each killed
  and the port proven closed before the next cell.
- Per cell the receipt records `props_n_ctx`, `total_slots`, `slots_n_ctx`,
  `models_n_ctx_train`, `kv_pool_n_ctx`, `log_lines` (every log line matching
  n_ctx | kv_unified | n_seq | capping | rounding | KV pool | llama_kv_cache:
  size), `kv_pool_candidates`, raw sha256 digests, teardown result.
- Load cells: a 1000-token prompt is built via POST `/tokenize` (token ids
  sent; `add_special` default false, matching the array-of-numbers completion
  path) and POSTed to `/completion` with `n_predict 600`, `ignore_eos true`,
  `cache_prompt false`. Concurrent mode (L1/L2) starts both requests behind a
  threading barrier; the measured start gap was 0.0001 s (<= 50 ms).
- Exit codes: tool 0, counter 0.

## Registered count and counter output

Command:
```
python3 .ufo/waves/round-25/count-c2.py .ufo/waves/round-25/a2-build/out/ExecCapacityTool/receipt/context-capacity-receipt.json
```
Output: `registered 14 observed 14 bound True missing []` (exit 0). The
`bound` check passed on `server_version` containing `build 11755` and
`model_sha256 == 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.

## Observed cells (receipt rows)

| id | args | props_n_ctx | total_slots | slots_n_ctx | pool (kv_pool_n_ctx) |
|---|---|---|---|---|---|
| K1 | `-c 0` | 2048 | 4 | 4×2048 | 2048 |
| K2 | `-c 2048 -np 2 --no-kv-unified` | 1024 | 2 | 2×1024 | 2048 |
| K3 | `-c 2048 -np 2 --kv-unified` | 2048 | 2 | 2×2048 | 2048 |
| K4 | `-c 1024 -np 1` | 1024 | 1 | 1×1024 | 1024 |
| K5 | `-c 4096 -np 1` | 2048 | 1 | 1×2048 | 4096 |
| K6 | `-c 1000 -np 3 --no-kv-unified` | 512 | 3 | 3×512 | 1536 |
| K7 | `-np 2 --kv-unified-per-slot 512` | 512 | 2 | 2×512 | 1024 |
| K8 | `-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512` | 512 | 4 | 4×512 | 4096 |
| X1 | `-np 4 --no-kv-unified` | 2048 | 4 | 4×2048 | 8192 |
| X2 | `-c 8192 -np 4 --no-kv-unified` | 2048 | 4 | 4×2048 | 8192 |
| X3 | `-np 4 --no-kv-unified --fit off` | 512 | 4 | 4×512 | 2048 |
| L1 | `-c 0` concurrent | 2048 | 4 | 4×2048 | 2048 |
| L2 | `-c 8192 -np 4 --no-kv-unified` concurrent | 2048 | 4 | 4×2048 | 8192 |
| L3 | `-c 0` sequential | 2048 | 4 | 4×2048 | 2048 |

Every cell's `models_n_ctx_train` is 2048. The K6 rounding line was captured:
`llama_context: n_ctx is not divisible by n_seq_max - rounding down to 1536`
(also matching the "../../ warning line).

Load cells (requests each: prompt_tokens 1000, n_predict 600):

- L1: both requests HTTP 500, error text `Context size has been exceeded.` —
  the shared 2048 pool cannot hold 2 × 1600 cells; prediction (at least one
  error) matched.
- L2: both HTTP 200, `tokens_predicted 600` each.
- L3: both HTTP 200, `tokens_predicted 600` each (sequential on `-c 0`).

## Sources opened this round (fetched fresh 2026-10-22, pinned commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad)

- `src/llama-context.cpp` — URL `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp` (sha256 `2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5`). Lines 379-383: "if (cparams.kv_unified) { cparams.n_ctx_seq = cparams.n_ctx; } else { cparams.n_ctx_seq = cparams.n_ctx / cparams.n_seq_max;" ; line 383: `cparams.n_ctx_seq = GGML_PAD(cparams.n_ctx_seq, 256);` ; lines 389-391: "n_ctx is not divisible by n_seq_max - rounding down to %u" ; line 396: `LLAMA_LOG_INFO("%s: n_ctx                 = %u\n", __func__, cparams.n_ctx);` — the source of the `llama_context: n_ctx = N` pool line (note the aligned spacing: `n_ctx                 =`).
- `common/fit.cpp` — URL `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp` (sha256 `1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58`). Lines 195-197: "with non-unified kv, we need to take into account n_streams" and `const uint32_t n_streams = cparams->kv_unified ? 1 : std::max<uint32_t>(1, cparams->n_seq_max);` ; line 267: `const uint32_t n_ctx_max = (uint32_t) std::min<uint64_t>(uint64_t(hp_nct) * n_streams, UINT32_MAX);` ; lines 270-272: "if (n_ctx_auto) { cparams->n_ctx = n_ctx_max;".
- `tools/server/server-context.cpp` — URL `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp` (sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`). Line 1392: `SRV_INF("initializing, n_slots = %d, n_ctx_slot = %d, kv_unified = '%s'\n", ...)` ; lines 1395-1397: `n_ctx_capped` / capping warning "the slot context (%d) exceeds the training context of the model (%d) - capping" ; line 4301: `err = "Context size has been exceeded.";` ; lines 3665-3681: exceeded-context errors `"input (%d tokens) is larger than the max context size (%d tokens). skipping"` and `"request (%d tokens) exceeds the available context size (%d tokens), try increasing it"` ; lines 5737-5746: `/tokenize` handler (`body.at("content")`, `tokenize_mixed`).
- `tools/server/server.cpp` — URL `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp` (sha256 `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4`). Lines 169-173: "n_parallel is set to auto, using n_parallel = 4 and kv_unified = true" ; lines 179-186: `ctx_pool_auto_sized` / `--kv-unified-per-slot: sizing KV pool to n_parallel * kv_unified_per_slot = %d * %d = %d` ; line 285: `ctx_http.post("/completion", ...)` (legacy) ; line 305: `ctx_http.post("/tokenize", ...)`.
- `tools/server/server-common.cpp` — URL `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp` (sha256 `b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442`). Lines 1092-1093: array-of-numbers prompt (`json_is_array_of_numbers`) is used verbatim as tokens (no special tokens added) — basis for sending the 1000 token ids directly.

All fetched bytes matched the lane's pinned round-16 snapshot digests where the
snapshot holds the same file (server-context.cpp, server-http.cpp, server.cpp).

## Notes / risks

- X1 (`-np 4 --no-kv-unified`, fit on) log contains three `llama_context:
  n_ctx` lines: 2048 (the fit measurement context, before fit set the unset
  context), then 8192, 8192 (the serving pools). The receipt's
  `kv_pool_n_ctx` is the **last** value (8192), which is the one consistent
  with `props_n_ctx 2048` × 4 slots in non-unified mode; all candidates are
  kept in `kv_pool_candidates` for transparency.
- The K1-K8 observations reproduce the pilot rows; X1/X3 confirm the fit
  mechanism: fit raises the unset non-unified context to 8192 (pool) / 2048
  (per-slot), while `--fit off` leaves it at 2048 / 512. X2's surfaces equal
  K1's per-slot values with an 8192 pool (per-slot n_ctx of 2048 does not
  reveal pool size; only the log does).
- No tool installs or updates were performed this seat (fetch-only; python3,
  curl, ss, pgrep already present).
- Blocker: none. All children killed; ports 47400-47419 confirmed closed
  (`ss -ltn` no matches after the run; `pgrep -x llama-server` empty).
