#!/usr/bin/env python3
"""Probe the os/stat semantics that install_links() relies on, on the host Python.

Mirrors tools/kama-llamacpp-live.py install_links() (a29bb84, lines 211-226) and the
regular-only install_tree() digest (lines 182-202). Operates only inside a fresh
temporary directory under /tmp; nothing else is touched.
"""
import errno
import hashlib
import os
import stat
import sys
import tempfile


def links_digest(directory):
    links = {}
    for name in sorted(os.listdir(directory)):
        full = os.path.join(directory, name)
        try:
            if stat.S_ISLNK(os.lstat(full).st_mode):
                links[name] = os.readlink(full)
        except OSError:
            continue
    combined = hashlib.sha256(
        ''.join(f'{n} -> {links[n]}\n' for n in sorted(links)).encode()).hexdigest()
    return links, combined


def regular_digest(directory):
    tree = {}
    for name in sorted(os.listdir(directory)):
        full = os.path.join(directory, name)
        try:
            if not stat.S_ISREG(os.lstat(full).st_mode):
                continue
        except OSError:
            continue
        with open(full, 'rb') as fh:
            tree[name] = hashlib.sha256(fh.read()).hexdigest()
    return hashlib.sha256(
        ''.join(f'{n} {tree[n]}\n' for n in sorted(tree)).encode()).hexdigest()


print('python', sys.version.split()[0], 'platform', sys.platform, 'os.name', os.name)
with tempfile.TemporaryDirectory(prefix='kama-r21-probe-') as d:
    names = ['zeta', 'alpha', 'mid', 'beta', 'omega', 'libllama.so.0.0.0', 'libllama.so.0.0.1']
    for n in names:
        with open(os.path.join(d, n), 'w') as fh:
            fh.write('payload ' + n + '\n')
    raw = os.listdir(d)
    print('listdir_raw_order', raw)
    print('listdir_equals_sorted', raw == sorted(raw))
    soname = os.path.join(d, 'libllama.so.0')
    os.symlink('libllama.so.0.0.0', soname)
    os.symlink(os.path.join(d, 'alpha'), os.path.join(d, 'abs-link'))
    print('readlink_relative', os.readlink(soname))
    print('readlink_absolute_is_abs', os.path.isabs(os.readlink(os.path.join(d, 'abs-link'))))
    print('lstat_S_ISLNK', bool(stat.S_ISLNK(os.lstat(soname).st_mode)))
    print('stat_follows_S_ISREG', bool(stat.S_ISREG(os.stat(soname).st_mode)))
    try:
        os.readlink(os.path.join(d, 'alpha'))
        print('readlink_regular_file', 'no error')
    except OSError as e:
        print('readlink_regular_file_errno', e.errno, errno.errorcode.get(e.errno))
    before_links, before_links_sha = links_digest(d)
    before_regular = regular_digest(d)
    os.remove(soname)
    os.symlink('libllama.so.0.0.1', soname)
    after_links, after_links_sha = links_digest(d)
    after_regular = regular_digest(d)
    print('links_before', before_links)
    print('links_after', after_links)
    print('links_digest_changed', before_links_sha != after_links_sha)
    print('regular_digest_changed', before_regular != after_regular)
print('probe_done')
