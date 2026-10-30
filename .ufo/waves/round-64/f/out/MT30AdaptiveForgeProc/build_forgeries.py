#!/usr/bin/env python3
"""MT30AdaptiveForgeProc - build three forged tools for round-64 C1.

Each forgery is a patched copy of the tip tool (23b3fdb1).  The patch is
structural (string replacement on the tool's own source), reproducible and
recorded as a unified diff next to the forged file.

  F1 forwarder : the process that ACCEPTS the counter's probes is a python
                  forwarder; the answers themselves are genuine (a real
                  pinned llama-server answers on a private port).
  F2 canned    : no inference engine at all - a python HTTP server that
                  emits llama.cpp-shaped JSON.
  F3 fdleak    : the genuine tool, plus a dup of the run-port listener
                  socket handed to a pre-existing, non-dumpable helper.

Usage: python3 build_forgeries.py <tip-tool.py> <outdir> <helper-sock>
"""
import os
import sys

FORWARDER_SRC = '''FORWARDER_SRC = r"""
import http.server, socket, sys, threading, urllib.request, urllib.error
TARGET = int(sys.argv[1]); PORT = int(sys.argv[2])
class H(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'
    def _go(self, body):
        req = urllib.request.Request(
            f'http://127.0.0.1:{TARGET}{self.path}', data=body,
            method=self.command, headers={'Content-Type': 'application/json'})
        op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            r = op.open(req, timeout=60)
            code, data, ct = r.status, r.read(), r.headers.get('Content-Type')
        except urllib.error.HTTPError as e:
            code, data, ct = e.code, e.read(), e.headers.get('Content-Type')
        self.send_response(code)
        self.send_header('Content-Type', ct or 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers(); self.wfile.write(data)
    def do_GET(self): self._go(None)
    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        self._go(self.rfile.read(n))
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H)
srv.serve_forever()
"""
'''

CANNED_SRC = '''CANNED_SRC = r"""
import http.server, json, sys, time
ALIAS = sys.argv[2]
PORT = int(sys.argv[1])
def _tokcount(prompt):
    return max(1, len(str(prompt).split()) + 1)
def _completion(payload):
    n = int(payload.get('n_predict') or 8)
    p = str(payload.get('prompt') or '')
    pt = _tokcount(p)
    text = ' the cat sat on the mat and the story went on.'
    return {
        'object': 'text_completion',
        'created': 1767225600,
        'id': 'cmpl-canned-0001',
        'model': ALIAS,
        'system_fingerprint': 'b1-c0ffee1234',
        'choices': [{'index': 0, 'text': text, 'logprobs': None,
                     'finish_reason': 'length'}],
        'usage': {'prompt_tokens': pt, 'completion_tokens': n,
                  'total_tokens': pt + n,
                  'prompt_tokens_details': {'cached_tokens': 0}},
        'timings': {'predicted_n': n, 'cache_n': 0, 'prompt_n': pt,
                    'predicted_ms': 1.25},
    }
class H(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'
    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path == '/health':
            b = b'{"status":"ok"}'
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(b)))
            self.end_headers(); self.wfile.write(b)
        elif self.path == '/v1/models':
            self._send(200, {'object': 'list', 'data': [{'id': ALIAS}]})
        elif self.path == '/props':
            self._send(200, {'model_alias': ALIAS})
        else:
            self._send(404, {'error': {'message': 'not found'}})
    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(n) if n else b'{}'
        try:
            payload = json.loads(raw.decode('utf-8'))
        except Exception:
            payload = {}
        if self.path == '/v1/completions':
            if 'prompt' not in payload:
                self._send(400, {'error': {'message': 'no prompt',
                                           'code': 400}})
                return
            self._send(200, _completion(payload))
        elif self.path == '/tokenize':
            content = payload.get('content') or ''
            self._send(200, {'tokens': list(range(_tokcount(content)))})
        else:
            self._send(404, {'error': {'message': 'not found'}})
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H)
srv.serve_forever()
"""
'''

