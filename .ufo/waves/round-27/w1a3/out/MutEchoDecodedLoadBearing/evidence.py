#!/usr/bin/env python3
"""Preserve actual scratch diffs and summarize the three detector phases."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from pathlib import Path
import sys

LANE = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
OUT = LANE / '.ufo/waves/round-27/w1a3/out/MutEchoDecodedLoadBearing'
SCRATCH = Path('/fast/scratch/hyaku/kama-r27c/MutEchoDecodedLoadBearing')
SOURCE = LANE / '.ufo/waves/round-27/count-c1.py'
PIN = '49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765'
LABELS = ('M1', 'M2', 'M3', 'M4', 'M5')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(name: str) -> dict:
    return json.loads((OUT / name).read_bytes())


def save(name: str, data: dict) -> None:
    (OUT / name).write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('capture', 'finish'))
    args = parser.parse_args()
    original = (SCRATCH / 'pristine.py').read_bytes()
    assert sha(original) == PIN and SOURCE.read_bytes() == original
    if args.phase == 'capture':
        result = {}
        for label in LABELS:
            current = (SCRATCH / f'{label}.py').read_bytes()
            receipt = load(f'{label}.mutated.json')
            assert sha(current) == receipt['counter_sha256_before'] == receipt['counter_sha256_after']
            patch = ''.join(difflib.unified_diff(
                original.decode().splitlines(keepends=True), current.decode().splitlines(keepends=True),
                fromfile='pristine.py', tofile=f'{label}.py', n=3))
            assert patch
            (OUT / f'{label}.diff').write_text(patch, encoding='utf-8')
            result[label] = {'original_sha256': PIN, 'mutated_sha256': sha(current),
                             'diff': f'{label}.diff'}
        save('mutations.json', result)
        print('captured actual diffs and hashes for M1 M2 M3 M4 M5; exit=0')
        return 0

    mutations = load('mutations.json')
    rows = []
    for label in LABELS:
        receipts = {phase: load(f'{label}.{phase}.json')
                    for phase in ('pristine', 'mutated', 'restored')}
        assert all(receipt['total'] == 12 for receipt in receipts.values())
        assert receipts['pristine']['flagged'] == receipts['restored']['flagged'] == 12
        assert receipts['pristine']['counter_sha256_before'] == PIN
        assert receipts['restored']['counter_sha256_before'] == PIN
        assert all(receipt['counter_sha256_before'] == receipt['counter_sha256_after']
                   for receipt in receipts.values())
        assert sha((SCRATCH / f'{label}.py').read_bytes()) == PIN
        mutation = receipts['mutated']
        verdict = 'survived' if mutation['flagged'] == 12 else 'killed'
        row = {'mutant': label, 'verdict': verdict, 'total': 12,
               'phase_flagged': {phase: receipt['flagged'] for phase, receipt in receipts.items()},
               'phase_exit_codes': {phase: receipt['exit_code'] for phase, receipt in receipts.items()},
               'phase_hashes': {phase: receipt['counter_sha256_before'] for phase, receipt in receipts.items()},
               'restored_exact_bytes': (SCRATCH / f'{label}.py').read_bytes() == original,
               'matched_guard_names': sorted({guard for item in mutation['rows']
                                             for hit in item['hits'] for guard in hit['guards']}),
               'all_hits_exact_case_verbatim': all(hit['exact_case_verbatim'] for item in mutation['rows'] for hit in item['hits']),
               'diff': mutations[label]['diff']}
        rows.append(row)
        print(f"{label} pristine={receipts['pristine']['flagged']}/12 mutated={mutation['flagged']}/12 restored={receipts['restored']['flagged']}/12 {verdict} exact_restoration=True")
    save('summary.json', {'rows': rows, 'source_sha256': PIN, 'lane_source_unchanged': True,
                          'all_scratch_restored_exact_bytes': True, 'exit_code': 0})
    print('lane source and six scratch files match frozen bytes; exit=0')
    return 0


if __name__ == '__main__':
    sys.exit(run())
