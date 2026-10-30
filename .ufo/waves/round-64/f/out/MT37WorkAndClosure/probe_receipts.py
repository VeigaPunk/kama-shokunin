import pathlib, subprocess, sys, json
S=pathlib.Path('/fast/scratch/hyaku/kama-r64/f/MT37WorkAndClosure'); D=S/'clone2'; R=S/'receipts'; base='23b3fdb1a925129a9961cf551f6d40bf251602cb'
rows=[]
for label,counter in [('pristine',D/'tools/round64-c2-counter.py'),('W2-exists',R/'W2-exists.mutant.py'),('W3-isdir',R/'W3-isdir.mutant.py')]:
 for shape in ['empty-tip','run-only','sym-tip','broken-sym','hidden','file-tip','file-run','scratch-name','clean','used','link-used']:
  p=subprocess.run([sys.executable,str(counter),'--repo',str(D),'--tip',base,'--work',str(S/'probe'/shape),'--probe-work'],capture_output=True,text=True)
  rows.append({'counter':label,'shape':shape,'exit':p.returncode,'out':p.stdout.strip(),'err':p.stderr.strip()})
for shape in ['used','./used','link-used']:
 p=subprocess.run([sys.executable,str(D/'tools/round64-c2-counter.py'),'--repo',str(D),'--tip',base,'--work',shape,'--probe-work'],cwd=S/'probe',capture_output=True,text=True)
 rows.append({'counter':'pristine-relative','shape':shape,'exit':p.returncode,'out':p.stdout.strip()})
(R/'guard-probes.json').write_text(json.dumps(rows,indent=2))
(R/'guard-probes.txt').write_text('\n'.join(f"{x['counter']} {x['shape']} exit={x['exit']} {x['out']}" for x in rows)+'\n')
print((R/'guard-probes.txt').read_text())
p=subprocess.run(['python3','--version'],capture_output=True,text=True); q=subprocess.run(['git','--version'],capture_output=True,text=True)
(R/'versions.txt').write_text(p.stdout+q.stdout+'Installs/updates: none.\n')
