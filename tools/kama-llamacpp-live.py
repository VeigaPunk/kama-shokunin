#!/usr/bin/env python3
"""kama-llamacpp-live.py — ephemeral lane-owned llama.cpp server lifecycle harness.

Domain: local model serving & endpoint health (kama-shokunin). Capability
acquisition tool: it launches a caller-selected ``llama-server`` against a
digest-pinned GGUF on a free loopback port that is never a registered consumer
port, captures the documented HTTP lifecycle surfaces (loading -> ready),
runs ``tools/kama-probe.sh`` against it twice (matching and mismatched
``--expect``), then tears the server down and proves the teardown.

It is deliberately lane-owned and ephemeral: no ~/.config, ~/.omp, systemd or
service writes; the only filesystem artifacts are a temp stdout/stderr log
(deleted after the interesting lines are copied into the receipt) and the
optional ``--out`` receipt file.

Exit codes:
    0  every check passed
    1  at least one check failed (server ran; receipt written)
    2  setup error (missing binary/model, launch failure, ready timeout,
       terminated by signal, receipt write failure)
Receipt schema: ``kama-llamacpp-live/v2``. Only argv is recorded from the
launch environment — never env. Any exception in teardown or the finally
block still writes a receipt with ``setup_error`` ``internal:<ExcType>``
and exit 2 — never an escaped traceback without a receipt.

Deps: python3 stdlib only, plus whatever the probed server and
``bash tools/kama-probe.sh`` (curl, ss) need.
"""
from __future__ import annotations

import argparse
import http.client
import hashlib
import json
import os
import re
import shutil
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = 'kama-llamacpp-live/v2'
SCRIPT = Path(__file__).resolve()
LANE = SCRIPT.parent.parent
REGISTRY = LANE / 'registry' / 'endpoint-consumers.tsv'
DEFAULT_PROBE = LANE / 'tools' / 'kama-probe.sh'

# Pinned upstream evidence for the sourced predicates (b11755).
LLAMA_COMMIT = '704366d76f8748cf9ad3df62a464bfcc8d1ae6ad'
_LLAMA_RAW = ('https://raw.githubusercontent.com/ggml-org/llama.cpp/'
              + LLAMA_COMMIT + '/tools/server/')
POPEN_RETURNCODE_DOC = ('https://docs.python.org/3/library/subprocess.html'
                        '#subprocess.Popen.returncode')
# The exact JSON document a ready /health must answer (object equality;
# a 200 with {"status":"degraded"} is not ready).
HEALTH_READY_BODY = {'status': 'ok'}

# Ports that must never be served even if the OS offers them: the two known
# consumer pins plus anything the registry TSV names (parsed at runtime).
HARD_REFUSED_PORTS = {8080, 34113}
PORT_PICK_ATTEMPTS = 64

POLL_TIMEOUT = 0.5          # per-request readiness poll timeout, seconds
PROBE_TIMEOUT = 60          # seconds per kama-probe.sh invocation
TERM_GRACE = 10.0           # SIGTERM grace before SIGKILL
TRANSITION_BODY_CAP = 4096  # verbatim body kept on lifecycle transitions
LOADING_BODY_MAX = 256      # distinct loading-503 bodies kept verbatim
CAPTURE_BODY_CAP = 65536    # verbatim body kept on ready captures (= read cap)
LOG_KEEP = re.compile(r'build|model loaded|listening|loading', re.IGNORECASE)
HTTP_BODY_CAP = 65536       # max bytes read per response (R3)
LOG_TAIL_CAP = 65536        # only the last bytes of the temp log are kept
LOG_KEEP_MAX = 200          # copied log lines before truncation flag
MISMATCH_EXPECT = 'kama-not-this-model'
# Child process environment allowlist: the server sees only these names when
# present in the harness env — names are recorded, values never are.
CHILD_ENV_KEYS = ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')


# Documentation anchors for the checks array (llama.cpp b11755).
DOC = {
    'health_ready': (
        'llama.cpp ' + _LLAMA_RAW + 'server-context.cpp L5288-5299: '
        'get_health answers res->ok({{"status","ok"}}); a 200 with any '
        'other body (e.g. {"status":"degraded"}) is not ready'
    ),
    'models_alias_id': (
        'llama.cpp tools/server README @ b11755 GET /v1/models: '
        'OpenAI-compatible list whose data[].id is the --alias value'
    ),
    'models_owned_by_llamacpp': (
        'llama.cpp server b11755 /v1/models emits owned_by "llamacpp" '
        '(observed by L1 smoke 2026-10-20: data[0].owned_by == "llamacpp")'
    ),
    'metrics_not_enabled': (
        'llama.cpp tools/server README @ b11755: GET /metrics requires the '
        '--metrics flag; without it the endpoint answers exactly 501'
    ),
    'props_alias': (
        'llama.cpp server /props returns model_alias equal to the --alias '
        'value (server_params -> props endpoint, b11755)'
    ),
    'probe_model_ok': (
        'tools/kama-probe.sh classify() contract: matching served id -> '
        'MODEL_OK reason "matched", exit 0'
    ),
    'probe_mismatch': (
        'tools/kama-probe.sh classify() contract: non-matching served id -> '
        'MODEL_MISMATCH reason "served-id-mismatch", exit 2'
    ),
    'teardown_graceful': (
        'llama.cpp ' + _LLAMA_RAW + 'server.cpp L529-534 installs '
        'signal_handler for SIGTERM, L519-523 shutdown_handler calls '
        'ctx_server.terminate(), L575-590 start_loop() unblocks and '
        'llama_server returns 0 — the documented graceful exit status; '
        'per ' + POPEN_RETURNCODE_DOC + ' a negative returncode means '
        'the child was terminated by that signal and fails; the "0" '
        'grounds on this shutdown code path plus the round-16 observed '
        'receipt (returncode 0, 3 ms), not on the Python row alone. '
        'Also requires port_listener_ownership == "child" proven before '
        'teardown, i.e. harness-initiated on our own child'
    ),
    'teardown_port_closed': (
        'lane ownership: passes only when the port was proven owned by '
        'our child earlier in this run (port_listener_ownership '
        '"child") AND refuses connections after teardown; vacuous '
        'otherwise -> fail'
    ),
    'loading_envelope_graded': (
        'llama.cpp ' + _LLAMA_RAW + 'server-http.cpp L314-325: while '
        'is_ready is false every non-frontend path answers 503 '
        '{"error":{"message":"Loading model","type":"unavailable_error"'
        ',"code":503}}. Grades EVERY distinct captured 503 body; no 503 '
        'observed -> fail with {"loading_observed": false} (a real '
        'b11755 run shows dozens). Limit: bodies are deduped by sha256 '
        'and capped at LOADING_BODY_MAX, so identical repeats are '
        'graded once'
    ),
    'model_unchanged': (
        'lane input integrity, not subject behaviour: the GGUF must '
        'hash identically after teardown; only external mutation can '
        'flip it'
    ),
}


