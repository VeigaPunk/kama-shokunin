#!/usr/bin/env python3
"""freshness_check.py — bind SOURCES rows S038/S039 at a pinned revision to host bytes.

Offline, stdlib only, read-only. Compares:
  S038 asset size/digest      <-> host release archive bytes
  archive members              <-> installed tree (regular files by sha256, symlinks by target)
  install tree (tool rule)     <-> live receipt server.install_tree / install_tree_sha256 /
                                   server.sha256 / server.server_impl_sha256
  S039 size/LFS sha256         <-> host model bytes <-> receipt model.sha256 / model_sha256_post

Exit: 0 every check evaluated and matched; 1 at least one evaluated mismatch (an observed
verdict); 2 nothing mismatched but at least one check could not be evaluated (unreadable
input, unparseable row/receipt). Errors are never reported as mismatches.
"""
import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tarfile

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
REV = '37bd4c5bd456a2f8a54d3312c28495c321715856'
ARCHIVE = '/home/vgpnk/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz'
INSTALL = '/home/vgpnk/.local/opt/llama-b11755'
MODEL = '/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf'
RECEIPT = LANE + '/.ufo/waves/round-18/live-recovery/receipt-1.json'

S038_RE = re.compile(r'tag b11755 → commit ([0-9a-f]{40}).*?asset `([^`]+)` size (\d+), '
                     r'digest sha256:([0-9a-f]{64})')
S039_RE = re.compile(r'repo commit ([0-9a-f]{40}) \(file commit ([0-9a-f]{40})\), size (\d+), '
                     r'LFS sha256 ([0-9a-f]{64})')


def sha256_stream(fh):
    h = hashlib.sha256()
    n = 0
    for chunk in iter(lambda: fh.read(1 << 20), b''):
        h.update(chunk)
        n += len(chunk)
    return h.hexdigest(), n


def sha256_path(path):
    with open(path, 'rb') as fh:
        return sha256_stream(fh)


def tree_digest(tree):
    """Same combined digest as tools/kama-llamacpp-live.py install_tree()."""
    return hashlib.sha256(
        ''.join(f'{n} {tree[n]}\n' for n in sorted(tree)).encode()).hexdigest()


class Checks:
    def __init__(self):
        self.rows = []

    def compare(self, name, expected, observed):
        status = 'match' if expected == observed else 'mismatch'
        self.rows.append({'check': name, 'status': status,
                          'expected': expected, 'observed': observed})

    def error(self, name, detail):
        self.rows.append({'check': name, 'status': 'error', 'detail': detail})

    def exit_code(self):
        states = {r['status'] for r in self.rows}
        if 'mismatch' in states:
            return 1
        if 'error' in states or not self.rows:
            return 2
        return 0


def row_cells(lane, rev, row_id):
    text = subprocess.run(['git', '-C', lane, 'show', f'{rev}:corpus/SOURCES.md'],
                          check=True, capture_output=True, text=True).stdout
    for line in text.splitlines():
        if line.startswith(f'| {row_id} |'):
            return line
    raise LookupError(f'{row_id} not found at {rev}')


def archive_members(path):
    """{basename: ('file', sha256) | ('link', target)} for members under the top dir."""
    members = {}
    with tarfile.open(path, 'r:gz') as tf:
        for m in tf:
            parts = m.name.split('/')
            if len(parts) != 2 or not parts[1]:
                continue
            if m.isreg():
                members[parts[1]] = ('file', sha256_stream(tf.extractfile(m))[0])
            elif m.issym():
                members[parts[1]] = ('link', m.linkname)
            else:
                members[parts[1]] = ('other', m.type.decode(errors='replace'))
    return members


