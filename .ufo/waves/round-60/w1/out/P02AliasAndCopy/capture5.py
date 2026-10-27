#!/usr/bin/env python3
"""Run 5: does a case-variant cp/create create a distinct entry or fold into the existing one?"""
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

PORT = int(sys.argv[1])
OUT = sys.argv[2]
OLLAMA = os.path.expanduser("~/.local/opt/ollama-v0.40.11/bin/ollama")
GGUF = os.path.expanduser("~/.cache/kama-shokunin/models/stories260K.gguf")
BASE = f"http://127.0.0.1:{PORT}"
CAP = os.path.join(OUT, "captures-case.jsonl")
seq = 0


def rec(kind, name, method, route, status=None, headers=None, body=b"", reading=""):
    global seq
    seq += 1
    h = {k.lower(): v for k, v in (headers or {}).items()}
    row = {"seq": seq, "kind": kind, "name": name, "method": method, "route": route, "status": status,
           "content_type": h.get("content-type"),
           "headers": {k: h[k] for k in ("content-type", "content-length", "date") if k in h},
           "body": body.decode("utf-8", "replace") if isinstance(body, bytes) else body,
           "body_sha256": hashlib.sha256(body if isinstance(body, bytes) else body.encode()).hexdigest(),
           "reading": reading}
    with open(CAP, "a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"{seq:02d} {kind:5s} {name:26s} {method:5s} {route:22s} {status}")
    return row


def call(name, method, route, payload=None, reading=""):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(BASE + route, data=data, method=method,
                                 headers={"Content-Type": "application/json"} if data else {})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            st, hd, body = r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        st, hd, body = e.code, dict(e.headers), e.read()
    return rec("http", name, method, route, st, hd, body, reading)


def cli(name, *args):
    p = subprocess.run([OLLAMA, *args], capture_output=True, text=True,
                       env={**os.environ, "OLLAMA_HOST": f"127.0.0.1:{PORT}"}, timeout=300)
    return rec("cli", name, "CLI", "ollama " + " ".join(args), None, {},
               json.dumps({"exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr}),
               f"exit {p.returncode}")


for _ in range(120):
    try:
        with urllib.request.urlopen(BASE + "/", timeout=2) as r:
            if r.status == 200:
                break
    except Exception:
        time.sleep(0.25)
else:
    sys.exit("not ready")

mf = os.path.join(os.path.dirname(CAP), "Modelfile-case.txt")
with open(mf, "w") as f:
    f.write(f"FROM {GGUF}\n")

cli("create-lower", "create", "caseprobe", "-f", mf)
cli("cp-lower-to-UPPER", "cp", "caseprobe", "CASEPROBE")
call("tags-after-upper-cp", "GET", "/api/tags", reading="one entry or two?")
cli("create-UPPER", "create", "UPPERFIRST", "-f", mf)
cli("cp-UPPER-to-lower", "cp", "UPPERFIRST", "upperfirst")
call("tags-after-lower-cp", "GET", "/api/tags", reading="one entry or two?")
call("show-CASEPROBE", "POST", "/api/show", {"model": "CASEPROBE"}, reading="uppercase query")
call("show-caseprobe", "POST", "/api/show", {"model": "caseprobe"}, reading="lowercase query")
call("show-UPPERFIRST", "POST", "/api/show", {"model": "UPPERFIRST"}, reading="uppercase query")
call("show-upperfirst", "POST", "/api/show", {"model": "upperfirst"}, reading="lowercase query")
call("generate-CASEPROBE", "POST", "/api/generate",
     {"model": "CASEPROBE", "prompt": "Once", "stream": False, "options": {"num_predict": 4}},
     reading="uppercase request echo")
call("ps", "GET", "/api/ps", reading="ps name for an uppercase-requested model")
cli("list", "list")
print("done")
