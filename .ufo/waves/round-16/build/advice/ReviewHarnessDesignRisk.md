# ReviewHarnessDesignRisk: LiveHarness race windows (round 16, build wave)

Seat: reviewer, read-only. Date: 2026-10-20. These findings are advice, never verdicts.

**Scope and version pin.** The design under review is the LiveHarness item at
`.ufo/waves/round-16/build/make_spec.py:69` (same text as item `LiveHarness` in `spec.json`) plus the C2 bullet at
`make_spec.py:15`. The implementation (`tools/kama-llamacpp-live.py`) landed at 10:31 while this seat ran and was rewritten
continuously (699 → 711 → 734 → 788 → 795 → 801 → 871 → ~880 lines within ten minutes). **Implementation citations are
therefore symbol + exact quote, not line numbers**; the quoted code was last verified at sha256
`57d77fba…9be219` (~880 lines, `ast.parse` OK). Design, registry, probe and llama.cpp citations are `path:line` and stable.
Two transient blockers were observed mid-seat (a `pick_port` arity mismatch at sha `70179b74…`, reported to the owner;
and a 5-tuple/4-unpack mismatch). Both are fixed and not listed below. The owner is still editing; L1 must re-run this
checklist on the final artifact.

Sources opened: the harness; `tools/kama-probe.sh`; `registry/endpoint-consumers.tsv`;
`/proc/sys/net/ipv4/ip_local_port_range`; installed `llama-server --help/--version` (b11755, commit 704366d76); b11755
`tools/server/{server.cpp,server-http.cpp,server-context.cpp,server-common.cpp}`, `common/arg.cpp`, and
`vendor/cpp-httplib/{httplib.cpp,httplib.h}` on raw.githubusercontent.com. No server was launched and no lane gate or
measurement was run.

## Summary

- Four race windows, one detector each; the code now has the two structural ones: an inode listener-ownership gate
  (`port_owned_by`) at readiness and a `PR_SET_PDEATHSIG` backstop in `preexec_fn`. Both are the right primitives.
- The gate is **not re-applied after readiness** and treats "ownership unknown" as success. The remaining dangerous
  window is attribution: a child that dies after `/health` 200 leaves the port free, and the captures and both probe runs
  can be answered by a stranger while the receipt attributes them to the pinned binary/model.
- **Teardown ordering is inverted**: the SIGTERM/SIGINT/SIGHUP handlers are restored to their defaults before
  `teardown()` runs, so a second signal during teardown kills the harness and aborts the cleanup the design promises.
- Three reads are **unbounded** (`resp.read()`, `exc.read()`, whole log), exactly when the port-race scenario makes the
  peer untrusted.
- The loading-envelope predicate landed during the seat (`loading_envelope_exact`, recorded in the receipt); the older
  `loading_observed` boolean still reads as an assertion and should be renamed (R4, downgraded to INFO).
- Correction to `SentinelLiveSafety.md:48` (F3): for this argv a port collision is **loud** (`EADDRINUSE` → child exit),
  not a silent SO_REUSEPORT co-bind. The silent path requires an inherited `LLAMA_ARG_REUSE_PORT`, and the harness does
  not scrub the child environment. See "Checked and adequate".

## Named windows (the three in the assignment)

| Window | Where | Status at the final check |
|---|---|---|
| Port reuse between the selection socket's `close()` and the child's `bind()` | `pick_port` → `readiness_loop` | Detector exists but is lenient and one-shot (R1); the explicit `--port` path uses a connect test, not a bind test (R7). |
| Zombie / unreaped early exit | `readiness_loop` + `teardown` | Handled: `poll()` each iteration classifies early exit as setup error; `wait(timeout=...)` sets `returncode` before `teardown_exited` reads it. |
| Orphan when the harness dies | `Popen` + `finally` | PDEATHSIG is wired (good), but the receipt asserts it unconditionally (R11) and the handler-restore ordering can abort teardown on a second signal (R2). |
| Attribution after readiness (the window the first three feed) | `ready_captures`, `run_probe` | Unprotected: no `poll()`/ownership re-check before captures or probes (R1, R5). |
| Teardown proof | `teardown` | Connect-based, not identity-based (R9). |

