#!/usr/bin/env python3
"""Forgery helper (MT01 attack): sets PR_SET_DUMPABLE=0, then serves a run-port
listener handed to it over a unix control socket (SCM_RIGHTS) or bound itself.
Commands on the control socket:
  FD <qport>   (fd attached)  serve the attached listening socket, forward to qport
  BIND <port> <qport>         bind 127.0.0.1:<port> and serve, forward to qport
  HOLD         (fd attached)  keep the listening socket open, never accept
  DROP         close the listener (stay alive until the control socket closes)
Each command is acked with b'ok\n'.
"""
import ctypes
import http.server
import os
import socket
import sys
import threading
import urllib.error
import urllib.request

ctypes.CDLL(None).prctl(4, 0, 0, 0, 0)  # PR_SET_DUMPABLE = 0
ctl = sys.argv[1]
try:
    os.unlink(ctl)
except OSError:
    pass
us = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
us.bind(ctl)
us.listen(1)
conn, _ = us.accept()


def serve(ls, qport):
    class H(http.server.BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.0'

        def _go(self, body):
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'served.log'), 'a') as lg:
                lg.write(f'{os.getpid()} {self.command} {self.path}\n')
            req = urllib.request.Request(
                f'http://127.0.0.1:{qport}{self.path}', data=body,
                method=self.command,
                headers={'Content-Type': 'application/json'})
            op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            try:
                r = op.open(req, timeout=30)
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

    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H,
                                          bind_and_activate=False)
    srv.socket.close()
    srv.socket = ls
    srv.server_address = ls.getsockname()
    threading.Thread(target=srv.serve_forever,
                     kwargs={'poll_interval': 0.1}, daemon=True).start()
    return srv


srv = None
held = []
while True:
    msg, fds, _, _ = socket.recv_fds(conn, 256, 4)
    if not msg:
        break
    parts = msg.split()
    if parts[0] == b'FD':
        srv = serve(socket.socket(fileno=fds[0]), int(parts[1]))
    elif parts[0] == b'BIND':
        ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ls.bind(('127.0.0.1', int(parts[1])))
        ls.listen(16)
        srv = serve(ls, int(parts[2]))
    elif parts[0] == b'HOLD':
        held.append(fds[0])
    elif parts[0] == b'DROP':
        if srv is not None:
            srv.shutdown()
            srv.server_close()
            srv = None
        for f in held:
            os.close(f)
        held = []
    conn.sendall(b'ok\n')
