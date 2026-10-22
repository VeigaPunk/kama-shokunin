# SrcLlamaContextPad — advice (round 25, attempt 2, build wave)

Verdict: fresh `src/llama-context.cpp` at 704366d76 fetched and read (sha256
2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5, 4719 lines,
curl exit 0); no existing SOURCES row covers it, so a new row is drafted
(status queued for the L1); the file establishes padding/split/YaRN mechanics
and does not establish the fit.cpp interaction, any served values, a training
context cap, or concurrency behavior.

## Observation 1 — fetch and integrity

Command: `curl -sSL -o /fast/scratch/hyaku/kama-r25a2/SrcLlamaContextPad/llama-context.cpp
https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp`
- exit 0; `wc -l` = 4719; `sha256sum` = `2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5`.
- The round-16 pinned snapshot `.ufo/waves/round-16/sources/llama.cpp-704366d/`
  lists only server-side files (README.md, arg.cpp, server-common.cpp/h,
  server-context.cpp, server-http.cpp, server-models.cpp, server.cpp); it does
  not contain this file, so no pin diff was possible.

## Observation 2 — existing SOURCES rows

`grep` `llama-context` on `corpus/SOURCES.md`: 0 matches. S060 covers
`tools/server/server-context.cpp` (per-slot served metadata surfaces) — a
different file and scope. A new row is needed; drafted in
`.ufo/waves/round-25/a2-build/out/SrcLlamaContextPad/row.md`
(11-column table, id `S1xx`, status `queued`).

## Observation 3 — located source readings

Enclosing functions: `llama_context::llama_context(const llama_model &,
llama_context_params)` (signature lines 168-170) and
`llama_init_from_model(llama_model *, llama_context_params)` (lines 4021-4023).

- Line 219 (ctor): `cparams.n_ctx = params.n_ctx == 0 ? hparams.n_ctx_train : params.n_ctx;` — an unset `-c 0` resolves to training context before any splitting.
- Lines 376-393 (ctor): comment refs PR #17046; `cparams.n_ctx = GGML_PAD(cparams.n_ctx, 256);` (377); if `kv_unified`, `n_ctx_seq = n_ctx` (380); else `n_ctx_seq = n_ctx / n_seq_max` then `GGML_PAD(n_ctx_seq, 256)` (382-383); `n_ctx_seq == 0` throws (385-387); if `n_ctx != n_ctx_seq * n_seq_max` then `n_ctx = n_ctx_seq * n_seq_max` and warn `n_ctx is not divisible by n_seq_max - rounding down to %u` (389-392).
- Lines 409-417 (ctor): `n_ctx_seq < n_ctx_train` logs capacity-unused info; `n_ctx_seq > n_ctx_train` logs `possible training context overflow` warning; no clamp.
- Lines 4114-4118 (`llama_init_from_model`): if YaRN and `rope_freq_scale != rope_freq_scale_train`, re-adjust `model->hparams.n_ctx_train = cparams.n_ctx_orig_yarn / cparams.rope_freq_scale` with two info logs.
- Line 4034-4037: both `n_ctx == 0` and `n_ctx_train == 0` together are rejected (error, nullptr).

## Observation 4 — C2 relevance (as source reasoning, not evidence)

- K1/K3 (unified): line 380 gives `n_ctx_seq = n_ctx`; consistent with the pilot's per-slot 2048 rows.
- K2 (2048/2 split): 2048/2 = 1024 padded to 1024; product equals input, no warn; per-slot 1024. Consistent.
- K4 (1024/1): per-slot 1024.
- K6 (1000/3 split): 1000 -> 1024 (pad), 1024/3 = 341 -> 512 (per-slot), pool 512*3 = 1536, warning logged with 1536. Matches the critic's outside prediction (per-slot 512, pool 1536). Derived from the shown lines, not run.
- X1/X3: line 219 alone would give per-slot 512 for unset `-c 0 -np 4` (2048/4 -> 512) — i.e. the round-20 value — but only if `common/fit.cpp` has not rewritten params first. This file cannot decide the conflict; the fit decision is outside it.
- K5: the predicted cap of per-slot n_ctx at training context is NOT in this file (lines 409-417 log only). If real, it lives elsewhere (server layer; cf. S060).

## What the source does not establish

Listed in `.ufo/waves/round-25/a2-build/out/SrcLlamaContextPad/row.md` §"What this source does not establish": observed values/HTTP behavior; fit.cpp interaction (X1 conflict); a training-context cap (K5); auto-slots and kv-unified default gating; L1 concurrency/slot scheduling; monotonic direction of the "rounding down" warn.

## Files written

- `.ufo/waves/round-25/a2-build/out/SrcLlamaContextPad/row.md`
- `.ufo/waves/round-25/a2-build/advice/SrcLlamaContextPad.md` (this report)

No llama-server child was started; no repo files were edited; no installs made.
