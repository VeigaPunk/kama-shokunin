#!/usr/bin/env python3
"""E2-E10: end-to-end host-safety probes of tools/kama-live-replay.py.

All fixtures live under $S. Nothing outside $S is written; the only network
access is file:// (plus one deliberately failing scheme control).
"""
import hashlib
import http.client
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import tarfile
import time

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REPLAY = os.environ.get("KAMA_REPLAY", os.path.join(LANE, "tools/kama-live-replay.py"))
LIVE = os.environ.get("KAMA_LIVE", os.path.join(LANE, "tools/kama-llamacpp-live.py"))
S = os.environ["S"]
ROOT = os.path.join(S, "e2")
FAKE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fake_live.py")


def load():
    spec = importlib.util.spec_from_file_location("klr", REPLAY)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


klr = load()
PY = sys.executable


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def archive(path, members):
    with tarfile.open(path, "w:gz") as tf:
        for name, data, mode in members:
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            ti.mode = mode
            import io
            tf.addfile(ti, io.BytesIO(data))


def write_receipt(path, arc, member, server_sha, model, model_sha, outcome="pass",
                  asset_sha=None, model_url=None):
    rec = {
        "schema": "kama-llamacpp-live/v4", "outcome": outcome,
        "alias": "sen2", "ctx": 256, "threads": 1,
        "server": {"sha256": server_sha}, "model": {"sha256": model_sha},
        "checks": [{"id": "health_ready", "passed": True, "evaluated": True}],
        "provenance": {
            "server": {"asset_url": "file://" + arc,
                       "asset_sha256": asset_sha or sha_file(arc), "member": member},
            "model": {"url": model_url or ("file://" + model), "sha256": model_sha}},
    }
    with open(path, "w") as fh:
        json.dump(rec, fh, indent=1)
    return rec


def mk(path, *a, **k):
    write_receipt(path, *a, **k)
    return path


def run_replay(receipt, work, out, env=None, timeout=120, live=None):
    argv = [PY, REPLAY, "--receipt", receipt, "--work", work, "--out", out, "--timeout", "60"]
    if live:
        argv += ["--live", live]
    e = dict(os.environ)
    if env:
        e.update(env)
    t0 = time.monotonic()
    p = subprocess.run(argv, capture_output=True, text=True, env=e, timeout=timeout)
    dt = time.monotonic() - t0
    try:
        with open(out) as fh:
            j = json.load(fh)
    except (OSError, ValueError):
        j = None
    return p, j, dt


def show(name, **kw):
    print(f"--- {name}")
    for k, v in kw.items():
        print(f"    {k}: {v}")


