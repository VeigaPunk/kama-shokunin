# SentinelLiveSafety: C2 live-harness safety audit (round 16, build wave)

Seat: sentinel, read-only. These findings are advice, not a verdict. Date: 2026-10-20.

**Scope note.** `tools/kama-llamacpp-live.py` was **absent** at both checks during this seat (glob of `kama-shokunin/tools/kama-*` found only `kama-ollama-evidence.py` and `kama-probe.sh`; a recheck just before writing also found nothing). So this report audits the **design**: the context C2 bullet plus the LiveHarness item prompt in `.ufo/waves/round-16/build/spec.json` (item `LiveHarness`, line 57-59). I checked it against the shipped b11755 sources and the installed artifacts. Implementation line numbers can't be cited yet. Each item names the design clause it attacks. L1 should re-run this checklist against the file once it lands.

Sources fetched this session (2026-10-20): `https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/{common/arg.cpp, tools/server/server.cpp, vendor/cpp-httplib/httplib.cpp}`. I deleted the scratch copies under `/tmp/sls-*` after use; no other writes.

---

## Findings (highest severity first)

### F1: HIGH. Inherited environment can reconfigure llama-server and override "loopback-only / offline / no writes"
- **Design clause.** "record argv only (never env)". The spec never says to *scrub* the child's environment, so the default `Popen` inherits the full environment.
- **Evidence (arg.cpp @ b11755).**
  - `:787` `// handle environment variables` runs before `// handle command line arguments`. Every `set_env(...)` option is applied from the environment first, and argv overrides only the options argv names.
  - `LLAMA_ARG_CONNECT` (`:3497-3502`): "(experimental) open a peer-to-peer tunnel for server using llama-connect". This is an **off-host exposure** that `--host 127.0.0.1` does not cover.
  - `LLAMA_ARG_TOOLS` (`:3437-3445`): "available tools: read_file, ... exec_shell_command, write_file, edit_file". Shell-exec over the loopback HTTP endpoint.
  - `LLAMA_ARG_MCP_SERVERS_JSON` / `LLAMA_ARG_MCP_SERVERS_CONFIG` (`:3464`, `:3472`). server.cpp `:379` `mcp_mgr.start(params);` spawns MCP servers.
  - `LLAMA_ARG_TOOLS_RUNTIME` (`:3456`): "'ssh:<target>': run tools on a remote POSIX host over SSH".
  - `LLAMA_ARG_MODEL_URL` / `LLAMA_ARG_HF_REPO` / `HF_TOKEN` (`:3063`, `:3082`, `:3096`) cause network download. server.cpp `:427-429` `common_models_handler_apply(models_handler, params);` runs in single-model mode.
  - `LLAMA_ARG_LOG_FILE` (`:3921-3926`): "Log to file". Arbitrary file write, possibly under ~/.config.
  - `LLAMA_ARG_SLOT_SAVE_PATH` (`:3667`) is a file-write surface.
  - `LLAMA_API_KEY` (`:3533-3542`): "API key to use for authentication". Turns the probe result into UNAUTHORIZED, so `probe_model_ok` fails for a reason outside the C2 claim.
  - `LLAMA_ARG_ENDPOINT_METRICS` (`:3633-3638`) "enable prometheus compatible metrics endpoint" flips `metrics_not_enabled` to failing.
  - `LLAMA_ARG_N_PARALLEL` (`:2556`) changes `/slots` count.
- **Exploit path.** Any of these variables in the launching shell, from the operator's profile or a sibling tool, silently re-shapes the "ephemeral, lane-owned, loopback" server. `LLAMA_ARG_CONNECT=1` or `LLAMA_ARG_TOOLS=all` turns it into a remote or shell-exec surface for the run's lifetime. The receipt records argv only, so it would still claim `--host 127.0.0.1` and could never show this.
- **Smallest remediation.**
  - Launch with an explicit allow-list environment: `env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}`, with no HOME, LD_*, LLAMA_*, HF_*, GGML_* or *_proxy.
  - Add `--offline` to argv. It is a COMMON option: arg.cpp `:3973-3977` "Offline mode: forces use of cache, prevents network access".
  - Record in the receipt the **names** of the allowed variables (never values), e.g. `"child_env_keys": ["LANG","PATH"]`.
  - Apply the same allow-list to the probe subprocesses.
  - [INFERENCE] Negative argv forms (`--no-connect`, `--no-ui`) are belt-and-braces only. Scrubbing is the primary control.

