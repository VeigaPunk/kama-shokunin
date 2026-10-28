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

import tempfile
cases={}
cases['x1_port8080']=(['--port','8080'],None)
cases['x2_port0']=(['--port','0'],None)
cases['x3_port70000']=(['--port','70000'],None)
cases['x4_nomodel']=(['--model','/nonexistent/m.gguf'],None)
cases['x5_noserver']=(['--server','/nonexistent/llama-server'],None)
def holdfile(cmd,d):
    open(d+'/holdfile','w').write('x'); return cmd+['--hold-dir',d+'/holdfile'],None
cases['x6_holdfile']=([],holdfile)
def holdro(cmd,d):
    os.makedirs(d+'/ro',exist_ok=True); os.chmod(d+'/ro',0o500); return cmd+['--hold-dir',d+'/ro'],None
cases['x7_holdro']=([],holdro)
def outbad(cmd,d):
    i=cmd.index('--out'); cmd[i+1]=d+'/nodir/r.json'; return cmd,None
cases['x8_outbad']=([],outbad)
cases['x9_ready0']=(['--ready-timeout','0.01'],None)
cases['y1_ctx0']=(['--ctx','0'],None)
cases['y2_n0']=(['--n-predict','0'],None)
cases['y3_nneg']=(['--n-predict','-1'],None)
cases['y4_tempnan']=(['--temperature','nan'],None)
cases['y5_alias_empty']=(['--alias',''],None)
cases['y6_badsha_nonhex']=(['--model-sha256','zz'],None)
def workfile(cmd,d):
    open(d+'/wf','w').write('x'); cmd[cmd.index('--work')+1]=d+'/wf'; return cmd,None
cases['y7_workfile']=([],workfile)
cases['y8_ctxbig']=(['--ctx','100000000'],None)
cases['y9_threads0']=(['--threads','0'],None)
cases['yA_emptyserversha']=(['--server-sha256',''],None)
cases['yB_badutf8']=(['--prompt',b'ab\xffcd'],None)
sel=sys.argv[1:] or list(cases)
with cf.ThreadPoolExecutor(10) as ex:
    fs={ex.submit(run,n,*cases[n]):n for n in sel}
    out=[f.result() for f in cf.as_completed(fs)]
for o in sorted(out,key=lambda o:o['name']):
    o['stderr']=o['stderr'][-160:].replace('\n',' | '); print(json.dumps(o))
json.dump(out,open(S+'/summary2.json','w'),indent=1)
