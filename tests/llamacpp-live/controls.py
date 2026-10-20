#!/usr/bin/env python3
"""controls.py — C2 counting command for the kama-llamacpp-live harness.

Runs the lifecycle tool (tools/kama-llamacpp-live.py, or a staged/frozen copy)
against a generated fake llama-server and then runs the receipt gate
(tests/llamacpp-live/check-receipt.py) on whatever receipt the tool wrote.
K0 is a documented-behaviour server that MUST be accepted; K1-K8 each corrupt
exactly one behaviour or fault and MUST be rejected via the check that grades
that specific misbehaviour. A bad control that is accepted — or that crashes
the harness without a receipt — is an ACCEPTED-BAD defect. A run that is
rejected by a check other than the targeted one is INCONCLUSIVE (reported
separately, never counted as detection).

    controls.py --tool PATH --gate PATH [--probe PATH] [--json] [--only ID]

Arms:
* primary: tool exit + receipt checks + gate exit per control.
* gate-flip: for every bad control whose receipt records failing checks, a
  copy of that receipt with only the failing checks' ``passed`` flipped to
  true is re-run through the gate, which MUST still reject it (the gate
  re-derives checks from the stored evidence). Gate acceptance of a doctored
  receipt is counted in ``gate_flip_bad``.
* attribution: ``expected_failed`` per control is a list of lowercase check-id
  substrings (tokens, not exact ids, so the same expectation survives check
  renames between receipt versions). A rejected run whose failed checks do
  not cover the token set is ``inconclusive``.

Exit: 0 iff accepted_bad == 0, gate_flip_bad == 0, inconclusive == 0 and the
good control was accepted; 1 otherwise; 2 on a fault in this script itself.

Design notes
------------
* The tool resolves its registry as <tool-dir>/../registry/endpoint-
  consumers.tsv and hashes every regular file beside --server. Every run
  therefore stages a mini lane layout inside a TemporaryDirectory:
  work/lane/tools/<tool-basename>, work/lane/registry/endpoint-consumers.tsv,
  work/srv/fake_server.py (the only file in srv/). This is what makes the
  same command work verbatim against the round-17 frozen copies.
* The fake server is a generated stdlib script that parses the argv the tool
  passes (-m, --alias, --host, --port, -c, -t are read; unknown flags are
  ignored) and serves a behaviour shape baked in at generation time (the
  tool's child env allowlist would strip any env-var shape selector). It
  writes its pid to work/srv/fake.pid after launch; the pid file is created
  after the tool's install_tree hash, so the recorded tree only ever contains
  fake_server.py. Cleanup verifies /proc/<pid>/cmdline names that exact fake
  path, then kills the process GROUP (the tool uses start_new_session, so the
  fake's pgid == its pid) — a control can never leave a listener behind.
* Every serving fake answers >=3 loading 503s (exact llama.cpp envelope on
  /v1/models, plus the first /health poll) before going ready, so the v2
  loading-envelope checks have real evidence on the good control too.
* K6 runs the tool in-process inside a child ``python3 -c`` wrapper
  (importlib exec + ``teardown`` monkeypatched to raise; a fired-flag proves
  the patch landed), never in this process — the v1 tool would otherwise
  leave SIGINT/SIGTERM ignored here when its KeyError skips the handler
  restore. A surviving fake is reaped by its pdeathsig on wrapper exit and
  by the pgid kill regardless.
* TMPDIR is pointed at each control's workdir so the tool's own mkstemp log
  lands inside the sandbox.

Ports: none are bound by this script; the tool itself picks a free
unregistered ephemeral port (its refused-port logic excludes 8080, 34113 and
every port token in the staged registry copy).

Deps: python3 stdlib; the fake serves only what the tool and kama-probe.sh
(curl) request.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

SCHEMA = 'kama-live-controls/v1'
LANE = Path(__file__).resolve().parents[2]
REGISTRY_SRC = LANE / 'registry' / 'endpoint-consumers.tsv'
DEFAULT_PROBE = LANE / 'tools' / 'kama-probe.sh'

ALIAS = 'fakealias'
MODEL_BYTES = bytes(range(32))
TOOL_TIMEOUT = 180.0   # >= TERM_GRACE(10)+SIGKILL wait(5)+probe budget; L1: >=180
GATE_TIMEOUT = 60.0


# ---------------------------------------------------------------- fake server

# Tokens %%SHAPE%% and %%PIDFILE%% are substituted per control. The fake parses
# the same argv the tool builds for llama-server; anything unknown is ignored.
FAKE_TEMPLATE = r'''#!/usr/bin/env python3
"""Generated fake llama-server for tests/llamacpp-live/controls.py."""
import json
import os
import signal
import socket
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

SHAPE = '%%SHAPE%%'
PIDFILE = '%%PIDFILE%%'
STATE = {'models': 0, 'health': 0, 'probe_models': 0}


def _val(flag, default=None):
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == flag and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith(flag + '='):
            return a.split('=', 1)[1]
    return default


PORT = int(_val('--port', '0') or 0)
ALIAS = _val('--alias', 'fakealias')
# -m/--host/-c/-t/--no-webui/--offline are accepted and ignored deliberately.
_ = (_val('-m'), _val('--host'), _val('-c'), _val('-t'))


def _write_pidfile():
    try:
        with open(PIDFILE, 'w', encoding='ascii') as fh:
            fh.write(str(os.getpid()) + '\n')
    except OSError:
        pass


def _term_exit0(_signum, _frame):
    os._exit(0)


def _term_exit1(_signum, _frame):
    os._exit(1)


if SHAPE == 'k4':
    signal.signal(signal.SIGTERM, signal.SIG_IGN)   # must be SIGKILLed
elif SHAPE == 'k5':
    signal.signal(signal.SIGTERM, _term_exit1)      # dies rc 1 on SIGTERM
elif SHAPE == 'k8':
    pass                                            # default disposition: -15
else:
    signal.signal(signal.SIGTERM, _term_exit0)      # graceful exit 0

if SHAPE == 'k7':
    # Listens, never answers: raw accept backlog, no accept() at all.
    signal.signal(signal.SIGTERM, _term_exit0)
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind(('127.0.0.1', PORT))
    lsock.listen(16)
    _write_pidfile()
    while True:
        signal.pause()

GOOD_ENVELOPE = {'error': {'message': 'Loading model',
                           'type': 'unavailable_error', 'code': 503}}
BAD_ENVELOPE = {'error': {'message': 'Busy', 'type': 'unavailable_error',
                          'code': '503'}}
LOADING = {'/v1/models': 3, '/health': 1}  # loading 503s per path before ready
MODELS_OK = {'object': 'list', 'data': [
    {'id': ALIAS, 'object': 'model', 'created': 0, 'owned_by': 'llamacpp'}]}
PROPS = {'model_alias': ALIAS, 'total_slots': 1, 'is_sleeping': False,
         'build_info': 'controls-fake', 'default_generation_settings':
         {'n_ctx': 256}}


def _envelope():
    return BAD_ENVELOPE if SHAPE == 'k2' else GOOD_ENVELOPE


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    server_version = 'llama.cpp'
    sys_version = ''

    def version_string(self):
        return 'llama.cpp'

    def log_message(self, fmt, *args):
        try:
            sys.stderr.write('fake ' + (fmt % args) + '\n')
            sys.stderr.flush()
        except OSError:
            pass

    def _send(self, code, obj):
        body = json.dumps(obj, separators=(',', ':')).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def _loading(self, path, hits):
        """Still inside the scripted loading window? -> 503 envelope."""
        if hits < LOADING.get(path, 0):
            return _envelope()
        return None

    def do_GET(self):
        path = self.path.split('?', 1)[0].split('#', 1)[0]
        ua = self.headers.get('User-Agent') or ''
        if path == '/v1/models':
            env = self._loading(path, STATE['models'])
            STATE['models'] += 1
            if env is not None:
                return self._send(503, env)
            if 'curl' in ua:
                STATE['probe_models'] += 1
            self._send(200, MODELS_OK)
            # k3: exit rc 0 on our own, right after the second probe run's
            # /v1/models has been fully flushed — i.e. after the harness's
            # probe captures are served, before its teardown starts.
            if SHAPE == 'k3' and 'curl' in ua \
                    and STATE['probe_models'] >= 2:
                os._exit(0)
            return
        if path == '/health':
            env = self._loading(path, STATE['health'])
            STATE['health'] += 1
            if env is not None:
                return self._send(503, env)
            status = 'degraded' if SHAPE == 'k1' else 'ok'
            return self._send(200, {'status': status})
        if path == '/props':
            return self._send(200, PROPS)
        if path == '/slots':
            return self._send(200, [{'id': 0, 'state': 0}])
        if path == '/metrics':
            return self._send(501, {'error': {
                'message': 'metrics not enabled',
                'type': 'unavailable_error', 'code': 501}})
        return self._send(404, {'error': {
            'message': 'not found', 'type': 'not_found_error', 'code': 404}})


HTTPServer.allow_reuse_address = True
_httpd = HTTPServer(('127.0.0.1', PORT), Handler)
_write_pidfile()
_httpd.serve_forever()
'''


# K6: run the tool in-process inside a child wrapper so a teardown fault that
# escapes the tool's own handlers cannot corrupt this controls process (the v1
# tool leaves SIGINT/SIGTERM/SIGHUP ignored when its KeyError skips restore).
# importlib exec (not runpy.run_path) so the module is fully defined before the
# patch lands and its __main__ guard never runs main() under us. The patched
# teardown writes a fired-flag before raising so K6 cannot pass vacuously when
# the patch silently missed. A surviving fake dies via pdeathsig on wrapper
# exit plus the caller's pgid kill. Exits 4 on an unhandled escape.
K6_WRAPPER = r'''
import importlib.util
import sys
import traceback

flag_path = sys.argv[1]
tool = sys.argv[2]
tool_args = sys.argv[3:]
spec = importlib.util.spec_from_file_location('kama_live_under_test', tool)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def _boom(*a, **k):
    try:
        with open(flag_path, 'w', encoding='ascii') as fh:
            fh.write('fired\n')
    except OSError:
        pass
    raise RuntimeError('controls-k6: injected teardown fault')

mod.teardown = _boom
sys.argv = [tool] + tool_args
try:
    rc = mod.main()
except BaseException:
    traceback.print_exc()
    rc = 4
sys.exit(rc if isinstance(rc, int) else 2)
'''


class ControlsFault(Exception):
    """This suite's own machinery failed; mapped to exit 2, never a verdict."""


