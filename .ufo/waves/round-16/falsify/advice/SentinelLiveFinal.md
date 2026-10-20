VERDICT: partial — security review of the final tools/kama-llamacpp-live.py at b8e485c (sha256 cf95f382…a39ea; same as the working tree)

The trust boundaries hold: env allowlist, --offline, loopback bind, refusal set, ownership gates, teardown with signals ignored, PDEATHSIG, atomic receipt write, log deletion on handled paths, and no secrets in receipts. One exit-contract defect is confirmed: unexpected exceptions exit 1 with no receipt. Four smaller defects are also confirmed by demonstration. The live run itself never started llama-server: every experiment used scratch fake `--server` scripts or called functions directly in /tmp. The scratch dir is removed, and `pgrep -x llama-server` was empty at the end.

## Findings (severity order)

### F1 LOW-MED: exceptions other than SetupError/Terminated exit 1 with a traceback and no receipt
- **Exploit path:** an `OSError` from `Popen` (ENOEXEC/ETXTBSY), a `ValueError` from `_emit` (`allow_nan=False`), a `KeyError` at :956 when teardown failed, or a `Terminated` raised outside the protected window. None of these is caught at :935-940. `finally` still tears down, but the exception then leaves `main`.
- **Windows for `Terminated`:**
  - while lines :936-940 run;
  - between the per-signal SIG_IGN calls at :944-945;
  - after the handlers come back at :973-974, i.e. during `_emit` at :980. `_emit` catches only `OSError` (:677), so a sibling `.kama-live-*` temp file can be left behind.
- **Evidence:**
  - The docstring at :18-20 says "1 at least one check failed (server ran; receipt written)" and "2 setup error (… launch failure …)".
  - Run with a non-ELF executable as `--server`, a dummy model and the matching sha:
    - `python3 tools/kama-llamacpp-live.py --server …/fake-enoexec … --out …/r-enoexec.json` → `E2_exit=1`
    - stderr ends `OSError: [Errno 8] Exec format error`
    - `ls r-enoexec.json` → "No such file or directory". No temp log was leaked.
  - Calling the module directly: `_emit({'x': json.loads('NaN')}, …)` raised `ValueError Out of range float values are not JSON compliant: nan`, which `_emit` does not catch.
  - :951 stores `{'error': …}`, then :956 reads `receipt['teardown']['returncode']`, which raises `KeyError`.
- **Impact:**
  - A gate or caller reading exit 1 as "a check failed and a receipt exists" is misled.
  - The NaN path [INFERENCE] is practically unreachable from b11755, because nlohmann::json emits null rather than NaN.
- **Smallest remediation:**
  - Add `except Exception as exc: receipt['setup_error'] = f'unexpected:{type(exc).__name__}'; exit_code = 2` after :940.
  - Restore the signal handlers after `_emit`, not before it.
  - Catch `ValueError` in `_emit` and unlink the temp file on any `BaseException`.
  - Use `.get('returncode')` and `.get('port_refuses')` at :956-962.

### F2 LOW: the prctl report pipe's write end leaks into llama-server; the comment at :805-806 is false
- **Code:** :821-822 adds `pass_fds=(w_fd,)`. That makes the fd inheritable, so it survives `exec`.
- **Comment:** :806 says "exec() closes it, so EOF means the outcome is honestly 'unknown'".
- **Evidence:** the fake server ran `ls -l /proc/$$/fd` and showed `5 -> pipe:[8350258]` (`l-wx`) inherited across exec.
- **Impact [INFERENCE]:** if the child never writes the byte (e.g. `import ctypes` fails in `preexec_fn`), `os.read(r_fd, 1)` at :835 has no timeout. It blocks until the server exits, so `--ready-timeout` is bypassed. A signal still recovers through `Terminated`. The server also holds a stray fd.
- **Smallest remediation:** drop `pass_fds`.
  - Control: an O_CLOEXEC pipe without `pass_fds`, whose `preexec_fn` writes a byte.
  - Parent read `b'1'`; the child's fds were only `0 1 2`. `preexec_fn` runs before exec closes the fd, so the measurement survives and EOF really means "unknown".

