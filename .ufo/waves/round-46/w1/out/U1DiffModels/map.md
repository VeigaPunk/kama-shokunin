# U1DiffModels change map: b11889 (d854d98bae59) -> b11906 (4d71b42fd871), llama.cpp

Verdict: 17 commits, 65 files (4323+/2128-). Only 2 of the 16 population paths changed (server-context.cpp, server-models.cpp), both only by commit c6fb3b5be. No population row's pinned range or statement depends on any changed line. The other 14 population blobs are byte-identical.

Source: `git -C /fast/scratch/hyaku/kama-r46/L1/llama.git diff --stat d854d98.. 4d71b42..`, per-file `diff -U0`, `show <commit>:<path>`.

## 1. The 16 population paths (registry/release-recheck-b11889.tsv; 91 rows, column `path`)

| path | rows | blob b11889 == b11906 | changed by |
|---|---|---|---|
| common/arg.cpp | 3 | yes (9706b3ac) | - |
| common/common.cpp | 1 | yes (a4b4feae) | - |
| common/fit.cpp | 2 | yes (7a030082) | - |
| ggml/src/gguf.cpp | 2 | yes (75ceade7) | - |
| gguf-py/gguf/gguf_reader.py | 1 | yes (bf3e0838) | - |
| src/llama-context.cpp | 3 | yes (d5a66a49) | - |
| src/llama-kv-cache.cpp | 2 | yes (4ab280a6) | - |
| tools/quantize/README.md | 1 | yes (27384beb) | - |
| tools/server/README.md | 4 | yes (8e27e37b) | - |
| tools/server/server-common.cpp | 13 | yes (80a9f2d7) | - |
| tools/server/server.cpp | 3 | yes (b6ebf752) | - |
| tools/server/server-http.cpp | 1 | yes (cf147c7e) | - |
| tools/server/server-queue.cpp | 1 | yes (c4ce9072) | - |
| tools/server/server-schema.cpp | 36 | yes (0a14a962) | - |
| **tools/server/server-context.cpp** | 17 | **no** a5cba1d7 -> 9043fa2c | c6fb3b5be |
| **tools/server/server-models.cpp** | 1 (S479) | **no** e1e006f1 -> 57514014 | c6fb3b5be |

71 rows = rows on the 14 unchanged paths (the byte-identical set). 20 rows to read + S479: S037 S043 S108 (server.cpp, unchanged blob, only b11889 holds-reworded status), S042 S060 S109 S114-S125 S133 S138 (server-context.cpp), S479 (server-models.cpp).

## 2. tools/server/ and common/ files that changed

`git diff --stat d854d98 4d71b42 -- common tools/server` = 3 files: server-context.cpp (15 lines), server-models.cpp (2), tests/utils.py (2). common/ has ZERO changes (so arg.cpp, common.cpp, fit.cpp rows S054 S056 S110 S111 S106 S131 hold trivially).