# ------------------------------------------------------------------ controls

# id -> (shape, extra tool argv, run via K6 wrapper, expected failed-check-id
#        substrings (lowercase; empty = no check-level grading expected),
#        description)
CONTROLS = {
    'k0': ('k0', [], False, [],
           'good: >=3 exact loading 503s on /v1/models and /health, then '
           'documented ready surfaces; SIGTERM handler exits 0; MUST be '
           'accepted'),
    'k1': ('k1', [], False, ['health'],
           'health-degraded: /health 200 {"status":"degraded"} after loading'),
    'k2': ('k2', [], False, ['loading', 'envelope'],
           'loading-bad-envelope: 3x /v1/models + 1x /health 503 with '
           'message "Busy" and string code "503", then ready'),
    'k3': ('k3', [], False, ['teardown'],
           'self-exit: exits rc 0 itself right after the probe captures, '
           'before teardown'),
    'k4': ('k4', [], False, ['teardown', 'sigkill', 'kill',
                             'graceful'],
           'ignores-SIGTERM: requires the harness SIGKILL escalation'),
    'k5': ('k5', [], False, ['teardown', 'graceful', 'signal',
                            'returncode', 'exit_status'],
           'exits rc 1 on SIGTERM'),
    'k6': ('k0', [], True, ['teardown', 'fault'],
           'teardown-fault: tool teardown() monkeypatched to raise '
           'RuntimeError; receipt must still be written, exit 2'),
    'k7': ('k7', ['--ready-timeout', '2'], False, [],
           'hang: listens, never answers (bounded by --ready-timeout 2)'),
    'k8': ('k8', [], False, ['teardown', 'graceful', 'signal',
                            'returncode', 'exit_status'],
           'default SIGTERM disposition: killed by signal (rc -15)'),
}
TEARDOWN_TOKENS = ('teardown', 'sigterm', 'sigkill', 'graceful')
ALL_IDS = tuple(CONTROLS)


