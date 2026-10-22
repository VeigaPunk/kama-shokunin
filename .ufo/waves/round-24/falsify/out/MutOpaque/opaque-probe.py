#!/usr/bin/env python3
"""Observe only PM10/PM11 in the pinned runner; restore each temp specimen.

The stock runner's run_grid, mutation application, and classifier remain the
implementation under test. The observer saves its returned grid documents and
executes that same detector once more after restoring the mutant's exact bytes.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

SCRATCH = Path('/fast/scratch/hyaku/kama-r24/falsify/MutOpaque')
OUTPUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/MutOpaque')
AUDIT = SCRATCH / 'tools/report-landing-audit.py'
GRID = SCRATCH / 'tests/report-audit/promisor-grid.py'
RUNNER = SCRATCH / 'tests/report-audit/promisor-mutants.py'
MANIFEST = SCRATCH / 'tests/report-audit/promisor-grid-expectations.json'
ALLOWED = {'PM10-ignore-opaque-nonleaf-missing', 'PM11-any-hole-refusal'}
PINNED = {
    AUDIT: 'ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220',
    GRID: 'b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa',
    MANIFEST: 'd86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1',
    RUNNER: '6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def emit(path, doc):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(doc, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    args = sys.argv[1:]
    selected = [args[i + 1] for i, item in enumerate(args) if item == '--only']
    if len(selected) != 1 or selected[0] not in ALLOWED:
        raise SystemExit('this observer requires exactly one registered PM10/PM11 --only')
    if '--case' not in args or '--json' not in args:
        raise SystemExit('bounded explicit cases and JSON are required')
    label = selected[0].split('-')[0]
    capture = OUTPUT / label
    capture.mkdir()
    pristine = AUDIT.read_bytes()
    before = {str(path): digest(path.read_bytes()) for path in PINNED}
    if any(before[str(path)] != expected for path, expected in PINNED.items()):
        raise SystemExit('pinned source hash mismatch')
    namespace = runpy.run_path(str(RUNNER), run_name='MutOpaque_stock_inventory')
    stock_main = namespace['main']
    stock_run_grid = namespace['run_grid']
    target = next(m for m in namespace['MUTANTS'] if m['id'] == selected[0])
    transformed, alternative = namespace['apply_mutation'](pristine.decode('utf-8'), target)
    anchor = target['alternatives'][alternative]['anchor']
    state = {
        'argv': [sys.executable, str(Path(__file__).resolve()), *args],
        'pinned_revision': '2e254a1763a9c08aa07fc53081287f506c447d84',
        'only': selected,
        'hashes_before': before,
        'pattern': {'kind': 'insert', 'anchor': anchor,
                    'matches': pristine.decode('utf-8').count(anchor),
                    'alternative': alternative,
                    'compiles': namespace['compiles'](transformed, selected[0]),
                    'transformed_sha256': digest(transformed.encode('utf-8'))},
        'captures': [],
    }

    def save(stage, grid, auditor, arm, cases, timeout, input_hash, result, after_hash):
        code, rows, err, doc = result
        record = {
            'stage': stage,
            'command': [sys.executable, str(grid), '--arm', arm, '--current',
                        str(auditor), '--json',
                        *[part for case in cases or [] for part in ('--case', case)]],
            'timeout_seconds': timeout,
            'auditor_sha256_before': input_hash,
            'auditor_sha256_after_detector': after_hash,
            'grid_exit': code,
            'grid_stderr': err,
            'stock_harness_fault': namespace['harness_fault'](doc, rows, err),
            'stock_violated_rows': [namespace['row_name'](r)
                                    for r in namespace['violated_rows'](rows or [])],
            'grid_document': doc,
        }
        emit(capture / f'{stage}-grid.json', record)
        state['captures'].append({key: record[key] for key in (
            'stage', 'grid_exit', 'auditor_sha256_before',
            'auditor_sha256_after_detector', 'stock_harness_fault',
            'stock_violated_rows')})

    def observed_run_grid(grid, auditor, arm, cases, timeout):
        auditor = Path(auditor)
        specimen = auditor.name == selected[0] + '.py'
        if auditor != AUDIT and not specimen:
            raise RuntimeError(f'unexpected auditor input: {auditor}')
        if specimen and SCRATCH not in auditor.resolve().parents:
            raise RuntimeError('specimen escaped the assigned scratch')
        input_hash = digest(auditor.read_bytes())
        if not specimen:
            result = stock_run_grid(grid, auditor, arm, cases, timeout)
            save('pristine', grid, auditor, arm, cases, timeout, input_hash,
                 result, digest(auditor.read_bytes()))
            return result
        try:
            result = stock_run_grid(grid, auditor, arm, cases, timeout)
            save('mutated', grid, auditor, arm, cases, timeout, input_hash,
                 result, digest(auditor.read_bytes()))
        finally:
            # The stock runner owns this temporary file and removes it later.
            # Restore first, even when the detector or the observer raises.
            auditor.write_bytes(pristine)
            state['restored_specimen_sha256'] = digest(auditor.read_bytes())
            state['restored_specimen_exact_bytes'] = auditor.read_bytes() == pristine
        restored_input = digest(auditor.read_bytes())
        restored = stock_run_grid(grid, auditor, arm, cases, timeout)
        save('restored', grid, auditor, arm, cases, timeout, restored_input,
             restored, digest(auditor.read_bytes()))
        return result

    stock_main.__globals__['run_grid'] = observed_run_grid
    try:
        code = stock_main(args)
        state['stock_runner_exit'] = code
        return code
    finally:
        state['hashes_after'] = {str(path): digest(path.read_bytes()) for path in PINNED}
        state['candidate_exact_bytes_unchanged'] = AUDIT.read_bytes() == pristine
        emit(capture / 'probe-state.json', state)


if __name__ == '__main__':
    sys.exit(main())
