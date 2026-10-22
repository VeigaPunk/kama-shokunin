# ReopenS111: S111 row and its use in the entry

Verdict: defect found. The S111 row holds on every check. The entry's use of S111 (corpus/knowledge/context-capacity.md:71-72) attaches two conditions that S111 does not carry, leaves `-c 0` out of the raise trigger, and mislabels one log line. One registry gap sits behind the llama-server link.

Scope: SOURCES row S111 (corpus/SOURCES.md:123), its Gate line (corpus/lessons/round-25.md:27), and every use of S111 in the entry. Pinned commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, fetched 2026-10-22. No llama-server started; I read existing logs only. Full evidence: .ufo/waves/round-25/a2-falsify/out/ReopenS111/evidence.md.

## 1. S111 row: holds

| # | check | verdict | evidence |
|---|---|---|---|
| 1 | raw sha256 in anchor | holds | anchor `d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4`; fresh raw common.cpp (curl exit 0, 2460 lines) hashes to the same value; shell compare printed SHA_MATCH |
| 2 | fit guard, line 1245 | holds | common.cpp:1245 `if (params.fit_params) {` |
| 3 | call range 1270-1276 | holds | 1270 `common_fit_params(params.model.path.c_str(), &mparams, &cparams,`; 1276 ends `... GGML_LOG_LEVEL_ERROR);` |
| 4 | model load, line 1279 | holds | 1279 `llama_model_load_from_file(...)`, after the fit block closes at 1277 |
| 5 | range 1240-1280 | holds | 1240 is the `common_init_result` constructor header; 1280 starts the NULL-model check |
| 6 | range 1418-1425 | holds | 1418 `common_init_from_params(...) {`; 1419 builds the result; 1425 closes the NULL-model block |
| 7 | teaches: wrapper constructs the result | holds | common.cpp:1419 |
| 8 | teaches: fit_params true, pointers passed, call before load | holds | 1245 guard; 1270-1273 pass `&mparams, &cparams`; 1279 loads after |
| 9 | teaches: draft or MTP enables the extra-model argument | holds | 1250-1252 set `has_draft`, `spec_mtp`; 1263-1268 build `extra`; 1275 `has_draft || spec_mtp ? &extra : nullptr,` |
| 10 | teaches: verbosity selects the fit log level | holds | 1276 `params.verbosity >= LOG_LEVEL_DEBUG ? GGML_LOG_LEVEL_DEBUG : GGML_LOG_LEVEL_ERROR` |
| 11 | teaches says nothing beyond its lines | holds | every clause maps to a line above |
| 12 | Gate quotes (round-25.md:27) | holds | `if (params.fit_params) {` is line 1245; `common_fit_params(params.model.path.c_str(), &mparams, &cparams,` is line 1270; both exact after trimming indentation; 3 words each, under 25 |
| 13 | scope "not fit defaults" | holds | the only guard is line 1245 (`params.fit_params`); S111's lines contain no n_ctx test |
| 14 | status, opened, used-by | holds | `mined`, 2026-10-22, corpus/knowledge/context-capacity.md; the Gate line says the same |

## 2. Use of S111 in the entry: defects

Only two places in the entry cite S111: the front-matter list (context-capacity.md:1) and the sentence at lines 71-72. Other mentions are range citations (SKILL.md:678, corpus/README.md:395, round-25 report-draft.md:18 and :38).

### F1. "-c unset" and "(the default)" sit under an S111 citation (medium)

Entry line 71: "When `-c` is unset and `--fit` is on (the default), the fit step runs before the model loads (S111, common.cpp 1245-1276)".

- Holds: the ordering. The fit guard and call (1245-1276) come before the load at 1279. X1.server.log:16 starts the fit, :1077 says "successfully fit", and :1079 is the final model load.
- Contradicted: `-c unset` as a condition on the fit step. S111's only guard is `params.fit_params` (common.cpp:1245). The fit step runs with `-c` set. K2 is `-c 2048 -np 2 --no-kv-unified` (final/context-capacity-receipt.json, cell K2), and K2.server.log:16 reads `cmn common_init_: fitting params to device memory ...`, with :549 "successfully fit params".
- Not S111's to carry: "(the default)". The default is on: common/common.h:483 `bool fit_params = true;`. Fit runs with no flag in K1, K2 and X1 (K1.server.log:17; K2.server.log:16; X1.server.log:16), and X3 with `--fit off` has no fit lines. The claim is true. But S111's scope excludes fit defaults, and no registry row cites common.h (grep `common\.h` in corpus/SOURCES.md: no matches). So the sentence has no row for its default.
- Smallest correction: split the sentence. "When `--fit` is on (the default: `fit_params = true`, common/common.h:483), the fit step runs before the model loads (S111, common.cpp 1245-1276)." Then give common.h:483 a row, or cite the three observed default-on runs as the entry's own evidence.

### F2. The raise trigger is n_ctx == 0, so explicit `-c 0` raises too (medium-low)

Entry line 69 heading "Fit raises an unset split context"; line 71 "When `-c` is unset"; SKILL.md:687 row "`-c` unset, `-np` given, split cache".