class SetupError(Exception):
    """Fatal pre-check failure; mapped to exit 2 with a stable reason token."""

    def __init__(self, code):
        super().__init__(code)
        self.code = code


class Terminated(Exception):
    """SIGINT/SIGTERM/SIGHUP delivered mid-run; teardown still runs."""


def _utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace(
        '+00:00', 'Z')


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def install_tree(server_real):
    """{basename: sha256} for every regular file in dirname(server_real),
    plus a combined digest over the sorted 'name sha' lines. Symlinks are
    skipped as members (they are not regular files)."""
    tree = {}
    directory = os.path.dirname(server_real)
    try:
        entries = sorted(os.listdir(directory))
    except OSError:
        return tree, None
    for name in entries:
        full = os.path.join(directory, name)
        try:
            st = os.lstat(full)
        except OSError:
            continue
        if not stat.S_ISREG(st.st_mode):
            continue
        try:
            tree[name] = sha256_file(full)
        except OSError:
            continue
    combined = hashlib.sha256(
        ''.join(f'{n} {tree[n]}\n' for n in sorted(tree)).encode()).hexdigest()
    return tree, combined


def _envelope_ok(body_text):
    """True iff one loading-503 body parses to the documented envelope:
    error.message=="Loading model", error.type=="unavailable_error",
    error.code is int and ==503."""
    try:
        doc = json.loads(body_text or '')
    except (ValueError, TypeError):
        return False
    err = doc.get('error') if isinstance(doc, dict) else None
    if not isinstance(err, dict):
        return False
    code = err.get('code')
    return (err.get('message') == 'Loading model'
            and err.get('type') == 'unavailable_error'
            and type(code) is int and code == 503)


def loading_envelope_exact(loading_503):
    """Envelope grade of the first captured 503 body (receipt field
    loading_envelope_exact): True/False, or None when no 503 was seen.
    Not a check."""
    if loading_503 is None:
        return None
    return _envelope_ok(loading_503.get('body'))


def loading_envelopes_all(bodies):
    """True iff every distinct captured 503 body is the exact envelope;
    None when no body was captured. Grounds loading_envelope_graded."""
    if not bodies:
        return None
    return all(_envelope_ok(b.get('body')) for b in bodies)


class _BodyLog(list):
    """Distinct loading-503 bodies, plus the count dropped past
    LOADING_BODY_MAX so coverage limits are recorded, never hidden.
    Serializes as a plain JSON array."""
    dropped = 0


def refused_ports():
    """Ports we must never serve: hardcoded pins + every port token the
    registry TSV expresses (host:port, --port N, port=N markers; a bare digit
    run like 'Qwen3-Coder-30B' is never a port)."""
    refused = set(HARD_REFUSED_PORTS)
    try:
        text = REGISTRY.read_text(encoding='utf-8', errors='replace')
    except OSError:
        raise SetupError(f'registry-unreadable:{REGISTRY}')
    patterns = (
        r'(?:\d{1,3}\.){3}\d{1,3}:(\d{1,5})',
        r'localhost:(\d{1,5})',
        r'\[?::1\]?:?(\d{1,5})\b',  # only inside a URL-ish context; still guarded by range check
        r'--port[ =](\d{1,5})',
        r'\bport=(\d{1,5})',
        r'\bhost:(\d{1,5})',
    )
    for pat in patterns:
        for m in re.finditer(pat, text):
            try:
                n = int(m.group(1))
            except ValueError:
                continue
            if 1 <= n <= 65535:
                refused.add(n)
    return refused



def pick_port(refused, requested=None):
    """Select the serve port.

    Explicit --port: must clear the refused set AND refuse connections now
    (a live listener means the port is already in use). This is the only
    path that can exercise a refusal of a sub-ephemeral port like 8080 —
    the kernel's bind(:0) range is 32768-60999, so 34113 CAN be offered
    while 8080 cannot (port-gate advice, round 16).

    Default: bind 127.0.0.1:0, take the offered port, release; retry when
    refused. The release/rebind race is documented in the receipt.
    Never pass 0 through to llama-server: it would bind before any refusal
    check could reject a kernel-chosen registered port."""
    if requested is not None:
        if not (1 <= requested <= 65535):
            raise SetupError('explicit-port-out-of-range')
        if requested in refused:
            raise SetupError(f'port-refused-registered:{requested}')
        try:
            socket.create_connection(('127.0.0.1', requested),
                                     timeout=1.0).close()
        except ConnectionRefusedError:
            return requested
        except OSError:
            return requested  # timeout/reset: no proven listener; try anyway
        raise SetupError(f'port-in-use:{requested}')
    for _ in range(PORT_PICK_ATTEMPTS):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('127.0.0.1', 0))
            port = s.getsockname()[1]
        if port not in refused:
            return port
    raise SetupError('no-free-unregistered-port')


def _listen_inodes(port):
    """Socket inodes LISTENing on `port` AND bound to loopback, from
    /proc/net/tcp{,6} (state 0A). Local-address hex column: 127/8 is
    little-endian xxxxx7F? -> the high byte is 7F iff the address is in
    127.0.0.0/8; ::1 ends 00000001; an IPv4-mapped 127/8 is the
    v4-mapped prefix 0000000000000000FFFF00 plus the v4 tail. A child
    bound to 0.0.0.0 or :: still answers loopback connects but is not
    counted as the loopback-port owner — fail-closed."""
    inodes = set()
    for proc_net in ('/proc/net/tcp', '/proc/net/tcp6'):
        try:
            with open(proc_net, encoding='ascii') as fh:
                next(fh, None)
                for line in fh:
                    parts = line.split()
                    if len(parts) < 10 or parts[3] != '0A':
                        continue
                    addr_hex, port_hex = parts[1].rsplit(':', 1)
                    if int(port_hex, 16) != port:
                        continue
                    if proc_net.endswith('tcp6'):
                        if not (addr_hex.endswith('00000001')
                                or (addr_hex[:24]
                                    == '0000000000000000FFFF00'
                                    and addr_hex.endswith('7F'))):
                            continue
                    elif not addr_hex.endswith('7F'):
                        continue
                    inodes.add(parts[9])
        except (OSError, ValueError, IndexError):
            continue
    return inodes

