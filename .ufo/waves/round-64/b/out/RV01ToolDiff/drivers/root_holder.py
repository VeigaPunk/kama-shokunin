#!/usr/bin/env python3
"""Scratch demo helper (not lane source): as root, duplicate one fd of a target
process via pidfd_getfd(2) and hold it until a stop file appears or a timeout.
usage: root_holder.py <target_pid> <target_fd> <stopfile> <timeout_s>"""
import ctypes
import os
import sys
import time

target, tfd, stop, timeout = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], float(sys.argv[4])
libc = ctypes.CDLL(None, use_errno=True)
SYS_pidfd_open = 434   # x86_64
SYS_pidfd_getfd = 438  # x86_64
pfd = libc.syscall(SYS_pidfd_open, target, 0)
if pfd < 0:
    raise SystemExit(f'pidfd_open errno={ctypes.get_errno()}')
nfd = libc.syscall(SYS_pidfd_getfd, pfd, tfd, 0)
if nfd < 0:
    raise SystemExit(f'pidfd_getfd errno={ctypes.get_errno()}')
print(f'me={os.getpid()} dup_fd={nfd} target={target}:{tfd}', flush=True)
t0 = time.monotonic()
while not os.path.exists(stop) and time.monotonic() - t0 < timeout:
    time.sleep(0.05)
print('released', flush=True)
