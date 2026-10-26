"""Sen1Witness: status of each finding against the CURRENT working tree
(uncommitted, wave in flight), not the frozen commit. Pinned by digest in the
report; the tree is moving while seats land."""
import hashlib
import importlib.util
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request

S = os.environ.get("SEN1_S", "/fast/scratch/hyaku/kama-r49/Sen1Witness")
LANE = os.environ.get("SEN1_LANE_WT", os.path.join(S, "wt2"))
LIVE = os.path.join(LANE, "tools/kama-llamacpp-live.py")
REPLAY = os.path.join(LANE, "tools/kama-live-replay.py")
RECEIPT = os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-1.json")
SRV = os.path.join(S, "F/work/server/llama-b11909/llama-server")
MDL = os.path.join(S, "F/work/download/stories260K.gguf")
SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
FROZEN_EXE = "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0"
BASE = os.path.join(S, "wt")
shutil.rmtree(BASE, ignore_errors=True)


def mk(name):
    d = os.path.join(BASE, name)
    os.makedirs(os.path.join(d, "wd"), 0o755)
    os.makedirs(os.path.join(d, "work"), exist_ok=True)
    for x in ("tmp", "home", "cache"):
        os.makedirs(os.path.join(d, x), exist_ok=True)
    env = dict(os.environ, TMPDIR=os.path.join(d, "tmp"), HOME=os.path.join(d, "home"),
               XDG_CACHE_HOME=os.path.join(d, "cache"))
    return d, env


def port_open(port):
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=0.5)
        s.close()
        return True
    except OSError:
        return False


def post(port, path, body):
    q = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(body).encode(),
                               headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(q, timeout=10) as r:
        return json.loads(r.read())


def observe(pid, port):
    """The four checks the frozen C1 counter makes."""
    out = []
    try:
        h = hashlib.sha256(open(f"/proc/{pid}/exe", "rb").read()).hexdigest()
    except OSError as exc:
        return [f"exe unreadable: {exc}"]
    out.append(("exe-frozen", h == FROZEN_EXE))
    ss = subprocess.run(["ss", "-ltnpH", f"sport = :{port}"], capture_output=True, text=True).stdout
    out.append(("listen-owned", f"pid={pid}" in ss))
    argv = open(f"/proc/{pid}/cmdline", "rb").read().split(b"\0")
    m = argv[argv.index(b"-m") + 1].decode()
    out.append(("model-frozen", hashlib.sha256(open(m, "rb").read()).hexdigest()
                == "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"))
    try:
        tk = post(port, "/tokenize", {"content": "kama witness deadbeefdeadbeef", "with_pieces": True})["tokens"]
        dt = post(port, "/detokenize", {"tokens": [t["id"] for t in tk]})["content"]
        out.append(("nonce", dt.strip() == "kama witness deadbeefdeadbeef"))
    except (OSError, KeyError, ValueError) as exc:
        out.append(("nonce", f"failed: {exc}"))
    return out


# ---- W1: a pre-existing release is removed at start (F2 pre-start case) ----
d, env = mk("w1")
open(os.path.join(d, "wd/release"), "w").write("planted\n")
p = subprocess.Popen([sys.executable, REPLAY, "--receipt", RECEIPT, "--work", os.path.join(d, "work"),
                      "--out", os.path.join(d, "replay.json"), "--witness-dir", os.path.join(d, "wd"),
                      "--witness-timeout", "3"], env=env,
                     stdout=open(os.path.join(d, "log"), "wb"), stderr=subprocess.STDOUT)
code = p.wait(timeout=200)
rr = json.load(open(os.path.join(d, "work/rerun-receipt.json"))) if os.path.exists(
    os.path.join(d, "work/rerun-receipt.json")) else {}
w = rr.get("witness") or {}
print(f"W1 planted-release-before-run: replay exit {code} witness={w} -> "
      f"{'CLOSED' if w.get('released') is False and w.get('waited_ms', 0) >= 2900 else 'OPEN'}", flush=True)

