#!/usr/bin/env python3
"""Scratch attack battery for lane producer install_links()/install_tree().

Writes only under /tmp/kama-r21-C2ProducerReview/exp/work. Prints one JSON object.
Each case records what the functions return; 'EXC ...' marks a raised exception.
"""
import contextlib
import errno
import importlib.util
import json
import os
import shutil
import socket
import tempfile

LANE = '/tmp/kama-r21-C2ProducerReview/lane/tools/kama-llamacpp-live.py'
OLD = '/tmp/kama-r21-C2ProducerReview/exp/old/kll_old.py'
WORK = '/tmp/kama-r21-C2ProducerReview/exp/work'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kll = load('kll_new', LANE)
old = load('kll_old', OLD)
os.makedirs(WORK, exist_ok=True)
results = {'uid': os.getuid()}


def cleanup(d):
    for dp, dn, _ in os.walk(d):
        for x in dn + ['.']:
            try:
                os.chmod(os.path.join(dp, x), 0o755)
            except OSError:
                pass
    shutil.rmtree(d, ignore_errors=True)


@contextlib.contextmanager
def tree():
    d = tempfile.mkdtemp(prefix='case-', dir=WORK)
    server = os.path.join(d, 'llama-server')
    with open(server, 'wb') as fh:
        fh.write(b'stub\n')
    os.chmod(server, 0o755)
    try:
        yield d, server
    finally:
        cleanup(d)


def write(path, body=b'x\n'):
    with open(path, 'wb') as fh:
        fh.write(body)


def pl(server):
    links, digest, problems = kll.install_links(server)
    return {'links': links, 'problems': problems}


def attempt(fn, *args):
    try:
        return fn(*args)
    except BaseException as exc:
        return f'EXC {type(exc).__name__}: {exc}'


def c_newline_regular():
    with tree() as (d, s):
        write(os.path.join(d, 'lib\nx.so'))
        return pl(s)


def c_tab_symlink():
    with tree() as (d, s):
        os.symlink('libllama.so.0.7.0', os.path.join(d, 'lib\tx.so'))
        return pl(s)


def c_del_regular():
    with tree() as (d, s):
        write(os.path.join(d, 'lib\x7fx.so'))
        return pl(s)


def c_nel_regular():
    with tree() as (d, s):
        write(os.path.join(d, 'lib\x85x.so'))
        return pl(s)


def c_nonutf8_regular():
    with tree() as (d, s):
        write(os.path.join(os.fsencode(d), b'lib\xffx.so'))
        return {'install_links': pl(s), 'install_tree': attempt(kll.install_tree, s)}


def c_nonutf8_symlink():
    with tree() as (d, s):
        os.symlink('libllama.so.0.7.0', os.path.join(os.fsencode(d), b'lib\xff.so'))
        return {'install_links': pl(s), 'install_tree': attempt(kll.install_tree, s)}


def c_fifo():
    with tree() as (d, s):
        os.mkfifo(os.path.join(d, 'pipe0'))
        return {'install_links': pl(s), 'install_tree': attempt(kll.install_tree, s)}


def c_unix_socket():
    with tree() as (d, s):
        sk = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sk.bind(os.path.join(d, 'sock0'))
            return pl(s)
        finally:
            sk.close()


def c_dangling():
    with tree() as (d, s):
        os.symlink('libgone.so.1', os.path.join(d, 'libgone.so'))
        return pl(s)


def c_subdir_hwcaps():
    with tree() as (d, s):
        os.makedirs(os.path.join(d, 'glibc-hwcaps', 'x86-64-v3'))
        return {'new_install_links': pl(s),
                'old_install_tree_names': sorted(old.install_tree(s)[0])}


def c_hwcaps_symlink_outside():
    with tree() as (d, s):
        os.symlink('/usr/lib', os.path.join(d, 'glibc-hwcaps'))
        return pl(s)


