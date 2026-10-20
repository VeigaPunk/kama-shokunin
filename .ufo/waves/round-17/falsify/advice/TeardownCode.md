VERDICT: partial — signal bookkeeping fails closed on ProcessLookupError, but teardown does not gate SIGTERM on readiness.

## Findings

- **P3 — No ready/listening precondition guards cleanup SIGTERM (failure paths only).** `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:599-608` reports ready only after `/health` returns 200; main raises `SetupError` when `ready` is false (`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1155-1156`). However `finally` invokes `teardown` whenever a child or log exists (`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1250-1267`), without checking `ready` or handler installation. Thus a startup timeout/error can still receive SIGTERM before the harness has observed readiness. The receipt gate rejects non-null `setup_error` (`/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py:209-211`), and the graceful condition also requires child listener ownership and the expected signal/exit fields (`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1311-1317`), so this is not evidence of a false VALID receipt. If the intended invariant is that no SIGTERM is ever sent before the handler-installed/listening precondition, the implementation does not enforce it. Quotes: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1155` `if not ready:`; `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1265-1267` `if log_path is not None or proc is not None` / `td = teardown(proc, port, log_path)`.

## Confirmed teardown behavior

- `alive_at_teardown_start` is derived from a fresh `_child_running(proc)` call at `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:776-780`; `_child_running` calls `proc.poll()` at `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:749-756`. The SIGTERM call follows at `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:782`, after only the truth guard and `try` setup. The child is launched with `start_new_session=True` at `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1128-1133`, so `proc.pid` is the intended process-group ID.
- `sigterm_sent` starts false at `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:776` and is set true only after `os.killpg(proc.pid, signal.SIGTERM)` returns (`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:782-783`). `ProcessLookupError`, `PermissionError`, and other `OSError`s are caught at `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:784`; on the ProcessLookupError race, the flag remains false. The subsequent `proc.wait()` and returncode capture occur at `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:786-802`. The graceful predicate requires `sigterm_sent is True` at `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1313`, so this race cannot pass `teardown_graceful`, even if the observed returncode is 0. The stale `alive_at_teardown_start=True` is not sufficient to pass.
- This is a fresh poll immediately before the send attempt, not an atomic poll-and-signal operation; the check/use interval remains. `sigterm_sent=True` means the process-group signal call returned successfully, not an application-level acknowledgement that a particular handler ran.

## Residual risk and verification gaps

- No explicit readiness/handler-installed state is checked inside `teardown`; readiness gates the ordinary run path, while `finally` still performs cleanup on failures. The receipt gate prevents those setup failures from being accepted as complete runs.
- LSP was unavailable: `read xd://lsp` returned “No such tool.” Exact-line grep was used only as literal fallback; semantic conclusions above come from reading the implementation and receipt-gate source at the target commit. No runtime, tests, or other checks were run; no ports were contacted.
- Installs/updates: none.

## Commands run (exit codes)

```text
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/TeardownCode-clone && git -C /tmp/TeardownCode-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && echo OK  # 0
grep -n "teardown_graceful\|alive_at_teardown_start\|killpg\|sigterm_sent\|ProcessLookupError\|listening on\|listening\b" /tmp/TeardownCode-clone/tools/kama-llamacpp-live.py  # 0
wc -l /tmp/TeardownCode-clone/tools/kama-llamacpp-live.py && git -C /tmp/TeardownCode-clone log --oneline -1  # 0
grep -n "TERM_GRACE\|health\|ready\|start_new_session\|preexec\|setsid\|def run_\|def main\|teardown(\|_check(\|already listening" /tmp/TeardownCode-clone/tools/kama-llamacpp-live.py | sed -n 1,80p  # 0
grep -n -E "def _child_running|def teardown|alive_at_teardown_start|sigterm_sent|killpg|except \(ProcessLookupError|proc.wait|TERM_GRACE|raise SetupError\(fail\)|td = teardown|graceful =|returncode|start_new_session|def _port_refuses|def verify_live" /tmp/TeardownCode-clone/tools/kama-llamacpp-live.py  # 0
grep -n "F5\|F0\|F1\b\|F2\b\|F3\b\|F4\b\|F6\b\|F7\b\|F8\b\|killpg\|alive_at" /tmp/TeardownCode-clone/tests/llamacpp-live/controls.py | sed -n 1,40p; echo ---; grep -n "exit_code\|exit\b\|setup_error\|checks\|VALID" /tmp/TeardownCode-clone/tests/llamacpp-live/check-receipt.py | sed -n 1,40p  # 0
git -C /tmp/TeardownCode-clone rev-parse HEAD && git -C /tmp/TeardownCode-clone status --short  # 0
rm -rf /tmp/TeardownCode-clone  # 0
```

