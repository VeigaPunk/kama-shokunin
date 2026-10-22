# ReopenS111 evidence record

Seat: KamaR25a2.ReopenS111 (reviewer; round 25 attempt 2, wave 2 falsify).
Pinned commit: 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad.
Access date: 2026-10-22. Hash check time: `date -u` printed 2026-10-22T10:08:01Z.
Fetch form: `curl -sSfL -o <name> https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/<path>`.
Heavy copies (scratch, not committed): /fast/scratch/hyaku/kama-r25a2w2/ReopenS111/ (common.cpp, common.h, arg.cpp, fit.cpp, server.cpp, server-context.cpp).
No llama-server started. No tool installed or upgraded (curl, sha256sum, wc were already present).

## 1. Fetches and hashes (all curl exit 0)

| path at pinned commit | lines | sha256 | registry anchor | result |
|---|---|---|---|---|
| common/common.cpp | 2460 | d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4 | S111 anchor cell: raw sha256 d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4 | match; shell `[ "$got" = "$want" ] && echo SHA_MATCH` printed SHA_MATCH |
| common/arg.cpp | 4833 | bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d | S110 anchor cell: raw sha256 bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d | match |
| common/fit.cpp | 1113 | 1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58 | S106 anchor cell: raw file sha256 1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58 | match |
| tools/server/server.cpp | 591 | 2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4 | S108 anchor cell: raw SHA-256 2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4 | match |
| tools/server/server-context.cpp | 6320 | dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329 | S109 anchor cell: raw file sha256 dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329 | match |
| common/common.h | 1330 | 8bcc5708c856653b0094ba312030df9c2f43ec2703e8ad78474fd4339d2540a9 | none (no registry row anchors common.h; grep below) | not anchored |

## 2. S111 row checks (common.cpp, 1-based line numbers from the fetched file)

- 1240: `common_init_result::common_init_result(common_params & params, bool model_only) :` (constructor header)
- 1245: `    if (params.fit_params) {`
- 1250-1252: `has_draft` (params.speculative.has_dft()), `spec_mtp` (DRAFT_MTP type present)
- 1263-1268: `const common_fit_extra_model extra = { ... .shares_model = !has_draft ... };`
- 1270: `        common_fit_params(params.model.path.c_str(), &mparams, &cparams,`
- 1273-1274: `params.fit_params_target.data(),` / `params.fit_params_min_ctx,`
- 1275: `            has_draft || spec_mtp ? &extra : nullptr,`
- 1276: `            params.verbosity >= LOG_LEVEL_DEBUG ? GGML_LOG_LEVEL_DEBUG : GGML_LOG_LEVEL_ERROR);` (call ends)
- 1277: `    }` (closes the fit guard)
- 1279: `    llama_model * model = llama_model_load_from_file(params.model.path.c_str(), mparams);`
- 1418: `common_init_result_ptr common_init_from_params(common_params & params, bool model_only) {`
- 1419: `    common_init_result_ptr res(new common_init_result(params, model_only));`
- 1421-1425: model NULL check; 1425 `    }` closes it.

Gate quotes (lessons/round-25.md:27):
- `if (params.fit_params) {` is line 1245 after trimming indentation: exact. 3 words.
- `common_fit_params(params.model.path.c_str(), &mparams, &cparams,` is line 1270 after trimming indentation: exact. 3 words.

## 3. Entry and other uses of S111

- corpus/knowledge/context-capacity.md:1 front matter lists `S111 (common/common.cpp fit call)`.
- corpus/knowledge/context-capacity.md:71-72: "When `-c` is unset and `--fit` is on (the default), the fit step runs before the model loads (S111, common.cpp 1245-1276) and sets the context to the training context times the number of streams ... (S106, fit.cpp 195-198 and 266-273)."
- corpus/knowledge/context-capacity.md:69 heading "Fit raises an unset split context (supersedes the round-20 rule)".
- corpus/knowledge/context-capacity.md:76-79 X1 bullet: "...then the serving context (`n_ctx = 8192`, lines 812 and 1344) before `load_model: initializing` (line 1610)."
- corpus/knowledge/context-capacity.md:95-97: "An explicit `-c 0` is not the same as omitting `-c`: `-c 0` disables fit's context reduction (S110, arg.cpp 1646-1649)."
- corpus/knowledge/context-capacity.md:60: "(S110; common.h 580)" for default split cache; common.h:580 is `bool kv_unified = false;`.
- corpus/knowledge/context-capacity.md:173-174: "the `-c 0` split case: none was run."
- SKILL.md:678 (range S106-S113), SKILL.md:687 row trigger "`-c` unset, `-np` given, split cache".
- corpus/README.md:395 "mined S106-S113 and S060".
- .ufo/waves/round-25/report-draft.md:18 and :38 "S106-S113".
- Repo-wide grep for `S111` (gitignore off): SOURCES.md:123, lessons/round-25.md:27, context-capacity.md:1 and :72, plus wave dispatch files. No other entry or tool cites it.

## 4. Fit trigger chain (source, pinned commit)

