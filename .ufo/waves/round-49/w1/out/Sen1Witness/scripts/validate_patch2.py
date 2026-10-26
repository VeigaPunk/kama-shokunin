"""Sen1Witness: validate the r50 proposal (wt3) on top of the current working tree."""
import json
import os
import shutil
import socket
import subprocess
import sys
import time

S = os.environ.get("SEN1_S", "/fast/scratch/hyaku/kama-r49/Sen1Witness")
WT = os.environ.get("SEN1_WT", os.path.join(S, "wt3/tools"))
LIVE = os.path.join(WT, "kama-llamacpp-live.py")
REPLAY = os.path.join(WT, "kama-live-replay.py")
RECEIPT = os.path.join(S, "wt2/.ufo/waves/round-48/c2/live/receipt-1.json")
SRV = os.path.join(S, "F/work/server/llama-b11909/llama-server")
MDL = os.path.join(S, "F/work/download/stories260K.gguf")
SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
BASE = os.path.join(S, "pt2")
shutil.rmtree(BASE, ignore_errors=True)
res = []


def mk(name):
    d = os.path.join(BASE, name)
    os.makedirs(os.path.join(d, "wd"), 0o755)
    for x in ("tmp", "work"):
        os.makedirs(os.path.join(d, x), exist_ok=True)
    return d, dict(os.environ, TMPDIR=os.path.join(d, "tmp"))


def verdict(name, ok, detail):
    res.append(ok)
    print(f"{name}: {'PASS' if ok else 'FAIL'} {detail}", flush=True)


def live(env, wd, timeout, out):
    log = open(os.path.join(os.path.dirname(wd), "live.log"), "wb")
    p = subprocess.Popen([sys.executable, LIVE, "--server", SRV, "--model", MDL, "--model-sha256", SHA,
                          "--alias", "kama-r48-live", "--ctx", "256", "--threads", "1", "--out", out,
                          "--witness-dir", wd, "--witness-timeout", str(timeout)],
                         env=env, stdout=log, stderr=log)
    return p, log


def wait_ready(wd, p, limit=60):
    t0 = time.monotonic()
    while time.monotonic() - t0 < limit and p.poll() is None:
        rp = os.path.join(wd, "ready.json")
        if os.path.exists(rp):
            try:
                return json.load(open(rp))
            except (OSError, ValueError):
                pass
        time.sleep(0.02)
    return None


# V1: a release created before the announcement is ignored
d, env = mk("v1")
out = os.path.join(d, "receipt.json")
p, log = live(env, os.path.join(d, "wd"), 3, out)
time.sleep(0.15)  # still before ready.json: the server is loading
open(os.path.join(d, "wd/release"), "w").write("early\n")
r = wait_ready(os.path.join(d, "wd"), p)
p.wait(timeout=120)
rec = json.load(open(out)) if os.path.exists(out) else {}
w = rec.get("witness") or {}
verdict("V1-early-release-ignored", r is not None and w.get("released") is False
        and w.get("waited_ms", 0) >= 2800,
        f"ready={r is not None} witness={w}")
log.close()

# V2: a release created after the announcement releases promptly; nonce is recorded
d, env = mk("v2")
out = os.path.join(d, "receipt.json")
p, log = live(env, os.path.join(d, "wd"), 30, out)
r = wait_ready(os.path.join(d, "wd"), p)
time.sleep(0.3)
open(os.path.join(d, "wd/release"), "w").write("late\n")
p.wait(timeout=120)
rec = json.load(open(out)) if os.path.exists(out) else {}
w = rec.get("witness") or {}
mode = oct(os.stat(os.path.join(d, "wd/release")).st_mode & 0o777)
ready_mode = None
verdict("V2-late-release-releases", r is not None and w.get("released") is True
        and 250 <= w.get("waited_ms", 0) < 5000 and w.get("nonce") == (r or {}).get("nonce")
        and rec.get("outcome") == "pass",
        f"witness={w} ready_nonce={(r or {}).get('nonce')} outcome={rec.get('outcome')}")
# ready.json mode is checked on a still-open hold in V3
log.close()

# V3: ready.json is 0600 while held
d, env = mk("v3")
out = os.path.join(d, "receipt.json")
p, log = live(env, os.path.join(d, "wd"), 2, out)
r = wait_ready(os.path.join(d, "wd"), p)
mode = oct(os.stat(os.path.join(d, "wd/ready.json")).st_mode & 0o777) if r else None
p.wait(timeout=120)
verdict("V3-ready-0600", mode == "0o600", f"mode={mode}")
log.close()

# V4: non-finite / huge timeouts refused by both tools
d, env = mk("v4")
q = subprocess.run([sys.executable, LIVE, "--server", SRV, "--model", MDL, "--model-sha256", SHA,
                    "--witness-dir", os.path.join(d, "wd"), "--witness-timeout", "inf"],
                   capture_output=True, text=True, timeout=60)
q2 = subprocess.run([sys.executable, REPLAY, "--receipt", RECEIPT, "--work", os.path.join(d, "work"),
                     "--out", os.path.join(d, "replay.json"), "--witness-dir", os.path.join(d, "wd"),
                     "--witness-timeout", "inf"], capture_output=True, text=True, timeout=120)
spawned = os.path.exists(os.path.join(d, "work/download"))
msg1 = q.stdout + q.stderr
msg2 = q2.stdout + q2.stderr
ok1 = q.returncode == 2 and ("finite" in msg1 or "<= 3600" in msg1)
ok2 = q2.returncode == 2 and ("witness-timeout-out-of-range" in msg2 or "<= 3600" in msg2)
verdict("V4-inf-refused", ok1 and ok2 and not spawned,
        f"live_rc={q.returncode} replay_rc={q2.returncode} downloaded={spawned}")

print(f"\n{sum(1 for x in res if x)}/{len(res)} cases pass")
sys.exit(0 if all(res) else 1)
