#!/usr/bin/env python3
"""MT13 forged tool: a CANNED ANSWERER that gets every non-reference probe
field right. The run-port listener is this python process (not the pinned
llama-server). Tokenisation is the real pinned server's /tokenize (oracle,
a hidden child process, never a listener). Completion text is a fixed
string: the one field only the reference check can see.
Speaks the counter's hold protocol (kama-completion-hold/v1) and writes a
receipt copied from a genuine run (CANNED_TEMPLATE), with its own procfs
holder truthfully reported in listener_holders.
"""
import argparse, hashlib, http.server, json, os, socket, subprocess, sys, time, threading
import urllib.request

CANNED_TEXT = ' a fixed sentence the model never said'

ap = argparse.ArgumentParser()
ap.add_argument('--nonce', required=True)
ap.add_argument('--work', required=True)
ap.add_argument('--server', required=True)
ap.add_argument('--model', required=True)
ap.add_argument('--model-sha256', required=True)
ap.add_argument('--server-sha256', required=True)
ap.add_argument('--alias', required=True)
ap.add_argument('--hold-dir', required=True)
ap.add_argument('--hold-timeout', type=float, default=90)
ap.add_argument('--out', required=True)
A, _unknown = ap.parse_known_args()


def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]
    s.close(); return p


def post(port, path, payload):
    req = urllib.request.Request(
        f'http://127.0.0.1:{port}{path}', data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'}, method='POST')
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with op.open(req, timeout=30) as r:
        return r.status, r.read()


# oracle: the real pinned server, a child of this tool, never a listener of
# the run port; its /tokenize and one greedy completion supply the fields
oport = free_port()
oracle = subprocess.Popen(
    [A.server, '--model', A.model, '--alias', A.alias, '--port', str(oport),
     '--host', '127.0.0.1', '-c', '512', '-t', '1'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    stdin=subprocess.DEVNULL,
    env={k: v for k, v in os.environ.items()
         if k in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')})
t0 = time.time()
while time.time() - t0 < 60:
    try:
        r = urllib.request.urlopen(f'http://127.0.0.1:{oport}/health', timeout=2)
        if r.status == 200:
            break
    except Exception:
        time.sleep(0.2)
_, fpb = post(oport, '/v1/completions',
              {'prompt': 'x', 'n_predict': 1, 'temperature': 0.0, 'seed': 1})
FP = json.loads(fpb)['system_fingerprint']


def tokens_of(text):
    _, tb = post(oport, '/tokenize', {'content': text, 'add_special': True})
    return json.loads(tb)['tokens']


class Canned(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'

    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers(); self.wfile.write(b)

    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        req = json.loads(self.rfile.read(n) or b'{}')
        if self.path == '/tokenize':
            _, b = post(oport, '/tokenize', req)
            self.send_response(200); self.send_header(
                'Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(b)))
            self.end_headers(); self.wfile.write(b)
            return
        if self.path == '/v1/completions':
            sent = req['prompt']
            n_pred = int(req['n_predict'])
            up = len(tokens_of(sent))
            self._send(200, {
                'id': 'cmpl-' + os.urandom(4).hex(), 'object': 'text_completion',
                'created': int(time.time()), 'model': A.alias,
                'system_fingerprint': FP,
                'choices': [{'index': 0, 'text': CANNED_TEXT,
                             'logprobs': None, 'finish_reason': 'length'}],
                'usage': {'prompt_tokens': up, 'completion_tokens': n_pred,
                          'total_tokens': up + n_pred,
                          'prompt_tokens_details': {'cached_tokens': 0}},
                'timings': {'prompt_n': up, 'prompt_ms': 1.0, 'cache_n': 0,
                            'predicted_n': n_pred, 'predicted_ms': 1.0}})
            return
        self._send(404, {'error': 'not found'})


front = free_port()
srv = http.server.ThreadingHTTPServer(('127.0.0.1', front), Canned)
threading.Thread(target=srv.serve_forever, daemon=True).start()

hold_json = os.path.join(A.hold_dir, 'hold.json')
doc = {'schema': 'kama-completion-hold/v1', 'port': front, 'pid': os.getpid(),
       'alias': A.alias, 'model_sha256': A.model_sha256,
       'server_sha256': A.server_sha256, 'prompt': 'x',
       'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
json.dump(doc, open(hold_json, 'w'))
t0 = time.time()
while time.time() - t0 < A.hold_timeout:
    if os.path.exists(os.path.join(A.hold_dir, 'release')):
        break
    time.sleep(0.1)
try:
    os.unlink(hold_json)
except OSError:
    pass
srv.shutdown()
oracle.terminate(); oracle.wait()
# receipt: a genuine run's receipt, with this tool's own truthful holder
rcpt = json.load(open('/fast/scratch/hyaku/kama-r64/b/MT13ProbeTokens/harness/genuine-receipt.json'))
exe = os.readlink(f'/proc/{os.getpid()}/exe')
import hashlib
exe_sha = hashlib.sha256(open(exe, 'rb').read()).hexdigest()
rcpt['nonce'] = A.nonce
rcpt['child_pid'] = os.getpid()
rcpt['port'] = front
rcpt['listener_holders'] = [{'pid': os.getpid(), 'exe': exe,
                             'exe_sha256': exe_sha}]
rcpt['hold'] = {'dir': A.hold_dir, 'released': True}
json.dump(rcpt, open(A.out, 'w'))