- Source trigger: common/fit.cpp:198 `const bool n_ctx_auto = cparams->n_ctx == 0;`; fit.cpp:271-272 `if (n_ctx_auto) { cparams->n_ctx = n_ctx_max;`.
- Explicit `-c 0` gives n_ctx 0. arg.cpp:1645 `params.n_ctx = value;` (value 0); common.cpp:1714 `cparams.n_ctx = params.n_ctx;`; common.h:457 default `n_ctx = 0`. No code between them rewrites the zero (checked in arg.cpp, common.cpp, server.cpp, server-context.cpp).
- So `-c 0` takes the same raise. It differs from unset only in `fit_params_min_ctx = UINT32_MAX` (arg.cpp:1646-1648), which removes reduction (fit.cpp:394, 447-448). The bullet at entry lines 95-97 gets reduction right, but never says whether `-c 0` raises. A reader will infer that it does not.
- Not observed: a split cache with `-c 0`. The `-c 0` cells (K1, L1, L3) all run unified. Entry line 174 lists this case as not run, which is correct.
- Smallest correction: "When `-c` is unset or `-c 0` (both give n_ctx 0; fit.cpp:198, 271-272)" at line 71; "unset or zero" in the heading at line 69; the same condition in SKILL.md:687. Leave line 174 as written.

### F3. Log line 812 is labelled as the serving context (low)

Entry lines 76-79: "then the serving context (`n_ctx = 8192`, lines 812 and 1344)".

- X1.server.log:547 `context size unset and KV cache not unified -> using 8192 for 4 sequences`; :810-812 construct a context with `n_ctx = 8192`; :1077 `successfully fit params`.
- So line 812 falls inside the fit step, between the :547 message and the :1077 success line. [INFERENCE] It is the fit's own re-measure at fit.cpp:272-276.
- The serving context is X1.server.log:1341-1344 (`added </s> logit bias`, then construct with `n_ctx = 8192`), before `srv load_model: initializing` at :1610. Line 283 (probe, `n_ctx = 2048`) and line 1610 are correct as written.
- Smallest correction: "then the serving context (`n_ctx = 8192`, line 1344); line 812 is the fit's own 8192 re-measure, inside the fit step (lines 547-1077)."

### F4. The llama-server link to S111 is not in the registry (low)

- tools/server/server-context.cpp:1116 `bool load_model(common_params & params) {`; :1217 `llama_init = common_init_from_params(params_base);`. This is the only call into S111's wrapper in server.cpp or server-context.cpp.
- No registry row cites server-context.cpp:1116 or :1217 (grep `1217` in corpus/SOURCES.md: no matches). S109 says "not the load/fit path"; S108 covers server.cpp 159-186 only.
- Runtime shows the chain: K2.server.log:14 `srv load_model: loading model`, then :16 the fit; X1.server.log:14 and :16 the same.
- Smallest correction: one correction row (or a note in the entry) naming server-context.cpp:1116 and :1217 as the call site, citing K2.server.log:14-16 and X1.server.log:14-16 for the observed path. The S111 row needs no change, because its scope excludes server execution.

## 3. Checked and fine

- The S111 Gate line (round-25.md:27) uses the same URL as the row and the same line numbers (1245, 1270). The row has no quote column, so the quote text itself was checked against common.cpp only (section 1, row 12).
- The -c 0 bullet (entry lines 95-97) is right about reduction (arg.cpp:1646-1649; fit.cpp:447-448).
- Runtime: the S111 guard depends only on `fit_params`. K1 (`-c 0`) and K2 (`-c 2048`) run the fit; X3 (`--fit off`) does not.
- common.h:580 (cited under S110 at context-capacity.md:60) is `bool kv_unified = false;`, which supports "default split cache". The content is right, but common.h is not in any registry anchor (same gap as F1).

## 4. Smallest corrections, in one list

1. context-capacity.md:71: take "and `-c` is unset" out of the S111-cited clause; cite the default (common.h:483) separately, with a row or the observed runs.
2. context-capacity.md:69 and :71, SKILL.md:687: "unset or `-c 0`" (both give n_ctx 0).
3. context-capacity.md:78: line 812 is the fit's re-measure; the serving context is line 1344.
4. Registry: a row or note for server-context.cpp:1116 and :1217 (llama-server to S111), and for common/common.h:483 (fit default).
No change to the S111 row or to its Gate line.

## 5. Residual risk and verification gaps

- No llama-server was run (assignment forbade it). F2's raise for `-c 0` on a split cache rests on source (fit.cpp:198, 271-272), not an observed cell.
- F3's attribution of line 812 is an inference from log order and fit.cpp:272-276.
- I checked the cited line ranges and the code path, not all of common.cpp or fit.cpp. The S106 row's own teaches were not audited; I read only the fit.cpp lines the entry relies on here (198, 267, 271-276, 393-394, 447-455).
- Sources: every file came from raw.githubusercontent.com at the pinned commit (access date 2026-10-22). The S111 row's blob URL names the same commit path. I quote no prose beyond the Gate quotes (3 words each).

## 6. Files written and tools

- .ufo/waves/round-25/a2-falsify/advice/ReopenS111.md (this report)
- .ufo/waves/round-25/a2-falsify/out/ReopenS111/evidence.md (evidence record, with every line number and command result)
- Directories created: .ufo/waves/round-25/a2-falsify/out/ReopenS111/ and .ufo/waves/round-25/a2-falsify/advice/
- Scratch copies (heavy, not committed): /fast/scratch/hyaku/kama-r25a2w2/ReopenS111/{common.cpp, common.h, arg.cpp, fit.cpp, server.cpp, server-context.cpp}

Installed or upgraded: none. Commands used: curl (exit 0 on all six fetches), sha256sum, wc, date. No pacman, no git, no jj.

Report: .ufo/waves/round-25/a2-falsify/advice/ReopenS111.md
