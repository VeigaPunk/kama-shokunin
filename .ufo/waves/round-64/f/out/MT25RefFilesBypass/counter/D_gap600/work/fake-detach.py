
import argparse, json, os, signal, socket, subprocess, sys, time
import http.server, threading, urllib.request, urllib.error
ap = argparse.ArgumentParser()
for a in ('--nonce', '--work', '--server', '--model', '--model-sha256',
          '--server-sha256', '--alias', '--hold-dir', '--hold-timeout',
          '--out', '--prompt', '--n-predict', '--seed'):
    ap.add_argument(a)
A = ap.parse_args()
TPL = json.load(open(os.environ['KAMA_FAKE_TEMPLATE']))
MODE = os.environ['KAMA_FAKE_MODE']
os.makedirs(A.work, exist_ok=True)
def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]
    s.close(); return p
def spawn_real(port, extra_env=None, exe=None):
    env = {k: v for k, v in os.environ.items()
           if k in ('PATH', 'HOME', 'LANG', 'LC_ALL')}
    env.update(extra_env or {})
    return subprocess.Popen(
        [exe or A.server, '--model', A.model, '--alias', A.alias,
         '--port', str(port), '--host', '127.0.0.1', '-c', '512', '-t', '1'],
        stdout=open(os.path.join(A.work, 'srv.log'), 'wb'),
        stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env)
def wait_health(port, t=60):
    import urllib.request
    t0 = time.time()
    while time.time() - t0 < t:
        try:
            r = urllib.request.urlopen(
                f'http://127.0.0.1:{port}/health', timeout=2)
            if r.status == 200: return True
        except Exception:
            pass
        time.sleep(0.2)
    return False
def hold_and_release(doc):
    hp = os.path.join(A.hold_dir, 'hold.json')
    json.dump(doc, open(hp, 'w'))
    t0 = time.time()
    while time.time() - t0 < float(A.hold_timeout):
        if os.path.exists(os.path.join(A.hold_dir, 'release')): break
        time.sleep(0.1)
    try: os.unlink(hp)
    except OSError: pass
def write_receipt(child_pid, port, holders):
    r = json.loads(json.dumps(TPL))
    r['nonce'] = A.nonce
    r['child_pid'] = child_pid
    r['port'] = port
    r['listener_holders'] = holders
    r['hold'] = {'dir': A.hold_dir, 'released': True}
    json.dump(r, open(A.out, 'w'))
def hold_doc(pid, port):
    return {'schema': 'kama-completion-hold/v1', 'port': port, 'pid': pid,
            'alias': A.alias, 'model_sha256': A.model_sha256,
            'server_sha256': A.server_sha256, 'prompt': 'x',
            'at': '2026-10-28T00:00:00Z'}
def good_holders(pid):
    return [{'pid': pid, 'exe': A.server, 'exe_sha256': A.server_sha256}]
class Fwd(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'
    target = 0
    def _go(self, body):
        import urllib.request
        req = urllib.request.Request(
            f'http://127.0.0.1:{Fwd.target}{self.path}', data=body,
            method=self.command, headers={'Content-Type': 'application/json'})
        op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            r = op.open(req, timeout=30)
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
def serve(handler, port):
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv

port = free_port()
pid_file = os.path.join(A.work, 'detached.pid')
if os.fork() == 0:
    if os.fork() == 0:
        os.setsid()
        p = spawn_real(port)
        open(pid_file, 'w').write(str(p.pid)); p.wait(); os._exit(0)
    os._exit(0)
wait_health(port)
time.sleep(0.5)
pid = int(open(pid_file).read())
hold_and_release(hold_doc(pid, port))
os.kill(pid, signal.SIGTERM)
write_receipt(pid, port, good_holders(pid))
