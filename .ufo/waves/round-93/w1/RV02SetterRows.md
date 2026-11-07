# RV02SetterRows — K2 read of C2 (round 93 w1)

## Scope
Non-author read of the C2 target: `SKILL.md` section `## Listen port and slot-count setters (round 93 revision)` at
M2 `ee19acbdabc8ac572e82ae56459c364457895b06`, all rows P01–P48 plus decisions R16/R17, against the pinned
llama.cpp b12177 archive. Every cited file/line was opened; surrounding code, callers and consumers read where a
cell claims an effect. No edit to the lane; no runtime claimed.

## Commands and outputs (true exit codes)
- `curl -sSL ... codeload .../b12177` + `sha256sum` -> `f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13` (exit 0).
- `git show M2:SKILL.md`, `git show M2:corpus/SOURCES.md` (read-only) — exit 0.
- Independent population enumeration with the counter's `POP_RE` over `common/` + `tools/server/` (`*.cpp/*.h/*.hpp`):
  `population_lines=48 rows=48 missing=[] fabricated=[]` (out/population-check.out).
- Text bytes of all 48 rows vs archive lines: 0 mismatches (`text_mismatches: none`).
- `python3 tools/round93-setter-rows.py --repo . --rev M2 --archive b12177.tar.gz`: `SETTER_ROWS population=48
  rows=48 bound=48 unbound=0 missing=0 duplicates=0 fabricated=0 derived_checked=47 derived_disagree=0 decisions=2
  decisions_bound=2 archive_sha256=f50a52f4… rev=ee19acbd… skill=rev`, exit 0 (out/counter-M2.out).
- sha256 of the 9 cited files equals the S593/S596–S603 digests in `corpus/SOURCES.md` — I read the same bytes.

