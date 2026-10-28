import csv,subprocess,os,sys,time,re
repo='/home/vgpnk/Projects/shokunin/kama-shokunin'
S='/fast/scratch/hyaku/kama-r63/L1/diag-s'
os.makedirs(S,exist_ok=True)
tip=subprocess.check_output(['git','-C',repo,'rev-parse','master'],text=True).strip()
rows=list(csv.DictReader(open(repo+'/registry/capability-claims-r62.tsv'),delimiter='\t'))
env=dict(os.environ,TMPDIR=S)
for r in rows:
    cmd=r['run'].replace('%T',repo).replace('%S',S).replace('%R',repo).replace('TIPREV',tip)
    t=time.time()
    try:
        p=subprocess.run(['bash','-c',cmd],capture_output=True,text=True,timeout=1200,cwd=repo,env=env)
        out=p.stdout+p.stderr;rc=p.returncode
    except subprocess.TimeoutExpired: out='TIMEOUT';rc=124
    print(r['cap'],'rc=%s'%rc,'pat=%s'%(r['pattern'] in out),'%.0fs'%(time.time()-t),'|',out[-200:].replace('\n',' '),flush=True)
