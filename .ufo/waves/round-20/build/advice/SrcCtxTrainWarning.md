VERDICT: confirm - 704366d76 libllama warns without clamping at n_ctx_train; the server caps each slot at effective n_ctx_train. An oversized request is not a verdict or contradiction; compare served context with its effective cap.

Seat: CloseKama18.SrcCtxTrainWarning-2 (scout). Pin: llama.cpp 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad = b11755. Commands and exits: `.ufo/waves/round-20/build/out/SrcCtxTrainWarning-2/commands.txt`. Pinned copies, run logs and SHA256SUMS are in the same directory.

## Observed (source at the pin; runtime from the pinned b11755 binary on stories260K)
- `src/llama-context.cpp` (sha256 2a25e556…94aa5): line 219 maps `n_ctx` 0 to `n_ctx_train`. Line 377 pads `n_ctx` up to a multiple of 256 without a log line. Lines 379-393 split it per sequence. Lines 409-412 log at INFO when `n_ctx_seq < n_ctx_train`. Lines 414-417 log a WARN when `n_ctx_seq > n_ctx_train` (string at 415). After that WARN, no code assigns n_ctx_train to `n_ctx` or `n_ctx_seq`: a grep for assignments found only 219, 377, 380, 382-383 and 390.
- Same file, 4114-4117: a custom YaRN load (`rope_scaling_type == YARN && rope_freq_scale != rope_freq_scale_train`) rewrites `model->hparams.n_ctx_train = n_ctx_orig_yarn / rope_freq_scale`.
- `tools/server/server-context.cpp` (sha256 dd1de0f2…c2329; `cmp` with lane `.ufo/waves/round-16/sources/llama.cpp-704366d/server-context.cpp` exits 0):
  - `n_ctx_slot()` at 4654-4663 returns `std::min(res, llama_model_n_ctx_train(model_tgt))` (4662).
  - `slot.n_ctx = n_ctx_slot()` (1437), and `slot_n_ctx` comes from `n_ctx_slot()` (4829). That value feeds `/props` `default_generation_settings.n_ctx` (5236) and `/v1/models` `meta.n_ctx` (5186); `meta.n_ctx_train` (5187) comes from 4848.
  - The cap is only reported at 1351-1378, with the WARN at 1375.
- GGUF key: `src/llama-model.cpp:1382` `ml.get_key(LLM_KV_CONTEXT_LENGTH, hparams.n_ctx_train);` and `src/llama-arch.cpp:203` `{ LLM_KV_CONTEXT_LENGTH, "%s.context_length" }`.
- Runtime (llama-completion, exit 0 each run):
  - `-c 4096` logs `W llama_context: n_ctx_seq (4096) > n_ctx_train (2048) -- possible training context overflow` and still reports `n_ctx = 4096`, so libllama does not clamp.
  - `-c 256 -v` logs `I llama_context: n_ctx_seq (256) < n_ctx_train (2048) -- the full capacity of the model will not be utilized`.
  - `-c 100` gives `n_ctx = 256` (the pad); `-c 0` gives `n_ctx = 2048`.
- Server core: `libllama-cli-impl.so` NEEDs `libllama-server-impl.so`, the only one of the three impl libraries that holds the capping string. `unshare -rn timeout 60 llama-cli … -c 4096 -st` logged at load `W srv load_model: the slot context (4096) exceeds the training context of the model (2048) - capping` and `n_ctx_slot = 2048`. That run exited 124: the single turn never finished, and `timeout` stopped it at 60 s.
- Declared context: gguf-py 0.19.0 (oracle) reads `llama.context_length` = 2048 from stories260K (sha256 270cba1b…256d, matching), exit 0. Receipt `.ufo/waves/round-18/live-recovery/receipt-1.json` has argv `-c 256` (lines 13-14), served `default_generation_settings.n_ctx` 256 (line 64) and `/v1/models` `n_ctx` 256 / `n_ctx_train` 2048 (line 43).

## SOURCES row candidates (L1 assigns ids after S057; cells in registry order)
Primary, answering the question:
| S0xx | llama.cpp `llama_context` context sizing @ 704366d76 (release b11755) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp | code | A | what libllama does when the requested per-sequence context differs from the model's training context at commit 704366d76; not the server slot cap, not output quality | `n_ctx` 0→`n_ctx_train` 219; silent pad 377, per-sequence split 379-393; INFO under-use 409-412; WARN overflow 414-417 (string 415), no clamp; custom-YaRN `n_ctx_train` rewrite 4114-4117; raw sha256 2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5 | "n_ctx_seq (%u) > n_ctx_train (%u) -- possible training context overflow" (line 415, 10 words). Asking for more than the training context only produces a log line, never an error or clamp. | mined | 2026-10-21 | on-release | (L1) |

Companion, the clamp that decides the served value:
| S0xx | llama.cpp server slot-context cap @ 704366d76 (release b11755) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp | code | A | per-slot `n_ctx` served by single-model llama-server at 704366d76 (`/props` `default_generation_settings.n_ctx`, `/v1/models` `meta.n_ctx`); not router mode | `n_ctx_slot()` 4654-4663 (min with `llama_model_n_ctx_train` at 4662); report 1351-1378, WARN 1375; `slot.n_ctx` 1437; `slot_n_ctx` 4829 → props 5236, models meta 5186-5187; raw sha256 dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329 (same file as S042, new scope) | "the slot context (%d) exceeds the training context of the model (%d) - capping" (line 1375, 14 words). The served slot context never exceeds `n_ctx_train`. | mined | 2026-10-21 | on-release | (L1) |

## Reconciliation rule this grounds (D = header `<arch>.context_length`, S = served `/props` n_ctx, T = `/v1/models` `meta.n_ctx_train`)
- **S < D: consistent.** It is the observed case: D 2048, S 256, T 2048; the library's INFO says that the full model capacity will not be used (409-412).
- **S == D: consistent and full declared capacity only when T == D.** The effective per-slot size must reach D; `-c 0` or a total request ≥ D alone does not guarantee this when contexts are split across slots.
- **Requested context above D: warning, not contradiction.** The library warns; the single-model server caps each slot to at most effective `n_ctx_train`. Argv `-c` is not S, because padding can raise it (`-c 100` gives 256).
- **S > T:** contradicts the traced single-model server cap. If T differs from header D, first investigate a known context adjustment: custom YaRN rewrites `n_ctx_train` (4114-4117). Do not call that a contradiction against D without accounting for the override. [INFERENCE] The exact CLI flags that set custom YaRN were not traced.

## Unknowns
- The cap was seen through llama-cli's load log (linked server core), not through a llama-server `/props` call, because no server could be launched this wave. That `/props` would read 2048 is [INFERENCE] from 4829/5236 plus the observed `n_ctx_slot = 2048`.
- Router mode was not traced. `server-models.cpp:2378-2379` reports `context_length` from the offline `n_ctx_train`.
- `-fit` (on by default; `common.h:483-485`, `arg.cpp:1646-1648`) may lower an unset context to no less than 4096. That would be a legitimate S < D; its implementation file was not opened [INFERENCE].
- `llama-context.cpp:391` prints "rounding down" after a GGML_PAD that rounds up (383). This is a wording quirk, not a claim.

Tooling: no persistent installs. `uv run --no-project --with gguf` pulled the PyPI wheel gguf 0.19.0 into an ephemeral env to serve as the oracle. No llama-server was launched, `kama-llamacpp-live.py` was not run, and `pgrep` found no llama process after each run batch. The lane is unmodified; scratch `/tmp/kama-r20-SrcCtxTrainWarning` was deleted.
