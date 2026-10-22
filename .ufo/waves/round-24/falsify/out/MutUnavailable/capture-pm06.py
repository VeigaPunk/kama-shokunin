#!/usr/bin/env python3
"""Capture only the parent-authorized PM06 mutation and restoration."""
from __future__ import annotations

import contextlib
import difflib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import runpy
import sys

SCRATCH = Path('/fast/scratch/hyaku/kama-r24/falsify/MutUnavailable')
OUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutUnavailable')
AUDIT = SCRATCH / 'tools/report-landing-audit.py'
GRID = SCRATCH / 'tests/report-audit/promisor-grid.py'
RUNNER = SCRATCH / 'tests/report-audit/promisor-mutants.py'
MANIFEST = SCRATCH / 'tests/report-audit/promisor-grid-expectations.json'
SELECTOR = 'PM06-swallow-actual-read-error'
TIMEOUT = 600
os.environ['TMPDIR'] = str(SCRATCH)
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True


def save(name, doc):
    (OUT / name).write_text(json.dumps(doc, indent=2, sort_keys=True) + '\n')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


pinned = (AUDIT, GRID, RUNNER, MANIFEST)
before_bytes = AUDIT.read_bytes()
before = {str(p.relative_to(SCRATCH)): digest(p) for p in pinned}
module = runpy.run_path(str(RUNNER), run_name='mut_unavailable_pm06')
namespace = module['main'].__globals__
mutant = next(m for m in module['MUTANTS'] if m['id'] == SELECTOR)
source = before_bytes.decode('utf-8')
counts = []
for alternative in mutant['alternatives']:
    if alternative['kind'] == 'insert':
        counts.append(source.count(alternative['anchor']))
    elif alternative['kind'] == 'replace':
        counts.append(source.count(alternative['old']))
    else:
        counts.append(len(re.findall(alternative['pattern'], source, re.DOTALL)))
mutated, applied = module['apply_mutation'](source, mutant)
save('pm06-anchors-and-before.json', {
    'mutant': SELECTOR, 'registered_in_initial_list_exit_0': True,
    'match_counts': counts, 'applied_alternative': applied,
    'unique_match': isinstance(applied, int) and counts[applied] == 1,
    'compiles': mutated is not None and module['compiles'](mutated, SELECTOR),
    'before': before,
    'mutated_sha256': hashlib.sha256(mutated.encode()).hexdigest() if mutated else None,
    'expect_rows': mutant['expect_rows'],
})
(OUT / 'assigned-PM06.diff').write_text(''.join(difflib.unified_diff(
    source.splitlines(keepends=True), mutated.splitlines(keepends=True),
    fromfile='pristine/tools/report-landing-audit.py',
    tofile=SELECTOR + '/tools/report-landing-audit.py', n=3)))
original_run_grid = namespace['run_grid']
calls = []


def captured_grid(grid, auditor, arm, cases, timeout):
    stage = ('pristine' if not calls else 'restored') if Path(auditor) == AUDIT else SELECTOR
    rc, rows, err, doc = original_run_grid(grid, auditor, arm, cases, timeout)
    name = f'pm06-grid-{len(calls):02d}-{stage}.json'
    evidence = {
        'stage': stage,
        'command': [sys.executable, str(grid), '--arm', arm, '--current',
                    str(auditor), '--json'] +
                   [arg for case in cases or [] for arg in ('--case', case)],
        'exit': rc, 'auditor_sha256': digest(auditor), 'stderr': err,
        'harness_fault': namespace['harness_fault'](doc, rows, err),
        'violated_graded_rows': [namespace['row_name'](r) for r in namespace['violated_rows'](rows or [])],
        'document': doc,
    }
    save(name, evidence)
    calls.append({'artifact': name, 'stage': stage, 'exit': rc,
                  'auditor_sha256': evidence['auditor_sha256'],
                  'violated_graded_rows': evidence['violated_graded_rows'],
                  'harness_fault': evidence['harness_fault']})
    return rc, rows, err, doc


namespace['run_grid'] = captured_grid
args = ['--current', str(AUDIT), '--grid', str(GRID), '--arm', 'current',
        '--grid-timeout', str(TIMEOUT), '--json', '--only', SELECTOR]
stdout, stderr = io.StringIO(), io.StringIO()
runner_exit = restored_exit = None
try:
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runner_exit = module['main'](args)
    restored_exit, _, _, _ = captured_grid(GRID, AUDIT, 'current', None, TIMEOUT)
finally:
    (OUT / 'pm06-runner.stdout.json').write_text(stdout.getvalue())
    (OUT / 'pm06-runner.stderr.txt').write_text(stderr.getvalue())
    after = {str(p.relative_to(SCRATCH)): digest(p) for p in pinned}
    save('pm06-command-and-restoration.json', {
        'command': [sys.executable, str(RUNNER), *args],
        'entrypoint': str(Path(__file__).resolve()),
        'exit': runner_exit, 'restored_exit': restored_exit,
        'tmpdir': os.environ['TMPDIR'], 'before': before, 'after': after,
        'candidate_exact_bytes_restored': AUDIT.read_bytes() == before_bytes,
        'all_pinned_hashes_unchanged': before == after, 'calls': calls,
        'PM08_executed': False,
    })
print(json.dumps({'runner_exit': runner_exit, 'restored_exit': restored_exit,
                  'calls': calls, 'stdout': stdout.getvalue(),
                  'stderr': stderr.getvalue(),
                  'candidate_exact_bytes_restored': AUDIT.read_bytes() == before_bytes,
                  'all_pinned_hashes_unchanged': before == after}, indent=2))
sys.exit(runner_exit if restored_exit == 0 else 2)
