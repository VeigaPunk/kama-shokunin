#!/usr/bin/env python3
"""Record only: bounded C2 runs and exact scratch-byte states; no input edits."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path('/fast/scratch/hyaku/kama-r26w2/MutC2Binding')
OUT = Path(__file__).resolve().parent
CASES = ('pristine', 'raw-bytes', 'raw-sha', 'raw-deleted', 'raw-empty', 'raw-cross-cell')
COUNTER = '.ufo/waves/round-25/count-c2.py'
FINAL = '.ufo/waves/round-25/final'
EXPECTED = 'registered 14 observed 14 bound True missing []\n'
REJECTED = 'registered 14 observed 14 bound False missing []\n'
COMMAND = ['timeout', '--kill-after=2s', '20s', 'prlimit', '--as=268435456',
           '--cpu=10', '--nproc=8', '--nofile=64', '--', 'python3', COUNTER]


def snapshot(root):
    paths = [root / COUNTER] + sorted((root / FINAL).rglob('*'))
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file()}


def run_one(case):
    root = ROOT if case == 'pristine' else ROOT / case
    before = snapshot(root)
    started = time.monotonic()
    result = subprocess.run(COMMAND, cwd=root, capture_output=True, text=True, timeout=25)
    after = snapshot(root)
    record = {
        'case': case, 'cwd': str(root), 'command': COMMAND,
        'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr,
        'elapsed_seconds': round(time.monotonic() - started, 6),
        'accepted': result.returncode == 0 and result.stdout == EXPECTED,
        'rejected': result.returncode == 0 and result.stdout == REJECTED,
        'detector_changed_bytes': before != after, 'sha256': after,
    }
    if args.stage != 'baseline':
        baseline = json.loads((OUT / 'baseline.json').read_text())
        original = next(r['sha256'] for r in baseline['runs'] if r['case'] == case)
        record['changed_files_from_baseline'] = {
            p: {'before': original.get(p), 'after': after.get(p)}
            for p in sorted(set(original) | set(after)) if original.get(p) != after.get(p)
        }
        record['exact_restoration'] = original == after
    return record


parser = argparse.ArgumentParser()
parser.add_argument('--stage', required=True)
args = parser.parse_args()
with ThreadPoolExecutor(max_workers=4) as pool:
    runs = list(pool.map(run_one, CASES))
result = {
    'stage': args.stage, 'frozen_commit': 'f4066979096e3452ae731c0e09e50155c6d8258a',
    'acceptance': 'exit 0 and ' + EXPECTED.strip(), 'max_concurrent_detectors': 4,
    'runs': runs,
}
path = OUT / (args.stage + '.json')
path.write_text(json.dumps(result, indent=2) + '\n')
for r in runs:
    print(r['case'], args.stage, 'exit=' + str(r['exit_code']),
          'stdout=' + repr(r['stdout']), 'stderr=' + repr(r['stderr']))
    if args.stage != 'baseline':
        print('changed_files=' + json.dumps(r['changed_files_from_baseline'], sort_keys=True))
        print('exact_restoration=' + str(r['exact_restoration']))
print('evidence=' + str(path))
