#!/usr/bin/env python3
"""Crafted-input harness for verify_archive_member (kama-llamacpp-live.py:193).

Every case builds an archive in this scratch dir, then calls the REAL function
imported from a byte copy of the lane tool, so the measurements are of lane code.
"""
import gzip
import hashlib
import importlib.util
import io
import json
import os
import resource
import struct
import sys
import tarfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
LIVE = os.path.join(HERE, "kama-llamacpp-live.py")

spec = importlib.util.spec_from_file_location("kl", LIVE)
kl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kl)

WORK = os.path.join(HERE, "arc")
os.makedirs(WORK, exist_ok=True)
MEMBER = "rel/llama-server"
GOOD = b"#!/bin/sh\necho fixture\n"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def path(name):
    return os.path.join(WORK, name)


def tar_gz(name, members):
    """members: list of TarInfo-ish dicts -> produced with tarfile (no hand bytes)."""
    p = path(name)
    with tarfile.open(p, "w:gz") as tf:
        for spec_ in members:
            ti = tarfile.TarInfo(spec_["name"])
            ti.type = spec_.get("type", tarfile.REGTYPE)
            ti.linkname = spec_.get("linkname", "")
            ti.mode = spec_.get("mode", 0o755)
            if spec_.get("type", tarfile.REGTYPE) == tarfile.REGTYPE:
                data = spec_.get("data", b"")
                ti.size = len(data)
                tf.addfile(ti, io.BytesIO(data))
            else:
                tf.addfile(ti)
    return p, sha(open(p, "rb").read())


def run(label, archive, asset_sha, member, server_sha, limit=None):
    t0 = time.monotonic()
    try:
        got = kl.verify_archive_member(archive, asset_sha, member, server_sha)
        out = {"ok": True, "result": got}
    except kl.SetupError as exc:
        out = {"setup_error": exc.code}
    except BaseException as exc:  # noqa: BLE001 - we want to see every escape
        out = {"uncaught": f"{type(exc).__name__}: {exc}"}
    # NB: ru_maxrss is inherited from the pre-exec parent in this environment
    # (6.4 GB baseline), so it is not reported; use tracemalloc/VmHWM instead.
    out.update(label=label, seconds=round(time.monotonic() - t0, 3),
               size=os.path.getsize(archive) if os.path.exists(archive) else None)
    print(json.dumps(out), flush=True)
    return out


def gnu_sparse_blob(real_size, stored=b"A"):
    """Old GNU 'S' header (TarInfo._frombuf offsets 386..495) + one data block."""
    buf = bytearray(512)
    struct.pack_into("100s", buf, 0, MEMBER.encode())
    struct.pack_into("8s", buf, 100, b"0000755\0")
    struct.pack_into("8s", buf, 108, b"0000000\0")
    struct.pack_into("8s", buf, 116, b"0000000\0")
    struct.pack_into("12s", buf, 124, ("%011o\0" % len(stored)).encode())
    struct.pack_into("12s", buf, 136, b"14000000000\0")
    struct.pack_into("8s", buf, 148, b"        ")
    buf[156:157] = b"S"                       # GNUTYPE_SPARSE
    struct.pack_into("100s", buf, 157, b"")
    buf[257:265] = b"ustar  \0"               # GNU_MAGIC
    # one sparse entry: offset 0, numbytes 1 -> the rest is a hole
    struct.pack_into("12s", buf, 386, b"00000000000\0")
    struct.pack_into("12s", buf, 398, b"%011o\0" % len(stored))
    buf[482] = 0                              # isextended
    struct.pack_into("12s", buf, 483, ("%011o\0" % real_size).encode())
    chk = sum(buf)                              # checksum with spaces in place
    struct.pack_into("8s", buf, 148, ("%06o\0 " % chk).encode())
    body = bytes(buf) + stored.ljust(512, b"\0") + b"\0" * 1024
    return body


def sparse_archive(name, real_size):
    p = path(name)
    with open(p, "wb") as fh:
        fh.write(gzip.compress(gnu_sparse_blob(real_size), 9))
    return p, sha(open(p, "rb").read())


