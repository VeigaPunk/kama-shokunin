#!/usr/bin/env python3
import pathlib, subprocess, shutil, os, json, importlib.util, hashlib
L=pathlib.Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
O=L/'.ufo/waves/round-83/w1/RV02AttackC2'
S=pathlib.Path('/fast/scratch/hyaku/kama-r83/RV02AttackC2')
BASE='30d8eac394a8714fad3dc792b74a45a25b4366a2'
SEALED='b1ba614b51255a3dcfe3e0946f32f8e31bd65c09'
results=[]
def cmd(args, cwd=None):
 p=subprocess.run([str(a) for a in args],cwd=cwd,capture_output=True,text=True)
 return p
try:
 S.mkdir(parents=True,exist_ok=True); os.environ['TMPDIR']=str(S)
 D=S/'clone'
 p=cmd(['git','clone','--shared','--no-checkout',L,D]); assert p.returncode==0,p.stderr
 assert cmd(['git','-C',D,'rev-parse','--show-toplevel']).stdout.strip()==str(D)
 def git(*a):
  p=cmd(['git','-C',D,*a]); assert p.returncode==0,p.stderr; return p.stdout
 git('checkout','-B','master',BASE)
 git('config','user.name','RV02 fixture'); git('config','user.email','rv02@example.invalid')
 for seat,name in [('EX03SelfRecord','round83-selfrecord-round82.py'),('EX05PinRechecks','round83-pin-rechecks.py')]:
  source=L/f'.ufo/waves/round-83/w1/{seat}/{name}'
  shutil.copyfile(source,D/'tools'/name)
  (O/(name+'.sha256')).write_text(hashlib.sha256(source.read_bytes()).hexdigest()+'\n')
 def commit(label):
  git('add','-A'); git('commit','--allow-empty','-qm',label)
 def record(name, args, expected):
  p=cmd(args)
  text=f'COMMAND: {" ".join(str(a) for a in args)}\nEXIT: {p.returncode}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}'
  path=O/(name+'.out'); path.write_text(text)
  results.append(dict(name=name,expected=expected,exit=p.returncode,output=p.stdout,stderr=p.stderr,receipt=str(path),command=[str(a) for a in args]))
  return p
 log=(D/'LOG.md').read_text(); score=(D/'SCORECARD.md').read_text()
 keys=['log82-c1-selftest','sc82c1-selftest','calib82-selftest']
 old=[18,22,22]
 lines=[f'corrected F{i+1} old={k}={v} new={k}=23 at={SEALED} date=2026-11-04 fix={"LOG.md" if i==0 else "SCORECARD.md"}' for i,(k,v) in enumerate(zip(keys,old))]
 lesson='## Corrections\n'+'\n'.join(lines)+'\n## Mistakes\n'
 def c2fixture():
  (D/'LOG.md').write_text(log+'\n## Ordinary backing\n'+keys[0]+'=23\n')
  (D/'SCORECARD.md').write_text(score+'\n## Ordinary backing\n'+keys[1]+'=23\n'+keys[2]+'=23\n')
  (D/'corpus/lessons/round-83.md').write_text(lesson)
 c2=['python3',D/'tools/round83-selfrecord-round82.py','--repo',D]
 c2fixture(); commit('C2 honest'); record('c2-honest',c2,'green')
 for case in ['lesson-only-token','log-correction-only','correction-block-only','prefix-233','holding-F4','duplicate-F1','at-base','at-descendant']:
  c2fixture()
  if case=='lesson-only-token':
   (D/'LOG.md').write_text(log)
   (D/'corpus/lessons/round-83.md').write_text(lesson+'\n'+keys[0]+'=23\n')
  elif case=='log-correction-only': (D/'LOG.md').write_text(log+'\nLOG-CORRECTION '+keys[0]+'=23\n')
  elif case=='correction-block-only': (D/'LOG.md').write_text(log+'\n#### round-83 correction\n'+keys[0]+'=23\n')
  elif case=='prefix-233': (D/'LOG.md').write_text(log+'\n'+keys[0]+'=233\n')
  elif case=='holding-F4':
   line=f'corrected F4 old=log82-c2-debt-selftest=25 new=log82-c2-debt-selftest=25 at={SEALED} date=2026-11-04 fix=LOG.md\n'
   (D/'corpus/lessons/round-83.md').write_text(lesson.replace('## Mistakes',line+'## Mistakes'))
  elif case=='duplicate-F1': (D/'corpus/lessons/round-83.md').write_text(lesson.replace('## Mistakes',lines[0]+'\n## Mistakes'))
  elif case in ['at-base','at-descendant']:
   at=BASE if case=='at-base' else git('rev-parse','HEAD').strip()
   (D/'corpus/lessons/round-83.md').write_text(lesson.replace('at='+SEALED,'at='+at,1))
  commit(case); record('c2-'+case,c2,'red')
 c2fixture()
 src=D/'corpus/SOURCES.md'; source=src.read_text(); import re
 count=sum(bool(re.match(r'^ {0,3}\|[ \t]*S[0-9]{3,}\b',line)) for line in source.splitlines())
 src.write_text(source+''.join(f'\n| S{9000+i} | fixture |' for i in range(309-count))+'\n')
 commit('tip population 309'); record('c2-tip-population-309',c2,'green with F5 witness=305')
 # A changed tip witness must not erase the sealed stale fact.
 c2fixture()
 (D/'.ufo/waves/round-82/measured/after/c1-selftest.out').write_text('SELFRECORD_R81_SELFTEST pass=18 fail=0\n')
 changed=lesson.replace(lines[0]+'\n','').replace('=23','=18')
 (D/'corpus/lessons/round-83.md').write_text(changed)
 (D/'SCORECARD.md').write_text(score+'\n## Ordinary backing\n'+keys[1]+'=18\n'+keys[2]+'=18\n')
 commit('mutated tip witness'); record('c2-tip-witness-rewrite',c2,'red: sealed witness was 23')
 # C3 independent byte-rule fixtures, created under the clone.
 spec=importlib.util.spec_from_file_location('c3',D/'tools/round83-pin-rechecks.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
 F=D/'c3fixture'
 def c3fixture():
  if F.exists(): shutil.rmtree(F)
  F.mkdir(); m.build_green(F)
  assert cmd(['git','-C',F,'init','-q']).returncode==0
  assert cmd(['git','-C',F,'rev-parse','--show-toplevel']).stdout.strip()==str(F)
  cmd(['git','-C',F,'config','user.name','RV02 c3']); cmd(['git','-C',F,'config','user.email','rv02@example.invalid'])
  fcommit('c3 fixture baseline')
 def fcommit(label):
  p=cmd(['git','-C',F,'add','-A']); assert p.returncode==0,p.stderr
  p=cmd(['git','-C',F,'commit','-q','--allow-empty','-m',label]); assert p.returncode==0,p.stderr
 def rows(): return [x.split('\t') for x in (F/'rows.tsv').read_text().splitlines()]
 def save(r): (F/'rows.tsv').write_text('\n'.join('\t'.join(x) for x in r)+'\n')
 c3=['python3',D/'tools/round83-pin-rechecks.py','--repo',F,'--register','register.tsv','--rows','rows.tsv']
 c3fixture(); record('c3-honest',c3,'green: graded=2 ungraded=1')
 for case in ['wrong-line-valid-digest','25-words-plus-period','duplicate-conflicting-verdicts','ungraded-documented-ref','uncommitted-extract']:
  c3fixture(); r=rows()
  if case=='wrong-line-valid-digest': r[1][6]='10'; save(r)
  elif case=='25-words-plus-period':
   q=' '.join('word'+str(i) for i in range(25))+' .'
   for path,ref in [('extracts/engone-b1.txt','b1'),('extracts/engone-n2-health.txt','n2')]: m.write_extract(F,path,'https://example.com/raw',ref,10,12,['line ten',q,'line twelve'])
   r[1][5]=r[1][7]=q; save(r)
  elif case=='duplicate-conflicting-verdicts':
   duplicate=list(r[1]); duplicate[3]='drifted'; r.append(duplicate); save(r)
  elif case=='ungraded-documented-ref':
   r[1]=['engone','b1','n2','ungraded','2026-11-04','-','-','-','-','-','-','missing document b1']; save(r)
  elif case=='uncommitted-extract':
   fcommit('baseline for uncommitted mutant')
   m.write_extract(F,'extracts/engone-b1.txt','https://example.com/raw','b1',10,12,['uncommitted',m.SENTENCE_A,'line twelve'])
  if case!='uncommitted-extract': fcommit(case)
  record('c3-'+case,c3,'red')
 (O/'results.json').write_text(json.dumps(results,indent=2)+'\n')
 print(json.dumps([{'name':x['name'],'exit':x['exit'],'summary':x['output'].splitlines()[-1:] } for x in results],indent=2))
finally:
 shutil.rmtree(S,ignore_errors=True)
