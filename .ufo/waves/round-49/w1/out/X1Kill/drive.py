#!/usr/bin/env python3
"""X1Kill driver: kill a witnessed replay and observe leftovers.

Scenarios (each with a fresh --work/--witness-dir):
  A  SIGTERM the kama-live-replay.py process while the server is held
  B  SIGKILL the kama-live-replay.py process while the server is held
  C  SIGKILL the kama-llamacpp-live.py child while the server is held (pdeathsig path)

Observation window: 15 s per signal (HYPOTHESIS_WINDOW). Polls every 200 ms:
  - llama-server pid alive (/proc/<pid>)
  - live tool pid alive
  - replay pid alive
  - port listening (connect to 127.0.0.1:port)
  - ss -ltnp 'sport = :<port>' text snapshot at t=0 and at the end
After the window: leftovers are recorded, then cleaned up by this driver
(release file, then TERM/KILL as needed), and leftovers are re-measured.
"""
import json
import os
import re
import signal
import socket
import subprocess
import sys
import time

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REPLAY = os.path.join(LANE, "tools", "kama-live-replay.py")
RECEIPT = os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-1.json")
S = os.path.dirname(os.path.abspath(__file__))
WINDOW = 15.0
POLL = 0.2


def sh(argv):
    p = subprocess.run(argv, capture_output=True, text=True)
    return {"argv": argv, "rc": p.returncode, "out": p.stdout, "err": p.stderr}


