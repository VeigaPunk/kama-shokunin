#!/usr/bin/env python3
"""Reproduce round-11 counts and isolated negative controls; no live endpoint I/O.

Run: python3 .ufo/waves/round-11/reproduce.py
0 = expected measurements observed; 1 = unexpected verdict; 2 = could not evaluate.
Frozen input digests are verified BEFORE any gate comparison. Only temporary
copies are mutated; the lane tree is read-only. Output is a complete JSON receipt.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
WAVE = ROOT / '.ufo/waves/round-11'


def run(*args):
    command = [sys.executable, str(WAVE / 'measure.py'), *map(str, args)]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return {'command': command, 'exit': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr}


def main():
    expected = json.loads((WAVE / 'frozen/expected.json').read_text())
    mismatches = []
    for name, digest in expected['inputs'].items():
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            mismatches.append(name)
    if mismatches:
        print(json.dumps({'error': 'snapshot_tampered', 'inputs': mismatches}))
        return 2
    baseline = WAVE / 'legacy-baseline.json'
    records = {}
    ok = True
    for label, tree in [('before', WAVE / 'frozen/before'), ('after', ROOT)]:
        record = run('provenance', '--root', tree, '--baseline', baseline)
        payload = json.loads(record['stdout'])
        target = expected[label]
        match = record['exit'] == target['exit'] and all(
            payload.get(key) == value for key, value in target.items() if key != 'exit')
        record['matches_expected'] = match
        records[label] = record
        ok = ok and match
        crosswalk = run('crosswalk', '--root', tree)
        count = json.loads(crosswalk['stdout']).get('entry')
        crosswalk['matches_expected'] = count == expected['crosswalk_' + label] and (
            crosswalk['exit'] == (0 if label == 'after' else 1))
        records['crosswalk_' + label] = crosswalk
        ok = ok and crosswalk['matches_expected']
    records['selftest'] = run('--selftest')
    ok = ok and records['selftest']['exit'] == 0
    legacy = json.loads(baseline.read_text())
    selected = next(iter(legacy))
    original = (ROOT / selected).read_bytes()
    extent = legacy[selected]['bytes']
    with tempfile.TemporaryDirectory(prefix='kama-round11-controls-') as temp:
        copied = Path(temp)
        for name in legacy:
            dest = copied / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        variants = {
            'missing-field': original[:extent] + b'\n'.join(
                line for line in original[extent:].split(b'\n') if not line.startswith(b'recheck:')),
            'prefix-mutation': bytes([original[0] ^ 1]) + original[1:],
        }
        for finding, changed in variants.items():
            (copied / selected).write_bytes(changed)
            record = run('provenance', '--root', copied, '--baseline', baseline)
            payload = json.loads(record['stdout'])
            record['matches_expected'] = record['exit'] == 1 and finding in {
                row['name'] for row in payload.get('findings', [])}
            records['control_' + finding] = record
            ok = ok and record['matches_expected']
            (copied / selected).write_bytes(original)
        tampered = copied / 'baseline.json'
        tampered.write_bytes(baseline.read_bytes() + b' ')
        record = run('provenance', '--root', copied, '--baseline', tampered)
        record['matches_expected'] = record['exit'] == 2 and json.loads(
            record['stdout']).get('error') == 'snapshot_tampered'
        records['control_baseline-tampered'] = record
        ok = ok and record['matches_expected']
    revision = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'],
                              capture_output=True, text=True, check=True).stdout.strip()
    print(json.dumps({'schema': 'kama-round-11-reproduction/v1',
                      'measured_commit': revision, 'frozen_digests_verified': len(expected['inputs']),
                      'ok': ok, 'records': records}, indent=2))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
