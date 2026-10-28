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

# ---- MT03 forgery (round-64 wave b, attack C1 binding window) -----------
# Planted answerer, not a fix. The pinned child H keeps the run-port listener
# in procfs at raw_a and raw_b; the forger steals H's listener fd with
# pidfd_getfd only while H is SIGSTOPped and a counter connection is queued,
# answers the probe window from a second pinned llama-server P3, and gives the
# fd back before the last answer leaves. MT03_MODE selects the window shape.
MT03_MODE = 'c'
import ctypes as _ct
import threading as _th
import http.client as _hc

def _mt03_get(port, path, timeout=2.0):
    c = _hc.HTTPConnection('127.0.0.1', port, timeout=timeout)
    c.request('GET', path)
    r = c.getresponse(); r.read(); c.close()
    return r.status

def _mt03_fwd(port, method, path, body, ctype):
    c = _hc.HTTPConnection('127.0.0.1', port, timeout=60)
    c.request(method, path, body=body, headers={'Content-Type': ctype} if ctype else {})
    r = c.getresponse(); data = r.read()
    c.close()
    return r.status, data, r.getheader('Content-Type')

def _mt03_read(conn):
    buf = b''
    while b'\r\n\r\n' not in buf:
        ch = conn.recv(65536)
        if not ch:
            return None
        buf += ch
    head, _, rest = buf.partition(b'\r\n\r\n')
    lines = head.decode('latin-1').split('\r\n')
    method, path = lines[0].split(' ')[:2]
    hd = {}
    for ln in lines[1:]:
        k, _, v = ln.partition(':')
        hd[k.strip().lower()] = v.strip()
    n = int(hd.get('content-length') or 0)
    while len(rest) < n:
        ch = conn.recv(65536)
        if not ch:
            break
        rest += ch
    return method, path, rest[:n], hd.get('content-type')

def _mt03_send(conn, code, data, ct):
    head = (f'HTTP/1.1 {code} OK\r\nContent-Type: {ct or "application/json"}\r\n'
            f'Content-Length: {len(data)}\r\nConnection: close\r\n\r\n').encode()
    try:
        conn.sendall(head + data)
    finally:
        conn.close()

def _mt03_canned(path, fp):
    if path.startswith('/tokenize'):
        return 200, json.dumps({'tokens': [1]}).encode(), 'application/json'
    doc = {'id': 'cmpl-canned', 'object': 'text_completion', 'created': 1,
           'model': 'kama-completion-probe', 'system_fingerprint': fp,
           'choices': [{'index': 0, 'text': ' canned', 'finish_reason': 'length'}],
           'usage': {'prompt_tokens': 1, 'completion_tokens': 1, 'total_tokens': 2}}
    return 200, json.dumps(doc).encode(), 'application/json'

def _mt03_listen_fd(pid, port):
    inos = _live._listen_inodes(port)
    for fd in os.listdir(f'/proc/{pid}/fd'):
        try:
            ln = os.readlink(f'/proc/{pid}/fd/{fd}')
        except OSError:
            continue
        if ln.startswith('socket:[') and ln[8:-1] in inos:
            return int(fd)
    raise RuntimeError('no listener fd in the held pid')

def _mt03_pending(port):
    for path in ('/proc/net/tcp', '/proc/net/tcp6'):
        try:
            with open(path, encoding='ascii') as fh:
                next(fh, None)
                for ln in fh:
                    f = ln.split()
                    if (len(f) > 4 and f[3] == '0A'
                            and int(f[1].rpartition(':')[2], 16) == port
                            and int(f[4].split(':')[1], 16) > 0):
                        return True
        except (OSError, ValueError, IndexError):
            continue
    return False

def _mt03_setup(proc, port, argv, env, hold):
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p3port = s.getsockname()[1]; s.close()
    a3 = list(argv); a3[a3.index('--port') + 1] = str(p3port)
    p3 = subprocess.Popen(a3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                          stdin=subprocess.DEVNULL, env=env,
                          preexec_fn=_live._preexec_pdeathsig)
    t0 = time.monotonic()
    while True:
        try:
            if _mt03_get(p3port, '/health') == 200:
                break
        except OSError:
            pass
        if time.monotonic() - t0 > 90:
            raise RuntimeError('mt03 P3 not ready')
        time.sleep(0.2)
    os.kill(proc.pid, signal.SIGSTOP)
    return {'proc': proc, 'H': proc.pid, 'port': port, 'p3': p3port,
            'p3proc': p3, 'hold': hold}

