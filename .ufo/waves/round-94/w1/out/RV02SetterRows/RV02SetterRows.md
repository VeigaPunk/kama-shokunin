# RV02SetterRows — K2 read of C2 setter table (round 94 revision)

Scope: every row P01–P92 + decisions R18/R19 of SKILL.md (rev 6aa5fa6bd9bbf44c4b2ca3f1e2158e7d5aa92623) section "## Listen port and slot-count setters (round 94 revision)" vs the pinned llama.cpp b12177 archive (sha256 f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13 — verified) + S604–S615 census rows. Read surrounding code, callers, consuming variables. No tracked lane files edited.

## Commands and outputs (exit codes)

- `curl …/b12177.tar.gz; sha256sum` → `f50a52f4…ba63eea13` matches frozen pin. exit 0
- `git -C lane show 6aa5fa6b:SKILL.md` → extracted section; 92 P-rows + R18/R19 located (lines 2074–2209). exit 0
- Python byte-check of all P-row Text cells against archive source lines → 92 rows match exactly (P56 diff is only markdown `\|` escaping of `||`). exit 0
- Per-row semantic read (files quoted below). exit 0
- Cross-ref check: lines cited in section intro all resolve (`arg.cpp:729,779; common.cpp:1001; cli-server.h:35-44; server-models.cpp:1218,316,1235; server-common.h:765; server-common.cpp:2236; server-models-sched.cpp:423; server.cpp:116,129; arg.h:91`); S604–S615 present in corpus/SOURCES.md (mined, opened 2026-11-07). exit 0

## Findings

Legend: holds = parameter, ENTRY, scope, condition, effect, value all state source correctly; BLOCKER = misstates under K2; NOTE = vocabulary friction, semantics correct.

### P01–P10 config.ini route — holds
- P01 (arg.cpp:727, comment) `// 1. system-wide: /etc/llama.cpp/config.ini …` — unrelated/comment. holds. Quote (5 words): "1. system-wide: /etc/llama.cpp/config.ini"
- P02 (arg.cpp:728) user-level comment. holds.
- P03 (arg.cpp:729) `common_params_apply_system_config(common_params & params, llama_example ex) {` — definition reads system+user INI. holds.
- P04 (arg.cpp:735) `paths.push_back(program_data / "llama.cpp" / "config.ini");` — Windows program-data path. holds.
- P05 (arg.cpp:738) `paths.push_back("/etc/llama.cpp/config.ini");` — POSIX system path, `#else` of `_WIN32`. holds.
- P06 (arg.cpp:742) `paths.push_back(fs_get_config_directory() / "config.ini");` — user path; what fs returns verified common.cpp:1001–1015 (XDG_CONFIG_HOME or ~/.config, APPENDATA on Windows). holds.
- P07 (arg.cpp:763) `common_presets presets = ctx.load_from_ini(path, global);` — parses each found file. holds.
- P08 (arg.cpp:764) `global.apply_to_params(params);` — INI global section applied. holds. Mechanism verified preset.cpp:142–168 (handler_string/int/bool/void dispatched per option).
- P09 (arg.cpp:767) `it->second.apply_to_params(params);` — default ("default", preset.h:15) section applied after global. holds.
- P10 (arg.cpp:779) `common_params_apply_system_config(params, ctx_arg.ex);` — call inside common_params_parse_ex; verified wrapper common_params_parse at 1258 calls parse_ex, and apply runs before env (791) and argv. "BEFORE env and argv for every common_params_parse caller" correct. holds.

### P11–P20 parser defaults and declares — holds
- P11 (arg.cpp:1373) `params.n_parallel = -1;     // auto by default` — under `} else if (ex == LLAMA_EXAMPLE_SERVER) {` at 1372, in parser_init before options. holds.
- P12 (arg.cpp:2515) `{"-np", "--parallel"}, "N",` — server branch `if (ex == LLAMA_EXAMPLE_SERVER)` at 2512. declares. holds.
- P13 (arg.cpp:2521) `params.n_parallel = value;` — `if (value == 0) throw` at 2518–2520; env LLAMA_ARG_N_PARALLEL at 2523. holds. Value/N (0 refused; −1 keeps auto) correct.
- P14 (2523) env declare, server. holds.
- P15–P17 (2526/2529/2531) `else` branch of server-if at 2512 — reachable for non-server examples incl. llama-cli; never llama-server. "other"/LLAMA_EXAMPLE_COMMON correct. holds.
- P18 (3318) `{"--port"}, "PORT",` — server-only option (set_examples SERVER at 3323). declares. holds.
- P19 (3321) `params.port = value;` — `--port` or env LLAMA_ARG_PORT (3323). holds.
- P20 (3323) env declare. holds.