def port_owned_by(pid, port):
    """True: a LISTEN socket on `port` is an fd of `pid` (our child owns it).
    False: listener exists but none of its inodes is in the child's fd table
    (a stranger can satisfy /health before the child's bind failure lands).
    None: no listener yet, or /proc unreadable (ownership unknown)."""
    try:
        inodes = _listen_inodes(port)
        if not inodes:
            return None
        wanted = {f'socket:[{i}]' for i in inodes}
        for fd in os.listdir(f'/proc/{pid}/fd'):
            try:
                if os.readlink(f'/proc/{pid}/fd/{fd}') in wanted:
                    return True
            except OSError:
                continue
        return False
    except OSError:
        return None


def _preexec_pdeathsig():
    """Child-side: die with SIGKILL if the harness parent dies (Linux).
    Outcome is not observable post-close_fds, so the receipt records
    prctl_ok 'unknown' honestly rather than a guessed boolean (F2)."""
    try:
        import ctypes
        libc = ctypes.CDLL(None, use_errno=True)
        libc.prctl(1, signal.SIGKILL, 0, 0, 0)  # PR_SET_PDEATHSIG
        if os.getppid() != _FORKED_PPID[0]:
            os._exit(1)  # parent already gone before prctl landed
    except Exception:  # pragma: no cover - best effort hardening
        pass


_FORKED_PPID = [0]





def _header_subset(headers):
    return {
        'server': headers.get('Server'),
        'content-type': headers.get('Content-Type'),
    }


def http_get(port, path, timeout=POLL_TIMEOUT):
    """One loopback GET. Returns dict(status|None, error|None, headers,
    body, body_truncated). At most HTTP_BODY_CAP+1 bytes are read; the flag
    marks a truncated read. HTTPError is a normal response (status set);
    URLError/socket errors give status=None and an error class name."""
    url = f'http://127.0.0.1:{port}{path}'
    req = urllib.request.Request(url, method='GET')

    def _result(status, headers, raw):
        return {
            'status': status,
            'error': None,
            'headers': dict(headers),
            'body': raw[:HTTP_BODY_CAP],
            'body_truncated': len(raw) > HTTP_BODY_CAP,
        }

    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            return _result(resp.status, resp.headers.items(),
                           resp.read(HTTP_BODY_CAP + 1))
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read(HTTP_BODY_CAP + 1)
        except OSError:
            raw = b''
        return _result(exc.code,
                       exc.headers.items() if exc.headers else {}, raw)
    except urllib.error.URLError as exc:
        reason = getattr(exc, 'reason', exc)
        return {'status': None, 'error': type(reason).__name__,
                'headers': {}, 'body': b'', 'body_truncated': False}
    except (OSError, socket.timeout, TimeoutError) as exc:
        return {'status': None, 'error': type(exc).__name__,
                'headers': {}, 'body': b'', 'body_truncated': False}


def _decode_body(body, cap):
    """Return (text_or_None, truncated_bool); None when body exceeds cap."""
    if len(body) > cap:
        return None, True
    return body.decode('utf-8', errors='replace'), False


def _transition_row(t0, path, result):
    body_text, truncated = _decode_body(result['body'], TRANSITION_BODY_CAP)
    return {
        't_ms': round((time.monotonic() - t0) * 1000),
        'path': path,
        'status': result['status'],
        'error': result['error'],
        'body_sha256': hashlib.sha256(result['body']).hexdigest(),
        'body': body_text,
        'body_read_truncated': result.get('body_truncated', False),
        'body_over_cap': truncated,
        'headers': _header_subset(result['headers']),
        'repeats': 0,
    }


