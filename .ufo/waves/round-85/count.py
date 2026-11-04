#!/usr/bin/env python3
"""Frozen round85 counting command: committed authority cells and delivered debt mutants."""
import argparse, pathlib, re, subprocess, tempfile, os, json
BASE='4401b72f64a2202fd30f26479c463e9b9d9cabad'
GATE='b53cd336e0cb204cf71246e95fdf7494babeafa4'

def blob(repo, rev, path):
    return subprocess.check_output(['git','-C',str(repo),'show',f'{rev}:{path}'],text=True)

def cells(text):
    # CommonMark ATX headings permit zero through three leading spaces.
    kept=[]; depth=None
    for line in text.splitlines():
        h=re.match(r'^ {0,3}(#{1,6})\s+(.*)',line)
        if h and depth is not None and len(h[1])<=depth: depth=None
        if h and re.match(r'round-\d+ correction(?:\s|$)',h[2]): depth=len(h[1])
        if depth is None and 'LOG-CORRECTION' not in line: kept.append(line)
    text='\n'.join(kept)
    authority=re.search(r'^\*\*Current authority[^\n]+',text,re.M)
    axes=re.search(r'^## Axes\s*\n(.*?)(?=^## |\Z)',text,re.M|re.S)
    row=re.search(r'^\|\s*\*{0,2}calibration\*{0,2}\s*\|[^\n]+',axes[1],re.M) if axes else None
    return authority[0] if authority else '', row[0] if row else ''

def calibration(repo,rev):
    score=blob(repo,rev,'SCORECARD.md'); authority,row=cells(score)
    gate_ok=bool(re.search(r'PRE_REPORT round=84 arms=13 failed=0 uncommitted=0',authority)) and GATE in authority and 'under terminal measurement' not in authority
    paths=subprocess.check_output(['git','-C',str(repo),'ls-tree','-r','--name-only',rev,'corpus/lessons'],text=True)
    nums=[int(n) for n in re.findall(r'corpus/lessons/round-(\d+)-verifier-spotcheck\.md',paths)]
    newest=f'round-{max(nums)}-verifier-spotcheck.md'
    named=re.search(r'latest outside closure `corpus/lessons/(round-\d+-verifier-spotcheck\.md)`',row)
    closure_ok=bool(named and named[1]==newest)
    print(f'AUTHORITY_CELLS facts=2 mismatches={int(not gate_ok)+int(not closure_ok)} gate={int(gate_ok)} closure={int(closure_ok)} newest={newest}')
    return int(not(gate_ok and closure_ok))

def mutants(repo,rev,work):
    source=blob(repo,rev,'tools/round81-append-debt.py')
    condition='subject_round is not None and deletion != subject_round'
    old='            bad("note-wrong-deletion-round", f"{detail}: note deletion round {deletion} "\n                                             f"differs from subject round {subject_round}")\n            continue'
    replacements={'M2':(condition,'subject_round is not None and deletion != accepting'), 'M3':(condition,'subject_round is not None and deletion < subject_round'), 'M4':(old,old.rsplit('\n',1)[0])}
    escaped=bad=0
    with tempfile.TemporaryDirectory(prefix='r85-mutants-',dir=work) as directory:
        for name,(a,b) in replacements.items():
            if source.count(a)!=1: raise RuntimeError(f'{name}: mutation site count {source.count(a)}')
            path=pathlib.Path(directory)/(name+'.py'); path.write_text(source.replace(a,b))
            result=subprocess.run(['python3',str(path),'--selftest'],text=True,capture_output=True,env={**os.environ,'TMPDIR':directory})
            tally=re.search(r'^APPEND_DEBT_SELFTEST pass=(\d+) fail=(\d+)$',result.stdout,re.M)
            semantic=bool(result.returncode==1 and tally and int(tally[2])>0 and 'APPEND_DEBT_SELFTEST_FAIL note-' in result.stdout and not result.stderr)
            survived=bool(result.returncode==0 and tally and int(tally[2])==0)
            escaped+=survived;bad+=not(semantic or survived)
            print(f'MUTANT {name} exit={result.returncode} killed={int(semantic)} escaped={int(survived)}')
            print(result.stdout,end=''); print(result.stderr,end='')
    print(f'DEBT_MUTANTS mutants=3 killed={3-escaped-bad} escaped={escaped} invalid={bad}')
    return int(bool(escaped or bad))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('claim',choices=['c1','c2']);p.add_argument('--repo',default='.');p.add_argument('--rev',default='master');p.add_argument('--work',required=True);a=p.parse_args()
    pathlib.Path(a.work).mkdir(parents=True,exist_ok=True)
    raise SystemExit(calibration(a.repo,a.rev) if a.claim=='c1' else mutants(a.repo,a.rev,a.work))
