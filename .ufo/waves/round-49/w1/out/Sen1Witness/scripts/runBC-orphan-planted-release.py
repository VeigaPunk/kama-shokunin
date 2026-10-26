"""Sen1Witness runs B/C: orphaned hold after SIGTERM to the replay, and a
pre-existing release file in the witness dir of a real replay."""
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


def run(tag, witness_timeout, action, pre=None):
    base = os.path.join(S, tag)
    wd, work, out = (os.path.join(base, x) for x in ("wd", "work", "replay.json"))
    os.makedirs(wd, exist_ok=True)
    os.makedirs(work, exist_ok=True)
    env = dict(os.environ, HOME=os.path.join(base, "home"), XDG_CACHE_HOME=os.path.join(base, "cache"),
               TMPDIR=os.path.join(base, "tmp"))
    for k in ("HOME", "XDG_CACHE_HOME", "TMPDIR"):
        os.makedirs(env[k], exist_ok=True)
    if pre:
        pre(wd)
        print(f"{tag}: pre-seeded wd -> {sorted(os.listdir(wd))}", flush=True)
    log = open(os.path.join(base, "replay.log"), "wb")
    t0 = time.monotonic()
    p = subprocess.Popen([sys.executable, REPLAY, "--receipt", RECEIPT, "--work", work, "--out", out,
                          "--witness-dir", wd, "--witness-timeout", str(witness_timeout)],
                         env=env, stdout=log, stderr=log)
    ready = None
    while time.monotonic() - t0 < 600 and p.poll() is None:
        rp = os.path.join(wd, "ready.json")
        if os.path.exists(rp):
            try:
                ready = json.load(open(rp))
                break
            except (OSError, ValueError):
                pass
        time.sleep(0.1)
    tr = time.monotonic()
    print(f"{tag}: ready at +{tr-t0:.2f}s pid={ready and ready.get('pid')} port={ready and ready.get('port')}", flush=True)
    if not ready:
        print(f"{tag}: no ready, replay exit {p.poll()}", flush=True)
        return
    pid, port = ready["pid"], ready["port"]
    kids = subprocess.run(["pgrep", "-P", str(p.pid), "-a"], capture_output=True, text=True).stdout
    live_pids = [int(l.split()[0]) for l in kids.splitlines() if "kama-llamacpp-live" in l]
    action(p, live_pids, pid, port, tr, tag)
    code = p.wait()
    print(f"{tag}: replay exit {code} at +{time.monotonic()-tr:.2f}s after ready", flush=True)
    for i in range(300):
        alive_live = [lp for lp in live_pids if os.path.exists(f"/proc/{lp}")]
        alive_srv = os.path.exists(f"/proc/{pid}")
        st = port_state(port)
        if not alive_live and not alive_srv and st.startswith("CLOSED"):
            print(f"{tag}: all gone at +{time.monotonic()-tr:.2f}s (port {st})", flush=True)
            break
        if i % 20 == 0:
            print(f"{tag}: +{time.monotonic()-tr:.2f}s live_tool={alive_live} server={alive_srv} port={st}", flush=True)
        time.sleep(0.25)
    else:
        print(f"{tag}: STILL ALIVE after 75s: live={alive_live} srv={alive_srv} port={port_state(port)}", flush=True)
    rr = os.path.join(work, "rerun-receipt.json")
    if os.path.exists(rr):
        d = json.load(open(rr))
        print(f"{tag}: rerun witness={d.get('witness')} outcome={d.get('outcome')} "
              f"setup_error={d.get('setup_error')}", flush=True)
    else:
        print(f"{tag}: NO rerun receipt", flush=True)
    print(f"{tag}: wd after -> {sorted(os.listdir(wd))}", flush=True)
    log.close()


def sigterm_replay(p, live_pids, pid, port, tr, tag):
    print(f"{tag}: SIGTERM replay {p.pid} (live tool {live_pids}, server {pid})", flush=True)
    os.kill(p.pid, signal.SIGTERM)
    for i in range(12):
        time.sleep(0.25)
        print(f"{tag}: +{time.monotonic()-tr:.2f}s replay={p.poll()} "
              f"live={[lp for lp in live_pids if os.path.exists(f'/proc/{lp}')]} "
              f"server={os.path.exists(f'/proc/{pid}')} port={port_state(port)}", flush=True)


def watch_instant_release(p, live_pids, pid, port, tr, tag):
    # how long does the server stay reachable after ready.json appeared?
    for i in range(40):
        if p.poll() is not None:
            print(f"{tag}: replay exited +{time.monotonic()-tr:.2f}s after ready; port {port_state(port)}",
                  flush=True)
            break
        time.sleep(0.1)


print("=== B: SIGTERM to the replay only ===", flush=True)
run("B", 15, sigterm_replay)
print("=== C: pre-existing release file ===", flush=True)
run("C", 60, watch_instant_release,
    pre=lambda wd: open(os.path.join(wd, "release"), "w").write("planted before the run\n"))