def sha256_text(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def _fake_source(shape, pidfile):
    return (FAKE_TEMPLATE
            .replace('%%SHAPE%%', shape)
            .replace('%%PIDFILE%%', str(pidfile)))


def _kill_fake(srvdir):
    """Kill the fake's process GROUP. The tool uses start_new_session, so the
    fake's pgid == its pid; /proc/<pid>/cmdline must name this exact fake
    script before any signal is sent (pid-reuse guard)."""
    pidfile = Path(srvdir) / 'fake.pid'
    fake = Path(srvdir) / 'fake_server.py'
    try:
        pid = int(pidfile.read_text(encoding='ascii').strip())
    except (OSError, ValueError):
        return
    if pid <= 0:
        return
    try:
        with open(f'/proc/{pid}/cmdline', 'rb') as fh:
            cmdline = fh.read().decode('utf-8', 'replace')
    except OSError:
        return  # already gone
    if str(fake) not in cmdline:
        return  # not our fake (pid reused); do not signal
    try:
        os.killpg(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            pass


def _stage_control(root, cid, shape, tool):
    """Per-control sandbox: mini lane layout + fake dir + model + receipt."""
    wd = Path(root) / cid
    srv = wd / 'srv'
    tools_dir = wd / 'lane' / 'tools'
    registry_dir = wd / 'lane' / 'registry'
    for d in (srv, tools_dir, registry_dir):
        d.mkdir(parents=True, exist_ok=True)

    staged_tool = tools_dir / Path(tool).name
    shutil.copyfile(tool, staged_tool)
    os.chmod(staged_tool, 0o755)
    if REGISTRY_SRC.is_file():
        shutil.copyfile(REGISTRY_SRC, registry_dir / 'endpoint-consumers.tsv')
    else:
        (registry_dir / 'endpoint-consumers.tsv').write_text(
            '# staged empty registry for controls\n', encoding='utf-8')

    fake = srv / 'fake_server.py'
    fake.write_text(_fake_source(shape, srv / 'fake.pid'), encoding='utf-8')
    os.chmod(fake, 0o755)

    model = wd / 'model.gguf'
    model.write_bytes(MODEL_BYTES)
    return {
        'wd': wd, 'srv': srv, 'fake': fake, 'model': model,
        'staged_tool': staged_tool,
        'model_sha': hashlib.sha256(MODEL_BYTES).hexdigest(),
        'receipt': wd / 'receipt.json',
    }


def _tool_argv(st, probe, extra):
    return [
        str(st['staged_tool']),
        '--server', str(st['fake']),
        '--model', str(st['model']),
        '--model-sha256', st['model_sha'],
        '--alias', ALIAS,
        '--probe', str(probe),
        '--out', str(st['receipt']),
    ] + list(extra)


def _read_receipt(path):
    """(doc|None, file_exists). A file that exists but cannot be read or
    parsed still counts as written (the tool emitted bytes) but its checks
    are ungradeable, recorded as <receipt-unparseable>."""
    if not os.path.isfile(path):
        return None, False
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh), True
    except (OSError, ValueError):
        return None, True


def _failed_checks(doc):
    out = []
    checks = doc.get('checks') if isinstance(doc, dict) else None
    if isinstance(checks, list):
        for c in checks:
            if isinstance(c, dict) and c.get('passed') is False:
                out.append(str(c.get('id')))
    return out


def _teardown_ok(doc):
    """None: no teardown-ish check in the receipt. Else all(passed) over
    checks whose id carries a teardown token."""
    checks = doc.get('checks') if isinstance(doc, dict) else None
    vals = []
    if isinstance(checks, list):
        for c in checks:
            cid = str(c.get('id', '')).lower() if isinstance(c, dict) else ''
            if any(t in cid for t in TEARDOWN_TOKENS):
                vals.append(bool(c.get('passed')))
    return all(vals) if vals else None


def _attributed(failed, expected):
    """True when expected tokens exist and at least one token appears in the
    recorded failed-check ids; None when no attribution is expected."""
    if not expected:
        return None
    low = [f.lower() for f in failed]
    return any(tok in fid for tok in expected for fid in low)


def _gate_flip(st, gate, receipt_doc, failed):
    """Gate-only arm: flip only the failing checks' passed->true and require
    the gate to still reject (it re-derives checks from stored evidence).
    Returns {'exit','rejected','accepted'} or None when not applicable."""
    if not failed:
        return None
    flip = copy.deepcopy(receipt_doc)
    flipped = 0
    for c in flip.get('checks') or []:
        if isinstance(c, dict) and c.get('passed') is False:
            c['passed'] = True
            flipped += 1
    if not flipped:
        return None
    flip_path = st['wd'] / 'receipt-flipped.json'
    flip_path.write_text(json.dumps(flip, indent=2, sort_keys=True) + '\n',
                         encoding='utf-8')
    try:
        gp = subprocess.run(
            [sys.executable, str(gate), str(flip_path)],
            capture_output=True, text=True, timeout=GATE_TIMEOUT)
        rc = gp.returncode
    except subprocess.TimeoutExpired:
        rc = None
    return {'exit': rc, 'rejected': rc == 1,
            'accepted': rc == 0, 'flipped': flipped,
            # non-null means the gate could reject on setup_error alone, so
            # this arm does not isolate check re-derivation for this receipt
            'receipt_setup_error': receipt_doc.get('setup_error')}


def run_control(root, cid, tool, gate, probe):
    shape, extra, inprocess, expected, _desc = CONTROLS[cid]
    st = _stage_control(root, cid, shape, tool)
    env = dict(os.environ)
    env['TMPDIR'] = str(st['wd'])

    argv = _tool_argv(st, probe, extra)
    k6_flag = st['wd'] / 'k6.fired'
    if inprocess:
        cmd = [sys.executable, '-B', '-c', K6_WRAPPER, str(k6_flag)] + argv
    else:
        cmd = [sys.executable] + argv

    tool_exit = None
    tool_stderr_tail = ''
    tool_timed_out = False
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True,
                            timeout=TOOL_TIMEOUT, env=env,
                            cwd=str(st['wd']))
        tool_exit = cp.returncode
        tool_stderr_tail = (cp.stderr or '')[-2000:]
    except subprocess.TimeoutExpired as exc:
        tool_timed_out = True
        tool_stderr_tail = (exc.stderr or '')[-2000:] \
            if isinstance(exc.stderr, str) else ''
    finally:
        _kill_fake(st['srv'])

    doc, receipt_written = _read_receipt(st['receipt'])
    receipt_doc = doc if isinstance(doc, dict) else None
    if inprocess and not k6_flag.is_file() and receipt_written:
        # The run reached a receipt without the patched teardown firing: the
        # patch missed (renamed/indirect call) and K6 would grade real
        # teardown. A missing receipt is an escape instead, counted below.
        raise ControlsFault(
            f'k6: patched teardown never fired under {st["staged_tool"]}')

    gate_exit = None
    if receipt_written:
        try:
            gp = subprocess.run(
                [sys.executable, str(gate), str(st['receipt'])],
                capture_output=True, text=True, timeout=GATE_TIMEOUT)
            gate_exit = gp.returncode
        except subprocess.TimeoutExpired:
            gate_exit = None

    escaped = not receipt_written
    failed = _failed_checks(receipt_doc) if receipt_doc else []
    if receipt_written and receipt_doc is None:
        failed.append('<receipt-unparseable>')
    if tool_timed_out:
        failed.append('<tool-timeout>')
    td_ok = _teardown_ok(receipt_doc)
    attributed = _attributed(failed, expected)

    if cid == 'k0':
        accepted = (tool_exit == 0 and gate_exit == 0
                    and not escaped and not tool_timed_out)
        rejected = not accepted
        inconclusive = False
    else:
        base = (receipt_written and not tool_timed_out
                and (tool_exit != 0 or (gate_exit is not None
                                        and gate_exit != 0)))
        if cid == 'k6':
            # contract: receipt written on the internal fault, exit 2; accept
            # any nonzero+receipt as a rejection, record the exact exit.
            rejected = receipt_written and tool_exit not in (0, None)
        else:
            rejected = base
        accepted = not rejected
        # L1 decision 4: a rejected run whose failed checks do not cover the
        # expected tokens is inconclusive (rejected for the wrong reason),
        # never counted as detection.
        inconclusive = bool(rejected and attributed is False)

    gate_flip = None
    if cid != 'k0' and receipt_doc is not None:
        gate_flip = _gate_flip(st, gate, receipt_doc, failed)

    return {
        'id': cid,
        'tool_exit': tool_exit,
        'gate_exit': gate_exit,
        'receipt_written': receipt_written,
        'failed_checks': failed,
        'expected_failed': expected,
        'attributed': attributed,
        'inconclusive': inconclusive,
        'accepted': accepted,
        'rejected': rejected,
        'escaped': escaped,
        'teardown_ok': td_ok,
        'gate_flip': gate_flip,
        'tool_stderr_tail': tool_stderr_tail[-400:] or None,
    }


