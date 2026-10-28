#!/usr/bin/env python3
"""E10CounterAST hostile-env harness (scratch-only, rounds 62).

Runs a tip-pinned round62 counter in one of three arms and captures
rc / stdout / stderr / wall time plus the exact env diff applied.

  arm=clean    : ambient env with every GIT_* var removed
  arm=hostile  : clean + GIT_DIR / GIT_WORK_TREE / GIT_WORK_DIR /
                 GIT_INDEX_FILE pointing at a decoy repo in scratch
"""
import json
import os
import subprocess
import sys
import time

S = os.path.dirname(os.path.abspath(__file__))
LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
TIP = sys.argv[1] if len(sys.argv) > 1 else '65d7cad0fce90e34de37527cde22e97b63b118bf'
WHICH = sys.argv[2]                      # c1 | c2
ARM = sys.argv[3]                        # clean | hostile
LABEL = sys.argv[4] if len(sys.argv) > 4 else f'{WHICH}-{ARM}'
WORK = os.path.join(S, 'work', LABEL)

hostile = {
    'GIT_DIR': os.path.join(S, 'decoy', '.git'),
    'GIT_WORK_TREE': os.path.join(S, 'decoy'),
    'GIT_WORK_DIR': os.path.join(S, 'decoy'),
    'GIT_INDEX_FILE': os.path.join(S, 'decoy-index'),
}

env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
env.pop('TMPDIR', None)                  # never an inherited TMPDIR
if ARM == 'hostile':
    env.update(hostile)

counter = os.path.join(S, 'bin', f'{WHICH}-tip.py')
argv = [sys.executable, counter, '--repo', LANE, '--tip', TIP, '--work', WORK]
os.makedirs(WORK, exist_ok=True)
t0 = time.monotonic()
p = subprocess.run(argv, env=env, capture_output=True, text=True,
                   cwd=S, timeout=3600)
wall = round(time.monotonic() - t0, 1)
rec = {
    'counter': WHICH, 'arm': ARM, 'label': LABEL, 'tip': TIP, 'work': WORK, 'wall_s': wall,
    'rc': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr,
    'env_diff': hostile if ARM == 'hostile' else {},
    'env_git_vars_applied': sorted(k for k in env if k.startswith('GIT_')),
}
out = os.path.join(S, 'receipts', f'{LABEL}.json')
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w') as f:
    json.dump(rec, f, indent=1, sort_keys=True)
print(json.dumps({k: rec[k] for k in ('counter', 'arm', 'rc', 'wall_s')}))
print('STDOUT:', p.stdout.strip())
if p.stderr.strip():
    print('STDERR:', p.stderr.strip()[:1500])
