#!/usr/bin/env python3
"""J7Late probe run 5: where inside the single pass each executable range is read.

Instruments (does not edit) the frozen code_observe(): os.pread is wrapped to time every
read the frozen function makes of /proc/<pid>/mem, so the one pass can be placed on a
timeline: a rewrite of a range already read during the pass is invisible to the rest of
the pass.
"""
import glob
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import traceback

S = os.environ["S"]
LANE = os.path.join(S, "lane")
WORK = os.path.join(S, "work5")
WD = os.path.join(S, "wd5")
OUT = os.path.join(S, "out5.json")
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
    log = open(os.path.join(S, "replay5.log"), "wb")
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
    rpc = os.path.join(tree, "llama-b11909", RPC)
    # maps order of the tree rows, as code_observe walks them
    rows = []
    with open(f"/proc/{pid}/maps") as fh:
        for line in fh.read().splitlines():
            f = line.split(None, 5)
            if (len(f) < 6 or "x" not in f[1] or not f[5].startswith("/")
                    or f[5].startswith("/memfd:")):
                continue
            lo, hi = (int(v, 16) for v in f[0].split("-"))
            rows.append({"range": f[0], "path": f[5], "bytes": hi - lo,
                         "in_tree": f[5].startswith(tree + os.sep)})
    EV["maps_rows"] = rows
    env_pread = os.pread
    calls = []
    tstart = [None]

    def timed(fd, n, off):
        t = time.monotonic()
        b = env_pread(fd, n, off)
        dt = time.monotonic() - t
        if tstart[0] is None:
            tstart[0] = t
        calls.append({"off": off, "n": n, "s": round(dt, 5),
                      "at": round(t - tstart[0], 5)})
        return b
    os.pread = timed
    try:
        probs = []
        cobs = mod.code_observe(pid, tree, arc, probs)
    finally:
        os.pread = env_pread
    EV["code_observe"] = {"probs": probs,
                          "ranges": cobs["ranges"] if cobs else None,
                          "files": sorted(os.path.basename(m) for _d, _i, m in cobs["files"].values())
                          if cobs else None}
    EV["pread_calls"] = calls
    EV["pass_total_s"] = round(sum(c["s"] for c in calls), 4)
    by_off = {c["off"]: c for c in calls}
    named = []
    for r in rows:
        if not r["in_tree"]:
            continue
        lo = int(r["range"].split("-")[0], 16)
        c = by_off.get(lo)
        named.append({**r, "read_at_s": c["at"] if c else None,
                      "read_s": c["s"] if c else None})
    EV["tree_reads"] = named
    rpc_row = next((n for n in named if n["path"] == rpc), None)
    EV["rpc_read_at_s"] = rpc_row["read_at_s"] if rpc_row else None
    EV["rpc_read_s"] = rpc_row["read_s"] if rpc_row else None
    EV["bytes_before_rpc"] = sum(n["bytes"] for n in named
                                 if rpc_row and n["read_at_s"] is not None
                                 and rpc_row["read_at_s"] is not None
                                 and n["read_at_s"] < rpc_row["read_at_s"])
    EV["rpc_member_digest"] = hashlib.sha256(arc.member("llama-b11909/" + RPC)).hexdigest()
    with open(os.path.join(WD, "release"), "w") as fh:
        fh.write("released by J7Late probe run5\n")
    code = p.wait(timeout=300)
    log.close()
    EV["replay_exit"] = code
    EV["port_refuses"] = mod.port_refuses(ready["port"])
    EV["stamps_s"] = T
    with open(os.path.join(S, "probe5-evidence.json"), "w") as fh:
        json.dump(EV, fh, indent=1, default=str)
    print(json.dumps({k: EV[k] for k in ("code_observe", "rpc_read_at_s", "rpc_read_s",
                                          "pass_total_s", "replay_exit", "port_refuses")}, indent=1))
    for n in named:
        print(f"{n['path'].split('/')[-1]:28s} {n['bytes']:>9d} read at {n['read_at_s']} s "
              f"({n['read_s']} s)")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except BaseException:
        traceback.print_exc()
        rc = 5
    try:
        json.dump(EV, open(os.path.join(S, "probe5-evidence.json"), "w"), indent=1, default=str)
    except BaseException:
        pass
    sys.exit(rc)
