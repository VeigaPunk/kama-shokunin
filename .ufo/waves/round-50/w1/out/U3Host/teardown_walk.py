#!/usr/bin/env python3
"""U3Host teardown walk: witnessed replays of round-48 c2 receipt-1, kill
various ancestors, record what survives and when."""
import json, os, signal, socket, subprocess, sys, time

S = os.environ["S"]
LANE = os.path.join(S, "lane")
REPLAY = os.path.join(LANE, "tools/kama-live-replay.py")
RECEIPT = os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-1.json")
OUT = os.path.join(S, "out")
POLL = 0.025
LIMIT = 35.0


def env_min(extra=None):
    e = {k: os.environ[k] for k in ("PATH", "HOME", "LANG", "LC_ALL") if k in os.environ}
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "no_proxy"):
        if k in os.environ:
            e[k] = os.environ[k]
    e["TMPDIR"] = S
    if extra:
        e.update(extra)
    return e


def statf(pid):
    try:
        with open(f"/proc/{pid}/stat") as fh:
            r = fh.read().rsplit(")", 1)[1].split()
        return {"state": r[0], "ppid": int(r[1]), "start": int(r[19])}
    except (OSError, IndexError, ValueError):
        return None


def alive(pid, start=None):
    st = statf(pid)
    if st is None or st["state"] == "Z":
        return False
    return start is None or st["start"] == start


def ppid_chain(pid):
    chain = [pid]
    seen = {pid}
    cur = pid
    for _ in range(32):
        st = statf(cur)
        if st is None or st["ppid"] in (0, cur) or st["ppid"] in seen:
            break
        chain.append(st["ppid"])
        seen.add(st["ppid"])
        cur = st["ppid"]
    return chain


def descendants(root):
    out = {}
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        pid = int(d)
        st = statf(pid)
        if st is None:
            continue
        # walk ppid chain up to root
        cur, hops = pid, 0
        while hops < 32:
            s = statf(cur)
            if s is None:
                break
            if cur == root:
                out[pid] = st["start"]
                break
            if s["ppid"] in (0, cur):
                break
            cur = s["ppid"]
            hops += 1
    return out