def c_listdir_denied():
    with tree() as (d, s):
        os.chmod(d, 0)
        try:
            return pl(s)
        finally:
            os.chmod(d, 0o755)


def c_unreadable_member():
    with tree() as (d, s):
        lib = os.path.join(d, 'libllama.so.0.7.0')
        write(lib)
        os.chmod(lib, 0)
        return pl(s)


def c_ghost_listing():
    with tree() as (d, s):
        real = os.listdir
        os.listdir = lambda p: sorted(real(p)) + ['ghost.so.0']
        try:
            return pl(s)
        finally:
            os.listdir = real


def c_lstat_vanished():
    with tree() as (d, s):
        os.symlink('libllama.so.0.7.0', os.path.join(d, 'libllama.so.0'))
        real = os.lstat

        def fake(p, *a, **k):
            if os.path.basename(p) == 'libllama.so.0':
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), p)
            return real(p, *a, **k)
        os.lstat = fake
        try:
            return pl(s)
        finally:
            os.lstat = real


def c_readlink_einval():
    with tree() as (d, s):
        os.symlink('libllama.so.0.7.0', os.path.join(d, 'libllama.so'))
        real = os.readlink

        def fake(p, *a, **k):
            if os.path.basename(p) == 'libllama.so':
                raise OSError(errno.EINVAL, os.strerror(errno.EINVAL), p)
            return real(p, *a, **k)
        os.readlink = fake
        try:
            return pl(s)
        finally:
            os.readlink = real


def _drop_case(mode):
    """A regular member that install_tree() cannot hash, in one of three ways."""
    with tree() as (d, s):
        extra = os.path.join(d, 'libextra.so')
        write(extra, b'extra\n')
        full_names = sorted(kll.install_tree(s)[0])
        real_hash, real_access = kll.sha256_file, os.access

        def fake_hash(path):
            if os.path.basename(path) == 'libextra.so':
                if mode == 'unlink':
                    os.unlink(path)
                elif mode == 'eio':
                    raise OSError(errno.EIO, os.strerror(errno.EIO), path)
            return real_hash(path)

        def fake_access(p, m, *a, **k):
            if mode == 'access_lies' and os.path.basename(p) == 'libextra.so':
                return True
            return real_access(p, m, *a, **k)

        if mode == 'access_lies':
            os.chmod(extra, 0)
        kll.sha256_file = fake_hash
        os.access = fake_access
        try:
            tree_, sha = kll.install_tree(s)
            links = pl(s)
        finally:
            kll.sha256_file = real_hash
            os.access = real_access
        return {'full_tree_names': full_names,
                'recorded_tree_names': sorted(tree_),
                'install_tree_sha256': sha,
                'install_links': links}


def c_silent_drop_eio():
    return _drop_case('eio')


def c_silent_drop_unlink_race():
    return _drop_case('unlink')


def c_silent_drop_access_lies():
    return _drop_case('access_lies')


def c_selftest_unreadable_branch():
    calls = []
    real = kll.install_links

    def rec(server):
        r = real(server)
        calls.append(list(r[2]))
        return r
    kll.install_links = rec
    try:
        kll._install_identity_selftest()
        status = 'returned-ok'
    except BaseException as exc:
        status = f'EXC {type(exc).__name__}: {exc}'
    finally:
        kll.install_links = real
    return {'status': status,
            'install_links_problem_lists': calls,
            'unreadable_problem_seen': any('unreadable' in p
                                           for c in calls for p in c)}


def c_links_digest_surrogate():
    return kll.links_digest({'lib\udcffx.so': 'libllama.so.0.7.0'})


CASES = sorted((n, f) for n, f in list(globals().items()) if n.startswith('c_'))
for name, fn in CASES:
    try:
        results[name] = fn()
    except BaseException as exc:
        results[name] = f'EXC {type(exc).__name__}: {exc}'
print(json.dumps(results, indent=1, sort_keys=True, ensure_ascii=True))
