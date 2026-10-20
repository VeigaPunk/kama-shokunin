#!/usr/bin/env python3
"""Retain corrected counter reruns without overwriting the initial failed pass."""
import datetime, hashlib, json, subprocess, sys, time
from pathlib import Path
L=Path('/home/vgpnk/Projects/shokunin/kama-shokunin');W=L/'.ufo/waves/round-18';R=W/'runs';F=W/'frozen'
rev=subprocess.check_output(['git','-C',str(L),'rev-parse','master'],text=True).strip(); recs=[]
def run(name,args,want=0):
    at=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
    p=subprocess.run([str(x) for x in args],cwd=L,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (R/(name+'.stdout')).write_bytes(p.stdout);(R/(name+'.stderr')).write_bytes(p.stderr);(R/(name+'.exit')).write_text(f'exit={p.returncode}\n')
    recs.append({'name':name,'argv':[str(x) for x in args],'measured_commit':rev,'started_utc':at,'seconds':round(time.monotonic()-t,3),'exit':p.returncode,'expected_exit':want,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()})
    (R/'corrected-commands.json').write_text(json.dumps(recs,indent=1)+'\n');print(name,p.returncode,flush=True)
P=sys.executable
run('c1-counter-selftest-corrected',[P,W/'c1/measure.py','--selftest'])
run('c2-counter-selftest-corrected',[P,W/'c2/survivors.py','--selftest'])
run('c1-measure-corrected',[P,W/'c1/measure.py','--controls',L/'tests/llamacpp-live/controls.py','--frozen-tool',F/'tools_kama-llamacpp-live.py','--frozen-gate',F/'tests_llamacpp-live_check-receipt.py','--tool',L/'tools/kama-llamacpp-live.py','--gate',L/'tests/llamacpp-live/check-receipt.py','--probe',L/'tools/kama-probe.sh','--json','--out',R/'c1-measure-corrected.json'])
run('c2-survivors-corrected',[P,W/'c2/survivors.py','--json','--out',R/'c2-survivors-corrected.json'])
sys.exit(0 if all(r['exit']==r['expected_exit'] for r in recs) else 1)
