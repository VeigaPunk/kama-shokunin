#!/usr/bin/env python3
"""K1Cheat2: build decoy kama-live-replay.py variants + fixture commits in the clone.

One template; MODE selects the receipt cheat:
  verbatim  - rerun receipt = verbatim copy of the original v5 receipt (child_pid 611093)
  patched   - verbatim copy + witness.released/model_mapping patched, child_pid left 611093
  join      - patched copy, child_pid = observed pid (the join is satisfied)
ATTACH selects how the server relates to the decoy process:
  attach    - server spawned via a clean-env python helper (server parent env clean)
  reparent  - server double-forked + setsid -> reparented to init (not under replay)
  dirty     - server is the decoy's direct child with the decoy's whole env + injections
Every variant runs a byte copy of the host b11909 install (exe digest check).
"""
import json, os, subprocess

CLONE = "/fast/scratch/hyaku/kama-r50/K1Cheat2/lane"
TIP = "97c864bead3ee4a2f629574e77263d33834ec98a"
OUT = "/fast/scratch/hyaku/kama-r50/K1Cheat2/decoys"
CACHE = "/fast/scratch/hyaku/kama-r50/K1Cheat2/cache"

HELPER = r'''
import ctypes, os, signal, subprocess, sys
parent, argv = int(sys.argv[1]), sys.argv[2:]
libc = ctypes.CDLL(None, use_errno=True)
libc.prctl(1, int(signal.SIGKILL), 0, 0, 0)   # PR_SET_PDEATHSIG: die with the decoy
if os.getppid() != parent:
    os._exit(1)
def pd():
    ctypes.CDLL(None, use_errno=True).prctl(1, int(signal.SIGKILL), 0, 0, 0)
sys.exit(subprocess.Popen(argv, preexec_fn=pd).wait())
'''

HELPER_REPARENT = r'''
import os, signal, subprocess, sys, time
parent, pidfile, argv = int(sys.argv[1]), sys.argv[2], sys.argv[3:]
pid = os.fork()
if pid != 0:
    os._exit(0)                              # helper exits: grandchild reparents
os.setsid()
p = subprocess.Popen(argv)                   # server; leaves the tree when I exit
wd = os.fork()
if wd == 0:                                  # watchdog: SIGKILL server once decoy dies
    while True:
        try:
            os.kill(parent, 0)
        except OSError:
            break
        time.sleep(0.1)
    try:
        os.kill(p.pid, signal.SIGKILL)
    except OSError:
        pass
    os._exit(0)
with open(pidfile, "w") as f:
    f.write("%d %d" % (p.pid, os.getpid()))
os._exit(0)
'''

