# ExecSharedPool8192 — per-run table (unregistered supporting cells)

Lane: kama-shokunin, round 25 wave 2 (falsify). Fixture: stories260K.gguf, 
sha256 270cba1b…256d, llama-server build 11755 (commit 704366d76f). 
Ports 47420-47439 on 127.0.0.1, one child at a time, every child reaped and every port confirmed closed.

Request pair (L1 shape, reused by import from `tools/kama-context-capacity.py`): two concurrent 
POST /completion, each a 1000-token prompt as a flat list of token ids, n_predict 600, 
ignore_eos true, cache_prompt false, stream false.

| run | args | port | KV pool (last `llama_context: n_ctx`) | /props n_ctx | slots | /slots n_ctx | statuses | tokens predicted | truncated | error | start gap ms | overlap s | observed | port closed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | `-c 8192 -np 4 --kv-unified` | 47420 | 8192 | 2048 | 4 | [2048, 2048, 2048, 2048] | [200, 200] | [600, 600] | [False, False] |  | 0.126 | 0.2133 | True | True |
| S2 | `-c 8192 -np 4 --kv-unified` | 47421 | 8192 | 2048 | 4 | [2048, 2048, 2048, 2048] | [200, 200] | [600, 600] | [False, False] |  | 0.096 | 0.2099 | True | True |
| S3 | `-c 8192 -np 4 --kv-unified` | 47422 | 8192 | 2048 | 4 | [2048, 2048, 2048, 2048] | [200, 200] | [600, 600] | [False, False] |  | 0.090 | 0.2047 | True | True |
| D2048 | `-c 2048 -np 4 --kv-unified` | 47420 | 2048 | 2048 | 4 | [2048, 2048, 2048, 2048] | [500, 500] | [None, None] | [None, None] | Context size has been exceeded.; Context size has been exceeded. | 0.160 | 0.0215 | True | True |
| D3072 | `-c 3072 -np 4 --kv-unified` | 47421 | 3072 | 2048 | 4 | [2048, 2048, 2048, 2048] | [500, 500] | [None, None] | [None, None] | Context size has been exceeded.; Context size has been exceeded. | 0.147 | 0.1808 | True | True |
| D4096 | `-c 4096 -np 4 --kv-unified` | 47422 | 4096 | 2048 | 4 | [2048, 2048, 2048, 2048] | [200, 200] | [600, 600] | [False, False] |  | 0.100 | 0.2019 | True | True |
| D8192PS512 | `-c 8192 -np 4 --kv-unified --kv-unified-per-slot 512` | 47420 | 8192 | 512 | 4 | [512, 512, 512, 512] | [400, 400] | [None, None] | [None, None] | request (1000 tokens) exceeds the available context size (512 tokens), try increasing it; request (1000 tokens) exceeds the available context size (512 tokens), try increasing it | 0.135 | 0.0008 | True | True |

Committed comparison rows (from `.ufo/waves/round-25/final/context-capacity-receipt.json`, not re-run here):

| cell | args | KV pool | /props n_ctx | slots | statuses | tokens | truncated |
|---|---|---|---|---|---|---|---|
| L1 | `-c 0` | 2048 | 2048 | 4 | 500, 500 | None | None |
| L2 | `-c 8192 -np 4 --no-kv-unified` | 8192 | 2048 | 4 | 200, 200 | 600, 600 | false, false |
| L3 | `-c 0 (sequential)` | 2048 | 2048 | 4 | 200, 200 | 600, 600 | false, false |
