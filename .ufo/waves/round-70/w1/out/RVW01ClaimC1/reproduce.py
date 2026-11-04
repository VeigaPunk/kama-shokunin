#!/usr/bin/env python3
"""Read committed base bytes; mutate scratch copies only; retain exact receipts."""
import ast
import concurrent.futures
import hashlib
import os
from pathlib import Path
import shlex
import subprocess

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
BASE = '6035e952c2521999e192d6f236331f265ac98392'
S = Path('/fast/scratch/hyaku/kama-r70/RVW01ClaimC1')
OUT = Path(__file__).resolve().parent
S.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, TMPDIR=str(S), PYTHONDONTWRITEBYTECODE='1')
receipts = []
def run(argv):
    p = subprocess.run(argv, cwd=S, env=env, capture_output=True, text=True)
    return '$ ' + shlex.join(argv) + '\nSTDOUT:\n' + p.stdout + 'STDERR:\n' + p.stderr + f'EXIT={p.returncode}\n'
def blob(path):
    argv = ['git', '-C', LANE, 'show', f'{BASE}:{path}']
    p = subprocess.run(argv, capture_output=True, check=True)
    data = p.stdout
    receipts.append('$ ' + shlex.join(argv) + '\nSTDOUT: committed bytes retained in scratch; sha256=' + hashlib.sha256(data).hexdigest() + f' bytes={len(data)}\nSTDERR:\nEXIT={p.returncode}\n')
    return data
source = blob('tools/round42-selfdesc-reconcile.py')
r41 = blob('tools/round41-scorecard-reconcile.py')
census = blob('tools/round65-host-census.py')
node = next(n for n in ast.parse(census).body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'MEMBERS' for t in n.targets))
members = ast.literal_eval(node.value)
receipts.append('AST census MEMBERS count=' + str(len(members)) + '\nreconciler_members=' + repr([m[1] for m in members if 'round42-selfdesc' in m[1]]) + '\n')
anchor = b'    mism = sum(c.values()) + (0 if cp else 1)\n'
assert source.count(anchor) == 1
variants = {'frozen': source, 'blunt': source.replace(anchor, b'    mism = 0\n'), 'surgical': source.replace(anchor, b'    c = dict.fromkeys(c, 0)\n' + anchor)}
commands = []
for name, data in variants.items():
    root = S / ('replay-' + name)
    root.mkdir(exist_ok=True)
    script = root / 'round42-selfdesc-reconcile.py'
    script.write_bytes(data)
    (root / 'round41-scorecard-reconcile.py').write_bytes(r41)
    commands.append(['python3', str(script), '--repo', LANE, '--tip', BASE])
    commands.append(['python3', str(script), '--selftest', '--repo', LANE, '--tip', BASE, '--work', str(S / ('replay-work-' + name))])
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    receipts.extend(pool.map(run, commands))
(OUT / 'evidence.txt').write_text('\n'.join(receipts))
print('Evidence written:', OUT / 'evidence.txt')
for receipt in receipts:
    print(receipt)