### F3 LOW: the HTTP opener follows redirects (:320)
- **Code:** `build_opener(ProxyHandler({}))` keeps the default `HTTPRedirectHandler`.
- **Exploit path:** readiness polling (:412) runs before ownership is proven. A squatter that wins the bind race can 302 the harness to any http/https/ftp host. That is an off-loopback request despite the loopback-only design. The ownership gate (:435) rejects the run afterwards, but the outbound request has already been made.
- **Evidence:** in-process `http_get(<redirector port 42293>, '/health')` returned `status 200 body b'{"status":"ok"}'` from another loopback port (37229). The target logged a hit on `['/elsewhere']`.
- **Smallest remediation:** install an `HTTPRedirectHandler` subclass whose `redirect_request` returns `None`, so the 3xx is recorded as the status.

### F4 LOW: readiness deadline not enforced inside a request
- **Code:** `POLL_TIMEOUT=0.5` (:60) is a per-socket-operation timeout; the deadline is checked only between requests (:406, :443).
- **Evidence:** a slow-drip stub (1 byte every 0.4 s) kept one `http_get` busy for `elapsed_s 4.8` (status 200, body_len 12).
- **Impact:** a pre-ownership squatter can stall the harness indefinitely, up to 64 KiB at under 0.5 s per byte. The result is a hang, not a false pass; signals still work.
- **Smallest remediation:** read the body in chunks against a wall-clock deadline.

### F5 INFO: `killpg` on an already-reaped pid
- **Code:** `proc.poll()` at :407 reaps the child; `teardown` still calls `os.killpg(proc.pid, SIGTERM)` at :581.
- **Evidence:** with a fake server that runs `exit 0`, the run gave `setup_error server-exited-early-rc0`. The spied killpg calls were `[(511848, 15, False)]`, meaning `/proc/<pid>` was already gone.
- **Impact [INFERENCE]:** a different process group could be signalled only if the pid were reused within milliseconds. That is negligible with `pid_max` = 4194304.
- **Fix:** guard with `if proc.returncode is None` (what `Popen.send_signal` already does).

### F6 INFO: the server runs with default CORS `*` and no API key
- **Evidence:** pinned server.cpp:355-356 warns "security: no API key is set and CORS allows all origins". The argv at :773-782 sets neither option.
- **Impact [INFERENCE]:** for the few seconds of a run, any browser page can read `/props` and `/slots` and POST inference on 127.0.0.1:<port>. The model is tiny and holds no secrets.
- **Fix:** add `--cors-origins localhost` (README.md:197). An API key would break the probe's MODEL_OK path.

### F7 INFO: temp log leaks when the harness dies from an unhandled signal; PDEATHSIG backstop confirmed
`sig_driver.py` started the harness with fake `sleep 31.7` children:

| Signal | Harness rc | Child | Temp log | Receipt |
|---|---|---|---|---|
| SIGKILL | -9 | gone | `log_exists=True` | none |
| SIGQUIT | -3 | gone | `log_exists=True` | none |
| SIGTERM | 2 | gone | deleted | `'terminated:signal 15'`; teardown_exited, teardown_port_closed and model_unchanged all True |

- My driver deleted the leaked logs.
- The log is created 0600 by mkstemp [INFERENCE: documented mkstemp behaviour]. It holds only server stdout.
- **Fix (optional):** add SIGQUIT to the handled set at :795. Uncatchable SIGKILL cannot be fixed.

### F8 INFO: TOCTOU between hashing and exec
- **Model:** hashed at :710. The server is launched with `args.model` (:774), not the realpath recorded at :748. A same-uid swap-and-restore of a symlink during the run is not caught by the post-hash at :964.
- **Binary:** the same pattern applies to it (:719 → :824).
- **Fix:** pass `os.path.realpath(args.model)` in the argv so it matches the receipt. Full closure would need fd passing; this is same-uid only.

### F9 INFO: body/header caps inconsistent
- `loading_503.body` (:432) keeps up to 64 KiB (HTTP_BODY_CAP) rather than TRANSITION_BODY_CAP 4096.
- `_capture` stores the full header dict (:471), bounded only by http.client limits (100 headers, 64 KiB lines).
- Probe stdout is fully buffered and stored as `result` (:544-554).