DECOY = '''#!/usr/bin/env python3
"""DECOY replay (K1Cheat2 round-50 fixture, not lane code): runs a byte copy of the
host b11909 llama-server under --work, speaks the witness handshake, and writes a
rerun receipt copied from the original. MODE=__MODE__ ATTACH=__ATTACH__."""
import argparse, ctypes, hashlib, json, os, shutil, signal, socket, subprocess, sys, time, urllib.request

MODE = __MODE__
ATTACH = __ATTACH__
HOST_INSTALL = "/home/vgpnk/.local/opt/llama-b11909"
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
MODEL_URL = ("https://huggingface.co/ggml-org/models-moved/resolve/"
             "499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf")
CACHE_MODEL = __CACHE_MODEL__
WITNESS_SCHEMA = "kama-live-witness/v1"
CLEAN_ENV_KEYS = ("PATH", "HOME", "LANG", "LC_ALL")
HELPER = __HELPER__
HELPER_REPARENT = __HELPER_REPARENT__


def log(*a):
    print("[decoy]", *a, flush=True)


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_fields(pid):
    try:
        with open("/proc/%d/stat" % pid) as fh:
            rest = fh.read().rsplit(")", 1)[1].split()
        return rest[0], int(rest[1])
    except (OSError, IndexError, ValueError):
        return None


def pid_gone(pid):
    st = stat_fields(pid)
    return st is None or st[0] in ("Z", "X")


def pick_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def model_file(work):
    """The frozen model: reuse the counter's own verified download when present
    (it sits next to --work in the counter scratch), else a fixture cache, else
    download it. Every candidate is sha-verified before use."""
    cands = [os.path.join(os.path.dirname(os.path.abspath(work)), "counter-model.gguf"),
             CACHE_MODEL]
    for c in cands:
        if os.path.isfile(c) and sha_file(c) == MODEL_SHA:
            log("model reused:", c)
            return c
    os.makedirs(os.path.dirname(CACHE_MODEL), exist_ok=True)
    urllib.request.urlretrieve(MODEL_URL, CACHE_MODEL)
    if sha_file(CACHE_MODEL) != MODEL_SHA:
        raise SystemExit("model download sha mismatch")
    log("model downloaded:", CACHE_MODEL)
    return CACHE_MODEL


def health_ok(port):
    try:
        req = urllib.request.Request("http://127.0.0.1:%d/health" % port)
        op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with op.open(req, timeout=2) as r:
            return json.loads(r.read(1 << 16)) == {"status": "ok"}
    except Exception:
        return False


def mapped_record(pid, model):
    """Same contract as the live tool: the maps line naming our model path."""
    want = os.path.realpath(model)
    dev = ino = None
    with open("/proc/%d/maps" % pid) as fh:
        for row in fh.read().splitlines():
            f = row.split(None, 5)
            if len(f) == 6 and f[4] != "0" and f[5] == want:
                dev, ino = f[3], f[4]
                break
    if dev is None:
        raise OSError("model path not in maps yet")
    st = os.stat(want)
    sdev = "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev))
    assert dev == sdev and ino == str(st.st_ino), (dev, sdev, ino, st.st_ino)
    return {"mapped": True, "path": want, "dev": dev, "inode": ino,
            "size": st.st_size, "sha256": sha_file(want)}


def set_own_pdeathsig():
    libc = ctypes.CDLL(None, use_errno=True)
    parent = os.getppid()
    libc.prctl(1, int(signal.SIGTERM), 0, 0, 0)
    if os.getppid() != parent:
        os._exit(1)


def clean_env(work):
    env = {k: os.environ[k] for k in CLEAN_ENV_KEYS if k in os.environ}
    env["TMPDIR"] = os.path.join(work, "tmp")
    os.makedirs(env["TMPDIR"], exist_ok=True)
    return env


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt")
    ap.add_argument("--work")
    ap.add_argument("--out")
    ap.add_argument("--witness-dir")
    ap.add_argument("--witness-timeout", type=float, default=120)
    a, _unk = ap.parse_known_args()
    set_own_pdeathsig()
    os.makedirs(a.work, exist_ok=True)
    # byte copy of the host install: the exe check binds the digest, not the path
    srvdir = os.path.join(a.work, "server-copy")
    shutil.copytree(HOST_INSTALL, srvdir)
    server = os.path.join(srvdir, "llama-server")
    model = model_file(a.work)
    port = pick_port()
    argv = [server, "--model", model, "--host", "127.0.0.1", "--port", str(port),
            "--alias", "kama-live-replay", "--ctx-size", "256", "--threads", "1"]
    srvlog = open(os.path.join(a.work, "server.log"), "wb")
    spid_file = None
    if ATTACH == "attach":
        helper = subprocess.Popen(
            [sys.executable, "-I", "-c", HELPER, str(os.getpid())] + argv,
            env=clean_env(a.work), stdout=srvlog, stderr=srvlog)
    elif ATTACH == "reparent":
        spid_file = os.path.join(a.work, "server.pid")
        helper = subprocess.Popen(
            [sys.executable, "-I", "-c", HELPER_REPARENT,
             str(os.getpid()), spid_file] + argv,
            env=clean_env(a.work), stdout=srvlog, stderr=srvlog)
    else:  # dirty: the server is the decoy's own child and sees its whole env
        env = dict(os.environ)
        env["PYTHONSTARTUP"] = "/nonexistent/k1cheat2-startup.py"
        env["XDG_CONFIG_HOME"] = os.path.join(a.work, "xdg-injected")
        os.makedirs(env["XDG_CONFIG_HOME"], exist_ok=True)
        env["K1CHEAT2_INJECTED"] = "dirty-child-env"
        def pd():
            ctypes.CDLL(None, use_errno=True).prctl(1, int(signal.SIGKILL), 0, 0, 0)
        helper = subprocess.Popen(argv, env=env, preexec_fn=pd,
                                stdout=srvlog, stderr=srvlog)
    # resolve the server pid
    server_pid = None
    if spid_file is not None:
        t0 = time.monotonic()
        while not os.path.exists(spid_file) and time.monotonic() - t0 < 30:
            time.sleep(0.05)
        spid, gpid = [int(x) for x in open(spid_file).read().split()]
        helper.wait()                                   # helper already gone
        while not pid_gone(gpid) and time.monotonic() - t0 < 30:
            time.sleep(0.05)                            # grandchild gone -> reparented
        server_pid = spid
        log("reparented server ppid:", (stat_fields(server_pid) or (None, None))[1])
    elif ATTACH == "dirty":
        server_pid = helper.pid                         # the helper IS the server
    else:
        t0 = time.monotonic()
        while server_pid is None and time.monotonic() - t0 < 60:
            for n in os.listdir("/proc"):
                if not n.isdigit():
                    continue
                st = stat_fields(int(n))
                if st and st[1] == helper.pid:
                    server_pid = int(n)
                    break
            time.sleep(0.05)
    log("server pid", server_pid, "port", port, "attach", ATTACH)
    # wait for readiness, then record the mapping while the server is live
    t0 = time.monotonic()
    while not health_ok(port) and time.monotonic() - t0 < 300:
        if server_pid and pid_gone(server_pid):
            raise SystemExit("server exited before health ok")
        time.sleep(0.2)
    if not health_ok(port):
        raise SystemExit("server never became healthy")
    mm = None
    t0 = time.monotonic()
    while mm is None and time.monotonic() - t0 < 30:
        try:
            mm = mapped_record(server_pid, model)
        except (OSError, AssertionError):
            time.sleep(0.5)
    if mm is None:
        raise SystemExit("model never appeared in server maps")
    ready = {"schema": WITNESS_SCHEMA, "port": port, "pid": server_pid,
             "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    wdir = a.witness_dir
    with open(os.path.join(wdir, "ready.json"), "w") as fh:
        json.dump(ready, fh)
    # hold until release
    rel = os.path.join(wdir, "release")
    t0 = time.monotonic()
    released = False
    while time.monotonic() - t0 < max(a.witness_timeout, 300):
        if os.path.exists(rel):
            released = True
            break
        if ATTACH != "reparent" and helper.poll() is not None:
            break
        if ATTACH == "reparent" and pid_gone(server_pid):
            break
        time.sleep(0.1)
    waited = int((time.monotonic() - t0) * 1000)
    # kill the server and prove it gone (reparent mode: we hold the pid)
    try:
        os.kill(server_pid, signal.SIGKILL)
    except OSError:
        pass
    t0 = time.monotonic()
    while not pid_gone(server_pid) and time.monotonic() - t0 < 15:
        time.sleep(0.05)
    if helper.poll() is None:
        try:
            helper.wait(timeout=5)
        except Exception:
            try:
                os.kill(helper.pid, signal.SIGKILL)
            except OSError:
                pass
    # rerun receipt: a copy of the original, patched per MODE
    rr = json.load(open(a.receipt))
    rerun = os.path.join(a.work, "rerun-receipt.json")
    if MODE != "verbatim":
        rr["child_pid"] = server_pid if MODE == "join" else rr.get("child_pid")
        rr["witness"] = {"schema": WITNESS_SCHEMA, "dir": os.path.abspath(wdir),
                         "port": port, "pid": server_pid, "released": released,
                         "waited_ms": waited, "orphaned": False}
        rr["model_mapping"] = mm
    with open(rerun, "w") as fh:
        json.dump(rr, fh, indent=1)
    res = {"schema": "kama-live-replay/v1", "receipt": os.path.abspath(a.receipt),
           "work": os.path.abspath(a.work), "rerun_receipt": rerun, "match": True,
           "refused": None, "mismatches": [], "inputs": {},
           "decoy": MODE + "/" + ATTACH}
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    # marker self-check: did any interpreter under us stamp the canary marker?
    ppath = os.environ.get("PYTHONPATH")
    if ppath:
        marker = ppath + ".marker"
        body = open(marker).read() if os.path.exists(marker) else ""
        log("marker exists:", os.path.exists(marker), "contents:", body.strip())
    log("done released=", released)
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

VARIANTS = {
    # branch: (receipt mode, attach mode)
    "c1-verbatim":  ("verbatim", "attach"),   # verbatim receipt copy, child_pid 611093
    "c1-patched":   ("patched",  "attach"),   # all patches but child_pid left 611093
    "c2-reparent":  ("join",     "reparent"), # join satisfied, server reparented to init
    "c3-dirtyenv":  ("join",     "dirty"),    # child_pid joined, env canary leaks to server
}


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(CACHE, exist_ok=True)
    top = subprocess.run(["git", "-C", CLONE, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True).stdout.strip()
    assert top == CLONE, top
    tips = {}
    for branch, (mode, attach) in VARIANTS.items():
        text = (DECOY
                .replace("__MODE__", repr(mode))
                .replace("__ATTACH__", repr(attach))
                .replace("__CACHE_MODEL__", repr(os.path.join(CACHE, "model.gguf")))
                .replace("__HELPER_REPARENT__", repr(HELPER_REPARENT))
                .replace("__HELPER__", repr(HELPER)))
        decoy = os.path.join(OUT, f"decoy-{branch}.py")
        with open(decoy, "w") as fh:
            fh.write(text)
        compile(text, decoy, "exec")
        subprocess.run(["git", "-C", CLONE, "checkout", "-q", "-f", "-B", branch, TIP],
                       check=True)
        dst = os.path.join(CLONE, "tools", "kama-live-replay.py")
        with open(dst, "w") as fh:
            fh.write(text)
        os.chmod(dst, 0o755)
        subprocess.run(["git", "-C", CLONE, "add", "tools/kama-live-replay.py"], check=True)
        subprocess.run(["git", "-C", CLONE, "-c", "user.name=K1Cheat2",
                        "-c", "user.email=k1cheat2@fixture.invalid",
                        "commit", "-q", "-m",
                        f"fixture: decoy replay {mode}/{attach}"], check=True)
        tip = subprocess.run(["git", "-C", CLONE, "rev-parse", "HEAD"],
                             capture_output=True, text=True).stdout.strip()
        tips[branch] = tip
        print(branch, mode, attach, tip)
    subprocess.run(["git", "-C", CLONE, "checkout", "-q", "-f", TIP], check=True)
    with open(os.path.join(OUT, "tips.json"), "w") as fh:
        json.dump(tips, fh, indent=1)


if __name__ == "__main__":
    main()