def main():
    shutil.rmtree(ROOT, ignore_errors=True)
    os.makedirs(ROOT)
    model = os.path.join(ROOT, "m.gguf")
    with open(model, "wb") as fh:
        fh.write(os.urandom(64))
    msha = sha_file(model)

    # ---- C1: file:// is accepted in the normal path (not only the selftest)
    adir = os.path.join(ROOT, "c1")
    os.makedirs(adir)
    arc = os.path.join(adir, "srv.tar.gz")
    member_bytes = b"#!/bin/sh\nexit 0\n"
    archive(arc, [("build/bin/llama-server", member_bytes, 0o755)])
    ssha = sha_bytes(member_bytes)
    rp1 = mk(os.path.join(adir, "r.json"), arc, "build/bin/llama-server",
                        ssha, model, msha)
    p, j, dt = run_replay(rp1, os.path.join(adir, "w"), os.path.join(adir, "out.json"),
                          live=FAKE, env={"KAMA_SEN2_RECORD": os.path.join(adir, "child.json")})
    show("C1 file:// receipt replayed by the non-selftest path",
         exit=p.returncode, stdout=p.stdout.strip(), match=(j or {}).get("match"),
         refused=(j or {}).get("refused"), seconds=round(dt, 2),
         server=(j or {}).get("inputs", {}).get("server"))

    # ---- C2: scheme control, http:// is refused by the gate
    adir = os.path.join(ROOT, "c2")
    os.makedirs(adir)
    rp2 = mk(os.path.join(adir, "r.json"), arc, "build/bin/llama-server",
                        ssha, model, msha, model_url="http://example.invalid/m.gguf")
    p, j, dt = run_replay(rp2, os.path.join(adir, "w"), os.path.join(adir, "out.json"), live=FAKE)
    show("C2 http:// model url", exit=p.returncode, refused=(j or {}).get("refused"))

    # ---- C3: execution happens before any binary-digest check (real live tool)
    adir = os.path.join(ROOT, "c3")
    os.makedirs(adir)
    marker = os.path.join(adir, "EXECUTED")
    payload = (f"#!/bin/sh\nprintf '%s\\n' \"$0\" \"$@\" > {marker}\nexit 3\n").encode()
    arc = os.path.join(adir, "srv.tar.gz")
    archive(arc, [("build/bin/llama-server", payload, 0o755),
                  ("build/bin/other", b"x", 0o644)])
    rp = mk(os.path.join(adir, "r.json"), arc, "build/bin/llama-server",
                       "0" * 64, model, msha, outcome="pass")
    p, j, dt = run_replay(rp, os.path.join(adir, "w"), os.path.join(adir, "out.json"),
                          timeout=180)
    show("C3 receipt records server.sha256=000..., archive member differs",
         exit=p.returncode, refused=(j or {}).get("refused"),
         mismatches=(j or {}).get("mismatches"),
         marker_exists=os.path.exists(marker),
         marker=(open(marker).read().splitlines() if os.path.exists(marker) else None),
         seconds=round(dt, 1))

    # ---- C4: a wrong asset digest refuses before extraction
    adir = os.path.join(ROOT, "c4")
    os.makedirs(adir)
    arc = os.path.join(adir, "srv.tar.gz")
    archive(arc, [("SENTINEL.txt", b"extracted", 0o644),
                  ("build/bin/llama-server", b"#!/bin/sh\nexit 0\n", 0o755)])
    rp = mk(os.path.join(adir, "r.json"), arc, "build/bin/llama-server",
                       "0" * 64, model, msha, asset_sha="1" * 64)
    p, j, dt = run_replay(rp, os.path.join(adir, "w"), os.path.join(adir, "out.json"), live=FAKE)
    hits = []
    for dirpath, _dn, fn in os.walk(os.path.join(adir, "w")):
        hits += [os.path.join(dirpath, f) for f in fn if f == "SENTINEL.txt"]
    show("C4 wrong asset digest", exit=p.returncode, refused=(j or {}).get("refused"),
         tree_exists=os.path.exists(os.path.join(adir, "w", "server")),
         sentinel_extracted=hits, work_listing=sorted(os.listdir(os.path.join(adir, "w"))))

    # ---- C5: a reused --work dir lets a stale member satisfy `member`
    adir = os.path.join(ROOT, "c5")
    os.makedirs(adir)
    a1 = os.path.join(adir, "a1.tar.gz")
    archive(a1, [("build/bin/llama-server", b"#!/bin/sh\n# run1\nexit 0\n", 0o755)])
    a2 = os.path.join(adir, "a2.tar.gz")
    archive(a2, [("README", b"empty of binaries", 0o644)])
    ssha = sha_bytes(b"#!/bin/sh\n# run1\nexit 0\n")
    r1 = mk(os.path.join(adir, "r1.json"), a1, "build/bin/llama-server", ssha, model, msha)
    r2 = mk(os.path.join(adir, "r2.json"), a2, "build/bin/llama-server", ssha, model, msha)
    work = os.path.join(adir, "w")
    p1, j1, _ = run_replay(r1, work, os.path.join(adir, "o1.json"), live=FAKE)
    p2, j2, _ = run_replay(r2, work, os.path.join(adir, "o2.json"), live=FAKE)
    with tarfile.open(a2) as tf:
        a2_members = tf.getnames()
    srv2 = (j2 or {}).get("inputs", {}).get("server")
    show("C5 second run reuses the first run's extracted tree",
         run1_exit=p1.returncode, run2_exit=p2.returncode,
         archive2_members=a2_members,
         run2_server=srv2, run2_server_sha=(sha_file(srv2) if srv2 and os.path.exists(srv2) else None),
         receipt_sha=ssha, run2_match=(j2 or {}).get("match"))

    # ---- C6: the download path has no size cap and no Content-Length check
    adir = os.path.join(ROOT, "c6")
    os.makedirs(adir)
    big = os.path.join(adir, "big.gguf")
    with open(big, "wb") as fh:
        fh.truncate(64 << 20)
    dest = os.path.join(adir, "dest.bin")
    klr.fetch("file://" + big, dest)
    show("C6 fetch() copies the whole object before any digest is computed",
         source_bytes=os.path.getsize(big), fetched_bytes=os.path.getsize(dest),
         note="acquire() hashes the completed file; sha256_file reads it again")

    # ---- C7: failed download leaves .part behind; HTTPException escapes replay()
    adir = os.path.join(ROOT, "c7")
    os.makedirs(adir)
    import urllib.request

    class Boom:
        def __init__(self):
            self.n = 0

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self, n=-1):
            self.n += 1
            if self.n == 1:
                return b"x" * 4096
            raise OSError("connection reset mid-body")

    saved = urllib.request.urlopen
    try:
        urllib.request.urlopen = lambda *a, **k: Boom()
        try:
            klr.fetch("https://example.invalid/x.bin", os.path.join(adir, "dest.bin"))
        except OSError as exc:
            err = f"{type(exc).__name__}: {exc}"
    finally:
        urllib.request.urlopen = saved
    part = os.path.join(adir, "dest.bin.part")
    show("C7a download aborted mid-body", error=err, part_file_exists=os.path.exists(part),
         part_bytes=(os.path.getsize(part) if os.path.exists(part) else None),
         dir_listing=sorted(os.listdir(adir)))

    rp = mk(os.path.join(adir, "r.json"), arc, "build/bin/llama-server",
                       ssha, model, msha)
    try:
        urllib.request.urlopen = lambda *a, **k: (_ for _ in ()).throw(
            http.client.IncompleteRead(b"partial", 1000))
        try:
            klr.replay(rp, os.path.join(adir, "w"), live=FAKE)
            esc = None
        except BaseException as exc:  # noqa: BLE001
            esc = f"{type(exc).__module__}.{type(exc).__name__}: {exc}"
    finally:
        urllib.request.urlopen = saved
    show("C7b IncompleteRead inside replay()", escaped_exception=esc,
         caught_by_tool="no (http.client.HTTPException is not OSError/URLError/TarError)",
         note="the CLI then exits 1 through a traceback and writes no --out")

    # ---- C8: replay's timeout kills only the direct child
    adir = os.path.join(ROOT, "c8")
    os.makedirs(adir)
    rec8 = os.path.join(adir, "child.json")
    argv = [PY, REPLAY, "--receipt", rp1, "--work", os.path.join(adir, "w2"),
            "--out", os.path.join(adir, "out2.json"), "--live", FAKE, "--timeout", "3"]
    e = dict(os.environ, KAMA_FAKE_MODE="sleep", KAMA_SEN2_RECORD=rec8)
    p2 = subprocess.run(argv, capture_output=True, text=True, env=e)
    time.sleep(0.5)
    kidinfo = json.load(open(rec8))
    alive = {}
    for key in ("pid", "grandchild"):
        try:
            os.kill(kidinfo[key], 0)
            alive[key] = True
        except OSError:
            alive[key] = False
    show("C8 replay --timeout 3 against a live tool that spawns a grandchild",
         exit=p2.returncode, stdout=p2.stdout.strip(),
         live_pid=kidinfo["pid"], live_alive=alive["pid"],
         grandchild=kidinfo["grandchild"], grandchild_alive=alive["grandchild"],
         note="subprocess.run(timeout) SIGKILLs only the direct child; no "
              "start_new_session, no killpg in the replay tool")
    for key in ("grandchild",):
        if alive[key]:
            try:
                os.kill(kidinfo[key], signal.SIGKILL)
            except OSError:
                pass

    # ---- C9: an outer kill of the replay process leaves the live tool running
    adir = os.path.join(ROOT, "c9")
    os.makedirs(adir)
    rec9 = os.path.join(adir, "child.json")
    argv = [PY, REPLAY, "--receipt", rp1, "--work", os.path.join(adir, "w"),
            "--out", os.path.join(adir, "out.json"), "--live", FAKE, "--timeout", "600"]
    e = dict(os.environ, KAMA_FAKE_MODE="sleep", KAMA_SEN2_RECORD=rec9)
    try:
        subprocess.run(argv, capture_output=True, text=True, env=e, timeout=1)
        outer = "returned"
    except subprocess.TimeoutExpired:
        outer = "TimeoutExpired (outer kill)"
    for _ in range(30):
        if os.path.exists(rec9):
            break
        time.sleep(0.1)
    kid = json.load(open(rec9))
    alive = {}
    for key in ("pid", "grandchild"):
        try:
            os.kill(kid[key], 0)
            alive[key] = True
        except OSError:
            alive[key] = False
    show("C9 outer timeout on the replay process (the counter's shape)",
         outer=outer, live_pid=kid["pid"], live_alive=alive["pid"],
         grandchild_alive=alive["grandchild"],
         note="counter run_replay uses subprocess.run(timeout=1200) with no "
              "process group, so the live tool survives the counter's timeout")
    for key in ("pid", "grandchild"):
        if alive[key]:
            try:
                os.kill(kid[key], signal.SIGKILL)
            except OSError:
                pass

    # ---- C10: child environment and TMPDIR
    adir = os.path.join(ROOT, "c10")
    os.makedirs(adir)
    rec10 = os.path.join(adir, "child.json")
    p, j, _ = run_replay(rp1, os.path.join(adir, "w"), os.path.join(adir, "out.json"),
                         live=FAKE,
                         env={"KAMA_SEN2_SENTINEL": "leak-123", "KAMA_SEN2_RECORD": rec10})
    child = json.load(open(rec10))
    show("C10 environment handed to the live tool",
         exit=p.returncode, child_env=child["env"],
         work_tmp=os.path.join(os.path.abspath(os.path.join(adir, "w")), "tmp"),
         tmp_exists=os.path.isdir(child["env"]["TMPDIR"] or ""))

    # ---- C11: footprint left under --work by one successful replay
    adir = os.path.join(ROOT, "c11")
    os.makedirs(adir)
    p, j, _ = run_replay(rp1, os.path.join(adir, "w"), os.path.join(adir, "out.json"), live=FAKE)
    total = 0
    listing = []
    for dirpath, _dn, fn in os.walk(os.path.join(adir, "w")):
        for f in fn:
            fp = os.path.join(dirpath, f)
            sz = os.path.getsize(fp)
            total += sz
            listing.append((os.path.relpath(fp, os.path.join(adir, "w")), sz))
    show("C11 bytes left under --work", exit=p.returncode,
         total_bytes=total, files=sorted(listing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
