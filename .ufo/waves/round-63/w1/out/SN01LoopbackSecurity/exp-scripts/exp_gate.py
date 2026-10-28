#!/usr/bin/env python3
"""E4: pick_port -> bind race and the first-answer ownership gate, against the lane tool's run().
G1: a stranger on the picked port answers /health 200 {"status":"ok"} before the child binds.
G2: a stranger on the picked port answers nothing useful (404 everywhere).
G3: a stranger on 127.0.0.2 with the same port while the child binds 127.0.0.1 (gate semantics)."""
import argparse, importlib.util, json, os, socket, sys, threading, time
import http.server

S = '/fast/scratch/hyaku/kama-r63/w/SN01LoopbackSecurity'
TOOL = f'{S}/clone/tools/kama-completion-live.py'
OUT = f'{S}/exp/gate'
os.makedirs(OUT, exist_ok=True)
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('ct', TOOL)
ct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ct)
LIVE = ct._live


def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p


def stranger(bind_ip, port, health_ok, log):
    class H(http.server.BaseHTTPRequestHandler):
        def _send(self, code, body):
            b = body.encode()
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(b)))
            self.end_headers(); self.wfile.write(b)

        def do_GET(self):
            log.append(('GET', self.path))
            if health_ok and self.path == '/health':
                self._send(200, '{"status":"ok"}')
            else:
                self._send(404, '{"error":"nope"}')

        def do_POST(self):
            n = int(self.headers.get('Content-Length') or 0); self.rfile.read(n)
            log.append(('POST', self.path))
            self._send(200, '{"object":"text_completion","choices":[{"text":"STRANGER","index":0}]}')

        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer((bind_ip, port), H)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def args_for(work, out):
    return argparse.Namespace(
        server=None, work=work, model=ct.DEFAULT_MODEL,
        model_sha256=ct.DEFAULT_MODEL_SHA, server_sha256=ct.DEFAULT_SERVER_SHA,
        alias='kama-completion-probe', ctx=512, threads=1,
        prompt='The cat sat on the', n_predict=8, temperature=0.0, seed=7,
        port=None, ready_timeout=20.0, hold_dir=None, hold_timeout=30.0,
        out=out, nonce='gate')


results = {}
for name, health_ok, extra_ip in (('G1_first_answer_health_ok', True, None),
                                  ('G2_first_answer_404', False, None),
                                  ('G3_secondary_loopback_127_0_0_2', None, '127.0.0.2')):
    P = free_port()
    log = []
    srvs = []
    if extra_ip:
        # G3: child binds 127.0.0.1:P normally; the stranger holds 127.0.0.2:P
        srvs.append(stranger(extra_ip, P, True, log))
        orig = LIVE.pick_port
        LIVE.pick_port = lambda refused, requested=None, _p=P: _p
    else:
        srvs.append(stranger('127.0.0.1', P, health_ok, log))
        LIVE.pick_port = lambda refused, requested=None, _p=P: _p
    work = f'{OUT}/{name}-work'
    rec_path = f'{OUT}/{name}-receipt.json'
    t0 = time.monotonic()
    try:
        receipt, rc = ct.run(args_for(work, rec_path))
    finally:
        LIVE.pick_port = globals().get('orig_pick', None) or LIVE.pick_port
    elapsed = round(time.monotonic() - t0, 2)
    for s in srvs:
        s.shutdown(); s.server_close()
    child = receipt.get('child_pid')
    child_alive = None
    if child:
        try:
            os.kill(child, 0); child_alive = True
        except ProcessLookupError:
            child_alive = False
    results[name] = {
        'rc': rc, 'verdict': receipt.get('verdict'), 'port': P,
        'setup_error': receipt.get('setup_error'), 'child_pid': child,
        'child_alive_after_run': child_alive, 'elapsed_s': elapsed,
        'stranger_requests': log,
        'listener_owned_check': receipt.get('checks', {}).get('listener_owned'),
        'failed_checks': {k: v['reason'] for k, v in receipt.get('checks', {}).items() if v.get('evaluated') and not v.get('passed')},
    }
    print(name, json.dumps(results[name]))
json.dump(results, open(f'{OUT}/summary.json', 'w'), indent=1)