### P21–P34 preset lambdas — holds
- P21/P22 (4613/4616) `--embd-gemma-default` lambda sets port 8011, n_parallel 32; set_examples({EMBEDDING, SERVER}) at 4621; no env declared → argv-only. holds.
- P23–P28 (4629/4643/4657/4673/4689/4703) FIM Qwen presets → port 8012, SERVER-only at 4635/4649/4663/4679/4695/4709. holds.
- P29/P30 (4717/4720) `--gpt-oss-20b-default` → 8013 / n_parallel 2; SERVER+CLI at 4728. holds.
- P31/P32 (4735/4738) `--gpt-oss-120b-default` → 8013 / 2; SERVER+CLI at 4746. holds.
- P33/P34 (4753/4764) vision-gemma 4b/12b → 8014; SERVER+CLI at 4757/4768. holds.
- Resolved: preset lambda runs when option parsed (preset mechanism verified preset.cpp:150–164 handler_void → `opt.handler_void(params)`).

### P35 — holds with NOTE
- P35 (arg.h:91) `bool operator<(const common_arg& other) const {` — verified strcmp on args[0] (arg.h:91–96). Mechanism claim "router child argv order decides which setter is parsed last" is supported: options stored in `std::map<common_arg,String>` (preset.h:23), so iteration in to_args() (preset.cpp:44) follows operator<, and child argv is rendered via preset.to_args (server-models.cpp:322). BUT Entry cell says "unrelated" while scope ties it to router-child ordering. The frozen vocab defines unrelated as "text/URL parsing, not a setter" — operator< is mechanism, not a URL parser. NOTE (not BLOCKER): labels arguable, semantics stated correctly. Quote: "strcmp(args[0], other.args[0]) < 0"

### P36–P39 — holds
- P36 (common.cpp:1001) `fs_get_config_directory() {` — returns XDG_CONFIG_HOME||~/.config + /llama.cpp (1009–1014). holds.
- P37 (common.h:464) `n_parallel = 1` — member init; server parser P11 replaces with −1 before options. holds.
- P38 (common.h:632) `port = 9931` — member init; value a parse keeps absent setters. holds.
- P39 (common.h:939) declaration of fs_get_config_directory. declares. holds.

### P40–P43 http.h — holds
- P40/P41/P42 (http.h:90/92/94) URL port parsing (stoi / 80 / 443) — client URL parser, not listen port. unrelated. holds.
- P43 (http.h:324) `int port = ntohs(serv_addr.sin_port);` — reads OS-assigned port from getsockname after bind of port 0 (common.h/http.h ~301). Callers verified: cli-server.h:35, server-models.cpp:1218. Entry "unrelated" + Parameter=port is odd vocabulary but condition/effect/copies correct. NOTE at most.

### P44–P47 preset mechanism — holds
- P44 (preset.cpp:142) `apply_to_params(…)` — runs each option handler (150–164). holds.
- P45 (preset.cpp:285) `load_from_ini(…)` — parses INI into presets, section "default" empty default, "*" global (preset.cpp:231,291,335–341). holds.
- P46/P47 declarations (preset.h:47/70). declares. holds.

### P48–P51 cli-server — holds
- P48 (cli-context.h:6) `#include "cli-server.h"`. unrelated (include only). holds.
- P49 (cli-server.h:13) `int port = -1;` — handle member; start() at 35 sets it, not a listen default. default −1. holds.
- P50 (cli-server.h:35) `port = common_http_get_free_port();` — embedded server binds free port, ignores parsed params.port. Verified start() writes server_params.port = port at 44 before llama_server call. holds.
- P51 (cli-server.h:44) `server_params.port = port;` — copies free port into copied params. holds.

