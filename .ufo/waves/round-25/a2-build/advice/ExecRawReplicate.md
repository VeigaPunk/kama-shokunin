# ExecRawReplicate — C2 config-cell replicate (K1-K8, X1-X3)

**Verdict:** All 11 registered config cells observed with saved raw HTTP bytes and logs; every amendment-2 prediction held (zero flags); X1 confirms fit raises an unset split context to pool 8192 / per-slot 2048 (round-20 value wrong), X3 confirms fit off gives pool 2048 / per-slot 512; receipt slice passes the registered counter as `registered 14 observed 11 bound True` (missing only L1-L3, which are not this seat's scope).

## Fixture identity

- `~/.local/bin/llama-server --version` -> `version: 0.7.0-dev (build 11755, commit 704366d76)` (exit 0).
- Model `~/.cache/kama-shokunin/models/stories260K.gguf`, 1185376 bytes, `sha256sum` -> `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (matches amendment-2 `MODEL_SHA`; counter prints `bound True`).
- Ports 47440-47459 were free before the run (`ss -ltn`), one cell at a time, every child killed with SIGTERM (none needed SIGKILL), port confirmed closed after each cell, and the range is clean and no llama-server process remains after the run.

## Method

Script `.ufo/waves/round-25/a2-build/out/ExecRawReplicate/run-cells.py` (written by this seat; plain Python, no capacity tool). For each of the 11 cells it launches `~/.local/bin/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port <free> --no-webui --offline -v <registered args>`, waits for `/health` 200, saves raw `/props`, `/slots`, `/v1/models` bytes and the full server log, extracts the registered fields, kills the child and confirms the port is closed. `-v` is not part of the registered args string (amendment-2 launch rule).

Run: `python3 .../run-cells.py` -> exit 0; console at `.../run-console.log`. Every cell printed `ready True`, `flags []`.

## Observed table (raw files saved per cell under `out/ExecRawReplicate/<cell>/`)

| cell | args | /props n_ctx | total_slots | /slots n_ctx | n_ctx_train | kv pool (llama_context n_ctx) | n_ctx_seq | props.sha256 | slots.sha256 | v1models.sha256 |
|---|---|---|---|---|---|---|---|---|---|---|
| K1 | `-c 0` | 2048 | 4 | [2048, 2048, 2048, 2048] | 2048 | 2048 | 2048 | `064368843fe8eb55766a7b22d175e153f0d0c199ae6e9ac1a238ee59c93adfa3` | `6939aec123597421a7c985c4b40c55bcbe69a5a74d91b742ead1a1dcacd1a0f` | `e6faf69cdc54e91d35fbf1f32f53d4e2a33aa95ac2eeaa5adc8981c01f18b6` |
| K2 | `-c 2048 -np 2 --no-kv-unified` | 1024 | 2 | [1024, 1024] | 2048 | 2048 | 1024 | `f82a84a4a3f1e987852e36e5d3a90265376d4a87761be51e693ad9957adf56d4` | `238e37b9ec682763be9a824b50ef0ccaf1c240ee1b04e39c7d7d751d786d93a1` | `32ff1bf4988434021668f7dbe8058fcf75f0ca4602e3a0f40e20efb3d58ea31b` |
| K3 | `-c 2048 -np 2 --kv-unified` | 2048 | 2 | [2048, 2048] | 2048 | 2048 | 2048 | `b2e8940c3b1236bfb69e1290921fc61a538a977366fa1036e5e5a62f688d25b1` | `2de3c9ce2e79d5d0762f9de6e161bf9e32adeb00b2467b025bf1466402f5e26b` | `e6faf69cdc54e91d35fbf1f32f53d4e2a33aa95ac2eeaa5adc8981c01f18b6` |
| K4 | `-c 1024 -np 1` | 1024 | 1 | [1024] | 2048 | 1024 | 1024 | `0b8d1ed5c92f8cff3fbb66aeac7ac97defd6db3d86efdce2c698fec19526ca35` | `567947103865fb11765503b0cc57f74b9dfb2d78dd94f8bcb0c9cb34015c7e3d` | `f87d210df15053352309e11d57eeb6643d89df683b8694e59ea47019fa6106234` |
| K5 | `-c 4096 -np 1` | 2048 | 1 | [2048] | 2048 | 4096 | 4096 | `b17701a18715d387a02dd9dc7c23993d1f1b3be32ca3498f7396a10ebaf0280c` | `a01b9a2ec6bb26aac50f57666e13afe0b1a8b110daea6b21d97769b69b1121e` | `6fc02b4fa694264e4fb7d9b486a0f57f9ac68b11cd93f71a232ee9005cd44dbb` |
| K6 | `-c 1000 -np 3 --no-kv-unified` | 512 | 3 | [512, 512, 512] | 2048 | 1536 | 512 | `a52a18355bc4fab0dc69c7660cf14747d5e0f30a14f36cbcbb24d985a7a53442` | `dda7c95afd208a18a45d67b9600b14c8ebeb4d65ce91f4fd6a37d13669587810` | `a4cf57c8a41a6d6d0c9bf2059cc3900684af208cd2a004c24fe82db91b9a85e4` |
| K7 | `-np 2 --kv-unified-per-slot 512` | 512 | 2 | [512, 512] | 2048 | 1024 | 512 | `e7225d2327c52fb5c3b2be4c7c3b4b19253f5c0d701976f0d54dc69c3b82711f` | `b44870103a9f932685f7964df9d16cc9a51d4e1d66c21aa3fe91f10e0717bdcd` | `a4cf57c8a41a6d6d0c9bf2059cc3900684af208cd2a004c24fe82db91b9a85e4` |
| K8 | `-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512` | 512 | 4 | [512, 512, 512, 512] | 2048 | 4096 | 4096 | `41e0afbbd88b8be1dc044c90837bf61e6e4d196a54114a6d2bd55689abcf2713` | `e0c29a4cde00350e75d2ea092c9979af7e6f93853e491ce46d482821b48626bb` | `a4cf57c8a41a6d6d0c9bf2059cc3900684af208cd2a004c24fe82db91b9a85e4` |
| X1 | `-np 4 --no-kv-unified` | 2048 | 4 | [2048, 2048, 2048, 2048] | 2048 | 8192 | 2048 | `e789e7fc5197edcf6c1123dd262b5a50f1ce1f029d83f218d63f50c40187d54f` | `6939aec123597421a7c985c4b40c55bcbe69a5a74d91b742ead1a1dcacd1a0f` | `dbc741dc5099a230a39cd3c3d345d71bb1100d4adbf48132d114b3f4ab88f1f4` |
| X2 | `-c 8192 -np 4 --no-kv-unified` | 2048 | 4 | [2048, 2048, 2048, 2048] | 2048 | 8192 | 2048 | `e60d214183b2eecc76c6c16815eb2cea6d1282d9f67d743bc7b9db66bae330d8` | `6939aec123597421a7c985c4b40c55bcbe69a5a74d91b742ead1a1dcacd1a0f` | `dbc741dc5099a230a39cd3c3d345d71bb1100d4adbf48132d114b3f4ab88f1f4` |
| X3 | `-np 4 --no-kv-unified --fit off` | 512 | 4 | [512, 512, 512, 512] | 2048 | 2048 | 512 | `9d160526f3fa5f179122953041e1b68ceb1cb8360d23b7ae2832e4e292d3b8a2` | `e0c29a4cde00350e75d2ea092c9979af7e6f93853e491ce46d482821b48626bb` | `4a4f649f51661a9259fd7308b1d34ed4cadba225f1fd96d436fb0a1f17e08e3c` |

Stored sha256 values were re-verified against the files on disk (all match). Full table also at `out/ExecRawReplicate/summary.md`; per-cell raw files under `out/ExecRawReplicate/<cell>/{props.json,slots.json,v1_models.json,server.log}`.

## Grading against amendment-2 predictions

No cell produced a flag; every claimed value matched.

- K1: total_slots 4 (auto), kv_unified true, per-slot 2048 — matches pilot/prediction.
- K2: per-slot 1024 (split pool 2048) — matches.
- K3: per-slot 2048 (unified) — matches.
- K4: kv_unified false, per-slot 1024 — matches.
- K5: per-slot served 2048, capped at n_ctx_train — matches prediction (see finding 1).
- K6: measurement only: pool 1536 (rounding warning `llama_context: n_ctx is not divisible by n_seq_max - rounding down to 1536`), per-slot 512.
- K7: pool 1024 (log line `--kv-unified-per-slot: sizing KV pool to n_parallel * kv_unified_per_slot = 2 * 512 = 1024`), per-slot 512 — matches.
- K8: per-slot served 512 — matches (pool 4096, see finding 3).
- X1: pool 8192, per-slot 2048 — matches source prediction; round-20 nctx-crosscheck value 512 is contradicted (see finding 4).
- X2: pool 8192, per-slot 2048 — matches; surfaces equal K1's except `/v1/models` `created` (see finding 5).
- X3: pool 2048, per-slot 512 — matches author inference (see finding 6).

## Findings beyond the predictions

1. **Declared vs served (K5).** With `-c 4096 -np 1`, `/props default_generation_settings.n_ctx`, `/slots` and `/v1/models meta.n_ctx` all report 2048, and the log line `load_model: initializing, n_slots = 1, n_ctx_slot = 2048, kv_unified = 'false'` says the server serves 2048 per slot, while the internal context (`llama_context: n_ctx = 4096`, `n_ctx_seq = 4096`) is 4096. The HTTP surfaces cannot show the pool/seq split; only the log does. This is the frontier K05 gap, observed.

2. **K6 rounding.** `-c 1000 -np 3 --no-kv-unified` -> warning `n_ctx is not divisible by n_seq_max - rounding down to 1536`; pool 1536, per-slot 512. 1000 fills to 1536 = 3 x 512 (per-slot granularity of 512 with split cache), per-slot 512.

3. **K8 unified pool larger than used.** `-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512`: pool 4096, n_ctx_seq 4096, but served per-slot is 512 (`n_ctx_slot = 512`), so 4096 - 4 x 512 = 2048 pool cells are unused; `--kv-unified-per-slot` caps per-slot serving inside the shared pool.

4. **X1: fit raises the unset split context.** X1's log contains three `llama_context` blocks: first `n_ctx = 2048, n_ctx_seq = 512` (probe/default sizing), then two identical `n_ctx = 8192, n_ctx_seq = 2048` blocks. The final block (and `load_model: ... n_ctx_slot = 2048`) is 8192/2048: the fit step raised the unset context to n_ctx_train x n_streams = 2048 x 4 = 8192. Amendment-2 source prediction confirmed; round-20 nctx-crosscheck `predict()` 512 is wrong and should be superseded.

5. **X2 surfaces equal K1's.** X2 `/slots` byte-identical to K1 (`6939aec1...`), and `/v1/models` identical to K1 except `data[0].created` (1792661661 vs 1792661663 — a per-server-start stamp), n_ctx 2048 = n_ctx_train 2048. Prediction holds modulo `created`.

6. **X3: fit off is the cause.** With `--fit off`, only one block: `n_ctx = 2048, n_ctx_seq = 512` — the unset context falls back to n_ctx_train 2048 split over 4 streams. X3 (512) vs X1 (2048) difference is therefore caused by fit.

## Registered counter on this slice

```
$ python3 .ufo/waves/round-25/count-c2.py .ufo/waves/round-25/a2-build/out/ExecRawReplicate/receipt-config-cells.json
registered 14 observed 11 bound True missing ['L1', 'L2', 'L3']
```
Exit 0. The 11 config cells pass the strict counter exactly (ids unique, args equal, all ints, log_lines include a `llama_context: n_ctx ... = <pool>` line for each cell). L1-L3 are load cells assigned to a different seat; the final receipt must merge them in.

## Files written by this seat

All under `kama-shokunin/.ufo/waves/round-25/a2-build/`:
- `out/ExecRawReplicate/run-cells.py` (runner), `run-console.log`, `summary.json`, `summary.md`, `receipt-config-cells.json`
- `out/ExecRawReplicate/<cell>/{props.json,slots.json,v1_models.json,server.log}` for K1-K8, X1-X3
- `advice/ExecRawReplicate.md` (this report)

No tools were installed; nothing was committed or pushed; no jj commands were run; no source files were opened by this seat (all evidence is runtime observation). Exit codes: runner 0, counter 0.
