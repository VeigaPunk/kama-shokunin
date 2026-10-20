VERDICT: confirm — llama.cpp accepts duplicate flags with only a warning (last value wins), so "duplicate flag is INVALID" can only be enforced by the lane's own gate; and argv alone cannot pin the effective config (env and config.ini are applied first).

Seat: KamaR18.ScoutLlamaArgParse-2. Round start `e75cf680b53484a61709ee1b2787d8dbc6419f74`. All upstream citations are the pinned commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (llama.cpp b11755), fetched as raw files; `sha256(common/arg.cpp)=bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d`, 4833 lines. Installed runtime under test: `~/.local/bin/llama-server` (b11755).

Source URLs (each = `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/<path>`): `common/arg.cpp`, `common/common.cpp`, `common/common.h`, `common/preset.cpp`, `tools/server/server.cpp`.

## Findings (source)

**F1 — Duplicate known flags are NOT an error; last value wins.** `common/arg.cpp:832-837`: quote "DEPRECATED: argument '%s' specified multiple times, use comma-separated values instead (only last value will be used)". The `throw` above it fires only for unknown tokens (`arg.cpp:829-830`, quote "error: invalid argument: %s"). `--spec-type` is the sole warning exemption (`arg.cpp:833`, quote `const bool skip = (arg == "--spec-type");`). Consequence for C1: the server will happily run with `--port A --port B` (uses B) and `--host A --host B` (uses B, because the handler clears the vector: `arg.cpp:3337-3343`, quote "params.hostnames.clear();"). No server-side rejection exists to lean on.

**F2 — `--api-key` appends, it does not overwrite.** `arg.cpp:3533-3542`: quote "API key to use for authentication, multiple keys can be provided as a comma-separated list (default: none)", handler "params.api_keys.push_back(key);", env "LLAMA_API_KEY". So duplicate `--api-key` accumulates keys (no last-wins), and env + CLI accumulate together. The generic override warning printed for this option is therefore misleading: I observed both keys working simultaneously (see O3).

**F3 — Env vars are applied before CLI, with a warning; scalar CLI wins.** `arg.cpp:775` quote "config file applies first, so env variables and CLI arguments override it"; `arg.cpp:787-810` env loop. Env names: `--host`→`LLAMA_ARG_HOST` (`:3349`), `--port`→`LLAMA_ARG_PORT` (`:3356`), `--api-key`→`LLAMA_API_KEY` (`:3542`). Observed: `LLAMA_ARG_HOST=198.51.100.7 --host 203.0.113.9` prints "warn: LLAMA_ARG_HOST environment variable is set, but will be overwritten…" and binds 203.0.113.9 (O4).

**F4 — A config.ini is applied FIRST, before env and CLI, and can set any option by flag name.** `arg.cpp:723-724` quote "user-level: ${XDG_CONFIG_HOME:-~/.config}/llama.cpp/config.ini"; `arg.cpp:734` system path `/etc/llama.cpp/config.ini`; `arg.cpp:757` quote "using config file: %s". `common/common.cpp:1018-1021` resolves `XDG_CONFIG_HOME`, else `get_home_directory()/".config"`. `common/preset.cpp:251-263` maps keys by `rm_leading_dashes(arg)`, so the INI key for `--api-key` is literally `api-key`. Key ordering is: INI → env → CLI (`arg.cpp:775`).

