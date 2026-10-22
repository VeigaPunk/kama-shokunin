# ExecLoadReplicate — C2 L1-L3 load replicate (round 25 attempt 2)

Verdict: all three L cells reproduced the amendment-2 predictions exactly and stably over 3 fresh-server repetitions each — L1 (concurrent, `-c 0`): both requests fail HTTP 500 `Context size has been exceeded.` (shared 2048 KV pool cannot hold 2 x 1600); L2 (concurrent, `-c 8192 -np 4 --no-kv-unified`): both requests complete HTTP 200 with 600 tokens each (four independent 2048 streams in an 8192 pool); L3 (sequential, `-c 0`): both requests complete HTTP 200 with 600 tokens each (same shared 2048 pool, one at a time). No capacity tool used.

## Method (this seat's own harness)

- Harness: `.ufo/waves/round-25/a2-build/out/ExecLoadReplicate/load_replicate.py` (Python 3.14 stdlib only; `urllib` in two threads for concurrency, strictly serial send for L3).
- Fixture launch per rep, one child at a time:
  `~/.local/bin/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port <47420-47428> --no-webui --offline -v <registered args>`.
- Fixture identity: `~/.local/bin/llama-server --version` -> `version: 0.7.0-dev (build 11755, commit 704366d76)` (exit 0); model `stories260K.gguf` sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (matches registered).
- Prompt: `POST /tokenize` with "The quick brown fox jumps over the lazy dog. " x 4000; first 1000 token ids used as prompt (`prompt_tokens_used 1000` verified per run).
- Requests: `POST /completion` body `{"prompt":[1000 token ids],"n_predict":600,"ignore_eos":true,"cache_prompt":false}`. L1/L2: two threads start simultaneously; L3: second request sent only after first response returned.
- Each cell x 3 reps, each rep on a freshly started server; server killed and port confirmed closed (`ss -ltn`) after every rep.
- Attempt-1 outputs were not reused (per disposition they are unverified); every value below is a fresh observation from this seat's runs.

## Per-run table (acceptance; same table in `out/ExecLoadReplicate/runs.md`)

| cell | rep | port | mode | /props n_ctx | slots n_ctx | /v1/models n_ctx_train | kv pool (log) | req | HTTP status | error text | tokens_predicted | timings predicted_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 | 1 | 47420 | concurrent | 2048 | [2048,2048,2048,2048] | 2048 | 2048 | 0 | 500 | Context size has been exceeded. | None | None |
| L1 | 1 | 47420 | concurrent | 2048 | [2048,2048,2048,2048] | 2048 | 2048 | 1 | 500 | Context size has been exceeded. | None | None |
| L1 | 2 | 47421 | concurrent | 2048 | [2048,2048,2048,2048] | 2048 | 2048 | 0 | 500 | Context size has been exceeded. | None | None |
| L1 | 2 | 47421 | concurrent | 2048 | [2048,2048,2048,2048] | 2048 | 2048 | 1 | 500 | Context size has been exceeded. | None | None |
| L1 | 3 | 47422 | concurrent | 2048 | [2048,2048,2048,2048] | 2048 | 2048 | 0 | 500 | Context size has been exceeded. | None | None |
| L1 | 3 | 47422 | concurrent | 2048 | [2048,2048,2048,2048] | 2048 | 2048 | 1 | 500 | Context size has been exceeded. | None | None |
| L2 | 1 | 47423 | concurrent | 2048 | [2048,2048,2048,2048] | 2048 | 8192 | 0 | 200 | (none) | 600 | 182.168 |
| L2 | 1 | 47423 | concurrent | 2048 | [2048,2048,2048,2048] | 2048 | 8192 | 1 | 200 | (none) | 600 | 182.203 |
| L2 | 2 | 47424 | concurrent | 2048 | [2048,2048,2048,2048] | 2048 | 8192 | 0 | 200 | (none) | 600 | 184.843 |
| L2 | 2 | 47424 | concurrent | 2048 | [2048,2048,2048,2048] | 2048 | 8192 | 1 | 200 | (none) | 600 | 184.792 |
| L2 | 3 | 47425 | concurrent | 2048 | [2048,2048,2048,2048] | 2048 | 8192 | 0 | 200 | (none) | 600 | 189.363 |
| L2 | 3 | 47425 | concurrent | 2048 | [2048,2048,2048,2048] | 2048 | 8192 | 1 | 200 | (none) | 600 | 189.395 |
| L3 | 1 | 47426 | sequential | 2048 | [2048,2048,2048,2048] | 2048 | 2048 | 0 | 200 | (none) | 600 | 122.130 |
| L3 | 1 | 47426 | sequential | 2048 | [2048,2048,2048,2048] | 2048 | 2048 | 1 | 200 | (none) | 600 | 122.663 |
| L3 | 2 | 47427 | sequential | 2048 | [2048,2048,2048,2048] | 2048 | 2048 | 0 | 200 | (none) | 600 | 117.960 |
| L3 | 2 | 47427 | sequential | 2048 | [2048,2048,2048,2048] | 2048 | 2048 | 1 | 200 | (none) | 600 | 119.830 |
| L3 | 3 | 47428 | sequential | 2048 | [2048,2048,2048,2048] | 2048 | 2048 | 0 | 200 | (none) | 600 | 117.136 |
| L3 | 3 | 47428 | sequential | 2048 | [2048,2048,2048,2048] | 2048 | 2048 | 1 | 200 | (none) | 600 | 122.985 |

Notes: every successful response carried `tokens_predicted 600`, `timings.predicted_n 600`, content length 1242-1383 chars; the response JSON did not surface a `finished_reason` field for these params, so it is recorded as absent (no fabrication). Error responses carried no content and no timings.

## Stability verdict per cell