### server-context.cpp - commit c6fb3b5be "mtmd: add mtmd_helper_get_capabilities (#31183)"
-U0 hunks, b11889 coordinates -> b11906: 1014+0 -> 1015 (add member `mtmd_helper_cap mtmd_cap = {};`), 1020 and 1024 (has_cap_tts / has_cap_chat bodies now `return mtmd_cap.audio_gen;` / `return mtmd_cap.chat;`), 1399 (+2 lines `mtmd_cap = mtmd_helper_get_capabilities(model_tgt, mctx);`), 1708-1710 (allow_image/audio/video from mtmd_cap.vision/audio/video), 5130 (has_audio_stream from mtmd_cap.audio_stream). Net +3 lines, all hunks end by line 5130.
- Every population range of every server-context row lies at b11889 line >= 1887 and none intersects a hunk; all ranges after line 1399 shift by exactly +3 lines at b11906. Checked: 26 range pairs (S042 S060 S109 S114-S125 S133 S138), b11889 range text vs b11906 text at +3 shift = equal for all (S121 equal after strip: indentation only differs in the pin line, which the counter's text-equal ignores).
- Pin range vs b11906 range, line by line (pin lines paired with the b11889 release_lines ranges, shifted +3): equal for all 17 server-context rows (S121 modulo indentation; the pin line is the 12-space-indented `res->error(...--reranking...)` and sits at 8 spaces at b11906:6855).
- Row dependence: none. Rows S114-S125 quote error strings (refusals, pooling, rerank, infill) and S042/S060/S109/S133/S138 sizing, shutdown and slot predicates; none quotes has_cap_*, allow_image/audio/video or mctx. Behaviour of has_cap_chat/tts is unchanged: old rule `mctx == nullptr || mtmd_helper_model_can_chat(...)`, new `cap.chat = !cap.audio_gen || chat template != nullptr` (true when mctx NULL), same rule.

### server-models.cpp - commit c6fb3b5be, row S479
One line changed, b11889:536 / b11906:536 (comment `// same rule as mtmd_helper_model_can_chat()` -> `// same rule as mtmd_helper_get_capabilities()` in server_model_meta::update_caps). No line count change, so S479's b11889 ranges 2276 (get_router_models) and 2325-2326 (guarded `model_info["context_length"] = meta.n_ctx_train;`) are at the same line numbers at b11906. Pin 2329,2378-2379 vs b11906 2276,2325-2326: text equal. `max_model_len` absence is unaffected (change is comment-only). Row dependence: none; verdict holds.

### tools/server/tests/utils.py - commit 224d94c02 (#31174)
DEFAULT_HTTP_TIMEOUT 60 -> 600 (line 32). No population row cites tests/utils.py.

## 3. Everything else, by commit (no population row depends)
| commit | files | note |
|---|---|---|
| 4d71b42fd ggml-cpu concat | ggml-cpu/ops.cpp, tests/test-backend-ops.cpp | kernel |
| 70c5f2632 vulkan rms_norm | ggml-vulkan/*, rms_norm.comp, test-backend-ops | kernel |
| 5cd62ffee / 38645c2ad / 02269b4c0 / 5320c87ff sycl | ggml-sycl/mmvq.cpp, concat.cpp, ggml-sycl.cpp | backend |
| 74b104c9b common: pin model resolution | tests/test-model-resolution.cpp (new, 2250 lines) | test only, no common/ source touched |
| 8b28c2394 | ggml-cpu/arch/arm/quants.c | |
| fd8f8451a test-llama-archs | src/llama-arch.cpp, llama-ext.h, llama-model-saver.{cpp,h}, tests/ | src/ but not llama-context.cpp / llama-kv-cache.cpp |
| 9125a2ebe | ggml-webgpu | |
| 9b8446b91 | ggml-metal mul_mm.metal, test-backend-ops | |
| dc9e3bed4, 69b3cc406 ui | tools/ui/** (WebUI Svelte, 29 files) | not tools/server/*.cpp |
| 48c36110a | .github/workflows/build-apple.yml | CI |
| a07421535 deepseekv4.1 | conversion/deepseek*.py, src/llama-hparams.h, llama-kv-cache-dsv4.*, llama-model-saver.cpp, llama-model.h, src/models/*, test-backend-ops | not llama-kv-cache.cpp |
| c6fb3b5be | tools/mtmd/{mtmd-cli.cpp,mtmd-helper.cpp,mtmd-helper.h} + the two server files above | adds mtmd_helper_cap/mtmd_helper_get_capabilities; mtmd_helper_model_can_chat and mtmd_helper_support_video kept as DEPRECATED wrappers |

## 4. Ledger consequence
- All 91 rows: holds expected at b11906. 71 rows by blob identity; 20 by reading. The 20 are byte-equal after shifting +3 (server-context) or +0 (server-models), or blob identity (server.cpp S037 S043 S108).
- The ranges recorded in release-recheck-b11889.tsv are NOT valid for b11906 on server-context.cpp: write release_lines with +3 for every server-context row (e.g. S042 5171-5174,5606-5617 -> 5174-5177,5609-5620; S116 3233 -> 3236; new = b11889 + 3). server-models.cpp and server.cpp: same lines as b11889.
- S037 S043 S108: pin text vs release text differs (holds-reworded at b11889 for reasons unrelated to this diff); server.cpp blob unchanged, so their b11906 verdicts/witnesses can be copied from b11889 unchanged (witness_pin/witness_new still absent/present).
