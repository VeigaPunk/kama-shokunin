"""Sen1Witness run A: real witnessed replay held open; probe exposure from another
uid, then SIGTERM the live tool during the hold and watch teardown.

Uses the frozen lane tools from the read-only clone; all state in $S.
"""
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request

S = "/fast/scratch/hyaku/kama-r49/Sen1Witness"
TREE = os.path.join(S, "lane")
RECEIPT = os.path.join(TREE, ".ufo/waves/round-48/c2/live/receipt-1.json")
REPLAY = os.path.join(TREE, "tools/kama-live-replay.py")
wd = os.path.join(S, "A/wd")
work = os.path.join(S, "A/work")
out = os.path.join(S, "A/replay-A.json")
os.makedirs(wd, exist_ok=True)
os.makedirs(work, exist_ok=True)
env = dict(os.environ, HOME=os.path.join(S, "A/home"), XDG_CACHE_HOME=os.path.join(S, "A/cache"),
           TMPDIR=os.path.join(S, "A/tmp"))
for k in ("HOME", "XDG_CACHE_HOME", "TMPDIR"):
    os.makedirs(env[k], exist_ok=True)

live = open(os.path.join(S, "A/replay.log"), "wb")
t0 = time.monotonic()
p = subprocess.Popen([sys.executable, REPLAY, "--receipt", RECEIPT, "--work", work, "--out", out,
                      "--witness-dir", wd, "--witness-timeout", "45"],
                     env=env, stdout=live, stderr=live)
print(f"replay pid {p.pid}", flush=True)

ready = None
while time.monotonic() - t0 < 600 and p.poll() is None:
    rp = os.path.join(wd, "ready.json")
    if os.path.exists(rp):
        try:
            ready = json.load(open(rp))
            break
        except (OSError, ValueError):
            pass
    time.sleep(0.2)
print(f"ready after {time.monotonic()-t0:.1f}s: {ready}", flush=True)
if ready is None:
    print(f"NO READY; replay exit {p.poll()}; log tail:", flush=True)
    print(open(os.path.join(S, "A/replay.log"), errors="replace").read()[-2000:], flush=True)
    sys.exit(1)

pid, port = ready["pid"], ready["port"]
st = os.stat(os.path.join(wd, "ready.json"))
print(f"ready.json mode {oct(st.st_mode & 0o777)} uid {st.st_uid}", flush=True)

ss = subprocess.run(["ss", "-ltnpH", f"sport = :{port}"], capture_output=True, text=True)
print("ss:", ss.stdout.strip(), flush=True)
print("live pid cmdline:", open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ")[:200], flush=True)
print("is the ready pid the server child? comm:", open(f"/proc/{pid}/comm").read().strip(), flush=True)

# the replay's direct child (the live tool)
kids = subprocess.run(["pgrep", "-P", str(p.pid), "-a"], capture_output=True, text=True).stdout
print("replay children:", kids.strip()[:300], flush=True)
livetool_pids = [int(l.split()[0]) for l in kids.splitlines() if "kama-llamacpp-live" in l]
print("live tool pids:", livetool_pids, flush=True)

# exposure from another uid
for path, body in (("/props", None), ("/tokenize", {"content": "kama witness probe", "with_pieces": True})):
    code = ("import json,sys,urllib.request as u;"
            f"r=u.urlopen(u.Request('http://127.0.0.1:{port}{path}',"
            + (f"data=json.dumps({body!r}).encode(),headers={{'Content-Type':'application/json'}}," if body else "")
            + "),timeout=10);print(r.status, r.read()[:120])")
    q = subprocess.run(["sudo", "-n", "-u", "nobody", sys.executable, "-c", code],
                       capture_output=True, text=True, timeout=60)
    print(f"as nobody {path}: rc={q.returncode} out={q.stdout.strip()[:200]} err={q.stderr.strip()[:120]}", flush=True)

# SIGTERM the live tool during the hold
print(f"SIGTERM live tool {livetool_pids}", flush=True)
for lp in livetool_pids:
    os.kill(lp, signal.SIGTERM)
for i in range(60):
    alive = os.path.exists(f"/proc/{pid}")
    refuse = subprocess.run([sys.executable, "-c",
                             f"import socket;s=socket.socket();\n"
                             f"try: s.connect(('127.0.0.1',{port}));print('OPEN')\n"
                             f"except OSError as e: print('CLOSED',type(e).__name__)"],
                            capture_output=True, text=True).stdout.strip()
    if not alive or "CLOSED" in refuse:
        print(f"after {i*0.25:.2f}s: server pid alive={alive} port={refuse}", flush=True)
        if not alive:
            break
    time.sleep(0.25)
code = p.wait(timeout=180)
print(f"replay exit {code} after {time.monotonic()-t0:.1f}s", flush=True)
print("replay out json:", json.dumps(json.load(open(out)) if os.path.exists(out) else None)[:400], flush=True)
rr = os.path.join(work, "rerun-receipt.json")
if os.path.exists(rr):
    d = json.load(open(rr))
    print("rerun witness:", d.get("witness"), "outcome:", d.get("outcome"),
          "setup_error:", d.get("setup_error"), flush=True)
print("wd now:", sorted(os.listdir(wd)), flush=True)
live.close()
