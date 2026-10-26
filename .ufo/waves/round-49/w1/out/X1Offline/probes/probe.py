#!/usr/bin/env python3
"""X1Offline round-49 probe: witness-dir failure modes of kama-llamacpp-live.py.

Each scenario prepares a witness dir, starts the live tool as a child, polls
<dir>/ready.json from t0 (20 ms) exactly as the documented observer would, records
what it read and when, releases only when the scenario says so, then reports the
receipt fields and the leftovers (ready.json content, release, pid alive, port
accepting, any llama-server process still running).
"""
import json
import os
import shutil
import subprocess
import sys
import time

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
LIVE = os.path.join(LANE, "tools", "kama-llamacpp-live.py")
PROBE = os.path.join(LANE, "tools", "kama-probe.sh")
SERVER = "/home/vgpnk/.local/opt/llama-b11909/llama-server"
MODEL = "/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf"
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"


def llama_pids():
    out = {}
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            with open(f"/proc/{d}/comm") as fh:
                if fh.read().strip() == "llama-server":
                    with open(f"/proc/{d}/stat") as fh:
                        state = fh.read().rsplit(")", 1)[1].split()[0]
                    out[int(d)] = state
        except (OSError, IndexError):
            continue
    return out


def pid_alive(pid):
    try:
        with open(f"/proc/{pid}/stat") as fh:
            return fh.read().rsplit(")", 1)[1].split()[0] not in ("Z", "X")
    except (OSError, IndexError):
        return False


def port_accepts(port):
    import socket
    s = socket.socket()
    s.settimeout(0.3)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def read_json(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def run(scenario, D, timeout, release_when, witness_timeout=30.0):
    S = os.path.dirname(D)
    out = os.path.join(S, f"receipt-{scenario}.json")
    log = os.path.join(S, f"live-{scenario}.log")
    pre = llama_pids()
    argv = [sys.executable, LIVE, "--server", SERVER, "--model", MODEL,
            "--model-sha256", MODEL_SHA, "--alias", "kama-x1offline",
            "--ctx", "256", "--threads", "1", "--probe", PROBE,
            "--out", out, "--witness-dir", D,
            "--witness-timeout", str(witness_timeout)]
    events, ready_history, released = [], [], False
    t0 = time.monotonic()
    with open(log, "wb") as lf:
        p = subprocess.Popen(argv, cwd=S, stdout=lf, stderr=lf)
        previous = None
        try:
            while p.poll() is None and time.monotonic() - t0 < timeout:
                r = read_json(os.path.join(D, "ready.json"))
                if isinstance(r, dict):
                    key = (r.get("pid"), r.get("port"), r.get("written_utc"))
                    if key != previous:
                        previous = key
                        alive = pid_alive(r["pid"]) if isinstance(r.get("pid"), int) else None
                        accepts = port_accepts(r["port"]) if isinstance(r.get("port"), int) else None
                        events.append({"t_ms": int((time.monotonic() - t0) * 1000),
                                       "pid": r.get("pid"), "port": r.get("port"),
                                       "written_utc": r.get("written_utc"),
                                       "pid_alive_at_read": alive,
                                       "port_accepts_at_read": accepts})
                if released or not (release_when and release_when(events)):
                    time.sleep(0.02)
                    continue
                with open(os.path.join(D, "release"), "w") as fh:
                    fh.write("x1offline\n")
                released = True
            try:
                code = p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                p.kill()
                code = None
        finally:
            if p.poll() is None:
                p.kill()
                p.wait()
    post = llama_pids()
    mine = {}
    for pid in sorted(post):
        if pid in pre:
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as fh:
                cmd = fh.read().replace(b"\0", b" ").decode("utf-8", "replace")
            with open(f"/proc/{pid}/stat") as fh:
                ppid = int(fh.read().rsplit(")", 1)[1].split()[1])
        except (OSError, IndexError, ValueError):
            cmd, ppid = None, None
        mine[pid] = {"cmdline": cmd, "ppid": ppid,
                     "touches_my_scratch": bool(cmd and S in cmd)}
    rec = read_json(out) or {}
    ready_final = read_json(os.path.join(D, "ready.json"))
    w = rec.get("witness") if isinstance(rec.get("witness"), dict) else None
    summary = {
        "scenario": scenario,
        "exit": code,
        "wall_ms": int((time.monotonic() - t0) * 1000),
        "receipt": os.path.basename(out),
        "outcome": rec.get("outcome"),
        "setup_error": rec.get("setup_error"),
        "internal_fault": rec.get("internal_fault"),
        "witness": w,
        "checks_all_true": (all(c.get("passed") is True for c in rec.get("checks", []))
                            if rec.get("checks") else None),
        "events": events,
        "released_by_observer": released,
        "ready_json_after_run": ready_final,
        "release_exists_after_run": os.path.exists(os.path.join(D, "release")),
        "witness_dir_listing": sorted(os.listdir(D)) if os.path.isdir(D) else "absent",
        "llama_pids_before": pre,
        "llama_pids_after": post,
        "new_server_procs": mine,
    }
    if isinstance(ready_final, dict) and isinstance(ready_final.get("pid"), int):
        summary["final_pid_alive"] = pid_alive(ready_final["pid"])
        summary["final_port_accepts"] = port_accepts(ready_final["port"])
    return summary


def fresh(D):
    shutil.rmtree(D, ignore_errors=True)
    os.makedirs(D)


def stale_files(D, with_release):
    fresh(D)
    stale = {"schema": "kama-live-witness/v1", "port": 6553, "pid": 999999,
             "written_utc": "2026-10-26T00:00:00Z"}
    with open(os.path.join(D, "ready.json"), "w") as fh:
        json.dump(stale, fh)
    if with_release:
        with open(os.path.join(D, "release"), "w") as fh:
            fh.write("stale release from an earlier run\n")
    os.utime(os.path.join(D, "ready.json"), (1700000000, 1700000000))


def observe_new(events):
    # release once the live tool's own ready.json (not the stale one) is seen
    return bool(events) and events[-1]["pid"] != 999999


def main():
    scenario = sys.argv[1]
    S = sys.argv[2]
    D = os.path.join(S, f"wd-{scenario}")
    if scenario == "fresh":
        fresh(D)
        r = run(scenario, D, 120, observe_new)
    elif scenario == "stale-ready-release":
        stale_files(D, True)
        r = run(scenario, D, 120, None)
    elif scenario == "stale-ready-only":
        stale_files(D, False)
        r = run(scenario, D, 120, observe_new)
    elif scenario == "unwritable":
        fresh(D)
        os.chmod(D, 0o500)
        try:
            r = run(scenario, D, 120, None)
        finally:
            os.chmod(D, 0o700)
    elif scenario == "tmp-is-dir":
        fresh(D)
        os.makedirs(os.path.join(D, "ready.json.tmp"))
        r = run(scenario, D, 120, None)
    elif scenario == "ready-is-dir":
        fresh(D)
        os.makedirs(os.path.join(D, "ready.json"))
        r = run(scenario, D, 120, None)
    elif scenario == "release-is-dir":
        fresh(D)
        os.makedirs(os.path.join(D, "release"))
        r = run(scenario, D, 120, None)
    else:
        raise SystemExit(f"unknown scenario {scenario}")
    print(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
