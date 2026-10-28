import subprocess, sys, os, json, socket, time, concurrent.futures as cf
S='/fast/scratch/hyaku/kama-r63/w/EX05CompletionEdges'
T=S+'/exp/tools/kama-completion-live.py'
def freeport():
    s=socket.socket(); s.bind(('127.0.0.1',0)); p=s.getsockname()[1]; s.close(); return p
def run(name, extra, pre=None, timeout=240):
    d=f'{S}/c_{name}'; os.makedirs(d+'/w',exist_ok=True)
    env={k:v for k,v in os.environ.items() if k in('PATH','HOME','LANG','LC_ALL')}
    cmd=['python3',T,'--work',d+'/w','--out',d+'/r.json']+extra
    cleanup=None
    if pre: cmd,cleanup=pre(cmd,d)
    t=time.monotonic()
    p=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=timeout,cwd=d)
    dt=time.monotonic()-t
    if cleanup: cleanup()
    open(d+'/stdout.txt','w').write(p.stdout); open(d+'/stderr.txt','w').write(p.stderr)
    r=None
    try: r=json.load(open(d+'/r.json'))
    except Exception as e: r={'_err':repr(e)}
    fails=[k for k,v in (r.get('checks') or {}).items() if v.get('evaluated') and not v.get('passed')]
    ne=[k for k,v in (r.get('checks') or {}).items() if not v.get('evaluated')]
    return dict(name=name,rc=p.returncode,dt=round(dt,1),verdict=r.get('verdict'),setup_error=r.get('setup_error'),failed=fails,notevald=ne,
      receipt=('_err' not in r),traceback=('Traceback' in p.stderr+p.stdout),stderr=p.stderr[-400:],stdout=p.stdout[:200])
cases={}
cases['a_model_sha']=(['--model-sha256','0'*64],None)
cases['b_server_sha']=(['--server-sha256','0'*64],None)
cases['c_temp05']=(['--temperature','0.5'],None)
cases['d_npredict1']=(['--n-predict','1'],None)
cases['e_nonascii']=(['--prompt','Die Katze saß auf der Mütze — 猫は座った 🐈 naïve'],None)
def hold(cmd,d):
    os.makedirs(d+'/hold',exist_ok=True); return cmd+['--hold-dir',d+'/hold','--hold-timeout','2'],None
cases['f_hold2s']=([],hold)
def busy(cmd,d):
    p=freeport(); h=subprocess.Popen([sys.executable,'-m','http.server',str(p),'--bind','127.0.0.1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,cwd=d)
    time.sleep(1.0); open(d+'/port.txt','w').write(str(p))
    return cmd+['--port',str(p)],(lambda:(h.terminate(),h.wait()))
cases['g_portbusy']=([],busy)
cases['h_ctx8']=(['--ctx','8'],None)
cases['i_emptyprompt']=(['--prompt',''],None)
cases['z_baseline']=([],None)
sel=sys.argv[1:] or list(cases)
with cf.ThreadPoolExecutor(9) as ex:
    fs={ex.submit(run,n,*cases[n]):n for n in sel}
    out=[f.result() for f in cf.as_completed(fs)]
for o in sorted(out,key=lambda o:o['name']): print(json.dumps(o))
json.dump(out,open(S+'/summary.json','w'),indent=1)
