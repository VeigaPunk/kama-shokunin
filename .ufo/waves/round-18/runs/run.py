#!/usr/bin/env python3
"""L1 round-18 official commands. Artifacts are raw stdout/stderr plus explicit exits."""
from pathlib import Path
import datetime, hashlib, json, shutil, subprocess, sys, tempfile, time
L=Path('/home/vgpnk/Projects/shokunin/kama-shokunin'); W=L/'.ufo/waves/round-18'; R=W/'runs'; F=W/'frozen'
records=[]
rev=subprocess.check_output(['git','-C',str(L),'rev-parse','master'],text=True).strip()
dirty_lines=[line for line in subprocess.check_output(
    ['git','-C',str(L),'status','--porcelain'],text=True).splitlines()
    if not ((line[3:].startswith('.ufo/waves/round-18/runs/')
             and not line[3:].endswith('/run.py'))
            or line[3:].startswith('.ufo/waves/round-18/live-recovery/')
            or line[3:].startswith('.ufo/waves/round-19/'))]
dirty='\n'.join(dirty_lines)
if dirty:
    print('refusing: lane working tree is dirty; commit the measured bytes first:\n'+dirty,file=sys.stderr)
    sys.exit(2)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(name,argv,want=0,cwd=L,timeout=7200):
    t=time.monotonic(); at=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        p=subprocess.run([str(a) for a in argv],cwd=str(cwd),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
        rc=p.returncode; out=p.stdout; err=p.stderr
    except subprocess.TimeoutExpired as e:
        rc=124;out=e.stdout or b'';err=(e.stderr or b'')+b'\nL1 command timeout\n'
    (R/(name+'.stdout')).write_bytes(out);(R/(name+'.stderr')).write_bytes(err)
    (R/(name+'.exit')).write_text('exit='+str(rc)+'\n')
    rec={'name':name,'argv':[str(a) for a in argv],'cwd':str(cwd),'started_utc':at,'seconds':round(time.monotonic()-t,3),'exit':rc,'expected_exit':want,'as_expected':rc==want,'stdout_sha256':hashlib.sha256(out).hexdigest(),'stderr_sha256':hashlib.sha256(err).hexdigest()}
    records.append(rec);(R/'commands.json').write_text(json.dumps({'measured_commit':rev,'python':sys.version,'commands':records},indent=1)+'\n')
    print(name,'exit='+str(rc),'want='+str(want),flush=True)
    return rc
P=sys.executable
for name,path,args in [
 ('tool-selftest',L/'tools/kama-llamacpp-live.py',[]),
 ('gate-selftest',L/'tests/llamacpp-live/check-receipt.py',[]),
 ('controls-selftest',L/'tests/llamacpp-live/controls.py',[]),
 ('checker-selftest',L/'tests/probe-verdicts/check.py',['--probe',L/'tools/kama-probe.sh','--json']),
 ('fault-controls-selftest',L/'tests/probe-verdicts/fault-controls.py',['--json']),
 ('append-only-selftest',L/'tools/sources-append-only.py',[]),
 ('provenance-selftest',W/'dispatch-provenance.py',[]),
 ('c1-counter-selftest',W/'c1/measure.py',[]),
 ('c2-counter-selftest',W/'c2/survivors.py',[]),
 ('source-pins-selftest',W/'sources/pin.py',[]),
]: run(name,[P,path,'--selftest',*args])
c1=[P,W/'c1/measure.py','--controls',L/'tests/llamacpp-live/controls.py','--frozen-tool',F/'tools_kama-llamacpp-live.py','--frozen-gate',F/'tests_llamacpp-live_check-receipt.py','--tool',L/'tools/kama-llamacpp-live.py','--gate',L/'tests/llamacpp-live/check-receipt.py','--probe',L/'tools/kama-probe.sh','--json']
run('c1-measure',c1+['--out',R/'c1-measure.json'])
run('c1-self-mutants',c1+['--self-mutants','--baseline-runs','1','--out',R/'c1-self-mutants.json'])
# Real producer/gate runs: pin caller-selected bytes, never resolve the binary from PATH.
server=Path('/home/vgpnk/.local/opt/llama-b11755/llama-server')
impl=server.parent/'libllama-server-impl.so'
if not impl.is_file():
    raise SystemExit(f'impl library missing: {impl}')
model=Path('/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf')
model_sha='270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
import importlib.util
_spec=importlib.util.spec_from_file_location('kama_live_tool',L/'tools/kama-llamacpp-live.py')
_tool_mod=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_tool_mod)
_tree,_tree_sha=_tool_mod.install_tree(str(server.resolve()))
if not isinstance(_tree,dict) or not _tree or not isinstance(_tree_sha,str) or len(_tree_sha)!=64:
    raise SystemExit('install-tree digest unavailable')
