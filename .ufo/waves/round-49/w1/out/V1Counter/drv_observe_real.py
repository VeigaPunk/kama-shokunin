#!/usr/bin/env python3
"""O1: run the real frozen b11909 llama-server on loopback with the frozen model,
exercise exactly the counter's observe() comparisons (/tokenize with_pieces,
/detokenize), record the empirical JSON shapes."""
import importlib.util
import hashlib
import json
import os
import secrets
import signal
import socket
import subprocess
import sys
import time
import urllib.request

S = "/fast/scratch/hyaku/kama-r49/V1Counter"
OUT = open(f"{S}/out/observe_real.txt", "w")
MODEL_URL = ("https://huggingface.co/ggml-org/models-moved/resolve/"
             "499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf")
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
SERVER = "/home/vgpnk/.local/opt/llama-b11909/llama-server"

spec = importlib.util.spec_from_file_location(
    "r49c1", f"{S}/lane/tools/round49-replay-witness-audit.py")
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)

def w(s=""):
    print(s)
    OUT.write(s + "\n")

def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

model = f"{S}/stories260K.gguf"
if not os.path.isfile(model):
    w("downloading model...")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(MODEL_URL, timeout=120) as r, open(model, "wb") as fh:
        fh.write(r.read())
    w(f"downloaded sha256={sha_file(model)}")
    assert sha_file(model) == MODEL_SHA, "model digest mismatch"
else:
    w(f"model already present sha256={sha_file(model)}")

vocab = cc.gguf_tokens(model)
w(f"vocab size={len(vocab)} (gguf_tokens)")

# pick a free port
s = socket.socket()
s.bind(("127.0.0.1", 0))
port = s.getsockname()[1]
s.close()
w(f"using port {port}")

logp = f"{S}/server.log"
proc = subprocess.Popen(
    [SERVER, "-m", model, "--alias", "kama-witness-probe",
     "--host", "127.0.0.1", "--port", str(port),
     "-c", "256", "-t", "1", "--no-webui", "--offline"],
    stdout=open(logp, "wb"), stderr=subprocess.STDOUT,
    start_new_session=True)
try:
    # wait for /health 200
    ok = False
    for _ in range(300):
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/health")
            with urllib.request.urlopen(req, timeout=2) as r:
                if r.status == 200:
                    ok = True
                    break
        except Exception:
            pass
        time.sleep(0.3)
    w(f"health ready={ok} (pid={proc.pid})")

    nonce = f"kama witness {secrets.token_hex(8)}"
    w(f"nonce={nonce!r}")

    def post(path, body):
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
                                     data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"},
                                     method="POST")
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(req, timeout=20) as r:
            return json.loads(r.read(1 << 20))

    tk = post("/tokenize", {"content": nonce, "with_pieces": True})["tokens"]
    w(f"tokenize returned {len(tk)} tokens; shapes:")
    for t in tk[:5]:
        w(f"  {t!r}")
    ids = [t["id"] for t in tk]
    bad = [t for t in tk if not (isinstance(t.get("piece"), str)
                                 and 0 <= t["id"] < len(vocab)
                                 and vocab[t["id"]].replace("\u2581", " ") == t["piece"])]
    w(f"counter bad-list (piece comparisons failing): {bad[:3]}")
    dt = post("/detokenize", {"tokens": ids})["content"]
    w(f"detokenize content={dt!r}")
    w(f"dt == nonce? {dt == nonce}; dt == ' '+nonce? {dt == ' ' + nonce}")
    # byte-piece experiment: non-ASCII content, e.g. 'á' (README example)
    tk2 = post("/tokenize", {"content": "á", "with_pieces": True})["tokens"]
    w("non-ASCII 'á' pieces (README says byte lists):")
    for t in tk2:
        w(f"  {t!r}  isinstance-str={isinstance(t.get('piece'), str)}")
finally:
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()
    w(f"server exit rc={proc.returncode}")

# port should refuse now
s2 = socket.socket()
s2.settimeout(2)
try:
    s2.connect(("127.0.0.1", port))
    w("port STILL accepts (unexpected)")
except OSError:
    w("port refuses connections after teardown (expected)")
finally:
    s2.close()

OUT.close()
print("DONE")