# ---- W2: a symlink at the per-run temp name is never followed (F1) ----
spec = importlib.util.spec_from_file_location("klive", LIVE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
d, _ = mk("w2")
victim = os.path.join(d, "victim.txt")
open(victim, "w").write("OPERATOR DATA\n")
c = subprocess.Popen(["sleep", "30"])
os.symlink(victim, os.path.join(d, "wd", "ready.json.tmp.%d" % c.pid))
try:
    m.hold_for_witness(os.path.join(d, "wd"), c, 4001, 0.5)
    print("W2 temp-symlink: NO RAISE (open)", flush=True)
except Exception as e:
    print(f"W2 temp-symlink: raised {type(e).__name__}: {getattr(e, 'code', e)} "
          f"victim={open(victim).read().strip()!r} wd={sorted(os.listdir(os.path.join(d, 'wd')))} -> "
          f"{'CLOSED' if open(victim).read().strip() == 'OPERATOR DATA' else 'OPEN'}", flush=True)
c.kill(); c.wait()

# ---- W3: an unwritable witness dir fails at validation (F7) ----
d, env = mk("w3")
os.chmod(os.path.join(d, "wd"), 0o500)
q = subprocess.run([sys.executable, LIVE, "--server", SRV, "--model", MDL, "--model-sha256", SHA,
                    "--witness-dir", os.path.join(d, "wd"), "--witness-timeout", "3"],
                   capture_output=True, text=True, timeout=120)
print(f"W3 unwritable-dir: rc={q.returncode} err={q.stderr.strip().splitlines()[-1][:110]} -> "
      f"{'CLOSED' if q.returncode == 2 and 'witness-dir-unwritable' in q.stderr else 'OPEN'}", flush=True)
os.chmod(os.path.join(d, "wd"), 0o755)

# ---- W4: --witness-timeout inf still accepted by the live tool (F4) ----
d, env = mk("w4")
q = subprocess.run([sys.executable, LIVE, "--server", SRV, "--model", MDL, "--model-sha256", SHA,
                    "--witness-dir", os.path.join(d, "wd"), "--witness-timeout", "inf"],
                   capture_output=True, text=True, timeout=5) if False else None
p = subprocess.Popen([sys.executable, LIVE, "--server", SRV, "--model", MDL, "--model-sha256", SHA,
                      "--alias", "kama-r48-live", "--ctx", "256", "--threads", "1",
                      "--out", os.path.join(d, "receipt.json"), "--witness-dir", os.path.join(d, "wd"),
                      "--witness-timeout", "inf"], env=env,
                     stdout=open(os.path.join(d, "live.log"), "wb"), stderr=subprocess.STDOUT)
ready, t0 = None, time.monotonic()
while time.monotonic() - t0 < 60 and p.poll() is None:
    rp = os.path.join(d, "wd/ready.json")
    if os.path.exists(rp):
        ready = json.load(open(rp))
        break
    time.sleep(0.05)
held = ready is not None
print(f"W4 inf-hold: ready={ready} after {time.monotonic()-t0:.1f}s "
      f"(a finite 0.5 s timeout would have ended the hold); -> "
      f"{'OPEN' if ready else 'refused'}", flush=True)
if ready:
    pid = ready["pid"]
    time.sleep(1.5)
    still = os.path.exists(f"/proc/{pid}") and port_open(ready["port"])
    print(f"W4 still-held-after-1.5s: {still} -> {'OPEN (no deadline)' if still else 'closed'}", flush=True)
p.send_signal(signal.SIGTERM)
p.wait(timeout=60)

# ---- W5: the replay still dies with OverflowError on inf (F4) ----
d, env = mk("w5")
q = subprocess.run([sys.executable, REPLAY, "--receipt", RECEIPT, "--work", os.path.join(d, "work"),
                    "--out", os.path.join(d, "replay.json"), "--witness-dir", os.path.join(d, "wd"),
                    "--witness-timeout", "inf"], env=env, capture_output=True, text=True, timeout=300)
tail = (q.stderr or q.stdout).strip().splitlines()[-1]
print(f"W5 replay-inf: rc={q.returncode} out_written={os.path.exists(os.path.join(d, 'replay.json'))} "
      f"tail={tail[:90]} -> {'OPEN' if q.returncode != 2 or 'OverflowError' in tail else 'CLOSED'}", flush=True)

# ---- foreign server used by W6/W7 ----
d, env = mk("foreign")
pl = subprocess.Popen([sys.executable, LIVE, "--server", SRV, "--model", MDL, "--model-sha256", SHA,
                       "--alias", "kama-r48-live", "--ctx", "256", "--threads", "1",
                       "--out", os.path.join(d, "receipt.json"), "--witness-dir", os.path.join(d, "wd"),
                       "--witness-timeout", "inf"], env=env,
                      stdout=open(os.path.join(d, "log"), "wb"), stderr=subprocess.STDOUT)
fready, t0 = None, time.monotonic()
while time.monotonic() - t0 < 60 and pl.poll() is None:
    rp = os.path.join(d, "wd/ready.json")
    if os.path.exists(rp):
        fready = json.load(open(rp))
        break
    time.sleep(0.05)
print(f"foreign server {fready}", flush=True)

# ---- W6: ready.json planted in the pre-announcement window (F3 residual) ----
d, env = mk("w6")
p = subprocess.Popen([sys.executable, REPLAY, "--receipt", RECEIPT, "--work", os.path.join(d, "work"),
                      "--out", os.path.join(d, "replay.json"), "--witness-dir", os.path.join(d, "wd"),
                      "--witness-timeout", "5"], env=env,
                     stdout=open(os.path.join(d, "log"), "wb"), stderr=subprocess.STDOUT)
wd = os.path.join(d, "wd")
seen, planted, t0 = None, False, time.monotonic()
while time.monotonic() - t0 < 120:
    kids = subprocess.run(["pgrep", "-P", str(p.pid)], capture_output=True, text=True).stdout.split()
    if kids and not planted:
        # the live tool exists: it has just run prepare_witness_dir and is starting the server
        shutil.copy(os.path.join(os.path.dirname(os.path.dirname(d)), "foreign/wd/ready.json")
                    if False else os.path.join(BASE, "foreign/wd/ready.json"),
                    os.path.join(wd, "ready.json"))
        planted = True
        print(f"W6 planted foreign ready.json at +{time.monotonic()-t0:.2f}s (live tool pid {kids[0]})", flush=True)
    if os.path.exists(os.path.join(wd, "ready.json")):
        try:
            seen = json.load(open(os.path.join(wd, "ready.json")))
            break
        except (OSError, ValueError):
            pass
    time.sleep(0.01)
print(f"W6 poller read at +{time.monotonic()-t0:.2f}s: {seen}", flush=True)
if seen:
    print(f"W6 observations on the announced pid: {observe(seen['pid'], seen['port'])}", flush=True)
open(os.path.join(wd, "release"), "w").write("released\n")
code = p.wait(timeout=300)
rr = json.load(open(os.path.join(d, "work/rerun-receipt.json"))) if os.path.exists(
    os.path.join(d, "work/rerun-receipt.json")) else {}
print(f"W6 replay exit {code} rerun witness={(rr.get('witness') or {})} -> "
      f"{'OPEN' if seen and seen.get('pid') == fready['pid'] else 'closed'}", flush=True)

# ---- W7: ready.json replaced during the hold (F3 residual) ----
d, env = mk("w7")
p = subprocess.Popen([sys.executable, REPLAY, "--receipt", RECEIPT, "--work", os.path.join(d, "work"),
                      "--out", os.path.join(d, "replay.json"), "--witness-dir", os.path.join(d, "wd"),
                      "--witness-timeout", "8"], env=env,
                     stdout=open(os.path.join(d, "log"), "wb"), stderr=subprocess.STDOUT)
wd = os.path.join(d, "wd")
own, t0 = None, time.monotonic()
while time.monotonic() - t0 < 120:
    rp = os.path.join(wd, "ready.json")
    if os.path.exists(rp):
        try:
            own = json.load(open(rp))
            break
        except (OSError, ValueError):
            pass
    time.sleep(0.05)
print(f"W7 the tool's own announcement {own}", flush=True)
shutil.copy(os.path.join(BASE, "foreign/wd/ready.json"), os.path.join(wd, "ready.json"))
late = json.load(open(os.path.join(wd, "ready.json")))
print(f"W7 replaced during the hold; a later poller reads {late}", flush=True)
print(f"W7 observations: {observe(late['pid'], late['port'])}", flush=True)
open(os.path.join(wd, "release"), "w").write("released\n")
code = p.wait(timeout=300)
print(f"W7 replay exit {code}; announced own pid {own['pid']} vs delivered {late['pid']} -> "
      f"{'OPEN' if own['pid'] != late['pid'] else 'closed'}", flush=True)
pl.terminate()
pl.wait(timeout=60)
