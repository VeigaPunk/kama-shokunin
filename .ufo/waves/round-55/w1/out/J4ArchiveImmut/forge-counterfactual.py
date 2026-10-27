#!/usr/bin/env python3
"""J4ArchiveImmut forge counterfactual (round-55, lane kama).

The live attack left a FORGED archive at the counter's own reference path while
the counter was running, with attacker bytes in llama-b11909/libggml-base.so.0.27.0,
and the counter still reported met=True with code=1 over 16 byte-equal ranges.
That is only decisive if a reference that DID consult the file would have seen the
attacker bytes.  This probe shows the two tamper SHAPES against the frozen class
and against the pre-fix class:

  (A) IN-PLACE overwrite of the same inode (the Sen1Mem F1 shape) - the fixture is
      > 256 KiB with the target member first, because CPython's buffered tarfile
      reader serves small archives from its 8 KiB window and would mask the shape.
  (B) rename the reference aside + forged archive at the path (new inode).

Readers:
  (1) the FROZEN Archive - round-54, reads the file once into io.BytesIO
  (2) the round-53 Archive - tarfile.open(path), member bytes read lazily from the
      fd; reconstructed verbatim from .ufo/waves/round-53/w1/out/Sen1Mem/
      c1-reference-immutability.diff
  (3) a re-read - Archive(path) again after the tamper: the only laundering shape,
      which the frozen counter never performs (apath: lines 915/918/920 only).
"""
import hashlib
import importlib.util
import io
import os
import shutil
import sys
import tarfile
import tempfile

COUNTER = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-replay-code-audit.py"
TARGET = "a/libggml-base.so"
RELEASE = b"REAL-RELEASE-MEMBER-BYTES"
ATTACK = b"!!ATTACKER-MEMBER-BYTES!!"          # same length: offsets stay aligned
FILLER = bytes(range(256)) * 1024              # 256 KiB, keeps the member out of the read buffer


def load_counter():
    spec = importlib.util.spec_from_file_location("c1_frozen", COUNTER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Archive53:
    """The pre-fix class, verbatim from Sen1Mem's round-53 diff."""

    def __init__(self, path):
        self.tf = tarfile.open(path)
        self.cache = {}

    def member(self, name):
        if name not in self.cache:
            try:
                ti = self.tf.getmember(name)
            except KeyError:
                self.cache[name] = None
            else:
                self.cache[name] = self.tf.extractfile(ti).read() if ti.isreg() else None
        return self.cache[name]


def make_tar(path, member_bytes):
    with tarfile.open(path, "w") as tf:
        for name, data in ((TARGET, member_bytes), ("a/filler.bin", FILLER)):
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            tf.addfile(ti, io.BytesIO(data))
    return path


def inplace_forge(path, member_bytes):
    tmp = path + ".new"
    make_tar(tmp, member_bytes)
    blob = open(tmp, "rb").read()
    os.unlink(tmp)
    ino0 = os.stat(path).st_ino
    with open(path, "r+b") as fh:
        fh.seek(0)
        fh.write(blob)
        fh.truncate()
    return ino0, os.stat(path).st_ino, hashlib.sha256(blob).hexdigest()


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "-"
    m = load_counter()
    lines = []

    def p(s="", *a):
        s = s % a if a else s
        print(s)
        lines.append(s)

    d = tempfile.mkdtemp(prefix="j4-forge-", dir=os.environ.get("TMPDIR", "/tmp"))
    p("frozen counter           %s", COUNTER)
    p("frozen counter sha256    %s",
      hashlib.sha256(open(COUNTER, "rb").read()).hexdigest())
    p("tamper member            %s (%d bytes)", TARGET, len(RELEASE))

    # ---------------------------------------------------------------- (A)
    pa = os.path.join(d, "reference-a.tar")
    make_tar(pa, RELEASE)
    arc_a = m.Archive(pa)                     # the frozen reference, read once
    old_a = Archive53(pa)                     # the pre-fix reference, held by fd
    release_digest = hashlib.sha256(open(pa, "rb").read()).hexdigest()
    p()
    p("--- (A) IN-PLACE overwrite of the same inode (Sen1Mem F1 shape) ---")
    p("fixture                  %s bytes", os.path.getsize(pa))
    p("frozen member(before)    %r", arc_a.member(TARGET))
    p("round-53 member(before)  %r (a different member, so %s stays uncached)",
      old_a.member("a/filler.bin")[:8], TARGET)
    ino0, ino1, forged = inplace_forge(pa, ATTACK)
    p("inode before/after       %s / %s   same inode: %s", ino0, ino1, ino0 == ino1)
    p("file sha256 now          %s...  differs from release: %s  (release %s...)",
      forged[:16], forged != release_digest, release_digest[:16])
    f_a = arc_a.member(TARGET)
    o_a = old_a.member(TARGET)
    p("(1) frozen member(after) %r   attacker bytes? %s", f_a, f_a == ATTACK)
    p("    frozen sha256(blob) == release digest: %s",
      hashlib.sha256(arc_a.blob).hexdigest() == release_digest)
    p("(2) round-53 member(after) %r   attacker bytes? %s", o_a, o_a == ATTACK)
    p("    => pre-fix, the same in-place overwrite hands the counter the ATTACKER bytes")
    p("       (Sen1Mem F1); the frozen class still returns the RELEASE bytes and its")
    p("       digest is still the release digest.")

    # ---------------------------------------------------------------- (B)
    pb = os.path.join(d, "reference-b.tar")
    make_tar(pb, RELEASE)
    arc_b = m.Archive(pb)
    old_b = Archive53(pb)
    os.rename(pb, pb + ".stolen")
    make_tar(pb, ATTACK)
    b1, b2 = arc_b.member(TARGET), old_b.member(TARGET)
    p()
    p("--- (B) rename the reference aside + forged archive at the path (new inode) ---")
    p("(1) frozen member        %r   attacker bytes? %s", b1, b1 == ATTACK)
    p("(2) round-53 member      %r   attacker bytes? %s", b2, b2 == ATTACK)
    p("    => a rename-over is inert for BOTH: the frozen class snapshotted the bytes,")
    p("       the pre-fix fd still points at the old inode. Only an in-place overwrite")
    p("       (A) ever changed what the pre-fix counter compared.")

    # ---------------------------------------------------------------- (3)
    naive = m.Archive(pb)
    n = naive.member(TARGET)
    p()
    p("(3) re-read Archive(path) after the tamper: %r   attacker bytes? %s", n, n == ATTACK)
    p("    => a post-replay re-read is the only shape that would launder the swap; the")
    p("       frozen counter never performs one: apath is used at lines 915, 918, 920.")
    p("       NOTE (pre-registration honesty): case (A) on a small archive does NOT")
    p("       reproduce the pre-fix exposure - CPython's buffered tarfile reader serves")
    p("       archives under its 8 KiB window from cache. The fixture above is 256 KiB.")

    shutil.rmtree(d, ignore_errors=True)
    text = "\n".join(lines) + "\n"
    if out != "-":
        with open(out, "w") as fh:
            fh.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
