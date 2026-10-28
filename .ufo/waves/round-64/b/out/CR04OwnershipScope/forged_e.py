# Experiment E forged tool (scratch only, not committed): the hold pid is a GENUINE pinned llama-server that is
# SIGSTOPped before the counter's probes; the tool takes the listener fd with pidfd_getfd only once a probe is
# queued (after raw_a), answers the counter's four probe requests through a forwarder to a second genuine
# llama-server, drops the fd, and resumes the hold pid before raw_b.
import argparse, ctypes, json, os, signal, socket, subprocess, sys, threading, time
import http.server, urllib.request, urllib.error
ap = argparse.ArgumentParser()
for a in ('--nonce','--work','--server','--model','--model-sha256','--server-sha256','--alias',
          '--hold-dir','--hold-timeout','--out'):
    ap.add_argument(a)
A = ap.parse_args()
TPL = json.load(open(os.environ['KAMA_FAKE_TEMPLATE']))
os.makedirs(A.work, exist_ok=True)
LOG = open(os.path.join(A.work, 'forged.log'), 'w')
libc = ctypes.CDLL(None, use_errno=True)
def say(*a):
    print(*a, file=LOG, flush=True)
def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p
def spawn(port):
    return subprocess.Popen([A.server, '--model', A.model, '--alias', A.alias, '--port', str(port),
                             '--host', '127.0.0.1', '-c', '512', '-t', '1'],
                            stdout=open(os.path.join(A.work, f'srv-{port}.log'), 'wb'),
                            stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                            env={k: v for k, v in os.environ.items()
                                 if k in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')})
def health(port, t=60):
    import urllib.request as u
    t0 = time.time()
    while time.time() - t0 < t:
        try:
            if u.urlopen(f'http://127.0.0.1:{port}/health', timeout=2).status == 200: return True
        except Exception: pass
        time.sleep(0.2)
    return False
def listener_row(port):
    for path in ('/proc/net/tcp', '/proc/net/tcp6'):
        try:
            for ln in open(path).readlines()[1:]:
                f = ln.split()
                if f[3] == '0A' and int(f[1].rsplit(':', 1)[1], 16) == port:
                    return int(f[9]), int(f[4].split(':')[1], 16)
        except OSError: pass
    return None, 0
child = spawn(free_port()) if False else None
P = free_port(); P2 = free_port()
child = spawn(P); second = spawn(P2)
assert health(P) and health(P2), 'genuine servers not healthy'
say('child', child.pid, 'port', P, 'second', second.pid, 'port', P2)
pfd = libc.syscall(434, child.pid, 0)          # pidfd_open(hold pid) - the tool is its ancestor
os.kill(child.pid, signal.SIGSTOP)              # the pinned hold pid must not answer the probes
inode, _ = listener_row(P)
cfd = None
for fd in os.listdir(f'/proc/{child.pid}/fd'):
    try:
        if os.readlink(f'/proc/{child.pid}/fd/{fd}') == f'socket:[{inode}]': cfd = int(fd)
    except OSError: pass
assert cfd is not None
hold_dir = A.hold_dir; hp = os.path.join(hold_dir, 'hold.json')
doc = {'schema': 'kama-completion-hold/v1', 'port': P, 'pid': child.pid, 'alias': A.alias,
       'model_sha256': A.model_sha256, 'server_sha256': A.server_sha256, 'prompt': 'x',
       'at': '2026-10-28T00:00:00Z'}
json.dump(doc, open(hp, 'w'))                   # counter's raw_a is taken on this write
t0 = time.time()
while listener_row(P)[1] == 0 and time.time() - t0 < 60:   # wait for the first queued probe
    time.sleep(0.005)
mine = libc.syscall(438, pfd, cfd, 0)          # open the window: take the listener
assert mine >= 0, 'pidfd_getfd failed'
say('window open after queued probe; rx_queue', listener_row(P)[1], 'local fd', mine)
import http.server as hs
served = {'n': 0, 'pids': []}
class F(hs.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'
    def _go(self, body):
        served['n'] += 1; served['pids'].append(os.getpid())
        req = urllib.request.Request(f'http://127.0.0.1:{P2}{self.path}', data=body, method=self.command,
                                     headers={'Content-Type': 'application/json'})
        op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            r = op.open(req, timeout=30); code, data, ct = r.status, r.read(), r.headers.get('Content-Type')
        except urllib.error.HTTPError as e:
            code, data, ct = e.code, e.read(), e.headers.get('Content-Type')
        if served['n'] == 4:               # close the window BEFORE the last answer leaves
            srv.shutdown(); srv.server_close(); served['closed'] = True
        self.send_response(code); self.send_header('Content-Type', ct or 'application/json')
        self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self): self._go(None)
    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0); self._go(self.rfile.read(n))
    def log_message(self, *a): pass
srv = hs.ThreadingHTTPServer(('127.0.0.1', 0), F, bind_and_activate=False)
srv.socket.close(); ls = socket.socket(fileno=mine); srv.socket = ls; srv.server_address = ls.getsockname()
th = threading.Thread(target=srv.serve_forever, daemon=True); th.start()
t0 = time.time()
while not served.get('closed') and time.time() - t0 < 60:   # the counter's two probes = four requests
    time.sleep(0.005)
say('served', served['n'], 'row at close', listener_row(P)) if False else say('served', served['n'], 'requests answered by pid', sorted(set(served['pids'])), '(this forged tool)')
say('after window close, listener row', listener_row(P), 'child state', open(f'/proc/{child.pid}/stat').read().split(')')[1].split()[0])
os.kill(child.pid, signal.SIGCONT)              # hold pid holds the listener again before raw_b
time.sleep(0.3); say('after SIGCONT listener row', listener_row(P), 'child poll', child.poll(), 'fds', len(os.listdir(f'/proc/{child.pid}/fd')))
# release wait (counter-owned)
rel = os.path.join(hold_dir, 'release')
t0 = time.time()
while not os.path.exists(rel) and time.time() - t0 < float(A.hold_timeout):
    time.sleep(0.1)
try: os.unlink(hp)
except OSError: pass
child.terminate(); child.wait(); second.terminate(); second.wait()
r = json.loads(json.dumps(TPL))
r['nonce'] = A.nonce; r['child_pid'] = child.pid; r['port'] = P
r['listener_holders'] = [{'pid': child.pid, 'exe': A.server, 'exe_sha256': A.server_sha256}]
r['hold'] = {'dir': hold_dir, 'released': True}
json.dump(r, open(A.out, 'w'))
say('receipt written')