### P52–P57 other tools — holds
- P52 (imatrix.cpp:1869) `params.n_parallel = n_seq;` — n_seq from max(1, n_batch/n_ctx) at 1860. other. holds.
- P53/P54 (perplexity.cpp:2009/2012) max(4,n_parallel) hist/hellaswag branch; max(1, n_batch/n_ctx) else branch — conditions correct (2008 branch on hellaswag/winogrande/multiple_choice). other. holds.
- P55 (rpc-server.cpp:80) `port = 50052`. other/default. holds.
- P56 (rpc-server.cpp:132) `} else if (arg == "-p" || arg == "--port") {` — own argv parser text (escaped `||` in table, byte text verified). unrelated (text match, not llama-server --port). holds.
- P57 (rpc-server.cpp:136) `params.port = std::stoi(argv[i]);` — own parser. other/overrides. holds.

### P58–P61 router detection + connect — holds
- P58 (server-common.cpp:2236) `return std::getenv(SERVER_ENV_ROUTER_PORT) != nullptr;` — definition of is_managed_by_router; TRUE = child. router-child/declares. holds.
- P59 (server-common.h:765) `#define SERVER_ENV_ROUTER_PORT "LLAMA_SERVER_ROUTER_PORT"` — presence marks child. declares. holds.
- P60 (server-connect.cpp:194) `bool server_connect::start(const common_params & params, int port) {` — entry anchor; sets no port itself (caller server.cpp:341 passes ctx_http.port). Entry "unrelated" arguably should be "other" (separate llama-connect binary) — NOTE, definition claim correct.
- P61 (server-connect.cpp:208) `"--port", std::to_string(port),` — passes bound port to llama-connect binary. other/copies. holds.

### P62–P68 server-http — holds
- P62 (server-http.cpp:96) `port = std::stoi(getenv("AIP_HTTP_PORT", "8080"));` — getenv helper (99–109) returns default when unset OR empty. Applied only when gcp.enabled = AIP_MODE=="PREDICTION" (93). copies. holds.
- P63 (server-http.cpp:116) `port = params.port;` — init copies parsed port. copies. holds.
- P64/P65 trace/warning text, unrelated. holds.
- P66 (server-http.cpp:125) `port = gcp.port;` — under `if (gcp.enabled)` at 118, replaces parsed port. overrides, value AIP_HTTP_PORT else 8080. holds.
- P67 (server-http.cpp:512) `port = bound_port;` — under `else if (port == 0)` at 508; `.sock` hosts bind unix socket via bind_to_port(host,8080) at 507 ignoring port. overrides OS free port. holds.
- P68 (server-http.h:92) `int port = 9931;` — member init replaced by init copy (P63) before bind. default. holds.