## Findings

### R1 (HIGH). Ownership is proven once, and "unknown" is accepted as ready

**Design clause.** "a free loopback port that is never a registered consumer port" (`make_spec.py:15`) and "until
/health is 200 or timeout" (`make_spec.py:69`).

**Code.** `readiness_loop` checks ownership only at the ready transition:

```python
if path == '/health' and result['status'] == 200:
    owned = port_owned_by(proc.pid, port)
    if owned is False:
        return (transitions, loading_503, False,
                'port-listener-not-our-child', owned)
    return transitions, loading_503, True, None, owned
```

`port_owned_by` is deliberately tri-state: `None` means "no listener yet, or /proc unreadable (ownership unknown)"
(its docstring). The caller fails only on `False`, so an unreadable `/proc` or a listener that vanished between the 200
response and the scan is accepted as ours. After `readiness_loop` returns, `ready_captures` and the two probes hit the
port with **no `proc.poll()` and no ownership re-check**. A child that exits after readiness frees `P` for a stranger;
the captures and both probe runs are then foreign evidence, and the receipt attributes them to the pinned binary/model.

**Minimal mitigation.** On `/health` 200, retry the scan once on `None`, then fail closed (exit 2). Re-run
`port_owned_by` and `proc.poll() is None` immediately before `ready_captures` and before each probe; return the owned
inode from the readiness loop and compare against it. These are setup gates, not checks: "we measured nothing" must not
be encoded as a failed check verdict.

### R2 (MEDIUM-HIGH). Handlers are restored before teardown, so a second signal aborts teardown

**Design clause.** "Always tear down (try/finally, signal handlers)" (`make_spec.py:69`).

**Code.** In the `finally`, the order is:

```python
for sig, handler in old_handlers.items():
    signal.signal(sig, handler)
if log_path is not None or proc is not None:
    receipt['teardown'] = teardown(proc, port, log_path)
```

The restored handlers are the pre-run defaults, so from the first line of the `finally` until `teardown()` returns, a
SIGTERM/SIGINT kills the harness immediately. Before `killpg` it orphans the server (own session, no terminal HUP);
during `wait(timeout=TERM_GRACE)` it skips the SIGKILL fallback. The handler exists to make cleanup reliable and this
ordering removes that guarantee in the teardown window.

**Minimal mitigation.** Keep the handlers installed until `teardown()` returns (restore last), or block
`SIGTERM/SIGINT/SIGHUP` with `signal.pthread_sigmask` at teardown entry. A `_teardown_done` flag makes a re-entrant call a
no-op. (Same class as `SentinelLiveSafety.md` F4.3, but here it is ordering, not the handler body.)

### R3 (MEDIUM). Unbounded body and log reads

**Code.** `http_get` reads whole bodies: `'body': resp.read(),` and, in the `HTTPError` branch, `body = exc.read()`.
`_decode_body` caps only after the bytes are in memory, and the `loading_503` entry re-decodes the full body
(`'body': result['body'].decode(...)`). `teardown` reads the whole temp log with
`text = Path(log_path).read_text(...)` before keeping at most 200 lines. Under R1 the peer is untrusted (hijacked port),
and `--server` is caller-supplied; either can return or write megabytes. `CAPTURE_BODY_CAP` (1 MiB) and `LOG_KEEP_MAX`
(200) bound the receipt, not the read.

**Minimal mitigation.** `read(cap + 1)` and keep the existing over-cap flag; hash the prefix and say so if a full-body
digest is not needed; read at most ~256 KiB of the log (prefix or tail) before filtering.

### R4 (INFO, downgraded during the seat). `loading_observed` still reads as an assertion

