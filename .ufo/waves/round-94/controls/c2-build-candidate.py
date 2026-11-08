#!/usr/bin/env python3
"""Round-94 C2 candidate builder: renders the round-94 setter section rows from the pinned
archive lines and the L1's hand-written reading of each line (META below). Text cells are copied
from the archive bytes, never typed. The population is the frozen round-94 set: every line of
common/ and tools/ (*.cpp, *.h, *.hpp) matching POP_RE, the config-route pattern, or an
entry-point anchor. Each row carries an ENTRY cell (which parsed program the row governs).
Usage: round94-build-setter-candidate.py <extracted llama.cpp-b12177 dir> > section.md
"""
import sys
from pathlib import Path

root = Path(sys.argv[1])
SRC = {"common/arg.cpp": "S596", "common/arg.h": "S610", "common/common.h": "S593", "common/common.cpp": "S605",
       "common/http.h": "S600", "common/preset.cpp": "S604", "common/preset.h": "S611",
       "tools/cli/cli-context.h": "S612", "tools/cli/cli-server.h": "S606", "tools/imatrix/imatrix.cpp": "S613",
       "tools/perplexity/perplexity.cpp": "S614", "tools/rpc/rpc-server.cpp": "S615",
       "tools/server/server.cpp": "S597", "tools/server/server-connect.cpp": "S601", "tools/server/server-http.cpp": "S598",
       "tools/server/server-http.h": "S602", "tools/server/server-models.cpp": "S599", "tools/server/server-models.h": "S603",
       "tools/server/server-common.cpp": "S607", "tools/server/server-common.h": "S608", "tools/server/server-models-sched.cpp": "S609"}
