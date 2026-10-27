#!/usr/bin/env python3
"""Reject probe: /proc/<pid>/environ alone is not proof of interpreter cleanliness.

The child sets a canary in its own environment *after* exec and reports what its
own os.environ holds; the parent reads /proc/<pid>/environ.  The kernel file is
the exec-time environment block, so the canary is invisible there while the
process really carries it.  The counter therefore checks a *marker file* written
by the planted sitecustomize, not environ alone.
"""
import os
import subprocess
import sys
import tempfile
import time

d = tempfile.mkdtemp(prefix="environ-", dir=os.environ.get("TMPDIR") or None)
report = os.path.join(d, "child-view.txt")
child = subprocess.Popen([sys.executable, "-c",
                          "import os,sys,time\n"
                          "os.environ['KAMA_R50_CANARY']='planted-after-exec'\n"
                          "open(sys.argv[1],'w').write('KAMA_R50_CANARY' in os.environ and os.environ['KAMA_R50_CANARY'])\n"
                          "time.sleep(30)\n", report])
time.sleep(0.6)
while not os.path.exists(report):
    time.sleep(0.05)
raw = open(f"/proc/{child.pid}/environ", "rb").read()
keys = sorted(k for k, _, _ in (e.partition(b"=") for e in raw.split(b"\0")) if k)
print("pid:", child.pid)
print("child's own os.environ carries KAMA_R50_CANARY:", open(report).read())
print("/proc/<pid>/environ carries KAMA_R50_CANARY:", b"KAMA_R50_CANARY" in raw)
print("environ key count:", len(keys))
child.kill()
child.wait()
