"""Sen1Witness runs F/E: --witness-timeout inf (no deadline) with SIGKILL of the
live tool, and SIGKILL of the replay (pdeathsig chain replay -> live tool -> server)."""
import json
import os
import signal
import socket
import subprocess
import sys
import time

S = "/fast/scratch/hyaku/kama-r49/Sen1Witness"
TREE = os.path.join(S, "lane")
RECEIPT = os.path.join(TREE, ".ufo/waves/round-48/c2/live/receipt-1.json")
REPLAY = os.path.join(TREE, "tools/kama-live-replay.py")


def port_state(port):
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=0.5)
        s.close()
        return "OPEN"
    except OSError as e:
        return "CLOSED:" + type(e).__name__


def start(tag, wt):
    base = os.path.join(S, tag)
    wd, work, out = (os.path.join(base, x) for x in ("wd", "work", "replay.json"))
    for d in (wd, work):
        os.makedirs(d, exist_ok=True)
    env = dict(os.environ, HOME=os.path.join(base, "home"), XDG_CACHE_HOME=os.path.join(base, "cache"),
               TMPDIR=os.path.join(base, "tmp"))
    for k in ("HOME", "XDG_CACHE_HOME", "TMPDIR"):
        os.makedirs(env[k], exist_ok=True)
    log = open(os.path.join(base, "replay.log"), "wb")
    t0 = time.monotonic()
    p = subprocess.Popen([sys.executable, REPLAY, "--receipt", RECEIPT, "--work", work, "--out", out,
                          "--witness-dir", wd, "--witness-timeout", str(wt)],
                         env=env, stdout=log, stderr=log)
    while time.monotonic() - t0 < 120 and p.poll() is None:
        rp = os.path.join(wd, "ready.json")
        if os.path.exists(rp):
            try:
                return p, json.load(open(rp)), work, wd, time.monotonic()
            except (OSError, ValueError):
                pass
        time.sleep(0.1)
    return p, None, work, wd, time.monotonic()


print("=== F: --witness-timeout inf, then SIGKILL the live tool ===", flush=True)
p, ready, work, wd, tr = start("F", "inf")
print("F: replay argv ok, ready:", ready, flush=True)
pid, port = ready["pid"], ready["port"]
kids = subprocess.run(["pgrep", "-P", str(p.pid), "-a"], capture_output=True, text=True).stdout
live = [int(l.split()[0]) for l in kids.splitlines() if "kama-llamacpp-live" in l]
print("F: live tool:", live, flush=True)
for i in range(12):
    time.sleep(0.5)
    print(f"F: +{time.monotonic()-tr:.1f}s (inf -> no deadline) live={os.path.exists(f'/proc/{live[0]}')} "
          f"server={os.path.exists(f'/proc/{pid}')} port={port_state(port)} replay={p.poll()}", flush=True)
print("F: SIGKILL live tool", flush=True)
os.kill(live[0], signal.SIGKILL)
for i in range(20):
    time.sleep(0.1)
    if not os.path.exists(f"/proc/{pid}"):
        print(f"F: server gone +{0.1*(i+1):.1f}s after SIGKILL; port {port_state(port)}", flush=True)
        break
else:
    print(f"F: SERVER SURVIVED SIGKILL of the live tool: server={os.path.exists(f'/proc/{pid}')} "
          f"port={port_state(port)}", flush=True)
code = p.wait(timeout=120)
print(f"F: replay exit {code} at +{time.monotonic()-tr:.1f}s", flush=True)
o = os.path.join(os.path.dirname(work), "replay.json")
print("F: replay out:", (json.load(open(o)) if os.path.exists(o) else {}) and
      json.dumps(json.load(open(o)))[:260], flush=True)
rr = os.path.join(work, "rerun-receipt.json")
print("F: rerun receipt present:", os.path.exists(rr), flush=True)

print("=== E: SIGKILL the replay (pdeathsig chain) ===", flush=True)
p, ready, work, wd, tr = start("E", 8)
print("E: ready:", ready, flush=True)
pid, port = ready["pid"], ready["port"]
kids = subprocess.run(["pgrep", "-P", str(p.pid), "-a"], capture_output=True, text=True).stdout
live = [int(l.split()[0]) for l in kids.splitlines() if "kama-llamacpp-live" in l]
print(f"E: SIGKILL replay {p.pid} (live tool {live}, server {pid})", flush=True)
os.kill(p.pid, signal.SIGKILL)
for i in range(10):
    time.sleep(0.25)
    print(f"E: +{time.monotonic()-tr:.1f}s replay={p.poll()} "
          f"live={[l for l in live if os.path.exists(f'/proc/{l}')]} "
          f"server={os.path.exists(f'/proc/{pid}')} port={port_state(port)}", flush=True)
time.sleep(1)
print("E: after the 8s witness timeout:", flush=True)
for i in range(40):
    alive_live = [l for l in live if os.path.exists(f"/proc/{l}")]
    alive = os.path.exists(f"/proc/{pid}")
    st = port_state(port)
    if not alive_live and not alive:
        print(f"E: torn down at +{time.monotonic()-tr:.1f}s port={st}", flush=True)
        break
    time.sleep(0.5)
else:
    print(f"E: STILL ALIVE live={alive_live} server={alive} port={port_state(port)}", flush=True)
rr = os.path.join(work, "rerun-receipt.json")
print("E: rerun witness:", (json.load(open(rr)).get("witness") if os.path.exists(rr) else None), flush=True)
