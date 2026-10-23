#!/usr/bin/python3
"""Round-28 DataG13 probe #3: map single-token strings, then run one clean
preserved_tokens row request whose stored value is sorted and de-duplicated."""
import hashlib
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

HOST = "127.0.0.1"
PORT = 48213
OUT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/DataG13"
LOG = "/fast/scratch/hyaku/kama-r28/w1/DataG13/server3.log"
BIN = os.path.expanduser("~/.local/opt/llama-b11755/llama-server")
MODEL = os.path.expanduser("~/.cache/kama-shokunin/models/stories260K.gguf")
BASE = {"prompt": "Once upon a time", "n_predict": 1}
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
CANDIDATES = ["Once", "once", " once", "the", " the", "time", " time", "upon",
              " upon", "a", " a", "and", " and", " gone"]


def http(path, body=None, timeout=60.0):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(f"http://{HOST}:{PORT}{path}", data=data,
                                 headers={"Content-Type": "application/json"},
                                 method="POST" if body is not None else "GET")
    try:
        with OPENER.open(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:  # noqa: BLE001
        return -1, repr(e).encode()


def post(tag, body, store):
    st, raw = http("/completion", body)
    path = os.path.join(OUT, f"resp-{tag}.json")
    with open(path, "wb") as f:
        f.write(raw)
    doc = json.loads(raw) if raw[:1] == b"{" else None
    gs = doc.get("generation_settings") if isinstance(doc, dict) else None
    msg = None
    if isinstance(doc, dict) and isinstance(doc.get("error"), dict):
        msg = doc["error"].get("message")
    rec = {"tag": tag, "request": body, "status": st,
           "response_sha256": hashlib.sha256(raw).hexdigest(), "body_file": path,
           "message": msg,
           "preserved_tokens": None if not isinstance(gs, dict) else gs.get("preserved_tokens")}
    store.append(rec)
    return rec


def main():
    os.makedirs(OUT, exist_ok=True)
    dfd = open(LOG, "wb")
    proc = subprocess.Popen(
        [BIN, "-m", MODEL, "--host", HOST, "--port", str(PORT)],
        stdout=dfd, stderr=subprocess.STDOUT, start_new_session=True,
        cwd="/fast/scratch/hyaku/kama-r28/w1/DataG13")
    results = []
    mapping = {}
    try:
        deadline = time.time() + 120
        while time.time() < deadline:
            st, _ = http("/health", timeout=5.0)
            if st == 200:
                break
            time.sleep(0.5)
        else:
            print(json.dumps({"error": "not ready"}))
            return 1
        for i, s in enumerate(CANDIDATES):
            rec = post(f"m{i:02d}", BASE | {"preserved_tokens": [s]}, results)
            ids = rec["preserved_tokens"]
            mapping[s] = ids
            print("map", json.dumps(s), rec["status"], ids, flush=True)
        singles = {s: ids[0] for s, ids in mapping.items() if isinstance(ids, list) and len(ids) == 1}
        if len(singles) >= 2:
            ranked = sorted(singles.items(), key=lambda kv: kv[1])
            low_s, low_id = ranked[0]
            high_s, high_id = ranked[-1]
            chosen = [high_s, high_s, low_s]
            rec = post("r01-final", BASE | {"preserved_tokens": chosen}, results)
            print("final", json.dumps(chosen), rec["status"], rec["preserved_tokens"],
                  "expected", [low_id, high_id], flush=True)
            print("sorted_ascending", rec["preserved_tokens"] == sorted(rec["preserved_tokens"]), flush=True)
        else:
            print("fewer than two single-token candidates", json.dumps(singles), flush=True)
    finally:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait(timeout=10)
        dfd.close()
    time.sleep(0.5)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        closed = s.connect_ex((HOST, PORT)) != 0
    with open(os.path.join(OUT, "probe-results-3.json"), "w", encoding="utf-8") as f:
        json.dump({"port_closed": closed, "mapping": mapping, "probes": results}, f, indent=1)
        f.write("\n")
    print("port_closed", closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
