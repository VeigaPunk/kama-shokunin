#!/usr/bin/env python3
"""Sen2Proc probe 5: port stealing between the counter's check and its release.

(a) a stranger listener on the observed port after the server is gone; (b) a listener
whose accept queue is saturated (SYN dropped): does port_refuses() still say "refuses"?
(c) SO_REUSEPORT steal attempt against an existing listener."""
import importlib.util
import json
import os
import socket
import subprocess
import sys
import time

S = "/fast/scratch/hyaku/kama-r50/Sen2Proc"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


c1 = load("c1", os.path.join(S, "imp", "c1.py"))


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def listen_state(port):
    rows = []
    for name in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            next(open(name))
        except (OSError, StopIteration):
            continue
        with open(name) as fh:
            next(fh, None)
            for line in fh:
                f = line.split()
                if len(f) >= 10 and f[3] == "0A" and int(f[1].rsplit(":", 1)[1], 16) == port:
                    rows.append({"file": name, "local": f[1], "state": f[3], "inode": f[9]})
    return rows


out = {}

# (a) stranger listener holding the port
port = free_port()
srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", port))
srv.listen(8)
try:
    t0 = time.monotonic()
    out["stranger_listener"] = {
        "port": port,
        "listen_rows": listen_state(port),
        "counter_listen_inodes": sorted(c1.listen_inodes(port)),
        "port_refuses": c1.port_refuses(port),
        "port_refuses_seconds": round(time.monotonic() - t0, 3),
        "pid_socket_inodes_of_a_stranger_pid": sorted(c1.pid_socket_inodes(os.getpid())),
    }
    # (c) a second bind with SO_REUSEPORT against a non-REUSEPORT listener
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    try:
        s2.bind(("127.0.0.1", port))
        out["reuseport_steal"] = "BIND-SUCCEEDED"
    except OSError as exc:
        out["reuseport_steal"] = f"{type(exc).__name__}: {exc}"
    finally:
        s2.close()
finally:
    srv.close()

# (b) listener with a saturated accept queue: connect() stops completing, but the port is
# still LISTENing.  The counter's port_refuses() maps any OSError to True.
port = free_port()
sat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sat.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sat.bind(("127.0.0.1", port))
sat.listen(0)
clients = []
try:
    for _ in range(8):
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.setblocking(False)
        c.connect_ex(("127.0.0.1", port))
        clients.append(c)
    time.sleep(0.2)
    rows = listen_state(port)
    t0 = time.monotonic()
    refused = c1.port_refuses(port)
    out["saturated_backlog"] = {
        "port": port,
        "listen_rows_while_probe": rows,
        "port_refuses": refused,
        "port_refuses_seconds": round(time.monotonic() - t0, 3),
        "still_listening_after_probe": bool(listen_state(port)),
    }
finally:
    for c in clients:
        c.close()
    sat.close()

# (d) the control: nothing listening
port = free_port()
t0 = time.monotonic()
out["no_listener_control"] = {"port": port, "port_refuses": c1.port_refuses(port),
                              "seconds": round(time.monotonic() - t0, 3)}
print(json.dumps(out, indent=1))
