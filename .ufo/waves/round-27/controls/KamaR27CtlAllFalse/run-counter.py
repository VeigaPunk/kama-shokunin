#!/usr/bin/env python3
"""Record the frozen bounded detector for one isolated control stage."""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path('/fast/scratch/hyaku/kama-r27/KamaR27CtlAllFalse')
EVIDENCE = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/controls/KamaR27CtlAllFalse')
COUNTER = '.ufo/waves/round-27/count-c1.py'
PIN = '382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6'
STAGES = {'pristine', 'all-false', 'restored'}
FILES = ['SKILL.md', 'corpus/SOURCES.md', 'registry/error-signatures-r27.json', COUNTER]

def digests():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            if (ROOT / name).is_file() else None for name in FILES}

def limits():
    resource.setrlimit(resource.RLIMIT_AS, (16 * 1024**3, 16 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_NOFILE, (1024, 1024))

stage = sys.argv[1]
if stage not in STAGES:
    raise SystemExit('unknown stage')
before = digests()
if before[COUNTER] != PIN:
    raise SystemExit('frozen counter hash mismatch')
env = dict(os.environ)
for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
    env.pop(key, None)
if stage == 'all-false':
    diff = subprocess.run(['git', '-C', str(ROOT), 'diff', '--', 'SKILL.md', 'corpus/SOURCES.md'],
                          env=env, capture_output=True, timeout=30, check=True)
    (EVIDENCE / 'control.diff').write_bytes(diff.stdout)
command = ['flock', '/fast/scratch/hyaku/kama-r27/counter.lock', 'timeout', '900',
           'python3', COUNTER, '--lane', '.', '--repo', '.',
           '--out', str(EVIDENCE / f'{stage}-receipt.json')]
start = time.monotonic()
run = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=3300,
                     preexec_fn=limits)
(EVIDENCE / f'{stage}-stdout.txt').write_bytes(run.stdout)
(EVIDENCE / f'{stage}-stderr.txt').write_bytes(run.stderr)
(EVIDENCE / f'{stage}-exit-code.txt').write_text(str(run.returncode) + '\n')
record = {'stage': stage, 'cwd': str(ROOT), 'command': command,
          'exit_code': run.returncode, 'seconds': round(time.monotonic() - start, 3),
          'stdout': run.stdout.decode('utf-8', 'replace'),
          'stderr': run.stderr.decode('utf-8', 'replace'),
          'before_hashes': before, 'after_hashes': digests(),
          'memory_address_space_cap_bytes': 16 * 1024**3,
          'core_dump_cap_bytes': 0, 'file_descriptor_cap': 1024}
(EVIDENCE / f'{stage}-run.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
raise SystemExit(run.returncode)