LEAK_SRC = '''import ctypes, os, socket, struct, sys
HELPER_SOCK = HELPER_SOCK_PATH
def _leak_listener_fd(pid, port):
    # Duplicate the run-port LISTEN socket out of the child and hand the
    # duplicate to a pre-existing, non-dumpable helper over SCM_RIGHTS.
    # The helper never accepts on it, so it is an invisible second holder
    # of the run-port listener (its /proc/<pid>/fd is unreadable for a
    # non-dumpable process and it started before the tool).
    libc = ctypes.CDLL('libc.so.6', use_errno=True)
    want = {f'socket:[{i}]' for i in _live._listen_inodes(port)}
    if not want:
        return None
    for name in sorted(os.listdir(f'/proc/{pid}/fd')):
        try:
            if os.readlink(f'/proc/{pid}/fd/{name}') not in want:
                continue
        except OSError:
            continue
        pfd = libc.syscall(434, pid, 0)          # pidfd_open
        if pfd < 0:
            continue
        newfd = libc.syscall(438, pfd, int(name), 0)   # pidfd_getfd
        os.close(pfd)
        if newfd < 0:
            continue
        try:
            c = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            c.connect(HELPER_SOCK)
            c.sendmsg([b'\\x01'],
                      [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                        struct.pack('i', newfd))])
            c.sendall(str(pid).encode())
            c.close()
        except OSError:
            pass
        finally:
            os.close(newfd)
        return newfd
    return None
'''


