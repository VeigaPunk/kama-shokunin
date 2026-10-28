import http.server, json, os, subprocess, sys, threading
LANE='/home/vgpnk/Projects/shokunin/kama-shokunin'
SCRATCH='/fast/scratch/hyaku/kama-r62/w/N01CompletionSecurity/counter-proxy'
ALIAS='kama-completion-probe'
HITS=[]
class Proxy(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n=int(self.headers.get('Content-Length') or 0); raw=self.rfile.read(n)
        try: req=json.loads(raw or b'{}')
        except ValueError: req={}
        HITS.append({'path':self.path,'prompt':req.get('prompt')})
        if 'prompt' not in req:
            body=json.dumps({'error':{'message':'no prompt'}}).encode(); self.send_response(400)
        else:
            body=json.dumps({'object':'text_completion','model':ALIAS,
                'system_fingerprint':'b9999-cafebabefeed',
                'choices':[{'text':'proxy-invented','index':0,'finish_reason':'length'}],
                'usage':{'prompt_tokens':5,'completion_tokens':8,'total_tokens':13},
                'timings':{'predicted_n':8,'predicted_ms':12.0}}).encode(); self.send_response(200)
        self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body)))
        self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        HITS.append({'path':self.path,'method':'GET'}); self.send_response(500)
        self.send_header('Content-Length','0'); self.end_headers()
    def log_message(self,*a): pass
srv=http.server.HTTPServer(('127.0.0.1',0),Proxy)
threading.Thread(target=srv.serve_forever,daemon=True).start()
pp=srv.server_address[1]
os.makedirs(SCRATCH,exist_ok=True)
env=dict(os.environ); env.update({'http_proxy':f'http://127.0.0.1:{pp}','HTTP_PROXY':f'http://127.0.0.1:{pp}',
  'all_proxy':f'http://127.0.0.1:{pp}','ALL_PROXY':f'http://127.0.0.1:{pp}'})
env.pop('no_proxy',None); env.pop('NO_PROXY',None); env['TMPDIR']=SCRATCH
p=subprocess.run([sys.executable,os.path.join(LANE,'tools','round62-c1-counter.py'),
   '--repo',LANE,'--tip','65d7cad0fce90e34de37527cde22e97b63b118bf','--work',SCRATCH],
   capture_output=True,env=env,timeout=280)
print('counter_rc=',p.returncode); print(p.stdout.decode().strip()); print('stderr:',p.stderr.decode()[-300:])
print('proxy_hits=',json.dumps(HITS)[:1200])
srv.shutdown()