def _sig(row):
    return (row['status'], row['error'], row['body_sha256'])


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """F3: refuse redirects — a 30x must surface as its own status, never
    be followed to a foreign document."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}),
                                      _NoRedirect)


class _KeepAlive:
    """Reused http.client connection for the tight readiness polls.
    Recycled once on transport errors so a server-side close is retried."""

    def __init__(self, port, timeout=POLL_TIMEOUT):
        self.port = port
        self.timeout = timeout
        self.conn = None

    def get(self, path):
        for attempt in range(2):
            try:
                if self.conn is None:
                    self.conn = http.client.HTTPConnection(
                        '127.0.0.1', self.port, timeout=self.timeout)
                self.conn.request('GET', path)
                resp = self.conn.getresponse()
                raw = resp.read(HTTP_BODY_CAP + 1)
                return {'status': resp.status, 'error': None,
                        'headers': dict(resp.getheaders()),
                        'body': raw[:HTTP_BODY_CAP],
                        'body_truncated': len(raw) > HTTP_BODY_CAP}
            except (OSError, http.client.HTTPException) as exc:
                self._close()
                if attempt == 1:
                    return {'status': None, 'error': type(exc).__name__,
                            'headers': {}, 'body': b'',
                            'body_truncated': False}

    def _close(self):
        try:
            if self.conn is not None:
                self.conn.close()
        finally:
            self.conn = None


def readiness_loop(proc, port, ready_timeout):
    """Two-phase lifecycle capture (ExecLoadingWindowCapture design):

    Phase 'models': GET /v1/models on a reused keep-alive connection, NO
    sleep, 0.5 s per-request timeout, until the first non-503 answer — the
    ~5-6 ms loading window needs an unbroken request cadence. The first 503
    is kept verbatim in loading_503, and every distinct 503 body is kept
    in loading_bodies (status, Server/Content-Type, body <=4096, sha256).

    Phase 'health': GET /health the same way until 200.

    D1: the FIRST successful HTTP response (any status) immediately triggers
    port_owned_by(child, port); foreign or unproven ownership discards every
    recorded body and is a setup error — a stranger's loading body can never
    reach loading_503.
    Returns (transitions, loading_503, loading_bodies, ready,
    failure_code, ownership). loading_bodies lists every DISTINCT 503
    body (deduped by sha256, repeats counted, capped) so the graded
    check covers all observed envelopes, not just the first."""
    t0 = time.monotonic()
    deadline = t0 + ready_timeout
    transitions = []
    loading_503 = None
    loading_bodies = _BodyLog()   # every distinct 503 body, {path,
                                  # body_sha256, body, repeats}
    _seen_503 = {}                # body_sha256 -> index into loading_bodies
    ownership = None
    proven = False
    conn = _KeepAlive(port)

    def _observe(phase, path, result):
        nonlocal loading_503, ownership, proven
        row = _transition_row(t0, path, result)
        row['phase'] = phase
        sig = _sig(row)
        if transitions and _sig(transitions[-1]) == sig \
                and transitions[-1]['path'] == path:
            transitions[-1]['repeats'] += 1
            transitions[-1]['t_ms'] = row['t_ms']
        else:
            transitions.append(row)
        if result['status'] is not None and not proven:
            # D1: prove the child owns the listener on first contact
            owned = port_owned_by(proc.pid, port)
            ownership = owned
            if owned is not True:
                return ('port-listener-not-our-child' if owned is False
                        else 'port-listener-ownership-unproven')
            proven = True
        if result['status'] == 503 and proven:
            body_text = result['body'][:TRANSITION_BODY_CAP].decode(
                'utf-8', errors='replace')
            sha = row['body_sha256']
            if sha in _seen_503:
                loading_bodies[_seen_503[sha]]['repeats'] += 1
            elif len(loading_bodies) < LOADING_BODY_MAX:
                _seen_503[sha] = len(loading_bodies)
                loading_bodies.append({'path': path,
                                       'body_sha256': sha,
                                       'body': body_text,
                                       'repeats': 0})
            else:
                loading_bodies.dropped += 1
            if loading_503 is None:
                loading_503 = {
                    't_ms': row['t_ms'],
                    'path': path,
                    'status': 503,
                    'headers': _header_subset(result['headers']),
                    'body_sha256': sha,
                    'body': body_text,
                }
        return None

    try:
        while time.monotonic() < deadline:
            rc = proc.poll()
            if rc is not None:
                return (transitions, loading_503, loading_bodies, False,
                        f'server-exited-early-rc{rc}', ownership)
            err = _observe('models', '/v1/models', conn.get('/v1/models'))
            if err:
                _discard_bodies(transitions, loading_503, loading_bodies)
                return transitions, None, [], False, err, ownership
            if transitions[-1]['status'] not in (None, 503):
                break
        else:
            return (transitions, loading_503, loading_bodies, False,
                    'ready-timeout', ownership)
        while time.monotonic() < deadline:
            rc = proc.poll()
            if rc is not None:
                return (transitions, loading_503, loading_bodies, False,
                        f'server-exited-early-rc{rc}', ownership)
            err = _observe('health', '/health', conn.get('/health'))
            if err:
                _discard_bodies(transitions, loading_503, loading_bodies)
                return transitions, None, [], False, err, ownership
            if transitions[-1]['status'] == 200 \
                    and transitions[-1]['path'] == '/health':
                return (transitions, loading_503, loading_bodies, True,
                        None, ownership)
        return (transitions, loading_503, loading_bodies, False,
                'ready-timeout', ownership)
    finally:
        conn._close()


def _discard_bodies(transitions, loading_503, loading_bodies=()):
    """D1: on an ownership failure, no recorded body may survive — a
    stranger's response must never reach the receipt."""
    for row in transitions:
        row['body'] = None
        row['body_sha256'] = None
    if loading_503 is not None:
        loading_503['body'] = None
        loading_503['body_sha256'] = None
    for b in loading_bodies:
        b['body'] = None
        b['body_sha256'] = None


def verify_live(proc, port, label):
    """R1 liveness gate: child must be running AND provably own the LISTEN
    socket. Returns (error_code|None, ownership) — 'child'/'foreign'/
    'unproven'. Callers: before ready_captures, before each probe, after
    probes."""
    if proc.poll() is not None:
        return f'{label}:child-exited-rc{proc.returncode}', 'unproven'
    owned = port_owned_by(proc.pid, port)
    if owned is not True:
        code = ('port-listener-not-our-child' if owned is False
                else 'port-listener-ownership-unproven')
        return f'{label}:{code}', 'foreign' if owned is False else 'unproven'
    return None, 'child'


def _capture(port, path, keep_body):
    result = http_get(port, path, timeout=10.0)
    cap = {
        'path': path,
        'status': result['status'],
        'error': result['error'],
        'headers': dict(result['headers']),
        'body_sha256': hashlib.sha256(result['body']).hexdigest(),
        'body_read_truncated': result.get('body_truncated', False),
    }
    if keep_body:
        text, truncated = _decode_body(result['body'], CAPTURE_BODY_CAP)
        cap['body'] = text
        cap['body_truncated'] = truncated
    return cap, result


def ready_captures(port):
    """Documented lifecycle surfaces once /health is 200."""
    captures = {}
    health, health_res = _capture(port, '/health', keep_body=True)
    captures['health'] = health

    models, models_res = _capture(port, '/v1/models', keep_body=True)
    captures['models'] = models
    models_doc = None
    try:
        models_doc = json.loads(models_res['body'])
    except (ValueError, TypeError):
        pass
    captures['_models_doc'] = models_doc  # stripped before emit

    props, props_res = _capture(port, '/props', keep_body=False)
    props_fields = None
    try:
        doc = json.loads(props_res['body'])
        if isinstance(doc, dict):
            dgs = doc.get('default_generation_settings')
            props_fields = {
                'model_alias': doc.get('model_alias'),
                'total_slots': doc.get('total_slots'),
                'is_sleeping': doc.get('is_sleeping'),
                'build_info': doc.get('build_info'),
                'default_generation_settings.n_ctx':
                    dgs.get('n_ctx') if isinstance(dgs, dict) else None,
            }
    except (ValueError, TypeError):
        pass
    props['fields'] = props_fields
    captures['props'] = props

    slots, slots_res = _capture(port, '/slots', keep_body=False)
    slots_count = None
    try:
        doc = json.loads(slots_res['body'])
        if isinstance(doc, list):
            slots_count = len(doc)
    except (ValueError, TypeError):
        pass
    slots['element_count'] = slots_count
    captures['slots'] = slots

    metrics, _ = _capture(port, '/metrics', keep_body=False)
    captures['metrics'] = {'path': '/metrics', 'status': metrics['status'],
                           'error': metrics['error']}
    return captures