SV = "LLAMA_EXAMPLE_SERVER"
CS = "LLAMA_EXAMPLE_CLI, LLAMA_EXAMPLE_SERVER"
EG = "LLAMA_EXAMPLE_EMBEDDING, LLAMA_EXAMPLE_SERVER"
PRE = "preset option `{o}` (argv only: the block declares no env name); the preset lambda runs when the option is parsed"
# entry vocabulary: server | cli | router-child | router | shared | other | unrelated
# (file, line): (parameter, entry, scope, condition, effect, value)
META = {
    # ---- config.ini route (arg.cpp 727-779) ----
    ("common/arg.cpp", 727): ("-", "shared", "config.ini route", "comment naming the system-wide config path", "unrelated", "-"),
    ("common/arg.cpp", 728): ("-", "shared", "config.ini route", "comment naming the user-level config path", "unrelated", "-"),
    ("common/arg.cpp", 729): ("-", "shared", "config.ini route", "`common_params_apply_system_config` definition: reads system+user config.ini and applies presets before env/argv", "copies", "-"),
    ("common/arg.cpp", 735): ("-", "shared", "config.ini route", "pushes `%PROGRAMDATA%/llama.cpp/config.ini` (Windows) onto the config path list", "copies", "-"),
    ("common/arg.cpp", 738): ("-", "shared", "config.ini route", "pushes `/etc/llama.cpp/config.ini` onto the config path list", "copies", "-"),
    ("common/arg.cpp", 742): ("-", "shared", "config.ini route", "pushes `fs_get_config_directory()/config.ini` (XDG_CONFIG_HOME or ~/.config) onto the config path list", "copies", "-"),
    ("common/arg.cpp", 763): ("-", "shared", "config.ini route", "`ctx.load_from_ini(path, global)` parses each config.ini into presets", "copies", "-"),
    ("common/arg.cpp", 764): ("-", "shared", "config.ini route", "`global.apply_to_params(params)` applies the INI global section to params", "copies", "-"),
    ("common/arg.cpp", 767): ("-", "shared", "config.ini route", "`it->second.apply_to_params(params)` applies the INI default section", "copies", "-"),
    ("common/arg.cpp", 779): ("-", "shared", "config.ini route", "`common_params_apply_system_config(params, ctx_arg.ex)` call inside `common_params_parse_ex`: config.ini applied BEFORE env and argv for every common_params_parse caller", "copies", "-"),
    # ---- r93 rows (P01-P48), P05-P07 corrected ----
    ("common/arg.cpp", 1373): ("n_parallel", "server", "llama-server parser", "per-example default under `ex == LLAMA_EXAMPLE_SERVER` (line 1372), set before any option is read", "default", "-1"),
    ("common/arg.cpp", 2515): ("n_parallel", "server", SV, "declares `-np`/`--parallel` for the server (inside `if (ex == LLAMA_EXAMPLE_SERVER)`, line 2512)", "declares", "-"),
    ("common/arg.cpp", 2521): ("n_parallel", "server", SV, "`-np N` / `--parallel N` or env `LLAMA_ARG_N_PARALLEL` (line 2523); value 0 is refused (lines 2518-2520)", "overrides", "the parsed N (0 refused; -1 keeps auto)"),
    ("common/arg.cpp", 2523): ("n_parallel", "server", SV, "declares env `LLAMA_ARG_N_PARALLEL` for `--parallel` (server branch)", "declares", "-"),
    ("common/arg.cpp", 2526): ("n_parallel", "other", "LLAMA_EXAMPLE_COMMON", "`--parallel` of the `else` branch of `if (ex == LLAMA_EXAMPLE_SERVER)` (line 2512): registered for non-server tools (llama-cli and others), never for llama-server", "declares", "-"),
    ("common/arg.cpp", 2529): ("n_parallel", "other", "LLAMA_EXAMPLE_COMMON", "lambda of the non-server `--parallel` (`else` branch, line 2524): reachable in llama-cli and other tools, not llama-server", "overrides", "the parsed N"),
    ("common/arg.cpp", 2531): ("n_parallel", "other", "LLAMA_EXAMPLE_COMMON", "env `LLAMA_ARG_N_PARALLEL` of the non-server `--parallel` (`else` branch): reachable in llama-cli and other tools, not llama-server", "declares", "-"),
    ("common/arg.cpp", 3318): ("port", "server", SV, "declares `--port`", "declares", "-"),
    ("common/arg.cpp", 3321): ("port", "server", SV, "`--port PORT` or env `LLAMA_ARG_PORT` (line 3323); `--port 0` asks for any free port (row for `server-http.cpp:512`)", "overrides", "the parsed PORT"),
    ("common/arg.cpp", 3323): ("port", "server", SV, "declares env `LLAMA_ARG_PORT` for `--port`", "declares", "-"),
    ("common/arg.cpp", 4613): ("port", "server", EG, PRE.format(o="--embd-gemma-default"), "overrides", "8011"),
    ("common/arg.cpp", 4616): ("n_parallel", "server", EG, PRE.format(o="--embd-gemma-default"), "overrides", "32"),
    ("common/arg.cpp", 4629): ("port", "server", SV, PRE.format(o="--fim-qwen-1.5b-default"), "overrides", "8012"),
    ("common/arg.cpp", 4643): ("port", "server", SV, PRE.format(o="--fim-qwen-3b-default"), "overrides", "8012"),
    ("common/arg.cpp", 4657): ("port", "server", SV, PRE.format(o="--fim-qwen-7b-default"), "overrides", "8012"),
    ("common/arg.cpp", 4673): ("port", "server", SV, PRE.format(o="--fim-qwen-7b-spec"), "overrides", "8012"),
    ("common/arg.cpp", 4689): ("port", "server", SV, PRE.format(o="--fim-qwen-14b-spec"), "overrides", "8012"),
    ("common/arg.cpp", 4703): ("port", "server", SV, PRE.format(o="--fim-qwen-30b-default"), "overrides", "8012"),
    ("common/arg.cpp", 4717): ("port", "server", CS, PRE.format(o="--gpt-oss-20b-default"), "overrides", "8013"),
    ("common/arg.cpp", 4720): ("n_parallel", "server", CS, PRE.format(o="--gpt-oss-20b-default"), "overrides", "2"),
    ("common/arg.cpp", 4735): ("port", "server", CS, PRE.format(o="--gpt-oss-120b-default"), "overrides", "8013"),
    ("common/arg.cpp", 4738): ("n_parallel", "server", CS, PRE.format(o="--gpt-oss-120b-default"), "overrides", "2"),
    ("common/arg.cpp", 4753): ("port", "server", CS, PRE.format(o="--vision-gemma-4b-default"), "overrides", "8014"),
    ("common/arg.cpp", 4764): ("port", "server", CS, PRE.format(o="--vision-gemma-12b-default"), "overrides", "8014"),
    # ---- arg.h / common ----
    ("common/arg.h", 91): ("-", "unrelated", "preset argv ordering", "`common_arg::operator<` orders preset options by first arg name (strcmp on args[0]); the router child argv order that decides which setter is parsed last", "copies", "-"),
    ("common/common.cpp", 1001): ("-", "shared", "config.ini route", "`fs_get_config_directory()` returns XDG_CONFIG_HOME or ~/.config + /llama.cpp; supplies the user config.ini path", "copies", "-"),
    ("common/common.h", 464): ("n_parallel", "shared", "every tool (shared `common_params`)", "member initializer; for llama-server replaced by the parser's per-example default before options are read", "default", "1"),
    ("common/common.h", 632): ("port", "shared", "every tool (shared `common_params`)", "member initializer of `common_params::port`; the value a start parses when no setter row applies", "default", "9931"),
    ("common/common.h", 939): ("-", "shared", "config.ini route", "declaration of `fs_get_config_directory()`", "declares", "-"),
    ("common/http.h", 90): ("-", "unrelated", "HTTP client URL parser", "port of a parsed URL (`parts`), explicit `:port` in the URL; not the server's listen port", "unrelated", "-"),
    ("common/http.h", 92): ("-", "unrelated", "HTTP client URL parser", "scheme `http` without an explicit port; not the server's listen port", "unrelated", "-"),
    ("common/http.h", 94): ("-", "unrelated", "HTTP client URL parser", "scheme `https` without an explicit port; not the server's listen port", "unrelated", "-"),
    ("common/http.h", 324): ("port", "unrelated", "`common_http_get_free_port()`", "reads back (`getsockname`) the port the OS gave a throw-away socket bound to port 0 (line 301); the router and llama-cli use it for a child/embedded server", "copies", "-"),
    # ---- preset.cpp / preset.h (config route mechanism) ----
    ("common/preset.cpp", 142): ("-", "shared", "config.ini route", "`common_preset::apply_to_params` runs each preset option's handler against params; the mechanism config.ini and --models-preset use to set port/n_parallel", "copies", "-"),
    ("common/preset.cpp", 285): ("-", "shared", "config.ini route", "`common_preset_context::load_from_ini` parses an INI file into presets (config.ini and --models-preset)", "copies", "-"),
    ("common/preset.h", 47): ("-", "shared", "config.ini route", "declaration of `apply_to_params`", "declares", "-"),
    ("common/preset.h", 70): ("-", "shared", "config.ini route", "declaration of `load_from_ini`", "declares", "-"),
    # ---- cli-server.h (llama-cli embedded server) ----
    ("tools/cli/cli-context.h", 6): ("-", "cli", "llama-cli embedded server", "`#include \"cli-server.h\"` pulls the embedded-server helper into cli-context", "unrelated", "-"),
    ("tools/cli/cli-server.h", 13): ("port", "cli", "llama-cli embedded server", "member `int port = -1` of the embedded-server handle; set at start, not a listen default", "default", "-1"),
    ("tools/cli/cli-server.h", 35): ("port", "cli", "llama-cli embedded server", "`port = common_http_get_free_port()`: llama-cli's embedded server binds a free port, never the parsed params.port", "overrides", "the OS-chosen free port"),
    ("tools/cli/cli-server.h", 44): ("port", "cli", "llama-cli embedded server", "`server_params.port = port`: hands the free port to the embedded `llama_server` call", "copies", "-"),
    # ---- other tools (POP_RE matches, not llama-server) ----
    ("tools/imatrix/imatrix.cpp", 1869): ("n_parallel", "other", "imatrix", "`params.n_parallel = n_seq` sets imatrix's own sequence count; not llama-server", "overrides", "n_seq"),
    ("tools/perplexity/perplexity.cpp", 2009): ("n_parallel", "other", "perplexity", "`params.n_parallel = std::max(4, params.n_parallel)` for perplexity; not llama-server", "overrides", "max(4, n_parallel)"),
    ("tools/perplexity/perplexity.cpp", 2012): ("n_parallel", "other", "perplexity", "`params.n_parallel = std::max(1, params.n_batch / n_ctx)` for perplexity; not llama-server", "overrides", "max(1, n_batch/n_ctx)"),
    ("tools/rpc/rpc-server.cpp", 80): ("port", "other", "rpc-server", "`int port = 50052` member initializer of the rpc-server default; not llama-server", "default", "50052"),
    ("tools/rpc/rpc-server.cpp", 132): ("-", "other", "rpc-server", "`arg == \"-p\" || arg == \"--port\"` text in rpc-server's own argv parser; not llama-server's --port", "unrelated", "-"),
    ("tools/rpc/rpc-server.cpp", 136): ("port", "other", "rpc-server", "`params.port = std::stoi(argv[i])` in rpc-server's own argv parser; not llama-server", "overrides", "the parsed port"),
    # ---- server-connect.cpp ----
    ("tools/server/server-connect.cpp", 194): ("-", "unrelated", "`--connect` (llama-connect child)", "`server_connect::start` definition; the entry anchor, sets no port itself", "declares", "-"),
    ("tools/server/server-connect.cpp", 208): ("port", "other", "`--connect` (llama-connect child)", "passes the port the server is bound to (`ctx_http.port`) to the separate `llama-connect` binary; sets nothing in llama-server", "copies", "-"),
    # ---- server-http.cpp / .h ----
    ("tools/server/server-http.cpp", 96): ("port", "server", "llama-server HTTP init", "constructor of `gcp_params`: reads `AIP_HTTP_PORT` (8080 when unset or empty) into `gcp.port`; applied only under `AIP_MODE=PREDICTION`", "copies", "-"),
    ("tools/server/server-http.cpp", 116): ("port", "server", "llama-server HTTP init", "`server_http_context::init` copies the parsed `params.port` into the listen port", "copies", "-"),
    ("tools/server/server-http.cpp", 119): ("-", "server", "llama-server HTTP init", "trace text inside `SRV_TRC`; not an assignment", "unrelated", "-"),
    ("tools/server/server-http.cpp", 122): ("-", "server", "llama-server HTTP init", "warning text inside `SRV_WRN` (printed when the AIP port differs); not an assignment", "unrelated", "-"),
    ("tools/server/server-http.cpp", 125): ("port", "server", "llama-server HTTP init", "env `AIP_MODE` equals `PREDICTION`: the listen port becomes `AIP_HTTP_PORT`, replacing every parsed port", "overrides", "AIP_HTTP_PORT, else 8080"),
    ("tools/server/server-http.cpp", 512): ("port", "server", "llama-server HTTP bind", "the port at bind time is 0 (`--port 0` / `LLAMA_ARG_PORT=0`) on a TCP host: the server binds any free port and records it; a `.sock` host binds a Unix socket", "overrides", "the OS-chosen free port"),
    ("tools/server/server-http.h", 92): ("port", "server", "llama-server HTTP context", "member initializer of `server_http_context::port`; replaced by the init copy before any bind", "default", "9931"),
    # ---- server-models.cpp / .h (router child spawn) ----
    ("tools/server/server-models.cpp", 69): ("-", "router", "router child monitor", "records a child's port in the monitor entry for log prefixes; sets no listen port", "unrelated", "-"),
    ("tools/server/server-models.cpp", 90): ("-", "router", "router child monitor", "member initializer of the monitor's `child_t::port` (log prefix); sets no listen port", "unrelated", "-"),
    ("tools/server/server-models.cpp", 288): ("-", "router", "router child spawn", "`get_environment()` copies the router's whole environment for the child; carries `LLAMA_SERVER_ROUTER_PORT` and any inherited `AIP_*`/`LLAMA_ARG_*`", "copies", "-"),
    ("tools/server/server-models.cpp", 312): ("-", "router-child", "router child spawn (`update_args`)", "`server_model_meta::update_args` definition: renders the child's argv from its preset", "declares", "-"),
    ("tools/server/server-models.cpp", 316): ("port", "router-child", "router child spawn (`update_args`)", "a router spawning a model instance writes `LLAMA_ARG_PORT` = the instance's `meta.port` into the child's preset, after removing reserved args; the child parses it through the `--port` setter", "overrides", "the free port of the child"),
    ("tools/server/server-models.cpp", 343): ("-", "router-child", "router child caps refresh", "`preset.apply_to_params(params, {...})` applies a child preset's model-related keys for capability refresh; not a listen-port setter", "copies", "-"),
    ("tools/server/server-models.cpp", 399): ("-", "router", "router child spawn", "`base_env(get_environment())`: the router's environment (incl. any inherited setter env) is the base the child's env copies", "copies", "-"),
    ("tools/server/server-models.cpp", 478): ("-", "router-child", "router child spawn", "`meta.update_args(ctx_preset, bin_path)` call site rendering the child argv", "copies", "-"),
    ("tools/server/server-models.cpp", 742): ("-", "router", "router preset (`--models-preset`)", "`ctx_preset.load_from_ini(base_params.models_preset, global)`: a router loads its model presets from an INI file; preset options can set port/n_parallel for children", "copies", "-"),
    ("tools/server/server-models.cpp", 863): ("-", "router", "router preset comparison", "comment: `update_args()` injects HOST/PORT/ALIAS/LOG_COLORS, stripped before comparing presets", "unrelated", "-"),
    ("tools/server/server-models.cpp", 866): ("-", "router", "router preset comparison", "removes `LLAMA_ARG_PORT` from a preset copy before comparing presets; sets no port", "unrelated", "-"),
    ("tools/server/server-models.cpp", 1020): ("-", "router-child", "router child spawn", "`inst.meta.update_args(ctx_preset, bin_path)` call site rendering the child argv", "copies", "-"),
    ("tools/server/server-models.cpp", 1218): ("port", "router-child", "router child spawn (`load`)", "a router loading a model instance stores a free port from `common_http_get_free_port()` in `meta.port`; the child setter row hands it to the child", "copies", "-"),
    ("tools/server/server-models.cpp", 1231): ("-", "router-child", "router child spawn", "`inst.meta.update_args(ctx_preset, bin_path)` call site rendering the child argv", "copies", "-"),
    ("tools/server/server-models.cpp", 1292): ("port", "router", "router child spawn", "copies the child's `meta.port` for the monitor; sets no listen port", "copies", "-"),
    ("tools/server/server-models.cpp", 2157): ("-", "router", "router `/models` status answer", "removes `LLAMA_ARG_PORT` from the preset text the router shows; sets no port", "unrelated", "-"),
    ("tools/server/server-models.h", 80): ("port", "router-child", "router model metadata", "member initializer of `server_model_meta::port`; set by the child-spawn row before an instance is spawned", "default", "0"),
    ("tools/server/server-models.h", 111): ("-", "router-child", "router child spawn", "declaration of `update_args`", "declares", "-"),
    # ---- server.cpp (role detection + n_parallel default) ----
    ("tools/server/server.cpp", 103): ("-", "router", "llama-server startup", "`server_role_detect` definition: `LLAMA_SERVER_ROUTER_PORT` env or model presence decides router vs instance role", "declares", "-"),
    ("tools/server/server.cpp", 127): ("-", "server", "llama-server startup", "trace text inside `SRV_TRC`; not an assignment", "unrelated", "-"),
    ("tools/server/server.cpp", 129): ("n_parallel", "server", "llama-server startup (`server_prepare_params`)", "`params.n_parallel < 0` (auto) and the role is not the router: auto resolves to 4 slots with a unified KV cache; the router role keeps auto", "default", "4"),
    ("tools/server/server.cpp", 752): ("-", "router", "llama-server startup", "`server_role_detect(params, role)` call site choosing router vs instance", "copies", "-"),
    # ---- server-common.cpp / .h (router-child detection) ----
    ("tools/server/server-common.cpp", 2236): ("-", "router-child", "router-child detection", "`is_managed_by_router()` returns true when `LLAMA_SERVER_ROUTER_PORT` is set: a process with that env is a router child, not a router", "declares", "-"),
    ("tools/server/server-common.h", 765): ("-", "router-child", "router-child detection", "`#define SERVER_ENV_ROUTER_PORT \"LLAMA_SERVER_ROUTER_PORT\"`: the env var whose presence makes a llama-server process a router child", "declares", "-"),
    ("tools/server/server-models.cpp", 1235): ("-", "router-child", "router child spawn", "`child_env.push_back(SERVER_ENV_ROUTER_PORT + \"=\" + base_params.port)`: the router sets the child's `LLAMA_SERVER_ROUTER_PORT` to its own port so the child detects it is managed", "copies", "-"),
    ("tools/server/server-models-sched.cpp", 423): ("-", "router-child", "router child spawn (measure)", "`child_env.push_back(SERVER_ENV_ROUTER_PORT + \"=\" + base_params.port)`: the measure process also gets the router-port env, marking it a router child", "copies", "-"),
}
order = sorted(META)
ids = {k: f"P{i + 1:02d}" for i, k in enumerate(order)}
print("| Id | File | Line | Text (pinned b12177 bytes) | Parameter | Entry | Scope | Condition | Effect | Value | Source |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for k in order:
    f, ln = k
    text = (root / f).read_text().split("\n")[ln - 1].strip()
    text = text.replace("|", "\\|")
    assert "`" not in text, k
    p, ent, sc, cond, eff, val = META[k]
    esc = lambda s: str(s).replace("|", "\\|")
    print(f"| {ids[k]} | {f} | {ln} | `{text}` | {esc(p)} | {esc(ent)} | {esc(sc)} | {esc(cond)} | {esc(eff)} | {esc(val)} | {SRC.get(f, 'S596')} |")
for k in order:
    print(f"{ids[k]} {k[0]}:{k[1]}", file=sys.stderr)
