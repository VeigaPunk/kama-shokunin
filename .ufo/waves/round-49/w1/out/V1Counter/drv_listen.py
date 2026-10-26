#!/usr/bin/env python3
"""L1: listen_inodes() against real sockets (state 0A, address acceptance)."""
import importlib.util
import socket
import sys
import os

S = "/fast/scratch/hyaku/kama-r49/V1Counter"
OUT = open(f"{S}/out/listen.txt", "w")

spec = importlib.util.spec_from_file_location(
    "r49c1", f"{S}/lane/tools/round49-replay-witness-audit.py")
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)

spec2 = importlib.util.spec_from_file_location(
    "live", f"{S}/lane/tools/kama-llamacpp-live.py")
live = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(live)

def w(s=""):
    print(s)
    OUT.write(s + "\n")

socks = []
try:
    s4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s4.bind(("127.0.0.1", 0)); s4.listen()
    socks.append(("tcp4 127.0.0.1", s4))

    s61 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    s61.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
    s61.bind(("::1", 0, 0, 0)); s61.listen()
    socks.append(("tcp6 ::1 V6ONLY=1", s61))

    s6all = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    s6all.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    s6all.bind(("::", 0, 0, 0)); s6all.listen()
    socks.append(("tcp6 :: dual-stack V6ONLY=0", s6all))

    s6map = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    s6map.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    s6map.bind(("::ffff:127.0.0.1", 0, 0, 0)); s6map.listen()
    socks.append(("tcp6 ::ffff:127.0.0.1 (mapped)", s6map))
except OSError as e:
    w(f"socket setup error: {e}")

for name, s in socks:
    port = s.getsockname()[1]
    row4 = row6 = None
    try:
        with open("/proc/net/tcp") as fh:
            row4 = [ln for ln in fh.read().splitlines()[1:]
                    if ln.split() and int(ln.split()[1].rsplit(":", 1)[1], 16) == port]
    except OSError:
        pass
    try:
        with open("/proc/net/tcp6") as fh:
            row6 = [ln for ln in fh.read().splitlines()[1:]
                    if ln.split() and int(ln.split()[1].rsplit(":", 1)[1], 16) == port]
    except OSError:
        pass
    li = cc.listen_inodes(port)
    li_live = live._listen_inodes(port)
    w(f"--- {name} port={port} ---")
    if row4:
        f = row4[0].split()
        w(f"  /proc/net/tcp row: st={f[3]} addr={f[1]} inode={f[9]}")
    if row6:
        f = row6[0].split()
        w(f"  /proc/net/tcp6 row: st={f[3]} addr={f[1]} inode={f[9]}")
    w(f"  C1 listen_inodes={sorted(li)}  live-tool _listen_inodes={sorted(li_live)}")
    if not row4 and not row6:
        w("  (no proc row visible)")

for _, s in socks:
    s.close()
OUT.close()
print("DONE")