def sub(text, old, new, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit(f'anchor not unique/found ({n} != {count}): '
                         f'{old[:70]!r}')
    return text.replace(old, new)


def build_f1(src):
    t = src
    t = sub(t, "FINGERPRINT_RE = re.compile(r'^b\\d+-[0-9a-f]{9,40}$')\n",
            "FINGERPRINT_RE = re.compile(r'^b\\d+-[0-9a-f]{9,40}$')\n"
            + FORWARDER_SRC)
    t = sub(t, "    proc = None\n    child_pre_dead = False\n",
            "    proc = None\n    fwd = None\n    child_pre_dead = False\n")
    t = sub(t, """        _live._FORKED_PPID[0] = os.getpid()
        proc = subprocess.Popen(
            receipt['argv'], stdout=log_f, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, env=env,
            preexec_fn=_live._preexec_pdeathsig)
        receipt['child_pid'] = proc.pid
        receipt['server_log'] = log_path
""", """        _live._FORKED_PPID[0] = os.getpid()
        # FORGERY F1: the real pinned server is moved to a private port and
        # a python forwarder takes the advertised run port.  The answers
        # the counter sees are genuine; the process that accepts them is
        # not the pinned server.
        _srv_port = int(receipt['argv'][receipt['argv'].index('--port') + 1])
        _priv = _live.pick_port(refused, None)
        receipt['argv'][receipt['argv'].index('--port') + 1] = str(_priv)
        proc = subprocess.Popen(
            receipt['argv'], stdout=log_f, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, env=env,
            preexec_fn=_live._preexec_pdeathsig)
        _fwd_py = os.path.join(work, 'forwarder.py')
        with open(_fwd_py, 'w') as _fh:
            _fh.write(FORWARDER_SRC)
        fwd = subprocess.Popen(
            [sys.executable, _fwd_py, str(_priv), str(port)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL, env=env)
        receipt['child_pid'] = fwd.pid
        receipt['server_log'] = log_path
        receipt['forged'] = {'kind': 'F1-forwarder',
                             'answerer_pid': fwd.pid,
                             'engine_pid': proc.pid,
                             'engine_port': _priv}
""")
    t = sub(t, "        if not _live.port_owned_by(proc.pid, port):\n",
            "        if not _live.port_owned_by(fwd.pid, port):\n")
    t = sub(t, "                'pid': proc.pid,\n",
            "                'pid': fwd.pid,\n")
    t = sub(t, """        owned = _live.port_owned_by(proc.pid, port)
""", """        if fwd is not None and fwd.poll() is None:
            fwd.send_signal(signal.SIGTERM)
            try:
                fwd.wait(timeout=10)
            except subprocess.TimeoutExpired:
                fwd.kill()
                fwd.wait(timeout=5)
        owned = _live.port_owned_by(fwd.pid, port) if fwd else False
""")
    return t


def build_f2(src):
    t = src
    t = sub(t, "FINGERPRINT_RE = re.compile(r'^b\\d+-[0-9a-f]{9,40}$')\n",
            "FINGERPRINT_RE = re.compile(r'^b\\d+-[0-9a-f]{9,40}$')\n"
            + CANNED_SRC)
    t = sub(t, "    proc = None\n    child_pre_dead = False\n",
            "    proc = None\n    fwd = None\n    child_pre_dead = False\n")
    t = sub(t, """        _live._FORKED_PPID[0] = os.getpid()
        proc = subprocess.Popen(
            receipt['argv'], stdout=log_f, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, env=env,
            preexec_fn=_live._preexec_pdeathsig)
        receipt['child_pid'] = proc.pid
        receipt['server_log'] = log_path
""", """        _live._FORKED_PPID[0] = os.getpid()
        # FORGERY F2: no inference engine at all.  A python HTTP server
        # on the run port answers llama.cpp-shaped JSON; the pinned
        # llama-server is never started.
        _canned_py = os.path.join(work, 'canned.py')
        with open(_canned_py, 'w') as _fh:
            _fh.write(CANNED_SRC)
        fwd = subprocess.Popen(
            [sys.executable, _canned_py, str(port), args.alias],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL, env=env)
        proc = fwd
        receipt['child_pid'] = fwd.pid
        receipt['server_log'] = log_path
        receipt['forged'] = {'kind': 'F2-canned',
                             'answerer_pid': fwd.pid, 'engine_pid': None}
""")
    t = sub(t, "        if not _live.port_owned_by(proc.pid, port):\n",
            "        if not _live.port_owned_by(fwd.pid, port):\n")
    t = sub(t, "                'pid': proc.pid,\n",
            "                'pid': fwd.pid,\n")
    t = sub(t, """        owned = _live.port_owned_by(proc.pid, port)
""", """        owned = _live.port_owned_by(fwd.pid, port) if fwd else False
""")
    return t


def build_f3(src, helper_sock):
    t = src
    t = sub(t, "FINGERPRINT_RE = re.compile(r'^b\\d+-[0-9a-f]{9,40}$')\n",
            "FINGERPRINT_RE = re.compile(r'^b\\d+-[0-9a-f]{9,40}$')\n"
            + LEAK_SRC.replace('HELPER_SOCK_PATH', repr(helper_sock)))
    t = sub(t, """        check('listener_owned',
              True,
              f'first-answer listener on {port} owned by child {proc.pid}')
""", """        # FORGERY F3: leak a duplicate of the run-port listener socket to a
        # pre-existing, non-dumpable helper.  The helper is a second
        # holder of the run-port listener that the counter cannot see.
        # (inserted BEFORE the listener_owned check so that the counter's
        # own committed forge patch still applies to this tool)
        receipt['forged'] = {'kind': 'F3-fdleak',
                             'leaked_to': HELPER_SOCK,
                             'helper_sock': HELPER_SOCK}
        _leak_listener_fd(proc.pid, port)
        check('listener_owned',
              True,
              f'first-answer listener on {port} owned by child {proc.pid}')
""")
    return t


def main():
    src_path, outdir, helper_sock = sys.argv[1], sys.argv[2], sys.argv[3]
    src = open(src_path, encoding='utf-8').read()
    os.makedirs(outdir, exist_ok=True)
    for name, text in (('forged-f1-forwarder.py', build_f1(src)),
                        ('forged-f2-canned.py', build_f2(src)),
                        ('forged-f3-fdleak.py', build_f3(src, helper_sock))):
        p = os.path.join(outdir, name)
        with open(p, 'w', encoding='utf-8') as fh:
            fh.write(text)
        print('wrote', p)


if __name__ == '__main__':
    main()
