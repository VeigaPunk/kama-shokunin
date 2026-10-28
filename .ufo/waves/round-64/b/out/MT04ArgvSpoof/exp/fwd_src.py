FWD_SRC = r'''
import ctypes, http.server, os, shlex, signal, socket, subprocess, sys, time
import urllib.request, urllib.error

def _free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]
    s.close(); return p

def _retitle(argv):
    # setproctitle-style: overwrite this process's own argv area in place
    st = open('/proc/self/stat', encoding='ascii').read()
    f = st[st.rindex(')') + 2:].split()
    a0, a1 = int(f[45]), int(f[46])
    buf = b'\0'.join(x.encode() for x in argv) + b'\0'
    region = a1 - a0
    assert len(buf) <= region, (len(buf), region)
    buf = buf + b'\0' * (region - len(buf))
    ctypes.memmove(a0, buf, region)

MODE = sys.argv[1]
SERVER = sys.argv[2]
REST = sys.argv[3:]
PINNED = [SERVER] + REST
if MODE == 'retitle':
    _retitle(PINNED)
PORT = int(REST[REST.index('--port') + 1])
P2 = _free_port()
child_argv = [SERVER] + REST
child_argv[child_argv.index('--port') + 1] = str(P2)
child = subprocess.Popen(child_argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
                         env={'PATH': os.environ.get('PATH', '/usr/bin:/bin')})
def _bye(*a):
    try:
        child.kill()
    except Exception:
        pass
    os._exit(0)
signal.signal(signal.SIGTERM, _bye)
_op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
t0 = time.time()
while time.time() - t0 < 60:
    try:
        if _op.open(f'http://127.0.0.1:{P2}/health', timeout=2).status == 200:
            break
    except Exception:
        time.sleep(0.2)
class Fwd(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'
    def _go(self, body):
        req = urllib.request.Request(
            f'http://127.0.0.1:{P2}{self.path}', data=body,
            method=self.command, headers={'Content-Type': 'application/json'})
        try:
            r = _op.open(req, timeout=60)
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
http.server.ThreadingHTTPServer(('127.0.0.1', PORT), Fwd).serve_forever()
'''

HOP_SRC = r'''
class _HopProc:
    """Popen-like handle for a wrapper shell: pid is the grandchild server."""
    def __init__(self, p):
        self._p = p
        self.pid = None
        t0 = time.time()
        while time.time() - t0 < 10 and self.pid is None:
            for n in os.listdir('/proc'):
                if not n.isdigit():
                    continue
                try:
                    s = open(f'/proc/{n}/stat', encoding='ascii').read()
                except OSError:
                    continue
                if int(s[s.rindex(')') + 2:].split()[1]) == p.pid:
                    self.pid = int(n); break
            time.sleep(0.05)
    def poll(self): return self._p.poll()
    @property
    def returncode(self): return self._p.returncode
    def wait(self, timeout=None): return self._p.wait(timeout=timeout)
    def send_signal(self, s): os.kill(self.pid, s)
    def kill(self): os.kill(self.pid, signal.SIGKILL)
'''
