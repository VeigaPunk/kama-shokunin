#!/usr/bin/env python3
"""Launch one validated Kimi wave. No --auto. No seat replacement.

Reads the validator's run.json taskCall and starts every lane in one batch.
Each seat is `kimi --agent ufo-<role> --add-dir ... -p <context+task>`.
A seat that dies stays dead: it is never replaced.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
FLEET = Path("/home/vgpnk/Projects/shokunin")
SHOKUKNOW = Path("/home/vgpnk/Projects/shokuknow")
WAVE = LANE / ".ufo/waves/round-36/w2"
RUN = WAVE / "run.json"
OUT = WAVE / "out"
SEAT_TIMEOUT = 480


def main() -> int:
    payload = json.loads(RUN.read_text())
    task_call = payload.get("taskCall")
    if not task_call or not task_call.get("tasks"):
        raise SystemExit("refusing to launch: empty taskCall")
    context = task_call["context"]
    tasks = task_call["tasks"]
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "dispatchedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "transport": "kimi -p batched; no --auto; AgentSwarm tool unavailable to this L1",
        "seatTimeoutSec": SEAT_TIMEOUT,
        "seats": [],
    }
    procs = []
    for task in tasks:
        name = task["name"]
        role = task["agent"]
        prompt = context + "\n\n" + task["task"]
        seat_dir = OUT / name
        seat_dir.mkdir(parents=True, exist_ok=True)
        (seat_dir / "prompt.txt").write_text(prompt)
        log_path = seat_dir / "seat.log"
        log_f = log_path.open("w")
        cmd = [
            "kimi",
            "--agent",
            f"ufo-{role}",
            "--add-dir",
            str(FLEET),
            "--add-dir",
            str(SHOKUKNOW),
            "--add-dir",
            str(LANE),
            "-p",
            prompt,
        ]
        if "--auto" in cmd:
            raise SystemExit("refusing to launch: --auto in argv")
        proc = subprocess.Popen(
            cmd,
            cwd=str(LANE),
            stdout=log_f,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        procs.append((name, role, proc, log_f, log_path, time.time()))
        manifest["seats"].append(
            {
                "name": name,
                "role": role,
                "pid": proc.pid,
                "argv0": "kimi",
                "flags": "--agent -p --add-dir; no --auto",
            }
        )
    (OUT / "dispatch-manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"launched {len(procs)} seats", flush=True)
    deadline = time.time() + SEAT_TIMEOUT + 30
    pending = {
        proc.pid: (name, role, proc, log_f, log_path, started)
        for name, role, proc, log_f, log_path, started in procs
    }
    exits = []
    while pending and time.time() < deadline:
        done = []
        for pid, row in list(pending.items()):
            name, role, proc, log_f, log_path, started = row
            rc = proc.poll()
            if rc is None and time.time() - started > SEAT_TIMEOUT:
                proc.terminate()
                try:
                    proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=10)
                rc = proc.returncode if proc.returncode is not None else 124
            if rc is not None:
                log_f.close()
                report = OUT / f"{name}.md"
                persisted = False
                if not report.is_file() and log_path.is_file():
                    text = log_path.read_text(errors="replace")
                    if text.strip():
                        report.write_text(text)
                        persisted = True
                exits.append(
                    {
                        "name": name,
                        "role": role,
                        "pid": pid,
                        "rc": rc,
                        "timed_out": rc == 124 or (time.time() - started) >= SEAT_TIMEOUT,
                        "report_exists": report.is_file(),
                        "stdout_persisted": persisted,
                        "log_bytes": log_path.stat().st_size if log_path.is_file() else 0,
                    }
                )
                done.append(pid)
        for pid in done:
            pending.pop(pid, None)
        if pending:
            time.sleep(2)
    for pid, row in list(pending.items()):
        name, role, proc, log_f, log_path, started = row
        proc.kill()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        log_f.close()
        exits.append(
            {
                "name": name,
                "role": role,
                "pid": pid,
                "rc": 124,
                "timed_out": True,
                "report_exists": (OUT / f"{name}.md").is_file(),
                "stdout_persisted": False,
                "log_bytes": log_path.stat().st_size if log_path.is_file() else 0,
                "note": "killed at wave deadline; not replaced",
            }
        )
    (OUT / "seat-exit-codes.json").write_text(json.dumps(exits, indent=1) + "\n")
    returned = sum(1 for row in exits if row["report_exists"])
    timed = sum(1 for row in exits if row.get("timed_out"))
    print(f"settled seats={len(exits)} reports={returned} timed_out={timed}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
