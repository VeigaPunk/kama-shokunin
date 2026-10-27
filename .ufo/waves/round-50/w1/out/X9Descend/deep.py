#!/usr/bin/env python3
"""Fork a chain of <depth> processes under the caller; every ancestor waits for its
child, so the whole spine stays alive until the leaf exits. The leaf sleeps."""
import os
import sys
import time

depth = int(sys.argv[1])
for _ in range(depth):
    pid = os.fork()
    if pid:
        os.waitpid(pid, 0)
        os._exit(0)
time.sleep(600)
