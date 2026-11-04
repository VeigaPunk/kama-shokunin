#!/usr/bin/env python3
"""MT01Mutants round85: build independent candidate + M1-M5 mutants, run, classify.

Selftest-only additions to the delivered tools/round81-append-debt.py (no grade-rule change):
  - note-equality-accepted:      deletion==subject, accepting>deletion  -> exit0 (kills M2)
  - note-deletion-above-subject: deletion>subject                      -> exit1 (kills M3)
  - note-exact-summary:          full summary + ordered findings pinned -> exit1 (kills M4)
Mutants (all applied to the CANDIDATE, exact single sites):
  M2/M3/M4: frozen literals imported from count.py
  M1 binding-removal (mine): subject_round = subject_rounds(...) -> subject_round = None
  M5 None-mismatch (mine):   drop `subject_round is not None and` guard
"""
import hashlib, json, os, pathlib, re, subprocess, sys

SCRATCH = pathlib.Path('/fast/scratch/hyaku/kama-r85/MT01Mutants')
REPO = '/home/vgpnk/Projects/shokunin/kama-shokunin'
BUILD = SCRATCH / 'build'
BUILD.mkdir(exist_ok=True)
(SCRATCH / 'tmp').mkdir(exist_ok=True)
ENV = {**os.environ, 'TMPDIR': str(SCRATCH / 'tmp')}

def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()

src = subprocess.check_output(
    ['git', '-C', REPO, 'show', 'master:tools/round81-append-debt.py'], text=True)
delivered_status = subprocess.run(
    ['git', '-C', REPO, 'status', '--porcelain', '--', 'tools/round81-append-debt.py'],
    capture_output=True, text=True).stdout
blob_hash = subprocess.check_output(
    ['git', '-C', REPO, 'rev-parse', 'master:tools/round81-append-debt.py'], text=True).strip()

import ast
counter_text = (pathlib.Path(REPO) / '.ufo/waves/round-85/count.py').read_text()
tree = ast.parse(counter_text)
function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'mutants')
namespace = {}
for statement in function.body:
    if isinstance(statement, ast.Assign) and isinstance(statement.targets[0], ast.Name):
        name = statement.targets[0].id
        if name in {'condition', 'old', 'replacements'}:
            exec(compile(ast.Module(body=[statement], type_ignores=[]), '<frozen literals>', 'exec'), namespace)
M2a, M2b = namespace['replacements']['M2']
M3a, M3b = namespace['replacements']['M3']
M4old, M4new = namespace['replacements']['M4']

ANCHOR = (
    '            subject_rounds=lambda commit: None)\n'
    '    cases.append(("note-subject-unresolvable", r, 0, None))\n'
)
ADDITION = '''
    # MT01 r85 additions: equality, direction, exact-summary controls pinning the
    # subject-binding check. Selftest-only; grade rules untouched.
    r = run(frozen, [late_row(B, "SCORECARD.md", H2,
                              note="round-81 accepts round-79 subject; accepted history")],
            subject_rounds=lambda commit: 79)
    cases.append(("note-equality-accepted", r, 0, None))
    r = run(frozen, [late_row(B, "SCORECARD.md", H2,
                              note="round-82 accepts round-80 subject; accepted history")],
            subject_rounds=lambda commit: 79)
    cases.append(("note-deletion-above-subject", r, 1, "note-wrong-deletion-round"))
    exact_expectations = []
    r = run(frozen, [late_row(B, "SCORECARD.md", H2,
                              note="round-81 accepts round-78 subject; accepted history")],
            subject_rounds=lambda commit: 79)
    exact_expectations.append(("note-exact-summary", r,
                               {"events": 2, "accepted": 1, "late": 0, "pending": 1,
                                "unaccepted": 1, "bad_rows": 1, "bad_declarations": 0,
                                "out_of_population": 0},
                               ["note-wrong-deletion-round", "count-short"]))
'''
TALLY_OLD = '    print(f"APPEND_DEBT_SELFTEST pass={len(cases) - fail} fail={fail}")\n'
TALLY_NEW = '''    for name_e, res_e, want_summary, want_classes in exact_expectations:
        if (res_e["summary"] != want_summary
                or [f["class"] for f in res_e["findings"]] != want_classes):
            fail += 1
            print(f"APPEND_DEBT_SELFTEST_FAIL {name_e} exit=1 want=1 "
                  f"summary={res_e['summary']} findings={res_e['findings'][:2]}")
    print(f"APPEND_DEBT_SELFTEST pass={len(cases) + len(exact_expectations) - fail} fail={fail}")
'''

MUTANTS = {
    'M1': ('        subject_round = subject_rounds(commit) if subject_rounds is not None else None\n',
           '        subject_round = None\n'),
    'M2': (M2a, M2b),
    'M3': (M3a, M3b),
    'M4': (M4old, M4new),
    'M5': ('        if subject_round is not None and deletion != subject_round:\n',
           '        if deletion != subject_round:\n'),
}

