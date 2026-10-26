#!/usr/bin/env python3
"""Proposed replacement for verify_archive_member (kama-llamacpp-live.py:193-219).

Run against the same crafted matrix as probe_archive.py to show the caps close
the bomb/hang/TOCTOU cases without weakening the seven type refusals.
"""
import hashlib
import importlib.util
import os
import stat
import sys
import tarfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import probe_archive as P  # noqa: E402  (reuses the crafted archives)


class SetupError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


ARCHIVE_MAX_BYTES = 1 << 30      # release assets are ~70 MB; 1 GiB is already generous
MEMBER_MAX_BYTES = 1 << 30       # the member is the server binary
MEMBER_MAX_COUNT = 4096          # index entries; the real archive has ~40


def verify_archive_member(archive, asset_sha256, member, server_sha256):
    try:
        st = os.stat(archive)
    except OSError:
        raise SetupError('provenance-archive-unreadable')
    if not stat.S_ISREG(st.st_mode):
        raise SetupError('provenance-archive-not-regular')
    if st.st_size > ARCHIVE_MAX_BYTES:
        raise SetupError('provenance-archive-too-large')
    try:
        arc = open(archive, 'rb')
    except OSError:
        raise SetupError('provenance-archive-unreadable')
    with arc:
        h_arc = hashlib.sha256()
        for chunk in iter(lambda: arc.read(1 << 20), b''):
            h_arc.update(chunk)
        archive_sha = h_arc.hexdigest()
        if archive_sha != asset_sha256:
            raise SetupError('provenance-archive-digest-mismatch')
        arc.seek(0)
        try:
            with tarfile.open(fileobj=arc, mode='r:*') as tf:
                found, count = None, 0
                for info in tf:                 # streaming: no full index in memory
                    count += 1
                    if count > MEMBER_MAX_COUNT:
                        raise SetupError('provenance-archive-too-many-members')
                    if info.name == member:
                        found = info            # last occurrence wins = extraction order
                if found is None:
                    raise SetupError('provenance-member-absent')
                if not found.isfile() or found.sparse or found.size > MEMBER_MAX_BYTES:
                    raise SetupError('provenance-member-not-a-file')
                h = hashlib.sha256()
                fh = tf.extractfile(found)
                for chunk in iter(lambda: fh.read(1 << 20), b''):
                    h.update(chunk)
        except SetupError:
            raise
        except KeyError:
            raise SetupError('provenance-member-absent')
        except (OSError, tarfile.TarError):
            raise SetupError('provenance-archive-unreadable')
    if h.hexdigest() != server_sha256:
        raise SetupError('provenance-member-digest-mismatch')
    return archive_sha, h.hexdigest()


def run(label, archive, asset_sha, member, server_sha):
    t0 = time.monotonic()
    try:
        verify_archive_member(archive, asset_sha, member, server_sha)
    except SetupError as exc:
        print(f"{label:38s} refused {exc.code:38s} {time.monotonic()-t0:.3f}s")
    except BaseException as exc:  # noqa: BLE001
        print(f"{label:38s} UNCAUGHT {type(exc).__name__}: {exc}")
    else:
        print(f"{label:38s} ok{'':36s} {time.monotonic()-t0:.3f}s")


if __name__ == "__main__":
    a, s = P.tar_gz("p-regular.tgz", [{"name": P.MEMBER, "data": P.GOOD}])
    run("regular-ok", a, s, P.MEMBER, P.sha(P.GOOD))
    run("regular-wrong-server-digest", a, s, P.MEMBER, P.sha(b"other"))
    for tname, ti in (
        ("symlink", {"name": P.MEMBER, "type": tarfile.SYMTYPE, "linkname": "/bin/sh"}),
        ("hardlink", {"name": P.MEMBER, "type": tarfile.LNKTYPE, "linkname": "rel/o"}),
        ("dir", {"name": P.MEMBER, "type": tarfile.DIRTYPE}),
        ("chrdev", {"name": P.MEMBER, "type": tarfile.CHRTYPE}),
        ("fifo", {"name": P.MEMBER, "type": tarfile.FIFOTYPE}),
    ):
        x, xs = P.tar_gz(f"p-{tname}.tgz", [ti])
        run(f"member-{tname}", x, xs, P.MEMBER, P.sha(P.GOOD))
    a2, s2 = P.tar_gz("p-dup.tgz", [{"name": P.MEMBER, "data": P.GOOD},
                                    {"name": P.MEMBER, "data": b"decoy\n"}])
    run("duplicate-last-wins", a2, s2, P.MEMBER, P.sha(b"decoy\n"))
    sa, ss = P.sparse_archive("p-sparse.tgz", 1 << 30)
    run("gnu-sparse-1GiB", sa, ss, P.MEMBER, P.sha(b"A"))
    na, ns = P.many_members("p-many.tgz", 20000)
    run("20k-members", na, ns, P.MEMBER, P.sha(P.GOOD))
    os.makedirs(os.path.join(HERE, "fifo2"), exist_ok=True)
    run("fifo-archive-path", os.path.join(HERE, "fifo2", "f"), "0" * 64, P.MEMBER, "0" * 64)
