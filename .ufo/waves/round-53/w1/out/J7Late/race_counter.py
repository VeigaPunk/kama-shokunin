#!/usr/bin/env python3
"""J7Late end-to-end race: does the FROZEN counter still report code=1 when a library is
rewritten in place right after its one /proc/<pid>/mem read?

The counter writes <scratch>/r53c1-*/wd-b1/release immediately AFTER code_observe() has
returned. This driver starts the counter, reads the announced server pid from wd-b1/
ready.json, waits for wd-b1/release to appear (proof the read is over), then flips one
byte in that run's unpacked libggml-rpc.so (same inode, O_RDWR) while the server is still
alive, and records the counter's verdict.
"""
import glob
import hashlib
import json
import os
import subprocess
import sys
import time

S = os.environ["S"]
LANE = os.path.join(S, "lane")
COUNTER = os.path.join(LANE, "tools", "round53-replay-code-audit.py")
TIP = "c22602bd8d83ab26349d1087e916ca537ee4f9d1"
SCRATCH = os.path.join(S, "ctr")
OUT = os.path.join(S, "c1-race.out")
RPC = "libggml-rpc.so"
BYTE_OFF = 0x22000       # file offset of the byte in libggml-rpc.so's r-x range
EV = {}


def sha_path(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def alive(pid):
    try:
        with open(f"/proc/{pid}/stat") as fh:
            return fh.read().split()[2] != "Z"
    except OSError:
        return False


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    log = open(os.path.join(S, "c1-race.log"), "wb")
    p = subprocess.Popen([sys.executable, COUNTER, "--repo", LANE, "--tip", TIP,
                          "--scratch", SCRATCH, "--out", OUT],
                         cwd=LANE, stdout=log, stderr=subprocess.STDOUT,
                         start_new_session=True)
    t0 = time.monotonic()
    ready, pid, port, wd = None, None, None, None
    deadline = t0 + 900
    while time.monotonic() < deadline and ready is None and p.poll() is None:
        for cand in glob.glob(os.path.join(SCRATCH, "r53c1-*", "wd-b1", "ready.json")):
            try:
                r = json.load(open(cand))
            except (OSError, ValueError):
                continue
            if isinstance(r.get("pid"), int) and isinstance(r.get("port"), int):
                ready, pid, port = r, r["pid"], r["port"]
                wd = os.path.dirname(cand)
                break
        time.sleep(0.002)
    if ready is None:
        print("no ready.json; counter exit", p.poll())
        print(open(os.path.join(S, "c1-race.log"), "rb").read()[-3000:].decode("utf-8", "replace"))
        return 3
    EV["ready"] = ready
    EV["ready_after_ctr_start_s"] = round(time.monotonic() - t0, 3)
    print("ready", ready, "after", EV["ready_after_ctr_start_s"], "s")
    # wait for the counter's release file: it is written after code_observe() returned
    release = os.path.join(wd, "release")
    t_ready = time.monotonic()
    while time.monotonic() < deadline and not os.path.exists(release) and p.poll() is None:
        time.sleep(0.002)
    have_release = os.path.exists(release)
    t_rel = time.monotonic()
    EV["release_seen"] = have_release
    EV["release_after_ready_s"] = round(t_rel - t_ready, 4)
    EV["server_alive_at_release"] = alive(pid)
    if not have_release:
        print("no release file; counter exit", p.poll())
        return 4
    rpc = os.path.join(os.path.dirname(wd), "work-b1", "server", "llama-b11909", RPC)
    EV["rpc"] = rpc
    if not os.path.exists(rpc):
        print("unpacked rpc absent:", rpc)
        return 5
    st = os.stat(rpc)
    EV["before"] = {"inode": st.st_ino, "nlink": st.st_nlink, "sha256": sha_path(rpc)}
    with open(rpc, "rb") as fh:
        fh.seek(BYTE_OFF)
        orig = fh.read(1)
    fd = os.open(rpc, os.O_RDWR)
    try:
        os.pwrite(fd, bytes([orig[0] ^ 0xFF]), BYTE_OFF)
        os.fsync(fd)
    finally:
        os.close(fd)
    t_flip = time.monotonic()
    st2 = os.stat(rpc)
    EV["flip"] = {"after_release_s": round(t_flip - t_rel, 4),
                  "byte": f"{orig.hex()}->{bytes([orig[0] ^ 0xFF]).hex()}",
                  "same_inode": st2.st_ino == st.st_ino,
                  "sha256_now": sha_path(rpc),
                  "server_alive": alive(pid)}
    print("flipped", EV["flip"])
    # when does the server die?
    t_dead = None
    while time.monotonic() < deadline and p.poll() is None:
        if not alive(pid):
            if t_dead is None:
                t_dead = time.monotonic()
            break
        time.sleep(0.002)
    EV["server_dead_after_flip_s"] = round(t_dead - t_flip, 4) if t_dead else None
    code = p.wait(timeout=300)
    log.close()
    EV["counter_exit"] = code
    EV["counter_output"] = open(OUT).read() if os.path.exists(OUT) else None
    EV["server_alive_after_counter"] = alive(pid)
    print("counter exit", code)
    print(EV["counter_output"])
    with open(os.path.join(S, "race-evidence.json"), "w") as fh:
        json.dump(EV, fh, indent=1)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except BaseException:
        import traceback
        traceback.print_exc()
        rc = 5
    try:
        json.dump(EV, open(os.path.join(S, "race-evidence.json"), "w"), indent=1)
    except BaseException:
        pass
    sys.exit(rc)
