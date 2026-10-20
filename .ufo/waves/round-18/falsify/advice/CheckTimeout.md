VERDICT: confirm — same-PGID timeout rows fail and their child is killed; separate sessions are outside the process-group boundary.

# Scope and axes

Seat: `KamaR18.CheckTimeout`; advice only, not an admission or integration decision. Target clone was switched to commit `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. The three axes were: (1) timeout-row correctness, (2) same-process-group child cleanup, and (3) honest containment limits for a detached session.

# Findings by severity

No actionable finding against the assigned bounded claim. `tests/probe-verdicts/check.py:279-297` starts the probe in a new session, gives `communicate()` the timeout, sends `SIGKILL` to `os.killpg(proc.pid, ...)` on timeout, drains/reaps the direct probe, and re-raises `TimeoutExpired`. `grade()` at `:425-470` initializes `passed: false`, writes `probe timed out after …s` to the row, and returns it; `main()` at `:766-782` exits 1 when any row failed.

## Same-PGID child: observed timeout row and child termination

The independent controlled assay below called the delivered `grade()`/`run_probe()` path with a 1.0-second test timeout and a closed-port selftest row (no socket opened). `/proc` captured the child’s identity before timeout. Probe PID/PGID/SID were `2369348/2369348/2369348`; child PID/PPID/PGID/SID were `2369361/2369348/2369348/2369348`. Thus the child shared the exact process group targeted by `killpg`. On return the row was `error: "probe timed out after 1.0s"`, `passed: false`, `probe_exit: null`; the subreaper `waitpid()` returned status 9 (SIGKILL), and the child was absent after reaping.

This also matches the canonical evidence, which exercised the production 30-second timeout. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/c2-survivors.json`, `results.e.items[id=="escaped-sleep"].current`: outcome `handled`, check exit 1, 30.08 seconds, `row_passed: false`, `row_error: "probe timed out after 30s"`, `escaped_pids: []`, `killed_after_scan: []`. The paired frozen run was `accepted`: it emitted the same failed row but left PID 1280158 alive; the survivors runner then killed that specifically marked child. The current F17 detector result is `detected: true`, `check_exit: 1`.

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/checker-selftest.stdout:2723-2729` independently records the delivered `--selftest` timeout control: recorded timeout error, `child_completed: false`, `passed: true`; `.exit` says `exit=0`.

## Residual containment limit: a new session can escape

The controlled detached case called `setsid()` in the child. Probe PID/PGID/SID were `2369897/2369897/2369897`; child PID/PGID/SID were `2369898/2369898/2369898`. At the post-timeout observation the child remained in state `S` under the distinct session and PGID; it was not killed by the probe-group signal. The grader had not returned (`worker_done_before_external_reap: false`): the detached child inherited the captured stdout/stderr pipe descriptors, so the second unbounded `proc.communicate()` waited for EOF after the probe group was killed. The assay then SIGKILLed the exact adopted PID and `waitpid()` returned status 9; pipe closure let `grade()` return the failed timeout row. Final process check found the child absent.

This is the explicit boundary, not a claim of full process-tree containment: process-group kill cannot reach a child that deliberately creates a new session. If that child holds the captured pipes, the timeout row can be delayed until the pipes close (in this assay, 1.211 seconds for a 1.0-second timeout, because the assessor reaped the child immediately after observing the escape). No unbounded-wait or arbitrary-session-tree guarantee is claimed. This limitation is also called out at `.ufo/waves/round-18/build/advice/C2CheckPyRobust.md:26`.

# Exact experiment command and output

Command, run from the clone (no listener, no registered port):

```text
python3 /tmp/kama-r18-falsify-CheckTimeout/seatwork/contained_probe.py
```

Observed stdout and exit:

```text
{"case": "same-group", "child_absent_final": true, "child_identity": {"pgid": 2369348, "pid": 2369361, "ppid": 2369348, "sid": 2369348}, "child_state_after_timeout_branch": {"pgid": 2369348, "ppid": 2369342, "sid": 2369348, "state": "Z"}, "different_session_from_probe": false, "grade_returned": true, "grade_wall_seconds": 1.001, "probe_identity": {"pgid": 2369348, "pid": 2369348, "sid": 2369348}, "reap": {"pid": 2369361, "reaped": true, "status": 9}, "record_error": "probe timed out after 1.0s", "record_passed": false, "record_probe_exit": null, "same_pgid_as_probe": true, "timeout": 1.0, "worker_done_before_external_reap": true, "worker_exception": null}
{"case": "detached-session", "child_absent_final": true, "child_identity": {"pgid": 2369898, "pid": 2369898, "ppid": 2369897, "sid": 2369898}, "child_state_after_timeout_branch": {"pgid": 2369898, "ppid": 2369342, "sid": 2369898, "state": "S"}, "different_session_from_probe": true, "grade_returned": true, "grade_wall_seconds": 1.211, "probe_identity": {"pgid": 2369897, "pid": 2369897, "sid": 2369897}, "reap": {"pid": 2369898, "reaped": true, "status": 9}, "record_error": "probe timed out after 1.0s", "record_passed": false, "record_probe_exit": null, "same_pgid_as_probe": false, "timeout": 1.0, "worker_done_before_external_reap": false, "worker_exception": null}
{"assay": "PASS"}
EXIT=0
```

Exact experiment source (SHA-256 `4b3b0db4240eab212b34662c8b8762a73de7c28f9bb1771466073b110b91a796`):

```python
#!/usr/bin/env python3
"""Bounded same-group vs detached-session timeout assay.

Uses the delivered check.py module's grade() -> run_probe() directly. A
thread runs the grade path with a 1.0s timeout; the observer records group
and session identities before timeout. In the detached case, the original
process group is SIGKILLed while the new-session child continues holding the
captured stdout/stderr pipes, so grade remains blocked in its second
communicate(). This assay enables Linux child-subreaper mode, waits until the
child is adopted, sends SIGKILL to that exact pid, and waitpid()s it; this
releases the pipe and lets grade record its timeout row. No listeners or
registered ports: the selftest row is closed-port and bind is patched to 0.
Timeout=1s is the same branch as the production 30s PROBE_TIMEOUT; the
pristine check.py --selftest also exercises its embedded same-group timeout
control at 0.1s.
"""
import ctypes
import importlib.util
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path('/tmp/kama-r18-falsify-CheckTimeout')
CHECK = ROOT / 'tests/probe-verdicts/check.py'
PY = sys.executable
PR_SET_CHILD_SUBREAPER = 36
libc = ctypes.CDLL(None, use_errno=True)
if libc.prctl(PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0) != 0:
    err = ctypes.get_errno()
    raise OSError(err, os.strerror(err))

