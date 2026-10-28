import http.server, importlib.util, json, os, threading
LANE='/home/vgpnk/Projects/shokunin/kama-shokunin'
WORK='/fast/scratch/hyaku/kama-r62/w/N01CompletionSecurity/poison-fast'
spec=importlib.util.spec_from_file_location('r62c1',os.path.join(LANE,'tools','round62-c1-counter.py'))
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
HITS=[]
class Canary(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n=int(self.headers.get('Content-Length') or 0); raw=self.rfile.read(n)
        HITS.append(raw.decode())
        b=json.dumps({'object':'text_completion','model':'kama-completion-probe',
          'system_fingerprint':'b9999-cafebabefeed',
          'choices':[{'text':'impostor','index':0,'finish_reason':'length'}],
          'usage':{'prompt_tokens':2,'completion_tokens':1,'total_tokens':3},
          'timings':{'predicted_n':1,'predicted_ms':1.0}}).encode()
        self.send_response(200); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self,*a): pass
srv=http.server.HTTPServer(('127.0.0.1',0),Canary)
threading.Thread(target=srv.serve_forever,daemon=True).start(); port=srv.server_address[1]
os.makedirs(os.path.join(WORK,'hold'),exist_ok=True)
json.dump({'schema':'kama-completion-hold/v1','port':port,'pid':999999,
  'alias':'kama-completion-probe','model_sha256':c.MODEL_SHA,'server_sha256':c.SERVER_SHA,
  'prompt':'planted','at':'2026-01-01T00:00:00Z'},
  open(os.path.join(WORK,'hold','hold.json'),'w'))
receipt,witness,nonce=c.witness_run(WORK,'/fast/scratch/hyaku/kama-r62/w/N01CompletionSecurity/stub/tools/kama-completion-live.py')
print(json.dumps({'counter_generated_nonce':nonce,
  'canary_received':HITS,
  'tool_receipt':receipt is not None,
  'witness':witness,
  'witness_digests_equal_pins':(witness or {}).get('server_sha256')==c.SERVER_SHA and (witness or {}).get('model_sha256')==c.MODEL_SHA,
  'leftover_hold_files':sorted(os.listdir(os.path.join(WORK,'hold')))},indent=1,sort_keys=True))
srv.shutdown()
