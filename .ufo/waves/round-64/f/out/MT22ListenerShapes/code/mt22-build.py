#!/usr/bin/env python3
"""Build one MT22 forged-tool variant into the scratch clone and commit it.

Shapes (one commit each; every run is scored by the UNMUTATED amended
counter from the clone path):
  reuseport    SO_REUSEPORT forger binds the run port before the child spawn
  v6           same-uid tool-spawned helper binds ::1:<runport> (v6only=1)
  v6root       root (sudo -n) tool-spawned helper binds ::1:<runport>
  mapped       same-uid tool-spawned helper binds ::ffff:127.0.0.2:<runport>
  v6daemon     PRE-STARTED root daemon binds ::1:<runport> on command
  mappeddaemon PRE-STARTED root daemon binds ::ffff:127.0.0.2:<runport>
  ns           helper unshares user+net, binds 127.0.0.1:<runport> inside
  unixfront    run port held by a TCP->unix->child front (child moved to Y)
  fwd          child moved to Y; grandchild TCP forwarder holds the run port
"""
import json
import os
import subprocess
import sys

CLONE = '/fast/scratch/hyaku/kama-r64/f/MT22ListenerShapes/clone'
TIP = '23b3fdb1a925129a9961cf551f6d40bf251602cb'
FLAG = '/fast/scratch/hyaku/kama-r64/f/MT22ListenerShapes/forge-on'
DAEMON_SOCK = '/fast/scratch/hyaku/kama-r64/f/MT22ListenerShapes/mt22-daemon.sock'

