#!/usr/bin/env python3
"""Scratch wrapper: same log composition as attempt-1 score-probe.py, my paths only."""
import os
import subprocess
import sys
from pathlib import Path

D = Path('/tmp/kama-r29-w2-RerunCtlSourceBounds')
COUNTER = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py')
phase, tip, outname = sys.argv[1:]
receipt = D / 'out' / f'wrapped-{phase}-receipt.json'
argv = ['/usr/bin/timeout', '300', '/usr/bin/python3', str(COUNTER),
        '--repo', str(D / 'repo'), '--tip', tip, '--out', str(receipt)]
env = {k: v for k, v in os.environ.items()
       if k not in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE',
                    'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
                    'GIT_REPLACE_REF_BASE')}
p = subprocess.run(argv, env=env, capture_output=True, timeout=310)
log = p.stdout + (b'\n[stderr]\n' + p.stderr if p.stderr else b'') + f'\nexit={p.returncode}\n'.encode()
(D / 'out' / outname).write_bytes(log)
print(f"{phase} exit={p.returncode} bytes={len(log)} receipt_bytes={receipt.stat().st_size}")
