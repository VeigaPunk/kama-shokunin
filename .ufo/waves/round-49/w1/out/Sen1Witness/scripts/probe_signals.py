"""Sen1Witness: Ctrl-C (SIGINT to the replay's own process group) tears the
hold down; a negative --witness-timeout passed to the frozen replay is only
caught by the live tool, after the download."""
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time

S = os.environ.get("SEN1_S", "/fast/scratch/hyaku/kama-r49/Sen1Witness")
LANE = os.path.join(S, "lane")
REPLAY = os.path.join(LANE, "tools/kama-live-replay.py")
RECEIPT = os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-1.json")
BASE = os.path.join(S, "sig")
shutil.rmtree(BASE, ignore_errors=True)


def env_for(name):
    base = os.path.join(BASE, name)
    for x in ("wd", "work", "tmp", "home", "cache"):
        os.makedirs(os.path.join(base, x), exist_ok=True)
    return dict(os.environ, TMPDIR=os.path.join(base, "tmp"), HOME=os.path.join(base, "home"),
                XDG_CACHE_HOME=os.path.join(base, "cache")), base


def port_state(port):
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=0.5)
        s.close()
        return "OPEN"
    except OSError as e:
        return "CLOSED:" + type(e).__name__


env, base = env_for("ctrl-c")
log = open(os.path.join(base, "replay.log"), "wb")
t0 = time.monotonic()
p = subprocess.Popen([sys.executable, REPLAY, "--receipt", RECEIPT, "--work", os.path.join(base, "work"),
                      "--out", os.path.join(base, "replay.json"), "--witness-dir", os.path.join(base, "wd"),
                      "--witness-timeout", "60"],
                     env=env, stdout=log, stderr=log, start_new_session=True)
ready = None
while time.monotonic() - t0 < 120 and p.poll() is None:
    rp = os.path.join(base, "wd/ready.json")
    if os.path.exists(rp):
        ready = json.load(open(rp))
        break
    time.sleep(0.1)
pid, port = ready["pid"], ready["port"]
print(f"ctrl-c: ready pid={pid} port={port}; replay pgid={os.getpgid(p.pid)} (own session)", flush=True)
print("ctrl-c: SIGINT to the replay's process group (what a terminal Ctrl-C does)", flush=True)
os.killpg(os.getpgid(p.pid), signal.SIGINT)
for i in range(30):
    time.sleep(0.2)
    if not os.path.exists(f"/proc/{pid}"):
        print(f"ctrl-c: server gone +{0.2*(i+1):.1f}s port={port_state(port)} replay_exit={p.poll()}", flush=True)
        break
else:
    print(f"ctrl-c: SERVER STILL UP server={os.path.exists(f'/proc/{pid}')} port={port_state(port)}", flush=True)
code = p.wait(timeout=60)
print(f"ctrl-c: replay exit {code}", flush=True)
rr = os.path.join(base, "work/rerun-receipt.json")
d = json.load(open(rr)) if os.path.exists(rr) else {}
print(f"ctrl-c: rerun witness={d.get('witness')} outcome={d.get('outcome')} "
      f"setup_error={d.get('setup_error')}", flush=True)
log.close()

env, base = env_for("negative")
log = open(os.path.join(base, "replay.log"), "wb")
t0 = time.monotonic()
q = subprocess.run([sys.executable, REPLAY, "--receipt", RECEIPT, "--work", os.path.join(base, "work"),
                    "--out", os.path.join(base, "replay.json"), "--witness-dir", os.path.join(base, "wd"),
                    "--witness-timeout", "-5"], env=env, stdout=log, stderr=log, timeout=300)
print(f"negative: replay exit {q.returncode} after {time.monotonic()-t0:.1f}s "
      f"(download happened: {os.path.exists(os.path.join(base, 'work/download'))})", flush=True)
o = os.path.join(base, "replay.json")
print(f"negative: out={json.load(open(o)) if os.path.exists(o) else None}", flush=True)
log.close()
