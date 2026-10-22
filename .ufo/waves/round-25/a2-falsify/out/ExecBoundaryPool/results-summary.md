# ExecBoundaryPool — wave-2 falsification of the C2 pool arithmetic

Claim attacked (`corpus/knowledge/context-capacity.md`, L1 cell):
"In L1 both slots were released at `n_tokens = 1025`
(`.ufo/waves/round-25/final/raw/L1.server.log` lines 1849-1866): 2 x 1025
cells overflow the 2048 pool."

Target (unregistered supporting boundary pair on the L1 config `-c 0`): two
concurrent 1000-token prompts with `n_predict` 24 and with `n_predict` 30
(`ignore_eos` true, `cache_prompt` false, no streaming).

Harness: `exec-boundary-pool.py` (this directory), one `llama-server` child at
a time, 127.0.0.1 only, ports 47440-47459, every child SIGTERM'd and its port
proven closed (`port_refuses_after: true`, no listener left in range) before
the next run. Server: `~/.local/bin/llama-server` = build 11755, commit
704366d76; model `~/.cache/kama-shokunin/models/stories260K.gguf`.

Common to every run: KV pool 2048 (`llama_context: n_ctx = 2048`),
`load_model: initializing, n_slots = 4, n_ctx_slot = 2048, kv_unified = 'true'`,
prompt 1000 tokens per request, both requests overlapping (start gap
0.09-0.21 ms).

| run | n_predict | port | HTTP statuses | tokens_predicted | release `n_tokens` (slot 0, slot 1) | pool used at peak | outcome |
|---|---|---|---|---|---|---|---|
| np24-r1 | 24 | 47440 | 200, 200 | 24, 24 | 1023, 1023 | 2 x 1023 = 2046 | both pass |
| np24-r2 | 24 | 47441 | 200, 200 | 24, 24 | 1023, 1023 | 2 x 1023 = 2046 | both pass |
| np24-r3 | 24 | 47442 | 200, 200 | 24, 24 | 1023, 1023 | 2 x 1023 = 2046 | both pass |
| np25-r1 | 25 | 47447 | 200, 200 | 25, 25 | 1024, 1024 | 2 x 1024 = 2048 | both pass, zero slack |
| np25-r2 | 25 | 47450 | 200, 200 | 25, 25 | 1024, 1024 | 2 x 1024 = 2048 | both pass, zero slack |
| np26-r1 | 26 | 47448 | 500, 500 | none | 1025, 1025 | 2 x 1025 = 2050 | both fail |
| np26-r2 | 26 | 47440 | 500, 500 | none | 1025, 1025 | 2 x 1025 = 2050 | both fail |
| np26-r3 | 26 | 47449 | 500, 500 | none | 1025, 1025 | 2 x 1025 = 2050 | both fail |
| np27-r1 | 27 | 47446 | 500, 500 | none | 1025, 1025 | 2 x 1025 = 2050 | both fail |
| np30-r1 | 30 | 47443 | 500, 500 | none | 1025, 1025 | 2 x 1025 = 2050 | both fail |
| np30-r2 | 30 | 47444 | 500, 500 | none | 1025, 1025 | 2 x 1025 = 2050 | both fail |
| np30-r3 | 30 | 47445 | 500, 500 | none | 1025, 1025 | 2 x 1025 = 2050 | both fail |

Failing requests: HTTP 500, `error.type = server_error`,
`error.message = "Context size has been exceeded."` (both requests of the
pair, not only the newer one).

**Smallest failing n_predict = 26** (3 of 3 runs fail); 25 passes (2 of 2 runs).
