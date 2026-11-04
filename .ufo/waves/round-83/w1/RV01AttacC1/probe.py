import json, os, pathlib, shutil, subprocess, hashlib
L=pathlib.Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
O=L/'.ufo/waves/round-83/w1/RV01AttacC1'
S=pathlib.Path('/fast/scratch/hyaku/kama-r83/RV01AttacC1')
S.mkdir(parents=True,exist_ok=True); os.environ['TMPDIR']=str(S)
D=S/'clone'; receipts=[]
def cmd(a,cwd=None):
 p=subprocess.run(a,cwd=cwd,text=True,capture_output=True); return p
try:
 p=cmd(['git','clone','--shared','--quiet',str(L),str(D)]); assert p.returncode==0,p.stderr
 assert cmd(['git','-C',str(D),'rev-parse','--show-toplevel']).stdout.strip()==str(D)
 def git(*a):
  assert cmd(['git','-C',str(D),'rev-parse','--show-toplevel']).stdout.strip()==str(D)
  p=cmd(['git','-C',str(D),*a]); assert p.returncode==0,p.stderr; return p.stdout.strip()
 git('config','user.email','rv01@example.invalid');git('config','user.name','RV01')
 source=L/'.ufo/waves/round-83/w1/EX01LateBinding/round81-append-debt.py'
 shutil.copyfile(source,D/'tools/round81-append-debt.py')
 H='commit\tfile\tline_sha256\tcount\tclass\tnote\n'; base='30d8eac394a8714fad3dc792b74a45a25b4366a2'
 event=git('rev-parse','962bd251'); digest='1'*64
 row=lambda note,commit=event:'\t'.join([commit,'LOG.md',digest,'1','in-place-edit',note])+'\n'
 register=D/'registry/rv01.tsv'; register.write_text(H+row('round-82 accepts round-81 subject; accepted'))
 empty=D/'registry/rv01-empty.tsv';empty.write_text(H)
 git('add','tools/round81-append-debt.py','registry/rv01.tsv','registry/rv01-empty.tsv');git('commit','-qm','RV01 committed candidate and synthetic attack register')
 rev=git('rev-parse','HEAD')
 data={'schema':'append-only-audit/v3','to':rev,'events':[{'commit':event,'file':'LOG.md','status':'unrestored','undisclosed':[{'line_sha256':digest,'count':1,'classes':['in-place-edit']}]}],'declarations':[],'summary':{'bad_declarations':0}}
 audit=S/'audit.json';audit.write_text(json.dumps(data))
 root=['python3',str(D/'tools/round81-append-debt.py'),'--repo',str(D),'--round','83','--audit-json',str(audit)]
 def run(name,args,want):
  p=cmd(root+args,cwd=D);r={'name':name,'command':subprocess.list2cmdline(root+args),'cwd':str(D),'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'expected':want};receipts.append(r);print(name,p.returncode,p.stdout[:120],p.stderr[:120],flush=True)
 untracked=D/'registry/untracked.tsv';shutil.copyfile(register,untracked)
 run('untracked',['--late',str(untracked)],'exit 2')
 outside=S/'outside.tsv';shutil.copyfile(register,outside);link=D/'registry/outside-link.tsv';link.symlink_to(outside)
 run('outside-symlink',['--late',str(link)],'exit 2')
 run('base-mismatch',['--base','b1ba614b51255a3dcfe3e0946f32f8e31bd65c09','--late',str(register)],'exit 2')
 # Committed round-82 acceptance of the round-82 event is invalid, despite its claimed round-81 deletion.
 run('wrong-deletion-round',['--register',str(empty),'--late',str(register)],'exit 1 note/round cross-check')
 register.write_text(H+row('round-83 accepts round-82 subject; accepted'))
 run('uncommitted-note-rewrite',['--register',str(empty),'--late',str(register)],'exit 2 committed row identity mismatch')
 register.write_text(H+row('round-83 accepts round-81 subject; accepted'))
 git('add','registry/rv01.tsv');git('commit','-qm','RV01 commit edited round83 note')
 data['to']=git('rev-parse','HEAD');audit.write_text(json.dumps(data))
 run('copied-row-note-edited',['--register',str(empty),'--late',str(register)],'exit 1 if note/round rule rejects copied accepting round')
 run('flag-order-forward',['--late','registry/append-only-late.tsv','--register',str(empty)],'independent late and frozen paths')
 run('flag-order-reverse',['--register',str(empty),'--late','registry/append-only-late.tsv'],'same as forward')
 # A register on a parallel branch predates the event in graph ancestry.
 register.write_text(H+row('round-83 accepts round-82 subject; accepted',base))
 git('add','registry/rv01.tsv');git('commit','-qm','RV01 committed row naming a different event')
 data['to']=git('rev-parse','HEAD');audit.write_text(json.dumps(data))
 register.write_text(H+row('round-83 accepts round-82 subject; accepted'))
 run('uncommitted-event-rewrite',['--register',str(empty),'--late',str(register)],'exit 2 committed row identity mismatch; committed row names different event')
 git('restore','registry/rv01.tsv')
 git('checkout','--quiet','-b','predate',event+'^')
 shutil.copyfile(source,D/'tools/round81-append-debt.py');register.write_text(H+row('round-83 accepts round-82 subject; accepted'));empty.write_text(H)
 git('add','tools/round81-append-debt.py','registry/rv01.tsv','registry/rv01-empty.tsv');git('commit','-qm','RV01 non-descendant register')
 git('merge','--quiet','-s','ours','--no-edit',rev)
 shutil.copyfile(L/'plans/round-83-claims.md',D/'plans/round-83-claims.md');git('add','plans/round-83-claims.md');git('commit','-qm','RV01 frozen plan copy')
 data['to']=git('rev-parse','HEAD');audit.write_text(json.dumps(data))
 run('non-descendant-rows',['--register',str(empty),'--late',str(register)],'exit 1 not-descendant')
 (O/'late-receipts.json').write_text(json.dumps({'draft_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'fixtures':'shared clone; synthetic audit population explicitly supplied through --audit-json','receipts':receipts},indent=2)+'\n')
finally:
 shutil.rmtree(S)