def run_probe(probe, port, expect, child_env):
    """bash PROBE check --port P --expect E --json --timeout 2
    --connect-timeout 1. Returns parsed JSON + exit. Runs under the same
    allowlisted env as the server child (no proxy vars can redirect it);
    subprocess-level timeout is 60 s."""
    argv = ['bash', str(probe), 'check', '--port', str(port),
            '--expect', expect, '--json',
            '--timeout', '2', '--connect-timeout', '1']
    rec = {'expect': expect, 'argv': argv, 'exit': None,
           'result': None, 'stderr_tail': None}
    try:
        cp = subprocess.run(argv, capture_output=True, text=True,
                            timeout=PROBE_TIMEOUT, env=child_env)
    except subprocess.TimeoutExpired:
        rec['exit'] = None
        rec['stderr_tail'] = f'timeout after {PROBE_TIMEOUT}s'
        return rec
    rec['exit'] = cp.returncode
    if cp.stderr:
        rec['stderr_tail'] = cp.stderr[-2000:]
    try:
        rec['result'] = json.loads(cp.stdout)
    except (ValueError, TypeError):
        rec['result'] = None
        rec['stdout_tail'] = (cp.stdout or '')[-2000:]
    return rec


def probe_row(rec):
    """First rows[] element of a parsed kama-probe check payload, or None."""
    doc = rec.get('result')
    if not isinstance(doc, dict):
        return None
    rows = doc.get('rows')
    if isinstance(rows, list) and rows and isinstance(rows[0], dict):
        return rows[0]
    return None


def _child_running(proc):
    """Fresh aliveness: poll() reaps a self-exited child. False when the
    process is gone or the state cannot be proven — killpg stays off a
    dead child so its pgid can never hit a reincarnated process."""
    try:
        return proc is not None and proc.poll() is None
    except Exception:
        return False


def _port_refuses(port):
    """True iff a loopback connect to `port` is refused; False for any
    other outcome (a live listener, timeout, or reset)."""
    try:
        socket.create_connection(('127.0.0.1', port), timeout=1.0).close()
        return False
    except ConnectionRefusedError:
        return True
    except OSError:
        return False


def teardown(proc, port, log_path):
    """SIGTERM the process group, SIGKILL after TERM_GRACE, then prove the
    port refuses connections and reduce the temp log to kept lines.
    alive_at_teardown_start records whether the child was still running
    when teardown began — a self-exited child was never signalled."""
    out = {'returncode': None, 'sigterm_sent': False, 'sigkill_sent': False,
           'alive_at_teardown_start': _child_running(proc),
           'term_wait_ms': None, 'port_refuses': None, 'log_lines': [],
           'log_lines_truncated': False, 'log_path': str(log_path)}
    if out['alive_at_teardown_start']:  # F5: killpg only on a live child
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            out['sigterm_sent'] = True  # recorded only on delivery
        except (ProcessLookupError, PermissionError, OSError):
            pass
    if proc is not None:
        t0 = time.monotonic()
        try:
            proc.wait(timeout=TERM_GRACE)
        except subprocess.TimeoutExpired:
            if _child_running(proc):  # re-check: it may have exited just now
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                    out['sigkill_sent'] = True
                except (ProcessLookupError, PermissionError, OSError):
                    pass
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        out['term_wait_ms'] = round((time.monotonic() - t0) * 1000)
        out['returncode'] = proc.returncode
    # prove the port is closed
    out['port_refuses'] = _port_refuses(port)
    # reduce the log to kept lines; the temp file is unlinked even when
    # reduction raises, so an internal fault never leaves it behind
    try:
        try:
            with open(log_path, 'rb') as fh:  # keep only the last LOG_TAIL_CAP bytes (R3)
                fh.seek(0, os.SEEK_END)
                size = fh.tell()
                fh.seek(max(0, size - LOG_TAIL_CAP))
                tail = fh.read()
            text = tail.decode('utf-8', errors='replace')
            out['log_tail_truncated'] = size > LOG_TAIL_CAP
        except OSError:
            text = ''
            out['log_tail_truncated'] = None
        kept = [ln for ln in text.splitlines() if LOG_KEEP.search(ln)]
        out['log_lines_truncated'] = len(kept) > LOG_KEEP_MAX
        out['log_lines'] = kept[:LOG_KEEP_MAX]
    finally:
        try:
            os.unlink(log_path)
        except OSError:
            pass
    return out


def _check(check_id, passed, observed):
    return {'id': check_id, 'documented_by': DOC[check_id],
            'passed': bool(passed), 'observed': observed}


# Byte-contiguous spans of the pinned llama.cpp commit that ground the v2
# sourced predicates. Each binding is {check, row, commit, path, url,
# lines:[a,b], file_sha256, span_text, span_sha256}. `row` is the SOURCES
# registry id when a landed row already covers the proposition; null means
# this round still owes a row (the span is still cited and re-derivable).
# The span text is literal here so the gate can re-derive span_sha256
# without network access; file_sha256 is the raw digest of the whole file
# at the pinned commit (S036/S037 record the same digests).
def _binding(check, row, path, first, last, file_sha256, span_text):
    return {
        'check': check,
        'row': row,
        'commit': LLAMA_COMMIT,
        'path': 'tools/server/' + path,
        'url': _LLAMA_RAW + path,
        'lines': [first, last],
        'file_sha256': file_sha256,
        'span_text': span_text,
        'span_sha256': hashlib.sha256(
            span_text.encode('utf-8')).hexdigest(),
    }


SERVER_CONTEXT_SHA = (
    'dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329')
SERVER_HTTP_SHA = (
    '24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb')
SERVER_SHA_CPP = (
    '2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4')


