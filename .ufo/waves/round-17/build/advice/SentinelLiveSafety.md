VERDICT: partial — current tool keeps loopback/port-refusal/env safety, but the C2 plan has 3 high-severity cleanup/measurement gaps (frozen-path fail-closed, fake in foreign session, K6 in-process).

Seat: KamaR17.SentinelLiveSafety-2 (sentinel, read-only). Audited at lane tip `cff9e62`.
- Target state when audited: `tools/kama-llamacpp-live.py` is byte-identical to the frozen copy (`cmp` clean, sha256 `b8c5e8d4…4fe4`), i.e. **v2 not yet landed**.
- `tests/llamacpp-live/controls.py` **does not exist yet**.
- So the findings below cover the frozen/current v1 code and the C2 plan text (`.ufo/waves/round-17/build/spec.json` items C2LiveTool, C2Controls, C2ReceiptGate).
- Re-audit is needed once v2 and controls.py land.

All line numbers are `tools/kama-llamacpp-live.py` unless named otherwise.

## Findings (severity, exploit path, evidence, impact, smallest remediation)

### F1 HIGH — the frozen tool fails closed before launch when run where it sits, so the C2 "before" count is wrong
- **Exploit path:** run `controls.py --tool .ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py`, as the C2Controls item allows. The tool works out the lane root from its own path.
- **Evidence:**
  - `:51-53` "SCRIPT = Path(__file__).resolve() / LANE = SCRIPT.parent.parent / REGISTRY = LANE / 'registry' / 'endpoint-consumers.tsv'".
  - `:197-200` "except OSError: raise SetupError(f'registry-unreadable:{REGISTRY}')".
  - `:811-815` maps that to exit 2 before `Popen`.
  - Resolved path checked with `Path.resolve()`: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/registry/endpoint-consumers.tsv` → `False`. `DEFAULT_PROBE` → `.ufo/waves/round-17/tools/kama-probe.sh` → `False`.
- **Impact:** the safety side is fine, because a missing registry can never silently drop the refusal check. The counting side breaks:
  - Every control, K0 included, exits 2 with no server launched.
  - The "before" result becomes `accepted_bad 0, good_ok false`, which looks like a frozen tool that rejected every bad shape. The before→after delta for C2 is fake.
  - The same applies to ProbeSigtermFake's independent reproduction.
  - [INFERENCE: not executed — read-only seat. The conclusion follows from static path resolution.]
- **Smallest fix (controls.py):** copy the tool under test into a scratch lane layout: `<tmp>/tools/<tool>.py` plus `<tmp>/registry/endpoint-consumers.tsv` copied from the lane. Always pass `--probe` explicitly. Then assert in the JSON that `port_refusal_set ⊇ {8080, 34113}`.
- Both peers were messaged.

### F2 HIGH — the fake server runs in the tool's new session, so controls.py's "kill leftover fakes (process group)" cannot reach it
- **Exploit path:**
  - controls.py starts the tool, and the tool starts the fake with `start_new_session=True`.
  - The fake's pgid equals its own pid. That is neither the tool's group nor controls.py's group.
  - If the tool dies or skips teardown (K6 patched teardown, a controls timeout, the F7 window), `os.killpg(<tool pgid>)` in controls misses the fake.
- **Evidence:**
  - `:904` "start_new_session=True,".
  - `:666` "os.killpg(proc.pid, signal.SIGTERM)" is the only kill, and it lives inside `teardown()`.
  - C2Controls plan: "always kill leftover fakes (process group)".
- **Impact:** an orphaned fake keeps listening on 127.0.0.1:<ephemeral> after a control crashes. The only backstop is `PR_SET_PDEATHSIG` (`:303`), and it fires only when the fake's *direct parent* exits. That parent is the tool, or controls.py itself for in-process K6.
- **Smallest fix:**
  - The fake writes `os.getpid()` to `<tmpdir>/fake-<id>.pid` at startup.
  - After each control, and in a top-level `try/finally` plus a SIGTERM/SIGINT→exception handler, controls.py SIGKILLs that pgid. Do this only if `/proc/<pid>/cmdline` still names the fake path, which guards against PID reuse.
  - Finish with `ss -ltnp`/`/proc` confirmation in its own JSON.
  - Optionally: v2 records `child_pid` in the receipt.

### F3 HIGH — K6 run inside controls.py's own process leaves controls deaf to signals, leaks the fake, and leaks the temp log
- **Exploit path:** the C2Controls plan says "run the tool in-process via runpy/importlib with its teardown function monkeypatched to raise RuntimeError". With the frozen (or any v1) tool:
  - `teardown` raises → `:1021` stores `{'error': …}`.
  - `:1026` "receipt['teardown']['returncode'] is not None" raises KeyError inside the `finally`.
  - `main()` escapes before `:1069-1071` "for sig, handler in old_handlers.items(): signal.signal(sig, handler)".
- **Evidence:**
  - `:1014-1015` "for sig in old_handlers: signal.signal(sig, signal.SIG_IGN)".
  - The escape is already corroborated by round-16 `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md:34` "ESCAPED KeyError KeyError('returncode')".
- **Impact:**
  1. controls.py ignores SIGINT, SIGTERM and SIGHUP for the rest of its run, so L1 cannot Ctrl-C or terminate it cleanly.
  2. The patched teardown never runs `killpg`, so the fake survives holding its port until controls.py exits. Its PDEATHSIG parent is controls.py.
  3. The temp log `$TMPDIR/kama-llamacpp-live-*.log` is never unlinked: `:707-708` sits inside the patched `teardown`.
  4. [INFERENCE] If controls.py uses threads, `preexec_fn` (`:905`) after fork is not thread-safe according to the Python subprocess docs.
- **Smallest fix:** run K6 in a child `python3 -c '<importlib load tool; patch teardown; sys.exit(main(argv))>'`. The tool is still "in-process" relative to its own patched module.
  - That process's exit fires PDEATHSIG on the fake.
  - Signal-handler damage stays in the throwaway process.
  - Give it `TMPDIR=<controls tmpdir>`. Apply F2's pidfile kill as well.

### F4 MEDIUM — the v2 "receipt always written on internal faults" contract does not require the child to be killed on that path
- **Plan text (C2LiveTool):** "any exception in teardown/finally still writes a receipt with `setup_error` `internal:<ExcType>` and exit 2". It says nothing about process reaping, restoring signal handlers, or cleaning up the log.
- **Evidence:** today the only kill is inside `teardown()` (`:662-681`), and the log unlink is too (`:707-708`). Handler restore only happens after the emit (`:1069-1071`).
- **Impact:** a v2 that only wraps `teardown()` in `try/except → receipt` would turn a fault before `killpg` into a "clean" exit 2 receipt while the server is still running. That is fabricated readiness for teardown.
- **Smallest fix (C2LiveTool):**
  - Backstop in a `finally`: `if proc is not None and proc.poll() is None: os.killpg(proc.pid, SIGKILL); proc.wait(5)`. `poll() is None` means the child is unreaped, so the pid/pgid stays reserved and there is no PID-reuse kill.
  - Put the log `os.unlink(log_path)` in its own `finally`.
  - Restore handlers in an outer `finally` that encloses the emit.
  - Peer messaged.

### F5 MEDIUM — "loopback-only" is asserted from argv, never proven from the listening socket
- **Exploit path:** a llama-server build, a wrapper, or a controls fake ignores `--host 127.0.0.1` and binds `0.0.0.0:<port>`, exposing the model API to the LAN for the length of the run. Every ownership check still passes.
- **Evidence:**
  - `:268` "if int(parts[1].rsplit(':', 1)[1], 16) == port:" — the local address field of `/proc/net/tcp` is ignored.
  - `:863` "'--host', '127.0.0.1'," is only the request.
  - The gate checks only the claim: `tests/llamacpp-live/check-receipt.py:372` "if argv_flag(argv, "--host") != "127.0.0.1":".
- **Impact:** the bind address the receipt claims is not backed by evidence, and a non-loopback bind cannot fail the run.
- **Smallest fix:** in `_listen_inodes`/`port_owned_by`, record the local addresses of the child-owned LISTEN sockets. Treat any address other than `0100007F` (or the `::1` form in tcp6) as `port-listener-not-loopback` → setup error. Store `listen_addrs` in the receipt so the gate can re-derive it. The C2Controls fake must hard-bind `127.0.0.1` regardless of argv.

### F6 LOW-MEDIUM — `install_tree` hashes and names every regular file next to `--server`
- **Exploit path:** a control or probe seat puts the fake directly in `/tmp` (for example `/tmp/fake.py`). `install_tree` then opens and hashes every readable regular file in `/tmp` and writes their basenames into `server.install_tree` in the receipt.
- **Evidence:** `:151-153` "directory = os.path.dirname(server_real) … entries = sorted(os.listdir(directory))"; `:165` "tree[name] = sha256_file(full)".
- **Impact:** the receipt leaks other agents' or sessions' temp filenames and their content digests, and reads files outside the run's scope.
- **Smallest fix:**
  - controls.py / probe seats: put the fake in a dedicated subdirectory of the TemporaryDirectory.
  - Tool, optional: skip `install_tree` when `server_real`'s directory is world-writable (`S_ISVTX`/`/tmp`), or cap the entry count.
  - ProbeSigtermFake was messaged.

### F7 LOW — a signal during `Popen` can orphan the server until the harness exits
- **Exploit path:** `_term_handler` is installed at `:886-887` before `Popen` at `:909`. Popen's parent side blocks on the exec-status pipe after fork (`/usr/lib/python3.14/subprocess.py:1943` "part = os.read(errpipe_read, 50000)"), and the child's `preexec_fn` imports `ctypes` first (`:301`), which widens the window.
- **Impact:** a SIGTERM delivered there raises `Terminated` before `proc` is assigned. Teardown then runs `teardown(None, …)` (`:1019`) and skips `killpg`, so the server keeps running until the harness exits and PDEATHSIG fires. If the tool runs in-process inside a long-lived parent (F3), the orphan lives as long as that parent.
- **Smallest fix:** block SIGINT/SIGTERM/SIGHUP with `signal.pthread_sigmask(SIG_BLOCK, …)` around `Popen`, then unblock once `proc` is assigned.

### F8 LOW — a probe timeout or a signal SIGKILLs the bash probe, which skips its temp cleanup
- **Evidence:**
  - `:628-629` `subprocess.run(..., timeout=PROBE_TIMEOUT, env=child_env)`.
  - On timeout or exception, `run()` calls `process.kill()` (`/usr/lib/python3.14/subprocess.py:559` and `:573`).
  - The probe cleans up only through a trap: `tools/kama-probe.sh:93` "trap cleanup EXIT INT TERM", which SIGKILL bypasses.
- **Impact:** `/tmp/kama-probe.XXXXXX` leaks (`kama-probe.sh:1128`). A `curl` grandchild may outlive the probe, bounded by `--max-time 2`.
- **Smallest fix:** run the probe with `start_new_session=True` under `Popen`. On timeout, send SIGTERM to its group first, so the trap runs, then SIGKILL after about 2 s.

### F9 LOW — the probe's `curl` reads `$HOME/.curlrc`, because HOME is in the child env allowlist
- **Evidence:**
  - `:73` "CHILD_ENV_KEYS = ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')", which `run_probe` passes as-is (`:629`).
  - `tools/kama-probe.sh:294` "curl -sS --noproxy '*' --connect-timeout …" has no `-q`.
- **Impact [INFERENCE]:** `--noproxy '*'` neutralises proxies, but a `.curlrc` `connect-to`/`resolve` line could still steer the probe's "127.0.0.1" request elsewhere. Probe traffic would then leave loopback while the receipt records it as loopback evidence. In `check --port` mode, HOME only feeds `$UFO_SRC` defaults, which are unused there.
- **Smallest fix:** drop HOME from the probe's env only (keep it for the server), or have the probe pass `curl -q` as the first argument (lane probe change, out of C2 scope).

### F10 LOW — exception text and env-selected paths reach the receipt
- **Evidence:**
  - `:1021` "receipt['teardown'] = {'error': f'{type(exc).__name__}: {exc}'}".
  - `:894` "SetupError(f'log-mkstemp-failed:{exc}')".
  - `:891` `tempfile.mkstemp(...)` honours `$TMPDIR`. Its path is recorded as `teardown.log_path` (`:661`) and the server writes its log there.
- **Impact:** small path or message disclosure. "Writes only under /tmp + the receipt path" holds only while `$TMPDIR` is unset or points under `/tmp`. No env *values* are recorded: `:876` records names only, and the gate enforces the allowlist at `check-receipt.py:340-353`.
- **Smallest fix:** v2 `internal:<ExcType>` with no `str(exc)`, as the plan already asks. Optionally pass `dir='/tmp'` to the log `mkstemp`, or record that the location is selected by `TMPDIR`.

### F11 LOW — the gate checks only the two hard pins in `port_refusal_set`, not the ports the registry declares
- **Evidence:** `tests/llamacpp-live/check-receipt.py:223-225` "for pin in HARD_PINS: if pin not in refusal: bad(…)".
- **Impact:** a tool regression that drops the registry-parsed ports still validates. There is no live exposure today: the registry rows declare only 8080 and 34113 (`registry/endpoint-consumers.tsv` rows `omp-llama-cpp-default`, `ufo-fsd-thetick`, `ufo-fsd-local-helper`).
- **Smallest fix (C2ReceiptGate, optional):** recompute the expected refusal set from the lane registry when it is readable and require it to be a subset of the receipt's set.

### F12 PLAN — the controls timeout budget must cover the worst-case teardown, or receipts are lost and fakes orphaned
- **Evidence:**
  - `:62` "PROBE_TIMEOUT = 60" (×2 probes).
  - `:63` "TERM_GRACE = 10.0", plus a 5 s wait after SIGKILL (`:679`).
  - K4 (ignores SIGTERM) needs ≥10 s of teardown by design.
- **Impact:** a per-control `subprocess.run(timeout=…)` shorter than about `ready_timeout + 120 + 15` s SIGKILLs the tool (`subprocess.py:559`). No receipt is written, so the control is misclassified, and the K4 fake survives unless PDEATHSIG landed: `:912` records `prctl_ok 'unknown'`.
- **Smallest fix:** a per-control timeout of at least 180 s, plus F2's pidfile kill on timeout.

## Properties verified as kept (v2 must preserve them)
- **Loopback request path:**
  - Port pick binds `127.0.0.1:0` (`:250` "s.bind(('127.0.0.1', 0))").
  - The server is asked for `--host 127.0.0.1` (`:863`).
  - HTTP goes only to `127.0.0.1` (`:328`, `:413`) with no proxy or redirect: `:395` "build_opener(urllib.request.ProxyHandler({}), _NoRedirect)".
- **Registered-port refusal:**
  - Hard pins: `:58` "HARD_REFUSED_PORTS = {8080, 34113}".
  - Registry parse, fail-closed: `:196-200`.
  - Explicit `--port` refusal plus a live-listener refusal: `:237-246`.
  - bind(:0) retry: `:252`.
  - The rebind race is caught by D1 ownership: `:471-478`.
- **Teardown:**
  - `killpg` happens only while the child is unreaped: `:663` "if proc.returncode is None:  # F5: killpg only while child is alive". A zombie keeps its pgid reserved, so this kill cannot hit a recycled pid.
  - SIGKILL fallback: `:672-677`.
  - Teardown runs on every caught path through the `finally` at `:1010-1019`.
- **PDEATHSIG backstop:** `:303` "libc.prctl(1, signal.SIGKILL, 0, 0, 0)  # PR_SET_PDEATHSIG".
- **Env:**
  - Child env allowlist: `:875` "child_env = {k: os.environ[k] for k in CHILD_ENV_KEYS if k in os.environ}".
  - Only names are recorded: `:876`.
  - The probe gets the same allowlist: `:629`.
- **Receipt write:** atomic sibling temp file plus `os.replace`, mode 0600 from `mkstemp` (`:756-761`).
- **Digest gate before launch:** `:795-801`.
- **Probe writes:** in `check` mode the probe writes only under a removed `mktemp` dir (`tools/kama-probe.sh:9-10` "listeners/consumers/check write only to a removed mktemp dir"). `registry/history` is touched only by `snapshot`.

## Live-state observation
- `ps` found no running `llama-server`, `kama-llamacpp`, `controls.py` or fake processes when I checked (the grep exited 1, no matches).
- `ss -ltnp` showed only loopback `python3` listeners on 8787-8796, pids 1511-1518. [INFERENCE: long-lived host services, not lane fakes — low pids, not on the ephemeral range.]
- None of those ports is 8080, 34113 or registry-listed.

## Peer coordination (short messages, no file edits)
- KamaR17.C2Controls-2: F1, F2, F3, TMPDIR, F6.
- KamaR17.ProbeSigtermFake-2: F1, F6, F2.
- KamaR17.C2LiveTool-2: F4, F5, F10, child pid.

## Limitations
- Static review only. No tool, gate, fake or llama-server was run, because my item gives no scratch-run allowance.
- F1 rests on `Path.resolve()` of the frozen path plus an existence check, not an execution. F7, F9 and F12's PDEATHSIG behaviour are reasoned from source.
- v2 tool and controls.py were absent when I audited. Re-audit the F2–F5 remediations against the landed code.

## Installs
None.
