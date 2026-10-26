"""Sen1Witness: cross-uid symlink clobber of ready.json.tmp and non-regular
`release` acceptance. Unit level against the frozen clone."""
import importlib.util
import os
import shutil
import subprocess
import sys
import time

S = os.environ.get("SEN1_S", "/fast/scratch/hyaku/kama-r49/Sen1Witness")
TOOL = os.path.join(S, "lane/tools/kama-llamacpp-live.py")
spec = importlib.util.spec_from_file_location("klive", TOOL)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def child():
    return subprocess.Popen(["sleep", "30"])


# A. non-sticky world-writable witness dir, another uid plants ready.json.tmp
d = os.path.join(S, "unit/x-world-writable")
shutil.rmtree(d, ignore_errors=True)
os.makedirs(d)
os.chmod(d, 0o777)
victim = os.path.join(d, "operator-notes.txt")
open(victim, "w").write("OPERATOR DATA THAT MUST SURVIVE\n")
q = subprocess.run(["sudo", "-n", "-u", "nobody", "ln", "-s", victim,
                    os.path.join(d, "ready.json.tmp")], capture_output=True, text=True)
print(f"A: nobody planted ready.json.tmp rc={q.returncode} {q.stderr.strip()}")
c = child()
try:
    r = m.hold_for_witness(d, c, 4321, 0.2)
    print(f"A: hold released={r['released']}")
except Exception as e:
    print(f"A: hold raised {type(e).__name__}: {e}")
c.kill(); c.wait()
print(f"A: victim now {open(victim, 'rb').read()[:80]!r}")
rp = os.path.join(d, "ready.json")
print(f"A: ready.json islink={os.path.islink(rp)} "
      f"-> {os.readlink(rp) if os.path.islink(rp) else None} mode={oct(os.stat(rp).st_mode & 0o777)}")

# B. sticky world-writable dir: the kernel refuses the follow (fs.protected_symlinks=1)
d2 = os.path.join(S, "unit/x-sticky")
shutil.rmtree(d2, ignore_errors=True)
os.makedirs(d2)
os.chmod(d2, 0o1777)
v2 = os.path.join(d2, "notes.txt")
open(v2, "w").write("STICKY DIR DATA\n")
subprocess.run(["sudo", "-n", "-u", "nobody", "ln", "-s", v2, os.path.join(d2, "ready.json.tmp")],
               capture_output=True)
c = child()
try:
    m.hold_for_witness(d2, c, 4321, 0.2)
    print("B: no raise")
except Exception as e:
    print(f"B: raised {type(e).__name__}: {e}")
c.kill(); c.wait()
print(f"B: victim now {open(v2, 'rb').read()[:60]!r}")

# C. non-regular release (FIFO) releases the hold instantly
d3 = os.path.join(S, "unit/x-fifo")
shutil.rmtree(d3, ignore_errors=True)
os.makedirs(d3)
os.mkfifo(os.path.join(d3, "release"))
c = child()
r = m.hold_for_witness(d3, c, 4321, 30)
print(f"C: fifo release -> released={r['released']} waited_ms={r['waited_ms']}")
c.kill(); c.wait()

# D. pre-existing ready.json as a directory: loud failure, not a silent pass
d4 = os.path.join(S, "unit/x-readydir")
shutil.rmtree(d4, ignore_errors=True)
os.makedirs(os.path.join(d4, "ready.json"))
c = child()
try:
    m.hold_for_witness(d4, c, 4321, 0.2)
    print("D: no raise")
except Exception as e:
    print(f"D: raised {type(e).__name__}: {e}")
c.kill(); c.wait()
