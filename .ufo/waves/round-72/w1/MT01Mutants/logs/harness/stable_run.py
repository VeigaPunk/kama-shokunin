#!/usr/bin/env python3
"""Run each mutant family against whatever bytes are live, and repeat the family
until the lane hash is unchanged across the whole run (the three tools are being
edited by their authors while this seat scores them)."""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
S = Path("/fast/scratch/hyaku/kama-r72/MT01Mutants")

FAMILIES = [
    ("scope", "scope_mutants.py", LANE / "tools/round72-round-scope.py",
     S / "mut/pristine-scope/round72-round-scope.py"),
    ("bind", "bind_mutants.py", LANE / "tools/round72-receipt-tip-binding.py",
     S / "mut/pristine-bind/round72-receipt-tip-binding.py"),
    ("gate", "gate_mutants.py", LANE / "tools/pre-report-gate.py",
     S / "mut/pristine/pre-report-gate.py"),
]


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).exists() else "-"


def main() -> int:
    for name, script, live, pristine in FAMILIES:
        for attempt in range(1, 7):
            before = sha(live)
            if before == sha(pristine) and attempt == 1:
                print(f"{name}: already scored at {before[:16]} (bytes unchanged) -- skip")
                break
            p = subprocess.run([sys.executable, str(S / script)], capture_output=True, text=True)
            tail = [ln for ln in p.stdout.strip().splitlines() if ln.strip()][-3:]
            after = sha(live)
            print(f"{name} attempt={attempt} before={before[:16]} after={after[:16]} rc={p.returncode}")
            for ln in tail:
                print("   " + ln)
            if before == after and p.returncode == 0:
                print(f"{name}: PINNED at {after[:16]}")
                break
        else:
            print(f"{name}: NOT STABLE after 6 attempts")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