def many_members(name, count):
    p = path(name)
    with tarfile.open(p, "w:gz", compresslevel=1) as tf:
        for i in range(count):
            ti = tarfile.TarInfo(f"f/{i:08d}")
            ti.size = 0
            tf.addfile(ti)
    return p, sha(open(p, "rb").read())


def big_member(name, mib):
    p = path(name)
    chunk = b"\0" * (1 << 20)
    with tarfile.open(p, "w:gz", compresslevel=1) as tf:
        ti = tarfile.TarInfo(MEMBER)
        ti.size = mib << 20
        tf.addfile(ti, io.BytesIO(chunk * mib))  # in-memory: mib MiB
    return p, sha(open(p, "rb").read())


if __name__ == "__main__":
    case = sys.argv[1]
    if case == "regular":
        a, s = tar_gz("regular.tgz", [{"name": MEMBER, "data": GOOD}])
        run("regular-ok", a, s, MEMBER, sha(GOOD))
        run("regular-wrong-server-digest", a, s, MEMBER, sha(b"other"))
    elif case == "types":
        for tname, ti in (
            ("symlink", {"name": MEMBER, "type": tarfile.SYMTYPE, "linkname": "/bin/sh"}),
            ("hardlink", {"name": MEMBER, "type": tarfile.LNKTYPE, "linkname": "rel/other"}),
            ("dir", {"name": MEMBER, "type": tarfile.DIRTYPE}),
            ("chrdev", {"name": MEMBER, "type": tarfile.CHRTYPE}),
            ("blockdev", {"name": MEMBER, "type": tarfile.BLKTYPE}),
            ("fifo", {"name": MEMBER, "type": tarfile.FIFOTYPE}),
            ("contiguous", {"name": MEMBER, "type": tarfile.CONTTYPE, "data": GOOD}),
        ):
            a, s = tar_gz(f"{tname}.tgz", [ti])
            run(f"member-{tname}", a, s, MEMBER, sha(GOOD))
        a, s = tar_gz("absent.tgz", [{"name": "rel/other", "data": GOOD}])
        run("member-absent", a, s, MEMBER, sha(GOOD))
        a, s = tar_gz("two.tgz", [{"name": MEMBER, "data": GOOD},
                                  {"name": MEMBER, "data": b"decoy\n"}])
        run("duplicate-name-first-is-good", a, s, MEMBER, sha(GOOD))
        run("duplicate-name-first-is-decoy", a, s, MEMBER, sha(b"decoy\n"))
    elif case == "archive-level":
        a, s = tar_gz("epoch.tgz", [{"name": MEMBER, "data": GOOD}])
        run("asset-digest-mismatch", a, "0" * 64, MEMBER, sha(GOOD))
        open(path("not-a-tar.tgz"), "wb").write(b"x" * 4096)
        run("not-an-archive", path("not-a-tar.tgz"), sha(b"x" * 4096), MEMBER, sha(GOOD))
        run("missing-archive", path("nope.tgz"), "0" * 64, MEMBER, sha(GOOD))
        run("archive-is-dir", WORK, "0" * 64, MEMBER, sha(GOOD))
        # truncated member payload: header claims 4096 bytes, archive stops
        blob = gzip.decompress(open(a, "rb").read())
        cut = path("truncated.tgz")
        open(cut, "wb").write(gzip.compress(blob[:512 + 100], 9))
        run("truncated-member", cut, sha(open(cut, "rb").read()), MEMBER, sha(GOOD))
    elif case == "sparse":
        for real in (1 << 30, 1 << 40, 1 << 50):
            a, s = sparse_archive(f"sparse-{real}.tgz", real)
            run(f"gnu-sparse-declared-{real}", a, s, MEMBER, sha(b"A"))
    elif case == "big":
        a, s = big_member("big-64m.tgz", 64)
        run("regular-member-64MiB", a, s, MEMBER, sha(b"\0" * (64 << 20)))
    elif case == "many":
        a, s = many_members("many.tgz", 300000)
        run("300k-empty-members", a, s, MEMBER, sha(GOOD))
