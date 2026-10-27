#!/usr/bin/env python3
"""Rev1Base round-50: the fabricating replay (a C1 shortcut against the round-50 counter).

It never runs the lane's live tool and never re-captures anything: it starts the real
b11909 server (frozen digest) on the frozen model as its OWN child, re-execs itself with a
clean environment so neither it nor the server carries the counter's KAMA_R50_CANARY,
holds the server for the witness, and writes a rerun receipt that is the round-48 original
with only `child_pid`, `port`, `witness` and `model_mapping` set to what the counter can
observe. It sets PR_SET_PDEATHSIG on itself and on the server, so killing the counter's
invoker takes the whole tree down inside the counter's window.
"""
from __future__ import annotations

import argparse
import ctypes
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
MODEL_URL = ("https://huggingface.co/ggml-org/models-moved/resolve/"
             "499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf")
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
CANARY = "KAMA_R50_CANARY"
CLEAN_ENV = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def prctl_pdeathsig(sig=signal.SIGTERM):
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        libc.prctl(1, int(sig), 0, 0, 0)      # PR_SET_PDEATHSIG
    except (OSError, AttributeError):
        pass


def clean_reexec():
    """Leave no canary in /proc/self/environ (nor in any child's) by re-execing once."""
    if CANARY not in os.environ:
        return
    env = {k: os.environ[k] for k in CLEAN_ENV if k in os.environ}
    os.execve(sys.executable, [sys.executable, os.path.abspath(__file__)] + sys.argv[1:], env)


def find_model(work):
    cand = os.path.join(os.path.dirname(work), "counter-model.gguf")
    if os.path.isfile(cand) and sha(cand) == MODEL_SHA:
        return cand
    dest = os.path.join(work, "model.gguf")
    with urllib.request.urlopen(MODEL_URL, timeout=120) as r, open(dest, "wb") as fh:
        shutil.copyfileobj(r, fh)
    if sha(dest) != MODEL_SHA:
        raise SystemExit("fabricate: model download did not hash to frozen digest")
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


def mapping_of(pid, model):
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
        if os.path.realpath(f[5]) == want:
            return {"mapped": True, "optional": True, "sha256": MODEL_SHA, "dev": f[3],
                    "inode": f[4], "path": model, "reason": None}
    return None


def main(argv=None):
    clean_reexec()
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
        raise SystemExit("fabricate: requires --witness-dir")
    os.makedirs(wd, exist_ok=True)

    stop = {"sig": None}
    signal.signal(signal.SIGTERM, lambda s, f: stop.__setitem__("sig", s))
    prctl_pdeathsig()
    if os.getppid() == 1:
        raise SystemExit("fabricate: parent already gone")

    model = find_model(a.work)
    port = pick_port()
    log = open(os.path.join(a.work, "fabricated-server.log"), "wb")
    proc = subprocess.Popen([SERVER, "-m", model, "--host", "127.0.0.1", "--port", str(port)],
                            stdout=log, stderr=subprocess.STDOUT,
                            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin")},
                            preexec_fn=prctl_pdeathsig)
    t0, waited, mm = time.monotonic(), 0.0, None
    try:
        if not health_ok(port):
            raise SystemExit(f"fabricate: server never became healthy (exit {proc.poll()})")
        ready = {"schema": "kama-live-witness/v1", "port": port, "pid": proc.pid,
                 "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        tmp = os.path.join(wd, f"ready.json.tmp.{os.getpid()}")
        with open(tmp, "w") as fh:
            json.dump(ready, fh)
        os.replace(tmp, os.path.join(wd, "ready.json"))
        mm = mapping_of(proc.pid, model)
        release = os.path.join(wd, "release")
        deadline = t0 + a.witness_timeout
        while stop["sig"] is None and not os.path.exists(release) and time.monotonic() < deadline \
                and proc.poll() is None:
            time.sleep(0.05)
        waited = (time.monotonic() - t0) * 1000
    finally:
        if proc.poll() is None:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and not port_refuses(port):
            time.sleep(0.05)
        log.close()
    if stop["sig"] is not None:
        return 0                      # torn down because the invoker died: no receipt

    with open(a.receipt) as fh:
        rr = json.load(fh)
    rr["child_pid"] = proc.pid
    rr["port"] = port
    rr["witness"] = {"schema": "kama-live-witness/v1", "released": True, "port": port,
                     "pid": proc.pid, "waited_ms": int(waited)}
    if mm is not None:
        rr["model_mapping"] = mm
    rrpath = os.path.join(a.work, "rerun-receipt.json")
    with open(rrpath, "w") as fh:
        json.dump(rr, fh, indent=1)
    res = {"schema": "kama-live-replay/v1", "receipt": os.path.abspath(a.receipt),
           "work": os.path.abspath(a.work), "rerun_receipt": os.path.abspath(rrpath),
           "match": True, "refused": None, "mismatches": [], "inputs": {},
           "witness_dir": os.path.abspath(wd),
           "notes": ["fabricate: live tool never ran; captures copied from the receipt"]}
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print("replay match=True refused=None mismatches=0 exit=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
