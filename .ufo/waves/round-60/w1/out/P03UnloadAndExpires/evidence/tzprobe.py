#!/usr/bin/env python3
"""Second lane-owned run: does expires_at render in the server process TZ?"""
import datetime as dt
import hashlib
import http.client
import json
import os
import subprocess
import sys
import time

PORT = int(sys.argv[1])
S = sys.argv[2]
NAME = sys.argv[3]
TZ = sys.argv[4]
BIN = os.path.expanduser("~/.local/opt/ollama-v0.40.11/bin/ollama")
out = {"tz": TZ, "captures": []}


def call(label, method, path, body=None):
    t0 = time.time_ns()
    c = http.client.HTTPConnection("127.0.0.1", PORT, timeout=120)
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json"} if data else {}
    c.request(method, path, body=data, headers=h)
    r = c.getresponse()
    raw = r.read()
    t1 = time.time_ns()
    hs = {k.lower(): v for k, v in r.getheaders()}
    c.close()
    rec = {"label": label, "method": method, "route": path, "status": r.status,
           "content_type": hs.get("content-type"), "req_body": body,
           "body": raw.decode("utf-8", "replace"), "body_sha256": hashlib.sha256(raw).hexdigest(),
           "client_ms": round((t1 - t0) / 1e6, 3),
           "t_start_utc": dt.datetime.fromtimestamp(t0 / 1e9, dt.timezone.utc).isoformat()}
    out["captures"].append(rec)
    return rec


g = call("gen-ka20", "POST", "/api/generate",
         {"model": NAME, "prompt": "Hi", "stream": False, "keep_alive": "20s"})
gb = json.loads(g["body"])
ps = call("ps", "GET", "/api/ps")
m = (json.loads(ps["body"]).get("models") or [{}])[0]
env = {"PATH": "/usr/bin:/bin", "HOME": os.path.join(S, "home"), "OLLAMA_HOST": f"127.0.0.1:{PORT}"}
st = subprocess.run([BIN, "stop", NAME], capture_output=True, env=env, timeout=60)
tags = call("tags-after-stop", "GET", "/api/tags")
ps2 = call("ps-after-stop", "GET", "/api/ps")
out["obsv"] = {
    "expires_at_raw": m.get("expires_at"),
    "created_at_raw": gb.get("created_at"),
    "ps_created_plus_20s_client_check": None,
    "stop_exit": st.returncode,
    "tags_names_after_stop": [x.get("name") for x in json.loads(tags["body"]).get("models", [])],
    "tags_digests_after_stop": [x.get("digest") for x in json.loads(tags["body"]).get("models", [])],
    "ps_after_stop_models": json.loads(ps2["body"]).get("models"),
    "server_tz_seen": m.get("expires_at"),
}
print(json.dumps(out, indent=1, sort_keys=True))