def alive(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    # a zombie is not a running server
    try:
        with open(f"/proc/{pid}/stat") as fh:
            state = fh.read().rsplit(")", 1)[1].split()[0]
        return state != "Z"
    except OSError:
        return False


def listening(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except OSError:
        return False


def ss(port):
    return sh(["ss", "-ltnp", f"sport = :{port}"])["out"]


def proc_facts(pid):
    d = {"pid": pid}
    try:
        with open(f"/proc/{pid}/stat") as fh:
            fields = fh.read().rsplit(")", 1)[1].split()
        d["ppid"], d["pgrp"], d["session"] = int(fields[1]), int(fields[2]), int(fields[3])
    except OSError as exc:
        d["stat_error"] = str(exc)
    for key, path in (("exe", f"/proc/{pid}/exe"), ("cwd", f"/proc/{pid}/cwd")):
        try:
            d[key] = os.readlink(path)
        except OSError as exc:
            d[key] = f"error:{exc}"
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as fh:
            d["cmdline"] = fh.read().decode("utf-8", "replace").replace("\0", " ").strip()
    except OSError as exc:
        d["cmdline"] = f"error:{exc}"
    try:
        with open(f"/proc/{pid}/status") as fh:
            st = fh.read()
        d["ppid_from_status"] = re.search(r"^PPid:\s+(\d+)", st, re.M).group(1)
        d["sigpnd"] = re.search(r"^SigPnd:\s+(\w+)", st, re.M).group(1)
    except (OSError, AttributeError):
        pass
    return d


def children(pid):
    out = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        try:
            with open(f"/proc/{entry}/stat") as fh:
                fields = fh.read().rsplit(")", 1)[1].split()
            if int(fields[1]) == pid:
                out.append(int(entry))
        except OSError:
            continue
    return sorted(out)


def llama_servers():
    """Every process whose argv[0] is a llama-server binary (fleet-wide snapshot)."""
    out = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        try:
            with open(f"/proc/{entry}/cmdline", "rb") as fh:
                argv = fh.read().split(b"\0")
        except OSError:
            continue
        if argv and os.path.basename(argv[0].decode("utf-8", "replace")) == "llama-server":
            out.append({"pid": int(entry), "argv0": argv[0].decode("utf-8", "replace")})
    return sorted(out, key=lambda d: d["pid"])


def pgrep():
    return sh(["pgrep", "-af", "llama-server"])


def run_scenario(tag, sig_target):
    """sig_target: ('replay-term'|'replay-kill'|'live-kill')."""
    start = time.time()
    work = os.path.join(S, f"w-{tag}")
    wd = os.path.join(S, f"wd-{tag}")
    out = os.path.join(S, f"j-{tag}.json")
    os.makedirs(wd, exist_ok=True)
    os.makedirs(work, exist_ok=True)
    rec = {"tag": tag, "sig_target": sig_target, "start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "cmd": None, "baseline_servers": llama_servers(), "baseline_pgrep": pgrep()["out"],
           "timeline": [], "ready": None}
    argv = [sys.executable, REPLAY, "--receipt", RECEIPT, "--work", work, "--out", out, "--witness-dir", wd]
    rec["cmd"] = " ".join(argv)
    log = open(os.path.join(S, f"replay-{tag}.log"), "wb")
    # own session so cleanup can killpg without touching the harness
    p = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, cwd=S, start_new_session=True)
    rec["replay_pid"] = p.pid
    ready_path = os.path.join(wd, "ready.json")
    t0 = time.time()
    while time.time() - t0 < 240:
        if os.path.exists(ready_path):
            break
        if p.poll() is not None:
            break
        time.sleep(0.05)
    rec["ready_wait_s"] = round(time.time() - t0, 2)
    rec["replay_exit_before_ready"] = p.poll()
    if not os.path.exists(ready_path):
        rec["verdict"] = "no-ready.json"
        rec["replay_log_tail"] = open(os.path.join(S, f"replay-{tag}.log"), errors="replace").read()[-2000:]
        log.close()
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except OSError:
            pass
        return rec
    ready = json.load(open(ready_path))
    rec["ready"] = ready
    server, port = ready["pid"], ready["port"]
    rec["server_pid"], rec["port"] = server, port
    rec["before_signal"] = {
        "server": proc_facts(server),
        "server_exe_sha256": sh(["sha256sum", f"/proc/{server}/exe"])["out"].split()[0] if alive(server) else None,
        "live_children_of_replay": [{str(c): proc_facts(c)} for c in children(p.pid)],
        "ss": ss(port), "listening": listening(port),
        "pgrep": pgrep()["out"],
    }
    live = [c for c in children(p.pid) if c != server]
    live_pid = None
    for c in live:
        facts = proc_facts(c)
        if "kama-llamacpp-live.py" in facts.get("cmdline", ""):
            live_pid = c
    rec["live_pid"] = live_pid
    # signal
    if sig_target == "replay-term":
        target, signum = p.pid, signal.SIGTERM
    elif sig_target == "replay-kill":
        target, signum = p.pid, signal.SIGKILL
    else:  # live-kill
        target, signum = live_pid, signal.SIGKILL
    rec["signal"] = {"target": target, "sig": signal.Signals(signum).name,
                     "target_facts": proc_facts(target) if target else None}
    if target is None:
        rec["verdict"] = "live-child-not-found"
        return rec
    ts = time.time()
    os.kill(target, signum)
    gone = {"server": None, "port_closed": None, "live": None, "replay": None}
    samples = []
    while time.time() - ts < WINDOW:
        el = time.time() - ts
        st = {"t": round(el, 3), "replay": alive(p.pid), "live": alive(live_pid),
              "server": alive(server), "listening": listening(port)}
        samples.append(st)
        if gone["server"] is None and not st["server"]:
            gone["server"] = round(el, 3)
        if gone["port_closed"] is None and not st["listening"]:
            gone["port_closed"] = round(el, 3)
        if gone["live"] is None and not st["live"]:
            gone["live"] = round(el, 3)
        if gone["replay"] is None and not st["replay"]:
            gone["replay"] = round(el, 3)
        time.sleep(POLL)
    rec["gone_after_s"] = gone
    rec["samples_first"] = samples[:3]
    rec["samples_last"] = samples[-3:]
    rec["samples_n"] = len(samples)
    # leftovers at the end of the window
    rec["at_window_end"] = {
        "server_alive": alive(server), "listening": listening(port),
        "server": proc_facts(server),
        "ss": ss(port), "pgrep": pgrep()["out"],
        "replay_exit": p.poll(),
        "live": proc_facts(live_pid) if alive(live_pid) else None,
    }
    rec["hypothesis_held"] = (not alive(server)) and (not listening(port))
    # cleanup: release, then cooperative stop, then KILL
    open(os.path.join(wd, "release"), "w").write("x1kill\n")
    tc = time.time()
    while time.time() - tc < 20 and (alive(server) or alive(live_pid) or p.poll() is None):
        time.sleep(0.1)
    rec["after_release"] = {"s": round(time.time() - tc, 2), "server": alive(server),
                            "live": alive(live_pid), "listening": listening(port),
                            "replay_exit": p.poll()}
    for pid, name in ((live_pid, "live"), (server, "server")):
        if alive(pid):
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
    time.sleep(3)
    for pid, name in ((live_pid, "live"), (server, "server")):
        if alive(pid):
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except OSError:
        pass
    time.sleep(1)
    rec["after_cleanup"] = {"server": alive(server), "live": alive(live_pid),
                            "listening": listening(port), "ss": ss(port),
                            "pgrep": pgrep()["out"],
                            "elapsed_s": round(time.time() - start, 1)}
    log.close()
    rec["replay_log_tail"] = open(os.path.join(S, f"replay-{tag}.log"), errors="replace").read()[-3000:]
    try:
        rec["out_json"] = json.load(open(out))
    except (OSError, ValueError):
        rec["out_json"] = None
    return rec


if __name__ == "__main__":
    which = sys.argv[1:] or ["A", "B", "C"]
    plan = {"A": ("replay-term",), "B": ("replay-kill",), "C": ("live-kill",)}
    for tag in which:
        rec = run_scenario(tag, plan[tag][0])
        with open(os.path.join(S, f"result-{tag}.json"), "w") as fh:
            json.dump(rec, fh, indent=1)
        print(tag, "verdict=", rec.get("verdict"), "held=", rec.get("hypothesis_held"),
              "gone=", rec.get("gone_after_s"), flush=True)
