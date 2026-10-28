#!/usr/bin/env python3
"""Scratch probe: list own-uid pids whose /proc/<pid>/fd is unreadable, with the
counter's two readings (st_uid of /proc/<pid>, Uid: line of /proc/<pid>/status)."""
import os

me = os.getuid()
rows = []
for name in os.listdir('/proc'):
    if not name.isdigit():
        continue
    pid = int(name)
    try:
        os.listdir(f'/proc/{pid}/fd')
        continue
    except PermissionError:
        pass
    except OSError:
        continue
    try:
        st_uid = os.stat(f'/proc/{pid}').st_uid
    except OSError:
        st_uid = None
    try:
        uid_line = [l for l in open(f'/proc/{pid}/status') if l.startswith('Uid:')][0].split()[1]
        uid_line = int(uid_line)
    except (OSError, IndexError, ValueError):
        uid_line = None
    try:
        comm = open(f'/proc/{pid}/comm').read().strip()
    except OSError:
        comm = '?'
    rows.append((pid, st_uid, uid_line, comm))

print('unreadable fd-table pids (pid, stat_uid, status_uid, comm):')
for r in rows:
    print(r)
print('own-uid by stat_uid:', sum(1 for r in rows if r[1] == me),
      ' own-uid by status Uid:', sum(1 for r in rows if r[2] == me))
