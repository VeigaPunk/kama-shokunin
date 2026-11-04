import json, os, pathlib, shutil, subprocess, hashlib
L=pathlib.Path('/home/vgpnk/Projects/shokunin/kama-shokunin');O=L/'.ufo/waves/round-83/w1/RV01AttacC1';S=pathlib.Path('/fast/scratch/hyaku/kama-r83/RV01AttacC1');S.mkdir(parents=True,exist_ok=True);os.environ['TMPDIR']=str(S);D=S/'clone';rows=[]
def call(a):return subprocess.run(a,text=True,capture_output=True,cwd=O)
try:
 p=call(['git','clone','--shared','--quiet',str(L),str(D)]);assert p.returncode==0,p.stderr
 def git(*a):
  assert call(['git','-C',str(D),'rev-parse','--show-toplevel']).stdout.strip()==str(D)
  p=call(['git','-C',str(D),*a]);assert p.returncode==0,p.stderr;return p.stdout.strip()
 git('config','user.email','rv01@example.invalid');git('config','user.name','RV01')
 source=L/'.ufo/waves/round-83/w1/EX04PendingFalls/round83-pending-falls.py';shutil.copyfile(source,D/'tools/round83-pending-falls.py')
 events=[]
 for i,short in enumerate(['962bd251','a251cbab','0d7c7c3e','7ad14e6c','7ad14e6c','6a160310','8a3e8af2','9efa6f1c']):
  events.append({'commit':git('rev-parse',short),'file':'SCORECARD.md' if i==4 else 'LOG.md','status':'unrestored','undisclosed':[{'line_sha256':str(i+1)*64,'count':1,'classes':['in-place-edit']}]})
 register=D/'registry/append-only-late.tsv';header='commit\tfile\tline_sha256\tcount\tclass\tnote\n'
 def late(wrong=False):
  return header+''.join('\t'.join([git('rev-parse','30d8eac3') if wrong and i==0 else e['commit'],e['file'],e['undisclosed'][0]['line_sha256'],'1','in-place-edit','round-83 accepts round-82 subject; accepted'])+'\n' for i,e in enumerate(events))
 register.write_text(late())
 # Fixture-only deterministic audit replay: exercises pending CLI independently of audit implementation.
 replay=S/'audit.json';(D/'tools/append-only-audit.py').write_text('import pathlib\nprint(pathlib.Path('+repr(str(replay))+').read_text())\n')
 git('add','tools/round83-pending-falls.py','tools/append-only-audit.py','registry/append-only-late.tsv');git('commit','-qm','RV01 synthetic eight-event pending fixture')
 def update():replay.write_text(json.dumps({'schema':'append-only-audit/v3','to':git('rev-parse','HEAD'),'events':events}))
 update();receipt=D/'.ufo/waves/round-82/measured/after/gate.out';receipt.parent.mkdir(parents=True,exist_ok=True)
 honest='APPEND_DEBT round=82 base=aaf974dbd3b6 events=68 accepted=53 late=15 pending=8 unaccepted=0 bad_rows=0\n'
 receipt.write_text(honest)
 root=['python3',str(D/'tools/round83-pending-falls.py'),'--repo',str(D),'--round','83']
 def run(name,args=[],expected=''):
  p=call(root+args);r={'name':name,'command':subprocess.list2cmdline(root+args),'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'expected':expected};rows.append(r);print(name,p.returncode,p.stdout[:160],p.stderr[:100],flush=True);return p
 git('add','-f',str(receipt));git('commit','-qm','RV01 honest committed receipt');update()
 run('pending-honest',expected='exit 0 falls=yes')
 run('pending-json',['--json'],'falls true and same counts as honest')
 receipt.write_text(honest.replace('pending=8','pending=0'));git('add','-f',str(receipt));git('commit','-qm','RV01 zero declared receipt');update()
 run('pending-zero-window-eight',expected='exit 1 falls=no')
 run('pending-zero-json',['--json'],'falls false')
 receipt.write_text(honest);register.write_text(late(True));git('add','registry/append-only-late.tsv');git('add','-f',str(receipt));git('commit','-qm','RV01 wrong event commit coverage');update()
 run('pending-wrong-commit',expected='exit 1 accepted=7 unaccepted=1')
 receipt.write_text(honest.replace('pending=8','pending=0').replace('aaf974dbd3b6','30d8eac394a8'))
 run('pending-worktree-receipt-forgery',expected='must not accept forged uncommitted receipt changing frozen window')
 (O/'pending-receipts.json').write_text(json.dumps({'draft_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'fixture':'shared clone; explicitly synthetic eight-event audit replay; production pending module copied and committed','receipts':rows},indent=2)+'\n')
finally:shutil.rmtree(S)
