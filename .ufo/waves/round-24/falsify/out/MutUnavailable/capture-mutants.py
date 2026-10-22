#!/usr/bin/env python3
"""Capture the assigned --only run without changing the pinned detector."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import sys

SCRATCH = Path('/fast/scratch/hyaku/kama-r24/falsify/MutUnavailable')
OUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutUnavailable')
AUDIT = SCRATCH / 'tools/report-landing-audit.py'
GRID = SCRATCH / 'tests/report-audit/promisor-grid.py'
RUNNER = SCRATCH / 'tests/report-audit/promisor-mutants.py'
MANIFEST = SCRATCH / 'tests/report-audit/promisor-grid-expectations.json'
SELECTORS = ('PM03-skip-required-object-availability',
             'PM04-accept-unavailable-referenced-object')
TIMEOUT = 600

os.environ['TMPDIR'] = str(SCRATCH)
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True
OUT.mkdir(parents=True, exist_ok=True)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, doc):
    (OUT / name).write_text(json.dumps(doc, indent=2, sort_keys=True) + '\n')


pinned = (AUDIT, GRID, RUNNER, MANIFEST)
before_bytes = AUDIT.read_bytes()
before = {str(p.relative_to(SCRATCH)): digest(p) for p in pinned}
module = runpy.run_path(str(RUNNER), run_name='mut_unavailable_capture')
namespace = module['main'].__globals__
original_run_grid = namespace['run_grid']
calls = []


def captured_grid(grid, auditor, arm, cases, timeout):
    stage = 'pristine' if not calls else Path(auditor).stem
    result = original_run_grid(grid, auditor, arm, cases, timeout)
    rc, rows, err, doc = result
    evidence = {
        'stage': stage,
        'command': [sys.executable, str(grid), '--arm', arm, '--current',
                    str(auditor), '--json'] +
                   [arg for case in cases or [] for arg in ('--case', case)],
        'exit': rc,
        'auditor_sha256': digest(auditor),
        'stderr': err,
        'harness_fault': namespace['harness_fault'](doc, rows, err),
        'violated_graded_rows': [namespace['row_name'](r)
                                 for r in namespace['violated_rows'](rows or [])],
        'document': doc,
    }
    name = f'grid-{len(calls):02d}-{stage}.json'
    save(name, evidence)
    calls.append({'artifact': name, 'stage': stage, 'exit': rc,
                  'auditor_sha256': evidence['auditor_sha256'],
                  'violated_graded_rows': evidence['violated_graded_rows'],
                  'harness_fault': evidence['harness_fault']})
    return result


namespace['run_grid'] = captured_grid
args = ['--current', str(AUDIT), '--grid', str(GRID), '--arm', 'current',
        '--grid-timeout', str(TIMEOUT), '--json']
for selector in SELECTORS:
    args += ['--only', selector]
stdout = io.StringIO()
stderr = io.StringIO()
runner_exit = None
try:
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runner_exit = module['main'](args)
finally:
    (OUT / 'runner.stdout.json').write_text(stdout.getvalue())
    (OUT / 'runner.stderr.txt').write_text(stderr.getvalue())
    after = {str(p.relative_to(SCRATCH)): digest(p) for p in pinned}
    save('runner-command-and-hashes.json', {
        'command': [sys.executable, str(RUNNER), *args],
        'entrypoint': str(Path(__file__).resolve()),
        'exit': runner_exit,
        'tmpdir': os.environ['TMPDIR'],
        'before': before,
        'after_runner': after,
        'candidate_exact_bytes_unchanged': AUDIT.read_bytes() == before_bytes,
        'manifest_exact_hash_unchanged': before[str(MANIFEST.relative_to(SCRATCH))] == after[str(MANIFEST.relative_to(SCRATCH))],
        'calls': calls,
        'PM08_executed': False,
    })
print(json.dumps({'runner_exit': runner_exit, 'calls': calls,
                  'stdout': stdout.getvalue(), 'stderr': stderr.getvalue(),
                  'candidate_exact_bytes_unchanged': AUDIT.read_bytes() == before_bytes,
                  'all_pinned_hashes_unchanged': before == after}, indent=2))
sys.exit(runner_exit)