def _print_human(rows, result, selected):
    for r in rows:
        if r['id'] == 'k0':
            verdict = 'GOOD-OK' if r['accepted'] else 'GOOD-REJECTED'
        elif r['accepted']:
            verdict = 'ACCEPTED-BAD'
        elif r['inconclusive']:
            verdict = 'INCONCLUSIVE'
        else:
            verdict = 'rejected'
        esc = ' ESCAPED' if r['escaped'] else ''
        td = '' if r['teardown_ok'] is None else \
            f" teardown_ok={r['teardown_ok']}"
        gf = ''
        if r['gate_flip'] is not None:
            gf = (' gate_flip=REJECTED' if r['gate_flip']['rejected']
                  else ' gate_flip=ACCEPTED!')
        att = '' if r['attributed'] is None else f" attributed={r['attributed']}"
        print(f"{r['id']:<3} tool={r['tool_exit']!s:<5} "
              f"gate={r['gate_exit']!s:<5} "
              f"receipt={'yes' if r['receipt_written'] else 'NO '}"
              f"{esc}{td}{att}{gf} failed={r['failed_checks']} -> {verdict}")
    print(f"controls: {', '.join(selected)}; "
          f"accepted_bad={result['accepted_bad']} "
          f"gate_flip_bad={result['gate_flip_bad']} "
          f"inconclusive={result['inconclusive']} "
          f"good_ok={result['good_ok']}")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description='C2 accepted-bad control counter for '
                    'kama-llamacpp-live + check-receipt.')
    ap.add_argument('--tool', required=True,
                    help='kama-llamacpp-live.py (or a frozen copy) to grade')
    ap.add_argument('--gate', required=True,
                    help='check-receipt.py (or a frozen copy) to grade')
    ap.add_argument('--probe', default=None,
                    help=f'kama-probe.sh (default: {DEFAULT_PROBE})')
    ap.add_argument('--json', action='store_true',
                    help='print only the JSON result object')
    ap.add_argument('--only', choices=ALL_IDS, default=None,
                    help='run a single control (good_ok ignored when k0 '
                         'is not selected)')
    args = ap.parse_args(argv)

    for label, path in (('tool', args.tool), ('gate', args.gate),
                        ('probe', args.probe or DEFAULT_PROBE)):
        if not os.path.isfile(path):
            print(f'controls: {label} not found: {path}', file=sys.stderr)
            return 2
    probe = os.path.realpath(args.probe or DEFAULT_PROBE)

    result = {
        'schema': SCHEMA,
        'tool_sha256': sha256_text(args.tool),
        'gate_sha256': sha256_text(args.gate),
        'controls': [],
        'accepted_bad': 0,
        'gate_flip_bad': 0,
        'inconclusive': 0,
        'good_ok': True,
    }

    selected = (args.only,) if args.only else ALL_IDS
    try:
        with tempfile.TemporaryDirectory(
                prefix='kama-live-controls-') as root:
            for cid in selected:
                try:
                    row = run_control(root, cid, args.tool, args.gate, probe)
                finally:
                    # belt-and-braces: kill any fake that outlived its run
                    _kill_fake(Path(root) / cid / 'srv')
                result['controls'].append(row)
                if row['id'] == 'k0':
                    result['good_ok'] = bool(row['accepted'])
                else:
                    if row['accepted']:
                        result['accepted_bad'] += 1
                    if row['inconclusive']:
                        result['inconclusive'] += 1
                    if row['gate_flip'] is not None \
                            and row['gate_flip']['accepted']:
                        result['gate_flip_bad'] += 1
    except Exception as exc:
        print(f'controls: own fault: {type(exc).__name__}: {exc}',
              file=sys.stderr)
        return 2

    if 'k0' not in selected:
        result['good_ok'] = None  # not measured under --only

    clean = (result['accepted_bad'] == 0
             and result['gate_flip_bad'] == 0
             and result['inconclusive'] == 0)
    good_ok = bool(result['good_ok']) if result['good_ok'] is not None \
        else True
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        _print_human(result['controls'], result, selected)
    return 0 if (clean and good_ok) else 1


if __name__ == '__main__':
    sys.exit(main())
