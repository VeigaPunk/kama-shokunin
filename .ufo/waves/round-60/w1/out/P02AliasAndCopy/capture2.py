#!/usr/bin/env python3
"""P02 run 2: alias/copy + case probe, headers captured, short generate via options.num_predict."""
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
NONCE = sys.argv[3]
OLLAMA = os.path.expanduser("~/.local/opt/ollama-v0.40.11/bin/ollama")
GGUF = os.path.expanduser("~/.cache/kama-shokunin/models/stories260K.gguf")
BASE = f"http://127.0.0.1:{PORT}"
NAME = f"kama-p02b-{NONCE}"
ALIAS = f"{NAME}-alias"
NAME2 = f"{NAME}-b"
UP = "P02UPPER"
CAPNAME = sys.argv[4] if len(sys.argv) > 4 else "captures-run2.jsonl"
CAP = os.path.join(OUT, CAPNAME)
seq = 0


def rec(kind, name, method, route, status=None, headers=None, body=b"", extra=None, reading=""):
    global seq
    seq += 1
    h = {k.lower(): v for k, v in (headers or {}).items()}
    row = {"seq": seq, "kind": kind, "name": name, "method": method, "route": route, "status": status,
           "content_type": h.get("content-type"),
           "headers": {k: h[k] for k in ("content-type", "content-length", "server", "date", "transfer-encoding") if k in h},
           "body": body.decode("utf-8", "replace") if isinstance(body, bytes) else body,
           "body_sha256": hashlib.sha256(body if isinstance(body, bytes) else body.encode()).hexdigest(),
           "reading": reading}
    if extra:
        row.update(extra)
    with open(CAP, "a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"{seq:02d} {kind:5s} {name:24s} {method:6s} {route:32s} {status} {row['content_type']}")
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
    return rec("http", name, method, route, st, hd, body, None, reading)


def cli(name, *args):
    p = subprocess.run([OLLAMA, *args], capture_output=True, text=True,
                       env={**os.environ, "OLLAMA_HOST": f"127.0.0.1:{PORT}"}, timeout=300)
    return rec("cli", name, "CLI", "ollama " + " ".join(args), None, {},
               json.dumps({"exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr}), None,
               f"exit {p.returncode}")


for _ in range(120):
    try:
        with urllib.request.urlopen(BASE + "/", timeout=2) as r:
            if r.status == 200:
                break
    except Exception:
        time.sleep(0.25)
else:
    sys.exit("server never became ready")

call("version", "GET", "/api/version", reading="server version string")
call("tags-empty", "GET", "/api/tags", reading="fresh store")

mf = os.path.join(os.path.dirname(CAP), "Modelfile-" + CAPNAME + ".txt")
with open(mf, "w") as f:
    f.write(f"FROM {GGUF}\n")

cli("create-NAME", "create", NAME, "-f", mf)
cli("cp-NAME-ALIAS", "cp", NAME, ALIAS)
cli("create-NAME2", "create", NAME2, "-f", mf)
cli("cp-NAME-UPPER", "cp", NAME, UP)
cli("cp-qualified-src", "cp", f"{NAME}:latest", f"{NAME}-q")
call("tags-all", "GET", "/api/tags", reading="five names, one digest")
call("v1-all", "GET", "/v1/models", reading="openai id forms")
cli("list", "list")

queries = [NAME, f"{NAME}:latest", ALIAS, f"{ALIAS}:latest", NAME2, f"{NAME2}:latest",
           UP, f"{UP}:latest", UP.lower(), f"{UP.lower()}:latest",
           NAME.upper(), "P02NoSuchModel", "kama-p02b-missing:latest"]
for q in queries:
    call("show:" + q, "POST", "/api/show", {"model": q}, reading=f"show {q}")

call("ps-before", "GET", "/api/ps", reading="no generation yet")
call("generate-ALIAS-unqualified", "POST", "/api/generate",
     {"model": ALIAS, "prompt": "Once", "stream": False, "options": {"num_predict": 4}},
     reading="request unqualified ALIAS, stream:false, options.num_predict=4")
call("ps-after-alias", "GET", "/api/ps", reading="ps after ALIAS generation")
call("generate-NAME2-unqualified", "POST", "/api/generate",
     {"model": NAME2, "prompt": "Once", "stream": False, "options": {"num_predict": 4}},
     reading="same digest, requested through NAME2")
call("ps-after-name2", "GET", "/api/ps", reading="ps after NAME2 generation")
call("generate-UPPER-unqualified", "POST", "/api/generate",
     {"model": UP.lower(), "prompt": "Once", "stream": False, "options": {"num_predict": 4}},
     reading="lowercase request for the uppercase alias")
call("ps-after-upper-lower", "GET", "/api/ps", reading="ps after lowercase request")
call("tags-after", "GET", "/api/tags", reading="tags after generations")
call("v1-after", "GET", "/v1/models", reading="v1 ids after generations")
cli("ps-cli", "ps")
cli("list-final", "list")
print(json.dumps({"name": NAME, "alias": ALIAS, "name2": NAME2, "upper": UP, "port": PORT}))
