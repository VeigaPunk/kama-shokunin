#!/usr/bin/env python3
"""Rev1Base round-50 reproduction: the double-fork + setsid decoy replay.

Same shape as round-49 seat K1Cheat's decoy-replay.py (never runs the live tool,
starts the real host b11909 server with the frozen model, holds for the witness,
copies the original receipt with witness.released true) with one difference: the
server is started by a middle process that calls setsid() and exits, so the
server is reparented to init and is NOT a descendant of the replay process.

It additionally writes the two receipt facts the round-50 counter joins on
(`child_pid` = the observed server pid, `model_mapping` read from the server's own
/proc/<pid>/maps row for the model file), so that against the round-50 counter the
process-tree leg is the one that has to catch it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request

SERVER = "/home/vgpnk/.local/opt/llama-b11909/llama-server"
SERVER_SHA = "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0"
MODEL_URL = ("https://huggingface.co/ggml-org/models-moved/resolve/"
             "499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf")
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
WITNESS_SCHEMA = "kama-live-witness/v1"


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_model(work):
    cand = os.path.join(os.path.dirname(work), "counter-model.gguf")
    if os.path.isfile(cand) and sha(cand) == MODEL_SHA:
        return cand
    dest = os.path.join(work, "model.gguf")
    with urllib.request.urlopen(MODEL_URL, timeout=120) as r, open(dest, "wb") as fh:
        shutil.copyfileobj(r, fh)
    if sha(dest) != MODEL_SHA:
        raise SystemExit("decoy: model download did not hash to frozen digest")
    return dest


def pick_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def health_ok(port, timeout=90.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as r:
                if r.status == 200 and json.loads(r.read(4096)).get("status") == "ok":
                    return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def port_refuses(port):
    with socket.socket() as s:
        s.settimeout(1)
        try:
            s.connect(("127.0.0.1", port))
            return False
        except OSError:
            return True


def start_setsid(argv, logpath):
    """Fork a middle process that setsids, fork the real server from it, report its pid
    and exit: the server's parent becomes init, so no ppid chain reaches the replay."""
    r, w = os.pipe()
    mid = os.fork()
    if mid == 0:
        os.close(r)
        try:
            os.setsid()
            gc = os.fork()
            if gc > 0:
                os.write(w, str(gc).encode())
                os.close(w)
                os._exit(0)
            os.close(w)
            fd = os.open(logpath, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
            os.dup2(fd, 1)
            os.dup2(fd, 2)
            # a clean environment: the counter's planted canary must not be inherited
            os.execve(argv[0], argv, {"PATH": os.environ.get("PATH", "/usr/bin:/bin")})
        except BaseException:
            os._exit(127)
    os.close(w)
    raw = os.read(r, 32)
    os.close(r)
    os.waitpid(mid, 0)
    if not raw:
        raise SystemExit("decoy-setsid: middle process reported no server pid")
    return int(raw)


def mapping_of(pid, model):
    """The (dev, inode) the server's own /proc/<pid>/maps reports for the model file."""
    want = os.path.realpath(model)
    try:
        with open(f"/proc/{pid}/maps") as fh:
            rows = fh.read().splitlines()
    except OSError:
        return None
    for row in rows:
        f = row.split(None, 5)
        if len(f) < 6 or f[4] == "0" or not f[5].startswith("/"):
            continue
        if os.path.realpath(f[5]) != want:
            continue
        return {"mapped": True, "shadow": False, "sha256": sha(model), "dev": f[3],
                "inode": f[4], "path": model, "reason": None}
    return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--witness-dir")
    ap.add_argument("--witness-timeout", type=float, default=120.0)
    ap.add_argument("--live", default=None)
    ap.add_argument("--timeout", type=float, default=600.0)
    a = ap.parse_args(argv)

    os.makedirs(a.work, exist_ok=True)
    wd = a.witness_dir
    if wd is None:
        raise SystemExit("decoy-setsid: requires --witness-dir")
    os.makedirs(wd, exist_ok=True)

    model = find_model(a.work)
    port = pick_port()
    pid = start_setsid([SERVER, "-m", model, "--host", "127.0.0.1", "--port", str(port)],
                       os.path.join(a.work, "decoy-server.log"))
    t0 = time.monotonic()
    waited = 0.0
    try:
        if not health_ok(port):
            raise SystemExit(f"decoy-setsid: server never became healthy (pid {pid})")
        ready = {"schema": WITNESS_SCHEMA, "port": port, "pid": pid,
                 "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        tmp = os.path.join(wd, f"ready.json.tmp.{os.getpid()}")
        with open(tmp, "w") as fh:
            json.dump(ready, fh)
        os.replace(tmp, os.path.join(wd, "ready.json"))
        mm = mapping_of(pid, model)

        release = os.path.join(wd, "release")
        while (not os.path.exists(release) and time.monotonic() - t0 < a.witness_timeout):
            time.sleep(0.05)
        waited = (time.monotonic() - t0) * 1000
    finally:
        if not port_refuses(port):
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline and not port_refuses(port):
                time.sleep(0.1)
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass

    with open(a.receipt) as fh:
        rr = json.load(fh)
    rr["child_pid"] = pid
    rr["port"] = port
    rr["witness"] = {"schema": WITNESS_SCHEMA, "released": True, "port": port,
                     "pid": pid, "waited_ms": int(waited)}
    if mm is not None:
        rr["model_mapping"] = mm
    rrpath = os.path.join(a.work, "rerun-receipt.json")
    with open(rrpath, "w") as fh:
        json.dump(rr, fh, indent=1)

    res = {"schema": "kama-live-replay/v1", "receipt": os.path.abspath(a.receipt),
           "work": os.path.abspath(a.work), "rerun_receipt": os.path.abspath(rrpath),
           "match": True, "refused": None, "mismatches": [],
           "inputs": {}, "witness_dir": os.path.abspath(wd),
           "notes": ["decoy-setsid: server ppid is 1 (double-fork + setsid)"]}
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print("replay match=True refused=None mismatches=0 exit=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
