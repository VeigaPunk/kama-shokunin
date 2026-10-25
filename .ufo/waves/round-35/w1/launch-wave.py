#!/usr/bin/env python3
"""Launch one validated Kimi wave. No --auto. No seat replacement.

Reads the validator run.json taskCall and starts every lane in one batch.
Each seat is `kimi --agent ufo-<role> --add-dir <fleet> --add-dir <shokuknow>
-p <context+task>`. The --prompt/--auto pair is not used. Stdout is kept.
If a seat exits without writing its Report path, nonempty stdout is copied
there and marked stdout-persisted. A timed-out seat stays dead.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
FLEET = Path("/home/vgpnk/Projects/shokunin")
SHOKUKNOW = Path("/home/vgpnk/Projects/shokuknow")
RUN = LANE / ".ufo/waves/round-35/w1/run.json"
OUT = LANE / ".ufo/waves/round-35/w1/out"
SEAT_TIMEOUT = 480

def main() -> int:
    payload = json.loads(RUN.read_text())
    task_call = payload["taskCall"]
    context = task_call["context"]
    tasks = task_call["tasks"]
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "dispatchedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "transport": "kimi -p batched; no --auto; AgentSwarm tool unavailable",
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
        prompt_path = seat_dir / "prompt.txt"
        prompt_path.write_text(prompt)
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
            {"name": name, "role": role, "pid": proc.pid, "argv0": "kimi", "flags": "--agent -p --add-dir; no --auto"}
        )
    (OUT / "dispatch-manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"launched {len(procs)} seats", flush=True)
    deadline = time.time() + SEAT_TIMEOUT + 30
    pending = {p.pid: (name, role, proc, log_f, log_path, started) for name, role, proc, log_f, log_path, started in procs}
    exits = []
    while pending and time.time() < deadline:
        done = []
        for pid, row in pending.items():
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
                if not report.is_file():
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
                        "report_exists": report.is_file(),
                        "stdout_persisted": persisted,
                        "log_bytes": log_path.stat().st_size,
                    }
                )
                done.append(pid)
        for pid in done:
            pending.pop(pid)
        if pending:
            time.sleep(2)
    for pid, row in list(pending.items()):
        name, role, proc, log_f, log_path, started = row
        proc.kill()
        proc.wait(timeout=10)
        log_f.close()
        exits.append(
            {
                "name": name,
                "role": role,
                "pid": pid,
                "rc": 124,
                "report_exists": (OUT / f"{name}.md").is_file(),
                "stdout_persisted": False,
                "log_bytes": log_path.stat().st_size,
                "note": "killed at wave deadline; not replaced",
            }
        )
    (OUT / "seat-exit-codes.json").write_text(json.dumps(exits, indent=1) + "\n")
    returned = sum(1 for row in exits if row["report_exists"])
    print(f"settled seats={len(exits)} reports={returned}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