### F10 INFO: the probe inherits HOME
- The probe gets HOME through `child_env` (:907, :545). kama-probe.sh calls curl with `--noproxy '*'` but no `-q` (:292, :324), so `~/.curlrc` would be honored. None exists (`no-curlrc`).

## Confirmed holds (attacked, not refuted)
- **Env allowlist (:73, :784):**
  - Harness env set with `env -i PATH HOME KAMA_CANARY LLAMA_ARG_HOST=0.0.0.0 LLAMA_ARG_REUSE_PORT=1 HTTP_PROXY LD_LIBRARY_PATH`.
  - Child env names were exactly `HOME PATH PWD SHLVL _` (the last three set by sh itself), and the receipt has `child_env_keys ['HOME','PATH']`.
  - So LLAMA_ARG_* overrides and proxies cannot reach the server or the probe. Values are never recorded.
- **--offline / loopback:**
  - argv hardcodes `--host 127.0.0.1` and `--offline` (:776, :781); there is no CLI to override them.
  - README.md:111: "`--offline` | Offline mode: forces use of cache, prevents network access".
  - The L1 receipts' argv ends `--no-webui --offline`.
- **SO_REUSEPORT:** server-http.cpp:218-222 sets SO_REUSEPORT only with `--reuse-port`, which defaults to disabled (README.md:195), and the env route is stripped. So `port_owned_by` returning True when any one inode is the child's (:285-288) cannot be exploited by a same-address co-listener [INFERENCE].
- **Refusal set:**
  - :57 plus registry parsing, giving `port_refusal_set [8080, 34113]` in both receipts.
  - controls.txt records `port-refused-registered:34113`, `…:8080` and `port-in-use:631`, each exit 2.
  - An explicit port that neither refuses nor accepts is allowed (:244-245, fail-open), but the ownership gates catch a squatter.
- **Ownership gates:** at readiness (:435), pre-captures (:861), each pre-probe (:903) and post-probes (:910). They fail closed on None ("ownership-unproven").
- **Teardown with repeated signals:**
  - The fake server ignored SIGTERM. I sent SIGTERM, then SIGTERM again 2 s later, then SIGINT and SIGHUP during the grace period.
  - Result: rc 2, `term_wait_ms 10001`, `sigkill_sent True`, `returncode -9`, `port_refuses True`, log deleted. The SIG_IGN at :944-945 holds.
- **PDEATHSIG:** receipts show `prctl_ok: True`, and the SIGKILL/SIGQUIT runs above show the child gone after harness death.
- **Atomic write:** a sibling mkstemp file followed by `os.replace` (:671-676). The output is mode 0600 (`stat` → `600 r-fds.json`). There is no fsync, which affects durability only.
- **Temp log deletion on handled paths:** ready-timeout, SIGTERM, ENOEXEC and the L1 runs all gave `log_exists False`.
- **No secrets in receipts:**
  - I scanned both L1 receipts for token, api key, bearer, secret, passw, HF_, proxy, authorization, `sk-…`, LLAMA_ARG and cookie.
  - The only hit was "llama-tokenize", an install_tree filename. `/home/vgpnk` appears in paths (username only).
  - Captured headers are Server, Content-Type, Content-Length, Connection and an empty ACAO. The kept log lines are three load/listen lines.

## Commands run (all scratch in /tmp/kama-r16-SentinelLiveFinal, now removed)
- `sha256sum` of the working tree vs `git show b8e485c:…` → identical.
- Fake-server env/fd run → exit 2 (`ready-timeout`).
- ENOEXEC run → exit 1.
- `probe_units.py` (redirect, slow-drip, NaN `_emit`, killpg spy, plus a `main()` run with the exit0 fake whose result was exit 2 / server-exited-early-rc0) → driver exit 0.
- `sig_driver.py` (SIGKILL, SIGTERM, SIGQUIT) → driver exit 0.
- Double-signal driver → harness rc 2.
- O_CLOEXEC pipe control → `b'1'`, child fds `0 1 2`.
- `cat /proc/sys/kernel/pid_max` → 4194304.
- Final `pgrep -x llama-server` → empty; no `sleep 31.7` marker left.

## Limitations
- I did not start the real llama-server. The `os.read` hang in F2 and the impacts of F6 and F8 are reasoned, not reproduced.
- I did not try to hit the narrow `Terminated` windows in F1.

## Installs
None.
