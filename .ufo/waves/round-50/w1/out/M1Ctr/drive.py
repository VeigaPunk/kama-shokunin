#!/usr/bin/env python3
"""Run counter mutants against the lane clone at tip and base.
Usage: drive.py <manifest.json> <label-filter-regex> [parallel]
Each entry: label = <id>-<tip|base>. Writes $S/results.jsonl lines and
$S/logs/<label>.log (stdout+stderr). On timeout kills the run's process tree."""
import json, os, re, signal, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

S = "/fast/scratch/hyaku/kama-r50/M1Ctr"
LANE = f"{S}/lane"
TIP = "97c864bead3ee4a2f629574e77263d33834ec98a"
BASE = "26ecba64ad6fb571d09074b07202d1618a46ecd1"
TIMEOUT = 540

def kill_tree(label):
    # every process of the run has the run dir in argv (--scratch / --work / -m)
    subprocess.run(["pkill", "-9", "-f", f"M1Ctr/run/{label}"], capture_output=True)

def run(job):
    label, script, rev = job["label"], job["script"], job["rev"]
    rundir = f"{S}/run/{label}"
    os.makedirs(rundir, exist_ok=True)
    out = f"{S}/out/{label}.txt"
    log = f"{S}/logs/{label}.log"
    argv = ["python3", script, "--repo", LANE, "--tip", rev,
            "--scratch", rundir, "--out", out]
    t0 = time.monotonic()
    with open(log, "wb") as lf:
        p = subprocess.Popen(argv, stdout=lf, stderr=subprocess.STDOUT,
                             start_new_session=True)
        try:
            rc = p.wait(timeout=TIMEOUT)
            status = "done"
        except subprocess.TimeoutExpired:
            status = "timeout"
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except OSError:
                pass
            kill_tree(label)
            rc = None
    dur = round(time.monotonic() - t0, 1)
    kill_tree(label)  # hygiene: no leftovers from this run
    verdict = None
    try:
        txt = open(out).read()
        m = re.search(r"^bind=\d teardown=\d newrow=\d bound=\d/\d met=(True|False)", txt, re.M)
        verdict = m.group(0) if m else None
    except OSError:
        txt = ""
    rec = {"label": label, "id": job["id"], "rev": rev[:8], "rc": rc,
           "status": status, "dur_s": dur, "verdict": verdict,
           "out": out, "log": log}
    with open(f"{S}/results.jsonl", "a") as rf:
        rf.write(json.dumps(rec) + "\n")
    print(f"{label}: rc={rc} {status} {dur}s {verdict}", flush=True)
    return rec

def main():
    man = json.load(open(sys.argv[1]))
    filt = re.compile(sys.argv[2]) if len(sys.argv) > 2 else re.compile(".")
    par = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    jobs = []
    for e in man:
        if not filt.search(e["id"]):
            continue
        for tag, rev in (("tip", TIP), ("base", BASE)):
            jobs.append({"label": f"{e['id']}-{tag}", "id": e["id"],
                         "script": e["file"], "rev": rev})
    print(f"{len(jobs)} runs, parallel={par}", flush=True)
    with ThreadPoolExecutor(max_workers=par) as ex:
        list(ex.map(run, jobs))
    print("all done", flush=True)

if __name__ == "__main__":
    main()
