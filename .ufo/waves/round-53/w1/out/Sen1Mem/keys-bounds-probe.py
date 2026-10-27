#!/usr/bin/env python3
"""Seat Sen1Mem probe 3: byte comparison false pass, member-name use, size bounds.

Part 1 the counter's own code_observe() on a child executing *swapped* libraries (files under
       the replay's unpacked tree, mapped PROT_READ|PROT_EXEC):
       1a the honest reference archive (release bytes) -> four "mapped bytes ... differ"
          problems -> code leg 0 (this is the wave's declared ablation control: a library
          swapped after its member check)
       1b the same archive object after an in-place rewrite that keeps the layout -> no
          problem -> code leg 1. The counter's independent reference moved with the tamper.
Part 2 member names are only keys: getmember() is an exact-name lookup; traversal names are
       not resolved, and extraction of the tip drops symlinks and refuses traversal.
Part 3 size bounds: a member shorter than the mapped file is zero-padded (the mapped tail is
       expected to be zeros, so it passes) and the range length taken from the maps row is
       allocated and read with no cap.
"""
import importlib.util
import io
import mmap
import os
import subprocess
import sys
import tarfile
import tempfile

sys.dont_write_bytecode = True
COUNTER = "/fast/scratch/hyaku/kama-r53/Sen1Mem/c1.py"
LIBS = ("libllama-server-impl.so", "libggml-base.so.0.27.0", "libggml.so.0.27.0",
        "libggml-cpu-zen4.so")
PAD = b"P" * (1 << 20)
TAIL = b"T" * (1 << 20)
BIG = "big-extra.so"


