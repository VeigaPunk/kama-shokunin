"""Sen1Witness: exercise the proposed hardening (patch/new/) against the same
cases that fail on the frozen tip. Each case prints PASS/FAIL and the observed
token, so the patch is validated rather than asserted."""
import json
import os
import shutil
import socket
import stat
import subprocess
import sys
import time

S = os.environ.get("SEN1_S", "/fast/scratch/hyaku/kama-r49/Sen1Witness")
PATCH = os.path.join(S, "patch/wt/tools")
SRV = os.path.join(S, "F/work/server/llama-b11909/llama-server")
MDL = os.path.join(S, "F/work/download/stories260K.gguf")
SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
LIVE = os.path.join(PATCH, "kama-llamacpp-live.py")
REPLAY = os.path.join(PATCH, "kama-live-replay.py")
BASE = os.path.join(S, "patchtest")
shutil.rmtree(BASE, ignore_errors=True)
os.makedirs(BASE)
results = []


def run_live(wd, timeout, extra_env=None, wait=40):
    env = dict(os.environ, TMPDIR=os.path.join(BASE, "tmp"))
    os.makedirs(env["TMPDIR"], exist_ok=True)
    if extra_env:
        env.update(extra_env)
    out = os.path.join(BASE, "receipt.json")
    log = open(os.path.join(BASE, "live.log"), "wb")
    p = subprocess.Popen([sys.executable, LIVE, "--server", SRV, "--model", MDL, "--model-sha256", SHA,
                          "--alias", "kama-r48-live", "--ctx", "256", "--threads", "1", "--out", out,
                          "--witness-dir", wd, "--witness-timeout", str(timeout)],
                         env=env, stdout=log, stderr=log)
    return p, log, out


def verdict(name, ok, detail):
    results.append((name, ok, detail))
    print(f"{name}: {'PASS' if ok else 'FAIL'} {detail}", flush=True)


# 1. world-writable witness dir is refused before anything runs
d = os.path.join(BASE, "world"); os.makedirs(d); os.chmod(d, 0o777)
q = subprocess.run([sys.executable, LIVE, "--server", SRV, "--model", MDL, "--model-sha256", SHA,
                    "--witness-dir", d, "--witness-timeout", "5"],
                   capture_output=True, text=True)
verdict("1-world-writable-refused", q.returncode == 2 and "group-or-other-writable" in q.stderr,
        f"rc={q.returncode} err={q.stderr.strip().splitlines()[-1][:110]}")

# 2. a planted symlink at the old temp name is refused
d = os.path.join(BASE, "symlink"); os.makedirs(d, 0o755)
victim = os.path.join(d, "victim.txt")
open(victim, "w").write("KEEP\n")
os.symlink(victim, os.path.join(d, "ready.json.tmp"))
q = subprocess.run([sys.executable, LIVE, "--server", SRV, "--model", MDL, "--model-sha256", SHA,
                    "--witness-dir", d, "--witness-timeout", "5"], capture_output=True, text=True)
verdict("2-planted-tmp-symlink-refused", q.returncode == 2 and "stale:ready.json.tmp" in q.stderr
        and open(victim).read() == "KEEP\n",
        f"rc={q.returncode} victim={open(victim).read().strip()!r}")

# 3. a stale ready.json in a reused dir is refused
d = os.path.join(BASE, "stale"); os.makedirs(d, 0o755)
json.dump({"schema": "kama-live-witness/v1", "port": 1, "pid": 1}, open(os.path.join(d, "ready.json"), "w"))
q = subprocess.run([sys.executable, LIVE, "--server", SRV, "--model", MDL, "--model-sha256", SHA,
                    "--witness-dir", d, "--witness-timeout", "5"], capture_output=True, text=True)
verdict("3-stale-ready-refused", q.returncode == 2 and "stale:ready.json" in q.stderr,
        f"rc={q.returncode}")

