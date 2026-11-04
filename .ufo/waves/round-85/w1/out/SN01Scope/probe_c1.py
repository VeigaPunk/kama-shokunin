#!/usr/bin/env python3
"""Bounded local c1 counter probes; no production mutation or network."""
import json, os, pathlib, subprocess
ROOT=pathlib.Path('/fast/scratch/hyaku/kama-r85/SN01Scope')
REPO=ROOT/'fixtures/counter-probe'
COUNTER='/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-85/count.py'
OUT=ROOT/'receipts'
for p in (REPO, OUT, ROOT/'tmp', ROOT/'work'): p.mkdir(parents=True,exist_ok=True)
os.environ['TMPDIR']=str(ROOT/'tmp')
commands=[]
def run(argv):
    p=subprocess.run(argv,text=True,capture_output=True)
    commands.append({'argv':argv,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    return p
def git(*a):
    p=run(['git','-C',str(REPO),*a])
    if p.returncode: raise RuntimeError(commands[-1])
    return p.stdout.strip()
git('init','-q')
assert git('rev-parse','--show-toplevel')==str(REPO)
GATE='b53cd336e0cb204cf71246e95fdf7494babeafa4'
goodauth=f'**Current authority**: terminal `PRE_REPORT round=84 arms=13 failed=0 uncommitted=0` measured `{GATE}`; receipt round84; command count.py.'
staleauth='**Current authority**: round84 is under terminal measurement.'
goodrow='| **calibration** | latest outside closure `corpus/lessons/round-84-verifier-spotcheck.md` |'
stalerow='| **calibration** | latest outside closure `corpus/lessons/round-83-verifier-spotcheck.md` |'
def score(a,r): return '# Scorecard\n\n'+a+'\n\n## Axes\n\n'+r+'\n'
scenarios={'repaired':score(goodauth,goodrow),'stale':score(staleauth,stalerow)}
# Both witnesses are literal code, followed by genuinely stale live cells.
scenarios['fenced-shadow']='# Quoted example\n\n```markdown\n'+goodauth+'\n\n## Axes\n\n'+goodrow+'\n```\n\n'+score(staleauth,stalerow)
# Put correction-block witnesses BEFORE live cells so anchoring alone cannot explain rejection.
for n in range(4):
    scenarios[f'correction-{n}']=' '*n+'## round-84 correction\n\n'+goodauth+'\n\n### Axes example\n\n'+goodrow+'\n\n'+score(staleauth,stalerow)
scenarios['unrelated-tokens']='Unrelated PRE_REPORT round=84 arms=13 failed=0 uncommitted=0 '+GATE+'\nlatest outside closure `corpus/lessons/round-84-verifier-spotcheck.md`\n'+score(staleauth,stalerow)
scenarios['wrong-measured-with-backing']=score('**Current authority**: measured revision `4401b72f64a2202fd30f26479c463e9b9d9cabad`; unrelated backing `PRE_REPORT round=84 arms=13 failed=0 uncommitted=0` '+GATE,goodrow)
# A fake newest closure file has no closure result or evidentiary content.
lesson=REPO/'corpus/lessons/round-84-verifier-spotcheck.md'
lesson.parent.mkdir(parents=True,exist_ok=True)
lesson.write_text('Not a closure receipt; placeholder fixture data.\n')
results=[]
for name,text in scenarios.items():
    (REPO/'SCORECARD.md').write_text(text)
    git('add','--','SCORECARD.md','corpus/lessons/round-84-verifier-spotcheck.md')
    git('-c','user.name=probe','-c','user.email=probe@scratch','commit','-qm',name)
    rev=git('rev-parse','HEAD')
    p=run(['python3',COUNTER,'c1','--repo',str(REPO),'--rev',rev,'--work',str(ROOT/'work')])
    (OUT/f'{name}.md').write_text(text)
    (OUT/f'{name}.out').write_text('exit='+str(p.returncode)+'\n'+p.stdout+p.stderr)
    results.append({'scenario':name,'revision':rev,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
p=run(['git','-C',str(REPO),'cat-file','-e',GATE+'^{commit}'])
results.append({'scenario':'gate-object-existence','exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
(OUT/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
(OUT/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
