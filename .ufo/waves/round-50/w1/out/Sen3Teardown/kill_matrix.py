#!/usr/bin/env python3
"""kill_matrix.py - kama round-50 seat Sen3Teardown: teardown kill-variant matrix.

One FRESH witnessed replay of `.ufo/waves/round-48/c2/live/receipt-2.json` per variant, at
the lane clone's build tip, started exactly like the round-50 C1 counter starts it:
`python3 -I -c INVOKER python3 -I <tree>/tools/kama-live-replay.py --receipt R --work W
 --out J --witness-dir D` from a small invoker process, environment = PASS_ENV (+ proxies),
start_new_session on the invoker.

Variants: one signal (SIGINT, SIGTERM, SIGKILL) to one member of the tree --
  invoker / replay / live tool / llama-server -- during
  hold      the witness hold (ready.json names the server) and
  download  the initial download (a `*.part` file exists under <work>/download, no live child yet),
plus an `parent` family where a second-level parent (the counter's own position,
driver -> wrapper -> invoker -> replay) is killed during the hold.

Measured per variant, t0 = the instant the signal is sent:
  t_tree    first time no snapshotted process (pid + start time) of the tree is alive
  t_port    first time the witness port has no LISTEN socket and refuses connect
  t_srv     first time no llama-server whose argv names this run's paths exists
  the counter's contract is: tree gone within 30 s (KILL_WAIT), port refuses.
Survivors at the cap are recorded as leftovers and then SIGKILLed; every run dir is removed
after its result is written. No lane file is touched; nothing outside --scratch and --out.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time

PASS_ENV = ("PATH", "LANG", "HOME", "XDG_CACHE_HOME", "TMPDIR",
            "http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "no_proxy")
INVOKER = "import subprocess, sys\nsys.exit(subprocess.call(sys.argv[1:]))\n"
SIGS = {"INT": signal.SIGINT, "TERM": signal.SIGTERM, "KILL": signal.SIGKILL}
HOLD_CAP = 200.0      # seconds; the witness hold self-heals at ~120 s + teardown
DL_CAP = 60.0


# ---------------------------------------------------------------- /proc helpers
def stat_of(pid):
    try:
        with open(f"/proc/{pid}/stat", "rb") as fh:
            raw = fh.read()
    except OSError:
        return None
    i = raw.rfind(b")")
    if i < 0:
        return None
    f = raw[i + 2:].split()
    try:
        return {"state": f[0].decode(), "ppid": int(f[1]), "start": f[19].decode()}
    except (IndexError, ValueError):
        return None


def argv_of(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as fh:
            raw = fh.read()
    except OSError:
        return []
    return [a.decode("utf-8", "replace") for a in raw.split(b"\0") if a]


def proc_table():
    t = {}
    for name in os.listdir("/proc"):
        if name.isdigit():
            s = stat_of(int(name))
            if s:
                t[int(name)] = s
    return t


def descendants(root, table=None):
    t = table or proc_table()
    kids = {}
    for pid, s in t.items():
        kids.setdefault(s["ppid"], []).append(pid)
    out, stack = {}, [root]
    while stack:
        cur = stack.pop()
        for k in kids.get(cur, []):
            out[k] = t[k]["start"]
            stack.append(k)
    return out


def alive(pid, start):
    s = stat_of(pid)
    return bool(s and s["start"] == start and s["state"] != "Z")


def listen_inodes(port):
    inodes = set()
    for path in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            with open(path) as fh:
                lines = fh.read().splitlines()[1:]
        except OSError:
            continue
        for ln in lines:
            f = ln.split()
            if len(f) < 10 or f[3] != "0A":
                continue
            try:
                p = int(f[1].rsplit(":", 1)[1], 16)
            except (IndexError, ValueError):
                continue
            if p == port:
                inodes.add(f[9])
    return inodes


def port_refuses(port):
    for fam, host in ((socket.AF_INET, "127.0.0.1"), (socket.AF_INET6, "::1")):
        try:
            s = socket.socket(fam, socket.SOCK_STREAM)
            s.settimeout(0.5)
            rc = s.connect_ex((host, port))
            s.close()
            if rc == 0:
                return False
        except OSError:
            pass
    return True


def llama_servers(marker):
    """(pid, argv0) of every llama-server whose argv names `marker` (this run's paths)."""
    out = []
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        a = argv_of(pid)
        if a and os.path.basename(a[0]) == "llama-server" and marker in " ".join(a):
            out.append({"pid": pid, "argv0": a[0]})
    return out


def role_of(pid):
    a = argv_of(pid)
    if not a:
        return None
    if os.path.basename(a[0]) == "llama-server":
        return "server"
    blob = " ".join(a)
    if "kama-live-replay.py" in blob:
        return "replay"
    if "kama-llamacpp-live.py" in blob:
        return "live"
    if "-c" in a and any("sys.exit(subprocess.call" in x for x in a):
        return "invoker" if "kama-live-replay.py" not in blob else "replay"
    return "other"


# ---------------------------------------------------------------- one variant
def env_for(run_dir):
    env = {k: os.environ[k] for k in PASS_ENV if k in os.environ}
    for k in ("XDG_CACHE_HOME", "TMPDIR"):
        d = os.path.join(run_dir, k.lower())
        os.makedirs(d, exist_ok=True)
        env[k] = d
    return env


def wait_json(path, deadline):
    while time.monotonic() < deadline:
        try:
            with open(path) as fh:
                d = json.load(fh)
            if isinstance(d, dict):
                return d
        except (OSError, ValueError):
            pass
        time.sleep(0.01)
    return None


def wait_part(run_dir, deadline):
    dl = os.path.join(run_dir, "work", "download")
    while time.monotonic() < deadline:
        try:
            names = [n for n in os.listdir(dl) if n.endswith(".part")]
        except OSError:
            names = []
        if names:
            p = os.path.join(dl, names[0])
            try:
                size = os.path.getsize(p)
            except OSError:
                size = None
            return {"name": names[0], "bytes_at_kill": size}
        time.sleep(0.002)
    return None


def state_of(pid, start):
    s = stat_of(pid)
    if not s or s["start"] != start:
        return "gone"
    return s["state"]


def run_variant(tree, receipt, runs, tag, target, signame, phase, wrapper=False, keep=False,
                trace=False):
    run_dir = os.path.join(runs, tag)
    shutil.rmtree(run_dir, ignore_errors=True)
    os.makedirs(run_dir)
    work, wd = os.path.join(run_dir, "work"), os.path.join(run_dir, "wd")
    os.makedirs(wd)
    outj = os.path.join(run_dir, "out.json")
    log = open(os.path.join(run_dir, "run.log"), "wb")
    env = env_for(run_dir)
    replay_argv = [sys.executable, "-I", os.path.join(tree, "tools", "kama-live-replay.py"),
                   "--receipt", receipt, "--work", work, "--out", outj, "--witness-dir", wd]
    inner = [sys.executable, "-I", "-c", INVOKER] + replay_argv
    argv = ([sys.executable, "-I", "-c", INVOKER] + inner) if wrapper else \
           ([sys.executable, "-I", "-c", INVOKER] + replay_argv)
    res = {"tag": tag, "target": "parent" if wrapper else target, "signal": signame,
           "phase": phase, "tree": tree, "receipt": receipt, "work": work, "witness_dir": wd}
    t_start = time.monotonic()
    p = subprocess.Popen(argv, env=env, cwd=tree, stdout=log, stderr=log,
                         start_new_session=True)
    res["invoker_pid"] = p.pid
    port = None
    roles = {}
    snap = {}
    try:
        # ---- reach the phase
        if phase == "hold":
            ready = wait_json(os.path.join(wd, "ready.json"), time.monotonic() + 300)
            if ready is None or not isinstance(ready.get("pid"), int):
                res.update(stage="no-ready", invoker_exit=p.poll(),
                           log_tail=open(os.path.join(run_dir, "run.log")).read()[-400:])
                return res
            port = ready["port"]
            tab = proc_table()
            desc = descendants(p.pid, tab)
            roles = {"invoker": p.pid, "server": ready["pid"]}
            for pid in desc:
                r = role_of(pid)
                if r in ("replay", "live") and r not in roles:
                    roles[r] = pid
            if wrapper:
                # the invoker is the wrapper's child; the wrapper's only child chain
                roles["invoker"] = [pid for pid, s in tab.items() if s["ppid"] == p.pid][0] \
                    if any(s["ppid"] == p.pid for s in tab.values()) else roles.get("invoker")
            snap = descendants(p.pid, proc_table())
            snap[ready["pid"]] = (stat_of(ready["pid"]) or {}).get("start", "")
            res["ready"] = ready
            res["phase_attained"] = {"ready_utc_s": round(time.monotonic() - t_start, 2),
                                     "ready_bytes": os.path.getsize(os.path.join(wd, "ready.json"))}
        else:  # download
            part = wait_part(run_dir, time.monotonic() + 120)
            if part is None:
                res.update(stage="no-part", invoker_exit=p.poll(),
                           log_tail=open(os.path.join(run_dir, "run.log")).read()[-400:])
                return res
            tab = proc_table()
            desc = descendants(p.pid, tab)
            roles = {"invoker": p.pid}
            for pid in desc:
                r = role_of(pid)
                if r in ("replay", "live", "server") and r not in roles:
                    roles[r] = pid
            snap = {pid: s for pid, s in desc.items()}
            res["phase_attained"] = {"part": part, "part_utc_s": round(time.monotonic() - t_start, 2),
                                     "live_child_present": "live" in roles,
                                     "server_present": "server" in roles}
        # target resolution
        if wrapper:
            tpid = p.pid
        else:
            tpid = roles.get(target)
        res["roles"] = {k: v for k, v in roles.items()}
        res["target_pid"] = tpid
        if tpid is None:
            res["stage"] = "target-absent"
            res["note"] = f"no {target} process existed at the {phase} instant"
            return res
        if target == "server" and port is None:
            res["stage"] = "target-absent"
            return res
        # ---- kill and measure
        srv_marker = work
        t0 = time.monotonic()
        try:
            os.kill(tpid, SIGS[signame])
            res["signal_sent"] = True
        except OSError as exc:
            res["signal_sent"] = f"{type(exc).__name__}:{exc}"
        cap = HOLD_CAP if phase == "hold" else DL_CAP
        t_tree = t_port = t_srv = None
        death = {}
        tr = [] if trace else None
        while time.monotonic() - t0 < cap:
            now = time.monotonic() - t0
            for pid, start in snap.items():
                if pid not in death and not alive(pid, start):
                    death[pid] = round(now, 3)
            tree_alive = [pid for pid, start in snap.items() if alive(pid, start)]
            lsn = listen_inodes(port) if port else set()
            port_ok = (not lsn) and (port_refuses(port) if port else True)
            srv_left = llama_servers(srv_marker)
            if tr is not None:
                tr.append({"t": round(now, 3),
                           "states": {pid: state_of(pid, start) for pid, start in snap.items()},
                           "listen": len(lsn),
                           "llama_servers": [s["pid"] for s in srv_left],
                           "ready_json": os.path.exists(os.path.join(wd, "ready.json"))})
            if t_tree is None and not tree_alive:
                t_tree = round(now, 3)
            if t_port is None and port_ok:
                t_port = round(now, 3)
            if t_srv is None and not srv_left:
                t_srv = round(now, 3)
            if t_tree is not None and t_port is not None and t_srv is not None:
                break
            time.sleep(0.005 if tr is not None else 0.02)
        res["deaths_s"] = death
        res["t_tree_s"] = t_tree
        res["t_port_s"] = t_port
        res["t_no_server_s"] = t_srv
        res["left_alive"] = [{"pid": pid, "role": role_of(pid)} for pid, start in snap.items()
                             if alive(pid, start)]
        res["left_listen"] = sorted(listen_inodes(port)) if port else []
        res["left_llama_servers"] = llama_servers(srv_marker)
        res["port_refuses"] = port_refuses(port) if port else None
        res["within_30s"] = bool(t_tree is not None and t_port is not None
                                 and t_tree <= 30 and t_port <= 30)
        res["ready_left_behind"] = os.path.exists(os.path.join(wd, "ready.json"))
        rrp = os.path.join(work, "rerun-receipt.json")
        if os.path.exists(rrp):
            try:
                with open(rrp) as fh:
                    rr = json.load(fh)
                res["rerun_receipt"] = {
                    "setup_error": rr.get("setup_error"), "outcome": rr.get("outcome"),
                    "witness": rr.get("witness") if isinstance(rr.get("witness"), dict) else None,
                    "teardown": {k: (rr.get("teardown") or {}).get(k) for k in
                                 ("returncode", "sigterm_sent", "sigkill_sent", "port_refuses", "term_wait_ms")},
                    "child_pid": rr.get("child_pid"),
                }
            except (OSError, ValueError):
                res["rerun_receipt"] = "unreadable"
        if tr is not None:
            res["trace"] = tr
        # what the killed tree recorded, if anything
        if os.path.exists(outj):
            try:
                with open(outj) as fh:
                    j = json.load(fh)
                res["replay_out"] = {k: j.get(k) for k in ("match", "refused", "mismatches", "live_exit")}
            except (OSError, ValueError):
                res["replay_out"] = "unreadable"
        res["stage"] = "measured"
        return res
    finally:
        # ---- cleanup: kill whatever of this run is left, then remove the run dir
        try:
            for pid, start in list(snap.items()):
                if alive(pid, start):
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except OSError:
                        pass
            for s in llama_servers(os.path.join(run_dir, "work")):
                try:
                    os.kill(s["pid"], signal.SIGKILL)
                except OSError:
                    pass
            try:
                if p.poll() is None:
                    os.killpg(p.pid, signal.SIGKILL)
            except OSError:
                pass
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
            res["invoker_exit"] = p.returncode
            res["cleanup_left"] = [pid for pid, start in snap.items() if alive(pid, start)] \
                + [s["pid"] for s in llama_servers(os.path.join(run_dir, "work"))]
        except BaseException as exc:  # keep the result even if cleanup breaks
            res["cleanup_error"] = f"{type(exc).__name__}:{exc}"
        log.close()
        try:
            with open(os.path.join(run_dir, "result.json"), "w") as fh:
                json.dump(res, fh, indent=1)
        except OSError:
            pass
        if res.get("cleanup_left") == [] and not keep:
            shutil.rmtree(work, ignore_errors=True)


def build_variants():
    v = []
    for target in ("invoker", "replay", "live", "server"):
        for sig in ("INT", "TERM", "KILL"):
            v.append(dict(tag=f"hold-{target}-{sig}", target=target, signame=sig, phase="hold"))
    for target in ("invoker", "replay"):
        for sig in ("INT", "TERM", "KILL"):
            v.append(dict(tag=f"dl-{target}-{sig}", target=target, signame=sig, phase="download"))
    for sig in ("KILL", "TERM"):
        v.append(dict(tag=f"hold-parent-{sig}", target="parent", signame=sig, phase="hold",
                      wrapper=True))
    return v


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True, help="summary.json path")
    ap.add_argument("--only", default="", help="comma-separated tag substrings to run")
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--keep", action="store_true", help="keep each run's work dir")
    ap.add_argument("--trace", action="store_true", help="5 ms per-pid state trace")
    a = ap.parse_args(argv)
    variants = build_variants()
    if a.only:
        want = [w for w in a.only.split(",") if w]
        variants = [v for v in variants if any(w in v["tag"] for w in want)]
    os.makedirs(a.runs, exist_ok=True)
    results, lock = [], threading.Lock()
    queue = list(variants)

    def worker():
        while True:
            with lock:
                if not queue:
                    return
                v = queue.pop(0)
            try:
                r = run_variant(a.tree, a.receipt, a.runs, v["tag"], v["target"],
                                v["signame"], v["phase"], v.get("wrapper", False),
                                keep=a.keep, trace=a.trace)
            except BaseException as exc:
                r = {"tag": v["tag"], "stage": "driver-error",
                     "error": f"{type(exc).__name__}:{exc}"}
            with lock:
                results.append(r)
                print(f"{r['tag']}: {r.get('stage')} tree={r.get('t_tree_s')} "
                      f"port={r.get('t_port_s')} srv={r.get('t_no_server_s')} "
                      f"within30={r.get('within_30s')} left={len(r.get('left_alive') or [])}",
                      flush=True)

    threads = [threading.Thread(target=worker) for _ in range(max(1, a.parallel))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    results.sort(key=lambda r: r["tag"])
    with open(a.out, "w") as fh:
        json.dump({"tree": a.tree, "receipt": a.receipt, "variants": results}, fh, indent=1)
    bad = [r["tag"] for r in results
           if r.get("stage") != "measured" or not r.get("within_30s")]
    print(f"SUMMARY variants={len(results)} not-clean={bad}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
