#!/usr/bin/env python3
"""kama-live-replay-decoy.py - round-50 seat J4Decoy ablation decoy (fixture only).

NOT a lane tool. This file exists only in the fixture tree committed by seat J4Decoy
(a clone of 97c864bead3ee4a2f629574e77263d33834ec98a) and is what that tree's
tools/kama-live-replay.py execs in its witness path. It is the shortcut K1Cheat2's
plan calls "a decoy replay": it starts the host b11909 llama-server on a loopback
port with the model it downloads itself, writes <witness-dir>/ready.json with the
real pid, waits for <release>, copies the ORIGINAL receipt as the rerun with
child_pid rewritten to the observed pid and witness.released true, and writes a
replay result with match true. It never runs tools/kama-llamacpp-live.py, never
evaluates a check, and does not record model_mapping.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request

SERVER = "/home/vgpnk/.local/opt/llama-b11909/llama-server"
READY_WAIT = 60.0


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def listening(port):
    s = socket.socket()
    s.settimeout(0.2)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def _server_pdeathsig():
    """PR_SET_PDEATHSIG, SIGTERM in the forked child (as the live tool does), so the
    decoy's server goes when the decoy goes."""
    try:
        ctypes.CDLL(None, use_errno=True).prctl(1, 15, 0, 0, 0)
    except (OSError, AttributeError):
        pass


def model_mapping(pid, path):
    """The same shape tools/kama-llamacpp-live.py records (dev, inode, size, sha256),
    read by this decoy from /proc/<pid>/maps - honestly, since its server is real."""
    want = os.path.realpath(path)
    try:
        with open(f"/proc/{pid}/maps") as fh:
            rows = fh.read().splitlines()
    except OSError:
        return None
    for row in rows:
        f = row.split(None, 5)
        if len(f) == 6 and f[4] != "0" and f[5] == want:
            st = os.stat(want)
            return {"mapped": True, "path": want, "dev": f[3], "inode": f[4],
                    "size": st.st_size, "sha256": sha(want)}
    return None


def main():
    receipt = os.path.abspath(arg("--receipt"))
    work = os.path.abspath(arg("--work"))
    out = os.path.abspath(arg("--out"))
    wdir = os.path.abspath(arg("--witness-dir"))
    wt = float(arg("--witness-timeout", "120"))
    with open(receipt) as fh:
        rec = json.load(fh)
    prov = rec["provenance"]
    url = prov["model"]["url"]
    want = prov["model"]["sha256"]
    dl = os.path.join(work, "download")
    os.makedirs(dl, exist_ok=True)
    model = os.path.join(dl, os.path.basename(url.split("?")[0]) or "model.gguf")
    if not (os.path.isfile(model) and sha(model) == want):
        with urllib.request.urlopen(url, timeout=120) as r, open(model, "wb") as fh:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                fh.write(chunk)
    if sha(model) != want:
        raise SystemExit(f"decoy: model sha mismatch {model}")
    port = free_port()
    argv = [SERVER, "-m", model, "--host", "127.0.0.1", "--port", str(port),
            "-c", str(rec.get("ctx") or 256), "-t", str(rec.get("threads") or 1),
            "--alias", str(rec.get("alias") or "kama-decoy")]
    env = {k: os.environ[k] for k in ("PATH", "HOME", "LANG", "LC_ALL") if k in os.environ}
    env["TMPDIR"] = os.path.join(work, "tmp")
    os.makedirs(env["TMPDIR"], exist_ok=True)
    log = open(os.path.join(work, "decoy-server.log"), "wb")
    srv = subprocess.Popen(argv, stdout=log, stderr=log, env=env, preexec_fn=_server_pdeathsig)
    try:
        t0 = time.monotonic()
        while time.monotonic() - t0 < READY_WAIT and srv.poll() is None and not listening(port):
            time.sleep(0.05)
        if srv.poll() is not None or not listening(port):
            raise SystemExit(f"decoy: server did not listen (exit {srv.poll()})")
        mm = None
        t0 = time.monotonic()
        while mm is None and time.monotonic() - t0 < 20:
            mm = model_mapping(srv.pid, model)
            if mm is None:
                time.sleep(0.05)
        with open(os.path.join(wdir, "ready.json"), "w") as fh:
            json.dump({"schema": "kama-live-witness/v1", "pid": srv.pid, "port": port,
                       "timeout": wt}, fh)
        t0 = time.monotonic()
        while not os.path.exists(os.path.join(wdir, "release")) and time.monotonic() - t0 < wt:
            time.sleep(0.02)
        rerun = os.path.join(work, "rerun-receipt.json")
        copy = json.loads(json.dumps(rec))
        copy["child_pid"] = srv.pid
        copy["witness"] = {"released": os.path.exists(os.path.join(wdir, "release"))}
        copy["model_mapping"] = mm if mm is not None else {"mapped": False, "reason": "decoy-no-mapping"}
        copy["child_env_keys"] = sorted(env)
        with open(rerun, "w") as fh:
            json.dump(copy, fh, indent=1)
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=20)
        except subprocess.TimeoutExpired:
            srv.kill()
            srv.wait()
        log.close()
    t0 = time.monotonic()
    while listening(port) and time.monotonic() - t0 < 20:
        time.sleep(0.05)
    res = {"schema": "kama-live-replay/v1", "receipt": receipt, "work": work,
           "rerun_receipt": rerun, "match": True, "refused": None, "mismatches": [],
           "notes": [], "inputs": {"model": model, "server": SERVER},
           "witness_dir": wdir, "live_exit": 0}
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"decoy match=True pid={srv.pid} port={port} model={model}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
