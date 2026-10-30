#!/usr/bin/env python3
"""Coupling diagnostics: which single change explains which failing field."""
import os
import subprocess

REPO = '/fast/scratch/hyaku/kama-r64/f/CR08C2DoNothingScan/clone'
BASE = '0c1eff3cb9ac4c11402ab0124c35842f06a436fc'
TIP = '23b3fdb1a925129a9961cf551f6d40bf251602cb'
ENV = dict(os.environ,
           GIT_AUTHOR_NAME='seat', GIT_AUTHOR_EMAIL='seat@seat.invalid',
           GIT_COMMITTER_NAME='seat', GIT_COMMITTER_EMAIL='seat@seat.invalid')


def git(*a, input_bytes=None, env=None):
    return subprocess.run(['git', '-C', REPO, *a], capture_output=True,
                          input=input_bytes, env=env or ENV)


def blob_at(rev, path):
    p = git('show', f'{rev}:{path}')
    assert p.returncode == 0, (rev, path, p.stderr)
    return p.stdout


def commit_tree(name, files):
    idx = f'/fast/scratch/hyaku/kama-r64/f/CR08C2DoNothingScan/idx-{name}'
    if os.path.exists(idx):
        os.remove(idx)
    e = dict(ENV, GIT_INDEX_FILE=idx)
    subprocess.run(['git', '-C', REPO, 'read-tree', BASE + '^{tree}'],
                   capture_output=True, env=e, check=True)
    for path, data in files.items():
        h = subprocess.run(['git', '-C', REPO, 'hash-object', '-w', '--stdin'],
                           capture_output=True, input=data, env=e, check=True)
        subprocess.run(['git', '-C', REPO, 'update-index', '--add',
                        '--cacheinfo',
                        f'100644,{h.stdout.decode().strip()},{path}'],
                       capture_output=True, env=e, check=True)
    w = subprocess.run(['git', '-C', REPO, 'write-tree'], capture_output=True,
                       env=e, check=True)
    c = subprocess.run(['git', '-C', REPO, 'commit-tree',
                        w.stdout.decode().strip(), '-p', BASE, '-m', name],
                       capture_output=True, env=e, check=True)
    os.remove(idx)
    return c.stdout.decode().strip()


claims = blob_at(TIP, 'registry/capability-claims-r64.tsv')
regress = blob_at(TIP, 'registry/capability-regress-r64.tsv')
ledger = blob_at(TIP, 'registry/hexrun-ledger.tsv')
recon = blob_at(TIP, 'tools/round42-selfdesc-reconcile.py')

combos = {
    # claims + hexrun ledger: does the ledger row clear v1's hexrun mismatch?
    'x-claims+hexrun': {
        'registry/capability-claims-r64.tsv': claims,
        'registry/hexrun-ledger.tsv': ledger},
    # claims + regress: does the registry silence the regress-only crash?
    'x-claims+regress': {
        'registry/capability-claims-r64.tsv': claims,
        'registry/capability-regress-r64.tsv': regress},
    # claims + reconciler: does the closure conjunct clear recon_mismatches?
    'x-claims+reconciler': {
        'registry/capability-claims-r64.tsv': claims,
        'tools/round42-selfdesc-reconcile.py': recon},
}

for name, files in combos.items():
    sha = commit_tree(name, files)
    d = subprocess.run(['git', '-C', REPO, 'diff', '--name-only', BASE, sha],
                       capture_output=True, env=ENV).stdout.decode().split()
    assert sorted(d) == sorted(files), (name, d)
    print(f'{name}\t{sha}\t{",".join(d)}')
