import importlib.util, http.server, json, os, sys, threading, subprocess
sys.dont_write_bytecode = True
S = '/fast/scratch/hyaku/kama-r63/w/SN01LoopbackSecurity'
spec = importlib.util.spec_from_file_location('ctr', f'{S}/clone/tools/round63-c1-counter.py')
ctr = importlib.util.module_from_spec(spec); spec.loader.exec_module(ctr)
seen = []
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0); body = self.rfile.read(n)
        seen.append(self.path)
        b = b'{"object":"text_completion","model":"x","id":"s","created":1,"system_fingerprint":"b1-abcdef123","choices":[{"text":" x","index":0,"finish_reason":"length"}],"usage":{"prompt_tokens":1,"completion_tokens":1,"total_tokens":2}}'
        if self.path == '/tokenize': b = b'{"tokens":[1]}'
        self.send_response(200); self.send_header('Content-Type','application/json')
        self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass
srv = http.server.HTTPServer(('127.0.0.1', 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_address[1]
W = f'{S}/exp/stale-work'
subprocess.run(['rm', '-rf', W]); os.makedirs(f'{W}/hold')
# a hold.json left behind by an earlier run that was SIGKILLed mid-hold; it names a live, unrelated listener
json.dump({'schema': 'kama-completion-hold/v1', 'port': port, 'pid': 424242, 'alias': 'kama-completion-probe',
           'model_sha256': ctr.MODEL_SHA, 'server_sha256': ctr.SERVER_SHA, 'prompt': 'stale', 'at': 'stale'},
          open(f'{W}/hold/hold.json', 'w'))
receipt, witness, nonce = ctr.witness_run(W, f'{S}/clone/tools/kama-completion-live.py')
print(json.dumps({'stub_port': port, 'stub_received_paths': seen,
                  'witness_port': (witness or {}).get('port'), 'witness_pid': (witness or {}).get('pid'),
                  'witness_listener_owned': (witness or {}).get('listener_owned'),
                  'new_run_receipt_port': (receipt or {}).get('port'),
                  'new_run_verdict': (receipt or {}).get('verdict')}, indent=1))