def cmdline(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as fh:
            return fh.read().replace(b"\0", b" ").decode("utf-8", "replace")[:160]
    except OSError:
        return "<gone>"


def port_refuses(port):
    s = socket.socket()
    s.settimeout(1.0)
    try:
        s.connect(("127.0.0.1", port))
        return False
    except (ConnectionRefusedError, socket.timeout, OSError):
        return True
    finally:
        s.close()


def wait_ready(wd, timeout=300):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        p = os.path.join(wd, "ready.json")
        if os.path.isfile(p):
            try:
                with open(p) as fh:
                    return json.load(fh), time.monotonic() - t0
            except (OSError, ValueError):
                time.sleep(0.05)
                continue
        time.sleep(0.2)
    return None, timeout


def child_of(parent, needle):
    for pid, st in ((int(d), statf(int(d))) for d in os.listdir("/proc") if d.isdigit()):
        if st and st["ppid"] == parent and needle in cmdline(pid):
            return pid
    return None


def observe_death(t0, pids, port, limit=LIMIT):
    """poll until all pids dead and port refuses; return per-pid death times."""
    died = {}
    port_refused_at = None
    while time.monotonic() - t0 < limit:
        for name, (pid, start) in pids.items():
            if name not in died and not alive(pid, start):
                died[name] = round(time.monotonic() - t0, 3)
        if port_refused_at is None and port_refuses(port):
            port_refused_at = round(time.monotonic() - t0, 3)
        if len(died) == len(pids) and port_refused_at is not None:
            break
        time.sleep(POLL)
    return died, port_refused_at


def leg_a():
    """Killer shell (replay's parent) SIGKILLed during the witness hold."""
    wd, work = f"{S}/wd-A", f"{S}/work-A"
    os.makedirs(wd)
    outj, logp = f"{S}/out/A.json", f"{S}/out/A.log"
    script = f'python3 -I {REPLAY} --receipt {RECEIPT} --work {work} --out {outj} --witness-dir {wd} & wait'
    shell = subprocess.Popen(["bash", "-c", script], env=env_min(), cwd=LANE,
                             stdout=open(logp, "wb"), stderr=subprocess.STDOUT,
                             start_new_session=True)
    ready, wait_s = wait_ready(wd)
    rec = {"leg": "A", "mode": "shell(SIGKILL parent of replay)", "shell_pid": shell.pid,
           "wait_ready_s": round(wait_s, 1), "ready": ready}
    if ready is None:
        rec["error"] = "no ready.json"
        shell.kill()
        return rec
    rec["server_pid"] = ready["pid"]
    replay_pid = child_of(shell.pid, "kama-live-replay")
    live_pid = child_of(replay_pid, "kama-llamacpp-live") if replay_pid else None
    rec["replay_pid"], rec["live_pid"] = replay_pid, live_pid
    snap = descendants(shell.pid)
    rec["snapshot_descendants"] = {str(k): cmdline(k) for k, v in snap.items()}
    pids = {"replay": (replay_pid, statf(replay_pid)["start"]),
            "live": (live_pid, statf(live_pid)["start"]),
            "server": (ready["pid"], statf(ready["pid"])["start"])}
    rec["ppids_pre"] = {n: statf(p[0])["ppid"] for n, p in pids.items()}
    t0 = time.monotonic()
    os.kill(shell.pid, signal.SIGKILL)
    shell.wait()
    died, refused_at = observe_death(t0, pids, ready["port"])
    rec["shell_killed_rc"] = shell.returncode
    rec["died_after_s"] = died
    rec["port_refused_after_s"] = refused_at
    rec["all_dead_within_30s"] = len(died) == 3 and max(died.values()) <= 30 and (refused_at or 99) <= 30
    rec["ppids_at_2s"] = None
    # inspect leftover files
    rec["outj_exists"] = os.path.isfile(outj)
    rerun = os.path.join(work, "rerun-receipt.json")
    rec["rerun_exists"] = os.path.isfile(rerun)
    if rec["rerun_exists"]:
        try:
            rr = json.load(open(rerun))
            rec["rerun_fields"] = {
                "setup_error": rr.get("setup_error"),
                "outcome": rr.get("outcome"),
                "witness": rr.get("witness"),
                "teardown": {k: (rr.get("teardown") or {}).get(k)
                             for k in ("returncode", "sigterm_sent", "sigkill_sent",
                                       "alive_at_teardown_start", "port_refuses",
                                       "term_wait_ms")},
                "child_pid": rr.get("child_pid"),
            }
        except ValueError as e:
            rec["rerun_parse_error"] = str(e)
    rec["ready_json_left"] = os.path.isfile(os.path.join(wd, "ready.json"))
    rec["wd_entries"] = sorted(os.listdir(wd))
    log = open(logp, "rb").read().decode("utf-8", "replace")
    rec["log_tail"] = log[-800:]
    return rec


def leg_b():
    """SIGTERM the replay mid-hold: handler chain replay->live->server."""
    wd, work = f"{S}/wd-B", f"{S}/work-B"
    os.makedirs(wd)
    outj, logp = f"{S}/out/B.json", f"{S}/out/B.log"
    script = f'python3 -I {REPLAY} --receipt {RECEIPT} --work {work} --out {outj} --witness-dir {wd} & wait'
    shell = subprocess.Popen(["bash", "-c", script], env=env_min(), cwd=LANE,
                             stdout=open(logp, "wb"), stderr=subprocess.STDOUT,
                             start_new_session=True)
    ready, wait_s = wait_ready(wd)
    rec = {"leg": "B", "mode": "SIGTERM replay", "shell_pid": shell.pid,
           "wait_ready_s": round(wait_s, 1), "ready": ready}
    if ready is None:
        rec["error"] = "no ready.json"
        shell.kill()
        return rec
    rec["server_pid"] = ready["pid"]
    replay_pid = child_of(shell.pid, "kama-live-replay")
    live_pid = child_of(replay_pid, "kama-llamacpp-live") if replay_pid else None
    rec["replay_pid"], rec["live_pid"] = replay_pid, live_pid
    pids = {"replay": (replay_pid, statf(replay_pid)["start"]),
            "live": (live_pid, statf(live_pid)["start"]),
            "server": (ready["pid"], statf(ready["pid"])["start"])}
    t0 = time.monotonic()
    os.kill(replay_pid, signal.SIGTERM)
    died, refused_at = observe_death(t0, pids, ready["port"])
    shell_rc = shell.wait(timeout=30)
    rec["shell_wait_rc"] = shell_rc  # bash reports child's status (128+15=143 if SIGTERM)
    rec["died_after_s"] = died
    rec["port_refused_after_s"] = refused_at
    rec["outj_exists"] = os.path.isfile(outj)
    if rec["outj_exists"]:
        try:
            oj = json.load(open(outj))
            rec["outj_fields"] = {"match": oj.get("match"), "refused": oj.get("refused"),
                                  "mismatches": oj.get("mismatches")}
        except ValueError as e:
            rec["outj_parse_error"] = str(e)
    rerun = os.path.join(work, "rerun-receipt.json")
    rec["rerun_exists"] = os.path.isfile(rerun)
    if rec["rerun_exists"]:
        try:
            rr = json.load(open(rerun))
            rec["rerun_fields"] = {
                "setup_error": rr.get("setup_error"),
                "outcome": rr.get("outcome"),
                "witness": rr.get("witness"),
                "teardown": {k: (rr.get("teardown") or {}).get(k)
                             for k in ("returncode", "sigterm_sent", "sigkill_sent",
                                       "alive_at_teardown_start", "port_refuses",
                                       "term_wait_ms")},
                "child_pid": rr.get("child_pid"),
            }
        except ValueError as e:
            rec["rerun_parse_error"] = str(e)
    rec["ready_json_left"] = os.path.isfile(os.path.join(wd, "ready.json"))
    log = open(logp, "rb").read().decode("utf-8", "replace")
    rec["log_tail"] = log[-800:]
    return rec


def leg_c():
    """Chain: counter-shell -> python -I -c invoker -> replay. Kill the TOP
    (the counter stand-in) to test whether the chain covers a dead counter."""
    wd, work = f"{S}/wd-C", f"{S}/work-C"
    os.makedirs(wd)
    outj, logp = f"{S}/out/C.json", f"{S}/out/C.log"
    invoker_src = "import subprocess, sys\nsys.exit(subprocess.call(sys.argv[1:]))"
    inner = (f"python3 -I -c '{invoker_src}' python3 -I {REPLAY} "
             f"--receipt {RECEIPT} --work {work} --out {outj} --witness-dir {wd} & wait")
    shell = subprocess.Popen(["bash", "-c", inner], env=env_min(), cwd=LANE,
                             stdout=open(logp, "wb"), stderr=subprocess.STDOUT,
                             start_new_session=True)
    ready, wait_s = wait_ready(wd)
    rec = {"leg": "C", "mode": "SIGKILL counter-standin (parent of INVOKER, grandparent of replay)",
           "shell_pid": shell.pid, "wait_ready_s": round(wait_s, 1), "ready": ready}
    if ready is None:
        rec["error"] = "no ready.json"
        shell.kill()
        return rec
    rec["server_pid"] = ready["pid"]
    invoker_pid = child_of(shell.pid, "subprocess.call")
    replay_pid = child_of(invoker_pid, "kama-live-replay") if invoker_pid else None
    live_pid = child_of(replay_pid, "kama-llamacpp-live") if replay_pid else None
    rec["invoker_pid"], rec["replay_pid"], rec["live_pid"] = invoker_pid, replay_pid, live_pid
    pids = {"invoker": (invoker_pid, statf(invoker_pid)["start"]),
            "replay": (replay_pid, statf(replay_pid)["start"]),
            "live": (live_pid, statf(live_pid)["start"]),
            "server": (ready["pid"], statf(ready["pid"])["start"])}
    t0 = time.monotonic()
    os.kill(shell.pid, signal.SIGKILL)
    shell.wait()
    rec["counter_dead_at_s"] = 0.0
    # what survives? probe at 0.5s, 2s, 5s
    probes = {}
    for at in (0.5, 2.0, 5.0):
        while time.monotonic() - t0 < at:
            time.sleep(0.05)
        probes[f"at_{at}s"] = {n: alive(p, s) for n, (p, s) in pids.items()}
        probes[f"at_{at}s"]["port_open"] = not port_refuses(ready["port"])
    rec["survivors"] = probes
    # now kill the invoker as the counter's teardown_leg does
    t1 = time.monotonic()
    still = {n: v for n, v in pids.items() if alive(*v)}
    if invoker_pid and alive(invoker_pid):
        os.kill(invoker_pid, signal.SIGKILL)
    died, refused_at = observe_death(t1, still, ready["port"], limit=30)
    rec["invoker_killed_at_s"] = round(t1 - t0, 2)
    rec["died_after_invoker_kill_s"] = died
    rec["port_refused_after_invoker_kill_s"] = refused_at
    rerun = os.path.join(work, "rerun-receipt.json")
    rec["rerun_exists"] = os.path.isfile(rerun)
    if rec["rerun_exists"]:
        try:
            rr = json.load(open(rerun))
            rec["rerun_fields"] = {"setup_error": rr.get("setup_error"),
                                   "outcome": rr.get("outcome"),
                                   "witness": rr.get("witness")}
        except ValueError as e:
            rec["rerun_parse_error"] = str(e)
    log = open(logp, "rb").read().decode("utf-8", "replace")
    rec["log_tail"] = log[-800:]
    return rec


def main():
    results = []
    results.append(leg_a())
    json.dump(results, open(f"{S}/out/results.json", "w"), indent=1)
    results.append(leg_b())
    json.dump(results, open(f"{S}/out/results.json", "w"), indent=1)
    results.append(leg_c())
    json.dump(results, open(f"{S}/out/results.json", "w"), indent=1)
    for r in results:
        print(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
