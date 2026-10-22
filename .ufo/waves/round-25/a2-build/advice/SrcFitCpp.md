# Advice — SrcFitCpp (round 25 attempt 2, C2 sourced claim: common/fit.cpp)

Verdict: fit.cpp @ 704366d76 confirms the amendment-2 X1 source path (unset
context fitted to n_ctx_train x n_streams for a split cache); one drafted
SOURCES row S1xx (queued), Gate record, sha256, and a five-item
does-not-establish list below.

## Observations (all fresh, accessed 2026-10-22)

- Fetch: `curl -fsSL -o fit.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp`
  — exit 0. File: 1113 lines. sha256:
  `1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58`
  (stored at /fast/scratch/hyaku/kama-r25a2/SrcFitCpp/fit.cpp).
- Pinned round-16 snapshot contains no fit.cpp (its dir lists README.md, arg.cpp,
  server-common.cpp/h, server-context.cpp, server-http.cpp, server-models.cpp,
  server.cpp); nothing to diff, fresh fetch is authoritative.
- SOURCES.md: grep `fit\.cpp|common/fit` and `fit` -> no matches; no existing row
  covers this file/scope, so a new row is needed (drafted, not written to SOURCES.md).

### Unset-context fitting (lines 195-198, 261-278)
- `fit.cpp:195-197`: `n_streams = cparams->kv_unified ? 1 : std::max<uint32_t>(1, cparams->n_seq_max);`
  and `n_ctx_auto = cparams->n_ctx == 0;` (line 198).
- `fit.cpp:192`: `hp_nct = 0; // hparams.n_ctx_train` (set by the memory probe).
- `fit.cpp:267-268`: `n_ctx_max = min(hp_nct * n_streams, UINT32_MAX);`
  `n_ctx_min_total = min(n_ctx_min * n_streams, UINT32_MAX);`.
- `fit.cpp:270-276`: line 270 comment "llama_context would use only hp_nct in total
  for n_ctx == 0, resolve the context before measuring anything else:"; line 272
  `cparams->n_ctx = n_ctx_max;`; when `n_streams > 1` it re-measures (line 276).
  => For X1 (`-np 4 --no-kv-unified`, model n_ctx_train 2048): total 8192,
  matching the amendment-2 source-derived prediction, not round-20's per-slot 512.

### Minimum context (lines 182, 268, 886)
- `n_ctx_min` is a caller-supplied parameter (`common_params_fit_impl` line 182,
  `common_fit_params` line 886). The llama-server default is common.h:485
  `fit_params_min_ctx = 4096;` (fetched fresh, sha256 8bcc5708...4a9).
- `-c 0` sets it to `UINT32_MAX` in arg.cpp:1646-1649 (disables reduction), so
  reduction is skipped when n_ctx_auto with -c 0 (fit.cpp:447-448 "no change").

### When fit reduces context (lines 393-455)
- Reduction occurs only when `n_ctx_auto` && `n_ctx_max > n_ctx_min_total`
  (lines 393-394): linear interpolation between n_ctx_min_total and n_ctx_max
  (426-427), then `align = 256 * n_streams`, round-down, floored at
  `n_ctx_min_total` (429-430); log "context size reduced from ... to ..." (434).
- Otherwise no change: n_ctx_min == UINT32_MAX (447-448) or max <= min_total
  (450-451), or user-set context (455: "context size set by user to ... -> no
  change").

## Does-not-establish list
1. Not runtime behavior of the running b11755 server (call gating in server.cpp
   line 180-181 and arg.cpp; observed /props, /slots, /v1/models are runtime).
2. Not the default minimum context 4096 (that is common.h:485, separate file).
3. Not that `-c 0` disables reduction (arg.cpp:1646-1649, separate file).
4. Not the actual per-slot split of a shared pool at runtime (total n_ctx and
   n_streams multiplier only; slot serving lives in server-context.cpp).
5. Not when reduction triggers on a real host (depends on device-memory probing
   and margins; needs a live run) nor other commits/builds, router mode, or
   unified-KV serving beyond n_streams = 1.

## Files written
- `.ufo/waves/round-25/a2-build/out/SrcFitCpp/draft-sources-row.md` (draft row,
  Gate record, sha256, does-not-establish).
- Scratch: /fast/scratch/hyaku/kama-r25a2/SrcFitCpp/fit.cpp (raw fetch) and
  common.h (raw fetch).
- No llama-server child started; no edits to SOURCES.md or any production file.
