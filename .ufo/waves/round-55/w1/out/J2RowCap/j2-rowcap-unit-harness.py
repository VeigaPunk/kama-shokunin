#!/usr/bin/env python3
"""J2RowCap - unit probe of the ROW_CAP leg of code_observe in the frozen round-55
C1 counter tools/round54-replay-code-audit.py.

Two clauses are probed (the counter's docstring, "Legs ... (iii) each maps row is read
at most 64 MiB, and a row whose range extends past its archive member's end is a
problem, not zero-padded"):

  CLAUSE-A (ROW_CAP)      a maps row longer than ROW_CAP (64 MiB) is never read from
                          /proc/<pid>/mem and is reported as a problem.
  CLAUSE-B (past member)  a maps row whose file range [off, off+length) extends past
                          the end of the archive member is reported as a problem, not
                          silently zero-padded and byte-compared.

The probe imports the frozen counter by path with importlib (the lane file is READ
only; it is never edited), shadows the module's `open` and `os` with a synthetic
/proc/<pid>/maps reader and a fake mem fd, and drives code_observe() directly with
synthetic maps rows.  The full counter is NOT run (no network, no llama-server).

Mutant copies of the counter are written to the scratch dir only; the lane file is
never modified.  The mutants exist to show the probe has teeth: with the guard
removed the same synthetic row is accepted (CLAUSE-B) or read without bound
(CLAUSE-A), so a passing probe cannot be an artefact of a vacuous harness.

Usage: python3 j2-rowcap-unit-harness.py [--counter PATH] [--receipt PATH]
Exit 0 iff every check passes.
"""
from __future__ import annotations

import argparse
import builtins
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
COUNTER = os.path.join(LANE, "tools", "round54-replay-code-audit.py")
PREREG_SHA = "c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af"
TREE = "/fake/unpacked"

REAL_OPEN = builtins.open
REAL_OS = os

RESULTS = []


