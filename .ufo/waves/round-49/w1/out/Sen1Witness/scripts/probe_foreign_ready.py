"""Sen1Witness: a ready.json already in the witness dir is what a poller sees,
and it passes every observation the C1 counter makes (exe sha, listener inode,
-m hash, nonce round-trip) while the replay's own server is a different process."""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time

S = os.environ.get("SEN1_S", "/fast/scratch/hyaku/kama-r49/Sen1Witness")
LANE = os.path.join(S, "lane")
SRV = os.path.join(S, "F/work/server/llama-b11909/llama-server")
MDL = os.path.join(S, "F/work/download/stories260K.gguf")
SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
FROZEN = "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0"
P, P2 = os.path.join(S, "H/foreign-wd"), os.path.join(S, "H/replay-wd")
for x in (P, P2):
    shutil.rmtree(x, ignore_errors=True)
    os.makedirs(x)
env = dict(os.environ, TMPDIR=os.path.join(S, "H/tmp"), HOME=os.path.join(S, "H/home"),
           XDG_CACHE_HOME=os.path.join(S, "H/cache"))
for k in ("TMPDIR", "HOME", "XDG_CACHE_HOME"):
    os.makedirs(env[k], exist_ok=True)
log = open(os.path.join(S, "H/run.log"), "wb")

# a server that is NOT the replay's child, kept alive by a separate live-tool run
t0 = time.monotonic()
pl = subprocess.Popen([sys.executable, os.path.join(LANE, "tools/kama-llamacpp-live.py"),
                       "--server", SRV, "--model", MDL, "--model-sha256", SHA, "--alias", "kama-r48-live",
                       "--ctx", "256", "--threads", "1", "--out", os.path.join(S, "H/foreign-receipt.json"),
                       "--witness-dir", P, "--witness-timeout", "inf"], env=env, stdout=log, stderr=log)
ready = None
while time.monotonic() - t0 < 60 and pl.poll() is None:
    rp = os.path.join(P, "ready.json")
    if os.path.exists(rp):
        try:
            ready = json.load(open(rp))
            break
        except (OSError, ValueError):
            pass
    time.sleep(0.1)
print(f"H: foreign server {ready}", flush=True)
shutil.copy(os.path.join(P, "ready.json"), os.path.join(P2, "ready.json"))
pre = json.load(open(os.path.join(P2, "ready.json")))
print(f"H: pre-planted ready.json in the replay's witness dir: pid={pre['pid']} port={pre['port']}", flush=True)

# the replay that is supposed to be witnessed
wrk = os.path.join(S, "H/work")
os.makedirs(wrk, exist_ok=True)
outj = os.path.join(S, "H/replay.json")
p = subprocess.Popen([sys.executable, os.path.join(LANE, "tools/kama-live-replay.py"),
                      "--receipt", os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-1.json"),
                      "--work", wrk, "--out", outj, "--witness-dir", P2, "--witness-timeout", "4"],
                     env=env, stdout=log, stderr=log)
t0 = time.monotonic()
seen = None
while time.monotonic() - t0 < 20:
    try:
        seen = json.load(open(os.path.join(P2, "ready.json")))
    except (OSError, ValueError):
        pass
    if seen:
        break
    time.sleep(0.05)
print(f"H: a poller's first read of ready.json during the replay: +{time.monotonic()-t0:.2f}s "
      f"pid={seen['pid']} port={seen['port']} same_as_foreign={seen == pre}", flush=True)
# rerun what the counter checks on that pid/port
import urllib.request
pid, port = pre["pid"], pre["port"]


def post(path, body):
    q = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(body).encode(),
                               headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(q, timeout=10) as r:
        return json.loads(r.read())


h = hashlib.sha256(open(f"/proc/{pid}/exe", "rb").read()).hexdigest()
print(f"H: exe sha == frozen b11909: {h == FROZEN}", flush=True)
print("H: listeners on the announced port: " +
      subprocess.run(["ss", "-ltnpH", f"sport = :{port}"], capture_output=True, text=True).stdout.strip(),
      flush=True)
tk = post("/tokenize", {"content": "kama witness deadbeefdeadbeef", "with_pieces": True})["tokens"]
print(f"H: tokenize pieces {[t['piece'] for t in tk][:6]}", flush=True)
print(f"H: detokenize {post('/detokenize', {'tokens': [t['id'] for t in tk]})['content']!r}", flush=True)
code = p.wait(timeout=120)
print(f"H: replay exit {code}", flush=True)
j = json.load(open(outj)) if os.path.exists(outj) else {}
print(f"H: replay match={j.get('match')} mismatches={j.get('mismatches')}", flush=True)
rr = os.path.join(wrk, "rerun-receipt.json")
d = json.load(open(rr)) if os.path.exists(rr) else {}
print(f"H: rerun witness={d.get('witness')}", flush=True)
print(f"H: the replay's own server pid was {d.get('witness', {}).get('pid')}, observed pid was {pid} "
      f"-> bound={d.get('witness', {}).get('pid') == pid}", flush=True)
print(f"H: witness dir now {sorted(os.listdir(P2))}", flush=True)
pl.terminate()
pl.wait(timeout=60)
print(f"H: foreign server alive after SIGTERM: {os.path.exists(f'/proc/{pid}')}", flush=True)
log.close()