def load_counter():
    spec = importlib.util.spec_from_file_location("c1", COUNTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_tar(path, payloads):
    """payloads: {name: bytes}; layout = pad, the libraries, the extra member, tail."""
    with tarfile.open(path, "w") as tf:
        order = [("pad0.bin", PAD)] + [(n, payloads[n]) for n in LIBS if n in payloads] \
                + [(BIG, payloads[BIG])] + [("llama-server", TAIL)]
        for name, data in order:
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            tf.addfile(ti, io.BytesIO(data))


def vmsize(key="VmHWM"):
    for line in open("/proc/self/status"):
        if line.startswith(key):
            return line.strip()
    return "?"


CHILD = r"""
import mmap, sys, time
paths, length = sys.argv[1:-1], int(sys.argv[-1])
keep = []
for path in paths:
    fd = open(path, "rb")
    keep.append(mmap.mmap(fd.fileno(), length, flags=mmap.MAP_SHARED,
                          prot=mmap.PROT_READ | mmap.PROT_EXEC))
print("mapped", len(keep), flush=True)
time.sleep(60)
"""


def rows_of(pid):
    return [r for r in open(f"/proc/{pid}/maps").read().splitlines()
            if "x" in r.split()[1] and r.split(None, 5)[5].startswith("/")]


def main():
    c1 = load_counter()
    S = tempfile.mkdtemp(prefix="sen1mem-pass-", dir=os.environ.get("TMPDIR", "/tmp"))
    tree = os.path.join(S, "work-b1", "server")            # what bind_one hands code_observe
    os.makedirs(tree)
    release = {n: (b"R" + n.encode()) * 4096 for n in LIBS}
    swapped = {n: (b"S" + n.encode()) * 4096 for n in LIBS}
    for name, data in swapped.items():
        with open(os.path.join(tree, name), "wb") as fh:
            fh.write(data)
    apath = os.path.join(S, "counter-archive.tar.gz")
    payloads = dict(release)
    payloads[BIG] = b"B" * 4096
    make_tar(apath, payloads)
    arc_honest = c1.Archive(apath)     # a counter whose first member read precedes the tamper
    arc_after = c1.Archive(apath)      # the counter's real shape: Archive built at line 755,
                                       # first read deferred to code_observe inside replay 1

    print("== 1: the mem byte comparison, with the counter's own code_observe()")
    paths = [os.path.join(tree, n) for n in LIBS]
    child = subprocess.Popen([sys.executable, "-c", CHILD, *paths, str(4096)],
                             stdout=subprocess.PIPE, text=True)
    try:
        child.stdout.readline()
        rows = rows_of(child.pid)
        print(f"   child {child.pid}: {len(rows)} executable file mappings (the counter's filter)")
        probs = []
        cobs = c1.code_observe(child.pid, tree, arc_honest, probs)
        print(f"   1a honest archive            {cobs['ranges']} ranges compared, {len(probs)} problems")
        for pr in probs:
            print(f"      {pr}")
        print(f"      leg `not cprobs and cobs is not None` -> {not probs}  (code=0: control holds)")

        swapped[BIG] = payloads[BIG]
        make_tar(apath, swapped)                            # in-place, same layout, same uid
        probs = []
        cobs = c1.code_observe(child.pid, tree, arc_after, probs)  # the pre-tamper Archive object
        print(f"   1b archive rewritten to those bytes  {cobs['ranges']} ranges compared, "
              f"{len(probs)} problems: {probs}")
        print(f"      leg `not cprobs and cobs is not None` -> {not probs}  (code=1: FALSE PASS)")
        print("      files executed: " + ", ".join(f"{n} (sha {__import__('hashlib').sha256(swapped[n]).hexdigest()[:12]}...)" for n in LIBS))
    finally:
        child.kill()
        child.wait()

    print("== 2: member names are only keys")
    for name in ("../etc/passwd", "/etc/passwd", "libggml.so.0.27.0/../../x", ""):
        print(f"   Archive.member({name!r}) -> {arc_after.member(name)!r} (getmember exact match, line 384)")
    print("   extraction of the tip (git archive) drops symlinks/hardlinks and applies")
    print("   tarfile.data_filter (lines 776-779):")
    evil = os.path.join(S, "evil.tar")
    with tarfile.open(evil, "w") as tf:
        ti = tarfile.TarInfo("../../sen1mem-escaped")
        ti.size = 3
        tf.addfile(ti, io.BytesIO(b"abc"))
        sl = tarfile.TarInfo("link")
        sl.type = tarfile.SYMTYPE
        sl.linkname = "/etc/passwd"
        tf.addfile(sl)
    dest = os.path.join(S, "extract")
    os.makedirs(dest)
    try:
        with tarfile.open(evil) as tf:
            tf.extractall(dest, filter=lambda m, d: None if (m.issym() or m.islnk())
                          else tarfile.data_filter(m, d))
        print("   extractall -> no error (unexpected)")
    except Exception as exc:
        print(f"   extractall -> {type(exc).__name__}: {str(exc)[:110]}")
    print(f"   escaped file exists: {os.path.exists(os.path.join(S, 'sen1mem-escaped'))}; "
          f"symlink extracted: {os.path.lexists(os.path.join(dest, 'link'))}")

    print("== 3: size bounds")
    big = os.path.join(tree, BIG)
    with open(big, "wb") as fh:
        fh.write(b"B" * 4096)
        fh.truncate(256 << 20)                              # sparse: 4 KiB member, 256 MiB file
    before = vmsize()
    child = subprocess.Popen([sys.executable, "-c", CHILD, big, str(256 << 20)],
                             stdout=subprocess.PIPE, text=True)
    try:
        child.stdout.readline()
        row = [r for r in rows_of(child.pid) if BIG in r][0]
        hi_lo = int(row.split("-")[1].split()[0], 16) - int(row.split("-")[0], 16)
        probs = []
        cobs = c1.code_observe(child.pid, tree, arc_after, probs)
        print(f"   maps row {row.split()[0]} perms {row.split()[1]}: {hi_lo} bytes "
              f"({hi_lo >> 20} MiB), archive member {BIG!r} is 4096 bytes")
        print(f"   code_observe -> {cobs['ranges']} ranges, problems {probs}")
        print(f"   the whole range is held twice (want, line 424-425; got, line 427): the")
        print(f"   zero-padded tail compares equal, and nothing caps hi-lo")
    finally:
        child.kill()
        child.wait()
    print(f"   VmHWM {before.split()[1]} kB -> {vmsize().split()[1]} kB")


if __name__ == "__main__":
    main()
