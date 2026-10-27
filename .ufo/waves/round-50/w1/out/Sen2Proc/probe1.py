#!/usr/bin/env python3
"""Sen2Proc probe 1: does round50-replay-bind-audit.pid_alive bind a pid to its starttime,
and does a rapid spawn loop / a forced pid reuse show it?"""
import importlib.util
import json
import os
import subprocess
import sys
import time

C1 = "/fast/scratch/hyaku/kama-r50/Sen2Proc/imp/c1.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


c1 = load("c1", C1)


def stat_now(pid, tries=200):
    for _ in range(tries):
        st = c1.stat_fields(pid)
        if st is not None:
            return st
        time.sleep(0.002)
    return None


def mode_direct():
    out = {"mode": "direct"}
    p = subprocess.Popen(["sleep", "5"])
    try:
        st = stat_now(p.pid)
        out.update({
            "pid": p.pid,
            "stat_state_ppid_start": st,
            "alive_no_start": c1.pid_alive(p.pid),
            "alive_true_start": c1.pid_alive(p.pid, st[2]),
            "alive_start_plus_1": c1.pid_alive(p.pid, st[2] + 1),
            "alive_start_minus_1": c1.pid_alive(p.pid, st[2] - 1),
        })
    finally:
        p.kill()
        p.wait()
    # rapid spawn loop: 300 short-lived children, starttimes and post-exit aliveness
    rows, prev = [], None
    for _ in range(300):
        q = subprocess.Popen(["/bin/true"])
        st = stat_now(q.pid)
        q.wait()
        start = st[2] if st else None
        rows.append({"pid": q.pid, "start": start,
                     "alive_after_with_start": c1.pid_alive(q.pid, start) if start else None,
                     "alive_after_no_start": c1.pid_alive(q.pid)})
        if prev is not None and start is not None:
            assert start >= prev, (q.pid, start, prev)
        prev = start if start is not None else prev
    out["rapid"] = {
        "n": len(rows),
        "starttime_non_decreasing": True,
        "overlap_pids": len({r["pid"] for r in rows}) != len(rows),
        "any_alive_after_with_start": sum(1 for r in rows if r["alive_after_with_start"]),
        "any_alive_after_no_start": sum(1 for r in rows if r["alive_after_no_start"]),
        "sample": rows[:3],
    }
    return out


def mode_reuse():
    """Run inside `unshare -r -p -f --mount-proc`: force a recycled pid via ns_last_pid,
    then evaluate the counter's predicates against the pid as the OLD process's snapshot
    recorded them, and perform exactly what reap() would do on a true predicate."""
    import signal
    out = {"mode": "reuse-in-pidns", "ns_pid": os.getpid(), "clk_tck": os.sysconf("SC_CLK_TCK"),
           "attempts": []}

    def spawn():
        q = subprocess.Popen(["sleep", "30"])
        st = stat_now(q.pid)
        return q, st

    def attempt(delay, kill_on_predicate):
        q1, st1 = spawn()
        pid_a, start_a = q1.pid, st1[2]
        q1.kill()
        q1.wait()
        if delay:
            time.sleep(delay)
        with open("/proc/sys/kernel/ns_last_pid", "w") as fh:
            fh.write(str(pid_a - 1))
        q2, st2 = spawn()
        start_b = st2[2] if st2 else None
        row = {"delay_s": delay,
               "first": {"pid": pid_a, "start": start_a},
               "second": {"pid": q2.pid, "start": start_b},
               "pid_reused": q2.pid == pid_a,
               "start_delta": (start_b - start_a) if start_b is not None else None,
               "alive_with_old_start": c1.pid_alive(pid_a, start_a),
               "alive_no_start": c1.pid_alive(pid_a),
               "teardown_snapshot_reports_alive": c1.pid_alive(pid_a, start_a)}
        try:
            if kill_on_predicate and row["alive_with_old_start"]:
                os.kill(pid_a, signal.SIGKILL)  # exactly reap()'s action
                time.sleep(0.05)
            row["new_process_state"] = "gone" if q2.poll() is not None else "alive"
            row["new_process_rc"] = q2.poll()
            row["reap_acted_on_new_process"] = kill_on_predicate and q2.poll() is not None
        finally:
            try:
                q2.kill()
            except OSError:
                pass
            q2.wait()
        return row

    for _ in range(5):
        out["attempts"].append(dict(kind="same-tick", **attempt(0, True)))
    for _ in range(2):
        out["attempts"].append(dict(kind="later-tick", **attempt(0.05, True)))
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "direct"
    print(json.dumps(mode_reuse() if mode == "reuse" else mode_direct()))