### F2: HIGH. The server sha256 pins a 17 KB launcher; the real code is unpinned and can be redirected by the environment
- **Design clause.** "--server PATH ... record realpath and sha256 of that file".
- **Evidence.**
  - `ls -la`: `/home/vgpnk/.local/opt/llama-b11755/llama-server` is "17864" bytes.
  - `readelf -d`: "NEEDED ... [libllama-server-impl.so]", "(RUNPATH) Library runpath: [$ORIGIN]".
  - The install dir holds `libllama-server-impl.so` (7671544 B), `libllama.so.0.7.0`, `libllama-common.so.0.7.0`, `libggml-base.so.0.27.0` and 15 dynamically selected `libggml-cpu-*.so` variants.
  - A DT_RUNPATH is searched *after* `LD_LIBRARY_PATH` (ld.so(8) search order) [source-of-record: ld.so(8), not re-opened this session; mark INFERENCE].
- **Impact.** The receipt's "server identity" digest doesn't identify the code that served the requests. An inherited `LD_LIBRARY_PATH` or `LD_PRELOAD` substitutes it while the digest stays green. That is a provenance defect: the identity recorded is not the identity that ran.
- **Smallest remediation.**
  - F1's env scrub removes LD_* redirection.
  - Record `server_libs`: sha256 of every regular `*.so*` file in `dirname(realpath(server))`, sorted, plus a combined digest.
  - Keep the `load_backend` / "loaded CPU backend" log line by adding `load_backend` to the copied-log regex. That records which `libggml-cpu-*.so` variant actually loaded.

### F3: HIGH. SO_REUSEPORT plus a probe-then-close free-port pick means the harness can capture a *different* server and still pass
- **Design clause.** "bind 127.0.0.1:0 for a free port; refuse and retry ..." then launch with `--port P`.
- **Evidence.**
  - cpp-httplib @ b11755 (`vendor/cpp-httplib/httplib.cpp:6613-6620`): `default_socket_options` sets "SO_REUSEPORT, ... 1" on Linux.
  - The Python probe socket is closed before launch, so this is a TOCTOU window.
  - Sibling seats (LiveHarness dev runs, L1 measurements) launch the same binary under the same UID.
- **Exploit or failure path.** Two same-UID llama-servers both setting SO_REUSEPORT can both bind 127.0.0.1:P [INFERENCE: Linux SO_REUSEPORT same-euid rule]. The kernel then load-balances connections across them, so lifecycle and probe captures can come from the other process.
- **Second path.** If our child dies on EADDRINUSE, a loop that polls only HTTP will read whatever else answers on P until ready-timeout.
- **Either way.** The receipt attributes a foreign server's `/v1/models` to the pinned model and binary.
- **Smallest remediation.**
  1. Before launch, refuse P if `ss -ltnH "sport = :P"` shows any listener on any address.
  2. In the lifecycle loop, `child.poll()` every iteration. If it is not None, raise a setup error (exit 2) and never accept HTTP from P afterwards.
  3. After ready, prove ownership. Exactly one LISTEN socket for P, and its socket inode (`/proc/net/tcp` local `0100007F:%04X` state `0A`) must appear among `/proc/<child.pid>/fd` links. Record this as a check `listener_owned_by_child`, plus `listener_bound_loopback_only` (no `0.0.0.0`/`::` row for P).
  4. Re-verify ownership immediately after the probe runs.

### F4: MEDIUM. Teardown is not guaranteed on every exit path
- **Design clause.** "Always tear down (try/finally, signal handlers)"; "SIGTERM process group, wait 10s, SIGKILL fallback".
- **Gaps** [INFERENCE from Python/Linux semantics; the file is absent]:
  1. **Harness SIGKILL / OOM-kill.** No handler runs, and with `start_new_session=True` the child is in its own session, so terminal hangup won't reach it either. Result: an orphaned 127.0.0.1:P listener. Remediation: `preexec_fn` calling `ctypes.CDLL(None).prctl(1, signal.SIGKILL)` (PR_SET_PDEATHSIG; ctypes is stdlib), then `os.getppid()` == expected-parent recheck. Popen must be called from the main thread, because PDEATHSIG fires on the *forking thread's* exit.
  2. **Signal before the `try`.** If Popen runs before the handlers are installed or outside the `try`, a SIGTERM in that window leaks the child. Install the SIGTERM/SIGHUP/SIGINT handlers (raise a custom exception) **before** Popen, and put Popen inside the `try`.
  3. **Re-entrant signal during `finally`.** A second SIGTERM raises inside the teardown and aborts it midway. At teardown entry, call `signal.pthread_sigmask(SIG_BLOCK, {SIGTERM, SIGINT, SIGHUP})`, or set handlers to `SIG_IGN`.
  4. **PGID reuse.** After `child.wait()` reaps the leader, the SIGKILL fallback `os.killpg(pgid, SIGKILL)` can target a recycled PGID if no members remain. Observe exit with `os.waitid(P_PID, pid, WEXITED|WNOWAIT)`, `killpg` while the zombie still pins the PGID, then reap.
  5. **No group-empty proof.** `teardown_exited` (child returncode) does not prove that MCP/tools subprocesses (server.cpp `:379`) or router children are gone. Add a check `teardown_group_empty`: `os.killpg(pgid, 0)` raises `ProcessLookupError` after reap.
