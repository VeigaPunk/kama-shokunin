# Draft SOURCES row — llama.cpp src/llama-context.cpp @ 704366d76

Seat: KamaR25a2.SrcLlamaContextPad (build wave, attempt 2). Neither this row nor
anything in this folder is written into `corpus/SOURCES.md`; the L1 is the only
writer of lane production files. Status cell stays `queued` until the L1 cites
it.

## Fetched source record

- Command: `curl -sSL -o <scratch>/llama-context.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp`
- curl exit code: 0
- Lines: 4719 (`wc -l`)
- sha256: `2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5` (`sha256sum`)
- Access date: 2026-10-22
- Scratch copy: `/fast/scratch/hyaku/kama-r25a2/SrcLlamaContextPad/llama-context.cpp`
- Round-16 pinned snapshot `.ufo/waves/round-16/sources/llama.cpp-704366d/` holds
  only server-side files (README.md, arg.cpp, server-*.cpp/h, server.cpp); it does
  not contain `src/llama-context.cpp`, so no byte diff against the pin was possible.

## Existing SOURCES rows

`grep` for `llama-context` over `corpus/SOURCES.md` (path and scope): no matches.
Closest related rows: S035 (server README), S036 (server-http.cpp), S037/S043/S047
(server.cpp / server-queue.cpp), S054/S056 (common/arg.cpp), S059 (gguf-py reader),
S060 (tools/server/server-context.cpp — per-slot served context vs training-context
metadata surfaces). None covers this file or this scope. A new row is needed.

## Draft registry row (exact 11-column format)

| S1xx | llama.cpp src/llama-context.cpp @ 704366d76 (release b11755) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp | code | A | how llama-server at commit 704366d76 derives padded per-slot context (n_ctx, n_ctx_seq) and re-adjusts YaRN n_ctx_train internally; not HTTP surfaces, not common/fit.cpp behavior | llama_context ctor lines 377-393 (GGML_PAD to 256 at 377; per-sequence division 380-383; non-divisible reassign and warning 389-392; n_ctx_seq vs n_ctx_train logs 409-417; unset n_ctx default line 219) and llama_init_from_model lines 4114-4118 (YaRN re-adjust); raw sha256 2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5 | An unset n_ctx resolves to n_ctx_train (line 219), then n_ctx is padded up to a multiple of 256; with a split KV cache the per-slot n_ctx_seq is n_ctx / n_seq_max padded up to 256, and n_ctx is reassigned to n_ctx_seq * n_seq_max with a "rounding down" log when they differ; per-slot values below or above n_ctx_train only log, never clamp; custom YaRN scaling rewrites model n_ctx_train to n_ctx_orig_yarn / rope_freq_scale. | queued | 2026-10-22 | on-release | — |

## Gate record

- URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp (raw fetched, see sha256 above)
- Access date: 2026-10-22
- Located quote (1), line 391 of the raw file: `n_ctx is not divisible by n_seq_max - rounding down to %u` (11 words; the full statement is `LLAMA_LOG_WARN("%s: n_ctx is not divisible by n_seq_max - rounding down to %u\n", __func__, cparams.n_ctx);`)
- Located quote (2), line 4116: `model->hparams.n_ctx_train = cparams.n_ctx_orig_yarn / cparams.rope_freq_scale;` (8 words; guarded by the YaRN + custom-scale check at line 4114, logged at 4115 and 4117)

## What this source does not establish

1. No observed runtime values or HTTP behavior: nothing here was executed; served
   per-cell values come from the committed receipt (server `/props`, `/slots`,
   `/v1/models`, and the log lines required by amendment 1).
2. Not what `common/fit.cpp` does to params before `llama_init_from_model` runs.
   Whether X1's unset `-c 0 -np 4 --no-kv-unified` lands as per-slot 512
   (this file alone, via line 219 then 380-383: 2048/4 padded to 512) or as
   per-slot 2048 (the amendment-2 X1 prediction attributing it to fit.cpp)
   is decided by whether the server fitted first. This file cannot adjudicate
   the X1 round-20-formula conflict.
3. Not a cap of per-slot n_ctx to n_ctx_train. Lines 409-417 only log when
   `n_ctx_seq` is below or above `n_ctx_train`; there is no clamp in this file.
   K5's predicted cap (4096 requested -> 2048 served) is therefore not grounded
   here; if such a cap exists it lives elsewhere (e.g. the server layer, cf. S060).
4. Not the `total_slots` auto rule (`-np -1`), nor the kv-unified default gating
   (enabled only when slot count is auto); those decisions are outside this file.
5. Not the shared-pool concurrency failure (L1) or any request/slot scheduling,
   token accounting, or HTTP status behavior.
6. Not a monotonic "rounding down": the log text at 391 refers to the reassignment
   `n_ctx = n_ctx_seq * n_seq_max`, but because the per-slot value is padded up
   first (line 383), the reassigned pool can exceed the originally padded n_ctx.
   Worked (unexecuted) example from the shown lines: `-c 1000 -np 3 --no-kv-unified`
   -> 1000 padded to 1024, 1024/3 = 341, padded per-slot 512, pool 1536, warning
   logged with value 1536. This arithmetic is read from the code, not run.

## Files written by this seat

- `.ufo/waves/round-25/a2-build/out/SrcLlamaContextPad/row.md` (this file)
- `.ufo/waves/round-25/a2-build/advice/SrcLlamaContextPad.md` (advice report)
