#!/usr/bin/env python3
"""pin.py — fetch llama.cpp @704366d server sources and pin health/shutdown line ranges.

Read-only urllib GETs against raw.githubusercontent.com at one pinned commit.
Saves raw copies under llama.cpp-704366d/<repo-relative path> and writes
pins.json with url/sha256/bytes per file plus located line ranges.

All line ranges are located by string search (anchor regex + brace matching or
explicit end anchors) — never hardcoded numbers. Exit 2 if any pin fails.
"""
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

COMMIT = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"
BASE = f"https://raw.githubusercontent.com/ggml-org/llama.cpp/{COMMIT}/"
OUT_DIR = Path(__file__).resolve().parent / f"llama.cpp-{COMMIT[:9]}"
PINS_JSON = Path(__file__).resolve().parent / "pins.json"

# The four named files, plus server-queue.{cpp,h}: that is where the shutdown
# path's primitives (server_queue::terminate / start_loop, called from
# server_context::terminate in the signal handler) are defined.
FILES = [
    "tools/server/server.cpp",
    "tools/server/server-context.cpp",
    "tools/server/server-http.cpp",
    "tools/server/README.md",
    "tools/server/server-queue.cpp",
    "tools/server/server-queue.h",
]

# ---------------------------------------------------------------------------
# Locators. Each is (kind, file, spec):
#   block: find `start` regex (after optional `start_after` line), then match
#          braces from the first `{` at/after that line to its closing `}`.
#   span:  `start` regex to `end` regex, both inclusive, after `start_after`.
#   lines: every line matching `match` is recorded as a single-line range.
# `occurrence` (default 1) skips earlier matches of `start`.
# ---------------------------------------------------------------------------
PINS = {
    # --- signal path (server.cpp) ---
    "sigint_sigterm_registration": ("span", "tools/server/server.cpp", {
        "start": r"struct sigaction sigint_action;",
        "end": r"sigaction\(SIGTERM, &sigint_action, NULL\);",
    }),
    "sigterm_registration_windows": ("span", "tools/server/server.cpp", {
        "start": r"auto console_ctrl_handler",
        "end": r"SetConsoleCtrlHandler",
    }),
    "signal_handler_body": ("block", "tools/server/server.cpp", {
        "start": r"static inline void signal_handler\(int signal\)",
    }),
    "shutdown_handler_declaration": ("span", "tools/server/server.cpp", {
        "start": r"static std::function<void\(int\)> shutdown_handler;",
        "end": r"static std::atomic_flag is_terminating",
    }),
    "shutdown_handler_assignment_single": ("span", "tools/server/server.cpp", {
        "start_after": r"routes\.update_meta\(ctx_server\);",
        "start": r"shutdown_handler = \[&\]\(int\) \{",
        "end": r"^\s*\};",
    }),
    "shutdown_handler_assignment_router": ("span", "tools/server/server.cpp", {
        "start_after": r"clean_up = \[&models_routes, &mcp_mgr\]",
        "start": r"shutdown_handler = \[&\]\(int\) \{",
        "end": r"^\s*\};",
    }),
    "llama_server_terminate": ("block", "tools/server/server.cpp", {
        "start": r"^void llama_server_terminate\(\) \{",
    }),
    "sigpipe_ignore": ("span", "tools/server/server.cpp", {
        "start": r"Ignore SIGPIPE so the server does not crash",
        "end": r"signal\(SIGPIPE, SIG_IGN\);",
    }),
    # --- graceful exit status (server.cpp) ---
    "main_return_after_shutdown": ("span", "tools/server/server.cpp", {
        "start": r"// this call blocks the main thread until queue_tasks\.terminate\(\) is called",
        "end": r"^    return 0;$",
    }),
    "entry_return_propagates_status": ("span", "tools/server/server.cpp", {
        "start": r"const int result = llama_server\(params, argc, argv, child\);",
        "end": r"return result;",
    }),
    "model_loading_error_exit": ("span", "tools/server/server.cpp", {
        "start": r"if \(!ctx_server\.load_model\(params\)\)",
        "end": r"return 1;",
        "start_after": r"// start the HTTP server before loading the model",
    }),
    "clean_up_single_instance": ("block", "tools/server/server.cpp", {
        "start_after": r"// setup clean up function, to be called before exit",
        "start": r"clean_up = \[&ctx_http, &ctx_server, &mcp_mgr\]",
    }),
    # --- /health route + handler ---
    "health_route_registration": ("span", "tools/server/server.cpp", {
        "start": r'ctx_http\.get \("/health"',
        "end": r'"/v1/health"',
    }),
    "health_handler_body": ("block", "tools/server/server-context.cpp", {
        "start": r"this->get_health = \[this\]\(const server_http_req &\)",
    }),
    "health_ready_body_literal": ("lines", "tools/server/server-context.cpp", {
        "match": r'res->ok\(\{\{"status", "ok"\}\}\);',
    }),
    "health_loading_middleware": ("block", "tools/server/server-http.cpp", {
        "start": r"auto middleware_server_state = \[this\]",
    }),
    "health_public_endpoints": ("span", "tools/server/server-http.cpp", {
        "start": r"static const std::unordered_set<std::string> get_public_endpoints",
        "end": r'"/v1/health",',
    }),
    "is_ready_set_after_model_load": ("span", "tools/server/server.cpp", {
        "start_after": r"routes\.update_meta\(ctx_server\);",
        "start": r"ctx_http\.is_ready\.store\(true\);",
        "end": r"ctx_http\.is_ready\.store\(true\);",
    }),
    # --- documented contract (README) ---
    "health_docs": ("span", "tools/server/README.md", {
        "start": r"### GET `/health`: Returns health check result",
        "end": r"the model is successfully loaded and the server is ready",
    }),
    # --- shutdown primitives ---
    "ctx_server_start_loop": ("block", "tools/server/server-context.cpp", {
        "start": r"^void server_context::start_loop\(\) \{",
    }),
    "ctx_server_terminate": ("block", "tools/server/server-context.cpp", {
        "start": r"^void server_context::terminate\(\) \{",
    }),
    "server_queue_terminate": ("block", "tools/server/server-queue.cpp", {
        "start": r"^void server_queue::terminate\(\) \{",
    }),
    "server_queue_process_new_tasks": ("block", "tools/server/server-queue.cpp", {
        "start": r"^bool server_queue::process_new_tasks\(bool is_yielding\)",
    }),
    "server_queue_start_loop": ("block", "tools/server/server-queue.cpp", {
        "start": r"^void server_queue::start_loop\(int64_t idle_sleep_ms\)",
    }),
    "server_queue_terminate_decl": ("lines", "tools/server/server-queue.h", {
        "match": r"void terminate\(\);",
    }),

    "gcp_health_route_remap": ("span", "tools/server/server-http.cpp", {
        "start": r"if \(!gcp\.path_health\.empty\(\)\)",
        "end": r"get\(gcp\.path_health, health_handler->second\);",
    }),
}


