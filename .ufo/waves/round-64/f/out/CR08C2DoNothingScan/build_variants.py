#!/usr/bin/env python3
"""Build 'only this change' variants on top of the round-64 base tip.

Each variant is a commit whose tree is exactly the base tree with ONE of the
integration's changes applied (the file blob taken from the measured tip).
Nothing is written outside the scratch clone.
"""
import os
import subprocess
import sys

REPO = '/fast/scratch/hyaku/kama-r64/f/CR08C2DoNothingScan/clone'
BASE = '0c1eff3cb9ac4c11402ab0124c35842f06a436fc'
TIP = '23b3fdb1a925129a9961cf551f6d40bf251602cb'

ENV = dict(os.environ,
           GIT_AUTHOR_NAME='seat', GIT_AUTHOR_EMAIL='seat@seat.invalid',
           GIT_COMMITTER_NAME='seat', GIT_COMMITTER_EMAIL='seat@seat.invalid')


def git(*args, input_bytes=None, env=None):
    return subprocess.run(['git', '-C', REPO, *args], capture_output=True,
                          input=input_bytes, env=env or ENV)


def blob_at(rev, path):
    p = git('show', f'{rev}:{path}')
    assert p.returncode == 0, (rev, path, p.stderr)
    return p.stdout


def commit_tree(name, files):
    """files: {path: bytes}. Returns the commit sha."""
    idx = f'/fast/scratch/hyaku/kama-r64/f/CR08C2DoNothingScan/idx-{name}'
    if os.path.exists(idx):
        os.remove(idx)
    e = dict(ENV, GIT_INDEX_FILE=idx)
    p = subprocess.run(['git', '-C', REPO, 'read-tree', BASE + '^{tree}'],
                       capture_output=True, env=e)
    assert p.returncode == 0, p.stderr
    for path, data in files.items():
        h = subprocess.run(['git', '-C', REPO, 'hash-object', '-w', '--stdin'],
                           capture_output=True, input=data, env=e)
        assert h.returncode == 0, h.stderr
        u = subprocess.run(['git', '-C', REPO, 'update-index', '--add',
                            '--cacheinfo',
                            f'100644,{h.stdout.decode().strip()},{path}'],
                           capture_output=True, env=e)
        assert u.returncode == 0, u.stderr
    w = subprocess.run(['git', '-C', REPO, 'write-tree'], capture_output=True,
                       env=e)
    assert w.returncode == 0, w.stderr
    c = subprocess.run(['git', '-C', REPO, 'commit-tree',
                        w.stdout.decode().strip(), '-p', BASE, '-m', name],
                       capture_output=True, env=e)
    assert c.returncode == 0, c.stderr
    sha = c.stdout.decode().strip()
    os.remove(idx)
    return sha


base_sc = blob_at(BASE, 'SCORECARD.md').decode('utf-8')
tip_sc = blob_at(TIP, 'SCORECARD.md').decode('utf-8')
marker = '## Round 64 — process-bound request plane'
assert marker in tip_sc
r64_section = tip_sc[tip_sc.index(marker):]

variants = {}

# 1. the claim registry only
variants['v1-claims'] = {
    'registry/capability-claims-r64.tsv':
        blob_at(TIP, 'registry/capability-claims-r64.tsv')}

# 2. the regression table only
variants['v2-regress'] = {
    'registry/capability-regress-r64.tsv':
        blob_at(TIP, 'registry/capability-regress-r64.tsv')}

# 3. the counter instrument only
variants['v3-counter'] = {
    'tools/round64-c2-counter.py':
        blob_at(TIP, 'tools/round64-c2-counter.py')}

# 4. the reconciler (closure_ptr conjunct) only
variants['v4-reconciler'] = {
    'tools/round42-selfdesc-reconcile.py':
        blob_at(TIP, 'tools/round42-selfdesc-reconcile.py')}

# 5. the shortcut-tally reader only
variants['v5-tally'] = {
    'tools/shortcut-tally.py': blob_at(TIP, 'tools/shortcut-tally.py')}

# 6. the SCORECARD canonical list only: base SCORECARD + the round-64
#    canonical-list section appended (nothing else of the tip's SCORECARD).
variants['v6-canon'] = {
    'SCORECARD.md': (base_sc.rstrip('\n') + '\n\n' + r64_section).encode()}

# 6b. the whole tip SCORECARD.md (canonical list + calibration-row repair)
variants['v6b-scorecard-full'] = {'SCORECARD.md': tip_sc.encode()}

# 7. the hexrun ledger row only
variants['v7-hexrun-ledger'] = {
    'registry/hexrun-ledger.tsv': blob_at(TIP, 'registry/hexrun-ledger.tsv')}

out = []
for name, files in variants.items():
    sha = commit_tree(name, files)
    # verify the tree differs from BASE only in the intended paths
    d = subprocess.run(['git', '-C', REPO, 'diff', '--name-only', BASE, sha],
                       capture_output=True, env=ENV).stdout.decode().split()
    assert sorted(d) == sorted(files), (name, d, sorted(files))
    out.append((name, sha, d))
    print(f'{name}\t{sha}\t{",".join(d)}')

with open('/fast/scratch/hyaku/kama-r64/f/CR08C2DoNothingScan/variants.tsv',
          'w') as fh:
    for name, sha, d in out:
        fh.write(f'{name}\t{sha}\t{",".join(d)}\n')
print('OK')
