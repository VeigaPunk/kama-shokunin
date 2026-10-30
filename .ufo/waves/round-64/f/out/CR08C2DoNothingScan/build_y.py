#!/usr/bin/env python3
"""y-all7 and y-all7+evidence: is the seven-file C2 set sufficient on its own?"""
import os
import subprocess

REPO = '/fast/scratch/hyaku/kama-r64/f/CR08C2DoNothingScan/clone'
BASE = '0c1eff3cb9ac4c11402ab0124c35842f06a436fc'
TIP = '23b3fdb1a925129a9961cf551f6d40bf251602cb'
ENV = dict(os.environ,
           GIT_AUTHOR_NAME='seat', GIT_AUTHOR_EMAIL='seat@seat.invalid',
           GIT_COMMITTER_NAME='seat', GIT_COMMITTER_EMAIL='seat@seat.invalid')


def blob_at(rev, path):
    p = subprocess.run(['git', '-C', REPO, 'show', f'{rev}:{path}'],
                       capture_output=True)
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


SEVEN = {
    'registry/capability-claims-r64.tsv':
        blob_at(TIP, 'registry/capability-claims-r64.tsv'),
    'registry/capability-regress-r64.tsv':
        blob_at(TIP, 'registry/capability-regress-r64.tsv'),
    'tools/round64-c2-counter.py': blob_at(TIP, 'tools/round64-c2-counter.py'),
    'tools/round42-selfdesc-reconcile.py':
        blob_at(TIP, 'tools/round42-selfdesc-reconcile.py'),
    'tools/shortcut-tally.py': blob_at(TIP, 'tools/shortcut-tally.py'),
    'SCORECARD.md': blob_at(TIP, 'SCORECARD.md'),
    'registry/hexrun-ledger.tsv': blob_at(TIP, 'registry/hexrun-ledger.tsv'),
}
EVID = ('.ufo/waves/round-64/b/out/X09ScansTip/'
        'evidence-72c7713ef48cd5d5d02964ece2975602e3402a08.json')

print('y-all7\t' + commit_tree('y-all7', SEVEN))
y2 = dict(SEVEN)
y2[EVID] = blob_at(TIP, EVID)
print('y-all7+evidence\t' + commit_tree('y-all7-evidence', y2))
