#!/usr/bin/env python3
"""Reproduce C2's run_bound child environment and grade two scan templates.

run_bound (round62-c2-counter.py:259-262) executes `bash -c cmd` with the env
main() built at :379-382: dict(os.environ) + TMPDIR=scratch, PYTHONPATH popped.
It does NOT strip GIT_* -- so a hostile parent env reaches the bound tools.

Two arms: clean parent env, and parent env carrying the three named hostile
GIT_* vars (+ GIT_WORK_TREE) pointing at a decoy repo. Prints JSON.
"""
import json, os, subprocess, sys, tempfile

LANE, TIP = '/home/vgpnk/Projects/shokunin/kama-shokunin', sys.argv[1]
DECOY = sys.argv[2]          # decoy repo worktree (hostile git target)
scratch = tempfile.mkdtemp(prefix='e10-childenv-')
HOSTILE = {'GIT_DIR': os.path.join(DECOY, '.git'),
           'GIT_WORK_TREE': DECOY, 'GIT_WORK_DIR': DECOY,
           'GIT_INDEX_FILE': os.path.join(os.path.dirname(DECOY), 'decoy-index')}
CMDS = [
    ('digest-ledger', ['python3', f'{LANE}/tools/digest-ledger.py', 'scan',
                       '--repo', LANE, '--rev', TIP], 'unknown=0'),
    ('hexrun-census', ['python3', f'{LANE}/tools/hexrun-census.py', 'scan',
                       '--repo', LANE, '--rev', TIP], 'unknown=0'),
]
out = []
for arm in ('clean', 'hostile'):
    base = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    base['TMPDIR'] = scratch
    base.pop('PYTHONPATH', None)
    if arm == 'hostile':
        base.update(HOSTILE)
    for cap, argv, pattern in CMDS:
        p = subprocess.run(['bash', '-c', ' '.join(argv)], capture_output=True,
                           text=True, timeout=900, cwd=LANE, env=base)
        text = (p.stdout + p.stderr).strip()
        out.append({'arm': arm, 'cap': cap, 'rc': p.returncode,
                    'pattern_present': pattern in text,
                    'child_git_vars': sorted(k for k in base if k.startswith('GIT_')),
                    'tail': text.splitlines()[-1][:200] if text else ''})
subprocess.run(['rm', '-rf', scratch])
print(json.dumps(out, indent=1))
