#!/usr/bin/env python3
"""Capture the assigned native mutation probe without changing its detector."""
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import re
import runpy
import sys
import time

ROOT = Path('/fast/scratch/hyaku/kama-r24/falsify/MutOverRefusal')
OUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutOverRefusal')
IDS = ('PM01-blanket-metadata-refusal', 'PM02-blanket-unknown-refusal')
PINNED = {
    'tools/report-landing-audit.py': 'ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220',
    'tests/report-audit/promisor-grid.py': 'b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa',
    'tests/report-audit/promisor-grid-expectations.json': 'd86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1',
    'tests/report-audit/promisor-mutants.py': '6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2',
}
assert Path.cwd() == ROOT
assert os.environ.get('TMPDIR') == str(ROOT)
OUT.mkdir(parents=True, exist_ok=True)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def hashes():
    return {name: digest((ROOT / name).read_bytes()) for name in PINNED}


def store(name, value):
    path = OUT / name
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + '\n')


before = hashes()
assert before == PINNED, before
store('hashes-before.json', before)
ns = runpy.run_path(str(ROOT / 'tests/report-audit/promisor-mutants.py'), run_name='assigned_mutation_probe')
main = ns['main']
state = main.__globals__
source = (ROOT / 'tools/report-landing-audit.py').read_bytes()
text = source.decode('utf-8')
selected = [m for m in state['MUTANTS'] if m['id'] in IDS]
assert tuple(m['id'] for m in selected) == IDS
patterns = []
for mutant in selected:
    counts = []
    for alt in mutant['alternatives']:
        if alt['kind'] == 'replace':
            count = text.count(alt['old'])
        elif alt['kind'] == 'regex':
            count = len(re.findall(alt['pattern'], text, re.DOTALL))
        else:
            count = text.count(alt['anchor'])
        counts.append({'kind': alt['kind'], 'matches': count})
    changed, alternative = state['apply_mutation'](text, mutant)
    patterns.append({
        'mutant': mutant['id'], 'alternatives': counts,
        'applied_alternative': alternative,
        'compiles': changed is not None and state['compiles'](changed, mutant['id']),
        'before_sha256': digest(source),
        'mutant_sha256': digest(changed.encode('utf-8')) if changed is not None else None,
    })
store('selected-patterns.json', patterns)
original_run_grid = state['run_grid']
calls = []


def capture_grid(grid, auditor, arm, cases, timeout):
    phase = 'pristine' if not calls else Path(auditor).stem
    if phase == 'report-landing-audit':
        phase = 'restored'
    auditor_before = Path(auditor).read_bytes()
    command = [sys.executable, str(grid), '--arm', arm, '--current', str(auditor), '--json']
    for case in cases or []:
        command.extend(('--case', case))
    record = {'phase': phase, 'argv': command, 'cwd': str(ROOT),
              'TMPDIR': str(ROOT), 'timeout_seconds': timeout,
              'auditor_sha256_before': digest(auditor_before)}
    started = time.monotonic()
    rc, rows, err, doc = original_run_grid(grid, auditor, arm, cases, timeout)
    record.update(exit=rc, elapsed_seconds=round(time.monotonic() - started, 3),
                  auditor_sha256_after=digest(Path(auditor).read_bytes()),
                  harness_fault=state['harness_fault'](doc, rows, err),
                  violated_rows=[state['row_name'](row) for row in state['violated_rows'](rows or [])])
    store(f'{phase}.grid.json', doc)
    with (OUT / f'{phase}.stderr.txt').open('x', encoding='utf-8') as stream:
        stream.write(err + ('\n' if err else ''))
    calls.append(record)
    store(f'{phase}.command.json', record)
    return rc, rows, err, doc


state['run_grid'] = capture_grid
args = ['--arm', 'current', '--only', IDS[0], '--only', IDS[1], '--grid-timeout', '600', '--json']
stdout, stderr = io.StringIO(), io.StringIO()
runner_exit = None
restored_exit = None
try:
    with redirect_stdout(stdout), redirect_stderr(stderr):
        runner_exit = main(args)
finally:
    with (OUT / 'native.stdout.json').open('x', encoding='utf-8') as stream:
        stream.write(stdout.getvalue())
    with (OUT / 'native.stderr.txt').open('x', encoding='utf-8') as stream:
        stream.write(stderr.getvalue())
    assert (ROOT / 'tools/report-landing-audit.py').read_bytes() == source
    restored_exit, _, _, _ = capture_grid(
        ROOT / 'tests/report-audit/promisor-grid.py',
        ROOT / 'tools/report-landing-audit.py', 'current', None, 600)
    after = hashes()
    store('hashes-after.json', after)
    store('probe-result.json', {
        'native_argv': [sys.executable, str(ROOT / 'tests/report-audit/promisor-mutants.py'), *args],
        'native_invocation': 'runpy load; capture-only run_grid wrapper; main(args)',
        'native_exit': runner_exit, 'restored_exit': restored_exit,
        'before_equals_after': before == after,
        'mutation_files_removed': all(not Path(call['argv'][5]).exists() for call in calls if call['phase'] in IDS),
        'calls': calls,
    })
    assert after == before
print(json.dumps({'native_exit': runner_exit, 'restored_exit': restored_exit,
                  'calls': [{k: c[k] for k in ('phase', 'exit', 'elapsed_seconds', 'harness_fault', 'violated_rows')} for c in calls],
                  'before_equals_after': before == after}, indent=2))
raise SystemExit(runner_exit if runner_exit is not None else 2)
