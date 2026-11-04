#!/usr/bin/env python3
"""Read-only frozen-counter probes; no repositories or subprocess selftests needed."""
import argparse, contextlib, hashlib, io, json, pathlib, subprocess, types
from unittest.mock import patch

p=argparse.ArgumentParser()
p.add_argument('--repo', required=True)
a=p.parse_args()
repo=pathlib.Path(a.repo)
freeze='7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd'
def blob(path):
    return subprocess.check_output(['git','-C',str(repo),'show',f'{freeze}:{path}'],text=True)
source=blob('.ufo/waves/round-85/count.py')
m=types.ModuleType('frozen_counter'); exec(compile(source,'frozen-count.py','exec'),m.__dict__)
base=blob('SCORECARD.md')
auth,row=m.cells(base)
fixed_auth='**Current authority (round 84):** PRE_REPORT round=84 arms=13 failed=0 uncommitted=0 '+m.GATE
fixed_row='| calibration | 7 | latest outside closure `corpus/lessons/round-84-verifier-spotcheck.md` |'
positive=base.replace(auth,fixed_auth,1).replace(row,fixed_row,1)
fake=fixed_auth+'\n\n## Axes\n\n'+fixed_row+'\n\n'
cases={'stale':base,'positive':positive,
 'unrelated_tokens':base+'\nUnrelated witness '+fixed_auth.replace('**Current authority (round 84):** ','')+'\n'+fixed_row.replace('| calibration |','| unrelated |'),
 'fake_fenced_cells':'```markdown\n'+fake+'```\n\n'+base,
 'fake_html_comment_cells':'<!--\n'+fake+'-->\n\n'+base,
 'fake_table_location':base.replace(row,'```markdown\n'+fixed_row+'\n```\n'+row,1),
 'four_space_code':'    # round-85 correction\n'+base,
 'empty_atx_boundary':'# round-85 correction\n\n#\n\n'+positive}
for indent in range(4):
    cases[f'correction_indent_{indent}']=' '*indent+'# round-85 correction\n'+fake+'# End correction\n\n'+base
results=[]
for name,text in cases.items():
    captured=io.StringIO()
    with patch.object(m,'blob',return_value=text),patch.object(m.subprocess,'check_output',return_value='corpus/lessons/round-84-verifier-spotcheck.md\n'),contextlib.redirect_stdout(captured):
        rc=m.calibration(repo,freeze)
    selected=m.cells(text)
    results.append({'name':name,'exit':rc,'stdout':captured.getvalue(),'selected_authority_is_stale':selected[0]==auth,'selected_row_is_stale':selected[1]==row})
condition='subject_round is not None and deletion != subject_round'
old='            bad("note-wrong-deletion-round", f"{detail}: note deletion round {deletion} "\n                                             f"differs from subject round {subject_round}")\n            continue'
tool=blob('tools/round81-append-debt.py')
# Exercise the actual mutants() classifier with injected completed-process receipts.
# TemporaryDirectory still allocates inside the explicitly assigned scratch directory.
work=pathlib.Path('/fast/scratch/hyaku/kama-r85/CR01Cheats'); work.mkdir(parents=True,exist_ok=True)
responses={
 'runtime_error':(1,'APPEND_DEBT_SELFTEST_FAIL note-subject-mismatch\nAPPEND_DEBT_SELFTEST pass=30 fail=1\n','Traceback: error\n'),
 'missing_tally':(1,'APPEND_DEBT_SELFTEST_FAIL note-subject-mismatch\n',''),
 'malformed_tally':(1,'APPEND_DEBT_SELFTEST_FAIL note-subject-mismatch\nAPPEND_DEBT_SELFTEST pass=30 fail=oops\n',''),
 'unrelated_arm':(1,'APPEND_DEBT_SELFTEST_FAIL note-unrelated-arm\nAPPEND_DEBT_SELFTEST pass=30 fail=1\n',''),
 'contradictory_tally':(1,'APPEND_DEBT_SELFTEST_FAIL note-subject-mismatch\nAPPEND_DEBT_SELFTEST pass=31 fail=0\nAPPEND_DEBT_SELFTEST pass=30 fail=1\n',''),
 'duplicate_tally':(1,'APPEND_DEBT_SELFTEST_FAIL note-subject-mismatch\nAPPEND_DEBT_SELFTEST pass=30 fail=1\nAPPEND_DEBT_SELFTEST pass=31 fail=0\n',''),
 'no_completed_counts':(1,'APPEND_DEBT_SELFTEST_FAIL note-subject-mismatch\nAPPEND_DEBT_SELFTEST pass=0 fail=999\n',''),
 'valid_named_failure':(1,'APPEND_DEBT_SELFTEST_FAIL note-subject-mismatch\nAPPEND_DEBT_SELFTEST pass=30 fail=1\n',''),
 'survivor':(0,'APPEND_DEBT_SELFTEST pass=31 fail=0\n','')}
mutant_results=[]
for name,(rc,out,err) in responses.items():
    captured=io.StringIO()
    proc=subprocess.CompletedProcess(['injected-receipt'],rc,out,err)
    with patch.object(m,'blob',return_value=tool),patch.object(m.subprocess,'run',return_value=proc),contextlib.redirect_stdout(captured):
        result=m.mutants(repo,freeze,work)
    mutant_results.append({'name':name,'injected_receipt':{'exit':rc,'stdout':out,'stderr':err},'exit':result,'stdout':captured.getvalue()})
print(json.dumps({'axes':['calibration','operability'],'freeze':freeze,'counter_sha256':hashlib.sha256(source.encode()).hexdigest(),'mutation_sites':{'condition':tool.count(condition),'continue_block':tool.count(old)},'c1':results,'c2_classifier':mutant_results},indent=2))
