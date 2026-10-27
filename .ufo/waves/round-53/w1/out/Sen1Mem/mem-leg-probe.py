#!/usr/bin/env python3
"""Seat Sen1Mem probe 1: the counter's /proc/<pid>/mem read.

A  descendant target (the counter's real shape under Yama ptrace_scope 1): open the
   memory read-only, read bytes, and show that a write on that descriptor is impossible
   (the counter opens O_RDONLY and only pread()s: tools/round53-replay-code-audit.py:405,427).
B  a target this process is NOT an ancestor of (the shape ptrace_scope 2 produces for a
   descendant too: PTRACE_MODE_ATTACH denied - man 2 ptrace, scope 2 "Only processes with
   the CAP_SYS_PTRACE capability ... may perform PTRACE_MODE_ATTACH operations"): the maps
   file (PTRACE_MODE_READ) still opens, /proc/<pid>/mem (PTRACE_MODE_ATTACH) does not - and
   the counter's own code_observe()/leg expression are run on that pid to show the receipt
   it would produce.
Run: python3 mem-leg-probe.py <non-descendant-pid>
"""
import ctypes
import errno
import importlib.util
import os
import resource
import subprocess
import sys
import time

sys.dont_write_bytecode = True
COUNTER = "/fast/scratch/hyaku/kama-r53/Sen1Mem/c1.py"   # byte copy of the lane counter
TARGET = r"""
import ctypes, mmap, os, sys, time
m = mmap.mmap(-1, 4096)
m.write(b"SEN1MEM-MARKER " + b"\0" * (4096 - 15))
print(hex(ctypes.addressof(ctypes.c_char.from_buffer(m))), flush=True)
time.sleep(60)
"""


def load_counter():
    spec = importlib.util.spec_from_file_location("c1", COUNTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def is_ancestor_of(anc, pid):
    seen = 0
    while pid > 1 and seen < 512:
        try:
            with open(f"/proc/{pid}/stat") as fh:
                ppid = int(fh.read().rsplit(")", 1)[1].split()[1])
        except (OSError, IndexError, ValueError):
            return False
        if ppid == anc:
            return True
        pid, seen = ppid, seen + 1
    return False


def part_a():
    print("== A: descendant (the counter's real shape, ptrace_scope 1)")
    p = subprocess.Popen([sys.executable, "-c", TARGET], stdout=subprocess.PIPE, text=True)
    try:
        addr = int(p.stdout.readline().strip(), 16)   # the child's marker address
        fd = os.open(f"/proc/{p.pid}/mem", os.O_RDONLY)
        got = os.pread(fd, 15, addr)
        print(f"   child pid            {p.pid} (probe {os.getpid()} is its ancestor: "
              f"{is_ancestor_of(os.getpid(), p.pid)})")
        print(f"   open /proc/<pid>/mem O_RDONLY  ok, fd {fd}; pread 15 bytes at {addr:#x} -> {got!r} (marker read back)")
        try:
            os.write(fd, b"\x00")
        except OSError as exc:
            print(f"   os.write on that descriptor     {errno.errorcode.get(exc.errno)} ({exc.strerror}) "
                  f"-> a read-only mem descriptor cannot modify the child")
        os.close(fd)
        print("   byte content never leaves the counter: code_observe only compares and")
        print("   appends 'mapped bytes ... differ' (no bytes in the receipt) "
              "tools/round53-replay-code-audit.py:433")
    finally:
        p.kill()
        p.wait()


def part_b(pid):
    print(f"== B: pid {pid}, not a descendant of this probe ({os.getpid()})")
    c1 = load_counter()
    try:
        rows = open(f"/proc/{pid}/maps").read().splitlines()
        xrows = [r for r in rows if "x" in r.split()[1]]
        print(f"   /proc/<pid>/maps (PTRACE_MODE_READ)   readable: {len(rows)} rows, {len(xrows)} executable")
    except OSError as exc:
        print(f"   /proc/<pid>/maps unreadable: {exc}")
    probs = []
    cobs = c1.code_observe(pid, "/nonexistent-tree", None, probs)
    print(f"   c1.code_observe(pid, tree, arc=None)  -> {cobs!r}")
    for pr in probs:
        print(f"      problem: {pr}")
    oprobs = []
    se = c1.sealed_exe(pid, oprobs)
    print(f"   c1.sealed_exe(pid) (READ mode)        -> {'tuple' if se else None} "
          f"(image {'opened' if se else 'not opened'}), problems {len(oprobs)}: {oprobs[:1]}")
    leg = (not probs and cobs is not None)
    print(f"   counter leg expression (line 660) `not cprobs and cobs is not None` -> {leg}")
    print("   receipt it would print: bind/sealed/teardown/newrow unaffected (READ mode),")
    print("   code=0 coderuns=0/3 met=False, exit 1 -> fail closed, no leg silently passes.")
    print("   NOTE: the counter does not refuse a non-descendant pid before the read; it only")
    print("   records 'does not descend from the replay process' (lines 576-577) and reads anyway.")


def main():
    part_a()
    if len(sys.argv) > 1:
        part_b(int(sys.argv[1]))
    else:
        print("== B skipped: no non-descendant pid given")
    print(f"probe maxrss {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} KiB")


if __name__ == "__main__":
    main()