spec = importlib.util.spec_from_file_location('delivered_check', CHECK)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
check.bind_closed_port = lambda: 0
ENTRY = {'test': dict(check.SELFTEST_VALID_TEST), 'source': '<seat-assay>'}


def stat(pid):
    try:
        raw = Path(f'/proc/{pid}/stat').read_bytes()
        fields = raw[raw.rfind(b')') + 2:].split()
        return {'state': fields[0].decode(), 'ppid': int(fields[1]),
                'pgid': int(fields[2]), 'sid': int(fields[3])}
    except OSError:
        return None


def reap(pid, timeout=5):
    if pid is None:
        return {'pid': None, 'reaped': True, 'status': None}
    deadline = time.monotonic() + timeout
    status = None
    while time.monotonic() < deadline:
        try:
            got, status = os.waitpid(pid, os.WNOHANG)
            if got == pid:
                return {'pid': pid, 'reaped': True, 'status': status}
        except ChildProcessError:
            pass
        time.sleep(0.02)
    try:
        os.kill(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            got, status = os.waitpid(pid, os.WNOHANG)
            if got == pid:
                return {'pid': pid, 'reaped': True, 'status': status,
                        'sigkill_sent': True}
        except ChildProcessError:
            if stat(pid) is None:
                return {'pid': pid, 'reaped': True, 'status': None,
                        'adopted_elsewhere': True}
        time.sleep(0.02)
    return {'pid': pid, 'reaped': False, 'status': status}


def run_case(name, detach, sleep_seconds=60):
    with tempfile.TemporaryDirectory(prefix=f'kama-ct-{name}-') as td:
        d = Path(td)
        child_info, probe_info = d / 'child.json', d / 'probe.json'
        helper, probe = d / 'worker.py', d / 'probe.sh'
        helper.write_text(
            'import json, os, time\n'
            f"open({str(probe_info)!r}, 'w').write(json.dumps({{'pid':os.getpid(),'pgid':os.getpgrp(),'sid':os.getsid(0)}}))\n"
            'pid = os.fork()\n'
            'if pid == 0:\n'
            + ('    os.setsid()\n' if detach else '')
            + f"    open({str(child_info)!r}, 'w').write(json.dumps({{'pid':os.getpid(),'ppid':os.getppid(),'pgid':os.getpgrp(),'sid':os.getsid(0)}}))\n"
            + f'    time.sleep({sleep_seconds})\n'
            + '    os._exit(0)\n'
            + f'else: time.sleep({sleep_seconds})\n', encoding='utf-8')
        probe.write_text('#!/usr/bin/env bash\nexec ' + PY + ' ' + str(helper) + '\n',
                         encoding='utf-8')
        probe.chmod(0o700)
        result, done = {}, threading.Event()
        def grade_worker():
            t0 = time.monotonic()
            try:
                result['record'] = check.grade(ENTRY, probe, timeout=1.0)
                result['exception'] = None
            except BaseException as exc:
                result['exception'] = f'{type(exc).__name__}: {exc}'
            result['seconds'] = round(time.monotonic() - t0, 3)
            done.set()
        th = threading.Thread(target=grade_worker, name=f'grade-{name}')
        th.start()
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline and not child_info.exists():
            time.sleep(0.01)
        if not child_info.exists():
            th.join(5)
            return {'case': name, 'error': 'probe did not write child identity',
                    'worker_exception': result.get('exception')}
        c, p = json.loads(child_info.read_text()), json.loads(probe_info.read_text())
        # Give the 1s timeout path time to issue killpg. The detached child's
        # held pipes make the worker remain inside the final communicate().
        time.sleep(1.2)
        child_at_timeout = stat(c['pid'])
        worker_done_before_reap = done.is_set()
        if detach and child_at_timeout:
            # The original parent/group is dead. As a child subreaper, this
            # assessor adopts the child and reaps it by its exact pid.
            try:
                os.kill(c['pid'], signal.SIGKILL)
            except ProcessLookupError:
                pass
        th.join(8)
        record = result.get('record') or {}
        reaped = reap(c['pid'], 5)
        out = {
            'case': name, 'timeout': 1.0,
            'grade_returned': done.is_set(),
            'grade_wall_seconds': result.get('seconds'),
            'record_error': record.get('error'),
            'record_passed': record.get('passed'),
            'record_probe_exit': record.get('probe_exit'),
            'worker_exception': result.get('exception'),
            'probe_identity': p, 'child_identity': c,
            'child_state_after_timeout_branch': child_at_timeout,
            'worker_done_before_external_reap': worker_done_before_reap,
            'reap': reaped,
            'same_pgid_as_probe': c['pgid'] == p['pgid'],
            'different_session_from_probe': c['sid'] != p['sid'],
            'child_absent_final': stat(c['pid']) is None,
        }
        return out


if __name__ == '__main__':
    a = run_case('same-group', detach=False, sleep_seconds=60)
    print(json.dumps(a, sort_keys=True), flush=True)
    assert a.get('same_pgid_as_probe') is True
    assert a.get('record_error') == 'probe timed out after 1.0s'
    assert a.get('record_passed') is False
    assert a.get('child_absent_final') is True
    b = run_case('detached-session', detach=True, sleep_seconds=60)
    print(json.dumps(b, sort_keys=True), flush=True)
    assert b.get('different_session_from_probe') is True
    assert b.get('child_state_after_timeout_branch') is not None
    assert b.get('worker_done_before_external_reap') is False
    assert b.get('record_error') == 'probe timed out after 1.0s'
    assert b.get('record_passed') is False
    assert b.get('child_absent_final') is True
    print(json.dumps({'assay': 'PASS'}, sort_keys=True))
```

# Verification gaps and safety

- `xd://lsp` is not mounted (`read` returned `No such tool: xd://lsp`). References, definitions and diagnostics could not be requested. Line citations above are direct source inspection, not semantic LSP proof.
- The controlled assay is specifically a `grade()` call with the timeout argument shortened to 1 second; it follows the delivered default branch exactly but does not wait 30 seconds. The independent canonical F17 and checker-selftest evidence above cover the production timeout path. No new mutant or broad survivor sweep was run.
- An exploratory direct `python3 check.py --selftest --json` run also returned exit 0 and `selftest.passed: true`, but its captured 72-row matrix output was not retained. It bound sequential loopback stub sockets through port 0; the selected ports were not logged in that wrapper, so this run is not used as the protected-port safety proof. The controlled assay monkeypatches `bind_closed_port` to return 0 without opening a socket. Afterward, the seat-process `/proc` scan returned `seat_process_matches: []`; `ss -H -ltnp '( sport = :8080 or sport = :34113 )'` returned no rows. No service was started; no fixed consumer port was explicitly addressed or contacted.
- Clone target was `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. Reviewed artifacts: `check.py` SHA-256 `12367de62efafa02641c4acb497e50f1be5019b54879a9ac6da13efd5f8071a5`; `fault-controls.py` SHA-256 `58dac1f71346734532bddc60a2d20f95f640406e924b1aec00a0b750feed072a`; `c2/survivors.py` SHA-256 `87cad1cad4565be01ce06e7f92c578c2f449c951894a880166040c3f118dc3ac`. Python was 3.14.8.
- No tools or packages installed or updated. No model/runtime was invoked; no canonical-runtime, identity-rerouting, or saturation claim was tested.
- Only this report was written to the lane. The clone and all seat scratch were removed after recording this report.