def check(case, name, ok, detail):
    RESULTS.append({"case": case, "check": name, "ok": bool(ok), "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {case}: {name} :: {detail}")


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------- synthetic /proc
class FakeMem:
    """A fake /proc/<pid>/mem: regions of bytes; everything else reads as zeros
    (the kernel's behaviour for the zero-filled tail of a file's last page)."""

    def __init__(self):
        self.regions = []          # (start, bytes)
        self.calls = []            # (offset, length) of every pread
        self.opens = []
        self.closed = []
        self.fd = 4242

    def add(self, start, data):
        self.regions.append((start, data))

    def pread(self, length, offset):
        self.calls.append((offset, length))
        out = bytearray(b"\0" * length)
        for start, data in self.regions:
            s = max(start, offset)
            e = min(start + len(data), offset + length)
            if e > s:
                out[s - offset:e - offset] = data[s - start:e - start]
        return bytes(out)


class FakeOS:
    """Shadows the `os` module inside the counter: os.open("/proc/<pid>/mem")
    returns the fake mem fd, os.pread serves the fake memory, everything else is
    the real os."""

    def __init__(self, mem):
        self.__dict__["_real"] = REAL_OS
        self.__dict__["_mem"] = mem

    def __getattr__(self, name):
        return getattr(self.__dict__["_real"], name)

    def open(self, path, flags, *a, **kw):
        if str(path).endswith("/mem"):
            self.__dict__["_mem"].opens.append(str(path))
            return self.__dict__["_mem"].fd
        return self.__dict__["_real"].open(path, flags, *a, **kw)

    def pread(self, fd, length, offset):
        return self.__dict__["_mem"].pread(length, offset)

    def close(self, fd):
        self.__dict__["_mem"].closed.append(fd)


class FakeArchive:
    """The counter's Archive interface: member(name) -> bytes or None."""

    def __init__(self, members):
        self.members = members

    def member(self, name):
        return self.members.get(name)


def maps_open(rows):
    text = "".join(r + "\n" for r in rows)

    def _open(path, *a, **kw):
        if str(path).endswith("/maps"):
            return io.StringIO(text)
        return REAL_OPEN(path, *a, **kw)
    return _open


def row(lo, hi, off, path, perm="r-xp", dev="00:01", ino="1234"):
    return f"{lo:012x}-{hi:012x} {perm} {off:08x} {dev} {ino} {path}"


# --------------------------------------------------------------- the counter
def observe(mod, rows, members, mem, pid=4242):
    """Run code_observe() against synthetic maps rows and the fake mem fd."""
    probs = []
    mod.open = maps_open(rows)
    mod.os = FakeOS(mem)
    arc = FakeArchive(members)
    out = mod.code_observe(pid, TREE, arc, probs, collect=True)
    return probs, out


def code_problems(probs):
    return [p for p in probs if p.startswith("code:")]


def leg_code(probs, out):
    """The counter's own verdict for the code leg (bind_one: "code": not cprobs and
    cobs is not None)."""
    return (not code_problems(probs)) and out is not None


def required_members(size=0x2000):
    """Four synthetic members so the counter's REQUIRED check passes and the only
    problems in a scenario are the ones under test.  Each member is `size` bytes, so
    a one-page (0x1000) executable row at offset 0 lies inside the member."""
    return {
        "libllama-server-impl.so": bytes(range(256)) * (size // 256),
        "libggml-base.so.0.27.0": bytes(range(128)) * (size // 128),
        "libggml.so.0.27.0": bytes(range(64)) * (size // 64),
        "libggml-cpu-zen4.so": bytes(range(32)) * (size // 32),
    }


def build_rows_and_mem(members, extra_rows=(), extra_regions=()):
    """One good executable row per required member (bytes match the archive) plus
    the caller's extra rows/regions.  The good rows live at 0x7F0000000000+; extra
    rows must use addresses outside that band (see EXTRA_BASE)."""
    rows, regions, lo = [], [], 0x7F0000000000
    for name, data in members.items():
        path = os.path.join(TREE, name)
        length = 0x1000
        rows.append(row(lo, lo + length, 0, path))
        regions.append((lo, data[:length]))
        lo += 0x100000
    rows.extend(extra_rows)
    regions.extend(extra_regions)
    return rows, regions


# extra (synthetic) rows live far away from the good rows' band so that no two
# rows can share an address range
EXTRA_BASE = 0x7F4000000000


# --------------------------------------------------------------- the scenarios
def scenario_control(mod):
    """CONTROL: an in-range executable row whose mapped bytes equal the member's
    bytes is read, compared and recorded; no code problem."""
    members = required_members()
    rows, regions = build_rows_and_mem(members)
    mem = FakeMem()
    for start, data in regions:
        mem.add(start, data)
    probs, out = observe(mod, rows, members, mem)
    cp = code_problems(probs)
    check("control", "no code problem", not cp, f"code problems={cp}")
    check("control", "four archive files seen", len(out["files"]) == 4,
          f"files={sorted(out['files'])}")
    check("control", "one range read per file", out["ranges"] == 4,
          f"ranges={out['ranges']} pread_calls={mem.calls}")
    check("control", "every pread within ROW_CAP",
          all(l <= mod.ROW_CAP for _o, l in mem.calls),
          f"ROW_CAP={mod.ROW_CAP} calls={mem.calls}")
    check("control", "snaps recorded", len(out["snaps"]) == 4,
          f"snaps={sorted(out['snaps'])}")
    check("control", "code leg passes", leg_code(probs, out), "not cprobs and cobs")


def scenario_row_cap(mod):
    """CLAUSE-A: a maps row of ROW_CAP + 4096 bytes over an archive member must be
    reported as a problem and never read from /proc/<pid>/mem."""
    cap = mod.ROW_CAP
    members = required_members()
    rows, regions = build_rows_and_mem(members)
    victim = os.path.join(TREE, "libggml.so.0.27.0")
    big_lo = EXTRA_BASE + 0x1000000
    big_len = cap + 4096
    rows.append(row(big_lo, big_lo + big_len, 0, victim))
    mem = FakeMem()
    for start, data in regions:
        mem.add(start, data)
    probs, out = observe(mod, rows, members, mem)
    cp = code_problems(probs)
    want = f"is {big_len} bytes; not read"
    hit = [p for p in cp if want in p]
    check("clause-A", "oversized row reported as a problem", bool(hit), f"hit={hit} all={cp}")
    check("clause-A", "no pread longer than ROW_CAP",
          all(l <= cap for _o, l in mem.calls),
          f"calls={mem.calls} ROW_CAP={cap}")
    check("clause-A", "oversized row not counted as compared", out["ranges"] == 4,
          f"ranges={out['ranges']}")
    check("clause-A", "code leg fails", not leg_code(probs, out),
          "a ROW_CAP violation is a code problem")


def scenario_past_member(mod):
    """CLAUSE-B: a maps row whose file range extends past the archive member's end
    must be reported as a problem, not zero-padded and byte-compared."""
    members = required_members()
    rows, regions = build_rows_and_mem(members)
    victim = os.path.join(TREE, "libggml.so.0.27.0")
    data = members["libggml.so.0.27.0"]
    past_lo = EXTRA_BASE + 0x2000000
    length = 0x1000
    off = len(data) - 0x800          # starts inside the member, ends past its end
    rows.append(row(past_lo, past_lo + length, off, victim))
    mem = FakeMem()
    for start, blob in regions:
        mem.add(start, blob)
    mem.add(past_lo, data[off:off + 0x800])   # the file-backed part; the rest is zeros
    probs, out = observe(mod, rows, members, mem)
    cp = code_problems(probs)
    hit = [p for p in cp if "extends past the member" in p]
    check("clause-B", "past-the-end row reported as a problem", bool(hit),
          f"hit={hit} all={cp}")
    check("clause-B", "the past-the-end row was not read",
          all(not (o == past_lo) for o, _l in mem.calls),
          f"pread offsets={[o for o, _l in mem.calls]}")
    check("clause-B", "past-the-end row not counted as compared", out["ranges"] == 4,
          f"ranges={out['ranges']}")
    past_range = f"{past_lo:012x}-{past_lo + 0x1000:012x}"
    accepted = [k for k in out["snaps"] if k.endswith("|" + past_range)]
    check("clause-B", "not zero-padded into a byte-equal verdict", not accepted,
          f"accepted snaps for the past-the-end row={accepted} snaps={sorted(out['snaps'])}")
    check("clause-B", "code leg fails", not leg_code(probs, out),
          "a past-the-end row is a code problem")


# --------------------------------------------------------------- mutants
ROW_CAP_GUARD = '''                if length > ROW_CAP:
                    probs.append(f"code: maps row {f[0]} of {member} is {length} bytes; not read")
                    continue
'''

PAST_END_GUARD = '''                if off + length > len(data):
                    probs.append(f"code: maps row {f[0]} of {member} extends past the member "
                                 f"({off + length} > {len(data)} bytes)")
                    continue
'''


def mutant_source(src, drop=(), replace=None):
    out = src
    if "row_cap" in drop:
        assert ROW_CAP_GUARD in out
        out = out.replace(ROW_CAP_GUARD, "                if False:\n                    pass\n")
    if "past_end" in drop:
        assert PAST_END_GUARD in out
        out = out.replace(PAST_END_GUARD, "                if False:\n                    pass\n")
    if replace == "zero_pad_accept":
        # A mutant that "fixes" the past-the-end case by zero-padding the expected
        # bytes instead of failing: the zero-padded tail then matches the kernel's
        # zero-filled tail and the row is accepted.
        pad = ('                if off + length > len(data):\n'
               '                    want = data[off:off + length].ljust(length, b"\\0")\n'
               '                    try:\n'
               '                        got = os.pread(mem, length, lo)\n'
               '                    except OSError:\n'
               '                        continue\n'
               '                    compared += 1\n'
               '                    if collect:\n'
               '                        snaps[f"{path}|{f[0]}"] = hashlib.sha256(got).hexdigest()\n'
               '                    if got != want:\n'
               '                        probs.append(f"code: mapped bytes {f[0]} (offset {f[2]}) '
               'of {member} differ from the archive member")\n'
               '                    seen.setdefault(path, (dev, ino, member))\n'
               '                    continue\n')
        assert PAST_END_GUARD in out
        out = out.replace(PAST_END_GUARD, pad)
    return out


def scenario_mutants(src, scratch):
    """The probe must have teeth: with the guards removed the same synthetic rows
    are accepted or read without bound."""
    # M1: ROW_CAP guard removed -> the oversized row is read (unbounded per-row
    # allocation, the Sen1Mem F3 hazard).
    m1 = os.path.join(scratch, "mutant-no-row-cap.py")
    with REAL_OPEN(m1, "w") as fh:
        fh.write(mutant_source(src, drop=("row_cap",)))
    mod1 = load_module(m1, "mutant_no_row_cap")
    cap = mod1.ROW_CAP
    members = required_members()
    # the victim member must be large enough that the PAST-THE-END guard does not
    # fire first, so that only the removed ROW_CAP guard stands between the
    # oversized row and the read
    victim_name = "libggml-cpu-zen4.so"
    members[victim_name] = bytes(range(32)) * ((cap + 0x2000) // 32)
    rows, regions = build_rows_and_mem(members)
    victim = os.path.join(TREE, victim_name)
    big_lo = EXTRA_BASE + 0x1000000
    big_len = cap + 4096
    rows.append(row(big_lo, big_lo + big_len, 0, victim))
    mem = FakeMem()
    for start, data in regions:
        mem.add(start, data)
    probs, out = observe(mod1, rows, members, mem)
    over = [(o, l) for o, l in mem.calls if l > cap]
    check("mutant-M1", "without the ROW_CAP guard the oversized row IS read",
          bool(over), f"oversized preads={over} (ROW_CAP={cap})")
    check("mutant-M1", "without the ROW_CAP guard the oversized row is not reported",
          not [p for p in code_problems(probs) if "not read" in p],
          f"code problems={code_problems(probs)}")

    # M2: past-the-end guard removed -> the row is read and truncated-compared
    # (the "zero-padded" tail never matches, so the row is compared, not refused).
    m2 = os.path.join(scratch, "mutant-no-past-end.py")
    with REAL_OPEN(m2, "w") as fh:
        fh.write(mutant_source(src, drop=("past_end",)))
    mod2 = load_module(m2, "mutant_no_past_end")
    members = required_members()
    rows, regions = build_rows_and_mem(members)
    victim = os.path.join(TREE, "libggml.so.0.27.0")
    data = members["libggml.so.0.27.0"]
    past_lo = EXTRA_BASE + 0x2000000
    off = len(data) - 0x800
    rows.append(row(past_lo, past_lo + 0x1000, off, victim))
    mem = FakeMem()
    for start, blob in regions:
        mem.add(start, blob)
    mem.add(past_lo, data[off:off + 0x800])
    probs, out = observe(mod2, rows, members, mem)
    read = [(o, l) for o, l in mem.calls if o == past_lo]
    check("mutant-M2", "without the past-the-end guard the row IS read",
          bool(read), f"preads={mem.calls}")
    check("mutant-M2", "without the past-the-end guard the row is not refused",
          not [p for p in code_problems(probs) if "extends past the member" in p],
          f"code problems={code_problems(probs)}")

    # M3: past-the-end case "fixed" by zero-padding the expected bytes -> the row
    # is accepted as byte-equal (the exact hazard clause B forbids).
    m3 = os.path.join(scratch, "mutant-zero-pad.py")
    with REAL_OPEN(m3, "w") as fh:
        fh.write(mutant_source(src, replace="zero_pad_accept"))
    mod3 = load_module(m3, "mutant_zero_pad")
    members = required_members()
    rows, regions = build_rows_and_mem(members)
    victim = os.path.join(TREE, "libggml.so.0.27.0")
    data = members["libggml.so.0.27.0"]
    past_lo = EXTRA_BASE + 0x2000000
    off = len(data) - 0x800
    rows.append(row(past_lo, past_lo + 0x1000, off, victim))
    mem = FakeMem()
    for start, blob in regions:
        mem.add(start, blob)
    mem.add(past_lo, data[off:off + 0x800])
    probs, out = observe(mod3, rows, members, mem)
    accepted = [k for k in out["snaps"] if k.startswith(victim)]
    check("mutant-M3", "a zero-padding 'fix' accepts the past-the-end row",
          bool(accepted) and not [p for p in code_problems(probs)
                                  if "extends past the member" in p],
          f"accepted snaps={accepted} code problems={code_problems(probs)}")


CHILD_SRC = r'''
import ctypes, os, sys, time
libc = ctypes.CDLL("libc.so.6", use_errno=True)
libc.mmap.restype = ctypes.c_void_p
libc.mmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int,
                       ctypes.c_int, ctypes.c_int, ctypes.c_long]
tree = sys.argv[1]
MAP_PRIVATE, PROT_READ, PROT_EXEC = 0x02, 0x01, 0x04
for spec in sys.argv[2:]:
    name, length = spec.rsplit(":", 1)
    p = os.path.join(tree, name)
    fd = os.open(p, os.O_RDONLY)
    addr = libc.mmap(None, int(length), PROT_READ | PROT_EXEC, MAP_PRIVATE, fd, 0)
    if addr in (None, ctypes.c_void_p(-1).value):
        raise SystemExit("mmap failed for %s: %s" % (name, os.strerror(ctypes.get_errno())))
print(os.getpid(), flush=True)
time.sleep(120)
'''


def scenario_mutant_m4(src, scratch):
    """M4: with an archive member SMALLER than the oversized row (the real b11909
    archive: the largest member is 7.9 MB, far below ROW_CAP), removing the ROW_CAP
    guard does not change the verdict - the past-the-end guard refuses the row too,
    only with a different message.  So the ROW_CAP refusal path is dormant with the
    real archive and reachable only for a member >= ROW_CAP (M1) - which is exactly
    what the real-kernel scenario exercises (a 64 MiB + 4096 sparse member)."""
    m4 = os.path.join(scratch, "mutant-no-row-cap-small-member.py")
    with REAL_OPEN(m4, "w") as fh:
        fh.write(mutant_source(src, drop=("row_cap",)))
    mod4 = load_module(m4, "mutant_no_row_cap_small_member")
    members = required_members()
    rows, regions = build_rows_and_mem(members)
    victim = os.path.join(TREE, "libggml.so.0.27.0")
    big_lo = EXTRA_BASE + 0x3000000
    big_len = mod4.ROW_CAP + 4096
    rows.append(row(big_lo, big_lo + big_len, 0, victim))
    mem = FakeMem()
    for start, data in regions:
        mem.add(start, data)
    probs, out = observe(mod4, rows, members, mem)
    over = [(o, l) for o, l in mem.calls if l > mod4.ROW_CAP]
    cp = code_problems(probs)
    check("mutant-M4", "with a small member, the oversized row is still refused without "
          "the ROW_CAP guard", not over and bool(cp),
          f"oversized preads={over} problems={cp}")
    check("mutant-M4", "the refusal message differs (ROW_CAP guard vs past-the-end guard)",
          not [p for p in cp if "bytes; not read" in p]
          and bool([p for p in cp if "extends past the member" in p]),
          f"problems={cp}")


def scenario_real_kernel(mod, src, workdir):
    """REAL-KERNEL variant: no fake mem fd and no synthetic maps rows.  A child
    process mmaps real files (through libc mmap, which - unlike python's mmap -
    permits a length past EOF) under a tree whose names satisfy the counter's
    REQUIRED patterns, and the counter reads the child's REAL /proc/<pid>/maps and
    /proc/<pid>/mem.

    Case 1 (legitimate): four 8192-byte files mapped over 8192 bytes -> each row
    is read, byte-compared and accepted.
    Case 2 (clause B, past the member's end): a 4096-byte file mapped over 8192
    bytes - the mapping runs past EOF, the exact shape clause B names -> the
    counter must refuse the row as a problem, not read and zero-pad it.
    Case 3 (clause A, ROW_CAP): a sparse file mapped over ROW_CAP + 4096 bytes ->
    the counter must refuse the row as a problem and never read it.
    """
    import subprocess
    import time

    tree = os.path.join(workdir, "tree")
    os.makedirs(tree, exist_ok=True)
    names = ["libllama-server-impl.so", "libggml-base.so.0.27.0",
             "libggml.so.0.27.0", "libggml-cpu-zen4.so"]
    payload = {}
    for i, n in enumerate(names):
        blob = bytes((i * 37 + j * 11) % 256 for j in range(8192))
        payload[n] = blob
        with REAL_OPEN(os.path.join(tree, n), "wb") as fh:
            fh.write(blob)
    # a file mapped past EOF: 4096 bytes of file, 8192 bytes of mapping
    payload["libggml-past-eof.so"] = payload[names[0]][:4096]
    with REAL_OPEN(os.path.join(tree, "libggml-past-eof.so"), "wb") as fh:
        fh.write(payload["libggml-past-eof.so"])
    # a file whose size is NOT page aligned (6144) mapped over 8192: the kernel
    # zero-fills the last 2048 bytes of the final page.  A zero-padding
    # implementation of clause B is byte-equal to exactly this, so it accepts the
    # row - the hazard the clause names.
    payload["libggml-partial-eof.so"] = payload[names[1]][:6144]
    with REAL_OPEN(os.path.join(tree, "libggml-partial-eof.so"), "wb") as fh:
        fh.write(payload["libggml-partial-eof.so"])
    # a sparse file larger than ROW_CAP, mapped over ROW_CAP + 4096 bytes
    cap = mod.ROW_CAP
    big_len = cap + 4096
    big_name = "libggml-cpu-huge.so"
    big_path = os.path.join(tree, big_name)
    with REAL_OPEN(big_path, "wb") as fh:
        fh.truncate(big_len)

    child = os.path.join(workdir, "child.py")
    with REAL_OPEN(child, "w") as fh:
        fh.write(CHILD_SRC)
    specs = [f"{n}:8192" for n in names] + ["libggml-past-eof.so:8192",
                                            "libggml-partial-eof.so:8192",
                                            f"{big_name}:{big_len}"]
    proc = subprocess.Popen([sys.executable, child, tree] + specs,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        line = proc.stdout.readline().strip()
        if not line.isdigit():
            err = proc.stderr.read()
            raise RuntimeError(f"child did not start: {line!r} stderr={err[:400]!r}")
        pid = int(line)
        time.sleep(0.8)
        saved_open, saved_os = mod.open, mod.os
        mod.open = REAL_OPEN
        mod.os = REAL_OS
        try:
            members = dict(payload)
            members[big_name] = b"\0" * big_len
            probs = []
            out = mod.code_observe(pid, tree, FakeArchive(members), probs, collect=True)
        finally:
            mod.open, mod.os = saved_open, saved_os
        cp = code_problems(probs)
        past = [p for p in cp if "extends past the member" in p]
        oversize = [p for p in cp if "bytes; not read" in p]
        check("real-kernel", "the real past-EOF row is refused as a problem",
              bool(past), f"hit={past} all={cp}")
        check("real-kernel", "the real past-EOF row was not byte-compared",
              not [k for k in out["snaps"] if "past-eof" in k],
              f"snaps={sorted(out['snaps'])}")
        check("real-kernel", "the real >ROW_CAP row is refused as a problem",
              bool(oversize), f"hit={oversize} all={cp}")
        check("real-kernel", "the real >ROW_CAP row was not byte-compared",
              not [k for k in out["snaps"] if "huge" in k],
              f"snaps={sorted(out['snaps'])}")
        legit = [k for k in out["snaps"] if "past-eof" not in k and "huge" not in k]
        check("real-kernel", "the four legitimate real mappings were read and accepted",
              len(legit) == 4, f"accepted={sorted(legit)} problems={cp}")

        # the sharpest falsification, on the real kernel: a zero-padding
        # implementation of clause B is byte-equal to the REAL kernel's
        # zero-filled partial page past EOF, so it accepts the row.
        mz = os.path.join(workdir, "mutant-zero-pad.py")
        with REAL_OPEN(mz, "w") as fh:
            fh.write(mutant_source(src, replace="zero_pad_accept"))
        modz = load_module(mz, "mutant_zero_pad_real")
        # a freshly imported module keeps the builtin open and the real os, so it
        # reads the real /proc without any shadowing
        zprobs = []
        zout = modz.code_observe(pid, tree, FakeArchive(members), zprobs, collect=True)
        zaccepted = [k for k in zout["snaps"] if "partial-eof" in k]
        check("real-kernel", "the frozen counter also refuses the real partial-EOF row",
              not [k for k in out["snaps"] if "partial-eof" in k]
              and bool([p for p in cp if "partial-eof" in p]),
              f"frozen snaps={sorted(out['snaps'])} problems={cp}")
        check("real-kernel", "a zero-padding implementation ACCEPTS the real partial-EOF "
              "row (the kernel zero-fills the partial page past EOF, so zero-padding is "
              "byte-equal to it)", bool(zaccepted),
              f"accepted={zaccepted} problems={code_problems(zprobs)}")
    finally:
        proc.kill()
        proc.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", default=COUNTER)
    ap.add_argument("--receipt", default=None)
    ap.add_argument("--real-kernel", action="store_true",
                    help="also run the real /proc variant (spawns a short-lived child)")
    a = ap.parse_args()

    with REAL_OPEN(a.counter, "rb") as fh:
        src_bytes = fh.read()
    sha = hashlib.sha256(src_bytes).hexdigest()
    check("frozen", "counter bytes match the preregistration sha256",
          sha == PREREG_SHA, f"sha256={sha} expected={PREREG_SHA}")
    src = src_bytes.decode("utf-8")

    mod = load_module(a.counter, "frozen_round54_replay_code_audit")
    check("frozen", "ROW_CAP is 64 MiB", mod.ROW_CAP == 64 << 20,
          f"ROW_CAP={mod.ROW_CAP} ({mod.ROW_CAP} bytes)")
    check("frozen", "the two guards are present in the frozen source",
          ROW_CAP_GUARD in src and PAST_END_GUARD in src,
          "ROW_CAP guard and past-the-end guard found verbatim")

    scenario_control(mod)
    scenario_row_cap(mod)
    scenario_past_member(mod)

    scratch = tempfile.mkdtemp(prefix="j2rowcap-")
    try:
        scenario_mutants(src, scratch)
        scenario_mutant_m4(src, scratch)
        if a.real_kernel:
            scenario_real_kernel(mod, src, scratch)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    failed = [r for r in RESULTS if not r["ok"]]
    receipt = {"counter": a.counter, "counter_sha256": sha, "row_cap": mod.ROW_CAP,
               "checks": RESULTS, "passed": len(RESULTS) - len(failed),
               "failed": len(failed)}
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    if a.receipt:
        os.makedirs(os.path.dirname(os.path.abspath(a.receipt)), exist_ok=True)
        with REAL_OPEN(a.receipt, "w") as fh:
            json.dump(receipt, fh, indent=2, sort_keys=True)
            fh.write("\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