- **Mitigating fact.** server.cpp registers its SIGTERM handler only after load (`:529-534` `sigaction(SIGTERM, &sigint_action, NULL);` follows `load_model` at `:507`). So a SIGTERM during the loading phase takes the default terminate action. Teardown during load is reliable, and the 10 s SIGKILL fallback covers a hung `ctx_server.terminate()`.

### F5: MEDIUM. The registered-port refusal set is the registry's *claim*, not the effective endpoints
- **Design clause.** "refuse ... 8080, 34113 or any port number appearing in registry/endpoint-consumers.tsv".
- **Evidence.**
  - `registry/endpoint-consumers.tsv:35` says the omp row is a "code-level fallback pin, not proof of the effective environment-selected URL".
  - The header at `:17-18`: "declared_baseurl is the registry's claim, never the source of truth".
  - `registry/history/latest.tsv:2-4` ports are `8080`, `34113`, `34113`.
  - `/proc/sys/net/ipv4/ip_local_port_range` = "32768 60999". **34113 is inside the ephemeral range**, so `bind(:0)` can return it and the refusal path is live, not hypothetical. 8080 is outside it.
- **Gaps.** "any port number appearing" is ambiguous. A naive `\d+` over the whole file also refuses `6901` (from `RFC6901`, line 19), `30`, `6` and similar. That is harmless over-refusal, but it is undocumented and only accidentally correct. Ports resolved from the consumer files (the source of truth) are not included.
- **Smallest remediation.**
  - Define the set as the union of {8080, 34113}, every `:NNNN` port in the declared_baseurl column of non-comment rows, the `port` column of `registry/history/latest.tsv`, and every currently listening TCP port (`ss -ltnH`).
  - Record the refusal set and the retry count in the receipt.
  - Bound the retries (e.g. 32) and exit 2 when exhausted.
  - Re-check the final P against the set *after* the server is ready. This guards against code that re-picks the port.

