import subprocess,time,json,os,sys,threading
S='/fast/scratch/hyaku/kama-r63/w/EX10ReceiptSize'
def run(v,i,hold=False):
    W=f'{S}/m-{v}{"-hold" if hold else ""}-{i}'; os.makedirs(W,exist_ok=True)
    out=f'{S}/m-{v}{"-hold" if hold else ""}-{i}.json'
    cmd=['python3',f'{S}/{v}/tools/kama-completion-live.py','--work',W,'--out',out,'--nonce','ex10-nonce-%d'%i]
    if hold:
        H=f'{S}/hold-{v}-{i}'; os.makedirs(H,exist_ok=True); cmd+=['--hold-dir',H]
        def rel():
            for _ in range(2000):
                if os.path.exists(H+'/ready.json'):
                    time.sleep(0.2); open(H+'/release','w').close(); return
                time.sleep(0.02)
        threading.Thread(target=rel,daemon=True).start()
    t=time.monotonic(); p=subprocess.run(cmd,capture_output=True,text=True); w=time.monotonic()-t
    d=json.load(open(out)); ch=d['checks']
    npass=sum(1 for c in ch.values() if c.get('passed'))
    print(f'{v}{" hold" if hold else ""} run{i}: rc={p.returncode} wall={w:.3f}s bytes={os.path.getsize(out)} checks={len(ch)} passed={npass} verdict={d["verdict"]} schema={d["schema"]} stdout={len(p.stdout)}B stderr={len(p.stderr)}B',flush=True)
for i in (1,2,3):
    for v in ('base','clone'): run(v,i)
for v in ('base','clone'): run(v,1,True)
