#!/usr/bin/env python3
"""J7Late probe run 2: the frozen counter's exact observation order, then the honest window.

The frozen counter's code leg per receipt is: wait_ready (0.2 s poll) -> observe() (nonce
round trip) -> sealed_exe() (hash /proc/<pid>/exe) -> code_observe() (ONE read of every
executable range from /proc/<pid>/mem) -> write wd/release -> wait for the replay -> check
the rerun receipt's code_mappings and the replay's own_code.

Run 2 replays that order with the frozen counter's own functions (imported), then flips a
byte IN PLACE in libggml-rpc.so's executable range AFTER that read and leaves it flipped,
reads the range once more (a second read catches it), releases at once, and reads the final
artifacts: does the rerun still match, is own_code still verified, and what did the
receipt's code_mappings record?
"""
import glob
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
import traceback

S = os.environ["S"]
LANE = os.path.join(S, "lane")
WORK = os.path.join(S, "work2")
WD = os.path.join(S, "wd2")
OUT = os.path.join(S, "out2.json")
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


def stamp(name):
    T[name] = round(time.monotonic() - T0, 4)
    return T[name]


def sha_path(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_counter():
    spec = importlib.util.spec_from_file_location(
        "r53c1", os.path.join(TOOLS, "round53-replay-code-audit.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def xrows(pid, path):
    out = []
    with open(f"/proc/{pid}/maps") as fh:
        for line in fh.read().splitlines():
            f = line.split(None, 5)
            if len(f) < 6 or "x" not in f[1]:
                continue
            if f[5] in (path, path + " (deleted)"):
                out.append((f[0], f[1], f[2], f[3], f[4], f[5]))
    return out


def smaps_for(pid, rng):
    """raw smaps block for `rng` plus the diagnostic if it is missing."""
    lines = open(f"/proc/{pid}/smaps").read().splitlines()
    headers = [ln for ln in lines if ln[:1] not in (" ", "\t")]
    for i, ln in enumerate(lines):
        if ln[:1] not in (" ", "\t") and ln.split()[0] == rng:
            block = [ln]
            for nxt in lines[i + 1:]:
                if nxt[:1] not in (" ", "\t"):
                    break
                block.append(nxt)
            return {"found": True, "raw": block,
                    "fields": {p.split(":")[0]: p.split(":", 1)[1].strip()
                               for p in block[1:] if ":" in p}}
    return {"found": False, "headers_with_rx": [h for h in headers if "r-xp" in h][:12],
            "n_headers": len(headers)}


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
    log = open(os.path.join(S, "replay2.log"), "wb")
    p = subprocess.Popen(argv, env=env, cwd=LANE, stdout=log, stderr=log, start_new_session=True)
    print("replay pid", p.pid)
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
        print("NO READY exit", p.poll())
        print(open(os.path.join(S, "replay2.log"), "rb").read()[-4000:].decode("utf-8", "replace"))
        return 3
    stamp("ready")
    pid, port = ready["pid"], ready["port"]
    EV["ready"] = ready
    tree = os.path.realpath(os.path.join(WORK, "server"))
    archive = [a for a in glob.glob(os.path.join(WORK, "download", "*")) if a.endswith(".tar.gz")][0]
    model = [a for a in glob.glob(os.path.join(WORK, "download", "*")) if a.endswith(".gguf")][0]
    member = os.path.relpath(os.path.join(tree, "llama-b11909", RPC), tree)
    mod = load_counter()
    arc = mod.Archive(archive)
    data = arc.member(member)
    EV.update({"tree": tree, "archive": archive, "member": member,
               "member_sha256": hashlib.sha256(data).hexdigest()})
    rpc = os.path.join(tree, member)
    st0 = os.stat(rpc)
    EV["path_before"] = {"inode": st0.st_ino, "nlink": st0.st_nlink, "uid": st0.st_uid,
                         "sha256": sha_path(rpc)}
    rows = xrows(pid, rpc)
    lo, hi = (int(v, 16) for v in rows[0][0].split("-"))
    off = int(rows[0][2], 16)
    EV["rows"] = [list(r) for r in rows]
    EV["smaps_before"] = smaps_for(pid, rows[0][0])

    # ---- the frozen counter's observation order, timed
    vocab = mod.gguf_tokens(model)
    probs = []
    t = time.monotonic()
    nonce, mapped = mod.observe(pid, port, vocab, "KAMA_R51_CANARY", probs)
    EV["observe"] = {"s": round(time.monotonic() - t, 4), "probs": probs, "nonce": nonce}
    stamp("observe_done")
    oprobs = []
    t = time.monotonic()
    obs = mod.sealed_exe(pid, oprobs)
    EV["sealed_exe"] = {"s": round(time.monotonic() - t, 4), "probs": oprobs,
                        "link": obs[2] if obs else None}
    stamp("sealed_done")
    cprobs = []
    t = time.monotonic()
    cobs = mod.code_observe(pid, tree, arc, cprobs)
    EV["code_observe_T1"] = {"s": round(time.monotonic() - t, 4), "probs": cprobs,
                             "ranges": cobs["ranges"],
                             "files": sorted(os.path.basename(m) for _d, _i, m in cobs["files"].values())}
    EV["T1_after_ready_s"] = stamp("T1") - T["ready"]
    print("T1 after ready:", EV["T1_after_ready_s"], "s; code_observe probs:", cprobs)
    base = read_mem(pid, lo, hi)
    want = data[off:off + (hi - lo)]
    EV["T1_mem_equal_member"] = base == want

    # ---- flip in place AFTER the counter's read, leave it flipped
    delta = (hi - lo) // 2
    abs_off = off + delta
    orig, new = data[abs_off:abs_off + 1], bytes([data[abs_off] ^ 0xFF])
    fd = os.open(rpc, os.O_RDWR)
    try:
        os.pwrite(fd, new, abs_off)
        os.fsync(fd)
    finally:
        os.close(fd)
    stamp("flip")
    EV["flip"] = {"file_offset": hex(abs_off), "range_offset": delta,
                  "byte": f"{orig.hex()}->{new.hex()}", "inode": os.stat(rpc).st_ino,
                  "nlink": os.stat(rpc).st_nlink, "sha256_now": sha_path(rpc)}
    after = read_mem(pid, lo, hi)
    n = sum(1 for a, b in zip(after, want) if a != b)
    EV["after_flip_mem"] = {"equal": after == want, "n_diff": n,
                            "mem_byte_at_flip": after[delta:delta + 1].hex()}
    EV["smaps_after_flip"] = smaps_for(pid, rows[0][0])
    stamp("flip_mem_read")
    # a second read catches it (the miss is the single sample, not blindness)
    cprobs2 = []
    cobs2 = mod.code_observe(pid, tree, arc, cprobs2)
    EV["code_observe_T2_post_flip"] = {"probs": cprobs2, "ranges": cobs2["ranges"] if cobs2 else None}
    stamp("T2_second_read")

    # ---- release immediately (what the counter does right after its one read)
    with open(os.path.join(WD, "release"), "w") as fh:
        fh.write("released by J7Late probe run2\n")
    stamp("release")
    code = p.wait(timeout=300)
    stamp("replay_exit")
    log.close()
    EV["replay_exit"] = code
    EV["post_read_window_s"] = round(T["replay_exit"] - T["release"], 4)
    alive = []
    try:
        os.kill(pid, 0)
        alive.append(pid)
    except OSError:
        pass
    EV["server_alive_after"] = alive
    EV["port_refuses_after"] = mod.port_refuses(port)
    if os.path.exists(OUT):
        j = json.load(open(OUT))
        EV["out_match"] = j.get("match")
        EV["out_mismatches"] = j.get("mismatches")
        EV["own_code"] = j.get("own_code")
        EV["live_exit"] = j.get("live_exit")
        rr_path = j.get("rerun_receipt")
        if rr_path and os.path.exists(rr_path):
            shutil.copy(rr_path, os.path.join(S, "rerun-receipt2.json"))
            rr = json.load(open(rr_path))
            EV["receipt_rpc_entries"] = [e for e in (rr.get("code_mappings") or {}).get("mappings", [])
                                         if RPC in str(e.get("path"))]
            EV["receipt_witness"] = rr.get("witness")
            EV["receipt_outcome"] = rr.get("outcome")
            EV["receipt_started_utc"] = rr.get("started_utc")
            EV["receipt_ended_utc"] = rr.get("ended_utc")
            EV["receipt_mtime"] = os.stat(rr_path).st_mtime
    else:
        print("no out2.json; log tail")
        print(open(os.path.join(S, "replay2.log"), "rb").read()[-4000:].decode("utf-8", "replace"))
    EV["stamps_s"] = T
    with open(os.path.join(S, "probe2-evidence.json"), "w") as fh:
        json.dump(EV, fh, indent=1, default=str)
    print("\n=== RUN2 SUMMARY ===")
    print(json.dumps({k: EV.get(k) for k in (
        "T1_after_ready_s", "code_observe_T1", "T1_mem_equal_member", "flip",
        "after_flip_mem", "code_observe_T2_post_flip", "post_read_window_s",
        "server_alive_after", "port_refuses_after", "out_match", "out_mismatches",
        "own_code", "receipt_rpc_entries", "receipt_witness", "receipt_outcome",
        "smaps_before", "smaps_after_flip", "stamps_s")}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except BaseException:
        traceback.print_exc()
        rc = 5
    try:
        with open(os.path.join(S, "probe2-evidence.json"), "w") as fh:
            json.dump(EV, fh, indent=1, default=str)
    except BaseException:
        pass
    sys.exit(rc)