def installed_members(directory):
    members = {}
    for name in sorted(os.listdir(directory)):
        full = os.path.join(directory, name)
        st = os.lstat(full)
        if stat.S_ISREG(st.st_mode):
            members[name] = ('file', sha256_path(full)[0])
        elif stat.S_ISLNK(st.st_mode):
            members[name] = ('link', os.readlink(full))
        else:
            members[name] = ('other', oct(stat.S_IFMT(st.st_mode)))
    return members


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--lane', default=LANE)
    ap.add_argument('--rev', default=REV)
    ap.add_argument('--archive', default=ARCHIVE)
    ap.add_argument('--install-dir', default=INSTALL)
    ap.add_argument('--model', default=MODEL)
    ap.add_argument('--receipt', default=RECEIPT)
    ap.add_argument('--out', help='write the JSON result here as well as stdout')
    args = ap.parse_args()
    c = Checks()
    facts = {'rev': args.rev, 'archive': args.archive, 'install_dir': args.install_dir,
             'model': args.model, 'receipt': args.receipt}

    s038 = s039 = None
    try:
        m = S038_RE.search(row_cells(args.lane, args.rev, 'S038'))
        if not m:
            raise LookupError('S038 anchor pattern absent')
        s038 = {'commit': m[1], 'asset': m[2], 'size': int(m[3]), 'sha256': m[4]}
    except (OSError, subprocess.CalledProcessError, LookupError) as exc:
        c.error('S038 row parse', f'{type(exc).__name__}: {exc}')
    try:
        m = S039_RE.search(row_cells(args.lane, args.rev, 'S039'))
        if not m:
            raise LookupError('S039 anchor pattern absent')
        s039 = {'repo_commit': m[1], 'file_commit': m[2], 'size': int(m[3]), 'sha256': m[4]}
    except (OSError, subprocess.CalledProcessError, LookupError) as exc:
        c.error('S039 row parse', f'{type(exc).__name__}: {exc}')
    facts['S038'] = s038
    facts['S039'] = s039

    receipt = None
    try:
        with open(args.receipt, 'rb') as fh:
            raw = fh.read()
        facts['receipt_sha256'] = hashlib.sha256(raw).hexdigest()
        receipt = json.loads(raw)
        if not isinstance(receipt.get('server'), dict) or not isinstance(receipt.get('model'), dict):
            raise ValueError('receipt lacks server/model objects')
    except (OSError, ValueError) as exc:
        c.error('receipt read', f'{type(exc).__name__}: {exc}')
        receipt = None

    # S038 <-> archive bytes
    archive = None
    try:
        a_sha, a_size = sha256_path(args.archive)
        facts['archive_sha256'], facts['archive_size'] = a_sha, a_size
        if s038:
            c.compare('S038 asset name == archive basename', s038['asset'],
                      os.path.basename(args.archive))
            c.compare('S038 size == archive size', s038['size'], a_size)
            c.compare('S038 digest == archive sha256', s038['sha256'], a_sha)
        archive = archive_members(args.archive)
    except (OSError, tarfile.TarError, EOFError) as exc:
        c.error('archive read', f'{type(exc).__name__}: {exc}')

    # archive members <-> installed tree
    installed = None
    try:
        installed = installed_members(args.install_dir)
    except OSError as exc:
        c.error('install dir read', f'{type(exc).__name__}: {exc}')
    if archive is not None and installed is not None:
        only_a = sorted(set(archive) - set(installed))
        only_i = sorted(set(installed) - set(archive))
        differ = sorted(n for n in set(archive) & set(installed) if archive[n] != installed[n])
        facts['archive_member_count'] = len(archive)
        facts['archive_regular_count'] = sum(1 for v in archive.values() if v[0] == 'file')
        facts['archive_symlink_count'] = sum(1 for v in archive.values() if v[0] == 'link')
        c.compare('archive members only in archive', [], only_a)
        c.compare('installed entries not in archive', [], only_i)
        c.compare('members whose bytes/target differ', [], differ)

    # installed tree (tool rule) <-> receipt
    if installed is not None:
        tree = {n: v[1] for n, v in installed.items() if v[0] == 'file'}
        facts['installed_tree_count'] = len(tree)
        facts['installed_tree_sha256'] = tree_digest(tree)
        if archive is not None:
            a_tree = {n: v[1] for n, v in archive.items() if v[0] == 'file'}
            c.compare('archive-derived tree digest == installed tree digest',
                      tree_digest(a_tree), facts['installed_tree_sha256'])
        if receipt is not None:
            srv = receipt['server']
            r_tree = srv.get('install_tree')
            if isinstance(r_tree, dict):
                c.compare('receipt install_tree == installed tree', r_tree, tree)
            else:
                c.error('receipt install_tree', 'absent or not an object')
            c.compare('receipt install_tree_sha256 == installed tree digest',
                      srv.get('install_tree_sha256'), facts['installed_tree_sha256'])
            c.compare('receipt server.sha256 == installed llama-server',
                      srv.get('sha256'), tree.get('llama-server'))
            c.compare('receipt server_impl_sha256 == installed libllama-server-impl.so',
                      srv.get('server_impl_sha256'), tree.get('libllama-server-impl.so'))

    # S039 <-> model bytes <-> receipt
    try:
        m_sha, m_size = sha256_path(args.model)
        facts['model_sha256'], facts['model_size'] = m_sha, m_size
        if s039:
            c.compare('S039 size == model size', s039['size'], m_size)
            c.compare('S039 LFS sha256 == model sha256', s039['sha256'], m_sha)
        if receipt is not None:
            c.compare('receipt model.path == model path', receipt['model'].get('path'), args.model)
            c.compare('receipt model.sha256 == model sha256', receipt['model'].get('sha256'), m_sha)
            c.compare('receipt model_sha256_post == model sha256',
                      receipt.get('model_sha256_post'), m_sha)
    except OSError as exc:
        c.error('model read', f'{type(exc).__name__}: {exc}')

    code = c.exit_code()
    doc = {'schema': 'kama-freshness-s038-s039/v1', 'exit': code, 'facts': facts,
           'checks': c.rows}
    text = json.dumps(doc, indent=1, sort_keys=True) + '\n'
    if args.out:
        with open(args.out, 'x') as fh:
            fh.write(text)
    sys.stdout.write(text)
    for row in c.rows:
        print(f"{row['status']:8} {row['check']}", file=sys.stderr)
    return code


if __name__ == '__main__':
    sys.exit(main())
