#!/usr/bin/python3
"""Round-28 DataG13 probe #4: repeat the final preserved_tokens request twice to show
determinism, then confirm the port is closed with ss."""
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
LOG = "/fast/scratch/hyaku/kama-r28/w1/DataG13/server4.log"
BIN = os.path.expanduser("~/.local/opt/llama-b11755/llama-server")
MODEL = os.path.expanduser("~/.cache/kama-shokunin/models/stories260K.gguf")
BODY = {"prompt": "Once upon a time", "n_predict": 1,
        "preserved_tokens": ["upon", "upon", "a"]}
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


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


def main():
    dfd = open(LOG, "wb")
    proc = subprocess.Popen(
        [BIN, "-m", MODEL, "--host", HOST, "--port", str(PORT)],
        stdout=dfd, stderr=subprocess.STDOUT, start_new_session=True,
        cwd="/fast/scratch/hyaku/kama-r28/w1/DataG13")
    out = []
    try:
        deadline = time.time() + 120
        while time.time() < deadline:
            st, _ = http("/health", timeout=5.0)
            if st == 200:
                break
            time.sleep(0.5)
        else:
            print("not ready")
            return 1
        for i in (1, 2):
            st, raw = http("/completion", BODY)
            path = os.path.join(OUT, f"resp-r0{i}-final.json")
            with open(path, "wb") as f:
                f.write(raw)
            doc = json.loads(raw)
            out.append({"tag": f"r0{i}", "status": st,
                        "response_sha256": hashlib.sha256(raw).hexdigest(),
                        "preserved_tokens": doc["generation_settings"]["preserved_tokens"],
                        "content": doc.get("content")})
            print(f"r0{i}", st, out[-1]["preserved_tokens"], out[-1]["response_sha256"][:16], flush=True)
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
    with open(os.path.join(OUT, "probe-results-4.json"), "w", encoding="utf-8") as f:
        json.dump({"port_closed": closed, "probes": out}, f, indent=1)
        f.write("\n")
    print("port_closed", closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
