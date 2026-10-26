#!/usr/bin/env python3
"""run-witnessed.py - run one witnessed replay with the X1Observe observer attached.

For each receipt: a fresh witness directory, this seat's own observer
(observe-witness.py) started first, then the lane's tools/kama-live-replay.py at
the measured commit with --witness-dir, so the observer - not the replay and not
the C1 counter - checks the held server from outside and writes the receipt.
The observer writes <wdir>/release after its observations; the replay then tears
the server down and the observer sees the pid disappear.

Usage:
  run-witnessed.py --lane DIR --receipt R --work W --wdir D --observations O
                   --replay-receipt J [--observer ...] [--witness-timeout 60]

Exit: replay exit code; prints one line with both verdicts.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OBSERVER = os.path.join(HERE, "observe-witness.py")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--wdir", required=True)
    ap.add_argument("--observations", required=True)
    ap.add_argument("--replay-receipt", required=True)
    ap.add_argument("--observer", default=DEFAULT_OBSERVER)
    ap.add_argument("--witness-timeout", type=float, default=60.0)
    a = ap.parse_args(argv)

    for path in (a.wdir,):
        if os.path.isdir(path):
            shutil.rmtree(path)
        os.makedirs(path)
    os.makedirs(a.work, exist_ok=True)
    replay_tool = os.path.join(a.lane, "tools", "kama-live-replay.py")
    if not os.path.isfile(replay_tool):
        print(f"missing replay tool: {replay_tool}")
        return 2

    obs = subprocess.Popen([sys.executable, a.observer, "--witness-dir", a.wdir,
                            "--out", a.observations, "--receipt", a.receipt],
                           cwd=a.wdir)
    rep = subprocess.run([sys.executable, replay_tool, "--receipt", a.receipt,
                          "--work", a.work, "--out", a.replay_receipt,
                          "--witness-dir", a.wdir,
                          "--witness-timeout", str(a.witness_timeout)],
                         capture_output=True, text=True)
    try:
        obs_rc = obs.wait(timeout=120)
    except subprocess.TimeoutExpired:
        obs.kill()
        obs_rc = None
    if not os.path.exists(os.path.join(a.wdir, "release")):
        # watchdog: the observer died before freeing the server; free it here so
        # the replay is not stalled, and record the run as uninstrumented
        with open(os.path.join(a.wdir, "release"), "w") as fh:
            fh.write("driver-watchdog\n")
        print("WATCHDOG: observer left no release file; released from the driver")
    observations = None
    if os.path.isfile(a.observations):
        with open(a.observations) as fh:
            observations = json.load(fh)
    else:
        observations = {"verdict": "observer-crashed", "checks": []}
        with open(a.observations, "w") as fh:
            json.dump(observations, fh, indent=1)
    print("run-witnessed replay_exit=%s observer_exit=%s observer_verdict=%s"
          % (rep.returncode, obs_rc,
             (observations or {}).get("verdict")))
    for line in (rep.stdout or "").splitlines():
        print("  replay:", line)
    for line in (rep.stderr or "").strip().splitlines()[-5:]:
        print("  replay-stderr:", line)
    return rep.returncode


if __name__ == "__main__":
    sys.exit(main())