tree_sha=_tree_sha
for i in range(1,4):
    receipt=W/'live-recovery'/('receipt-'+str(i)+'.json');receipt.parent.mkdir(parents=True,exist_ok=True)
    run('live-'+str(i),[P,L/'tools/kama-llamacpp-live.py','--server',server,'--model',model,'--model-sha256',model_sha,'--alias','kama-r18-live','--out',receipt])
    run('live-gate-'+str(i),[P,L/'tests/llamacpp-live/check-receipt.py',receipt,'--require-schema','v3','--expect-model-sha256',model_sha,'--expect-server-sha256',sha(server),'--expect-server-impl-sha256',sha(impl),'--expect-install-tree-sha256',tree_sha,'--expect-probe-sha256',sha(L/'tools/kama-probe.sh'),'--expect-tool-sha256',sha(L/'tools/kama-llamacpp-live.py')])
grid=[P,L/'tests/llamacpp-live/install-tree-grid.py','--gate',L/'tests/llamacpp-live/check-receipt.py','--receipt',W/'live-recovery'/'receipt-1.json','--model-sha',model_sha,'--server-sha',sha(server),'--impl-sha',sha(impl),'--probe-sha',sha(L/'tools/kama-probe.sh'),'--tool-sha',sha(L/'tools/kama-llamacpp-live.py')]
run('tree-grid-no-pin',list(grid),want=1)
run('tree-grid-pin',grid+['--tree-sha',tree_sha])
run('tree-pin-negative',[P,L/'tests/llamacpp-live/check-receipt.py',W/'live-recovery'/'receipt-1.json','--require-schema','v3','--expect-model-sha256',model_sha,'--expect-server-sha256',sha(server),'--expect-server-impl-sha256',sha(impl),'--expect-probe-sha256',sha(L/'tools/kama-probe.sh'),'--expect-tool-sha256',sha(L/'tools/kama-llamacpp-live.py'),'--expect-install-tree-sha256','0'*64],want=1)
# Historical receipt compatibility with each receipt's own four recorded pins.
legacy=[L/'.ufo/waves/round-16/live/receipt.json',L/'.ufo/waves/round-16/live/receipt-frozen-probe.json']+[L/('.ufo/waves/round-17/live/receipt-'+str(i)+'.json') for i in range(1,4)]
for i,p in enumerate(legacy):
    d=json.loads(p.read_text()); pins=[]
    for key,flag in [('model','model'),('server','server'),('probe','probe'),('tool','tool')]:
        pins+=['--expect-'+flag+'-sha256',d[key]['sha256']]
    run('legacy-frozen-'+str(i),[P,F/'tests_llamacpp-live_check-receipt.py',p,*pins])
    run('legacy-current-'+str(i),[P,L/'tests/llamacpp-live/check-receipt.py',p,*pins])
    if i==1:
        run('legacy-wrong-probe-pin',[P,L/'tests/llamacpp-live/check-receipt.py',p,'--expect-probe-sha256',sha(L/'tools/kama-probe.sh')],want=1)
# No git-writing test runs in the lane: isolated clone only.
with tempfile.TemporaryDirectory(prefix='kama-r18-L1-noharm-') as tmp:
    clone=Path(tmp)/'lane'
    subprocess.run(['git','clone','-q',str(L),str(clone)],check=True)
    run('snapshot-clone',['bash',clone/'tools/test-snapshot.sh'],cwd=clone)
    run('r16-measure-clone',[P,clone/'.ufo/waves/round-16/measure.py'],cwd=clone)
# Full named C2 universe, serial child runs and retained raw evidence.
# The counter's --out is exclusive-create by design; keep its JSON on
# stdout so a rerun never has to clobber retained evidence.
run('c2-survivors',[P,W/'c2/survivors.py','--json'])
identity={}
for rel in ['tools/kama-probe.sh']+[str(p.relative_to(L)) for p in sorted((L/'tests/probe-verdicts').glob('*.json'))]:
    old=subprocess.check_output(['git','-C',str(L),'show','e75cf680b53484a61709ee1b2787d8dbc6419f74:'+rel]);new=(L/rel).read_bytes()
    identity[rel]={'before_sha256':hashlib.sha256(old).hexdigest(),'after_sha256':hashlib.sha256(new).hexdigest(),'same':old==new}
(R/'probe-matrix-identity.json').write_text(json.dumps(identity,indent=1)+'\n')
print('commands',len(records),'unexpected',sum(not r['as_expected'] for r in records),flush=True)
sys.exit(0 if all(r['as_expected'] for r in records) and all(r['same'] for r in identity.values()) else 1)
