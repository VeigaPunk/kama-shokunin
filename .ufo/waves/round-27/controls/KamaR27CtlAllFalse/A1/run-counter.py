#!/usr/bin/env python3
"""Record pristine, replay and restoration with the unmodified A1 detector."""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path('/fast/scratch/hyaku/kama-r27/KamaR27CtlAllFalse-A1')
OUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/controls/KamaR27CtlAllFalse/A1')
COUNTER = '.ufo/waves/round-27/count-c1.py'
PIN = '780c915672177f7d673eecec1bf2204aaf39c3c4ca837f23335c2995513885a6'
FILES = ['SKILL.md', 'corpus/SOURCES.md', 'registry/error-signatures-r27.json', COUNTER]

def hashes():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            if (ROOT / name).is_file() else None for name in FILES}

def caps():
    resource.setrlimit(resource.RLIMIT_AS, (16 * 1024**3, 16 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_NOFILE, (1024, 1024))

stage = sys.argv[1]
if stage not in {'pristine', 'replay40', 'augmented', 'restored'}:
    raise SystemExit('unknown stage')
before = hashes()
if before[COUNTER] != PIN:
    raise SystemExit('frozen A1 counter hash mismatch')
env = dict(os.environ)
for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
    env.pop(key, None)
if stage in {'replay40', 'augmented'}:
    patch = subprocess.run(['git', '-C', str(ROOT), 'diff', '--', 'SKILL.md', 'corpus/SOURCES.md'],
                           env=env, capture_output=True, timeout=30, check=True)
    (OUT / f'{stage}-control.diff').write_bytes(patch.stdout)
command = ['flock', '/fast/scratch/hyaku/kama-r27/counter.lock', 'timeout', '900',
           'python3', COUNTER, '--lane', '.', '--repo', '.',
           '--out', str(OUT / f'{stage}-receipt.json')]
started = time.monotonic()
run = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=3300, preexec_fn=caps)
(OUT / f'{stage}-stdout.txt').write_bytes(run.stdout)
(OUT / f'{stage}-stderr.txt').write_bytes(run.stderr)
(OUT / f'{stage}-exit-code.txt').write_text(str(run.returncode) + '\n')
record = {'stage': stage, 'cwd': str(ROOT), 'command': command, 'exit_code': run.returncode,
          'seconds': round(time.monotonic() - started, 3), 'before_hashes': before,
          'after_hashes': hashes(), 'stdout': run.stdout.decode('utf-8', 'replace'),
          'stderr': run.stderr.decode('utf-8', 'replace'),
          'memory_address_space_cap_bytes': 16 * 1024**3, 'file_descriptor_cap': 1024,
          'core_dump_cap_bytes': 0}
(OUT / f'{stage}-run.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
raise SystemExit(run.returncode)
