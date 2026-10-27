#!/usr/bin/env python3
"""J7Late probe run 3: residency and accounting of the flipped page.

Same replay drive as run 1/2; captures /proc/<pid>/smaps for libggml-rpc.so's r-x range
before the mem read, after the mem read, and after an in-place flip of one byte, to say
whether the page is resident and whether the private file mapping was copied.
"""
import glob
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import traceback

S = os.environ["S"]
LANE = os.path.join(S, "lane")
WORK = os.path.join(S, "work3")
WD = os.path.join(S, "wd3")
OUT = os.path.join(S, "out3.json")
RECEIPT = os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-1.json")
TOOLS = os.path.join(LANE, "tools")
REPLAY = os.path.join(TOOLS, "kama-live-replay.py")
INVOKER = ("import subprocess, sys\n"
           "sys.exit(subprocess.call(sys.argv[1:]))\n")
PASS_ENV = ("PATH", "LANG", "http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
            "NO_PROXY", "no_proxy")
RPC = "libggml-rpc.so"
HDR = re.compile(r"^[0-9a-f]+-[0-9a-f]+ ")
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


def smaps_block(pid, rng):
    lines = open(f"/proc/{pid}/smaps").read().splitlines()
    for i, ln in enumerate(lines):
        if HDR.match(ln) and ln.split()[0] == rng:
            block = [ln]
            for nxt in lines[i + 1:]:
                if HDR.match(nxt):
                    break
                block.append(nxt)
            return {"header": ln,
                    "fields": {p.split(":")[0]: p.split(":", 1)[1].strip()
                               for p in block[1:] if ":" in p},
                    "raw": block}
    return {"found": False}


def read_mem(pid, lo, hi):
    fd = os.open(f"/proc/{pid}/mem", os.O_RDONLY)
    try:
        return os.pread(fd, hi - lo, lo)
    finally:
        os.close(fd)


def main():
    os.makedirs(WD, exist_ok=True)
    home, tmp = os.path.join(S, "home"), os.path.join(S, "tmp")
    os.makedirs(os.path.join(home, ".cache"), exist_ok=True)
    os.makedirs(tmp, exist_ok=True)
    env = {k: os.environ[k] for k in PASS_ENV if k in os.environ}
    env.update({"HOME": home, "XDG_CACHE_HOME": os.path.join(home, ".cache"), "TMPDIR": tmp})
    argv = [sys.executable, "-I", "-c", INVOKER, sys.executable, "-I", REPLAY,
            "--receipt", RECEIPT, "--work", WORK, "--out", OUT, "--witness-dir", WD]
    log = open(os.path.join(S, "replay3.log"), "wb")
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
    member = os.path.relpath(os.path.join(tree, "llama-b11909", RPC), tree)
    mod = load_counter()
    arc = mod.Archive(archive)
    data = arc.member(member)
    rpc = os.path.join(tree, member)
    with open(f"/proc/{pid}/maps") as fh:
        rows = [ln.split(None, 5) for ln in fh.read().splitlines()
                if len(ln.split(None, 5)) >= 6 and "x" in ln.split(None, 5)[1]
                and ln.split(None, 5)[5] in (rpc, rpc + " (deleted)")]
    rng = rows[0][0]
    lo, hi = (int(v, 16) for v in rng.split("-"))
    off = int(rows[0][2], 16)
    EV.update({"member_sha256": hashlib.sha256(data).hexdigest(), "range": rng,
               "offset": hex(off), "len": hi - lo,
               "smaps_window_kb": (hi - lo) // 1024})
    EV["before_read"] = smaps_block(pid, rng)
    base = read_mem(pid, lo, hi)
    want = data[off:off + (hi - lo)]
    EV["mem_equal"] = base == want
    EV["after_read"] = smaps_block(pid, rng)
    delta = (hi - lo) // 2
    abs_off = off + delta
    orig = data[abs_off:abs_off + 1]
    new = bytes([orig[0] ^ 0xFF])
    fd = os.open(rpc, os.O_RDWR)
    try:
        os.pwrite(fd, new, abs_off)
        os.fsync(fd)
    finally:
        os.close(fd)
    stamp("flip")
    EV["flip"] = {"file_offset": hex(abs_off), "byte": f"{orig.hex()}->{new.hex()}",
                  "same_inode": os.stat(rpc).st_ino == int(rows[0][4]),
                  "sha256_now": sha_path(rpc)}
    EV["after_flip_no_read"] = smaps_block(pid, rng)
    after = read_mem(pid, lo, hi)
    EV["after_flip_mem"] = {"equal": after == want,
                            "n_diff": sum(1 for a, b in zip(after, want) if a != b),
                            "byte_at_flip": after[delta:delta + 1].hex()}
    EV["after_flip_read"] = smaps_block(pid, rng)
    # restore so nothing is left modified
    fd = os.open(rpc, os.O_RDWR)
    try:
        os.pwrite(fd, orig, abs_off)
        os.fsync(fd)
    finally:
        os.close(fd)
    EV["restored_sha256"] = sha_path(rpc)
    EV["restored_mem_equal"] = read_mem(pid, lo, hi) == want
    with open(os.path.join(WD, "release"), "w") as fh:
        fh.write("released by J7Late probe run3\n")
    stamp("release")
    code = p.wait(timeout=300)
    stamp("exit")
    log.close()
    EV["replay_exit"] = code
    EV["port_refuses"] = mod.port_refuses(ready["port"])
    EV["stamps_s"] = T
    with open(os.path.join(S, "probe3-evidence.json"), "w") as fh:
        json.dump(EV, fh, indent=1, default=str)
    print(json.dumps(EV, indent=1, default=str))
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except BaseException:
        traceback.print_exc()
        rc = 5
    try:
        json.dump(EV, open(os.path.join(S, "probe3-evidence.json"), "w"), indent=1, default=str)
    except BaseException:
        pass
    sys.exit(rc)