### P69–P92 router/roles — holds
- P69 (server-models-sched.cpp:423) `child_env.push_back(... SERVER_ENV_ROUTER_PORT ... base_params.port)` — measure child also marked managed; role additionally MEASURE via line 424. router-child/copies. holds.
- P70/P71 (server-models.cpp:69/90) monitor child_t port for log prefix (`LOG("[%5d]")` at 189/191). unrelated. holds.
- P72 (server-models.cpp:288) `get_environment() {` — copies router environ verbatim (292–310). "carries LLAMA_SERVER_ROUTER_PORT…" overreads: top-level router's own environ lacks ROUTER_PORT; it is added separately at P84/P69. Wording is generic possession, not claim of presence-at-capture. NOTE.
- P73 (server-models.cpp:312) update_args definition. declares. holds.
- P74 (server-models.cpp:316) `preset.set_option(..., "LLAMA_ARG_PORT", to_string(port));` — renders child preset port from meta.port after unset_reserved_args (314,268–286 which unsets PORT? — verified unset list does NOT include PORT, so set is the primitive; reserved list covers ssl/api/models/connect). "after removing reserved args" correct. The child parses it through --port setter via preset.to_args → argv (preset.cpp:37–76; args.back()) then parse. router-child/overrides free port. holds.
- P75 (server-models.cpp:343) `preset.apply_to_params(params, {MODEL…})` — model keys only for caps refresh. copies/not listen setter. holds.
- P76 (server-models.cpp:399) `base_env(get_environment()),` — base copied to children. copies. holds.
- P77/P81/P83 update_args call sites. copies. holds.
- P78 (server-models.cpp:742) `custom_presets = ctx_preset.load_from_ini(base_params.models_preset, global);` — --models-preset route; cascade at 747–749 + merge into final_presets, rendered via update_args → port/n_parallel settable for children. holds.
- P79/P80/P86 strip/unset LLAMA_ARG_PORT for preset comparison/display (comment 863). unrelated. holds.
- P82 (server-models.cpp:1218) `inst.meta.port = common_http_get_free_port();` — free port stored; handed via P74. copies. holds.
- P84 (server-models.cpp:1235) ROUTER_PORT = base_params.port (router's own port) for child detection. copies. holds.
- P85 (server-models.cpp:1292) `int port = inst.meta.port;` — local copy to monitor watch (1297). copies. holds.
- P87 (server-models.h:80) `int port = 0;` — meta member init; set at P82 before spawn (checked at 1223 → throw if <=0). default 0. holds.
- P88 declaration. declares. holds.
- P89 (server.cpp:103) server_role_detect definition: env-managed → role from CHILD_ROLE; else has_model? INSTANCE : ROUTER (103–112). router/declares. holds.
- P90 trace text (server.cpp:127). unrelated. holds.
- P91 (server.cpp:129) `params.n_parallel = 4;` — under `if (params.n_parallel < 0)` at 126 AND `if (role_type != SERVER_ROLE_ROUTER)` at 116; kv_unified=true at 130. Router keeps auto. server/default 4. holds.
- P92 (server.cpp:752) role_detect call site. copies. holds.

### Decisions R18/R19 — hold
- R18 (port, server+cli+router-child+shared): overrides set P19,P21,P23–29,P31,P33,P34,P38,P49,P50,P66,P67,P68,P74,P87 — each is a port-default/override for its entry (checked: P38/P68/P87 defaults, P49 cli init, P50 cli free port, P66 AIP override, P67 bind-free-port, P74 child port, P19 --port, P21–P34 presets). Text names config.ini port line (P03–P10 route, correctly NOT in overrides set since those rows are Effect=copies) plus argv-order rule (operator< P35 cited via S610) plus per-entry port: --port/env (server), AIP_HTTP_PORT (server), child LLAMA_ARG_PORT free port, CLI embedded free port, config.ini port, 9931 default, --port 0 any-free. Router's own port (non-child instance/router role) covered by P19/P38. No population row sets a listen port for a stated entry that the decision omits: rpc/other (P55–P57) and URL/params-internal rows P40–P43/P61 correctly excluded from decision text (different binaries / not llama-server listen port). Cross-refs common.h:632, server-http.cpp:512, arg.cpp (port defaults) resolve. Claim "argv still beats env beats file" (section intro) grounded at arg.cpp:778–779 + env loop 791+. holds.
- R19 (n_parallel, server+shared): set P11,P13,P22,P30,P32,P37,P91 — server parser default −1 (P11), server --parallel/env (P13), presets (P22=32, P30/P32=2), shared default 1 (P37), auto-resolve 4 (P91). Text names config.ini parallel line (P03–P10, copies-rows correctly excluded from overrides), notes non-server --parallel branch reaches CLI/tools not server (P15–P17), notes router keeps auto/no resolution. No omissions: imatrix/perplexity P52–P54 correctly scoped to other tools. holds.

## Deliverables (paths in out dir)

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-94/w1/out/RV02SetterRows/RV02SetterRows.md (this report; canonical trajectory copy)

## Notes (no BLOCKER)
- N1 P35 Entry "unrelated": mechanism row for router-child ordering; vocab friction, semantics right.
- N2 P60 Entry "unrelated" for llama-connect child anchor; "other" fits vocab better, P61 already uses it. Semantics right.
- N3 P72 "carries LLAMA_SERVER_ROUTER_PORT" — router's own environ doesn't contain it; added at P84/P69. Generic wording, not a false presence claim.
- N4 P43 Entry "unrelated" with Parameter=port — readback not listen-setter; condition/effect correct.

VERDICT: holds — All 92 rows and both decisions verified against pinned b12177 source; no BLOCKER misstatements, four vocabulary NOTEs only.
