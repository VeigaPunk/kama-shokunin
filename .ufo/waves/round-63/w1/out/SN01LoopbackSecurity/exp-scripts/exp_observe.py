import importlib.util, http.server, json, socket, sys, threading
sys.dont_write_bytecode = True
S = '/fast/scratch/hyaku/kama-r63/w/SN01LoopbackSecurity'
spec = importlib.util.spec_from_file_location('ctr', f'{S}/clone/tools/round63-c1-counter.py')
ctr = importlib.util.module_from_spec(spec); spec.loader.exec_module(ctr)
seen = []
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0); body = self.rfile.read(n)
        seen.append((self.path, body[:80].decode(errors='replace')))
        b = b'{"object":"text_completion","choices":[{"text":" x","index":0}]}'
        self.send_response(200); self.send_header('Content-Type','application/json')
        self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass
srv = http.server.HTTPServer(('127.0.0.1', 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_address[1]
# hold.json-shaped document naming an arbitrary port (the counter reads h.get('port') unchecked)
w = ctr.observe(port, 999999, {'alias': 'x', 'model_sha256': 'x', 'server_sha256': 'x'}, ctr.load_live_mod(f'{S}/clone/tools/kama-completion-live.py'), 'r63-probe')
print(json.dumps({'stub_port': port, 'stub_received': seen, 'observe_listener_owned': w['listener_owned']}))
print('refused check in observe path: none (observe calls http() directly)')