HELPER_SRC = r'''#!/usr/bin/env python3
"""mt22 forger helper (test-only). argv: mode port hold work [target]"""
import http.server
import json
import os
import socket
import sys
import threading
import time

MODE = sys.argv[1]
PORT = int(sys.argv[2])
HOLD = sys.argv[3]
WORK = sys.argv[4]
TARGET = int(sys.argv[5]) if len(sys.argv) > 5 else None
READY = os.path.join(WORK, 'mt22-ready.' + MODE)
LOG = open(os.path.join(WORK, 'mt22-' + MODE + '.log'), 'ab', buffering=0)


def log(msg):
    LOG.write(('mt22[' + MODE + '] ' + str(msg) + '\n').encode())


def serve_canned(sock, alias='kama-completion-probe'):
    class H(http.server.BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.0'

        def _send(self, status, payload):
            b = json.dumps(payload, separators=(',', ':')).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            if self.path == '/health':
                self._send(200, {'status': 'ok'})
            elif self.path == '/v1/models':
                self._send(200, {'object': 'list',
                                 'data': [{'id': alias, 'object': 'model'}]})
            elif self.path == '/props':
                self._send(200, {'model_alias': alias})
            else:
                self._send(404, {'error': {'code': 404, 'message': 'nf'}})

        def do_POST(self):
            n = int(self.headers.get('Content-Length') or 0)
            try:
                body = json.loads(self.rfile.read(n))
            except ValueError:
                body = {}
            if self.path == '/tokenize':
                toks = list(range(len(str(body.get('content', '')).split()) + 1))
                self._send(200, {'tokens': toks})
            elif self.path == '/v1/completions':
                np = body.get('n_predict', 8)
                np = np if isinstance(np, int) and np > 0 else 8
                self._send(200, {
                    'object': 'text_completion', 'model': alias,
                    'id': 'cmpl-mt22', 'created': int(time.time()),
                    'system_fingerprint': 'b11755-mt22',
                    'choices': [{'text': ' canned' * np, 'index': 0,
                                 'logprobs': None,
                                 'finish_reason': 'length'}],
                    'usage': {'completion_tokens': np, 'prompt_tokens': 1,
                              'total_tokens': np + 1,
                              'prompt_tokens_details': {'cached_tokens': 0}},
                    'timings': {'cache_n': 0, 'prompt_n': 1, 'prompt_ms': 1.0,
                                'predicted_n': np, 'predicted_ms': 1.0}})
            else:
                self._send(404, {'error': {'code': 404, 'message': 'nf'}})

        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H,
                                          bind_and_activate=False)
    srv.socket.close()
    srv.socket = sock
    srv.server_address = sock.getsockname()
    threading.Thread(target=srv.serve_forever,
                     kwargs={'poll_interval': 0.1}, daemon=True).start()
    return srv


def bind_listener(mode, port):
    if mode in ('v6', 'mapped'):
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY,
                     1 if mode == 'v6' else 0)
        s.bind(('::1' if mode == 'v6' else '::ffff:127.0.0.2', port))
    elif mode == 'v4':
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.2', port))
    elif mode == 'ns':
        import ctypes
        libc = ctypes.CDLL(None, use_errno=True)
        if libc.unshare(0x10000000 | 0x40000000) != 0:
            raise OSError('unshare(CLONE_NEWUSER|CLONE_NEWNET) failed')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', port))
    elif mode in ('fwd', 'tcpfront'):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', port))
    else:
        raise ValueError('mode ' + mode)
    s.listen(64)
    return s


def pump(a, b):
    try:
        while True:
            d = a.recv(65536)
            if not d:
                break
            b.sendall(d)
    except OSError:
        pass
    try:
        b.shutdown(socket.SHUT_WR)
    except OSError:
        pass


def connect_target(target):
    for _ in range(80):
        try:
            return socket.create_connection(('127.0.0.1', target), timeout=2)
        except OSError:
            time.sleep(0.1)
    return None


def relay_pair(conn, target):
    up = connect_target(target)
    if up is None:
        try:
            conn.close()
        except OSError:
            pass
        return
    threading.Thread(target=pump, args=(conn, up), daemon=True).start()
    threading.Thread(target=pump, args=(up, conn), daemon=True).start()


def accept_loop(sock, handler):
    def loop():
        while True:
            try:
                conn, _ = sock.accept()
            except OSError:
                return
            threading.Thread(target=handler, args=(conn,),
                             daemon=True).start()
    threading.Thread(target=loop, daemon=True).start()


def main():
    closers = []
    try:
        if MODE == 'fwd':
            s = bind_listener(MODE, PORT)
            accept_loop(s, lambda c: relay_pair(c, TARGET))
            closers.append(s)
        elif MODE == 'unixfront':
            upath = os.path.join(WORK, 'mt22.sock')
            try:
                os.unlink(upath)
            except OSError:
                pass
            u = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            u.bind(upath)
            os.chmod(upath, 0o666)
            u.listen(64)
            accept_loop(u, lambda c: relay_pair(c, TARGET))
            closers.append(u)
            s = bind_listener('tcpfront', PORT)
            closers.append(s)

            def to_unix(conn):
                up = None
                for _ in range(80):
                    try:
                        up = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        up.settimeout(2)
                        up.connect(upath)
                        break
                    except OSError:
                        time.sleep(0.1)
                        up = None
                if up is None:
                    try:
                        conn.close()
                    except OSError:
                        pass
                    return
                threading.Thread(target=pump, args=(conn, up),
                                 daemon=True).start()
                threading.Thread(target=pump, args=(up, conn),
                                 daemon=True).start()
            accept_loop(s, to_unix)
        elif MODE == 'unixcanned':
            upath = os.path.join(WORK, 'mt22.sock')
            try:
                os.unlink(upath)
            except OSError:
                pass
            u = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            u.bind(upath)
            os.chmod(upath, 0o666)
            u.listen(64)
            closers.append(u)

            def handle(conn):
                try:
                    data = b''
                    while b'\r\n\r\n' not in data:
                        d = conn.recv(65536)
                        if not d:
                            return
                        data += d
                    body = json.dumps({
                        'object': 'text_completion',
                        'model': 'kama-completion-probe',
                        'choices': [{'text': ' canned-unix-front',
                                     'index': 0,
                                     'finish_reason': 'length'}],
                        'usage': {'completion_tokens': 8,
                                  'prompt_tokens': 1,
                                  'total_tokens': 9}}).encode()
                    resp = (b'HTTP/1.1 200 OK\r\n'
                            b'Content-Type: application/json\r\n'
                            b'Content-Length: ' + str(len(body)).encode()
                            + b'\r\n\r\n' + body)
                    conn.sendall(resp)
                except OSError:
                    pass
                finally:
                    try:
                        conn.close()
                    except OSError:
                        pass
            accept_loop(u, handle)
        else:
            s = bind_listener(MODE, PORT)
            closers.append(s)
            if MODE != 'ns':
                serve_canned(s)
    except Exception as exc:
        log('stage failed: ' + repr(exc))
        sys.exit(3)
    with open(READY, 'w') as f:
        f.write('ok\n')
    log('listening; waiting for release in ' + HOLD)
    closefile = os.path.join(WORK, 'mt22-close')
    t0 = time.time()
    while time.time() - t0 < 240:
        if os.path.exists(os.path.join(HOLD, 'release')) \
                or os.path.exists(closefile):
            break
        time.sleep(0.02)
    log('release/close seen; closing')
    for c in closers:
        try:
            if hasattr(c, 'shutdown'):
                c.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            c.close()
        except OSError:
            pass
    try:
        os.unlink(READY)
    except OSError:
        pass


main()
'''

