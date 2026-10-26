#!/usr/bin/env python3
"""The real release/rebind hazard in pick_port's default branch
(tools/kama-llamacpp-live.py:371-378): the socket is bound to 127.0.0.1:0, the offered port is
read, and the socket is CLOSED before the child binds. If the kernel hands that just-released
port to the next bind(:0), two concurrent runs can pick one port.

Model: bind(:0) -> read -> close -> bind(:0) -> read, in one process (the kernel's ephemeral
rover is per net namespace, shared by all processes, so this models a second run picking right
after the first released). Mechanism evidence only, not a lane tool run.
"""
import json
import socket
import sys

TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 200000


def pick():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


same = 0
firsts = []
for _ in range(TRIALS):
    p1 = pick()
    p2 = pick()
    firsts.append(p1)
    if p1 == p2:
        same += 1
print(json.dumps({"trials": TRIALS, "released_port_reassigned": same,
                  "rate": same / TRIALS, "distinct_first_ports": len(set(firsts))}))