- common/common.h:457 `int32_t n_ctx = 0; // context size, 0 == context the model was trained with`
- common/common.h:483 `bool fit_params = true;`
- common/common.h:485 `int32_t fit_params_min_ctx = 4096;`
- common/arg.cpp:1641-1651 `-c, --ctx-size` handler: 1645 `params.n_ctx = value;`; 1646-1648 `if (value == 0) { ... params.fit_params_min_ctx = UINT32_MAX; }`.
- common/arg.cpp:2881-2894 `-fit, --fit` handler; help text prints `params.fit_params ? "on" : "off"`.
- common/common.cpp:1714 `cparams.n_ctx = params.n_ctx;` (only copy; no other rewrite of n_ctx on this path).
- common/fit.cpp:198 `const bool n_ctx_auto = cparams->n_ctx == 0;`
- common/fit.cpp:267 `n_ctx_max = min(hp_nct * n_streams, UINT32_MAX)`
- common/fit.cpp:271-272 `if (n_ctx_auto) { cparams->n_ctx = n_ctx_max;`
- common/fit.cpp:273-276 n_streams > 1 log line, then device-memory re-measure with the new context.
- common/fit.cpp:393-394 `if (n_ctx_auto) { if (n_ctx_max > n_ctx_min_total) {` (reduction branch)
- common/fit.cpp:447-448 `if (n_ctx_min == UINT32_MAX) { ... "user has requested full context size ... -> no change"`
- common/fit.cpp:455 `context size set by user to %u -> no change` (n_ctx_auto false)
- A grep of arg.cpp, common.cpp, server.cpp, server-context.cpp for n_ctx assignments found no rewrite of a zero `-c` value before fit. server.cpp:179-184 rewrites n_ctx only when kv_unified_per_slot > 0, n_ctx == 0 and fit_params_min_ctx != UINT32_MAX. Preset handlers in arg.cpp (4634-4783) set n_ctx only for their own preset flags, none used by the cells.
- tools/server/server-context.cpp:1116 `bool load_model(common_params & params) {`; :1217 `llama_init = common_init_from_params(params_base);`; :1219-1220 model and context taken from llama_init.
- The grep for common_init_from_params / common_init_result / common_fit_params / llama_params_fit in server.cpp and server-context.cpp found only server-context.cpp:992 (variable) and :1217 (call).

## 5. Runtime logs (read only; cell args from final/context-capacity-receipt.json)

- K1, args `-c 0`: K1.server.log:17 `cmn  common_init_: fitting params to device memory ...`; :19 `common_params_fit_impl: getting device memory data for initial parameters:`; :548 `will leave 30972 >= 1024 MiB of system memory, no changes needed`; :549 `common_fit_params: successfully fit params to free device memory`.
- K2, args `-c 2048 -np 2 --no-kv-unified`: K2.server.log:14 `srv    load_model: loading model '...stories260K.gguf'`; :16 `cmn  common_init_: fitting params to device memory ...`; :18 getting device memory data; :283 `n_ctx = 2048` (probe, n_seq_max 2); :548 no changes needed; :549 successfully fit; :816 `n_ctx = 2048`, n_ctx_seq 1024.
- X1, args `-np 4 --no-kv-unified`: X1.server.log:14 load_model; :16 fitting; :18 getting device memory data; :281-283 constructing llama_context, `n_ctx = 2048` (probe); :547 `common_params_fit_impl: context size unset and KV cache not unified -> using 8192 for 4 sequences:`; :810-812 constructing llama_context, `n_ctx = 8192` (inside fit: after :547, before :1077); :1074-1076 `projected to use 9 MiB ...`, `will leave 30968 >= 1024 MiB ... no changes needed`; :1077 `common_fit_params: successfully fit params to free device memory`; :1079 loaded meta data (final model load); :1340 CPU_Mapped model buffer; :1341 `cmn  common_init_: added </s> logit bias = -inf`; :1342-1344 constructing llama_context, `n_ctx = 8192`, n_ctx_seq 2048 (serving context); :1609 warming up; :1610 `srv    load_model: initializing, n_slots = 4, n_ctx_slot = 2048, kv_unified = 'false'`.
- X3, args `-np 4 --no-kv-unified --fit off`: no line matches `fitting params|common_params_fit_impl|common_fit_params|successfully fit`. Its constructing llama_context lines are at 279-284 (n_ctx 2048).

[INFERENCE] X1.server.log:812 is the fit's own 8192 re-measure (fit.cpp:272-276), not the serving context: it sits between the fit message at :547 and the success line at :1077. The serving context is :1342-1344.

## 6. Registry checks

- grep `common\.h|1217` in corpus/SOURCES.md: no matches.
- grep `common\.h|server-context\.cpp|1217|fit_params` in corpus/SOURCES.md: rows that cite server-context.cpp use other lines: S042 5288-5299; S060 4654-4663, 5183-5188, 5229-5245; S109 4294-4341, 3331-3356, 1810-1835 (S109 scope: "not the load/fit path"). No row cites server-context.cpp:1116 or :1217.
- S108 anchor covers server.cpp 159-186 only.

## 7. Commands and exit codes (bash)

- `date -u +%Y-%m-%dT%H:%M:%SZ` -> 2026-10-22T10:08:01Z (exit 0)
- `sha256sum common.cpp` + compare -> SHA_MATCH d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4 (exit 0)
- curl of common/common.h, common/arg.cpp, common/fit.cpp, tools/server/server.cpp, tools/server/server-context.cpp -> each curl_exit=0; hashes in section 1.
- Tool greps and reads are listed by path and line above; the tool does not return a process exit code.
