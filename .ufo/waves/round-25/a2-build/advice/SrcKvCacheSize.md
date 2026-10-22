# SrcKvCacheSize — advice report (C2 sourced claim, round 25 attempt 2)

Verdict: llama.cpp `src/llama-kv-cache.cpp` at 704366d76 is a new, needed source row (no existing SOURCES row) — fetched fresh, byte-verified, quote located; it establishes stream/cell structure and the `llama_kv_cache: size` log line, and does not establish n_ctx→kv_size derivation.

## 1. Fetch evidence
- Command: `curl -sS -o /fast/scratch/hyaku/kama-r25a2/SrcKvCacheSize/llama-kv-cache.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp` — exit 0.
- Size 98638 bytes, 2962 lines. sha256 `d0739eaf00d8457f4109a616e0beb1cf07ea074c9b460d92a7b6d48c4519d294`.
- Git blob SHA-1 `b7dfadef4638f6221608f48aff0a1f83df281063` matches the GitHub contents API for that ref (name, size 98638) — byte-identical to the pinned commit.
- The round-16 lane pin dir `.ufo/waves/round-16/sources/llama.cpp-704366d/` contains no `llama-kv-cache.cpp` (verified with find), so no lane pin was available to diff; the GitHub API check substitutes.

## 2. Constructor findings (path:line)
- `llama-kv-cache.cpp:84` — `n_seq_max(n_seq_max), n_stream(unified ? 1 : n_seq_max)`; stream count is 1 when unified, else n_seq_max.
- `:135` — `GGML_ASSERT(n_stream == 1 || n_stream == n_seq_max);`
- `:142-145` — every stream `s` gets `v_cells[s].resize(kv_size)` → per-stream cell count = kv_size.
- `:233-234` — K/V tensors are `ggml_new_tensor_3d(..., embd, kv_size, n_stream)` → total cells per layer = kv_size × n_stream.
- `:242-245` — per-stream views slice the 3d tensor on its 3rd dim.
- `:301-304` — log line `%s: size = %7.2f MiB (%6u cells, %3d layers, %2u/%u seqs), K (%s): %7.2f MiB, V (%s): %7.2f MiB` with arguments cells=`kv_size`, layers, `n_seq_max`/`n_stream`. So "cells" in the log is the per-stream count; "%2u/%u seqs" is n_seq_max/n_stream.
- `:92-98` — when a shared source cache (`other`) exists, `kv_size` is overridden to the source size with a WARN (relevant where a fitted target shares cells with a draft).
- `:1221-1233` — `get_size()` returns per-stream cells (`v_cells[seq_to_stream[0]].size()`); `get_n_stream()` returns `n_stream`.

## 3. SOURCES check
- `grep -n "llama-kv-cache" corpus/SOURCES.md` → no matches; also no `kv-cache|kv_cache|KvCache|nctx-crosscheck` matches. No existing row on this file.
- Adjacent but different: S060 covers `tools/server/server-context.cpp` (per-slot served context vs n_ctx_train metadata). A new row is needed; the draft does not modify SOURCES.md.

## 4. Draft row
Written to `out/SrcKvCacheSize/draft-row.md` (id `S1xx`, status queued, 11 columns exactly as SOURCES.md header line 11).

## 5. Gate record
Written to `out/SrcKvCacheSize/gate-record.md`: URL (blob + raw), access date 2026-10-22, fetch command + exit 0, sha256 + blob sha1 verification, quote `"size = %7.2f MiB (%6u cells, %3d layers, %2u/%u seqs), K (%s): %7.2f MiB, V (%s): %7.2f MiB"` at lines 301-304 (18 words).

## 6. Does-not-establish (also in `out/SrcKvCacheSize/does-not-establish.md`)
1. How kv_size derives from n_ctx and n_seq_max (this file takes kv_size as a parameter; n_ctx appears only for yarn, line 1952).
2. That n_seq_max equals the server's -np slot count (caller-supplied).
3. The `load_model: initializing, n_slots/n_ctx_slot` server line (emitted elsewhere).
4. Runtime slot behavior: sequence-to-stream mapping at request time, eviction/head reuse, tokens actually served.
5. What /props, /slots, /v1/models report (server surfaces; S060).
6. Actual fixture memory footprint (backend allocation + offload flag decide buffers).
7. That the b11755 binary executes this path identically (live observation is the C2 receipt).

## 7. Compliance
- No llama-server child started; no clone; no edits to SOURCES.md or any product file; no jj/git mutations.
- No tool installs/updates performed (curl and python3 already present; tooling directive: none to record).
- All written artifacts are under `out/SrcKvCacheSize/` and this advice report.
