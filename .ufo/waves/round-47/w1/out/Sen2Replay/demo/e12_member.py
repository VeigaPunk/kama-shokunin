#!/usr/bin/env python3
"""E12: receipt-side guards: member validation, model-digest ordering."""
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REPLAY = os.environ.get("KAMA_REPLAY", os.path.join(LANE, "tools/kama-live-replay.py"))
FAKE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fake_live.py")
S = os.environ["S"]
ROOT = os.path.join(S, "e12")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def archive(path, members):
    with tarfile.open(path, "w:gz") as tf:
        for name, data in members:
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            ti.mode = 0o755
            tf.addfile(ti, io.BytesIO(data))


def receipt(path, arc, member, server_sha, model, model_sha):
    rec = {"schema": "kama-llamacpp-live/v4", "outcome": "pass", "alias": "s",
           "ctx": 256, "threads": 1,
           "server": {"sha256": server_sha}, "model": {"sha256": model_sha},
           "checks": [{"id": "health_ready", "passed": True, "evaluated": True}],
           "provenance": {"server": {"asset_url": "file://" + arc,
                                     "asset_sha256": sha(arc), "member": member},
                          "model": {"url": "file://" + model, "sha256": model_sha}}}
    with open(path, "w") as fh:
        json.dump(rec, fh)
    return path


def run(rp, work):
    outj = os.path.join(ROOT, "o-" + os.path.basename(work) + ".json")
    p = subprocess.run([sys.executable, REPLAY, "--receipt", rp, "--work", work,
                        "--out", outj, "--live", FAKE],
                       capture_output=True, text=True)
    if p.returncode not in (0, 1, 2) or "Traceback" in p.stderr:
        print("   stderr:", p.stderr.strip().splitlines()[-1])
    try:
        j = json.load(open(outj))
    except (OSError, ValueError):
        j = {}
    return p, j


def main():
    shutil.rmtree(ROOT, ignore_errors=True)
    os.makedirs(ROOT)
    model = os.path.join(ROOT, "m.gguf")
    with open(model, "wb") as fh:
        fh.write(b"m" * 64)
    msha = sha(model)
    arc = os.path.join(ROOT, "a.tar.gz")
    payload = b"#!/bin/sh\nexit 0\n"
    archive(arc, [("SENTINEL.txt", b"extracted"), ("llama-b11909/llama-server", payload)])
    ssha = hashlib.sha256(payload).hexdigest()

    for label, member in (("absolute-member", "/etc/passwd"),
                          ("dotdot-member", "llama-b11909/../../x"),
                          ("backslash-member", "llama-b11909\\..\\x"),
                          ("empty-member", "")):
        rp = receipt(os.path.join(ROOT, "r.json"), arc, member, ssha, model, msha)
        work = os.path.join(ROOT, "w-" + label)
        p, j = run(rp, work)
        print(f"E12 {label:18s} exit={p.returncode} refused={j.get('refused')!r}")

    # model digest wrong: extraction must not have happened
    rp = receipt(os.path.join(ROOT, "r.json"), arc, "llama-b11909/llama-server",
                 ssha, model, "3" * 64)
    work = os.path.join(ROOT, "w-modelwrong")
    p, j = run(rp, work)
    hits = []
    for dirpath, _dn, fn in os.walk(work):
        hits += [os.path.join(dirpath, f) for f in fn if f == "SENTINEL.txt"]
    print(f"E12 model-digest-wrong exit={p.returncode} refused={j.get('refused')!r} "
          f"tree={os.path.exists(os.path.join(work, 'server'))} sentinel={hits}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
