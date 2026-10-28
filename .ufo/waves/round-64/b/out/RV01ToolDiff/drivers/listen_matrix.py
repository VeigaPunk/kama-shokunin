#!/usr/bin/env python3
"""Scratch harness (not lane source): for each bind address, open a LISTEN socket on a
free-ish unregistered port, ask the tool's own _listen_inodes/_proc_holders what it sees,
and report. Imports the tool from the scratch clone, read-only."""
import importlib.util
import socket
import sys

D = sys.argv[1]
spec = importlib.util.spec_from_file_location('t', D + '/tools/kama-completion-live.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
live = m._live

cases = [
    ('127.0.0.1', socket.AF_INET, None),
    ('127.0.0.2', socket.AF_INET, None),
    ('::1', socket.AF_INET6, None),
    ('::ffff:127.0.0.1', socket.AF_INET6, None),
    ('0.0.0.0', socket.AF_INET, None),
    ('::', socket.AF_INET6, 0),
]
ip = socket.gethostbyname(socket.gethostname())
cases.append((ip, socket.AF_INET, None))
port = 45930
for addr, fam, v6only in cases:
    s = socket.socket(fam, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if v6only is not None:
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, v6only)
    try:
        s.bind((addr, port))
    except OSError as e:
        print(f'{addr:>18}: bind failed {e}')
        s.close()
        continue
    s.listen(1)
    inodes = live._listen_inodes(port)
    holders = m._proc_holders(port)
    print(f'{addr:>18}: _listen_inodes={sorted(inodes)} '
          f'_proc_holders={[(h["pid"]) for h in holders]} '
          f'port_closed_by_tool={not inodes}')
    s.close()
print('done')