# 4. a planted release is refused
d = os.path.join(BASE, "release"); os.makedirs(d, 0o755)
open(os.path.join(d, "release"), "w").write("stale\n")
q = subprocess.run([sys.executable, LIVE, "--server", SRV, "--model", MDL, "--model-sha256", SHA,
                    "--witness-dir", d, "--witness-timeout", "5"], capture_output=True, text=True)
verdict("4-planted-release-refused", q.returncode == 2 and "stale:release" in q.stderr, f"rc={q.returncode}")

# 5. non-finite timeout is refused
d = os.path.join(BASE, "inf"); os.makedirs(d, 0o755)
q = subprocess.run([sys.executable, LIVE, "--server", SRV, "--model", MDL, "--model-sha256", SHA,
                    "--witness-dir", d, "--witness-timeout", "inf"], capture_output=True, text=True)
verdict("5-inf-refused", q.returncode == 2 and "finite" in q.stderr, f"rc={q.returncode}")

# 6. a normal hold still works; ready.json is 0600; a FIFO release does not release
d = os.path.join(BASE, "hold"); os.makedirs(d, 0o755)
p, log, out = run_live(d, 3)
ready = None
t0 = time.monotonic()
while time.monotonic() - t0 < 60 and p.poll() is None:
    rp = os.path.join(d, "ready.json")
    if os.path.exists(rp):
        ready = json.load(open(rp))
        break
    time.sleep(0.05)
mode = oct(os.stat(os.path.join(d, "ready.json")).st_mode & 0o777) if ready else None
if ready:
    os.mkfifo(os.path.join(d, "release"))
code = p.wait(timeout=120)
r = json.load(open(out)) if os.path.exists(out) else {}
w = r.get("witness") or {}
verdict("6-hold-0600-fifo-ignored", ready is not None and mode == "0o600" and w.get("released") is False
        and w.get("waited_ms", 0) >= 2900 and w.get("timeout_s") == 3.0,
        f"ready={ready is not None} mode={mode} witness={w}")
verdict("6b-hold-outcome-pass", r.get("outcome") == "pass", f"outcome={r.get('outcome')}")
log.close()

# 7. a regular release created after the announcement releases it
d = os.path.join(BASE, "hold2"); os.makedirs(d, 0o755)
p, log, out = run_live(d, 30)
ready = None
t0 = time.monotonic()
while time.monotonic() - t0 < 60 and p.poll() is None:
    rp = os.path.join(d, "ready.json")
    if os.path.exists(rp):
        ready = json.load(open(rp))
        break
    time.sleep(0.05)
if ready:
    time.sleep(0.3)
    open(os.path.join(d, "release"), "w").write("released\n")
code = p.wait(timeout=120)
r = json.load(open(out)) if os.path.exists(out) else {}
w = r.get("witness") or {}
verdict("7-fresh-release-releases", w.get("released") is True and w.get("waited_ms", 0) >= 300,
        f"witness={w}")
log.close()

# 8. the patched replay refuses a non-finite timeout without spawning anything
wrk = os.path.join(BASE, "replaywork")
q = subprocess.run([sys.executable, REPLAY,
                    "--receipt", os.path.join(S, "lane/.ufo/waves/round-48/c2/live/receipt-1.json"),
                    "--work", wrk, "--out", os.path.join(BASE, "replay.json"),
                    "--witness-dir", os.path.join(BASE, "hold2"), "--witness-timeout", "inf"],
                   capture_output=True, text=True, timeout=120)
tokens = "witness-timeout-out-of-range" in q.stdout or "witness-timeout-out-of-range" in q.stderr
spawned = os.path.exists(os.path.join(wrk, "download"))
verdict("8-replay-inf-refused", q.returncode == 2 and tokens and not spawned,
        f"rc={q.returncode} spawned_download={spawned} out={q.stdout.strip()[:160]}")

print("\n%d/%d cases pass" % (sum(1 for _, ok, _ in results if ok), len(results)))
sys.exit(0 if all(ok for _, ok, _ in results) else 1)
