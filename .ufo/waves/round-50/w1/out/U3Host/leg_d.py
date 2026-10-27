#!/usr/bin/env python3
"""Leg D: counter-stand-in killed; does the orphaned chain self-clean at
witness timeout? Same chain as leg C but --witness-timeout 15 and no
invoker kill until after timeout observed."""
import json, os, signal, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from teardown_walk import (env_min, statf, alive, child_of, port_refuses,
                           wait_ready, cmdline)

S = os.environ["S"]
LANE = os.path.join(S, "lane")
REPLAY = os.path.join(LANE, "tools/kama-live-replay.py")
RECEIPT = os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-1.json")


def main():
    wd, work = f"{S}/wd-D", f"{S}/work-D"
    os.makedirs(wd)
    outj, logp = f"{S}/out/D.json", f"{S}/out/D.log"
    invoker_src = "import subprocess, sys\nsys.exit(subprocess.call(sys.argv[1:]))"
    inner = (f"python3 -I -c '{invoker_src}' python3 -I {REPLAY} "
             f"--receipt {RECEIPT} --work {work} --out {outj} --witness-dir {wd} "
             f"--witness-timeout 15 & wait")
    shell = subprocess.Popen(["bash", "-c", inner], env=env_min(), cwd=LANE,
                             stdout=open(logp, "wb"), stderr=subprocess.STDOUT,
                             start_new_session=True)
    ready, wait_s = wait_ready(wd)
    rec = {"leg": "D", "mode": "SIGKILL counter-standin; witness-timeout 15; no further kills",
           "wait_ready_s": round(wait_s, 1), "ready": ready}
    if ready is None:
        rec["error"] = "no ready.json"
        shell.kill()
        print(json.dumps(rec, indent=1))
        return
    invoker_pid = child_of(shell.pid, "subprocess.call")
    replay_pid = child_of(invoker_pid, "kama-live-replay") if invoker_pid else None
    live_pid = child_of(replay_pid, "kama-llamacpp-live") if replay_pid else None
    rec["pids"] = {"shell": shell.pid, "invoker": invoker_pid, "replay": replay_pid,
                   "live": live_pid, "server": ready["pid"]}
    pids = {"invoker": (invoker_pid, statf(invoker_pid)["start"]),
            "replay": (replay_pid, statf(replay_pid)["start"]),
            "live": (live_pid, statf(live_pid)["start"]),
            "server": (ready["pid"], statf(ready["pid"])["start"])}
    t0 = time.monotonic()
    os.kill(shell.pid, signal.SIGKILL)
    shell.wait()
    # watch for self-clean over witness-timeout + margin
    events = {}
    port_refused_at = None
    while time.monotonic() - t0 < 40:
        dt = time.monotonic() - t0
        for name, (pid, start) in pids.items():
            if name not in events and not alive(pid, start):
                events[name] = round(dt, 2)
        if port_refused_at is None and port_refuses(ready["port"]):
            port_refused_at = round(dt, 2)
        if len(events) == 4 and port_refused_at is not None:
            break
        time.sleep(0.2)
    rec["selfclean_after_s"] = events
    rec["port_refused_after_s"] = port_refused_at
    rec["survivors_at_40s"] = {n: alive(p, s) for n, (p, s) in pids.items()}
    # rerun receipt: witness.released false expected; orphaned relative to replay (alive) -> false
    rerun = os.path.join(work, "rerun-receipt.json")
    rec["rerun_exists"] = os.path.isfile(rerun)
    if rec["rerun_exists"]:
        try:
            rr = json.load(open(rerun))
            rec["rerun_fields"] = {"setup_error": rr.get("setup_error"),
                                   "outcome": rr.get("outcome"),
                                   "witness": rr.get("witness"),
                                   "teardown_sigterm": (rr.get("teardown") or {}).get("sigterm_sent"),
                                   "teardown_port_refuses": (rr.get("teardown") or {}).get("port_refuses")}
        except ValueError as e:
            rec["rerun_parse_error"] = str(e)
    rec["outj_exists"] = os.path.isfile(outj)
    if rec["outj_exists"]:
        try:
            oj = json.load(open(outj))
            rec["outj_fields"] = {"match": oj.get("match"), "refused": oj.get("refused"),
                                  "live_exit": oj.get("live_exit")}
        except ValueError as e:
            rec["outj_parse_error"] = str(e)
    rec["ready_json_left"] = os.path.isfile(os.path.join(wd, "ready.json"))
    print(json.dumps(rec, indent=1))
    with open(f"{S}/out/legD.json", "w") as fh:
        json.dump(rec, fh, indent=1)


if __name__ == "__main__":
    main()
