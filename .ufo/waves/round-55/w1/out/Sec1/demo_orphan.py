import os, signal, subprocess, sys, time
S = os.environ["S"]
c = subprocess.Popen([sys.executable, os.path.join(S, "c_standin.py"), S])
for _ in range(100):
    if os.path.exists(os.path.join(S, "CHILD.PID")) and os.path.exists(os.path.join(S, "INVOKER.PID")):
        break
    time.sleep(0.1)
inv = int(open(os.path.join(S, "INVOKER.PID")).read())
ch = int(open(os.path.join(S, "CHILD.PID")).read())
def alive(pid):
    try:
        os.kill(pid, 0); return True
    except OSError:
        return False
print("counter-stand-in pid %d, invoker %d, replay-stand-in %d" % (c.pid, inv, ch))
print("before: invoker alive=%s child alive=%s" % (alive(inv), alive(ch)))
os.kill(c.pid, signal.SIGKILL); c.wait()      # the counter dies as if OOM-killed
time.sleep(1.5)
print("after SIGKILL of the counter: invoker alive=%s child alive=%s" % (alive(inv), alive(ch)))
os.kill(inv, signal.SIGTERM)                  # the replay's own pdeathsig defence
time.sleep(1.0)
print("after SIGTERM of the invoker: invoker alive=%s child alive=%s" % (alive(inv), alive(ch)))
for pid in (inv, ch):
    if alive(pid):
        os.kill(pid, signal.SIGKILL)
for f in ("CHILD.PID", "INVOKER.PID", "inv.log"):
    p = os.path.join(S, f)
    if os.path.exists(p): os.unlink(p)
