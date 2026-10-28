#!/usr/bin/env python3
"""Scratch probe: after a child calls prctl(PR_SET_DUMPABLE,0), does /proc/<pid>
st_uid flip to 0 (root-owned, dumpable=0 semantics), and how does that depend on
when the parent first looks? Prints st_uid at several delays and the fd-table
readability; the status Uid line is printed for comparison."""
import os
import subprocess
import sys
import time

child = subprocess.Popen([sys.executable, '-c',
                          'import ctypes,time,os\n'
                          'ctypes.CDLL(None).prctl(4,0,0,0,0)\n'
                          'print("ready", flush=True)\n'
                          'time.sleep(60)'],
                         stdout=subprocess.PIPE, text=True)
child.stdout.readline()          # child is past prctl
pid = child.pid


def snap(tag):
    try:
        uid = os.stat(f'/proc/{pid}').st_uid
    except OSError as e:
        uid = f'err{e.errno}'
    try:
        os.listdir(f'/proc/{pid}/fd')
        fd = 'readable'
    except OSError as e:
        fd = f'EACCES' if e.errno == 13 else f'err{e.errno}'
    st = [l.strip() for l in open(f'/proc/{pid}/status') if l.startswith('Uid:')][0]
    print(f'{tag:>18}: st_uid={uid} fd={fd} {st}')


snap('immediately')
for d in (0.05, 0.5, 2.0):
    time.sleep(d)
    snap(f'after {d}s')
child.kill()

# fresh child: prctl, then stat repeatedly without any sleep
child2 = subprocess.Popen([sys.executable, '-c',
                           'import ctypes,time\n'
                           'ctypes.CDLL(None).prctl(4,0,0,0,0)\n'
                           'print("ready", flush=True)\n'
                           'time.sleep(60)'],
                          stdout=subprocess.PIPE, text=True)
child2.stdout.readline()
pid = child2.pid
snap('fresh-immediate')
snap('fresh-again')
child2.kill()