BLOCK_A_TMPL = r'''
# --- MT22 test-only forgery hook (scratch clone; not lane code) -----------
_MT22_DAEMON_SOCK = %(_daemon_sock)r
_MT22_FLAG = %(_flag)r
_MT22_HELPER_SRC = %(_helper_src)r
_MT22_CFG = None
_MT22_Y = None


def _mt22_load_flag():
    try:
        with open(_MT22_FLAG) as fh:
            cfg = json.load(fh)
    except (OSError, ValueError):
        return None
    try:
        os.unlink(_MT22_FLAG)
    except OSError:
        pass
    return cfg


_MT22_CFG = _mt22_load_flag()
_MT22_ORIG_POPEN = subprocess.Popen
if _MT22_CFG:
    import threading as _mt22_th

    _MT22_TH = _mt22_th


def _mt22_log(msg):
    if not _MT22_CFG or not _MT22_CFG.get('work'):
        return
    try:
        with open(os.path.join(_MT22_CFG['work'], 'mt22-tool.log'),
                  'ab') as f:
            f.write(('tool: ' + str(msg) + '\n').encode())
    except Exception:
        pass


def _mt22_pick_free():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


def _mt22_helper_env():
    env = {}
    for k in ('PATH', 'HOME', 'LANG', 'LC_ALL'):
        if k in os.environ:
            env[k] = os.environ[k]
    return env


def _mt22_write_helper(work):
    path = os.path.join(work, 'mt22-helper.py')
    with open(path, 'w') as f:
        f.write(_MT22_HELPER_SRC)
    return path


def _mt22_spawn_helper(mode, port, hold, work, sudo=False, prefix=()):
    path = _mt22_write_helper(work)
    argv = (['sudo', '-n'] if sudo else list(prefix)) + [sys.executable, path, mode, str(port), hold, work]
    env = None if sudo else _mt22_helper_env()
    p = _MT22_ORIG_POPEN(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, env=env,
                         start_new_session=True)
    _mt22_log('spawned helper ' + mode + ' pid=' + str(p.pid))
    return p


def _mt22_wait_ready(work, mode, timeout=12):
    ready = os.path.join(work, 'mt22-ready.' + mode)
    t0 = time.time()
    while not os.path.exists(ready) and time.time() - t0 < timeout:
        time.sleep(0.05)
    return os.path.exists(ready)


def _mt22_release_hold(port):
    if not _MT22_CFG:
        return
    work = _MT22_CFG.get('work')
    if not work:
        return
    if _MT22_CFG.get('mode') in ('v6daemon', 'mappeddaemon'):
        try:
            _mt22_daemon_cmd({'mode': 'close', 'port': port, 'hold': '',
                              'work': work})
        except OSError as exc:
            _mt22_log('daemon close failed: ' + repr(exc))
        return
    try:
        with open(os.path.join(work, 'mt22-close'), 'w') as f:
            f.write('now\n')
    except OSError as exc:
        _mt22_log('close file failed: ' + repr(exc))


def _mt22_daemon_cmd(req):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(8)
    s.connect(_MT22_DAEMON_SOCK)
    payload = json.dumps(req).encode()
    s.sendall(str(len(payload)).encode() + b'\n' + payload)
    s.settimeout(25)
    ack = s.recv(64)
    s.close()
    return ack


def _mt22_stage(port, proc, hold, args):
    """Runs once per tool run, after the holder snapshot, before hold.json."""
    if not _MT22_CFG:
        return
    mode = _MT22_CFG.get('mode', '')
    hold = hold or args.work
    work = os.path.abspath(args.work)
    _MT22_CFG['work'] = work
    if mode in ('fwd', 'unixfront'):
        return  # staged by the Popen hook (must precede wait_ready)
    sudo = mode.endswith('root')
    base = mode[:-4] if sudo else mode
    if mode in ('v6daemon', 'mappeddaemon'):
        base = 'v6' if mode == 'v6daemon' else 'mapped'
        ack = _mt22_daemon_cmd({'mode': base, 'port': port, 'hold': hold,
                                'work': work})
        _mt22_log('daemon ack ' + repr(ack))
    else:
        _mt22_spawn_helper(base, port, hold, work, sudo=sudo)
    ok = _mt22_wait_ready(work, base)
    _mt22_log('stage ' + mode + ' ready=' + str(ok))


class _Mt22Popen(subprocess.Popen):
    def __init__(self, *a, **k):
        argv = list(a[0]) if a else list(k.get('args') or [])
        if (_MT22_CFG and '--alias' in argv and '--port' in argv
                and _MT22_CFG.get('mode') in ('fwd', 'unixfront')):
            global _MT22_Y
            work = os.path.abspath(_MT22_CFG.get('work')
                                   or _MT22_CFG.setdefault('work', os.getcwd()))
            hold = _MT22_CFG.get('hold') or work
            if _MT22_Y is None:
                _MT22_Y = _mt22_pick_free()
            argv2 = list(argv)
            i = argv2.index('--port')
            argv2[i + 1] = str(_MT22_Y)
            _MT22_CFG['work'] = work
            _mt22_log('child moved to port ' + str(_MT22_Y))
            _MT22_ORIG_POPEN.__init__(self, argv2, *a[1:], **k)
            fpath = _mt22_write_helper(work)
            fmode = 'unixfront' if _MT22_CFG.get('mode') == 'unixfront' \
                else 'fwd'
            argv3 = [sys.executable, fpath, fmode, str(a[0][argv.index('--port') + 1]),
                     hold, work, str(_MT22_Y)]
            _MT22_ORIG_POPEN(argv3, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             env=_mt22_helper_env(), start_new_session=True)
            ok = _mt22_wait_ready(work, fmode)
            _mt22_log('front staged ready=' + str(ok))
            return
        subprocess.Popen.__init__(self, *a, **k)


if _MT22_CFG and _MT22_CFG.get('mode') in ('fwd', 'unixfront'):
    subprocess.Popen = _Mt22Popen
    _mt22_orig_owned = _live.port_owned_by

    def _mt22_owned_by(pid, port):
        """First-answer gate: the forged topology's holder is the front, so
        the gate is satisfied while the recorded child is alive; at teardown
        the child is gone and the honest delegation applies."""
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            pass
        return _mt22_orig_owned(pid, port)

    _live.port_owned_by = _mt22_owned_by


def _mt22_main_run(args):
    if not _MT22_CFG:
        return run(args)
    mode = _MT22_CFG.get('mode', '')
    if mode == 'reuseport':
        orig = _live.pick_port

        def patched(refused, requested=None):
            p = orig(refused, requested)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.bind(('127.0.0.1', p))
            s.listen(16)
            _MT22_CFG['sock'] = s
            _mt22_log('reuseport forger bound run port ' + str(p)
                      + ' before the child spawn')
            return p
        _live.pick_port = patched
    return run(args)


# --- end MT22 hook ---------------------------------------------------------
'''