**Code.** `main` records `receipt['loading_observed'] = loading_503 is not None` where `loading_503` is the first 503 from
either path. The seat-time finding was that the envelope was never evaluated; the owner has since added
`loading_envelope_exact(loading_503)` (message `"Loading model"`, type `"unavailable_error"`, integer `503`) and records
it in the receipt, which fixes the substance. The remaining nit is naming: `loading_observed` is true for *any* 503
(including a stranger's), so a reader can still over-read it.

**Minimal mitigation.** Rename to `first_503_seen` (or gate it on `loading_envelope_exact is True`). Keep the raw body and
the explicit envelope boolean.

### R5 (MEDIUM). Probe invocations are not the contract invocation and are not gated

**Code.** `run_probe` builds
`argv = ['bash', str(probe), 'check', '--port', str(port), '--expect', expect, '--json']` and
`env = dict(os.environ)`, forcing only `NO_PROXY`/`no_proxy`.

- No `--timeout 2 --connect-timeout 1`; the probe defaults are 5/2 (`tools/kama-probe.sh:66-67`), so the receipt's probe
  evidence is not comparable with the matrix and a wedged request costs 5 s instead of 2. The aggregate 60 s subprocess
  timeout is present and good.
- The environment is inherited wholesale. `SentinelLiveSafety.md` F1's allow-list applies: the probe needs `PATH`,
  `LANG`, the proxy pair, and `KAMA_PROBE_TMPDIR` if set.
- No `proc.poll()` / `port_owned_by` immediately before each probe (R1), so a post-ready death becomes a failed check
  instead of setup error 2, and the probe can hit a stranger.

**Minimal mitigation.** Pass both timeout flags, use the minimal env, and gate each probe on the live child plus the
recorded inode.

### R6 (MEDIUM). `refused_ports()` fails open

**Code.** `refused_ports` wraps the registry read:

```python
try:
    text = REGISTRY.read_text(...)
except OSError:
    return refused
```

If the registry is unreadable, the registry-derived ports silently disappear and the launch proceeds with only
`HARD_REFUSED_PORTS = {8080, 34113}`. The hardcoded pair covers today's two rows (`registry/endpoint-consumers.tsv:35-37`),
but the registry is the mechanism by which future consumer ports enter the set, and with `--port` (R7) the miss becomes a
direct path to serving a registered port.

**Minimal mitigation.** Fail closed with `SetupError('registry-unreadable')` (the setup `try` already maps it to exit 2).
A launch cannot honestly claim "never a registered consumer port" without having read the registry.

### R7 (LOW-MEDIUM). Explicit `--port` is out of contract, and its liveness test can mislead

**Code.** `--port` is not in the design's argument list (`make_spec.py:69`); it was added during the seat and is handled by
`pick_port(refused, requested=None)`. The validation is careful — range check, `if requested in refused:`, and a connect
test — but:

- the connect test treats timeout/reset as free: `return requested  # timeout/reset: no proven listener; try anyway`. A
  wedged listener (full accept backlog) passes, llama-server then fails to bind, and the run ends as an early-exit setup
  error. A **bind** test answers the actual question ("can llama-server bind?") without the ambiguity.
- `receipt['port_pick_note']` is unconditional: "port released after bind(:0) and re-bound by the server". For an
  explicit `--port` no `bind(:0)` happened; the note describes the wrong race and omits the connect-test → bind one.
- an explicit port is by definition not ephemeral; a caller can request a long-lived, well-known port the registry does
  not know. That is contrary to the C2 "ephemeral, lane-owned" framing, even though the default remains `bind(:0)`.

**Minimal mitigation.** Keep `--port` as a test-only affordance, document it, validate with a bind test (bind + close),
and make `port_pick_note` mode-specific.

### R8 (LOW). `HTTPError` is not closed, and redirects are followed

**Code.** Success responses use `with`, but the error branch does `body = exc.read()` without `exc.close()`. On CPython
the refcount closes it when the exception clears; a non-CPython port or a future edit that retains `exc` leaks the socket.
`_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))` leaves urllib's default redirect handler in
place, so a 302 from a hijacked `P` can move the request off loopback. `SentinelLiveSafety.md` F6 names the proxy half;
the redirect half is the same opener.

**Minimal mitigation.** `finally: exc.close()`; add a redirect handler that returns `None` (raises `HTTPError`) so a 3xx
is recorded as a status, never followed.

### R9 (LOW). `teardown_port_closed` is a connect probe, not an identity check

**Code.** `teardown` does `socket.create_connection(('127.0.0.1', port), timeout=1.0).close()` and sets `port_refuses`
from `ConnectionRefusedError`. If a stranger binds `P` between the child's exit and this probe, a correct teardown is
recorded as failed. It is R1's race in the opposite direction; the inode machinery already exists (`_listen_inodes`).

**Minimal mitigation.** Record the child's LISTEN inode at the ready gate; `teardown_port_closed` = that inode is absent
from `/proc/net/tcp{,6}`. Keep the connect probe as corroboration and record `port_reused_after_teardown` when a listener
exists with a different inode.

### R10 (LOW). Non-atomic receipt write

**Code.** `_emit` uses `Path(out_path).write_text(...)`. A kill mid-write leaves a truncated receipt. Minimal: write
`out_path + '.tmp'` in the same directory and `os.replace`. (The sentinel's F8 also covers `--out` symlink refusal; not
repeated here.)

### R11 (LOW). The receipt claims PDEATHSIG is active even when the helper failed

**Code.** `main` records `receipt['pdeathsig'] = 'SIGKILL (PR_SET_PDEATHSIG, Linux best-effort)'` unconditionally, while
`_preexec_pdeathsig` wraps `prctl` in `except Exception: pass`. If `prctl` fails (seccomp, restricted container) or the
helper is not applicable, the receipt still asserts the backstop. The same calibration failure as R4: a field naming a
control, not an observation.

**Minimal mitigation.** Record `pdeathsig_attempted` by default; prove success only if the child reports it (e.g. a
one-byte write to a `pass_fds` pipe after `prctl` returns 0). Never claim `active` from the parent side alone.

### R12 (INFO). The polling cadence is fine

`POLL_INTERVAL = 0.02` ("tight loop, but not a CPU spin") with two requests per iteration is ~100 requests/s and at most
~6000 requests over a 60 s timeout. That is not a spin and not a meaningful load for llama.cpp's HTTP pool. The
transition list folds consecutive identical signatures, so the receipt does not grow with the poll count.

## Checked and adequate

- **The loading-503 surface is observable.** The listener starts before the model loads — b11755
  `tools/server/server.cpp:493` "// start the HTTP server before loading the model to be able to serve /health requests",
  `:494` `ctx_http.start()`, `:507` `load_model(params)`, `:515` `is_ready.store(true)`. The envelope is the middleware
  at `tools/server/server-http.cpp:307-326` (`res.status = 503`; `"Loading model"`; `"unavailable_error"`).
- **HTTPError is treated as a status, not a connect error.** `http_get` returns `'status': exc.code` with `error=None`;
  the most likely implementation defect was avoided.
- **Early exit is classified as setup error.** `readiness_loop` checks `rc = proc.poll()` each iteration and returns
  `server-exited-early-rc{rc}`; `main` raises `SetupError(fail)` → exit 2. `poll()` reaps, and `teardown` proves exit
  with `proc.wait(timeout=...)`, so `teardown_exited`'s `returncode is not None` is a real proof.
- **The orphan backstop is present and wired.** `_preexec_pdeathsig` calls `libc.prctl(1, signal.SIGKILL, 0, 0, 0)` and
  re-checks `os.getppid()` against `_FORKED_PPID[0]`, which `main` sets from `os.getpid()` before `Popen` and passes as
  `preexec_fn`. The earlier unwired definition would have been dead code; that was fixed during the seat.
- **`start_new_session=True` + `killpg` is the right shape.** With `-m` set, b11755 takes single-model mode (no router
  child), and the server installs its SIGTERM handler only after load (`server.cpp:526-534`), so a load-phase SIGTERM
  takes the default action and teardown is immediate.
- **Digest and identity gates run before launch.** Model sha256 with exit 3 on mismatch, server realpath + sha256, probe
  existence, and the port pick all precede `Popen`; the setup `try` catches `SetupError`/`OSError` → exit 2.
- **The probe payload is parsed correctly.** `probe_row` takes `rows[0]`; the checks require `MODEL_OK/matched` and
  `MODEL_MISMATCH/served-id-mismatch`. The probe's CLI-override row emits `verdict`, `reason`, `served_model`, `drift`
  and exits 2 on drift (`tools/kama-probe.sh:848-853`, `:880-883`); the expected reasons are `:535` and `:537`.
- **Default port selection is bounded and sound.** 64 attempts; the selection socket sets `SO_REUSEADDR` (so it may
  return a TIME_WAIT port, which llama-server also tolerates via `server-http.cpp:219`); it cannot select a live listener.
  `34113` is inside `32768 60999` (`/proc/sys/net/ipv4/ip_local_port_range`), so the refusal retry is live; `8080` is
  outside the range and only reachable via the explicit path, which refuses it.
- **Collision is loud, not silent (correction to Sentinel F3).** cpp-httplib's default sets `SO_REUSEPORT`
  (`vendor/cpp-httplib/httplib.cpp:6613-6616`), but `Server::set_socket_options` replaces that default
  (`httplib.cpp:8942-8944` "socket_options_ = std::move(socket_options);"), and llama.cpp always calls it
  (`server-http.cpp:218-227`) with `SO_REUSEPORT` only when `reuse_port` is set. The argv does not pass `--reuse-port`;
  a second same-UID binder gets `EADDRINUSE` (`server-http.cpp:516-521` → `server.cpp:494-497`). The silent path survives
  only via inherited `LLAMA_ARG_REUSE_PORT` (`common/arg.cpp:3358-3363`), and the harness does **not** scrub the child
  env or pass `--offline`. The inode gate is the detector; the env scrub is the other half
  (`SentinelLiveSafety.md` F1/F2 cover env and library provenance — not repeated).
- **`/props` cannot KeyError.** All projected keys are unconditional in b11755 `server-context.cpp:5244-5264`.
  `owned_by: "llamacpp"` is real (`server-context.cpp:5182`), and `/metrics` without `--metrics` is
  `ERROR_TYPE_NOT_SUPPORTED` → `code = 501` (`server-common.cpp:115-118`).

## Minimal patch deltas (in order)

1. Readiness gate: retry `port_owned_by` on `None`, then fail closed; return the owned inode.
2. Before captures and before each probe: `proc.poll() is None` and ownership re-check, else exit 2.
3. `finally`: run `teardown()` first; restore handlers (or unblock signals) afterwards.
4. Bound the three reads; close `HTTPError`; refuse redirects.
5. Probe: add `--timeout 2 --connect-timeout 1`; allow-list env.
6. `refused_ports`: fail closed on `OSError`.
7. Explicit `--port`: bind-test, mode-specific `port_pick_note`.
8. `teardown_port_closed`: compare the recorded inode; connect refusal as corroboration.
9. `_emit`: tmp + `os.replace`; `pdeathsig` field renamed to `attempted` unless proven.

## Limitations

- The implementation changed at least ten times during the seat; the final check was sha256 `57d77fba…9be219` (881 lines).
  Symbol + quote citations are stable; if the owner edits again, re-locate by the quote. The harness was **not executed**,
  so R1/R2/R3/R5/R9 are code-path findings, not observed failures.
- I invoked the probe exactly once against **closed** port 1 to confirm its exit/reason JSON; no server, registry history
  or lane state was touched, and the `/tmp` scratch was deleted. No harness measurement was run.
- Linux-specific primitives (`/proc/net/tcp{,6}`, `prctl`, `pthread_sigmask`) match the linux-x64 host and are stdlib
  (`ctypes`). PDEATHSIG does not cover grandchildren if `--server` is a wrapper rather than the real binary.
- Collision probabilities and the "load finishes before the first poll" estimate are [INFERENCE]; only one 260K model is
  pinned.
- Not applicable: the generic reviewer checklist items for `resume_continuity_v1` and cross-runtime rerouting — this item
  has no resume path and no runtime selection.

## Installs

None. No tool was installed, upgraded or removed.
