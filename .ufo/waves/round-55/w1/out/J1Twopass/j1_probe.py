#!/usr/bin/env python3
"""J1Twopass - time-of-observation probe for kama round-55 C1 (operability).

The frozen counter tools/round54-replay-code-audit.py (sha256
c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af, preregistered in
.ufo/waves/round-55/preregistration.json) reads /proc/<pid>/mem in TWO passes whose
snapshots must agree, and re-hashes the observed archive paths after the replay exits.

This probe drives the counter's OWN bind_one() (the frozen bytes, imported read-only from
the lane clone at the measured tip 9c60eae6) and instruments it WITHOUT editing it, to
measure the sampling windows and to race an out-of-process, same-uid in-place rewriter.

Modes:
  characterize  - one clean run; measures the windows.
  race          - N runs; an attacker process rewrites a mapped library's r-x range in
                  place (same path, same inode, O_RDWR + pwrite) inside a chosen window.

Usage:
  j1_probe.py characterize --receipt 1 --out char.json
  j1_probe.py race --runs 10 --hold-ms 5 --out race.json
"""
from __future__ import annotations

import argparse
import builtins
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import threading
import time
import urllib.request

S = os.environ.get("J1_S", "/fast/scratch/hyaku/kama-r55/w1/J1Twopass")
LANE = os.path.join(S, "lane")
TIP = "9c60eae6f7ed84f7da93d219a406aadc30958c6c"
TREE = os.path.join(S, "tree")
ARC = os.path.join(S, "counter-archive.tar.gz")
MODEL = os.path.join(S, "counter-model.gguf")
TARGET_LIB = "libggml-rpc.so"   # mapped, executable, and NOT on the server's hot path
PREREG_SHA = "c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af"


