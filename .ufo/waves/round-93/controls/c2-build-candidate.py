#!/usr/bin/env python3
"""Round-93 C2 pre-freeze candidate builder: renders the candidate section rows from the pinned
archive lines and the L1's hand-written reading of each line (META below). Text cells are copied
from the archive bytes, never typed. Usage: c2-build-candidate.py <extracted llama.cpp-b12177 dir> > section.md
"""
import sys
from pathlib import Path

root = Path(sys.argv[1])
SRC = {"common/arg.cpp": "S596", "common/common.h": "S593", "tools/server/server.cpp": "S597",
       "tools/server/server-http.cpp": "S598", "tools/server/server-models.cpp": "S599",
       "common/http.h": "S600", "tools/server/server-connect.cpp": "S601", "tools/server/server-http.h": "S602",
       "tools/server/server-models.h": "S603"}
SV = "LLAMA_EXAMPLE_SERVER"
CS = "LLAMA_EXAMPLE_CLI, LLAMA_EXAMPLE_SERVER"
PRE = "preset option `{o}` (argv only: the block declares no env name); the preset lambda runs when the option is parsed"
# (file, line): (parameter, scope, condition, effect, value)
META = {
    ("common/arg.cpp", 1373): ("n_parallel", "llama-server parser", "per-example default under `ex == LLAMA_EXAMPLE_SERVER` (line 1372), set before any option is read", "default", "-1"),
    ("common/arg.cpp", 2515): ("n_parallel", SV, "declares `-np`/`--parallel` for the server (inside `if (ex == LLAMA_EXAMPLE_SERVER)`, line 2512)", "declares", "-"),
    ("common/arg.cpp", 2521): ("n_parallel", SV, "`-np N` / `--parallel N` or env `LLAMA_ARG_N_PARALLEL` (line 2523); value 0 is refused (lines 2518-2520)", "overrides", "the parsed N (0 refused; -1 keeps auto)"),
    ("common/arg.cpp", 2523): ("n_parallel", SV, "declares env `LLAMA_ARG_N_PARALLEL` for `--parallel` (server branch)", "declares", "-"),
    ("common/arg.cpp", 2526): ("-", "LLAMA_EXAMPLE_COMMON", "`--parallel` of the `else` branch of `if (ex == LLAMA_EXAMPLE_SERVER)` (line 2512): registered only when the parser is built for another tool, never for llama-server", "unrelated", "-"),
    ("common/arg.cpp", 2529): ("-", "LLAMA_EXAMPLE_COMMON", "lambda of the non-server `--parallel` (`else` branch, line 2524): not reachable in llama-server", "unrelated", "-"),
    ("common/arg.cpp", 2531): ("-", "LLAMA_EXAMPLE_COMMON", "env `LLAMA_ARG_N_PARALLEL` of the non-server `--parallel` (`else` branch): not reachable in llama-server", "unrelated", "-"),
    ("common/arg.cpp", 3318): ("port", SV, "declares `--port`", "declares", "-"),
    ("common/arg.cpp", 3321): ("port", SV, "`--port PORT` or env `LLAMA_ARG_PORT` (line 3323); `--port 0` asks for any free port (row P37)", "overrides", "the parsed PORT"),
    ("common/arg.cpp", 3323): ("port", SV, "declares env `LLAMA_ARG_PORT` for `--port`", "declares", "-"),
    ("common/arg.cpp", 4613): ("port", "LLAMA_EXAMPLE_EMBEDDING, LLAMA_EXAMPLE_SERVER", PRE.format(o="--embd-gemma-default"), "overrides", "8011"),
    ("common/arg.cpp", 4616): ("n_parallel", "LLAMA_EXAMPLE_EMBEDDING, LLAMA_EXAMPLE_SERVER", PRE.format(o="--embd-gemma-default"), "overrides", "32"),
    ("common/arg.cpp", 4629): ("port", SV, PRE.format(o="--fim-qwen-1.5b-default"), "overrides", "8012"),
    ("common/arg.cpp", 4643): ("port", SV, PRE.format(o="--fim-qwen-3b-default"), "overrides", "8012"),
    ("common/arg.cpp", 4657): ("port", SV, PRE.format(o="--fim-qwen-7b-default"), "overrides", "8012"),
    ("common/arg.cpp", 4673): ("port", SV, PRE.format(o="--fim-qwen-7b-spec"), "overrides", "8012"),
    ("common/arg.cpp", 4689): ("port", SV, PRE.format(o="--fim-qwen-14b-spec"), "overrides", "8012"),
    ("common/arg.cpp", 4703): ("port", SV, PRE.format(o="--fim-qwen-30b-default"), "overrides", "8012"),
    ("common/arg.cpp", 4717): ("port", CS, PRE.format(o="--gpt-oss-20b-default"), "overrides", "8013"),
    ("common/arg.cpp", 4720): ("n_parallel", CS, PRE.format(o="--gpt-oss-20b-default"), "overrides", "2"),
    ("common/arg.cpp", 4735): ("port", CS, PRE.format(o="--gpt-oss-120b-default"), "overrides", "8013"),
    ("common/arg.cpp", 4738): ("n_parallel", CS, PRE.format(o="--gpt-oss-120b-default"), "overrides", "2"),
    ("common/arg.cpp", 4753): ("port", CS, PRE.format(o="--vision-gemma-4b-default"), "overrides", "8014"),
    ("common/arg.cpp", 4764): ("port", CS, PRE.format(o="--vision-gemma-12b-default"), "overrides", "8014"),
    ("common/common.h", 464): ("n_parallel", "every tool (shared `common_params`)", "member initializer; for llama-server replaced by the parser's per-example default (row P01) before options are read", "default", "1"),
    ("common/common.h", 632): ("port", "every tool (shared `common_params`)", "member initializer of `common_params::port`; the value a llama-server parses when no setter row applies", "default", "9931"),
    ("common/http.h", 90): ("-", "HTTP client URL parser", "port of a parsed URL (`parts`), explicit `:port` in the URL; not the server's listen port", "unrelated", "-"),
    ("common/http.h", 92): ("-", "HTTP client URL parser", "scheme `http` without an explicit port; not the server's listen port", "unrelated", "-"),
    ("common/http.h", 94): ("-", "HTTP client URL parser", "scheme `https` without an explicit port; not the server's listen port", "unrelated", "-"),
    ("common/http.h", 324): ("port", "`common_http_get_free_port()`", "reads back (`getsockname`) the port the OS gave a throw-away socket bound to port 0 (line 301), closes it and returns it; the router uses it for a child (row P43)", "copies", "-"),
    ("tools/server/server-connect.cpp", 208): ("port", "`--connect` (llama-connect child)", "passes the port the server is bound to (`ctx_http.port`, `server.cpp:341`) to the separate `llama-connect` binary; sets nothing in llama-server", "copies", "-"),
    ("tools/server/server.cpp", 127): ("-", "llama-server startup", "trace text inside `SRV_TRC`; not an assignment", "unrelated", "-"),
    ("tools/server/server.cpp", 129): ("n_parallel", "llama-server startup (`server_prepare_params`)", "`params.n_parallel < 0` (auto, line 126) and the role is not the router (line 116): auto resolves to 4 slots with a unified KV cache (line 130); the router role keeps auto", "default", "4"),
    ("tools/server/server-http.cpp", 96): ("port", "llama-server HTTP init", "constructor of `gcp_params`: reads `AIP_HTTP_PORT` (8080 when unset or empty, helper `getenv` line 99) into `gcp.port`; applied only under `AIP_MODE=PREDICTION` by row P36", "copies", "-"),
    ("tools/server/server-http.cpp", 116): ("port", "llama-server HTTP init", "`server_http_context::init` copies the parsed `params.port` into the listen port", "copies", "-"),
    ("tools/server/server-http.cpp", 119): ("-", "llama-server HTTP init", "trace text inside `SRV_TRC`; not an assignment", "unrelated", "-"),
    ("tools/server/server-http.cpp", 122): ("-", "llama-server HTTP init", "warning text inside `SRV_WRN` (printed when the AIP port differs); not an assignment", "unrelated", "-"),
    ("tools/server/server-http.cpp", 125): ("port", "llama-server HTTP init", "env `AIP_MODE` equals `PREDICTION` (line 93, checked at line 118): the listen port becomes `AIP_HTTP_PORT`, replacing every parsed port", "overrides", "AIP_HTTP_PORT, else 8080"),
    ("tools/server/server-http.cpp", 512): ("port", "llama-server HTTP bind", "the port at bind time is 0 (`--port 0` / `LLAMA_ARG_PORT=0`, line 508) on a TCP host: the server binds any free port and records it; a `.sock` host binds a Unix socket and ignores the port (lines 503-507)", "overrides", "the OS-chosen free port"),
    ("tools/server/server-http.h", 92): ("port", "llama-server HTTP context", "member initializer of `server_http_context::port`; replaced by row P33 in `init()` before any bind", "default", "9931"),
    ("tools/server/server-models.cpp", 69): ("-", "router child monitor", "records a child's port in the monitor entry for log prefixes; sets no listen port", "unrelated", "-"),
    ("tools/server/server-models.cpp", 90): ("-", "router child monitor", "member initializer of the monitor's `child_t::port` (log prefix); sets no listen port", "unrelated", "-"),
    ("tools/server/server-models.cpp", 316): ("port", "router child spawn (`update_args`)", "a router spawning a model instance writes `LLAMA_ARG_PORT` = the instance's `meta.port` into the child's preset, after removing reserved args (line 314): the child parses it through row P09", "overrides", "the free port of row P43"),
    ("tools/server/server-models.cpp", 866): ("-", "router preset comparison", "removes `LLAMA_ARG_PORT` from a preset copy before comparing presets; sets no port", "unrelated", "-"),
    ("tools/server/server-models.cpp", 1218): ("port", "router child spawn (`load`)", "a router loading a model instance stores a free port from `common_http_get_free_port()` (row P30) in `meta.port`; row P41 hands it to the child", "copies", "-"),
    ("tools/server/server-models.cpp", 1292): ("port", "router child spawn", "copies the child's `meta.port` for the monitor (row P39); sets no listen port", "copies", "-"),
    ("tools/server/server-models.cpp", 2157): ("-", "router `/models` status answer", "removes `LLAMA_ARG_PORT` from the preset text the router shows; sets no port", "unrelated", "-"),
    ("tools/server/server-models.h", 80): ("port", "router model metadata", "member initializer of `server_model_meta::port`; set by row P43 before an instance is spawned", "default", "0"),
}

order = sorted(META)
ids = {k: f"P{i + 1:02d}" for i, k in enumerate(order)}
print("| Id | File | Line | Text (pinned b12177 bytes) | Parameter | Scope | Condition | Effect | Value | Source |")
print("|---|---|---|---|---|---|---|---|---|---|")
for k in order:
    f, ln = k
    text = (root / f).read_text().split("\n")[ln - 1].strip()
    assert "|" not in text and "`" not in text, k
    p, sc, cond, eff, val = META[k]
    print(f"| {ids[k]} | {f} | {ln} | `{text}` | {p} | {sc} | {cond} | {eff} | {val} | {SRC[f]} |")
for k in order:
    print(f"{ids[k]} {k[0]}:{k[1]}", file=sys.stderr)
