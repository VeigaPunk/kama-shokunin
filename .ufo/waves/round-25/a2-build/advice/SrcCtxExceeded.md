# Advice — SrcCtxExceeded (round 25, attempt 2, C2 sourced claim)

Verdict: fresh fetch of `tools/server/server-context.cpp` @ 704366d76 (sha256 dd1de0f2…2329) confirms lines 4290-4345 implement batch-halving retries on KV-cache-full decode failure and, once n_batch == 1, send `Context size has been exceeded.` to every processing slot and abort; no existing SOURCES row covers this scope, so a new row (draft S1xx, queued) is needed.

## Observations

1. Fetch: `curl -fsSL -o server-context.cpp 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp'` — exit 0. 264205 bytes. `sha256sum` = `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`, byte-identical to the pinned-snapshot digest recorded in existing rows S042/S060 (so line numbers hold for the pinned commit).
2. The decode failure handling, `server-context.cpp` (fresh fetched copy at `/fast/scratch/hyaku/kama-r25a2/SrcCtxExceeded/server-context.cpp`):
   - `decode(int32_t & n_batch, int32_t off)` starts at line 4253; returns true = success, false = retry with smaller batch size, throws on fatal.
   - `llama_process(ctx_tgt, LLAMA_PROCESS_TYPE_DECODE, batch.view.get())` at 4288 returns `ret`; on `ret != 0` (4294):
     - `if (n_batch == 1 && ret == 1)` → `err = "Context size has been exceeded."` (4298-4301).
     - `ret == -1` → `"Invalid input batch."` (4304-4306); `ret < -1` → `"Compute error."` (4308-4311); `ret == 2` left as a TODO (4313).
     - If `err` non-empty (4315): log via `SRV_ERR` (4316); for every processing slot (4318-4327): `send_error(slot, err)` (4320), `slot.release()` (4321), `slot.prompt_clear()` (4325); then `throw std::runtime_error(err)` (4330), with comment `// stop, do not retry with smaller batch size` (4329).
     - Otherwise (err empty, i.e. `ret == 1` with n_batch > 1): `if (!try_clear_idle_slots()) { n_batch /= 2; }` (4334-4337), `SRV_WRN("failed to find free space in the KV cache, retrying with smaller batch size, …")` (4339), `return false;` (4341) — the caller loop (3331-3352) `continue`s with the updated n_batch (3351); on success n_batch is restored from `llama_n_batch(ctx_tgt)` (3348).
   - The throw is caught in `update_slots` (3353-3356): `SRV_ERR("decode() failed: …")`, `abort_all_slots("decode() failed: …")`, `break`.
   - `try_clear_idle_slots` (1810-1835) returns false immediately when `!params_base.kv_unified` (1813-1815); otherwise it purges (`prompt_clear`) at most one idle slot that has a prompt (1822-1830) and returns true — so halving is skipped if a purge succeeded.
   - `send_error(slot, err)` (4320) resolves to the slot overload (2166-2168) → `send_error(slot.task->id, error, ERROR_TYPE_SERVER, n_tokens, n_ctx)` (2170-2185), which queues a `server_task_result_error` with `err_type`/`err_msg` to `queue_results`; the HTTP status/body rendering is outside this file (not read).
3. Existing SOURCES rows on this file: S042 (health route body) and S060 (per-slot context metadata) — neither covers the KV-full decode error path. `grep` of `corpus` for `Context size has been exceeded` found no matches. A new row is required; no existing row covers it. (No edit to `corpus/SOURCES.md` was made.)
4. The amendment-2 L1 prediction anchors are independently confirmed by the fresh read: line 4301 (error string) and lines 4318-4320 (processing-slot send loop) match exactly, i.e. the L1's cited source lines exist at the pinned commit.

## Draft registry row (11-column format, id placeholder S1xx, status queued)

See `.ufo/waves/round-25/a2-build/out/SrcCtxExceeded/draft-row.md` for the exact single table row (next free id at draft time is S106; the L1 assigns the final id).

## Gate record

See `.ufo/waves/round-25/a2-build/out/SrcCtxExceeded/gate-record.md` — URL, access date 2026-10-22, sha256 dd1de0f2…2329, and located quotes with line numbers (4301; 4334; 4329).

## Does-not-establish list

1. No runtime observation — no llama-server child started; unrun means unverified. Source alone does not prove `llama_process` returns 1 exactly when the KV pool is full, nor that halving converges before n_batch == 1.
2. The HTTP status/body the client receives for the error is not established (rendering lives outside this file; not read).
3. The full effect of `try_clear_idle_slots` (purge vs halving) is runtime-dependent; only its code shape is read.
4. The complete error taxonomy is not established (`ret == 2` is an unhandled TODO at 4313).
5. Nothing about context sizing/fit (`common/fit.cpp`), per-slot n_ctx assignment, or KV pool sizing — covered by other lines / existing row S060.
6. Pinned to commit 704366d76 alone; no cross-build behavior, and no proof the installed b11755 binary matches this source byte-for-byte (release asset link is S038).
7. No claim about what HTTP surfaces `/props`, `/slots`, `/v1/models` display during these retries/errors.

## Files written (this seat)

- `.ufo/waves/round-25/a2-build/out/SrcCtxExceeded/draft-row.md`
- `.ufo/waves/round-25/a2-build/out/SrcCtxExceeded/gate-record.md`
- `.ufo/waves/round-25/a2-build/advice/SrcCtxExceeded.md` (this report)
- Scratch: `/fast/scratch/hyaku/kama-r25a2/SrcCtxExceeded/server-context.cpp` (fetched raw copy; no server child started, no ports used)

No lane production files were edited; no commands were run against the fleet repo outside read-only reads.
