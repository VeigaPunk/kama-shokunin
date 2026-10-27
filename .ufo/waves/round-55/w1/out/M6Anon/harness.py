#!/usr/bin/env python3
"""Unit harness for the round-55 C1 anon-leg mutation probes (seat M6Anon).

Imports each mutant (and the pristine counter) by path with importlib, feeds
code_observe a hand-written /proc/<pid>/maps fixture, and records which rows it
flags. The maps file is faked through a module-level `open` shadow; the
/proc/<pid>/mem fd is a real memfd_create fd returned by a FakeOs shim, and
os.pread is served from a byte map so archive rows compare equal.

Fixture rows:
  00400000..00403000  r-xp  archive members under /fx/tree (bytes match arc)
  00500000            r-xp  /usr/lib/libc.so.6 (root-owned host lib, in HOST_LIBS)
  7f0000000000        r-xp  /memfd:llama-server (deleted)  == own (sealed image)
  7f0000100000        rwxp  anonymous executable page, no pathname (K1Cheat row)
  7f0000200000        r-xp  /memfd:foreign (deleted) != own (foreign exec memfd)
  7f0000300000        r-xp  [jitbuf] made-up bracket name
  7f0000400000        rw-p  anonymous NON-executable page, no pathname
  7ffffffde000        r-xp  [vdso] real kernel mapping
"""
import importlib.util
import io
import os
import re
import sys

PID = 424242
TREE = "/fx/tree"
LIBC = "/usr/lib/libc.so.6"
LIBC_INO = str(os.stat(LIBC).st_ino)
OWN = ("00:2b", "9999")  # (dev, inode) of the sealed image, as sealed_exe returns

MEMBERS = {
    "llama-b11909/libllama-server-impl.so": b"S" * 0x1000,
    "llama-b11909/libggml-base.so":         b"B" * 0x1000,
    "llama-b11909/libggml.so":              b"G" * 0x1000,
    "llama-b11909/libggml-cpu-haswell.so":  b"C" * 0x1000,
}
LO = {"llama-b11909/libllama-server-impl.so": 0x400000,
      "llama-b11909/libggml-base.so":         0x401000,
      "llama-b11909/libggml.so":              0x402000,
      "llama-b11909/libggml-cpu-haswell.so":  0x403000}
MEMREAD = {lo: data for m, (lo, data) in
           ((m, (LO[m], MEMBERS[m])) for m in MEMBERS)}

MAPS = "\n".join([
    "00400000-00401000 r-xp 00000000 08:01 111111 /fx/tree/llama-b11909/libllama-server-impl.so",
    "00401000-00402000 r-xp 00000000 08:01 222222 /fx/tree/llama-b11909/libggml-base.so",
    "00402000-00403000 r-xp 00000000 08:01 333333 /fx/tree/llama-b11909/libggml.so",
    "00403000-00404000 r-xp 00000000 08:01 444444 /fx/tree/llama-b11909/libggml-cpu-haswell.so",
    f"00500000-00521000 r-xp 00000000 00:20 {LIBC_INO} /usr/lib/libc.so.6",
    "7f0000000000-7f0000008000 r-xp 00000000 00:2b 9999 /memfd:llama-server (deleted)",
    "7f0000100000-7f0000108000 rwxp 00000000 00:00 0",
    "7f0000200000-7f000028000 r-xp 00000000 00:2a 4242 /memfd:foreign (deleted)",
    "7f0000300000-7f000030800 r-xp 00000000 00:00 0 [jitbuf]",
    "7f0000400000-7f000041000 rw-p 00000000 00:00 0",
    "7ffffffde000-7ffffffff000 r-xp 00000000 00:00 0 [vdso]",
    "",
])


class FakeArc:
    """archive.member(name) -> bytes, like the counter's Archive (members cached)."""
    def member(self, name):
        return MEMBERS.get(name)


class FakeOs:
    """os shim: a real memfd fd for /proc/<pid>/mem; pread served from MEMREAD."""
    def __init__(self):
        self.mem_fd = os.memfd_create("fx-mem")  # a real anonymous memfd
    def open(self, path, flags, *a, **k):
        if str(path) == f"/proc/{PID}/mem":
            return self.mem_fd
        return os.open(path, flags, *a, **k)
    def pread(self, fd, n, off):
        return MEMREAD.get(off, b"\x00" * n)[:n]
    def __getattr__(self, name):
        return getattr(os, name)


def load_mod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(path):
    mod = load_mod(path, "counter_under_test")
    mod.open = lambda p, *a, **k: (io.StringIO(MAPS) if str(p) == f"/proc/{PID}/maps"
                                   else open(p, *a, **k))
    mod.os = FakeOs()
    probs = []
    out = mod.code_observe(PID, TREE, FakeArc(), probs, collect=True, own=OWN)
    mod.os = os  # drop shim (fd already closed by code_observe's finally)
    return probs, out


def flagged(probs):
    """{row_range: problem_text} for classification problems only."""
    out = {}
    for p in probs:
        m = re.match(r"code: anonymous executable mapping (\S+) (\S+)", p)
        if m:
            out[m.group(1)] = p
            continue
        m = re.match(r"code: executable memfd .* \((\S+ \S+)\) is not the sealed image", p)
        if m:
            out[f"memfd:{m.group(1)}"] = p
            continue
        out[f"?{len(out)}"] = p
    return out


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "."
    mods = [("pristine", f"{base}/mut/pristine.py"),
            ("m1-anon-append", f"{base}/mut/m1-anon-append.py"),
            ("m2-memfd-name", f"{base}/mut/m2-memfd-name.py"),
            ("m3-kernel-maps", f"{base}/mut/m3-kernel-maps.py"),
            ("m4-xperm", f"{base}/mut/m4-xperm.py"),
            ("m5-nopath-skip", f"{base}/mut/m5-nopath-skip.py")]
    results = {}
    for name, path in mods:
        probs, out = run(path)
        results[name] = (probs, out)
        print(f"=== {name} ===")
        print(f"out: files={len(out['files'])} host={out['host']} ranges={out['ranges']} snaps={len(out['snaps'])}")
        for p in probs:
            print(f"  P {p}")
        if not probs:
            print("  (no problems)")
    pri = flagged(results["pristine"][0])
    need = ["7f0000100000-7f0000108000", "memfd:00:2a 4242", "7f0000300000-7f000030800"]
    assert all(k in pri for k in need), f"pristine failed to flag {set(need) - set(pri)}"
    assert not any("7f0000400000" in p for p in results["pristine"][0]), "pristine flagged the rw-p row"
    print("=== verdicts (unit detector) ===")
    for name, _ in mods[1:]:
        got = flagged(results[name][0])
        killed = got != pri
        print(f"{name}: {'KILLED' if killed else 'SURVIVED'}")
        for k in sorted(set(pri) - set(got)):
            print(f"   lost flag: {pri[k]}")
        for k in sorted(set(got) - set(pri)):
            print(f"   new flag: {got[k]}")
        if not killed:
            print("   (mutant produced identical classification)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
