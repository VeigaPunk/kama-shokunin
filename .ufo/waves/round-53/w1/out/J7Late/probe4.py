#!/usr/bin/env python3
"""J7Late probe run 4: is the counter's "single read" an instant, or a 0.3 s pass?

code_observe() walks /proc/<pid>/maps in address order and os.pread()s each executable
range in turn. Run 4 runs the FROZEN code_observe() in a thread and flips one byte in
libggml-rpc.so's r-x range after a growing delay, restoring it after each pass: the delay
at which the pass stops reporting the flip is the moment that range was read.
"""
import glob
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import threading
import time
import traceback

S = os.environ["S"]
LANE = os.path.join(S, "lane")
WORK = os.path.join(S, "work4")
WD = os.path.join(S, "wd4")
OUT = os.path.join(S, "out4.json")
RECEIPT = os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-1.json")
TOOLS = os.path.join(LANE, "tools")
REPLAY = os.path.join(TOOLS, "kama-live-replay.py")
INVOKER = ("import subprocess, sys\n"
           "sys.exit(subprocess.call(sys.argv[1:]))\n")
PASS_ENV = ("PATH", "LANG", "http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
            "NO_PROXY", "no_proxy")
RPC = "libggml-rpc.so"
EV, T = {}, {}
T0 = time.monotonic()


def stamp(n):
    T[n] = round(time.monotonic() - T0, 4)


def sha_path(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def load_counter():
    spec = importlib.util.spec_from_file_location(
        "r53c1", os.path.join(TOOLS, "round53-replay-code-audit.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    os.makedirs(WD, exist_ok=True)
    home, tmp = os.path.join(S, "home"), os.path.join(S, "tmp")
    os.makedirs(os.path.join(home, ".cache"), exist_ok=True)
    os.makedirs(tmp, exist_ok=True)
    env = {k: os.environ[k] for k in PASS_ENV if k in os.environ}
    env.update({"HOME": home, "XDG_CACHE_HOME": os.path.join(home, ".cache"), "TMPDIR": tmp})
    argv = [sys.executable, "-I", "-c", INVOKER, sys.executable, "-I", REPLAY,
            "--receipt", RECEIPT, "--work", WORK, "--out", OUT, "--witness-dir", WD]
    log = open(os.path.join(S, "replay4.log"), "wb")
    p = subprocess.Popen(argv, env=env, cwd=LANE, stdout=log, stderr=log, start_new_session=True)
    ready, deadline = None, time.monotonic() + 600
    while time.monotonic() < deadline and p.poll() is None:
        try:
            r = json.load(open(os.path.join(WD, "ready.json")))
        except (OSError, ValueError):
            r = None
        if isinstance(r, dict) and isinstance(r.get("pid"), int) and isinstance(r.get("port"), int):
            ready = r
            break
        time.sleep(0.005)
    if ready is None:
        print("NO READY", p.poll())
        return 3
    stamp("ready")
    pid = ready["pid"]
    tree = os.path.realpath(os.path.join(WORK, "server"))
    archive = [a for a in glob.glob(os.path.join(WORK, "download", "*")) if a.endswith(".tar.gz")][0]
    mod = load_counter()
    arc = mod.Archive(archive)
    member = os.path.relpath(os.path.join(tree, "llama-b11909", RPC), tree)
    data = arc.member(member)
    rpc = os.path.join(tree, member)
    # the pass's order and sizes, straight from maps
    order = []
    with open(f"/proc/{pid}/maps") as fh:
        for line in fh.read().splitlines():
            f = line.split(None, 5)
            if len(f) < 6 or "x" not in f[1] or not f[5].startswith("/") or f[5].startswith("/memfd:"):
                continue
            lo, hi = (int(v, 16) for v in f[0].split("-"))
            order.append({"range": f[0], "perm": f[1], "off": f[2], "dev": f[3],
                          "inode": f[4], "path": f[5], "bytes": hi - lo,
                          "is_rpc": f[5] == rpc})
    EV["pass_order"] = order
    EV["pass_total_bytes"] = sum(o["bytes"] for o in order)
    rpc_i = next(i for i, o in enumerate(order) if o["is_rpc"])
    EV["rpc_index_in_pass"] = rpc_i
    EV["bytes_before_rpc"] = sum(o["bytes"] for o in order[:rpc_i])
    rows = [o for o in order if o["is_rpc"]]
    lo, hi = (int(v, 16) for v in rows[0]["range"].split("-"))
    off = int(rows[0]["off"], 16)
    want = data[off:off + (hi - lo)]
    delta = (hi - lo) // 2
    abs_off = off + delta
    orig, new = data[abs_off:abs_off + 1], bytes([data[abs_off] ^ 0xFF])
    EV["flip"] = {"file_offset": hex(abs_off), "byte": f"{orig.hex()}->{new.hex()}",
                  "member_sha256": hashlib.sha256(data).hexdigest()}

    def pass_verdict(delay):
        probs = []
        box = {}

        def run():
            t = time.monotonic()
            cobs = mod.code_observe(pid, tree, arc, probs)
            box["s"] = round(time.monotonic() - t, 4)
            box["ranges"] = cobs["ranges"] if cobs else None
            box["files"] = len(cobs["files"]) if cobs else None
        th = threading.Thread(target=run)
        t0 = time.monotonic()
        th.start()
        time.sleep(delay)
        t_flip = time.monotonic() - t0
        fd = os.open(rpc, os.O_RDWR)
        try:
            os.pwrite(fd, new, abs_off)
            os.fsync(fd)
        finally:
            os.close(fd)
        th.join()
        fd = os.open(rpc, os.O_RDWR)
        try:
            os.pwrite(fd, orig, abs_off)
            os.fsync(fd)
        finally:
            os.close(fd)
        return {"delay_s": round(delay, 3), "flip_at_s": round(t_flip, 3),
                "pass_s": box.get("s"), "ranges": box.get("ranges"),
                "files": box.get("files"), "caught": bool(probs), "probs": probs,
                "sha_restored": sha_path(rpc) == hashlib.sha256(data).hexdigest()}

    trials = []
    for d in (0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15, 0.18, 0.21, 0.24, 0.27, 0.30, 0.33):
        trials.append(pass_verdict(d))
        print(json.dumps(trials[-1])[:300])
    EV["trials"] = trials
    first_miss = next((t["delay_s"] for t in trials if not t["caught"]), None)
    EV["first_miss_delay_s"] = first_miss
    with open(os.path.join(WD, "release"), "w") as fh:
        fh.write("released by J7Late probe run4\n")
    stamp("release")
    code = p.wait(timeout=300)
    stamp("exit")
    log.close()
    EV["replay_exit"] = code
    EV["port_refuses"] = mod.port_refuses(ready["port"])
    EV["stamps_s"] = T
    with open(os.path.join(S, "probe4-evidence.json"), "w") as fh:
        json.dump(EV, fh, indent=1, default=str)
    print("\nfirst miss delay:", first_miss, "pass bytes:", EV["pass_total_bytes"],
          "rpc index", rpc_i, "bytes before rpc", EV["bytes_before_rpc"])
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except BaseException:
        traceback.print_exc()
        rc = 5
    try:
        json.dump(EV, open(os.path.join(S, "probe4-evidence.json"), "w"), indent=1, default=str)
    except BaseException:
        pass
    sys.exit(rc)
