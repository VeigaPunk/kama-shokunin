# Gate record — SrcCtxExceeded (round 25, attempt 2)

## Fetch
- File: `tools/server/server-context.cpp`
- Commit pin: `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (release b11755)
- GitHub page: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp
- Raw fetch: https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp
- Access date: 2026-10-22
- Command: `curl -fsSL -o server-context.cpp '<raw url>'`
- Size: 264205 bytes
- **sha256: `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`**
- Byte-identical to the lane's pinned snapshot digest already recorded in S042/S060 (`dd1de0f2…2329`), so line numbers below hold for the pinned commit.

## Located quotes (each ≤ 25 words, with line numbers)
1. Line 4301 (error sent when a single-token batch still fails):
   `err = "Context size has been exceeded."` — guarded by line 4298 `if (n_batch == 1 && ret == 1)`.
2. Line 4334 (batch-halving retry comment):
   `// retry with half the batch size to try to find a free slot in the KV cache`
   — implemented 4335-4337: `if (!try_clear_idle_slots()) { n_batch /= 2; }`.
3. Line 4329 (no further retry once the error is set):
   `// stop, do not retry with smaller batch size` — followed by `throw std::runtime_error(err);` at 4330.

## What the source does NOT establish (does-not-establish list)
1. No runtime behavior is observed — the file was read only; nothing was run (no llama-server child started). It does not prove `llama_process` returns 1 exactly when the KV pool is full, nor that halving converges before n_batch == 1.
2. It does not establish the HTTP status or body the client receives: `send_error` (2177-2184) only queues a `server_task_result_error` with `err_type`/`err_msg`; the HTTP rendering lives outside this file and was not read.
3. It does not establish what happens when `try_clear_idle_slots` returns true (halving skipped): that helper (1810-1835) only acts when `kv_unified` is true (1813-1815) and purges at most one idle slot with a prompt per call (1829-1830), so its full effect is runtime-dependent.
4. It does not establish the complete error taxonomy: `ret == 2` (abort) is an unhandled TODO comment (4313); only ret == 1 at n_batch == 1, ret == -1 and ret < -1 map to messages.
5. It does not establish anything about context sizing/fit (`common/fit.cpp`), per-slot n_ctx assignment, or KV pool sizing — those are other lines, partly covered by existing row S060.
6. It pins only commit 704366d76; it does not establish behavior of other builds, nor that the installed b11755 binary matches this source byte-for-byte (that link is the release asset row S038).
7. It does not establish what the HTTP surfaces `/props`, `/slots`, `/v1/models` show while these retries/errors happen; that is runtime observation, out of source scope.

## Files written (this seat)
- `.ufo/waves/round-25/a2-build/out/SrcCtxExceeded/draft-row.md`
- `.ufo/waves/round-25/a2-build/out/SrcCtxExceeded/gate-record.md`
- `.ufo/waves/round-25/a2-build/advice/SrcCtxExceeded.md`
- Scratch (heavy): `/fast/scratch/hyaku/kama-r25a2/SrcCtxExceeded/server-context.cpp` (fetched raw copy)