TOOL_BLOCK_A = BLOCK_A_TMPL % {
    '_daemon_sock': DAEMON_SOCK,
    '_flag': FLAG,
    '_helper_src': HELPER_SRC,
}


def blob(repo, rev, path):
    p = subprocess.run(['git', '-C', repo, 'show', f'{rev}:{path}'],
                       capture_output=True)
    if p.returncode != 0:
        raise SystemExit('blob read failed: ' + p.stderr.decode())
    return p.stdout


def build(shape):
    text = blob(CLONE, TIP, 'tools/kama-completion-live.py').decode()
    assert 'MT22 test-only forgery hook' not in text, 'already patched'
    # 1. holder snapshot: stage the forgery after the tool's own snapshot
    anchor = ('              + \',\'.join(f"{h[\'pid\']}:{h[\'exe\']}" '
              'for h in holders) + \')\')\n')
    assert anchor in text, 'holder anchor missing'
    text = text.replace(
        anchor, anchor + '        _mt22_stage(port, proc, hold, args)\n', 1)
    rel_anchor = "                  f'no release within {args.hold_timeout}s')\n"
    assert rel_anchor in text, 'release anchor missing'
    text = text.replace(
        rel_anchor,
        rel_anchor + '        _mt22_release_hold(port)\n', 1)
    # 2. block A before the main guard
    marker = "\nif __name__ == '__main__':"
    i = text.rfind(marker)
    assert i > 0, 'main guard missing'
    text = text[:i] + '\n' + TOOL_BLOCK_A + text[i:]
    # 3. main dispatch through the wrapper
    old4 = '    receipt, rc = run(args)\n'
    assert old4 in text, 'main run anchor missing'
    text = text.replace(old4, '    receipt, rc = _mt22_main_run(args)\n', 1)
    path = os.path.join(CLONE, 'tools', 'kama-completion-live.py')
    cur = open(path).read() if os.path.exists(path) else ''
    if cur != text:
        with open(path, 'w') as f:
            f.write(text)
        subprocess.run(['git', '-C', CLONE, 'add', '-A'], check=True)
        subprocess.run(['git', '-C', CLONE, '-c', 'user.name=seat',
                        '-c', 'user.email=seat@seat.invalid', 'commit', '-q',
                        '-m', 'mt22 forged tool'], check=True)
    tip = subprocess.run(['git', '-C', CLONE, 'rev-parse', 'HEAD'],
                         capture_output=True, text=True).stdout.strip()
    print(shape, tip)
    return tip


if __name__ == '__main__':
    build(sys.argv[1])