def fetch(path: str) -> bytes:
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "kama-shokunin-source-pins"})
    return urllib.request.urlopen(req, timeout=60).read()


def find_line(lines, rx, start_at=0):
    pat = re.compile(rx)
    for i in range(start_at, len(lines)):
        if pat.search(lines[i]):
            return i
    return None


def brace_match(lines, start_idx):
    """Return index of line containing the `}` that closes the first `{`
    found at/after start_idx. Brace counting ignores braces in // comments
    and string/char literals crudely but deterministically."""
    depth = 0
    opened = False
    for i in range(start_idx, len(lines)):
        code = re.sub(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'', "", lines[i])
        code = code.split("//")[0]
        for ch in code:
            if ch == "{":
                depth += 1
                opened = True
            elif ch == "}":
                depth -= 1
                if opened and depth == 0:
                    return i
    return None


def locate(kind, spec, lines):
    """Return (start_line_1based, end_line_1based) or None."""
    start_at = 0
    if "start_after" in spec:
        idx = find_line(lines, spec["start_after"])
        if idx is None:
            return None
        start_at = idx + 1
    if kind == "lines":
        pat = re.compile(spec["match"])
        hits = [i + 1 for i, l in enumerate(lines) if pat.search(l)]
        return hits or None
    n = spec.get("occurrence", 1)
    s = None
    for _ in range(n):
        s = find_line(lines, spec["start"], start_at)
        if s is None:
            return None
        start_at = s + 1
    if kind == "block":
        e = brace_match(lines, s)
    else:  # span
        e = find_line(lines, spec["end"], s)
    if e is None:
        return None
    return (s + 1, e + 1)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files_meta = {}
    contents = {}
    for path in FILES:
        data = fetch(path)
        dest = OUT_DIR / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        files_meta[path] = {
            "url": BASE + path,
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
            "saved_as": str(dest.relative_to(PINS_JSON.parent)),
        }
        contents[path] = data.decode("utf-8").splitlines()
        print(f"fetched {path}: {len(data)} bytes sha256={files_meta[path]['sha256'][:16]}…")

    pins = {}
    missing = []
    for name, (kind, path, spec) in PINS.items():
        lines = contents[path]
        res = locate(kind, spec, lines)
        if res is None:
            missing.append(name)
            continue
        if kind == "lines":
            ranges = [[n, n] for n in res]
            verbatim = "\n".join(lines[n - 1] for n in res)
        else:
            ranges = [[res[0], res[1]]]
            verbatim = "\n".join(lines[res[0] - 1:res[1]])
        pins[name] = {
            "file": path,
            "ranges": ranges,
            "locator": {"kind": kind, **spec},
            "verbatim": verbatim,
        }
        print(f"pinned  {name}: {path}:{ranges[0][0]}-{ranges[0][1] if ranges else '?'}")

    doc = {
        "commit": COMMIT,
        "base_url": BASE,
        "pinned_by": str(Path(__file__).name),
        "files": files_meta,
        "pins": pins,
    }
    if missing:
        doc["missing_pins"] = missing
    PINS_JSON.write_text(json.dumps(doc, indent=2) + "\n")
    print(f"wrote {PINS_JSON}")
    if missing:
        print(f"FAILED pins: {missing}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