### F6: MEDIUM. urllib "no proxy" must be explicit, or loopback captures route through an inherited proxy
- **Design clause.** "urllib, 0.5s timeout, no proxy".
- **Evidence.** `urllib.request.urlopen` installs a default `ProxyHandler` that reads `<scheme>_proxy` from the environment (https://docs.python.org/3/library/urllib.request.html, "ProxyHandler ... By default, it reads the list of proxies from the environment variables `<protocol>_proxy`"). Unless `no_proxy` lists 127.0.0.1/localhost, the loopback request goes to the proxy [INFERENCE: CPython `proxy_bypass_environment`].
- The probe is already safe: `kama-probe.sh:290` and `:322` pass `curl -sS --noproxy '*'`.
- **Smallest remediation.** Use `urllib.request.build_opener(urllib.request.ProxyHandler({}))` for every capture, and never call module-level `urlopen`. Also disable redirects with a no-op `HTTPRedirectHandler` subclass, so a 3xx can't move the request off loopback.

### F7: LOW. Model digest gate has a check-then-use window and no post-run confirmation
- **Design clause.** "--model-sha256 ... mismatch -> exit 3 before launch".
- **Gap.** The file is hashed by path, and the server re-opens the same path later. A same-UID writer could swap it between the two. Pinned file: `~/.cache/kama-shokunin/models/stories260K.gguf`, 1185376 B, mode `-rw-r--r--`.
- **Smallest remediation.**
  - Refuse a symlinked `--model`, or record its realpath.
  - Re-hash after teardown and record `model_sha256_post`. Teardown fails if it differs from the pre-launch hash.
  - Alternatively, hash an opened fd and pass `/proc/self/fd/N` with `pass_fds`.
  - Hash in streaming mode (`hashlib.file_digest`).

### F8: LOW. Temp-log handling and receipt write
- **Design clause.** "stdout+stderr to a temp file ... delete temp log after copying only lines matching build|model loaded|listening|loading".
- **Gaps.**
  - The temp log survives a harness SIGKILL; `/tmp` is the default `tempfile` location.
  - The filter keeps lines carrying absolute home paths (llama.cpp logs the model path while loading). The receipt is likely tracked in the lane repo, so this leaks host username and layout (low).
  - `--out` could follow a planted symlink. Precedent: the probe refuses symlinked history outputs, "symlink refusal before mkdir -p: a planted link would aim the writes outside the lane's repo" (`kama-probe.sh`, snapshot section).
- **Smallest remediation.**
  - Use `tempfile.mkstemp(prefix='kama-llamacpp-live.')` (0600) and `os.unlink` in the same `finally` that does teardown.
  - Or pipe stdout/stderr through `subprocess.PIPE` into a bounded in-memory ring with a reader thread, so no file exists at all.
  - Rewrite `$HOME` to `~` in the copied lines.
  - Refuse `--out` when `os.path.islink` is true or when it resolves under `~/.config`, `~/.omp` or `/etc/systemd`, then write via tmp + `os.replace` in the same directory.

### F9: LOW. Captures could carry secrets or prompt data if the subset rule slips
- **Design clause** (good as written): `/props` keeps only `model_alias, total_slots, is_sleeping, build_info, default_generation_settings.n_ctx`, and `/slots` keeps only status plus element count.
- **Risk if implemented loosely.** Full `/props` includes model path and chat template; full `/slots` includes prompt/cache state [INFERENCE].
- **Remediation.** Keep the exact allow-list. Store `/v1/models` in full (no secret fields expected). For headers, keep only Server and Content-Type. Never store request headers.

### F10: LOW. Probe subprocess is unbounded
- **Gap.** `bash PROBE check --port P ...` has no stated subprocess timeout. A hung probe keeps the server alive until an external signal arrives.
- **Remediation.**
  - Pass `--timeout 2 --connect-timeout 1` (the matrix contract values), apply `subprocess.run(..., timeout=60)`, and use the F1 env allow-list.
  - Set `KAMA_PROBE_TMPDIR` explicitly to the system tmp. The probe honours it at `kama-probe.sh:1123`: `mktemp -d "${KAMA_PROBE_TMPDIR:-/tmp}/kama-probe.XXXXXX"`.
  - The probe cleans that dir up through `trap cleanup EXIT INT TERM` (`:89`).

---

## Items checked and found adequate in the design
- **Loopback bind.** `--host 127.0.0.1` is in argv, and argv overrides the `LLAMA_ARG_HOST` env (arg.cpp `:3349`). Adequate once F1 removes the other exposure variables.
- **Router-mode subprocess spawning** is avoided because `-m` is set. server.cpp `:152`: "is_router_server = params.model.path.empty() && params.model.hf_repo.empty()". This holds only if F1 removes `LLAMA_ARG_HF_REPO`.
- **No ~/.config, ~/.omp or systemd writes** are needed by llama-server in single-model mode with a local `-m`. The write surfaces are the env-driven ones in F1 (`LOG_FILE`, `SLOT_SAVE_PATH`, model download cache) [INFERENCE: no other write path inspected].
- **Probe `check --port`** uses a removed mktemp dir only. It does not touch `registry/history` (snapshot refuses `--port`), and it uses `--noproxy '*'`.

## Recommended additional receipt checks (for LiveReceiptGate parity)
`listener_owned_by_child`, `listener_bound_loopback_only`, `teardown_group_empty`, `model_sha256_post_equal`, `port_not_in_refusal_set` (with the set recorded), and `child_env_keys` ⊆ {PATH, LANG}.

## Limitations
- The implementation was absent, so every finding targets the spec and design. Implementation line numbers are not available.
- The Linux SO_REUSEPORT same-euid semantics, ld.so RUNPATH ordering and CPython proxy-bypass internals are cited from knowledge, marked [INFERENCE] where no document was opened.
- I did not inspect the operator's actual environment for LLAMA_*/LD_*/proxy variables, by contract ("Never dump environment variables"). F1 and F2 are therefore conditional exposures, not observed ones.
- `kama-probe.sh` was being edited concurrently: its line numbers shifted during this seat, so cited probe lines are as read at 2026-10-20.

## Installs
None.
