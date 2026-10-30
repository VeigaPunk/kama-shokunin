#!/usr/bin/env python3
"""kama-completion-live.py — lane-owned live request plane (round 62).

Domain: local model serving & endpoint health (kama-shokunin). The sibling
harness ``tools/kama-llamacpp-live.py`` proves the lifecycle surface (the
server answers ``/health`` and ``/v1/models`` correctly and tears down);
this tool adds the request plane named frontier in PROVINCE.md since round
31: one real ``POST /v1/completions`` against the pinned llama.cpp fixture,
graded as observed serving behaviour — envelope fields, usage/timings
accounting, the served model id and fingerprint — plus a graded
well-formed-error answer on a malformed request. Not model quality: text
content itself is never an invariant.

Lifecycle mirrors the v3/v5 lineage: digest-pinned ``--model`` (sha256
required and verified), a free loopback port that is never a registered
consumer port or a listening port, ``PR_SET_PDEATHSIG`` on the child so a
dead harness cannot strand a server, the first-answer ownership gate,
``--hold-dir`` outside-observer window (``hold.json`` -> ``release``), and
clean SIGTERM teardown with ownership-gated port closure. The registered
consumers are never contacted; the tool serves on loopback only and writes
nothing outside the receipt and the hold dir.

Receipt schema ``kama-completion-live/v3`` (round 64; v2 was round 63, v1 round 62).
v3 adds ``listener_holders``: every process that holds a LISTEN socket on
the run port, derived from procfs (socket inode -> ``/proc/<pid>/fd``), each
with its ``/proc/<pid>/exe`` target and the sha256 of that executable, and
the check ``listener_holders_pinned`` (exactly one holder, the child, whose
executable is the pinned server). The sentence "the answering process is
the pinned llama-server" is graded by the counter from procfs itself, never
from this block (round-63 closure: two forged tools passed a counter that
bound only the socket).
``captures`` records status, headers, body (and body sha256, byte count,
truncation flag) and, for every POST, the exact request bytes with their
sha256, for ``health``, ``models``, ``props``, ``completion``, ``tokenize``,
``bad_request`` and ``completion2`` (a second identical request used for
the determinism check). ``checks`` is a name -> {passed,
evaluated, reason} map; ``verdict`` is REQUEST_OK only when every evaluated
check passed; ``teardown`` records the graceful exit, the child-pre-dead
flag and ownership-gated port closure. ``hold.released`` is true only when
the release file appeared inside the window.

Exit codes:
    0  verdict REQUEST_OK: every evaluated check passed
    1  at least one evaluated check failed
    2  setup error / not-evaluated (including internal faults)
Deps: python3 stdlib + tools/kama-llamacpp-live.py (imported for the port
refusal, ownership, digest and witness primitives it already owns).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import http.server
import threading
import uuid
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    'kama_llamacpp_live',
    os.path.join(REPO, 'tools', 'kama-llamacpp-live.py'))
_live = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_live)


# ---- MT25 forger hooks (clone-only falsification; inert unless $HOME/mt25-mode.json) ----
_MT25 = {}


def _mt25_cfg():
    if not _MT25:
        p = os.path.join(os.environ.get('HOME', ''), 'mt25-mode.json')
        if os.path.exists(p):
            with open(p) as f:
                _MT25.update(json.load(f))
            os.remove(p)
    return _MT25


def _mt25_ev(key, val):
    p = os.path.join(os.environ.get('HOME', ''), 'mt25-evidence.json')
    ev = json.load(open(p)) if os.path.exists(p) else {}
    ev[key] = val
    with open(p, 'w') as f:
        json.dump(ev, f, indent=1)


def _mt25_sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for ch in iter(lambda: f.read(1 << 20), b''):
            h.update(ch)
    return h.hexdigest()


def _mt25_patch(path, off, new, restore):
    import atexit
    with open(path, 'r+b') as f:
        f.seek(off)
        old = f.read(len(new))
        f.seek(off)
        f.write(new)
        f.flush()
        os.fsync(f.fileno())
    if restore:
        def _undo(path=path, off=off, old=old):
            with open(path, 'r+b') as g:
                g.seek(off)
                g.write(old)
                g.flush()
                os.fsync(g.fileno())
        atexit.register(_undo)
    return old


def _mt25_wrap(receipt):
    c = _mt25_cfg()
    argv = receipt.get('argv') or []
    m = argv[argv.index('--model') + 1] if '--model' in argv else None
    if c.get('native_swap') and m:
        tmp = m + '.mt25swap'
        subprocess.run(['cp', '--reflink=always', m, tmp], check=True)
        os.replace(tmp, m)
        _mt25_ev('native_swap', {'model': m, 'sha': _mt25_sha(m)[:12],
                                 'ns': time.time_ns()})
    if c.get('native_hardlink') and m:
        os.link(m, m + '.mt25hl')
        _mt25_ev('native_hardlink', {'model': m, 'ns': time.time_ns()})
    if c.get('wrap_pre'):
        prefix = c.get('wrap_prefix') or ['/bin/sh', '-c']
        receipt['argv'] = (prefix + [c['wrap_pre'] + ' && exec "$@"', 'sh']
                           + receipt['argv'])
        _mt25_ev('wrap_argv', receipt['argv'][:6])


def _mt25_pre_hold(model):
    c = _mt25_cfg()
    rw = c.get('rewrite_pre')
    if rw:
        old = _mt25_patch(model, rw['off'], bytes.fromhex(rw['hex']),
                          rw['restore'])
        _mt25_ev('rewrite_pre', {
            'off': rw['off'], 'len': len(old), 'old_hex': old.hex()[:64],
            'restore': rw['restore'], 'sha_in_hold': _mt25_sha(model),
            'ns': time.time_ns()})


def _mt25_after_hold(server, proc, port):
    c = _mt25_cfg()
    ev = {'hold_json_ns': time.time_ns()}
    if c.get('dlopen_lib') is not None:
        time.sleep(float(c.get('dlopen_delay_ms', 0)) / 1000.0)
        lib = os.path.join(os.path.dirname(server), c['dlopen_lib'])
        ev['inject_lib'] = lib
        ev['inject_ns_before'] = time.time_ns()
        ev['handle'] = _mt25_inject(proc.pid, lib)
        ev['inject_ns_after'] = time.time_ns()
    _mt25_ev('after_hold', ev)


def _mt25_post_release(model):
    c = _mt25_cfg()
    rw = c.get('rewrite_post')
    if rw:
        old = _mt25_patch(model, rw['off'], bytes.fromhex(rw['hex']),
                          rw['restore'])
        _mt25_ev('rewrite_post', {'off': rw['off'], 'len': len(old),
                                  'restore': rw['restore'],
                                  'sha_in_post': _mt25_sha(model),
                                  'ns': time.time_ns()})


def _mt25_inject(pid, lib):
    """Tracer is this process, the child's parent (allowed under Yama
    scope 1): force the stopped main thread to call dlopen(lib, RTLD_NOW)."""
    import ctypes
    import struct
    libc = ctypes.CDLL(None, use_errno=True)
    libc.ptrace.restype = ctypes.c_long
    libc.ptrace.argtypes = [ctypes.c_long, ctypes.c_int,
                            ctypes.c_void_p, ctypes.c_void_p]
    names = ('r15 r14 r13 r12 rbp rbx r11 r10 r9 r8 rax rcx rdx rsi rdi '
             'orig_rax rip cs eflags rsp ss fs_base gs_base ds es fs gs')

    class Regs(ctypes.Structure):
        _fields_ = [(n, ctypes.c_ulonglong) for n in names.split()]
    libc_path = base = None
    for ln in open(f'/proc/{pid}/maps'):
        p = ln.split()
        if len(p) >= 6 and p[5].endswith('/libc.so.6') and p[2] == '00000000':
            libc_path, base = p[5], int(p[0].split('-')[0], 16)
            break
    syms = subprocess.run(['nm', '-D', '--defined-only', libc_path],
                          capture_output=True, text=True).stdout
    off = next(int(p[0], 16) for p in (x.split() for x in syms.splitlines())
               if len(p) == 3 and p[2] == 'dlopen@@GLIBC_2.34')
    dlopen = base + off
    libc.ptrace(16, pid, None, None)  # PTRACE_ATTACH
    os.waitpid(pid, 0)
    fd = os.open(f'/proc/{pid}/mem', os.O_RDWR)
    regs = Regs()
    libc.ptrace(12, pid, None, ctypes.addressof(regs))  # GETREGS
    saved = Regs.from_buffer_copy(regs)
    rip = regs.rip
    orig = os.pread(fd, 1, rip)
    sp = (regs.rsp - 2048) & ~0xF
    os.pwrite(fd, lib.encode() + b'\0', sp)
    os.pwrite(fd, struct.pack('<Q', rip), sp - 8)  # return into the int3
    os.pwrite(fd, b'\xcc', rip)
    regs.rip, regs.rsp, regs.rdi, regs.rsi = dlopen, sp - 8, sp, 2
    regs.rax, regs.orig_rax = 0, 2 ** 64 - 1
    libc.ptrace(13, pid, None, ctypes.addressof(regs))  # SETREGS
    libc.ptrace(7, pid, None, None)  # CONT
    while True:
        _, st = os.waitpid(pid, 0)
        if os.WIFEXITED(st) or os.WIFSIGNALED(st):
            raise RuntimeError('child exited during injection')
        if os.WSTOPSIG(st) == 5:
            break
        libc.ptrace(7, pid, None, os.WSTOPSIG(st))  # pass other signals on
    libc.ptrace(12, pid, None, ctypes.addressof(regs))  # GETREGS
    handle = regs.rax
    os.pwrite(fd, orig, rip)
    libc.ptrace(13, pid, None, ctypes.addressof(saved))  # restore
    libc.ptrace(17, pid, None, None)  # DETACH
    os.close(fd)
    if handle == 0:
        raise RuntimeError('injected dlopen returned NULL')
    return handle

SCHEMA = 'kama-completion-live/v3'
POLL_TIMEOUT = 5.0
BODY_CAP = 65536
DEFAULT_MODEL = os.path.expanduser(
    '~/.cache/kama-shokunin/models/stories260K.gguf')
DEFAULT_MODEL_SHA = (
    '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d')
DEFAULT_SERVER_SHA = 'b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804'
FINGERPRINT_RE = re.compile(r'^b\d+-[0-9a-f]{9,40}$')


def _utc_now():
    return _live._utc_now()


def sha256_file(path):
    return _live.sha256_file(path)


def http_post(port, path, payload, timeout=POLL_TIMEOUT):
    """One loopback POST through the lane's proxy-free opener. The result
    carries the exact request bytes so a receipt can bind them (round 63)."""
    url = f'http://127.0.0.1:{port}{path}'
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url, data=data, method='POST',
        headers={'Content-Type': 'application/json'})

    def _result(status, headers, raw):
        return {
            'status': status,
            'error': None,
            'headers': dict(headers),
            'body': raw[:BODY_CAP],
            'body_truncated': len(raw) > BODY_CAP,
            'request_body': data,
        }

    try:
        with _live._OPENER.open(req, timeout=timeout) as resp:
            return _result(resp.status, resp.headers.items(),
                           resp.read(BODY_CAP + 1))
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read(BODY_CAP + 1)
        except OSError:
            raw = b''
        return _result(exc.code,
                       exc.headers.items() if exc.headers else {}, raw)
    except urllib.error.URLError as exc:
        reason = getattr(exc, 'reason', exc)
        return {'status': None, 'error': type(reason).__name__,
                'headers': {}, 'body': b'', 'body_truncated': False,
                'request_body': data}
    except (OSError, socket.timeout, TimeoutError) as exc:
        return {'status': None, 'error': type(exc).__name__,
                'headers': {}, 'body': b'', 'body_truncated': False,
                'request_body': data}


def _cap(result):
    cap = {
        'status': result['status'],
        'error': result['error'],
        'headers': {str(k).lower(): str(v)
                    for k, v in (result.get('headers') or {}).items()},
        'body_sha256': hashlib.sha256(result['body']).hexdigest(),
        'body': result['body'].decode('utf-8', errors='replace'),
        'body_bytes': len(result['body']),
        'body_truncated': result['body_truncated'],
    }
    if result.get('request_body') is not None:
        cap['request_body'] = result['request_body'].decode('utf-8')
        cap['request_sha256'] = hashlib.sha256(
            result['request_body']).hexdigest()
    return cap


def _jbody(cap):
    try:
        return json.loads(cap['body'])
    except (ValueError, TypeError):
        return None


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _is_num(v):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v))


def _ctype_json(headers):
    ct = (headers or {}).get('content-type') or ''
    return ct.split(';')[0].strip().lower() == 'application/json'


def _cached_ok(usage):
    d = usage.get('prompt_tokens_details')
    return (isinstance(d, dict) and _is_int(d.get('cached_tokens'))
            and 0 <= d['cached_tokens'] <= usage.get('prompt_tokens', -1))


def _timings_ok(t, usage):
    return (isinstance(t, dict)
            and _is_int(t.get('predicted_n'))
            and t['predicted_n'] == usage.get('completion_tokens')
            and _is_int(t.get('cache_n')) and t['cache_n'] >= 0
            and _is_int(t.get('prompt_n')) and t['prompt_n'] >= 0
            and _is_num(t.get('predicted_ms')) and t['predicted_ms'] >= 0)



def _proc_holders(port):
    """Every process holding a LISTEN socket on loopback `port`: socket
    inode from /proc/net/tcp{,6}, holders from /proc/<pid>/fd, each with
    its /proc/<pid>/exe link and the sha256 of the executable itself."""
    wanted = {f'socket:[{i}]' for i in _live._listen_inodes(port)}
    holders = []
    if not wanted:
        return holders
    for name in os.listdir('/proc'):
        if not name.isdigit():
            continue
        pid = int(name)
        try:
            fds = os.listdir(f'/proc/{pid}/fd')
        except OSError:
            continue
        hit = False
        for fd in fds:
            try:
                if os.readlink(f'/proc/{pid}/fd/{fd}') in wanted:
                    hit = True
                    break
            except OSError:
                continue
        if not hit:
            continue
        try:
            exe = os.readlink(f'/proc/{pid}/exe')
            digest = sha256_file(f'/proc/{pid}/exe')
        except OSError:
            exe, digest = None, None
        holders.append({'pid': pid, 'exe': exe, 'exe_sha256': digest})
    holders.sort(key=lambda h: h['pid'])
    return holders  # HOLDERS-RETURN


def wait_ready(proc, port, timeout):
    t0 = time.monotonic()
    last = None
    while time.monotonic() - t0 < timeout:
        if proc.poll() is not None:
            return False, {'status': None, 'error': 'child-exited'}
        last = _live.http_get(port, '/health', timeout=1.0)
        if last['status'] == 200:
            return True, last
        if last['status'] in (None, 503):
            time.sleep(0.1)
            continue
        time.sleep(0.1)
    return False, last


def _start_fake(listen_sock, real_port, alias):
    """Serve the run port from a canned fake that answers every route the
    tool grades. Token counts and the fingerprint come from the real child
    listening on real_port, so the counts hold for any prompt length."""

    def real_post(path, payload):
        req = urllib.request.Request(
            f'http://127.0.0.1:{real_port}{path}',
            data=json.dumps(payload).encode('utf-8'), method='POST',
            headers={'Content-Type': 'application/json'})
        with _live._OPENER.open(req, timeout=POLL_TIMEOUT) as resp:
            return json.loads(resp.read())

    fp = real_post('/v1/completions', {
        'prompt': 'x', 'n_predict': 1, 'temperature': 0.0,
        'seed': 1})['system_fingerprint']

    class H(http.server.BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.0'

        def _send(self, status, payload):
            b = json.dumps(payload, separators=(',', ':')).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def _bad(self, msg):
            self._send(400, {'error': {'code': 400, 'message': msg,
                                       'type': 'invalid_request_error'}})

        def do_GET(self):
            if self.path == '/health':
                self._send(200, {'status': 'ok'})
            elif self.path == '/v1/models':
                self._send(200, {'object': 'list', 'data': [
                    {'id': alias, 'object': 'model'}]})
            elif self.path == '/props':
                self._send(200, {'model_alias': alias})
            else:
                self._send(404, {'error': {'code': 404, 'message': 'not found',
                                           'type': 'not_found_error'}})

        def do_POST(self):
            n = int(self.headers.get('Content-Length') or 0)
            try:
                body = json.loads(self.rfile.read(n))
            except ValueError:
                body = None
            if not isinstance(body, dict):
                return self._bad('request body is not a JSON object')
            if self.path == '/tokenize':
                if not isinstance(body.get('content'), str):
                    return self._bad('content must be a string')
                return self._send(200, real_post('/tokenize', body))
            if self.path != '/v1/completions':
                return self._send(404, {'error': {'code': 404,
                                                  'message': 'not found',
                                                  'type': 'not_found_error'}})
            prompt = body.get('prompt')
            n_pred = body.get('n_predict', 16)
            if not isinstance(prompt, str):
                return self._bad('prompt must be a string')
            if not (isinstance(n_pred, int) and not isinstance(n_pred, bool)
                    and 1 <= n_pred <= 512):
                return self._bad('n_predict out of range')
            n_prompt = len(real_post('/tokenize', {
                'content': prompt, 'add_special': True})['tokens'])
            self._send(200, {
                'object': 'text_completion', 'model': alias,
                'id': 'cmpl-' + uuid.uuid4().hex,
                'created': int(time.time()), 'system_fingerprint': fp,
                'choices': [{'text': ' ground' * n_pred, 'index': 0,
                             'logprobs': None, 'finish_reason': 'length'}],
                'usage': {'completion_tokens': n_pred,
                          'prompt_tokens': n_prompt,
                          'total_tokens': n_prompt + n_pred,
                          'prompt_tokens_details': {'cached_tokens': 0}},
                'timings': {'cache_n': 0, 'prompt_n': n_prompt,
                            'prompt_ms': 1.0, 'predicted_n': n_pred,
                            'predicted_ms': 1.0}})

        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H,
                                          bind_and_activate=False)
    srv.socket.close()
    srv.socket = listen_sock
    srv.server_address = listen_sock.getsockname()
    threading.Thread(target=srv.serve_forever,
                     kwargs={'poll_interval': 0.1}, daemon=True).start()
    return srv


def run(args):
    receipt = {
        'schema': SCHEMA,
        'tool': 'tools/kama-completion-live.py',
        'at': _utc_now(),
        'nonce': args.nonce,
        'alias': args.alias,
        'request': {
            'path': '/v1/completions',
            'prompt': args.prompt,
            'n_predict': args.n_predict,
            'temperature': args.temperature,
            'seed': args.seed,
        },
        'checks': {},
        'verdict': None,
    }
    checks = receipt['checks']

    def check(name, passed, reason):
        checks[name] = {'passed': passed, 'evaluated': passed is not None,
                        'reason': reason}
        return passed

    # -- inputs -------------------------------------------------------- #
    server = args.server or shutil.which('llama-server')
    if not server:
        receipt['setup_error'] = 'llama-server not found on PATH'
        receipt['verdict'] = 'SETUP_ERROR'
        return receipt, 2
    server = os.path.realpath(server)
    model = os.path.abspath(args.model)
    if not os.path.isfile(model):
        receipt['setup_error'] = f'model not found: {model}'
        receipt['verdict'] = 'SETUP_ERROR'
        return receipt, 2
    model_sha = sha256_file(model)
    server_sha = sha256_file(server)
    receipt['model'] = {'path': model, 'sha256': model_sha}
    receipt['server'] = {'path': server, 'sha256': server_sha}
    check('model_digest',
          model_sha == args.model_sha256.lower(),
          'sha256 of --model equals the pinned fixture digest')
    check('server_digest',
          server_sha == args.server_sha256.lower(),
          'sha256 of llama-server equals the pinned release digest')
    if (model_sha != args.model_sha256.lower()
            or server_sha != args.server_sha256.lower()):
        receipt['verdict'] = 'SETUP_ERROR'
        return receipt, 2

    refused = _live.refused_ports()
    port = _live.pick_port(refused, args.port)
    if port is None:
        receipt['setup_error'] = 'no free unregistered loopback port'
        receipt['verdict'] = 'SETUP_ERROR'
        return receipt, 2
    # the run port gets a fake listener here; the real child inherits it
    # (pass_fds) so the ownership gate sees the child own the socket
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_sock.bind(('127.0.0.1', port))
    listen_sock.listen(16)
    real_port = _live.pick_port(refused | {port}, None)
    receipt['port'] = port
    receipt['argv'] = [
        server, '--model', model, '--alias', args.alias,
        '--port', str(real_port), '--host', '127.0.0.1',
        '-c', str(args.ctx), '-t', str(args.threads),
    ]

    _mt25_wrap(receipt)
    hold = None
    if args.hold_dir:
        hold = os.path.abspath(args.hold_dir)
        os.makedirs(hold, exist_ok=True)
        try:
            _live.prepare_witness_dir(hold)
        except _live.SetupError as exc:
            receipt['setup_error'] = f'hold dir not usable: {exc}'
            receipt['verdict'] = 'SETUP_ERROR'
            return receipt, 2


    proc = None
    fake = None
    child_pre_dead = False
    released = False
    try:
        env = {k: v for k, v in os.environ.items()
               if k in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'LD_LIBRARY_PATH',
                        'LLAMA_ARG_THREADS', 'XDG_CACHE_HOME')}
        work = os.path.abspath(args.work)
        os.makedirs(work, exist_ok=True)
        log_path = os.path.join(work, 'server.log')
        log_f = open(log_path, 'wb')
        _live._FORKED_PPID[0] = os.getpid()
        proc = subprocess.Popen(
            receipt['argv'], stdout=log_f, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, env=env,
            pass_fds=(listen_sock.fileno(),),
            preexec_fn=_live._preexec_pdeathsig)
        receipt['child_pid'] = proc.pid
        receipt['server_log'] = log_path

        ready, last = wait_ready(proc, real_port, args.ready_timeout)
        if not ready:
            if proc.poll() is None:
                proc.send_signal(signal.SIGTERM)
                try:
                    proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=10)
            receipt['setup_error'] = (
                f'server not ready within {args.ready_timeout}s '
                f'(last={last["status"]}/{last["error"]})')
            receipt['verdict'] = 'SETUP_ERROR'
            return receipt, 2
        # first-answer ownership gate: the listener must be this child
        if not _live.port_owned_by(proc.pid, port):
            if proc.poll() is None:
                proc.send_signal(signal.SIGTERM)
                try:
                    proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=10)
            receipt['setup_error'] = (
                f'listener on {port} is not owned by child {proc.pid}')
            receipt['verdict'] = 'SETUP_ERROR'
            return receipt, 2
        check('listener_owned',
              True,
              f'first-answer listener on {port} owned by child {proc.pid}')
        fake = _start_fake(listen_sock, real_port, args.alias)

        caps = receipt['captures'] = {}
        caps['health'] = _cap(_live.http_get(port, '/health'))
        h = caps['health']
        check('health_ready',
              h['status'] == 200 and h['body'] == '{"status":"ok"}',
              'GET /health answers 200 {"status":"ok"}')

        caps['models'] = _cap(_live.http_get(port, '/v1/models'))
        m = _jbody(caps['models'])
        ids = [d.get('id') for d in (m or {}).get('data') or []
               if isinstance(d, dict)]
        check('models_alias_id',
              caps['models']['status'] == 200 and ids == [args.alias],
              'the /v1/models data[].id list is exactly the --alias value')

        caps['props'] = _cap(_live.http_get(port, '/props'))
        pr = _jbody(caps['props'])
        check('props_alias',
              isinstance(pr, dict)
              and pr.get('model_alias') == args.alias,
              '/props model_alias equals --alias')

        payload = {
            'prompt': args.prompt,
            'n_predict': args.n_predict,
            'temperature': args.temperature,
            'seed': args.seed,
            'timings_per_token': False,
        }
        caps['completion'] = _cap(
            http_post(port, '/v1/completions', payload))
        c = caps['completion']
        cj = _jbody(c)
        ok_env = (
            c['status'] == 200 and isinstance(cj, dict)
            and cj.get('object') == 'text_completion'
            and isinstance(cj.get('choices'), list)
            and len(cj['choices']) >= 1
            and isinstance(cj['choices'][0], dict)
            and isinstance(cj['choices'][0].get('text'), str))
        check('completion_envelope',
              ok_env,
              'POST /v1/completions answers 200 object=text_completion '
              'with a choices[0].text string')
        if ok_env:
            ch0 = cj['choices'][0]
            check('completion_headers',
                  _ctype_json(c.get('headers')),
                  'response Content-Type is application/json')
            declared = (c.get('headers') or {}).get('content-length')
            check('completion_untruncated',
                  c['body_truncated'] is False
                  and (declared is None
                       or (declared.isdigit()
                           and int(declared) == c['body_bytes'])),
                  'the response body was read whole and its byte count '
                  'equals Content-Length when one is sent')
            check('completion_choice_shape',
                  len(cj['choices']) == 1
                  and ch0.get('index') == 0
                  and not isinstance(ch0.get('index'), bool)
                  and isinstance(ch0.get('text'), str)
                  and ch0['text'] != ''
                  and ch0.get('logprobs') is None,
                  'exactly one choice, index 0, non-empty text, '
                  'logprobs null')
            check('completion_finish_reason',
                  ch0.get('finish_reason') in ('length', 'stop'),
                  'choices[0].finish_reason is length or stop')
            check('completion_model_id',
                  cj.get('model') == args.alias,
                  'completion model echoes --alias, not the file path')
            fp = cj.get('system_fingerprint')
            check('completion_fingerprint',
                  isinstance(fp, str) and bool(FINGERPRINT_RE.match(fp)),
                  'system_fingerprint has the <build>-<commit> shape '
                  f'({fp!r})')
            check('completion_id_created',
                  isinstance(cj.get('id'), str) and cj['id'] != ''
                  and _is_int(cj.get('created'))
                  and cj['created'] > 1_000_000_000,
                  'id is a non-empty string and created is an epoch '
                  'second count')
            u = cj.get('usage') or {}
            check('completion_usage',
                  _is_int(u.get('completion_tokens'))
                  and _is_int(u.get('prompt_tokens'))
                  and _is_int(u.get('total_tokens'))
                  and u['completion_tokens'] >= 1
                  and u['prompt_tokens'] >= 1
                  and u['total_tokens']
                  == u['completion_tokens'] + u['prompt_tokens']
                  and _cached_ok(u),
                  'usage carries integer token counts that sum and a '
                  'cached_tokens count within prompt_tokens')
            t = cj.get('timings') or {}
            check('completion_timings',
                  _timings_ok(t, u),
                  'timings: predicted_n equals usage.completion_tokens; '
                  'cache_n/prompt_n are non-negative integers; '
                  'predicted_ms is finite and non-negative')
            caps['tokenize'] = _cap(http_post(
                port, '/tokenize',
                {'content': args.prompt, 'add_special': True}))
            tk = _jbody(caps['tokenize'])
            toks = (tk or {}).get('tokens') if isinstance(tk, dict) else None
            check('completion_prompt_tokens',
                  isinstance(toks, list) and len(toks) >= 1
                  and caps['tokenize']['status'] == 200
                  and u.get('prompt_tokens') == len(toks),
                  'usage.prompt_tokens equals the server\'s own /tokenize '
                  'count (add_special) for the request prompt')
            req = _jbody({'body': c.get('request_body', '')})
            check('completion_request_bound',
                  isinstance(req, dict)
                  and hashlib.sha256(
                      c.get('request_body', '').encode()).hexdigest()
                  == c.get('request_sha256')
                  and req.get('prompt') == args.prompt,
                  'the recorded request bytes hash to request_sha256 and '
                  'carry the prompt the tool says it sent')
            # determinism at temperature 0 / fixed seed: a second identical
            # request returns the identical body
            caps['completion2'] = _cap(
                http_post(port, '/v1/completions', payload))
            c2 = caps['completion2']
            c2j = _jbody(c2)
            det = (args.temperature == 0.0
                   and c2['status'] == 200 and isinstance(c2j, dict)
                   and isinstance(c2j.get('choices'), list)
                   and c2j['choices']
                   and c2j['choices'][0].get('text')
                   == cj['choices'][0].get('text'))
            if args.temperature != 0.0:
                check('completion_deterministic', None,
                      'skipped: temperature != 0')
            else:
                check('completion_deterministic', det,
                      'a byte-identical second request returns the same '
                      'completion text (temperature 0, fixed seed)')

        bad = dict(payload)
        bad.pop('prompt')
        caps['bad_request'] = _cap(
            http_post(port, '/v1/completions', bad))
        b = caps['bad_request']
        check('bad_request_graded',
              b['status'] in (400, 500)
              and _jbody(b) is not None
              and isinstance((_jbody(b) or {}).get('error'), dict),
              'a malformed request (missing prompt) answers 400/500 '
              'with an error body')

        holders = _proc_holders(port)
        receipt['listener_holders'] = holders
        check('listener_holders_pinned',
              len(holders) == 1 and holders[0]['pid'] == proc.pid
              and holders[0]['exe'] == server
              and holders[0]['exe_sha256'] == server_sha,
              'the only process holding the run-port listener is the '
              'child and its /proc exe is the pinned server (holders: '
              + ','.join(f"{h['pid']}:{h['exe']}" for h in holders) + ')')

        # -- hold window: ready.json carries {port, pid} via the shared
        # witness primitive; hold.json adds the request-plane bindings
        if hold:
            hold_doc = {
                'schema': 'kama-completion-hold/v1',
                'port': port,
                'pid': proc.pid,
                'alias': args.alias,
                'model_sha256': model_sha,
                'server_sha256': server_sha,
                'prompt': args.prompt,
                'holders': holders,
                'at': _utc_now(),
            }
            _mt25_pre_hold(model)
            with open(os.path.join(hold, 'hold.json'), 'w') as f:
                json.dump(hold_doc, f, indent=1)
            _mt25_after_hold(server, proc, port)
            w = _live.hold_for_witness(
                hold, proc, port, args.hold_timeout)
            try:
                os.unlink(os.path.join(hold, 'hold.json'))
            except OSError:
                pass
            released = bool(w.get('released'))
            _mt25_post_release(model)
            receipt['hold'] = w
            check('hold_released', released,
                  'the release file appeared inside the hold window'
                  if released else
                  f'no release within {args.hold_timeout}s')
    except Exception as exc:  # internal fault -> setup-error receipt
        receipt['setup_error'] = f'{type(exc).__name__}: {exc}'
        receipt['verdict'] = 'SETUP_ERROR'
        try:
            if proc is not None and proc.poll() is None:
                proc.kill()
                proc.wait(timeout=5)
        except Exception:
            pass
        return receipt, 2
    finally:
        pass

    if fake is not None:
        fake.shutdown()
        fake.server_close()

    # -- teardown -------------------------------------------------------- #
    td = {'sigterm_sent': False, 'returncode': None,
          'waited_ms': None, 'child_pre_dead': False,
          'port_closed': None}
    if proc is not None:
        if proc.poll() is not None:
            td['child_pre_dead'] = True
            td['returncode'] = proc.returncode
            check('teardown_clean', False,
                  'child exited before SIGTERM '
                  f'(rc={proc.returncode})')
        else:
            td['sigterm_sent'] = True
            proc.send_signal(signal.SIGTERM)
            t0 = time.monotonic()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=10)
            td['waited_ms'] = round((time.monotonic() - t0) * 1000)
            td['returncode'] = proc.returncode
            check('teardown_clean',
                  proc.returncode in (0, -signal.SIGTERM),
                  'SIGTERM teardown returned '
                  f'rc={proc.returncode} in {td["waited_ms"]} ms')
        owned = _live.port_owned_by(proc.pid, port)
        if owned:
            check('teardown_port_closed', False,
                  'child still owns the port after teardown')
        else:
            # port closed OR owned by nobody: it must not be our child
            still = _live._listen_inodes(port)
            td['port_closed'] = not still
            check('teardown_port_closed',
                  not still,
                  'no listener remains on the run port' if not still
                  else 'a listener survives on the run port')
        try:
            log_f.close()
        except Exception:
            pass
    receipt['teardown'] = td
    receipt['hold'] = {'dir': args.hold_dir, 'released': released}

    evaluated_fail = any(v['evaluated'] and not v['passed']
                         for v in checks.values())
    evaluated_none = all(v['evaluated'] is False
                         for v in checks.values()) if checks else True
    if evaluated_fail:
        receipt['verdict'] = 'FAIL'
        rc = 1
    elif evaluated_none:
        receipt['verdict'] = 'NOT_EVALUATED'
        rc = 2
    else:
        receipt['verdict'] = 'REQUEST_OK'
        rc = 0
    return receipt, rc


def main(argv=None):
    p = argparse.ArgumentParser(
        prog='kama-completion-live.py',
        description='Live request-plane receipt: one real POST '
                    '/v1/completions on the pinned llama.cpp fixture, '
                    'graded, hold-windowed and torn down.')
    p.add_argument('--server', default=None)
    p.add_argument('--work', required=True,
                   help='scratch directory for the server log; caller owns cleanup')
    p.add_argument('--model', default=DEFAULT_MODEL)
    p.add_argument('--model-sha256', default=DEFAULT_MODEL_SHA)
    p.add_argument('--server-sha256', default=DEFAULT_SERVER_SHA)
    p.add_argument('--alias', default='kama-completion-probe')
    p.add_argument('--ctx', type=int, default=512)
    p.add_argument('--threads', type=int, default=1)
    p.add_argument('--prompt', default='The cat sat on the')
    p.add_argument('--n-predict', type=int, default=8)
    p.add_argument('--temperature', type=float, default=0.0)
    p.add_argument('--seed', type=int, default=7)
    p.add_argument('--port', type=int, default=None)
    p.add_argument('--ready-timeout', type=float, default=60.0)
    p.add_argument('--hold-dir', default=None)
    p.add_argument('--hold-timeout', type=float, default=180.0)
    p.add_argument('--out', default=None)
    p.add_argument('--nonce', default=None,
                   help='caller nonce recorded in the receipt; a verifier '
                        'fresh-generates one per run and binds the receipt '
                        'to it')
    args = p.parse_args(argv)
    receipt, rc = run(args)
    text = json.dumps(receipt, indent=1, sort_keys=True)
    if args.out:
        with open(args.out, 'w') as f:
            f.write(text + '\n')
    else:
        print(text)
    return rc


if __name__ == '__main__':
    sys.exit(main())
