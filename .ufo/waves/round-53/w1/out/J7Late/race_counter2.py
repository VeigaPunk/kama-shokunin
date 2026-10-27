#!/usr/bin/env python3
"""J7Late end-to-end race v2 (tight watcher): does the FROZEN counter still report code=1
when a library is rewritten in place immediately after its one /proc/<pid>/mem read?

The counter writes <scratch>/r53c1-*/wd-b1/release as the first statement after
code_observe() returns. This driver watches for that file with a busy spin (no sleep), so
the in-place rewrite lands while the held server is still alive; it records whether the
server was alive at the flip and how long it lived after it.
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
SCRATCH = os.path.join(S, "ctr2")
OUT = os.path.join(S, "c1-race2.out")
RPC = "libggml-rpc.so"
BYTE_OFF = 0x22000
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


def attempt(n):
    os.makedirs(SCRATCH, exist_ok=True)
    log = open(os.path.join(S, f"c1-race2-{n}.log"), "wb")
    p = subprocess.Popen([sys.executable, COUNTER, "--repo", LANE, "--tip", TIP,
                          "--scratch", SCRATCH, "--out", OUT],
                         cwd=LANE, stdout=log, stderr=subprocess.STDOUT,
                         start_new_session=True)
    t0 = time.monotonic()
    ready, pid, wd = None, None, None
    deadline = t0 + 900
    while time.monotonic() < deadline and ready is None and p.poll() is None:
        for cand in glob.glob(os.path.join(SCRATCH, "r53c1-*", "wd-b1", "ready.json")):
            try:
                r = json.load(open(cand))
            except (OSError, ValueError):
                continue
            if isinstance(r.get("pid"), int):
                ready, pid, wd = r, r["pid"], os.path.dirname(cand)
                break
        time.sleep(0.001)
    if ready is None:
        return {"attempt": n, "error": "no ready.json", "counter_exit": p.poll()}
    ev = {"attempt": n, "ready": ready, "ready_after_start_s": round(time.monotonic() - t0, 3)}
    release = os.path.join(wd, "release")
    # busy spin: the flip must land inside the server's remaining life
    t_spin = time.monotonic()
    while not os.path.exists(release) and p.poll() is None and time.monotonic() < deadline:
        pass
    seen = os.path.exists(release)
    t_seen = time.time()
    ev["release_seen"] = seen
    ev["spin_s"] = round(time.monotonic() - t_spin, 4)
    if not seen:
        ev["error"] = "no release file"
        p.wait(timeout=300)
        log.close()
        return ev
    try:
        ev["release_mtime_ns"] = os.stat(release).st_mtime_ns
        ev["seen_minus_mtime_s"] = round(t_seen - ev["release_mtime_ns"] / 1e9, 4)
    except OSError:
        pass
    rpc = os.path.join(os.path.dirname(wd), "work-b1", "server", "llama-b11909", RPC)
    st = os.stat(rpc)
    ev["before"] = {"inode": st.st_ino, "nlink": st.st_nlink, "sha256": sha_path(rpc)}
    ev["server_alive_at_decision"] = alive(pid)
    with open(rpc, "rb") as fh:
        fh.seek(BYTE_OFF)
        orig = fh.read(1)
    fd = os.open(rpc, os.O_RDWR)
    try:
        os.pwrite(fd, bytes([orig[0] ^ 0xFF]), BYTE_OFF)
        os.fsync(fd)
    finally:
        os.close(fd)
    t_flip = time.time()
    ev["flip"] = {"wall_s_after_release_mtime": round(t_flip - ev.get("release_mtime_ns", 0) / 1e9, 4),
                  "byte": f"{orig.hex()}->{bytes([orig[0] ^ 0xFF]).hex()}",
                  "same_inode": os.stat(rpc).st_ino == st.st_ino,
                  "sha256_now": sha_path(rpc),
                  "server_alive": alive(pid)}
    # how long does the server survive after the flip?
    t_dead = None
    while p.poll() is None and time.monotonic() < deadline:
        if not alive(pid):
            t_dead = time.time()
            break
    ev["server_lived_after_flip_s"] = round(t_dead - t_flip, 4) if t_dead else None
    code = p.wait(timeout=300)
    log.close()
    ev["counter_exit"] = code
    ev["counter_output"] = open(OUT).read() if os.path.exists(OUT) else None
    return ev


def main():
    evs = []
    for n in (1, 2):
        e = attempt(n)
        evs.append(e)
        print(json.dumps({k: e.get(k) for k in ("attempt", "release_seen", "spin_s",
                                                "server_alive_at_decision", "flip",
                                                "server_lived_after_flip_s", "counter_exit")}, indent=1))
        if e.get("flip", {}).get("server_alive"):
            break
    EV["attempts"] = evs
    out = evs[-1].get("counter_output")
    if out:
        print(out)
    with open(os.path.join(S, "race2-evidence.json"), "w") as fh:
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
        json.dump(EV, open(os.path.join(S, "race2-evidence.json"), "w"), indent=1)
    except BaseException:
        pass
    sys.exit(rc)