def _mt03_handoff(st, ls, newfd):
    kp = subprocess.Popen([sys.executable, os.path.abspath(__file__), '--mt03-k',
                           str(newfd), str(st['p3']), st['hold']],
                          pass_fds=(newfd,), stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    os.kill(st['H'], signal.SIGCONT)
    os.kill(st['H'], signal.SIGTERM)
    ls.close()
    st['proc'].wait(timeout=30)
    return kp

def _mt03_run(st):
    H, port, p3, hold = st['H'], st['port'], st['p3'], st['hold']
    rel = os.path.join(hold, 'release')
    libc = _ct.CDLL(None, use_errno=True)
    N = {'c': 4, 'cn': 4, 'c1': 1, 'b': 2}[MT03_MODE]
    fp, k, log = None, 0, []
    try:
        t0 = time.monotonic()
        while not _mt03_pending(port):
            if os.path.exists(rel) or time.monotonic() - t0 > 170:
                return
            time.sleep(0.0005)
        fdnum = _mt03_listen_fd(H, port)
        pfd = os.pidfd_open(H)
        newfd = libc.syscall(438, pfd, fdnum, 0)
        os.close(pfd)
        if newfd < 0:
            raise OSError(_ct.get_errno(), 'pidfd_getfd')
        log.append(['steal', time.monotonic()])
        ls = socket.socket(fileno=newfd)
        ls.settimeout(0.5)
        while True:
            try:
                conn, _ = ls.accept()
            except socket.timeout:
                continue
            req = _mt03_read(conn)
            if req is None:
                conn.close()
                continue
            k += 1
            method, path, body, ctype = req
            if MT03_MODE == 'cn' and k > 2:
                code, data, ct = _mt03_canned(path, fp)
            else:
                code, data, ct = _mt03_fwd(p3, method, path, body, ctype)
                if path.startswith('/v1/completions') and code == 200:
                    fp = json.loads(data).get('system_fingerprint', fp)
            if k == N:
                if MT03_MODE == 'b':
                    _mt03_send(conn, code, data, ct)
                    log.append(['handoff', time.monotonic()])
                    _mt03_handoff(st, ls, newfd)
                    log.append(['handoff_done', time.monotonic()])
                    break
                os.kill(H, signal.SIGCONT)
                log.append(['release', time.monotonic()])
                _mt03_send(conn, code, data, ct)
                ls.close()
                break
            _mt03_send(conn, code, data, ct)
    except Exception as exc:
        log.append(['error', f'{type(exc).__name__}: {exc}'])
    finally:
        t1 = time.monotonic()
        while not os.path.exists(rel) and time.monotonic() - t1 < 200:
            time.sleep(0.05)
        try:
            os.kill(H, signal.SIGCONT)
        except OSError:
            pass
        st['p3proc'].terminate()
        with open(os.path.join(os.path.dirname(hold), 'mt03-window.json'), 'w') as fh:
            json.dump({'mode': MT03_MODE, 'served_in_window': k, 'log': log}, fh)

def _mt03_k_main(fd, p3, hold):
    ls = socket.socket(fileno=fd)
    ls.settimeout(0.2)
    rel = os.path.join(hold, 'release')
    t0 = time.monotonic()
    while not os.path.exists(rel) and time.monotonic() - t0 < 200:
        try:
            conn, _ = ls.accept()
        except socket.timeout:
            continue
        req = _mt03_read(conn)
        if req is None:
            conn.close()
            continue
        code, data, ct = _mt03_fwd(p3, req[0], req[1], req[2], req[3])
        _mt03_send(conn, code, data, ct)

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
    receipt['port'] = port
    receipt['argv'] = [
        server, '--model', model, '--alias', args.alias,
        '--port', str(port), '--host', '127.0.0.1',
        '-c', str(args.ctx), '-t', str(args.threads),
    ]

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
            preexec_fn=_live._preexec_pdeathsig)
        receipt['child_pid'] = proc.pid
        receipt['server_log'] = log_path

        ready, last = wait_ready(proc, port, args.ready_timeout)
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
            _mt03 = _mt03_setup(proc, port, receipt['argv'], env, hold)
            with open(os.path.join(hold, 'hold.json'), 'w') as f:
                json.dump(hold_doc, f, indent=1)
            _th.Thread(target=_mt03_run, args=(_mt03,), daemon=True).start()
            w = _live.hold_for_witness(
                hold, proc, port, args.hold_timeout)
            try:
                os.unlink(os.path.join(hold, 'hold.json'))
            except OSError:
                pass
            released = bool(w.get('released'))
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


if len(sys.argv) > 1 and sys.argv[1] == '--mt03-k':
    _mt03_k_main(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    sys.exit(0)

if __name__ == '__main__':
    sys.exit(main())
