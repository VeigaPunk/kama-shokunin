#!/usr/bin/env python3
"""Seat Sen1Mem probe 2: is the counter's "own download" a trustworthy reference?

The counter writes its download to <S>/counter-archive.tar.gz (round53-replay-code-audit.py:747),
hashes it once (:752), opens it by path (tarfile.open(path), :379) and then launches the replay
(:560 bind_one) whose environment sets TMPDIR=<S>/tmp-<tag> (:499). The replay therefore knows <S>
- the directory holding the reference - runs as the same uid, and can rewrite the file. The
member *table* is read at open (so names/offsets are frozen), but each member's *bytes* are read
from the file at member() time (ExFileObject seeks ti.offset_data on the still-open fd), so an
in-place rewrite that keeps the layout changes the reference the counter compares memory against.

The layout mirrors the release archive: libraries early, the multi-MB binary last (a member in
the final buffered block is served from the buffer, so the tampered member is placed where the
real libraries are).
"""
import importlib.util
import io
import os
import subprocess
import sys
import tarfile
import tempfile

sys.dont_write_bytecode = True
COUNTER = "/fast/scratch/hyaku/kama-r53/Sen1Mem/c1.py"
RELEASE = b"RELEASE-ARCHIVE-BYTES " * 256
SWAPPED = b"ATTACKER-SWAPPED-BYTES" * 256
MEMBER = "llama-b11909/libggml-base.so.0.27.0"
LAYOUT = (("llama-b11909/pad0.bin", b"P" * (1 << 20)),
          (MEMBER, RELEASE),
          ("llama-b11909/llama-server", b"T" * (1 << 20)))


def load_counter():
    spec = importlib.util.spec_from_file_location("c1", COUNTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_tar(path, member_bytes):
    with tarfile.open(path, "w") as tf:
        for name, data in LAYOUT:
            data = member_bytes if name == MEMBER else data
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            tf.addfile(ti, io.BytesIO(data))


def main():
    c1 = load_counter()
    S = tempfile.mkdtemp(prefix="sen1mem-ref-", dir=os.environ.get("TMPDIR", "/tmp"))
    apath = os.path.join(S, "counter-archive.tar.gz")      # the counter's own name, line 747
    make_tar(apath, RELEASE)
    frozen = c1.sha_file(apath)
    print(f"counter download            {apath}")
    print(f"frozen digest of download   {frozen[:16]}... (compared once, line 752)")
    arc = c1.Archive(apath)                                # line 755: arc = Archive(apath)
    print(f"Archive opened by path      tarfile.open(path) line 379; member table loaded at "
          f"open: {arc.tf._loaded}; member bytes are read from the fd")

    env, canary, marker = c1.prepare_env(S, "b1")          # line 496: the replay's environment
    print(f"replay TMPDIR               {env['TMPDIR']}")
    print(f"-> dirname(TMPDIR) is S     {os.path.dirname(env['TMPDIR']) == S}; the reference sits "
          f"in it: {os.path.join(S, 'counter-archive.tar.gz')}")
    print(f"-> same uid as the counter  uid {os.getuid()}; file mode "
          f"{oct(os.stat(apath).st_mode & 0o777)}; S mode {oct(os.stat(S).st_mode & 0o777)}")

    # what the launched replay can do before the counter's first member() read: the payload
    # archive has the same layout (same names, sizes, offsets) and different library bytes
    swapped_tar = os.path.join(S, "swapped.tar")
    make_tar(swapped_tar, SWAPPED)
    p = subprocess.run([sys.executable, "-c",
                        "import shutil,sys;shutil.copyfile(sys.argv[1],sys.argv[2]);"
                        "print('rewrote (same layout, same uid)', sys.argv[2])",
                        swapped_tar, apath], capture_output=True, text=True)
    print(f"replay-like child           {p.stdout.strip() or p.stderr.strip()} rc={p.returncode}")

    after = c1.sha_file(apath)
    got = arc.member(MEMBER)
    print(f"digest after the rewrite    {after[:16]}...  equals the frozen digest: {after == frozen}")
    print(f"arc.member({MEMBER!r}) -> {got[:24].decode()!r}  RELEASE? {got == RELEASE}  "
          f"SWAPPED? {got == SWAPPED}")
    print("=> code_observe compares /proc/<pid>/mem against `want = arc.member(member)` (line 424)")
    print("   and bind_one hashes the same arc for the receipt and own_code digests (lines 636-640):")
    print("   the independent reference is whatever the audited process last wrote to that file.")
    print(f"cached members after this read {sorted(arc.cache)}; the cache is populated on the first")
    print("   read (inside replay 1), so a tamper before that read covers all three replays.")


if __name__ == "__main__":
    main()