def source_bindings():
    """Producer half of the source-binding contract (one entry per sourced
    predicate span). Plain data; never executed, never network-read."""
    return [
        _binding(
            'health_ready', None, 'server-context.cpp', 5288, 5299,
            SERVER_CONTEXT_SHA,
            '    this->get_health = [this](const server_http_req &) {\n'
            '        // error and loading states are handled by middleware\n'
            '        auto res = create_response(true);\n'
            '\n'
            '        // this endpoint can be accessed during sleeping\n'
            '        // the next LOC is to avoid someone accidentally use '
            'ctx_server\n'
            '        bool ctx_server; // do NOT delete this line\n'
            '        GGML_UNUSED(ctx_server);\n'
            '\n'
            '        res->ok({{"status", "ok"}});\n'
            '        return res;\n'
            '    };\n'),
        _binding(
            'loading_envelope_graded', 'S036', 'server-http.cpp',
            314, 325, SERVER_HTTP_SHA,
            '            res.status = 503;\n'
            '            res.set_content(\n'
            '                safe_json_to_str(json {\n'
            '                    {"error", {\n'
            '                        {"message", "Loading model"},\n'
            '                        {"type", "unavailable_error"},\n'
            '                        {"code", 503}\n'
            '                    }}\n'
            '                }),\n'
            '                "application/json; charset=utf-8"\n'
            '            );\n'
            '            return false;\n'),
        _binding(
            'teardown_graceful', None, 'server.cpp', 529, 534,
            SERVER_SHA_CPP,
            '        struct sigaction sigint_action;\n'
            '        sigint_action.sa_handler = signal_handler;\n'
            '        sigemptyset (&sigint_action.sa_mask);\n'
            '        sigint_action.sa_flags = 0;\n'
            '        sigaction(SIGINT, &sigint_action, NULL);\n'
            '        sigaction(SIGTERM, &sigint_action, NULL);\n'),
        _binding(
            'teardown_graceful', None, 'server.cpp', 519, 523,
            SERVER_SHA_CPP,
            '        shutdown_handler = [&](int) {\n'
            '            mcp_mgr.shutdown();\n'
            '            // this will unblock start_loop()\n'
            '            ctx_server.terminate();\n'
            '        };\n'),
        _binding(
            'teardown_graceful', None, 'server.cpp', 575, 590,
            SERVER_SHA_CPP,
            '        // this call blocks the main thread until '
            'queue_tasks.terminate() is called\n'
            '        ctx_server.start_loop();\n'
            '\n'
            '        clean_up();\n'
            '        ctx_http.join();\n'
            '        if (monitor_thread.joinable()) {\n'
            '            monitor_thread.join();\n'
            '        }\n'
            '\n'
            '        auto * ll_ctx = ctx_server.get_llama_context();\n'
            '        if (ll_ctx != nullptr) {\n'
            '            common_memory_breakdown_print(ll_ctx);\n'
            '        }\n'
            '    }\n'
            '\n'
            '    return 0;\n'),
    ]


def build_parser():
    p = argparse.ArgumentParser(
        prog='kama-llamacpp-live.py',
        description='Launch an ephemeral llama-server on a free unregistered '
                    'loopback port, capture its lifecycle, probe it with '
                    'kama-probe.sh, tear it down, and emit a '
                    'kama-llamacpp-live/v2 receipt.',
    )
    p.add_argument('--server', default=None,
                   help='llama-server binary (default: shutil.which'
                        '("llama-server")); realpath+sha256 recorded')
    p.add_argument('--model', required=True, help='GGUF path')
    p.add_argument('--model-sha256', required=True,
                   help='expected hex sha256 of --model; mismatch -> exit 3')
    p.add_argument('--alias', default='kama-live-probe',
                   help='--alias passed to llama-server')
    p.add_argument('--probe', default=str(DEFAULT_PROBE),
                   help='kama-probe.sh path')
    p.add_argument('--ctx', type=int, default=256, help='-c ctx size')
    p.add_argument('--threads', type=int, default=1, help='-t threads')
    p.add_argument('--ready-timeout', type=float, default=60.0,
                   help='seconds to wait for /health == 200')
    p.add_argument('--out', default=None,
                   help='receipt path (default: stdout)')
    p.add_argument('--port', type=int, default=None,
                   help='explicit port instead of bind(:0); still refused '
                        'when it is a registered consumer port (8080, 34113, '
                        'any port in registry/endpoint-consumers.tsv) or '
                        'already listening')
    return p


def _emit(receipt, out_path):
    text = json.dumps(receipt, ensure_ascii=True, allow_nan=False,
                      indent=2, sort_keys=True) + '\n'
    if out_path:
        # atomic publish: sibling temp file + os.replace
        fd, tmp = tempfile.mkstemp(prefix='.kama-live-',
                                   dir=str(Path(out_path).parent))
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as fh:
                fh.write(text)
            os.replace(tmp, out_path)
        except OSError:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
    else:
        sys.stdout.write(text)


