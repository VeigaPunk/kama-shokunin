import pathlib, subprocess, hashlib, json, shutil, sys
S=pathlib.Path('/fast/scratch/hyaku/kama-r64/f/MT37WorkAndClosure'); D=S/'clone'; R=S/'receipts'; R.mkdir(exist_ok=True)
def g(*args):
 return subprocess.run(['git','-C',str(D),*args],capture_output=True,text=True,check=True).stdout
assert g('rev-parse','--show-toplevel').strip()==str(D)
base='23b3fdb1a925129a9961cf551f6d40bf251602cb'
items={'B1-two-pointers':'2f7989aa8e6e','B2-backtick-style':'bc08090c1653','B3-pointer-in-historical':'7038b0972473','B4-round-063':'fabf8dd79e65','B5-round64-same-commit':'7c749ca50675','B6-round64-stale':'029021152c8f','B7-including-stale':'ba054de8755c'}
meta={}
for name,rev in items.items():
 tip=g('rev-parse',rev).strip(); work=S/('receipt-'+name)
 (R/(name+'.patch')).write_text(g('diff',base,tip,'--','SCORECARD.md','corpus/lessons/round-64-verifier-spotcheck.md'))
 text=g('show',tip+':SCORECARD.md'); before=g('show',base+':SCORECARD.md')
 meta[name]={'tip':tip,'before_sha256':hashlib.sha256(before.encode()).hexdigest(),'mutant_sha256':hashlib.sha256(text.encode()).hexdigest()}
 p=subprocess.run([sys.executable,str(D/'tools/round64-c2-counter.py'),'--repo',str(D),'--tip',tip,'--work',str(work)],cwd=D/'tools',capture_output=True,text=True,timeout=900)
 (R/(name+'.out')).write_text(p.stdout); (R/(name+'.err')).write_text(p.stderr); meta[name]['exit']=p.returncode
 print(name,p.returncode,p.stdout.strip(),flush=True)
 if name=='B4-round-063':
  p2=subprocess.run([sys.executable,str(D/'tools/round42-selfdesc-reconcile.py'),'--repo',str(D),'--tip',tip],cwd=D/'tools',capture_output=True,text=True,env=dict(__import__('os').environ,TMPDIR=str(S)),timeout=900)
  (R/'B4-reconciler.out').write_text(p2.stdout+p2.stderr)
 shutil.rmtree(work)
(R/'tree-meta.json').write_text(json.dumps(meta,indent=2))
# The SAME detector after restoring exact working-tree bytes.
p=subprocess.run([sys.executable,str(D/'tools/round64-c2-counter.py'),'--repo',str(D),'--tip',base,'--work',str(S/'restored-work')],cwd=D/'tools',capture_output=True,text=True,timeout=900)
(R/'restored.out').write_text(p.stdout); (R/'restored.err').write_text(p.stderr)
print('RESTORED',p.returncode,p.stdout.strip(),flush=True)
hashes={}
for repo in [D,S/'clone2']:
 for path in ['SCORECARD.md','tools/round64-c2-counter.py']:
  actual=(repo/path).read_bytes(); original=subprocess.run(['git','-C',str(repo),'show',base+':'+path],capture_output=True,check=True).stdout
  hashes[str(repo.name)+'/'+path]={'original':hashlib.sha256(original).hexdigest(),'restored':hashlib.sha256(actual).hexdigest(),'equal':actual==original}
(R/'restoration.json').write_text(json.dumps(hashes,indent=2))
shutil.rmtree(S/'restored-work')