## Findings
1. **BLOCKER — K2 fires on P05, P06, P07 (parameter/effect cells misstate the line and contradict the section's
   own glossary and their own twins).** Glossary: `unrelated` = "another variable, or text"; `declares` = "names an
   option or env, sets nothing". P05 `common/arg.cpp:2526` `{"-np", "--parallel"}, "N",` and P07 `:2531`
   `).set_env("LLAMA_ARG_N_PARALLEL"));` are the *same constructs* as P02/P04, which the table labels
   `n_parallel | declares`; P05/P07 carry `- | unrelated`. P06 `:2529` `params.n_parallel = value;` is
   character-identical to P03 `:2521`, which is labelled `n_parallel | overrides`; P06 carries `- | unrelated`.
   All three are neither "another variable" nor "text". A correct non-breaking label exists for P05/P07
   (`n_parallel | declares`, twins P02/P04; counter B3/B4/B7 pass); P06 cannot be fixed inside the frozen
   vocabulary (as `overrides` it would enter R17's mechanically derived overriding set) — the effect menu has no
   bin for "setter unreachable in the pinned server". The condition cells do state "not reachable in
   llama-server", so no value or decision is wrong; the cells are.
2. **DEFECT — R16's router-child clause is defeated for a child preset that carries a `--vision-gemma-*` preset
   option.** `common_preset::to_args` emits `std::map` order (`common/preset.cpp:44-51`) keyed by
   `strcmp(args[0], …)` (`common/arg.h:91-96`); `"--port" < "--vision-gemma-4b-default"`, so the child argv is
   `--port <meta.port> … --vision-gemma-4b-default`, whose lambda sets `params.port = 8014;` (`common/arg.cpp:4753`,
   P23/P24) *after* P41's `--port` (`server-models.cpp:316`). Such a child listens on 8014, not "the free port the
   router chose". The all-other presets sort before `--port` ('e','f','g' < 'p') and are safe. R16 states the free
   port for router children without this qualification; read as a terminal-port statement it is a second K2 hit,
   read as "what P41 contributes" it is not.
3. **DEFECT — Source cells are file-level while the S-rows declare narrow ranges that miss most cited lines.**
   `corpus/SOURCES.md:351` S596 "per-example defaults lines 1365-1380 and option lambdas (`--parallel` 2514-2522)",
   but P08–P10 cite 3318-3323 and P11–P24 cite 4607-4768; `:353` S598 "lines 93-125" but P37 cites 512; `:354`
   S599 "lines 1218-1235" but P39/P40/P41/P42/P44/P45 cite 69, 90, 316, 866, 1292, 2157. Digests match the whole
   file, so K3 ("cites a source not opened") does not fire, but the Source cell does not resolve to the cited line.
4. **NOTE — P37 omits the multi-TCP-host refusal.** `tools/server/server-http.cpp:135-137`
   (`if (port == 0 && n_tcp_hosts > 1) { SRV_ERR("--port 0 is not supported with multiple TCP addresses\n"); return false; }`):
   with two TCP `--host`s, `--port 0` exits before 508-512, so "the server binds any free port" holds only for one
   TCP host. At line 508-512 the row's condition is exact; the omission is a precondition, not a misstated branch.
5. **NOTE — the system config file is an unnamed channel for both defaults.** `common/arg.cpp:779`
   `common_params_apply_system_config(params, ctx_arg.ex)` applies `/etc/llama.cpp/config.ini` or the user
   `config.ini` through the same option handlers (`common/preset.cpp:142-168`) *before* env (`:791-814`) and argv
   (`:816+`). A start with empty argv/env can listen on a config-set port or run a config-set slot count, and R16's
   registry rule ("cites which of these the unit's argv or environment sets") has no branch for it. Within the
   disclosed limit if "a preset file" is read broadly; no host here has such a file (`/etc/llama.cpp/config.ini`
   and `~/.config/llama.cpp/config.ini` absent).
6. **NOTE — no cell states that argv position decides between `--port` and a preset option, or that env is applied
   before argv** (`common/arg.cpp:791-816`). For `--embd-gemma-default --port 9000` the port is 9000; R16's
   parentheticals list 8011 as the preset's port. The overriding set is right, the winner rule is unstated.

## Per-row table (source quoted from b12177)
| Id | verdict | cited source | note |
|---|---|---|---|
| P01 | holds | `common/arg.cpp:1372-1373` `params.n_parallel = -1;     // auto by default` | server branch, before options |
| P02 | holds | `:2514-2515` `{"-np", "--parallel"}, "N",` | declares, scope SERVER |
| P03 | holds | `:2518-2523` `if (value == 0) { throw … } params.n_parallel = value;` | 0 refused, env same lambda |
| P04 | holds | `:2523` `.set_env("LLAMA_ARG_N_PARALLEL").set_examples({LLAMA_EXAMPLE_SERVER})` | declares |
| P05 | **misstates** | `:2526` `{"-np", "--parallel"}, "N",` | twin P02 is `n_parallel/declares`; this is `-/unrelated` |
| P06 | **misstates** | `:2529` `params.n_parallel = value;` | twin P03 is `n_parallel/overrides`; this is `-/unrelated` |
| P07 | **misstates** | `:2531` `).set_env("LLAMA_ARG_N_PARALLEL"));` | twin P04 is `n_parallel/declares`; this is `-/unrelated` |
| P08 | holds | `:3317-3318` `{"--port"}, "PORT",` | declares |
| P09 | holds | `:3320-3323` `params.port = value; … .set_env("LLAMA_ARG_PORT")` | overrides, parsed PORT |
| P10 | holds | `:3323` `.set_examples({LLAMA_EXAMPLE_SERVER}).set_env("LLAMA_ARG_PORT")` | declares |
| P11 | holds | `:4613` `params.port = 8011;` | scope EMBEDDING,SERVER; no env on block |
| P12 | holds | `:4616` `params.n_parallel = 32;` | same block |
| P13–P18 | holds | `:4629,4643,4657,4673,4689,4703` `params.port = 8012;` | FIM presets, SERVER only |
| P19 | holds | `:4717` `params.port = 8013;` | gpt-oss-20b, SERVER,CLI |
| P20 | holds | `:4720` `params.n_parallel = 2;` | same block |
| P21/P22 | holds | `:4735` `params.port = 8013;` / `:4738` `params.n_parallel = 2;` | gpt-oss-120b |
| P23/P24 | holds | `:4753,4764` `params.port = 8014;` | vision-gemma 4b/12b |
| P25 | holds | `common/common.h:464` `int32_t n_parallel            =     1;` | replaced by P01 for the server |
| P26 | holds | `common/common.h:632` `int32_t port                = 9931;` | member initializer |
| P27–P29 | holds | `common/http.h:90,92,94` `parts.port = …` | client URL parse, not listen |
| P30 | holds | `common/http.h:301,316,324` `int port = ntohs(serv_addr.sin_port);` | free-port helper; router uses it |
| P31 | holds | `server-connect.cpp:194,208` `"--port", std::to_string(port),` | server.cpp:341 passes bound port |
| P32 | holds | `server-http.cpp:93-99` `port = std::stoi(getenv("AIP_HTTP_PORT", "8080"));` | read always, applied by P36 |
| P33 | holds | `:116` `port = params.port;` | copies parsed port |
| P34/P35 | holds | `:119,122` `SRV_TRC(…port = %d…)` / `SRV_WRN(…overriding server port…)` | text |
| P36 | holds | `:118,125` `if (gcp.enabled) { … port = gcp.port; }` | overrides every parsed port |
| P37 | holds (NOTE 4) | `:508-512` `} else if (port == 0) { … port = bound_port;` | multi-host precondition omitted |
| P38 | holds | `server-http.h:92` `int port    = 9931;` | overwritten by P33 in init() |
| P39/P40 | holds | `server-models.cpp:69,90` `c.port = port;` / `int port = 0;` | log prefix only (189/191) |
| P41 | holds (DEFECT 2) | `server-models.cpp:314-316` `unset_reserved_args(preset,false); … set_option(… "LLAMA_ARG_PORT" …)` | child parses it via P09; later-sorting preset wins |
| P42 | holds | `:866` `p.unset_option("LLAMA_ARG_PORT");` | preset compare, text |
| P43 | holds | `:1218` `inst.meta.port        = common_http_get_free_port();` | before spawn; <=0 throws (1223) |
| P44 | holds | `:1292` `int  port = inst.meta.port;` | feeds monitor at 1297 |
| P45 | holds | `:2157` `preset_copy.unset_option("LLAMA_ARG_PORT");` | /models text |
| P46 | holds | `server-models.h:80` `int port = 0;` | set by P43 before spawn |
| P47 | holds | `server.cpp:127` `SRV_TRC("%s", "n_parallel is set to auto, …")` | text |
| P48 | holds | `server.cpp:116,126,129-130` `if (params.n_parallel < 0) { … params.n_parallel = 4; … kv_unified = true;` | instance role only |
| R16 | holds (DEFECT 2, NOTEs 5,6) | set `P09,P11,P13–P18,P19,P21,P23,P24,P36,P37,P41` = all 15 port-`overrides` rows | 9931 only under the stated guard; `.sock` at 503-507 |
| R17 | holds | set `P03,P12,P20,P22` = all n_parallel-`overrides` rows; `server.cpp:116` keeps router auto | 4 + unified KV only while auto |

## Deliverables
- `.ufo/waves/round-93/w1/out/RV02SetterRows/counter-M2.out`, `population-check.out`, `archive.sha256`.
- This report. Scratch `/fast/scratch/hyaku/kama-r93/RV02SetterRows/` removed after receipt copy.
- Load at start: `uptime` 92.64/52.42/43.18 (no timing claim made).

VERDICT: falsified — K2 fires on P05/P06/P07 (parameter/effect cells contradict the section's own glossary and their P02/P04/P03 twins); 45 rows, R16 and R17 hold, and R16's router-child clause is defeated for `--vision-gemma-*` presets.
