#!/usr/bin/env python3
"""Build every crafted input once; both the round-48 (before) and round-49 (after)
verify_archive_member copies consume the identical files.

Nothing here imports lane code: it only produces archives with the stdlib.
"""
import gzip
import hashlib
import io
import json
import os
import struct
import sys
import tarfile

ART = sys.argv[1]
os.makedirs(ART, exist_ok=True)
MEMBER = "rel/llama-server"
GOOD = b"#!/bin/sh\necho fixture\n"
CHUNK = 16 << 20


def sha(b):
    return hashlib.sha256(b).hexdigest()


def p(name):
    return os.path.join(ART, name)


def digest(q):
    return sha(open(q, "rb").read())


def tar_gz(name, members):
    q = p(name)
    with tarfile.open(q, "w:gz") as tf:
        for s in members:
            ti = tarfile.TarInfo(s["name"])
            ti.type = s.get("type", tarfile.REGTYPE)
            ti.linkname = s.get("linkname", "")
            ti.mode = 0o755
            if ti.type == tarfile.REGTYPE:
                data = s.get("data", b"")
                ti.size = len(data)
                tf.addfile(ti, io.BytesIO(data))
            else:
                tf.addfile(ti)
    return q, digest(q)


def gnu_sparse_blob(real_size, stored=b"A"):
    """Old GNU 'S' header: realsize is the 12-byte octal field at 483."""
    buf = bytearray(512)
    struct.pack_into("100s", buf, 0, MEMBER.encode())
    struct.pack_into("8s", buf, 100, b"0000755\0")
    struct.pack_into("8s", buf, 108, b"0000000\0")
    struct.pack_into("8s", buf, 116, b"0000000\0")
    struct.pack_into("12s", buf, 124, ("%011o\0" % len(stored)).encode())
    struct.pack_into("12s", buf, 136, b"14000000000\0")
    struct.pack_into("8s", buf, 148, b"        ")
    buf[156:157] = b"S"
    buf[257:265] = b"ustar  \0"
    struct.pack_into("12s", buf, 386, b"00000000000\0")
    struct.pack_into("12s", buf, 398, b"%011o\0" % len(stored))
    buf[482] = 0
    struct.pack_into("12s", buf, 483, ("%011o\0" % real_size).encode())
    struct.pack_into("8s", buf, 148, ("%06o\0 " % sum(buf)).encode())
    return bytes(buf) + stored.ljust(512, b"\0") + b"\0" * 1024


def sparse_old(name, real_size):
    q = p(name)
    with open(q, "wb") as fh:
        fh.write(gzip.compress(gnu_sparse_blob(real_size), 9))
    return q, digest(q)


def sparse_pax(name, headers):
    q = p(name)
    with tarfile.open(q, "w:gz", format=tarfile.PAX_FORMAT) as tf:
        ti = tarfile.TarInfo(MEMBER)
        ti.size = 1
        ti.pax_headers = dict(headers)
        tf.addfile(ti, io.BytesIO(b"A"))
    return q, digest(q)


def many(name, count):
    q = p(name)
    with tarfile.open(q, "w:gz", compresslevel=1) as tf:
        for i in range(count):
            ti = tarfile.TarInfo(f"f/{i:08d}")
            ti.size = 0
            tf.addfile(ti)
    return q, digest(q)


def zeros_gz(name, total):
    """A gzip stream that decompresses to `total` zero bytes of tar index."""
    q = p(name)
    block = b"\0" * CHUNK
    with open(q, "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", compresslevel=1, mtime=0) as gz:
            for _ in range(total // CHUNK):
                gz.write(block)
    return q, digest(q)


def pax_size_bomb(name, declared, payload_bytes, staged_before=b""):
    """PAX member declaring `declared` bytes (decimal; beyond the 12-byte octal
    field), then `payload_bytes` of zeros so tarfile's skip must decompress all
    of it before it can raise."""
    q = p(name)
    tmp = p(name + ".inner.tar")
    with tarfile.open(tmp, "w", format=tarfile.PAX_FORMAT) as tf:
        tf.addfile(tarfile.TarInfo("f/000"), io.BytesIO(b""))      # a real member
        ti = tarfile.TarInfo(MEMBER)
        ti.size = 1
        ti.pax_headers = {"size": str(declared)}
        tf.addfile(ti, io.BytesIO(b"A"))
    inner = open(tmp, "rb").read()
    os.unlink(tmp)
    with open(q, "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", compresslevel=1, mtime=0) as gz:
            gz.write(staged_before + inner)
            block = b"\0" * CHUNK
            for _ in range(payload_bytes // CHUNK):
                gz.write(block)
    return q, digest(q)


def big_sparse_file(name, size):
    q = p(name)
    with open(q, "wb") as fh:
        fh.truncate(size)
    return q, digest(q)


out = {"memb": MEMBER, "good_sha": sha(GOOD), "good_size": len(GOOD)}
jobs = [
    ("regular", lambda: tar_gz("regular.tgz", [{"name": MEMBER, "data": GOOD}])),
    ("symlink", lambda: tar_gz("symlink.tgz", [{"name": MEMBER, "type": tarfile.SYMTYPE,
                                               "linkname": "/bin/sh"}])),
    ("dir", lambda: tar_gz("dir.tgz", [{"name": "rel", "type": tarfile.DIRTYPE}])),
    ("absent", lambda: tar_gz("absent.tgz", [{"name": "rel/other", "data": GOOD}])),
    ("dup_good_first", lambda: tar_gz("dup-good-then-decoy.tgz",
                                      [{"name": MEMBER, "data": GOOD},
                                       {"name": MEMBER, "data": b"decoy\n"}])),
    ("dup_decoy_first", lambda: tar_gz("dup-decoy-then-good.tgz",
                                       [{"name": MEMBER, "data": b"decoy\n"},
                                        {"name": MEMBER, "data": GOOD}])),
    ("gnu_old_1g", lambda: sparse_old("gnu-old-1g.tgz", 1 << 30)),
    ("gnu_old_8g", lambda: sparse_old("gnu-old-8g.tgz", 0o77777777777)),
    ("pax01_1e15", lambda: sparse_pax("pax-0.1-1e15.tgz",
                                      {"GNU.sparse.map": "0,1",
                                       "GNU.sparse.size": str(10 ** 15)})),
    ("pax10_1e15", lambda: sparse_pax("pax-1.0-1e15.tgz",
                                      {"GNU.sparse.map": "0,1",
                                       "GNU.sparse.major": "1",
                                       "GNU.sparse.minor": "0",
                                       "GNU.sparse.realsize": str(10 ** 15)})),
    ("many20k", lambda: many("many-20k.tgz", 20000)),
    ("zeros8g", lambda: zeros_gz("zeros-8g.tgz", 8 << 30)),
    ("paxsize_payload4g", lambda: pax_size_bomb("paxsize-1e15-payload4g.tgz",
                                                10 ** 15, 4 << 30)),
    ("archive_2g", lambda: big_sparse_file("archive-2g.bin", 2 << 30)),
]
for key, fn in jobs:
    q, d = fn()
    out[key] = [q, d, os.path.getsize(q)]
    print(key, out[key][2], d[:16], flush=True)

with open(os.path.join(ART, "artifacts.json"), "w") as fh:
    json.dump(out, fh, indent=1)
