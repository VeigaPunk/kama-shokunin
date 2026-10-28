import os,subprocess,time,json,sys
S='/fast/scratch/hyaku/kama-r63/w/EX03BoundRows'
R='/home/vgpnk/Projects/shokunin/kama-shokunin'
TIP='03a6a1d850902a66a13dfad33f89cf3a8b759a09'
env={'PATH':os.environ['PATH'],'HOME':os.environ['HOME'],'LANG':os.environ['LANG'],'TMPDIR':S+'/tmp'}
rows=[l.rstrip('\n').split('\t') for l in open(S+'/claims.tsv')][1:]
def pg():
    p=subprocess.run(['pgrep','-x','llama-server'],capture_output=True,text=True)
    return sorted(int(x) for x in p.stdout.split())
res=[]
for r in rows:
    cap,quote,binding,run,pat,verdict,obs,note=r
    cmd=run.replace('%T',S+'/tip').replace('%S',S+'/s').replace('%R',R).replace('TIPREV',TIP)
    before=pg() if cap=='context-capacity-receipt' else None
    t=time.time()
    try:
        p=subprocess.run(['bash','-c',cmd],capture_output=True,text=True,timeout=900,cwd=S+'/tip',env=env)
        out=p.stdout+p.stderr; rc=p.returncode
    except subprocess.TimeoutExpired as e:
        out='TIMEOUT';rc=124
    dt=time.time()-t
    after=pg() if before is not None else None
    open(f'{S}/out/{cap}.txt','w').write(out)
    d=dict(cap=cap,rc=rc,pattern_present=pat in out,wall=round(dt,2),recorded=verdict,bytes=len(out),before=before,after=after,alt_present=('host-not-idle-before-K1' in out) if before is not None else None)
    print(json.dumps(d),flush=True); res.append(d)
json.dump(res,open(S+'/res.json','w'))
