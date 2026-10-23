#!/usr/bin/env python3
"""Run only the assigned frozen counter, bounding every evidence-file write."""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys

ROOT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlSourceBounds')
REPO = Path('/fast/scratch/hyaku/kama-r29/ctl/CtlSourceBounds/repo')
COUNTER = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py')
EXPECTED = 'fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383'
BOUND = 1024 * 1024 - 1
phase, tip = sys.argv[1:]
if phase not in ('pristine', 'mutated', 'restored') or tip not in ('ctl', 'restored'):
    raise SystemExit('invalid phase/tip')


def save(name, data):
    data = data.encode() if isinstance(data, str) else data
    if len(data) > BOUND:
        raise RuntimeError(f'evidence exceeds bound: {name}')
    (ROOT / name).write_bytes(data)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_limit():
    resource.setrlimit(resource.RLIMIT_FSIZE, (BOUND, BOUND))


before = sha(COUNTER)
if before != EXPECTED:
    raise SystemExit(f'counter hash mismatch: {before}')
report = (ROOT / 'REPORT.md').read_bytes()
if phase == 'pristine':
    save('REPORT-before-scoring.md', report)
receipt = ROOT / ('receipt.json' if phase == 'mutated' else f'{phase}-receipt.json')
argv = ['/usr/bin/timeout', '300', '/usr/bin/python3', str(COUNTER),
        '--repo', str(REPO), '--tip', tip, '--out', str(receipt)]
env = {k: v for k, v in os.environ.items()
       if k not in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE',
                    'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
                    'GIT_REPLACE_REF_BASE')}
try:
    p = subprocess.run(argv, env=env, capture_output=True, timeout=310,
                       preexec_fn=file_limit)
    stdout, stderr, status = p.stdout, p.stderr, p.returncode
except subprocess.TimeoutExpired as e:
    stdout, stderr, status = e.stdout or b'', e.stderr or b'', 124
log = stdout + (b'\n[stderr]\n' + stderr if stderr else b'') + f'\nexit={status}\n'.encode()
log_name = 'counter.out' if phase == 'mutated' else f'{phase}-counter.out'
save(log_name, log)
state = {'phase': phase, 'tip': tip, 'argv': argv, 'exit': status,
         'counter_sha256_before': before, 'counter_sha256_after': sha(COUNTER),
         'report_sha256_before_run': hashlib.sha256(report).hexdigest(),
         'prediction_sha256': sha(ROOT / 'predictions.json'),
         'source_policy_sha256': sha(ROOT / 'source-policy.py'),
         'scorecard_sha256': sha(REPO / 'SCORECARD.md'),
         'shonen_sha256': sha(REPO / 'SHONEN.md'),
         'receipt_bytes': receipt.stat().st_size if receipt.exists() else None}
save(f'{phase}-status.json', json.dumps(state, indent=2) + '\n')
print(log.decode(errors='replace'), end='')
print(json.dumps(state, sort_keys=True))