# ------------------------------------------------------------------ frozen counter
def load_counter():
    src = subprocess.run(["git", "-C", LANE, "show", f"{TIP}:tools/round54-replay-code-audit.py"],
                         capture_output=True, check=True).stdout
    path = os.path.join(S, "counter-frozen.py")
    with open(path, "wb") as fh:
        fh.write(src)
    sha = hashlib.sha256(src).hexdigest()
    spec = importlib.util.spec_from_file_location("r54c1", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, {"counter_sha256": sha, "prereg_counter_sha256": PREREG_SHA,
                 "counter_sha_matches_prereg": sha == PREREG_SHA}


def build_tree():
    if os.path.isdir(TREE):
        return
    arc = subprocess.run(["git", "-C", LANE, "archive", "--format=tar", TIP],
                         capture_output=True, check=True).stdout
    os.makedirs(TREE, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(arc)) as tf:
        tf.extractall(TREE, filter=lambda m, dest: None if (m.issym() or m.islnk())
                      else tarfile.data_filter(m, dest))


def fetch(url, dest, timeout=300):
    if os.path.isfile(dest):
        return dest
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(url, timeout=timeout) as r, open(dest, "wb") as fh:
        shutil.copyfileobj(r, fh)
    return dest


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def maps_rows(pid):
    out = []
    try:
        with open(f"/proc/{pid}/maps") as fh:
            for row in fh.read().splitlines():
                f = row.split(None, 5)
                if len(f) < 6:
                    continue
                lo, hi = (int(v, 16) for v in f[0].split("-"))
                out.append({"lo": lo, "hi": hi, "perms": f[1], "off": int(f[2], 16),
                            "dev": f[3], "ino": f[4], "path": f[5]})
    except OSError:
        pass
    return out


def find_x_row(pid, libname):
    for r in maps_rows(pid):
        if r["path"].split(" ")[0].endswith("/" + libname) and "x" in r["perms"]:
            return r
    return None


# ------------------------------------------------------------------- the armed run
def armed_run(mod, EV, tag, receipt, mode, hold_ms, attacker_delay_ms=0.0, verbose=True):
    """One instrumented bind_one() run with an out-of-process same-uid attacker."""
    ev = {"tag": tag, "mode": mode, "hold_ms": hold_ms}
    detail = []
    orig_code_observe = mod.code_observe
    orig_sha_file = mod.sha_file
    orig_open = builtins.open
    orig_pread = os.pread
    st = {"reads": [], "server_pid": None, "x_row": None, "fired": False, "pass_index": 0,
          "mem_obs": None, "trigger_t": None}

    def code_observe(pid, tree, arc, probs, collect=False, own=None):
        if st["server_pid"] is None:
            st["server_pid"] = pid
            st["x_row"] = find_x_row(pid, TARGET_LIB)
            ev["server_pid"] = pid
            ev["x_row"] = st["x_row"]
        st["pass_index"] += 1
        t0 = time.monotonic()
        out = orig_code_observe(pid, tree, arc, probs, collect=collect, own=own)
        t1 = time.monotonic()
        ev.setdefault("passes", []).append({
            "index": st["pass_index"], "start": t0, "end": t1,
            "dur_ms": round((t1 - t0) * 1000, 3),
            "files": None if out is None else len(out["files"]),
            "ranges": None if out is None else out["ranges"],
            "host": None if out is None else out["host"]})
        # T_pin_post2: fire right AFTER pass 2 returns (the counter's last mem read)
        if mode == "pin_post2" and st["pass_index"] == 2 and not st["fired"]:
            st["fired"] = True
            ev["t_fired"] = t1
            with orig_open(trigger, "w") as fh:
                fh.write("go")
        return out

    def sha_rec(path):
        t = time.monotonic()
        out = orig_sha_file(path)
        ev.setdefault("sha_calls", []).append({"t": t, "path": str(path), "sha256": out})
        return out

    def open_(file, mode="r", *a, **kw):
        if isinstance(file, str) and file.endswith("/release") and "w" in mode:
            ev["t_release"] = time.monotonic()
        return orig_open(file, mode, *a, **kw)

    def pread(fd, n, off):
        t = time.monotonic()
        data = orig_pread(fd, n, off)
        st["reads"].append({"t": t, "len": n, "off": off})
        row = st["x_row"]
        # fire the attacker right after PASS 1's read of the target range
        if (mode == "pin_in" and row and not st["fired"]
                and st["pass_index"] == 1 and off == row["lo"] and n == row["hi"] - row["lo"]):
            st["fired"] = True
            ev["t_fired"] = t
            with orig_open(trigger, "w") as fh:
                fh.write("go")
        return data

    trigger = os.path.join(S, f"trigger-{tag}")
    result = os.path.join(S, f"attacker-{tag}.json")
    for p in (trigger, result):
        if os.path.exists(p):
            os.unlink(p)

    mod.code_observe = code_observe
    mod.sha_file = sha_rec
    builtins.open = open_
    os.pread = pread

    proc = None
    lib_path = os.path.join(S, f"work-{tag}", "server", "llama-b11909", TARGET_LIB)
    ev["t_run_start"] = time.monotonic()
    legs = {}
    box = {}

    def run_bind():
        rpath = os.path.join(TREE, ".ufo/waves/round-48/c2/live", f"receipt-{receipt}.json")
        try:
            box["legs"] = mod.bind_one(TREE, rpath, S, tag, EV["vocab"], EV["arc"], detail)
        except BaseException as exc:  # noqa: BLE001 - recorded, then re-raised below
            box["exc"] = exc

    th = threading.Thread(target=run_bind, daemon=True)
    th.start()
    try:
        member = "llama-b11909/" + TARGET_LIB
        pristine = EV["arc"].member(member)

        def mem_watch():
            """After the attacker writes, read the target range out of the server's
            memory: does the RUNNING text change?"""
            while not st["fired"]:
                time.sleep(0.0002)
            time.sleep(0.0015)
            row = st["x_row"]
            pid = st["server_pid"]
            try:
                fd = os.open(f"/proc/{pid}/mem", os.O_RDONLY)
            except OSError as exc:
                st["mem_obs"] = {"error": str(exc)}
                return
            try:
                got = orig_pread(fd, row["hi"] - row["lo"], row["lo"])
            except OSError as exc:
                st["mem_obs"] = {"error": str(exc)}
                return
            finally:
                os.close(fd)
            want = pristine[row["off"]:row["off"] + len(got)]
            diff = sum(1 for a, b in zip(got, want) if a != b)
            st["mem_obs"] = {"t": time.monotonic(), "len": len(got),
                             "bytes_differing_from_archive": diff,
                             "mem_equals_archive": got == want}

        watcher = None
        if mode.startswith("pin"):
            watcher = threading.Thread(target=mem_watch, daemon=True)
            watcher.start()

        def lifetime_watch():
            """How long after the counter's `release` file does the server still run?"""
            while ev.get("t_release") is None:
                time.sleep(0.0005)
            pid = st["server_pid"]
            t0 = time.monotonic()
            while time.monotonic() - t0 < 5.0:
                if mod.stat_fields(pid) is None:
                    break
                time.sleep(0.0005)
            st["server_lifetime_after_release_ms"] = round((time.monotonic() - t0) * 1000, 2)

        threading.Thread(target=lifetime_watch, daemon=True).start()
        if mode != "none":
            # wait for the replay to extract the archive, then arm the attacker
            t0 = time.monotonic()
            while not os.path.exists(lib_path) and time.monotonic() - t0 < 600:
                time.sleep(0.02)
            if not os.path.exists(lib_path):
                ev["error"] = "target library never extracted"
            else:
                ev["lib_path"] = lib_path
                ev["lib_sha256_before"] = sha_file(lib_path)
                proc = subprocess.Popen(
                    [sys.executable, os.path.join(S, "j1_attacker.py"), lib_path, trigger, result,
                     "--hold-ms", str(hold_ms), "--delay-ms", str(attacker_delay_ms)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                    env=dict(os.environ, PYTHONPATH=""))
                ev["attacker_pid"] = proc.pid
        th.join(timeout=900)
        if "exc" in box:
            raise box["exc"]
        legs = box.get("legs") or {}
    finally:
        os.pread = orig_pread
        builtins.open = orig_open
        mod.sha_file = orig_sha_file
        mod.code_observe = orig_code_observe
        if proc is not None:
            try:
                proc.wait(timeout=60)
            except subprocess.TimeoutExpired:
                proc.kill()
            err = proc.stderr.read().decode("utf-8", "replace")
            if err.strip():
                ev["attacker_stderr"] = err[-500:]

    ev["t_run_end"] = time.monotonic()
    ev["legs"] = legs
    ev["detail"] = detail
    ev["reads"] = st["reads"]
    ev["mem_obs"] = st["mem_obs"]
    ev["server_lifetime_after_release_ms"] = st.get("server_lifetime_after_release_ms")
    if os.path.exists(result):
        with open(result) as fh:
            ev["attacker"] = json.load(fh)
    if os.path.exists(lib_path):
        ev["lib_sha256_after"] = sha_file(lib_path)
    a = ev.get("attacker") or {}
    if "t_write" in a:
        ps = ev.get("passes") or []
        w = {"write_ms": round((a["t_write"] - ev["t_run_start"]) * 1000, 3),
             "restore_ms": round((a["t_restore"] - ev["t_run_start"]) * 1000, 3),
             "write_latency_after_trigger_ms": a.get("latency_ms_trigger_to_write")}
        for i, p in enumerate(ps, 1):
            w[f"pass{i}_start_ms"] = round((p["start"] - ev["t_run_start"]) * 1000, 3)
            w[f"pass{i}_end_ms"] = round((p["end"] - ev["t_run_start"]) * 1000, 3)
            w[f"write_in_pass{i}"] = bool(p["start"] <= a["t_write"] <= p["end"])
            w[f"restore_in_pass{i}"] = bool(p["start"] <= a["t_restore"] <= p["end"])
        if len(ps) >= 2:
            w["inter_pass_gap_ms"] = round((ps[1]["start"] - ps[0]["end"]) * 1000, 3)
            # per-range re-read interval of the target range
            row = st["x_row"]
            t1 = [r["t"] for r in st["reads"] if r["off"] == row["lo"] and r["len"] == row["hi"] - row["lo"]]
            if len(t1) >= 2:
                w["target_range_reread_interval_ms"] = round((t1[1] - t1[0]) * 1000, 3)
            w["write_before_pass2_target_read"] = bool(len(t1) >= 2 and a["t_write"] < t1[1])
            w["restore_before_pass2_target_read"] = bool(len(t1) >= 2 and a["t_restore"] < t1[1])
        if ev.get("t_release"):
            w["write_before_release"] = a["t_write"] < ev["t_release"]
            w["restore_before_release"] = a["t_restore"] < ev["t_release"]
            w["pass2_end_to_release_ms"] = round((ev["t_release"] - ps[-1]["end"]) * 1000, 3)
        ev["attack_window"] = w
    ev["timeline"] = timeline(ev)
    if verbose:
        print(json.dumps({"tag": tag, "legs": legs,
                          "write_ms": (ev.get("attack_window") or {}).get("write_ms"),
                          "restore_ms": (ev.get("attack_window") or {}).get("restore_ms"),
                          "mem_diff": (ev.get("mem_obs") or {}).get("bytes_differing_from_archive"),
                          "twopass": legs.get("twopass"), "code": legs.get("code"),
                          "rehash": legs.get("rehash")}))
        sys.stdout.flush()
    return ev


def timeline(ev):
    ps = ev.get("passes") or []
    t = {"n_passes": len(ps)}
    if len(ps) >= 2:
        t["pass1_dur_ms"] = ps[0]["dur_ms"]
        t["pass2_dur_ms"] = ps[1]["dur_ms"]
        t["inter_pass_gap_ms"] = round((ps[1]["start"] - ps[0]["end"]) * 1000, 3)
        t["pass2_end_to_release_ms"] = (round((ev["t_release"] - ps[1]["end"]) * 1000, 3)
                                        if ev.get("t_release") else None)
    tree_sha = [c for c in ev.get("sha_calls", []) if c["path"].startswith(TREE)]
    if tree_sha and ps:
        t["rehash_first_ms"] = round((tree_sha[0]["t"] - ps[-1]["end"]) * 1000, 3)
        t["rehash_calls"] = len(tree_sha)
    reads = ev.get("reads") or []
    t["total_reads"] = len(reads)
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["characterize", "race"])
    ap.add_argument("--receipt", type=int, default=1)
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--hold-ms", type=float, default=5.0)
    ap.add_argument("--delay-ms", type=float, default=0.0)
    ap.add_argument("--trigger", default="pin_in", choices=["pin_in", "pin_post2", "none"])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    mod, cev = load_counter()
    EV = dict(cev)
    build_tree()
    if not os.path.isfile(ARC):
        fetch(mod.ARCHIVE_URL, ARC)
    assert sha_file(ARC) == mod.ARCHIVE_SHA, "counter archive digest"
    if not os.path.isfile(MODEL):
        fetch(mod.MODEL_URL, MODEL)
    EV["archive_sha256"] = sha_file(ARC)
    EV["model_sha256"] = sha_file(MODEL)
    EV["vocab"] = mod.gguf_tokens(MODEL)
    EV["arc"] = mod.Archive(ARC)

    runs = []
    if a.mode == "characterize":
        ev = armed_run(mod, EV, f"c{int(time.time())}", a.receipt, "none", 0.0)
        runs.append(ev)
    else:
        for i in range(1, a.runs + 1):
            tag = f"r{i}_{int(time.time() * 1000) % 1000000}"
            ev = armed_run(mod, EV, tag, a.receipt, a.trigger, a.hold_ms, a.delay_ms)
            runs.append(ev)
            legs = ev.get("legs") or {}
            w = ev.get("attack_window") or {}
            print(json.dumps({
                "run": i, "mode": a.trigger, "hold_ms": a.hold_ms,
                "twopass": legs.get("twopass"), "code": legs.get("code"),
                "rehash": legs.get("rehash"), "bind": legs.get("bind"),
                "write_ms": w.get("write_ms"), "restore_ms": w.get("restore_ms"),
                "pass1": [w.get("pass1_start_ms"), w.get("pass1_end_ms")],
                "pass2": [w.get("pass2_start_ms"), w.get("pass2_end_ms")],
                "reread_gap_ms": w.get("target_range_reread_interval_ms"),
                "restore_before_pass2_read": w.get("restore_before_pass2_target_read"),
                "mem_diff": (ev.get("mem_obs") or {}).get("bytes_differing_from_archive"),
                "attacker_latency_ms": (ev.get("attacker") or {}).get("latency_ms_trigger_to_write"),
                "detail_twopass": [d for d in (ev.get("detail") or []) if "twopass" in d or "two observation" in d][:2],
                "detail_code": [d for d in (ev.get("detail") or []) if "differ from the archive member" in d][:2],
            }))
            sys.stdout.flush()
    EV["runs"] = runs
    out = a.out or os.path.join(S, f"{a.mode}.json")
    with open(out, "w") as fh:
        json.dump({k: v for k, v in EV.items() if k != "arc"}, fh, indent=1)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