for label, a in (('anchor', ANCHOR), ('tally', TALLY_OLD)):
    assert src.count(a) == 1, f'{label} site count {src.count(a)}'
candidate = src.replace(ANCHOR, ANCHOR + ADDITION).replace(TALLY_OLD, TALLY_NEW)

def run_selftest(path):
    p = subprocess.run(['python3', str(path), '--selftest'], text=True,
                       capture_output=True, env=ENV, cwd=str(SCRATCH))
    m = re.search(r'^APPEND_DEBT_SELFTEST pass=(\d+) fail=(\d+)$', p.stdout, re.M)
    tally = [int(m[1]), int(m[2])] if m else None
    semantic = (p.returncode == 1 and tally is not None and tally[1] > 0
                and 'APPEND_DEBT_SELFTEST_FAIL note-' in p.stdout and p.stderr == '')
    escaped = (p.returncode == 0 and tally is not None and tally[1] == 0)
    verdict = 'semantic-kill' if semantic else ('escaped' if escaped else 'invalid')
    return {'command': ['python3', str(path), '--selftest'],
            'exit': p.returncode, 'tally': tally, 'verdict': verdict,
            'stdout': p.stdout, 'stderr': p.stderr,
            'note_fails': sorted(set(re.findall(r'APPEND_DEBT_SELFTEST_FAIL (note-\S+)',
                                                p.stdout)))}

receipts = {
    'delivered_master_blob_gitsha': blob_hash,
    'delivered_sha256': sha(src),
    'delivered_status_porcelain': delivered_status,
    'base_4401b72_sha256': sha(subprocess.check_output(
        ['git', '-C', REPO, 'show',
         '4401b72f64a2202fd30f26479c463e9b9d9cabad:tools/round81-append-debt.py'],
        text=True)),
    'candidate_sha256': sha(candidate),
    'site_counts': {name: src.count(pair[0]) for name, pair in MUTANTS.items()},
}
OUT = pathlib.Path(REPO) / '.ufo/waves/round-85/w1/out/MT01Mutants'
OUT.mkdir(parents=True, exist_ok=True)
receipts['axes'] = ['calibration', 'operability']
receipts['revision'] = subprocess.check_output(
    ['git', '-C', REPO, 'rev-parse', 'master'], text=True).strip()
receipts['counter_sha256'] = sha(counter_text)
receipts['before_controls'] = []
for rev in ['4401b72f64a2202fd30f26479c463e9b9d9cabad',
            '7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd']:
    command = ['python3', str(pathlib.Path(REPO) / '.ufo/waves/round-85/count.py'),
               'c2', '--repo', REPO, '--rev', rev, '--work', str(SCRATCH)]
    p = subprocess.run(command, capture_output=True, text=True, env=ENV, cwd=SCRATCH)
    receipts['before_controls'].append({'command': command, 'exit': p.returncode,
                                       'stdout': p.stdout, 'stderr': p.stderr})
ex = pathlib.Path(REPO) / '.ufo/waves/round-85/w1/out/EX01DebtControls/tools/round81-append-debt.py'
subjects = {'delivered': src, 'independent': candidate, 'EX01': ex.read_text()}
receipts['subjects'] = {}
for label, text in subjects.items():
    probe = BUILD / (label + '.py')
    probe.write_text(text)
    before = run_selftest(probe)
    record = {'sha256': sha(text), 'pristine': before, 'mutants': {}}
    names = ['M1', 'M2', 'M3', 'M4', 'M5'] if label != 'delivered' else ['M1', 'M5']
    for name in names:
        a, b = MUTANTS[name]
        assert text.count(a) == 1, (label, name, text.count(a))
        altered = text.replace(a, b)
        try:
            probe.write_text(altered)
            result = run_selftest(probe)
        finally:
            probe.write_text(text)
        restored = run_selftest(probe)
        result.update({'before_sha256': sha(text), 'mutated_sha256': sha(altered),
                       'restored_sha256': sha(probe.read_text()), 'restored': restored})
        record['mutants'][name] = result
    receipts['subjects'][label] = record
    (OUT / (label + '-candidate.py')).write_text(text)
receipts['mutations'] = MUTANTS
(OUT / 'receipts.json').write_text(json.dumps(receipts, indent=2) + '\n')
for label, record in receipts['subjects'].items():
    print(label, 'pristine', record['pristine']['exit'], record['pristine']['tally'])
    for name, result in record['mutants'].items():
        print(label, name, result['exit'], result['tally'], result['verdict'],
              result['note_fails'], 'restored', result['restored']['exit'],
              result['restored_sha256'] == result['before_sha256'])
