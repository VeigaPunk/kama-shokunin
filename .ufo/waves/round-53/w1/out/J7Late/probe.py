#!/usr/bin/env python3
"""J7Late time-of-observation probe for kama round-53 C1.

Drives tools/kama-live-replay.py exactly as the frozen C1 counter's start_replay() does
(invoker, isolated env, --work/--out/--witness-dir), holds the server, then:

  T0      the live tool records receipt['code_mappings'] (hashes each executable file at
          its pathname) and then publishes wd/ready.json; the hold starts.
  T1      a counter-style observation: /proc/<pid>/maps + /proc/<pid>/mem over every
          executable range of libggml-rpc.so, compared with the archive member; verdict via
          the FROZEN counter's own code_observe() (imported, not re-implemented).
  (a)     in-place rewrite: pwrite one flipped byte into libggml-rpc.so's r-x range
          (same inode, O_RDWR), then re-read /proc/<pid>/mem; restore; re-read.
  (a2)    transient swap: flip + restore with no read in between, then read.
  (b)     rename-over: replace the path with a modified copy, then read maps + mem.
  release: wd/release; wait for the replay; read out.json + the rerun receipt.

Everything lives under $S. Nothing in the lane is written.
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
WORK = os.path.join(S, "work")
WD = os.path.join(S, "wd")
OUT = os.path.join(S, "out.json")
RECEIPT = os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-1.json")
TOOLS = os.path.join(LANE, "tools")
REPLAY = os.path.join(TOOLS, "kama-live-replay.py")
INVOKER = ("import subprocess, sys\n"
           "sys.exit(subprocess.call(sys.argv[1:]))\n")
PASS_ENV = ("PATH", "LANG", "http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
            "NO_PROXY", "no_proxy")
RPC = "libggml-rpc.so"
EV = {}          # evidence accumulated
T = {}           # monotonic stamps


def stamp(name):
    T[name] = round(time.monotonic() - T0, 4)
    return T[name]


def sha_path(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_fd(fd):
    h = hashlib.sha256()
    os.lseek(fd, 0, 0)
    while True:
        chunk = os.read(fd, 1 << 20)
        if not chunk:
            break
        h.update(chunk)
    return h.hexdigest()


def load_counter():
    spec = importlib.util.spec_from_file_location(
        "r53c1", os.path.join(TOOLS, "round53-replay-code-audit.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def member_bytes(archive, name):
    mod = load_counter()
    arc = mod.Archive(archive)
    data = arc.member(name)
    if data is None:
        raise SystemExit(f"archive has no member {name}")
    return data


def xrows(pid, path):
    """executable maps rows for exactly `path` (or its ' (deleted)' spelling)."""
    out = []
    with open(f"/proc/{pid}/maps") as fh:
        for line in fh.read().splitlines():
            f = line.split(None, 5)
            if len(f) < 6 or "x" not in f[1]:
                continue
            if f[5] == path or f[5] == path + " (deleted)":
                out.append((f[0], f[1], f[2], f[3], f[4], f[5]))
    return out


def smaps_row(pid, lo_hi):
    """the smaps block for an address range, as {key: value}."""
    want = lo_hi
    block, hit = [], None
    with open(f"/proc/{pid}/smaps") as fh:
        for line in fh:
            if line[0] not in " \t":
                if hit is not None:
                    break
                if line.split()[0] == want:
                    hit = True
            if hit:
                block.append(line.rstrip())
    return {ln.split(":")[0]: ln.split(":", 1)[1].strip()
            for ln in block[1:] if ":" in ln}


def read_mem(pid, lo, hi):
    fd = os.open(f"/proc/{pid}/mem", os.O_RDONLY)
    try:
        return os.pread(fd, hi - lo, lo)
    finally:
        os.close(fd)


def diff_offsets(got, want):
    return [i for i, (a, b) in enumerate(zip(got, want)) if a != b][:16], sum(
        1 for a, b in zip(got, want) if a != b)


def verdict(mod, pid, tree, archive, label):
    probs = []
    arc = mod.Archive(archive)
    res = mod.code_observe(pid, tree, arc, probs)
    ev = {"probs": probs,
          "files": {p: list(v) for p, v in (res or {}).get("files", {}).items()},
          "host": (res or {}).get("host"), "ranges": (res or {}).get("ranges")}
    EV[label] = ev
    print(f"--- code_observe[{label}] files={list(ev['files'])} ranges={ev['ranges']} "
          f"host={ev['host']} probs={probs}")
    return ev


def main():
    global T0
    T0 = time.monotonic()
    os.makedirs(WD, exist_ok=True)
    home = os.path.join(S, "home")
    tmp = os.path.join(S, "tmp")
    os.makedirs(os.path.join(home, ".cache"), exist_ok=True)
    os.makedirs(tmp, exist_ok=True)
    env = {k: os.environ[k] for k in PASS_ENV if k in os.environ}
    env.update({"HOME": home, "XDG_CACHE_HOME": os.path.join(home, ".cache"), "TMPDIR": tmp})
    # the counter's start_replay(): invoker -> python -I replay
    argv = [sys.executable, "-I", "-c", INVOKER, sys.executable, "-I", REPLAY,
            "--receipt", RECEIPT, "--work", WORK, "--out", OUT, "--witness-dir", WD]
    log = open(os.path.join(S, "replay.log"), "wb")
    p = subprocess.Popen(argv, env=env, cwd=LANE, stdout=log, stderr=log, start_new_session=True)
    EV["replay_argv"] = argv
    print("replay started pid", p.pid, "argv", argv[2:])
    ready = None
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline and p.poll() is None:
        try:
            with open(os.path.join(WD, "ready.json")) as fh:
                r = json.load(fh)
        except (OSError, ValueError):
            r = None
        if isinstance(r, dict) and isinstance(r.get("pid"), int) and isinstance(r.get("port"), int):
            ready = r
            break
        time.sleep(0.005)
    if ready is None:
        print("NO READY; exit", p.poll())
        print(open(os.path.join(S, "replay.log"), "rb").read()[-4000:].decode("utf-8", "replace"))
        return 3
    stamp("ready_seen")
    EV["ready"] = ready
    EV["ready_mtime"] = os.stat(os.path.join(WD, "ready.json")).st_mtime
    pid, port = ready["pid"], ready["port"]
    print("ready:", ready, "after", T["ready_seen"], "s")
    tree = os.path.realpath(os.path.join(WORK, "server"))
    archs = glob.glob(os.path.join(WORK, "download", "*"))
    archive = [a for a in archs if a.endswith(".tar.gz")][0]
    EV["tree"] = tree
    EV["archive"] = archive
    member = os.path.relpath(os.path.join(tree, "llama-b11909", RPC), tree)
    data = member_bytes(archive, member)
    EV["member"] = member
    EV["member_sha256"] = hashlib.sha256(data).hexdigest()
    rpc_path = os.path.join(tree, member)
    st0 = os.stat(rpc_path)
    EV["path_stat_before"] = {"dev": "%02x:%02x" % (os.major(st0.st_dev), os.minor(st0.st_dev)),
                              "inode": st0.st_ino, "nlink": st0.st_nlink, "uid": st0.st_uid,
                              "size": st0.st_size, "mode": oct(st0.st_mode),
                              "sha256": sha_path(rpc_path)}
    rows = xrows(pid, rpc_path)
    EV["xrows"] = [list(r) for r in rows]
    print("x rows:", len(rows), rows[:1])
    if not rows:
        print("NO x ROW for", rpc_path)
        return 4
    # counter-style observations timed: T1 = after a 35MB /proc/pid/exe hash (sealed leg)
    t = time.monotonic()
    sha_path(f"/proc/{pid}/exe")
    EV["exe_hash_s"] = round(time.monotonic() - t, 4)
    t = time.monotonic()
    verdict(load_counter(), pid, tree, archive, "T1_baseline")
    EV["code_observe_baseline_s"] = round(time.monotonic() - t, 4)
    stamp("T1_baseline_done")
    lo, hi = (int(v, 16) for v in rows[0][0].split("-"))
    off = int(rows[0][2], 16)
    EV["range"] = {"lo": hex(lo), "hi": hex(hi), "off": hex(off), "len": hi - lo,
                   "perms": rows[0][1], "dev": rows[0][3], "inode": rows[0][4]}
    base_mem = read_mem(pid, lo, hi)
    want = data[off:off + (hi - lo)]
    EV["baseline_mem_equal_member"] = base_mem == want
    EV["baseline_smaps"] = smaps_row(pid, rows[0][0])
    print("baseline mem == member:", base_mem == want, "rss:", EV["baseline_smaps"].get("Rss"))

    # ---- (a) in-place rewrite of the file's r-x range (same inode, O_RDWR)
    delta = (hi - lo) // 2
    abs_off = off + delta
    orig = data[abs_off:abs_off + 1]
    new = bytes([orig[0] ^ 0xFF])
    try:
        fd = os.open(rpc_path, os.O_RDWR)
        EV["open_rdwr"] = "ok"
    except OSError as exc:
        EV["open_rdwr"] = f"{exc.errno}:{exc.strerror}"
        print("OPEN O_RDWR FAILED", EV["open_rdwr"])
        fd = None
    if fd is not None:
        try:
            os.pwrite(fd, new, abs_off)
            os.fsync(fd)
            EV["pwrite"] = f"ok byte {orig.hex()}->{new.hex()} at file offset {hex(abs_off)}"
        except OSError as exc:
            EV["pwrite"] = f"{exc.errno}:{exc.strerror}"
            print("PWRITE FAILED", EV["pwrite"])
        finally:
            os.close(fd)
        stamp("flip_written")
        after = read_mem(pid, lo, hi)
        offs, n = diff_offsets(after, want)
        EV["inplace_mem_vs_member"] = {"equal": after == want, "n_diff_bytes": n,
                                       "first_diff_in_range": offs[:8],
                                       "flipped_at_range_offset": delta,
                                       "mem_byte_at_flip": after[delta:delta + 1].hex(),
                                       "member_byte_at_flip": want[delta:delta + 1].hex()}
        EV["file_sha_after_flip"] = sha_path(rpc_path)
        EV["path_stat_after_flip"] = {"inode": os.stat(rpc_path).st_ino,
                                      "nlink": os.stat(rpc_path).st_nlink}
        EV["smaps_after_flip"] = smaps_row(pid, rows[0][0])
        print("in-place: mem == member after flip:", after == want,
              "diff bytes:", n, "mem at flip:", after[delta:delta + 1].hex())
        stamp("T_flip_read")
        verdict(load_counter(), pid, tree, archive, "T2_after_inplace_flip")
        # restore
        fd = os.open(rpc_path, os.O_RDWR)
        try:
            os.pwrite(fd, orig, abs_off)
            os.fsync(fd)
        finally:
            os.close(fd)
        stamp("restored")
        EV["file_sha_after_restore"] = sha_path(rpc_path)
        restored_mem = read_mem(pid, lo, hi)
        EV["restored_mem_equal_member"] = restored_mem == want
        print("restored mem == member:", restored_mem == want,
              "file sha restored:", EV["file_sha_after_restore"] == EV["member_sha256"])
        verdict(load_counter(), pid, tree, archive, "T3_after_restore")

    # ---- (a2) transient swap: flip + restore with NO observation in between
    fd = os.open(rpc_path, os.O_RDWR)
    try:
        os.pwrite(fd, new, abs_off)
        os.fsync(fd)
        os.pwrite(fd, orig, abs_off)
        os.fsync(fd)
    finally:
        os.close(fd)
    stamp("transient_done")
    EV["transient_file_sha"] = sha_path(rpc_path)
    trans = read_mem(pid, lo, hi)
    EV["transient_mem_equal_member"] = trans == want
    EV["transient_note"] = ("flip+restore with no read between: the only observable is "
                            "memory at read time; history is not recorded")
    print("transient (flip+restore, no read): mem == member", trans == want)
    verdict(load_counter(), pid, tree, archive, "T4_after_transient")

    # ---- (b) rename-over: replace the path with a modified copy
    copy = rpc_path + ".attacker"
    mod_data = bytearray(data)
    mod_data[abs_off] ^= 0xFF
    with open(copy, "wb") as fh:
        fh.write(mod_data)
    os.chmod(copy, 0o755)
    pre = os.stat(rpc_path)
    os.replace(copy, rpc_path)
    post = os.stat(rpc_path)
    stamp("rename_over")
    EV["rename_over"] = {
        "old_inode": pre.st_ino, "new_inode": post.st_ino,
        "path_sha256_now": sha_path(rpc_path),
        "same_inode": pre.st_ino == post.st_ino,
        "maps_rows": [list(r) for r in xrows(pid, rpc_path)],
    }
    rows_now = xrows(pid, rpc_path)
    if rows_now:
        lo2, hi2 = (int(v, 16) for v in rows_now[0][0].split("-"))
        mem_now = read_mem(pid, lo2, hi2)
        off2 = int(rows_now[0][2], 16)
        want2 = data[off2:off2 + (hi2 - lo2)]
        offs2, n2 = diff_offsets(mem_now, want2)
        EV["rename_over"]["mem_equal_member"] = mem_now == want2
        EV["rename_over"]["n_diff_bytes"] = n2
        EV["rename_over"]["maps_path"] = rows_now[0][5]
    verdict(load_counter(), pid, tree, archive, "T5_after_rename_over")

    # ---- release; the replay finishes as the counter's would
    with open(os.path.join(WD, "release"), "w") as fh:
        fh.write("released by J7Late probe\n")
    stamp("released")
    code = p.wait(timeout=300)
    stamp("replay_exit")
    log.close()
    EV["replay_exit"] = code
    if os.path.exists(OUT):
        with open(OUT) as fh:
            j = json.load(fh)
        EV["out_match"] = j.get("match")
        EV["out_refused"] = j.get("refused")
        EV["out_mismatches"] = j.get("mismatches")
        EV["own_code"] = j.get("own_code")
        rr_path = j.get("rerun_receipt")
        EV["rerun_receipt"] = rr_path
        if rr_path and os.path.exists(rr_path):
            shutil.copy(rr_path, os.path.join(S, "rerun-receipt.json"))
            with open(rr_path) as fh:
                rr = json.load(fh)
            cm = rr.get("code_mappings")
            ents = [e for e in (cm.get("mappings") or []) if RPC in str(e.get("path"))]
            EV["receipt_rpc_entries"] = ents
            EV["receipt_witness"] = rr.get("witness")
            EV["receipt_started_utc"] = rr.get("started_utc")
            EV["receipt_child_pid"] = rr.get("child_pid")
            EV["receipt_keys"] = sorted(rr)
            EV["receipt_mtime"] = os.stat(rr_path).st_mtime
    else:
        print("no out.json; replay log tail:")
        print(open(os.path.join(S, "replay.log"), "rb").read()[-5000:].decode("utf-8", "replace"))
    EV["stamps_s"] = T
    with open(os.path.join(S, "probe-evidence.json"), "w") as fh:
        json.dump(EV, fh, indent=1, default=str)
    print("\n=== SUMMARY ===")
    print(json.dumps({k: EV.get(k) for k in (
        "member_sha256", "path_stat_before", "range", "baseline_mem_equal_member",
        "open_rdwr", "pwrite", "inplace_mem_vs_member", "file_sha_after_flip",
        "restored_mem_equal_member", "file_sha_after_restore", "transient_file_sha",
        "transient_mem_equal_member", "rename_over", "own_code", "receipt_rpc_entries",
        "receipt_witness", "out_match", "out_mismatches", "stamps_s")}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BaseException:
        traceback.print_exc()
        try:
            with open(os.path.join(S, "probe-evidence.json"), "w") as fh:
                json.dump(EV, fh, indent=1, default=str)
        except BaseException:
            pass
        sys.exit(5)
