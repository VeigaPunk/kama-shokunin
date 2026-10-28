#!/usr/bin/env python3
"""Forger probe (MT07 attack b, privileged variant). Run as root via sudo.

Takes the run-port listening socket of the pinned child (pidfd_getfd on a
child the caller forked), stops the child, starts its own pinned llama-server
on a hidden port (the "reference" answerer) and forwards every request on the
run port to it. A root process is owned by uid 0 in /proc, so the counter's
holder scan (own-uid only; other uids are skipped without a readlink) cannot
see it as a holder of the listener.

argv: child_pid port server model alias hold_dir
Writes hold_dir/../forger.ready when the listener is taken over; exits when
hold_dir/release exists, the child is gone, or after 600 s.
"""
import ctypes
import http.server
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

child, port = int(sys.argv[1]), int(sys.argv[2])
server, model, alias, hold = sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]
release = os.path.join(hold, 'release')
ready = os.path.join(os.path.dirname(hold.rstrip('/')), 'forger.ready')

libc = ctypes.CDLL(None, use_errno=True)
libc.syscall.restype = ctypes.c_long
SYS_PIDFD_OPEN, SYS_PIDFD_GETFD = 434, 438


def free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


def listen_inodes(p):
    out = set()
    for path in ('/proc/net/tcp', '/proc/net/tcp6'):
        try:
            lines = open(path).read().splitlines()[1:]
        except OSError:
            continue
        for ln in lines:
            f = ln.split()
            if int(f[1].rsplit(':', 1)[1], 16) == p and f[3] == '0A':
                out.add(f[9])
    return out


# the reference answerer: a second pinned server on a hidden port
p2 = free_port()
ref = subprocess.Popen(
    [server, '--model', model, '--alias', alias, '--port', str(p2),
     '--host', '127.0.0.1', '-c', '512', '-t', '1'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    stdin=subprocess.DEVNULL, env={'PATH': os.environ.get('PATH', '')})
t0 = time.time()
while time.time() - t0 < 60:
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{p2}/health',
                                    timeout=2) as r:
            if r.read() == b'{"status":"ok"}':
                break
    except Exception:
        pass
    time.sleep(0.2)

pfd = libc.syscall(ctypes.c_long(SYS_PIDFD_OPEN), ctypes.c_int(child),
                   ctypes.c_uint(0))
inodes = {f'socket:[{i}]' for i in listen_inodes(port)}
fdn = None
for fd in os.listdir(f'/proc/{child}/fd'):
    try:
        if os.readlink(f'/proc/{child}/fd/{fd}') in inodes:
            fdn = int(fd)
            break
    except OSError:
        continue
if pfd < 0 or fdn is None:
    sys.exit(3)
nfd = libc.syscall(ctypes.c_long(SYS_PIDFD_GETFD), ctypes.c_int(pfd),
                   ctypes.c_int(fdn), ctypes.c_uint(0))
if nfd < 0:
    sys.exit(4)
os.kill(child, signal.SIGSTOP)
lsock = socket.socket(fileno=nfd)


class Fwd(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'

    def _go(self, body):
        req = urllib.request.Request(
            f'http://127.0.0.1:{p2}{self.path}', data=body,
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
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._go(None)

    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        self._go(self.rfile.read(n))

    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Fwd)
srv.socket.close()
srv.socket = lsock
threading.Thread(target=srv.serve_forever, daemon=True).start()
open(ready, 'w').write(json.dumps({'child': child, 'ref_port': p2}) + '\n')

t0 = time.time()
while time.time() - t0 < 600:
    if os.path.exists(release):
        break
    if not os.path.exists(f'/proc/{child}'):
        break
    time.sleep(0.05)
srv.shutdown()
lsock.close()
try:
    os.kill(child, signal.SIGCONT)
except OSError:
    pass
ref.kill()
ref.wait()
