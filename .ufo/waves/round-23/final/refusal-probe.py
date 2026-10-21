import importlib.util, pathlib, subprocess, tempfile, json, os
P=pathlib.Path
root=P('/home/vgpnk/Projects/shokunin/kama-shokunin')
s=importlib.util.spec_from_file_location('grid',root/'tests/report-audit/repo-state-grid.py'); m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
results=[]
for name in ['plain','bare-lane','bare-fleet','linked-lane','linked-fleet','packed-graph','sparse-fleet','promisor-false','empty-grafts','comment-grafts','nonutf8-config']:
 with tempfile.TemporaryDirectory(prefix='kama-refusal-') as t:
  lane,fleet,oid=m.base(t)
  if name.startswith('bare-'):
   source=lane if name=='bare-lane' else fleet; dest=P(t)/'bare.git';m.g(t,'clone','-q','--bare',str(source),str(dest))
   if name=='bare-lane':lane=dest
   else:fleet=dest
  if name.startswith('linked-'):
   source=lane if name=='linked-lane' else fleet;dest=P(t)/'linked';m.g(source,'worktree','add','-q','--detach',str(dest),'HEAD')
   if name=='linked-lane':lane=dest
   else:fleet=dest
  if name=='packed-graph':
   for r in [lane,fleet]:
    m.g(r,'pack-refs','--all');m.g(r,'repack','-ad');m.g(r,'commit-graph','write','--reachable')
  if name=='sparse-fleet':m.g(fleet,'sparse-checkout','set','--no-cone','/absent')
  if name=='promisor-false':m.g(lane,'config','remote.origin.promisor','false')
  if name in ['empty-grafts','comment-grafts']:(lane/'.git/info/grafts').write_text('' if name=='empty-grafts' else '# no grafts\n')
  if name=='nonutf8-config':
   with open(lane/'.git/config','ab') as f:f.write(b'\n[branch "caf\xe9"]\n\tdescription = harmless\n')
  arms={}
  for arm,script in [('frozen',P('/tmp/kama-r23w2/CritRefusalScope-frozen.py')),('current',root/'tools/report-landing-audit.py')]:
   cmd=['python',str(script),'--lane-repo',str(lane),'--fleet-repo',str(fleet),'--rounds','1','--no-errata','--json']
   p=subprocess.run(cmd,capture_output=True,env=m.env(),timeout=15)
   arms[arm]={'command':cmd,'rc':p.returncode,'stdout':p.stdout.decode(errors='replace'),'stderr':p.stderr.decode(errors='replace')}
  results.append({'case':name,'arms':arms})
  print(name,[(a,x['rc'],x['stderr'].strip()) for a,x in arms.items()],flush=True)
P('/tmp/kama-r23-l1/refusal/refusal-results.json').write_text(json.dumps(results,indent=2))
