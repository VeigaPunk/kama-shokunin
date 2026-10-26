"""Sen1Witness: (F1) --witness-timeout inf on the live tool = no deadline, then
SIGKILL proves the pdeathsig chain; (F2) the replay with inf dies with an
uncaught OverflowError after spawning its live child (orphan, no receipt)."""
import json
import os
import signal
import socket
import subprocess
import sys
import time

S = os.environ.get("SEN1_S", "/fast/scratch/hyaku/kama-r49/Sen1Witness")
LANE = os.path.join(S, "lane")
SRV = os.path.join(S, "F/work/server/llama-b11909/llama-server")
MDL = os.path.join(S, "F/work/download/stories260K.gguf")
SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
import shutil
shutil.rmtree(os.path.join(S, "G"), ignore_errors=True)
shutil.rmtree(os.path.join(S, "F2"), ignore_errors=True)
WD = os.path.join(S, "G/wd")
os.makedirs(WD, exist_ok=True)
env = dict(os.environ, TMPDIR=os.path.join(S, "G/tmp"))
os.makedirs(env["TMPDIR"], exist_ok=True)
log = open(os.path.join(S, "G/live.log"), "wb")


def state(port):
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=0.5)
        s.close()
        return "OPEN"
    except OSError as e:
        return "CLOSED:" + type(e).__name__


print("F1: live tool --witness-timeout inf", flush=True)
t0 = time.monotonic()
p = subprocess.Popen([sys.executable, os.path.join(LANE, "tools/kama-llamacpp-live.py"),
                      "--server", SRV, "--model", MDL, "--model-sha256", SHA,
                      "--alias", "kama-r48-live", "--ctx", "256", "--threads", "1",
                      "--out", os.path.join(S, "G/live-receipt.json"),
                      "--witness-dir", WD, "--witness-timeout", "inf"],
                     env=env, stdout=log, stderr=log)
ready = None
while time.monotonic() - t0 < 120 and p.poll() is None:
    rp = os.path.join(WD, "ready.json")
    if os.path.exists(rp):
        try:
            ready = json.load(open(rp))
            break
        except (OSError, ValueError):
            pass
    time.sleep(0.1)
assert ready and os.path.exists(f"/proc/{ready['pid']}"), "stale ready.json"
print(f"F1: ready {ready} at +{time.monotonic()-t0:.1f}s", flush=True)
pid, port = ready["pid"], ready["port"]
for i in range(10):
    time.sleep(0.5)
    print(f"F1: +{time.monotonic()-t0:.1f}s live={p.poll() is None} "
          f"server={os.path.exists(f'/proc/{pid}')} port={state(port)}", flush=True)
print("F1: SIGKILL the live tool", flush=True)
os.kill(p.pid, signal.SIGKILL)
p.wait()
for i in range(20):
    if not os.path.exists(f"/proc/{pid}"):
        print(f"F1: server gone +{0.1*(i+1):.1f}s after SIGKILL, port {state(port)}", flush=True)
        break
    time.sleep(0.1)
else:
    print(f"F1: SERVER SURVIVED: {os.path.exists(f'/proc/{pid}')} port {state(port)}", flush=True)
print(f"F1: receipt written={os.path.exists(os.path.join(S, 'G/live-receipt.json'))} "
      f"wd after={sorted(os.listdir(WD))}", flush=True)

print("F2: replay --witness-timeout inf", flush=True)
base = os.path.join(S, "F2")
for x in ("wd", "work", "tmp", "home", "cache"):
    os.makedirs(os.path.join(base, x), exist_ok=True)
env2 = dict(os.environ, TMPDIR=os.path.join(base, "tmp"), HOME=os.path.join(base, "home"),
            XDG_CACHE_HOME=os.path.join(base, "cache"))
log2 = open(os.path.join(base, "replay.log"), "wb")
t0 = time.monotonic()
q = subprocess.Popen([sys.executable, os.path.join(LANE, "tools/kama-live-replay.py"),
                      "--receipt", os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-1.json"),
                      "--work", os.path.join(base, "work"), "--out", os.path.join(base, "replay.json"),
                      "--witness-dir", os.path.join(base, "wd"), "--witness-timeout", "inf"],
                     env=env2, stdout=log2, stderr=log2)
code = q.wait(timeout=180)
print(f"F2: replay exit {code} after {time.monotonic()-t0:.1f}s", flush=True)
print("F2: replay.log tail: " + open(os.path.join(base, "replay.log"), errors="replace").read().strip().splitlines()[-1], flush=True)
print(f"F2: replay.json written={os.path.exists(os.path.join(base, 'replay.json'))} "
      f"rerun receipt={os.path.exists(os.path.join(base, 'work/rerun-receipt.json'))} "
      f"wd={sorted(os.listdir(os.path.join(base, 'wd')))}", flush=True)
time.sleep(3)
left = subprocess.run(["pgrep", "-af", base], capture_output=True, text=True).stdout.strip()
print("F2: processes matching this run after the crash: " + (left or "none"), flush=True)
log.close(); log2.close()
