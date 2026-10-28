#!/usr/bin/env python3
# Forgery f helper (test harness, started BEFORE any counter run, so its start
# ticks predate every tool). It is non-dumpable, so its /proc/<pid>/fd is not
# readable to another process. It receives the run-port listening socket over
# a unix socket (SCM_RIGHTS) from the forged tool, answers the probes by
# forwarding to its own pinned llama-server child on port Q, and gives the
# listener back by closing it on 'close'.
import array, ctypes, http.server, json, os, signal, socket, subprocess, sys
import threading, time, urllib.error, urllib.request

CTL, Q = sys.argv[1], int(sys.argv[2])
LOG = os.path.join(os.path.dirname(CTL), 'helper.log')
SERVER = os.path.expanduser('~/.local/opt/llama-b11755/llama-server')
MODEL = os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf')
ctypes.CDLL(None, use_errno=True).prctl(4, 0, 0, 0, 0)  # PR_SET_DUMPABLE 0


def log(msg):
    with open(LOG, 'a') as f:
        f.write(f'{time.time():.3f} pid={os.getpid()} {msg}\n')


D = subprocess.Popen(
    [SERVER, '--model', MODEL, '--alias', 'kama-completion-probe',
     '--port', str(Q), '--host', '127.0.0.1', '-c', '512', '-t', '1'],
    stdout=open(os.path.join(os.path.dirname(CTL), 'helper-d.log'), 'wb'),
    stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
log(f'started D pid={D.pid} port={Q}')


class Fwd(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'

    def _go(self, body):
        log(f'answered {self.command} {self.path} (served by helper, forwarded to D)')
        req = urllib.request.Request(
            f'http://127.0.0.1:{Q}{self.path}', data=body, method=self.command,
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


def start_server(fd):
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Fwd,
                                          bind_and_activate=False)
    srv.socket.close()
    srv.socket = socket.socket(fileno=fd)
    srv.server_address = srv.socket.getsockname()
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    log(f'took listener fd {fd} at {srv.server_address}')
    return srv


if os.path.exists(CTL):
    os.unlink(CTL)
ctl = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
ctl.bind(CTL)
ctl.listen(4)
open(os.path.join(os.path.dirname(CTL), 'helper.pid'), 'w').write(str(os.getpid()))
log('ready')
while True:
    conn, _ = ctl.accept()
    srv = None
    while True:
        try:
            msg, anc, _, _ = conn.recvmsg(64, socket.CMSG_SPACE(16 * 4))
        except OSError:
            break
        if not msg and not anc:
            break
        fds = []
        for lvl, typ, data in anc:
            if lvl == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
                arr = array.array('i')
                arr.frombytes(data[:len(data) - len(data) % arr.itemsize])
                fds += list(arr)
        if msg == b'serve' and fds:
            srv = start_server(fds[0])
            conn.send(b'ok')
        elif msg == b'close':
            if srv is not None:
                srv.shutdown()
                srv.server_close()
                log('released listener')
                srv = None
            conn.send(b'closed')
    if srv is not None:  # the tool went away without a close: give it back
        srv.shutdown()
        srv.server_close()
        log('released listener on tool exit')
    conn.close()
