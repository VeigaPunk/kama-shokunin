#!/usr/bin/env python3
"""M2Ctr runner: runs each mutant counter against the lane tip and the r47-relabel
control, appending one JSONL record per run. Pristine (M00) runs first; the
pristine control measurement comes from the frozen builder's own score run."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

S = "/fast/scratch/hyaku/kama-r48/M2Ctr"
TIP = "380bcdff9c8af06997c482f6eb03db926a794a2b"
CTL_TIP = "a907a87fb7b6182f931f733c85e5ea6efb7c5126"
REPO = os.path.join(S, "ctl-r47-relabel")
PRISTINE = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round48-live-replay-v5-audit.py"
M00 = os.path.join(S, "mutants", "M00-pristine.py")
LEDGER = os.path.join(S, "ledger.jsonl")
LOCK = threading.Lock()


def run_one(tag, script, tip):
    root = os.path.join(S, "runs", tag.split("@")[0], tag.split("@")[1])
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root, exist_ok=True)
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, script, "--repo", REPO, "--tip", tip,
                            "--scratch", root], capture_output=True, text=True,
                           timeout=2400, cwd=S)
        exitcode, out, err = p.returncode, p.stdout, p.stderr[-2000:]
    except subprocess.TimeoutExpired as e:
        o = e.stdout
        out = o.decode("utf-8", "replace") if isinstance(o, bytes) else (o or "")
        exitcode, err = None, "TIMEOUT after 2400s"
    dur = round(time.time() - t0, 1)
    rec = {"tag": tag, "script": os.path.basename(script), "tip": tip, "exit": exitcode,
           "duration_s": dur, "stdout": out, "stderr_tail": err}
    with LOCK:
        with open(LEDGER, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
    first = out.split("\n")[0] if out else "(EMPTY STDOUT)"
    print(f"{tag}: exit={exitcode} {dur}s {first[:120]}", flush=True)
    return rec


def main():
    assert os.path.realpath(REPO) == REPO or os.path.isdir(REPO)
    src = open(PRISTINE).read()
    if not os.path.exists(M00):
        open(M00, "w").write(src)
    assert hashlib.sha256(open(M00, "rb").read()).hexdigest() == \
        hashlib.sha256(src.encode()).hexdigest(), "pristine copy mismatch"
    run_one("M00-pristine@tip", M00, TIP)  # network validation, blocking
    jobs = []
    for line in open(os.path.join(S, "mutants.json")):
        pass
    manifest = json.load(open(os.path.join(S, "mutants.json")))["mutants"]
    for m in manifest:
        mp = os.path.join(S, "mutants", f'{m["id"]}.py')
        jobs.append((f'{m["id"]}@tip', mp, TIP))
        jobs.append((f'{m["id"]}@ctl', mp, CTL_TIP))
    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(lambda j: run_one(*j), jobs))
    print("SWEEP-DONE runs=", 1 + len(jobs))


if __name__ == "__main__":
    main()
