#!/usr/bin/env python3
"""Round-88 repair receipt (not a frozen counter): the two router states wave-1 CR01 showed the
frozen rule grading against its own completion oracle — `sleeping` and default-autoload `unloaded`.

Reuses the frozen counter's helpers (tools/round88-router-cells.py) by import; runs the probe bytes
at --rev on lane-owned pinned b11755 router children and prints, per cell, the probe verdict, the
oracle's verdict (real POST /v1/chat/completions: 200 -> MODEL_OK, 400 'model is not loaded' ->
MODEL_UNLOADED) and ok=<0|1>. Exit 0 iff every cell agrees.

usage: oracle-cells.py --repo <lane> --rev <rev> --work <scratch>
"""
import argparse, importlib.util, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--repo", type=Path, required=True)
ap.add_argument("--rev", required=True)
ap.add_argument("--work", type=Path, required=True)
a = ap.parse_args()
spec = importlib.util.spec_from_file_location("rc", a.repo / "tools/round88-router-cells.py")
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)

a.work.mkdir(parents=True, exist_ok=True)
work = Path(tempfile.mkdtemp(prefix="oracle-cells-", dir=a.work))
rows = []
try:
    probe = work / "kama-probe.sh"
    probe.write_bytes(subprocess.run(["git", "-C", str(a.repo), "show", f"{a.rev}:tools/kama-probe.sh"],
                                     capture_output=True, check=True).stdout)
    env = dict(os.environ, TMPDIR=str(work))
    models = work / "models"
    models.mkdir()
    shutil.copyfile(rc.MODEL, models / f"{rc.MODEL_ID}.gguf")

    def child(extra):
        port = rc.free_port()
        p = subprocess.Popen([str(rc.SERVER), "--models-dir", str(models), "--models-max", "1",
                              "--host", "127.0.0.1", "--port", str(port)] + extra,
                             stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, start_new_session=True)
        return p, port

    def stop(p):
        try:
            os.killpg(p.pid, 15)
            p.wait(timeout=15)
        except Exception:
            os.killpg(p.pid, 9)

    # S1: sleeping (no autoload): load, idle past --sleep-idle-seconds, probe, oracle
    p, port = child(["--no-models-autoload", "--sleep-idle-seconds", "2"])
    try:
        rc.wait_status(port, "unloaded", 30)
        rc.http_json("POST", f"http://127.0.0.1:{port}/models/load", {"model": rc.MODEL_ID})
        rc.wait_status(port, "loaded")
        rc.wait_status(port, "sleeping", 30)
        got, reason = rc.run_probe(probe, port, rc.MODEL_ID, env)
        rows.append(("S1-sleeping-no-autoload", rc.oracle(port), got, reason))
    finally:
        stop(p)
    # A1: unloaded on a default (autoload) router
    p, port = child([])
    try:
        rc.wait_status(port, "unloaded", 30)
        got, reason = rc.run_probe(probe, port, rc.MODEL_ID, env)
        rows.append(("A1-unloaded-autoload", rc.oracle(port), got, reason))
    finally:
        stop(p)
    # N1: unloaded on a --no-models-autoload router (control: must stay MODEL_UNLOADED)
    p, port = child(["--no-models-autoload"])
    try:
        rc.wait_status(port, "unloaded", 30)
        got, reason = rc.run_probe(probe, port, rc.MODEL_ID, env)
        rows.append(("N1-unloaded-no-autoload", rc.oracle(port), got, reason))
    finally:
        stop(p)
finally:
    shutil.rmtree(work, ignore_errors=True)
bad = 0
for cid, exp, got, reason in rows:
    bad += exp != got
    print(f"ORACLE_CELL {cid} oracle={exp} probe={got} reason={reason} ok={int(exp == got)}")
print(f"ORACLE_CELLS rev={a.rev} cells={len(rows)} mismatches={bad}")
sys.exit(0 if bad == 0 and len(rows) == 3 else 1)
