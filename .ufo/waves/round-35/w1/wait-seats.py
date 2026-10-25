#!/usr/bin/env python3
"""Wait on already-dispatched seat pids. Does not spawn or replace seats."""

from __future__ import annotations

import json
import os
import signal
import time
from pathlib import Path

OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-35/w1/out")
MANIFEST = OUT / "dispatch-manifest.json"


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    started = time.mktime(time.strptime(manifest["dispatchedAt"], "%Y-%m-%dT%H:%M:%S%z"))
    # strptime %z may fail on some builds; fall back to file mtime.
    deadline = started + int(manifest["seatTimeoutSec"])
    if deadline < time.time():
        deadline = time.time() + 30
    exits = []
    pending = {row["pid"]: row for row in manifest["seats"]}
    while pending and time.time() < deadline:
        done = []
        for pid, row in pending.items():
            if not alive(pid):
                done.append(pid)
        for pid in done:
            pending.pop(pid)
        if pending:
            time.sleep(2)
    for pid, row in list(pending.items()):
        if alive(pid):
            os.kill(pid, signal.SIGTERM)
        pending[pid]["timed_out"] = True
    time.sleep(3)
    for pid, row in list(pending.items()):
        if alive(pid):
            os.kill(pid, signal.SIGKILL)
    time.sleep(1)
    for row in manifest["seats"]:
        pid = row["pid"]
        name = row["name"]
        log_path = OUT / name / "seat.log"
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
                "role": row["role"],
                "pid": pid,
                "alive_at_settle": alive(pid),
                "timed_out": bool(row.get("timed_out")),
                "report_exists": report.is_file(),
                "stdout_persisted": persisted,
                "log_bytes": log_path.stat().st_size if log_path.is_file() else 0,
            }
        )
    (OUT / "seat-exit-codes.json").write_text(json.dumps(exits, indent=1) + "\n")
    returned = sum(1 for row in exits if row["report_exists"])
    print(f"settled seats={len(exits)} reports={returned} timed_out={sum(1 for r in exits if r['timed_out'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