**F5 — Config-injected `api-key` silently changes auth with unchanged argv (observed, decisive).** With `HOME=<tmp>` holding `.config/llama.cpp/config.ini` = `api-key = cfgkey`, and the producer's exact argv shape (`-m model --host 127.0.0.1 --port 9955 -c 256 --no-webui --offline`), the server logged "using config file: …" and `/v1/models` returned **401** unauthenticated. This is the live confound for C1: the frozen producer allowlists `HOME` into the child env (`tools/kama-llamacpp-live.py:82-84`, quote `CHILD_ENV_KEYS = ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')`) and does **not** set `XDG_CONFIG_HOME` (`:1103`). So the operator's real `~/.config/llama.cpp/config.ini` reaches the server child; the receipt records argv only (`:21-22`, quote "Only argv is recorded from the launch environment — never env"), so the gate cannot see it.

**F6 — A malformed config.ini exits 1 before any argument error.** `common/preset.cpp:228` quote "failed to parse server config file: "; observed exit 1 with that message and no `error: invalid argument` line (O6). Only `fs_get_config_directory()` is wrapped in try/catch (`arg.cpp:737-741`); `load_from_ini` is not.

**F7 — Unknown flag, `--flag=value`, abbreviation, and positional model are all rejected with exit 1.** `tools/server/server.cpp:113-115` quote "if (!common_params_parse(argc, argv, params, LLAMA_EXAMPLE_SERVER)) { return 1; }". Observed: `--bogus-flag`, `--port=9951`, `--por 9951`, `model.gguf` each print "error: invalid argument: …" and exit 1 (O1, O5). So the `=` form and prefixes are safe to treat as INVALID in the gate — the server agrees.

**F8 — `_` is normalised to `-` for every `--` token.** `arg.cpp:826-828`: quote `std::replace(arg.begin(), arg.end(), '_', '-');`. A token `--api_key` is therefore the *same flag* as `--api-key` at runtime. A gate that rejects unknown tokens conservatively is still correct (the producer never emits underscores), but must not claim `--api_key` is a distinct/unknown option in an evidence string.

**F9 — `--port` accepts trailing garbage.** `arg.cpp:859` quote "opt.handler_int(params, std::stoi(val));" (`std::stoi` stops at the first non-digit). Observed: `--port 12abc` parsed as port 12 and reached a bind attempt on port 12 (O2). Therefore a receipt field `port: 12` cannot be distinguished from argv `--port 12abc` by value comparison; only whole-token equality catches it.

**F10 — Presence of `--api-key` does not imply auth.** Empty/whitespace values are dropped (`arg.cpp:3536-3540`). Observed: `--api-key ''` → `/v1/models` 200 unauthenticated (O7).

**F11 — `/health` and `/v1/health` are public even with an api-key set.** `tools/server/server.cpp:278-279` quote "public endpoint (no API key check)". Also `:493` quote "start the HTTP server before loading the model to be able to serve /health requests" — the listener exists before the model loads, matching the observed bind-before-load ordering. Consequence: the readiness/teardown checks may not infer "no auth configured" from a 200 `/health`; and the port is bound while the model is still loading (relevant to the loading-503 window and to `port_listener_ownership`).

**F12 — The build's default port is 9931, not 8080.** `common/common.h:630` quote `int32_t port = 9931;`; default host `common.h:652` quote `std::vector<std::string> hostnames = {"127.0.0.1"};`. Observed bind attempt "hostname: 127.0.0.1, port: 9931" with no `--port` (O4). 9931 does not appear in `registry/endpoint-consumers.tsv` (grep: only rows for 8080 and 34113 match).

## The exploit this creates in the frozen gate (grounds C1's "extra/duplicate flag is INVALID")

`tests/llamacpp-live/check-receipt.py:169-176` returns the **first** match ("for i, a in enumerate(argv[:-1]):"), while llama.cpp uses the **last** value (F1). The validator checks only `argv[0]`, `-m`, `--alias`, `--host`, `--port`, `-c`, `-t` and the last two tokens (`:387-421`); it never scans for unknown or repeated flags. [INFERENCE] Therefore `[..., "--port", "<claimed>", ..., "--port", "9999"]` passes the gate while the server listens on 9999, and an inserted `--api-key X` passes the gate while auth turns on (F2/F10). This is exactly the forged-receipt control C1 plans; the fix must be a whole-list comparison plus a "each flag appears exactly once" rule, because the server itself provides no error to detect (F1).

Related, not duplicated here: `RevExactArgv.md` already derives the exact producer list and the `argv_flag` first-match hole from the lane side; this report supplies the upstream semantics (last-wins, no rejection) and the argv-invisible channels.

## Actionable for C1 (ordered by evidence strength)

1. Implement exact-argv as full-list equality against the known producer list (16 tokens), not per-flag lookups. This subsumes duplicates, extra flags, ordering, and the `--port 12abc` class (F9).
2. Add a check that no token starting with `-` repeats and that every flag token is in the producer's known set, so the failure message names the offending token. Do not rely on llama-server to error (F1).
3. Neutralise or record the config channel: set `XDG_CONFIG_HOME` to the harness temp dir in the child env (F4/F5), and additionally assert the captured startup log has no `using config file:` line (F5) — `/etc/llama.cpp/config.ini` remains possible and only the log reveals it. Record the path if present and fail closed (not-evaluated), never pass.
4. Keep `LLAMA_ARG_*`/`LLAMA_API_KEY` out of the child env (already true by allowlist); the gate's `child_env_keys` allowlist (`check-receipt.py:371-384`) already enforces the names side (F3). Do not add `--api-key` to the producer argv; if a control ever adds it, require a non-empty value (F10).
5. Do not use `/health` 200 as evidence that auth is unconfigured (F11); use `/v1/models` unauthenticated, which is where the 401 appeared.
6. Candidate mutants for C1's self-checks that survive today: append `--api-key mutated` and append a second `--port <other>` to `server_argv`; both are accepted by the server (warning only) and both slip past `argv_flag`. The only detector is the gate.

## Sourced (candidate SOURCES rows for C1, S048+)

- `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp` — `:830`, `:836`, `:3337-3343`, `:3533-3542`, `:775`, `:757`, `:859`, `:827`.
- `.../common/common.cpp` — `:1018-1021` (XDG/HOME config dir).
- `.../common/common.h` — `:630` (default port 9931), `:652` (default host).
- `.../common/preset.cpp` — `:251-263` (key = flag name sans dashes), `:228` (malformed INI fatal).
- `.../tools/server/server.cpp` — `:113-115` (exit 1 on parse failure), `:278-279` (public health), `:493` (listen before model load).
- Local observations O1–O7 below (commands reproducible on this host, fixture model, loopback only).

## Limitations / unresolved

- Every runtime observation is from the installed b11755 binary; I read source at the same commit, so source and binary agree on the paths exercised, but I did not rebuild.
- Whether the operator's real `~/.config/llama.cpp/config.ini` exists on this host is **unverified** (privacy bounds forbid reading `~/.config`). The *mechanism* is proven with a temp `HOME`; its presence on this host is [INFERENCE]-unknown and must be probed by the tool at runtime, not by a seat.
- I did not run the lane gate or any measurement script (L1 owns those). The duplicate-flag exploit is [INFERENCE] from `check-receipt.py:169-176,387-421` plus F1; it should be demonstrated by the C1 forged-receipt control, not by this seat.
- `--host` with an IPv6 literal parses through `parse_csv_row` (comma-split) and therefore survives argv parsing; whether `::ffff:127.0.0.1` binds and how it appears in `/proc/net/tcp6` is another seat's question (see `ScoutProcNetTcpDoc.md`, `ScoutRfc4291Mapped.md`).

## Observations (commands abbreviated; ports 9951/9952/9955/12, all torn down, `ss -ltnp` clean)

- O1 `llama-server --bogus-flag` → "error: invalid argument: --bogus-flag", EXIT=1.
- O2 `llama-server --port 12abc -m <nonexistent>` → "couldn't bind HTTP server socket, hostname: 127.0.0.1, port: 12" (accepted 12), EXIT=1.
- O3 `LLAMA_API_KEY=envkey llama-server … --api-key cli-key` on 127.0.0.1:9951 — `/v1/models`: Bearer cli-key 200, Bearer envkey 200, Bearer nope 401; `/health` with no header 200 (public, F11). Both keys valid at once.
- O3b same run: warning "LLAMA_API_KEY environment variable is set, but will be overwritten by command line argument --api-key" while envkey still authenticated.
- O4 `LLAMA_ARG_HOST=198.51.100.7 llama-server --host 203.0.113.9` → warning, bind attempted on 203.0.113.9; with no `--port`, "port: 9931".
- O5 `--port=9951`, `--por 9951`, positional `model.gguf` → each "error: invalid argument: …", EXIT=1.
- O6 malformed `config.ini` → "using config file: …" then "failed to parse server config file: …", EXIT=1.
- O7 `--api-key ''` with valid model on 127.0.0.1:9952 → `/v1/models` 200 with no auth and 200 with a bogus Bearer (auth off).
- O8 `--host A --host B` → DEPRECATED warning; bind attempted only on B (203.0.113.9).

## Installs

None. No pacman/uv/npx/cargo invocations; only `curl` fetches of pinned raw sources into `/tmp/kama-r18-ScoutLlamaArgParse` (removed) and short-lived loopback `llama-server` runs, all confirmed gone with `pgrep -af llama-server` (empty) and `ss -ltnp` (no 9951/9952/9955).
