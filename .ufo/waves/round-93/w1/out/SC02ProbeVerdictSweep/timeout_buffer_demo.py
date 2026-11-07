#!/usr/bin/env python3
"""SC02: does `timeout` SIGTERM kill lose python's block-buffered stdout?

A python child writes many lines to a pipe (pipe => full buffering) then sleeps.
The reader sees only what was flushed before the kill.
"""
import subprocess, sys, time

SCRIPT = (
    "import sys,time\n"
    "for i in range(200000):\n"
    "    sys.stdout.write('%d\\tinvalid\\n' % i)\n"
    "time.sleep(30)\n"
)
FLUSHED = SCRIPT.replace("time.sleep(30)", "sys.stdout.flush(); time.sleep(30)")


def count(b):
    return b.decode(errors="replace").count("\n")


# 1) killed by SIGTERM (what `timeout` sends)
p = subprocess.Popen([sys.executable, "-c", SCRIPT], stdout=subprocess.PIPE)
time.sleep(2.0)
p.terminate()
out, _ = p.communicate(timeout=60)
print(f"SIGTERM case:   rc={p.returncode} lines_seen={count(out)} bytes={len(out)}")

# 2) same, but flushed before sleeping
p = subprocess.Popen([sys.executable, "-c", FLUSHED], stdout=subprocess.PIPE)
time.sleep(2.0)
p.terminate()
out, _ = p.communicate(timeout=60)
print(f"flushed+SIGTERM rc={p.returncode} lines_seen={count(out)} bytes={len(out)}")

# 3) the probe's exact wrapper: `timeout N python3 -c ...`
p = subprocess.run(["timeout", "2", sys.executable, "-c", SCRIPT], capture_output=True)
print(f"timeout wrapper: rc={p.returncode} lines_seen={count(p.stdout)} bytes={len(p.stdout)}")

# 4) line-buffered / unbuffered equivalents, for contrast
for extra, label in ((["-u"], "python -u"), (["-"], "no")):
    if label == "no":
        continue
    p = subprocess.Popen([sys.executable, *extra, "-c", SCRIPT], stdout=subprocess.PIPE)
    time.sleep(2.0)
    p.terminate()
    out, _ = p.communicate(timeout=60)
    print(f"{label}: rc={p.returncode} lines_seen={count(out)} bytes={len(out)}")