- **L1: STABLE.** 3/3 reps identical: both concurrent requests fail HTTP 500 with exactly `Context size has been exceeded.`; zero tokens predicted; failure occurs at decode of the first new token after both prompts were fully loaded (both slots released at n_tokens = 1025, i.e. 1000 prompt + 25 generated). Failure is a pool-capacity event, not a request-size event.
- **L2: STABLE.** 3/3 reps identical: both concurrent requests succeed HTTP 200 with 600 tokens each; per-request predicted_ms 182-189, elapsed ~0.20-0.21 s. Log pool `llama_context: n_ctx = 8192`, `n_ctx_seq = 2048`; `/props` n_ctx 2048 and `/slots` 4 x 2048 equal K1's shape despite the 8192 pool (pool size is visible only in the log).
- **L3: STABLE.** 3/3 reps identical: both sequential requests succeed HTTP 200 with 600 tokens each; per-request predicted_ms 117-123, elapsed ~0.126-0.131 s. Same fixture config as L1; the same requests that fail when concurrent succeed one after the other.

## Log excerpts (exact, from scratch logs)

L1 failure sequence, `/fast/scratch/hyaku/kama-r25a2/ExecLoadReplicate/L1-rep1.log`:

```
1737: W decode: failed to find a memory slot for batch of size 2
1739: W srv decode: failed to find free space in the KV cache, retrying with smaller batch size, off = 0, n_batch = 1024, ret = 1
... (retry loop halves n_batch 1024 -> 512 -> 256 -> 128 -> 64 -> 32 -> 16 -> 8 -> 4 -> 2 -> 1)
1827: E srv decode: Context size has been exceeded. off = 0, n_batch = 1, ret = 1
1828: E srv send_error: task id = 2, error: Context size has been exceeded.
1831: I slot release: id 0 | task 2 | stop processing: n_tokens = 1025, truncated = 0
1833: I slot prompt_clear: id 0 | task -1 | clearing prompt with 1025 tokens
1834: E srv send_error: task id = 1, error: Context size has been exceeded.
1837: I slot release: id 1 | task 1 | stop processing: n_tokens = 1025, truncated = 0
1839: I slot prompt_clear: id 1 | task -1 | clearing prompt with 1025 tokens
1840: E srv update_slots: decode() failed: Context size has been exceeded.
```

L2 (pool split) log lines, `L2-rep1.log` lines 283-285 and 1081:

```
283: I llama_context: n_ctx = 8192
284: I llama_context: n_ctx_seq = 2048
1081: I srv load_model: initializing, n_slots = 4, n_ctx_slot = 2048, kv_unified = 'false'
```

L1/L3 (unified pool) log lines, `L1-rep1.log` lines 284-285 and 1082:

```
284: I llama_context: n_ctx = 2048
285: I llama_context: n_ctx_seq = 2048
1082: I srv load_model: initializing, n_slots = 4, n_ctx_slot = 2048, kv_unified = 'true'
```

## Sources opened (fresh fetch, pinned, accessed 2026-10-22)

- `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp` (sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`; byte-identical to the round-16 pinned snapshot).
  - Line 4301: `err = "Context size has been exceeded.";`
  - Lines 4318-4320: `for (auto & slot : slots) {` / `if (slot.is_processing()) {` / `send_error(slot, err);` — the observed error text and its broadcast to every processing slot match these source lines (>=25-words quote kept minimal).

## Files written

All under `.ufo/waves/round-25/a2-build/out/ExecLoadReplicate/`:
- `load_replicate.py` (harness; executable)
- `runs.json` (full per-run records: props, slots, kv pool/seq, requests with status/error/tokens_predicted/timings/elapsed, log_lines, failure excerpts, port_closed)
- `runs.md` (per-run acceptance table, above)
- `l-cells-receipt.json` (aggregate per-cell receipt-shape for L1-L3)

Scratch logs: `/fast/scratch/hyaku/kama-r25a2/ExecLoadReplicate/{L1,L2,L3}-rep{1,2,3}.log`.

Aggregate validation with the registered counter (run from kama-shokunin root):

```
$ python3 .ufo/waves/round-25/count-c2.py .ufo/waves/round-25/a2-build/out/ExecLoadReplicate/l-cells-receipt.json
registered 14 observed 3 bound True missing ['K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'X1', 'X2', 'X3']
exit=0
```

The three L cells satisfy the strict load-cell rules (request_mode, >=2 requests with int status, prompt_tokens 1000, n_predict 600, kv_pool_n_ctx matching a captured `llama_context: n_ctx` log line).

## Tooling

No tool installs performed (used existing system `python3` 3.14.8 and `curl` 8.23.0; nothing installed or updated).

## Ports / teardown

Used 47420-47428 (assigned range 47420-47439, 127.0.0.1 only). After all runs, `ss -ltn | grep -E "474[0-3][0-9]"` found no listeners (grep exit 1). One unrelated listener `127.0.0.1:47446` was observed after the runs; it is outside the assigned range, was not started by this seat, and was not touched or probed.

## Risks / notes for the integrator

- The harness's first pass (before the kv regex fix) produced identical HTTP/behavior results; only the kv_pool_n_ctx parse was missing, and the parse was fixed before the second, final pass. Both passes are in the scratch logs; the committed artifacts come from the final pass.
- L1's failure is deterministic and symmetric: both slots fail, each at n_tokens = 1025 (1000 prompt + 25 decoded), consistent with a shared 2048 pool filling at ~2 x 1025 = 2050 within reclamation slack.
- The HTTP surface cannot show the KV pool size: `/props`, `/slots` and `/v1/models` read per-slot values in every L cell; only the log `llama_context: n_ctx` line shows the pool (2048 unified vs 8192 split).