def main(argv=None):
    args = build_parser().parse_args(argv)

    # ---- setup: resolve and verify identities BEFORE launch ----------------
    server_arg = args.server or shutil.which('llama-server')
    if not server_arg:
        print('kama-llamacpp-live: no llama-server on PATH and --server '
              'not given', file=sys.stderr)
        return 2
    server_real = os.path.realpath(server_arg)
    if not (os.path.isfile(server_real) and os.access(server_real, os.X_OK)):
        print(f'kama-llamacpp-live: server not executable: {server_real}',
              file=sys.stderr)
        return 2
    if not os.path.isfile(args.model):
        print(f'kama-llamacpp-live: model not found: {args.model}',
              file=sys.stderr)
        return 2
    if not os.path.isfile(args.probe):
        print(f'kama-llamacpp-live: probe not found: {args.probe}',
              file=sys.stderr)
        return 2

    model_sha = sha256_file(args.model)
    if model_sha.lower() != args.model_sha256.lower():
        print('kama-llamacpp-live: model digest mismatch\n'
              f'  expected: {args.model_sha256.lower()}\n'
              f'  actual:   {model_sha}\n'
              '  refusing to launch', file=sys.stderr)
        return 3

    try:
        server_sha = sha256_file(server_real)
        tree, tree_sha = install_tree(server_real)
        impl_path = os.path.join(os.path.dirname(server_real),
                                 'libllama-server-impl.so')
        impl_sha = (sha256_file(impl_path)
                    if os.path.isfile(impl_path) else None)
        probe_sha = sha256_file(args.probe)
        refused = refused_ports()
        port = pick_port(refused, args.port)
    except SetupError as exc:
        print(f'kama-llamacpp-live: {exc.code}', file=sys.stderr)
        return 2
    except OSError as exc:
        print(f'kama-llamacpp-live: setup error: {exc}', file=sys.stderr)
        return 2

    receipt = {
        'schema': SCHEMA,
        'started_utc': _utc_now(),
        'ended_utc': None,
        'server': {
            'arg': server_arg,
            'realpath': server_real,
            'sha256': server_sha,
            'install_tree': tree,
            'install_tree_sha256': tree_sha,
            'server_impl_sha256': impl_sha,
        },
        'model': {
            'path': os.path.realpath(args.model),
            'sha256': model_sha,
        },
        'model_sha256_post': None,
        'probe': {'path': str(args.probe), 'sha256': probe_sha},
        'alias': args.alias,
        'ctx': args.ctx,
        'threads': args.threads,
        'port': port,
        'port_refusal_set': sorted(refused),
        'child_env_keys': sorted(CHILD_ENV_KEYS),
        'argv': None,
        'transitions': [],
        'loading_503': None,
        'loading_503_bodies': [],
        'loading_bodies_dropped': 0,
        'loading_observed': False,
        'loading_envelope_exact': None,
        'captures': {},
        'probes': [],
        'teardown': None,
        'checks': [],
        'setup_error': None,
        'internal_fault': None,
        'child_pid': None,
        'port_listener_ownership': 'unproven',
        'source_binding': source_bindings(),
        'port_pick_note': 'port released after bind(:0) and re-bound by the '
                          'server; a sub-second collision race is possible',
        'tool': {'path': str(SCRIPT),
                 'sha256': None},  # filled below; self-hash of this script
    }

    server_argv = [
        server_real, '-m', args.model,
        '--alias', args.alias,
        '--host', '127.0.0.1',
        '--port', str(port),
        '-c', str(args.ctx),
        '-t', str(args.threads),
        '--no-webui',
        '--offline',
    ]
    receipt['argv'] = server_argv
    try:
        receipt['tool']['sha256'] = sha256_file(SCRIPT)
    except OSError:
        pass  # self-hash unverifiable is recorded as null, not fatal
    child_env = {k: os.environ[k] for k in CHILD_ENV_KEYS if k in os.environ}
    receipt['child_env_keys'] = sorted(child_env)

    proc = None
    log_path = None
    exit_code = 2

    def _term_handler(signum, _frame):
        raise Terminated(f'signal {signum}')

    old_handlers = {}
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        old_handlers[sig] = signal.signal(sig, _term_handler)

    try:
        try:
            log_fd, log_path = tempfile.mkstemp(prefix='kama-llamacpp-live-',
                                                suffix='.log')
        except OSError as exc:
            raise SetupError(f'log-mkstemp-failed:{exc}') from exc
        log_file = os.fdopen(log_fd, 'wb')
        # F2: no pass_fds/pipe — close_fds would close a reporting fd before
        # preexec_fn runs, so the prctl outcome is recorded honestly as
        # 'unknown'; the prctl itself remains best-effort hardening.
        _FORKED_PPID[0] = os.getpid()
        popen_kwargs = dict(
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            preexec_fn=_preexec_pdeathsig,
            env=child_env,
        )
        try:
            proc = subprocess.Popen(server_argv, **popen_kwargs)
            receipt['child_pid'] = proc.pid
        finally:
            log_file.close()  # child holds its own dup of the fd
        receipt['pdeathsig'] = {'requested': True, 'prctl_ok': 'unknown'}

        (transitions, loading_503, loading_bodies, ready, fail,
         ownership) = readiness_loop(proc, port, args.ready_timeout)
        receipt['port_listener_ownership'] = {
            True: 'child', False: 'foreign', None: 'unproven',
        }[ownership]
        receipt['transitions'] = transitions
        receipt['loading_503'] = loading_503
        receipt['loading_503_bodies'] = loading_bodies
        receipt['loading_bodies_dropped'] = getattr(
            loading_bodies, 'dropped', 0)
        receipt['loading_observed'] = loading_503 is not None
        receipt['loading_envelope_exact'] = loading_envelope_exact(loading_503)
        if not ready:
            raise SetupError(fail)

        # R1 liveness gate before the ready captures
        err, owned_state = verify_live(proc, port, 'pre-captures')
        receipt['port_listener_ownership'] = owned_state
        if err:
            raise SetupError(err)

        captures = ready_captures(port)
        models_doc = captures.pop('_models_doc')
        receipt['captures'] = captures

        checks = []
        health_status = captures['health']['status']
        health_body = None
        try:
            health_body = json.loads(captures['health'].get('body') or '')
        except (ValueError, TypeError):
            pass
        checks.append(_check(
            'health_ready',
            health_status == 200 and health_body == HEALTH_READY_BODY,
            {'status': health_status, 'body': health_body,
             'expected_body': HEALTH_READY_BODY}))

        data = models_doc.get('data') if isinstance(models_doc, dict) else None
        ids = [e.get('id') for e in data if isinstance(e, dict)] \
            if isinstance(data, list) else []
        owners = [e.get('owned_by') for e in data if isinstance(e, dict)] \
            if isinstance(data, list) else []
        checks.append(_check(
            'models_alias_id',
            bool(ids) and all(i == args.alias for i in ids),
            {'data_ids': ids, 'expected_alias': args.alias}))
        checks.append(_check(
            'models_owned_by_llamacpp',
            bool(owners) and all(o == 'llamacpp' for o in owners),
            {'owned_by': owners}))

        checks.append(_check(
            'metrics_not_enabled',
            captures['metrics']['status'] is not None
            and captures['metrics']['status'] == 501,
            {'status': captures['metrics']['status']}))

        props_fields = captures['props']['fields']
        checks.append(_check(
            'props_alias',
            isinstance(props_fields, dict)
            and props_fields.get('model_alias') == args.alias,
            {'fields': props_fields}))

        for i, expect in enumerate((args.alias, MISMATCH_EXPECT)):
            err, owned_state = verify_live(proc, port, f'pre-probe-{i + 1}')
            receipt['port_listener_ownership'] = owned_state
            if err:
                raise SetupError(err)
            rec = run_probe(args.probe, port, expect, child_env)
            receipt['probes'].append(rec)
        # R1: one more gate after the probes, before verdict checks
        err, owned_state = verify_live(proc, port, 'post-probes')
        receipt['port_listener_ownership'] = owned_state
        if err:
            raise SetupError(err)

        ok_probe, bad_probe = receipt['probes']
        ok_row = probe_row(ok_probe) or {}
        bad_row = probe_row(bad_probe) or {}
        checks.append(_check(
            'probe_model_ok',
            ok_probe['exit'] == 0
            and ok_row.get('verdict') == 'MODEL_OK'
            and ok_row.get('reason') == 'matched',
            {'exit': ok_probe['exit'], 'verdict': ok_row.get('verdict'),
             'reason': ok_row.get('reason')}))
        checks.append(_check(
            'probe_mismatch',
            bad_probe['exit'] == 2
            and bad_row.get('verdict') == 'MODEL_MISMATCH'
            and bad_row.get('reason') == 'served-id-mismatch',
            {'exit': bad_probe['exit'], 'verdict': bad_row.get('verdict'),
             'reason': bad_row.get('reason')}))

        receipt['checks'] = checks
        exit_code = 0 if all(c['passed'] for c in checks) else 1
    except SetupError as exc:
        receipt['setup_error'] = exc.code
        exit_code = 2
    except Terminated as exc:
        receipt['setup_error'] = f'terminated:{exc}'
        exit_code = 2
    except Exception as exc:  # F1: unexpected post-launch failure -> exit 2
        receipt['setup_error'] = f'unexpected:{type(exc).__name__}'
        exit_code = 2
    finally:
        # R2/F1: block SIGINT/SIGTERM/SIGHUP for the whole shutdown —
        # teardown, model rehash AND the receipt write. Handlers are
        # restored only after the write, in the outer-finally epilogue.
        # Every failure in here writes a receipt and exits 2 — nothing
        # escapes as a traceback.
        internal_fault = None
        try:
            for sig in old_handlers:
                signal.signal(sig, signal.SIG_IGN)
        except Exception as exc:
            internal_fault = type(exc).__name__
        td = None
        checks = receipt.get('checks') or []
        try:
            if log_path is not None or proc is not None:
                try:
                    td = teardown(proc, port, log_path)
                except Exception as exc:
                    internal_fault = type(exc).__name__
                    td = {
                        'error': f'{type(exc).__name__}: {exc}',
                        'returncode': proc.returncode if proc else None,
                        'sigterm_sent': False,
                        'sigkill_sent': False,
                        'alive_at_teardown_start':
                            _child_running(proc),
                        'port_refuses': None,
                        'term_wait_ms': None,
                        'log_lines': [],
                    }
        except Exception as exc:
            internal_fault = internal_fault or type(exc).__name__
        # last-chance kill: any fault path that left the group running
        # still reaps it here — poll() is fresh, so a dead child's pgid
        # can never hit a reincarnated process.
        try:
            if _child_running(proc):
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                    if isinstance(td, dict):
                        td['sigkill_sent'] = True
                except (ProcessLookupError, PermissionError, OSError):
                    pass
                try:
                    proc.wait(timeout=5)
                    if isinstance(td, dict):
                        td['returncode'] = proc.returncode
                except subprocess.TimeoutExpired:
                    pass
        except Exception as exc:
            internal_fault = internal_fault or type(exc).__name__
        # a faulted teardown never probed the port; do it now that the
        # backstop above had its chance to reap the group
        if isinstance(td, dict) and td.get('port_refuses') is None:
            try:
                td['port_refuses'] = _port_refuses(port)
            except Exception as exc:
                internal_fault = internal_fault or type(exc).__name__
        receipt['teardown'] = td
        try:
            graceful = (
                isinstance(td, dict)
                and td.get('sigterm_sent') is True
                and td.get('sigkill_sent') is False
                and td.get('alive_at_teardown_start') is True
                and td.get('returncode') == 0
                and receipt.get('port_listener_ownership') == 'child')
            checks.append(_check(
                'teardown_graceful', graceful,
                {'sigterm_sent': td.get('sigterm_sent')
                 if isinstance(td, dict) else None,
                 'sigkill_sent': td.get('sigkill_sent')
                 if isinstance(td, dict) else None,
                 'alive_at_teardown_start':
                     td.get('alive_at_teardown_start')
                     if isinstance(td, dict) else None,
                 'returncode': td.get('returncode')
                 if isinstance(td, dict) else None,
                 'port_listener_ownership':
                     receipt.get('port_listener_ownership'),
                 'error': td.get('error')
                 if isinstance(td, dict) else None}))
            checks.append(_check(
                'teardown_port_closed',
                isinstance(td, dict)
                and td.get('port_refuses') is True
                and receipt.get('port_listener_ownership') == 'child',
                {'port_refuses': td.get('port_refuses')
                 if isinstance(td, dict) else None,
                 'port_listener_ownership':
                     receipt.get('port_listener_ownership')}))
            bodies = receipt.get('loading_503_bodies') or []
            total_503 = sum(1 + (b.get('repeats') or 0)
                            for b in bodies if isinstance(b, dict))
            checks.append(_check(
                'loading_envelope_graded',
                receipt.get('loading_observed') is True
                and loading_envelopes_all(bodies) is True,
                {'loading_observed':
                     receipt.get('loading_observed'),
                 'distinct_bodies': len(bodies),
                 'bodies_dropped':
                     receipt.get('loading_bodies_dropped', 0),
                 'total_503_responses': total_503,
                 'all_exact': loading_envelopes_all(bodies),
                 'exact': loading_envelopes_all(bodies)}))
            try:
                receipt['model_sha256_post'] = sha256_file(args.model)
            except OSError as exc:
                receipt['model_sha256_post'] = f'rehash-error:{exc}'
            checks.append(_check(
                'model_unchanged',
                receipt['model_sha256_post'] == model_sha,
                {'pre': model_sha,
                 'post': receipt['model_sha256_post']}))
            receipt['checks'] = checks
        except Exception as exc:
            internal_fault = internal_fault or type(exc).__name__
        try:
            if internal_fault is not None:
                receipt['internal_fault'] = f'internal:{internal_fault}'
                if receipt['setup_error'] is None:
                    receipt['setup_error'] = receipt['internal_fault']
                exit_code = 2
            elif receipt['setup_error'] is None:
                exit_code = (0 if all(
                    isinstance(c, dict) and c.get('passed') is True
                    for c in receipt['checks']) else 1)
        except Exception as exc:  # last guard: never escape the finally
            receipt['internal_fault'] = f'internal:{type(exc).__name__}'
            if receipt['setup_error'] is None:
                receipt['setup_error'] = receipt['internal_fault']
            exit_code = 2

    # F1: receipt write + handler restore run outside the try/finally so
    # the receipt is emitted even after an unexpected mid-run exception.
    # The outer finally restores handlers on every escape, including an
    # internal fault inside the block above.
    emitted = False
    try:
        receipt['ended_utc'] = _utc_now()
        try:
            _emit(receipt, args.out)
            emitted = True
        except Terminated as exc:
            # a signal landed during the write; annotate and retry once
            receipt['setup_error'] = (
                f"{receipt['setup_error']}+terminated-during-emit"
                if receipt['setup_error'] else f'terminated:{exc}')
            exit_code = 2
            try:
                _emit(receipt, args.out)
                emitted = True
            except (OSError, Terminated):
                pass
        except OSError as exc:
            print(f'kama-llamacpp-live: cannot write receipt: {exc}',
                  file=sys.stderr)
            exit_code = 2
        except Exception as exc:
            print('kama-llamacpp-live: emit fault '
                  f'{type(exc).__name__}: {exc}', file=sys.stderr)
            exit_code = 2
    finally:
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)
    if not emitted:
        return 2
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
