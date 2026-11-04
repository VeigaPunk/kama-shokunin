#!/usr/bin/env python3
"""Assemble W/w1/MT01Mutants/{mutants.tsv,logs/} and assert the scored bytes still
match the lane bytes (no report on stale hashes)."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
S = Path("/fast/scratch/hyaku/kama-r72/MT01Mutants")
W = LANE / ".ufo/waves/round-72/w1/MT01Mutants"
LOGS = S / "logs"

TOOLS = {
    "gate": ("tools/pre-report-gate.py", S / "mut/pristine/pre-report-gate.py"),
    "round72-round-scope.py": ("tools/round72-round-scope.py",
                               S / "mut/pristine-scope/round72-round-scope.py"),
    "round72-receipt-tip-binding.py": ("tools/round72-receipt-tip-binding.py",
                                       S / "mut/pristine-bind/round72-receipt-tip-binding.py"),
}


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main() -> int:
    stale = []
    for name, (rel, pristine) in TOOLS.items():
        live = sha(LANE / rel)
        scored = sha(pristine)
        print(f"{name}: lane={live[:16]} scored={scored[:16]} {'OK' if live == scored else 'STALE'}")
        if live != scored:
            stale.append(name)
    if stale:
        print("REFUSING to publish: " + ",".join(stale))
        return 1

    W.mkdir(parents=True, exist_ok=True)
    (W / "logs").mkdir(exist_ok=True)
    rows = []
    for src in ("rows-gate.jsonl", "rows-scope.jsonl", "rows-bind.jsonl"):
        for line in (S / src).read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))

    order = {"gate": 0, "round72-round-scope.py": 1, "round72-receipt-tip-binding.py": 2}
    rows.sort(key=lambda r: (order.get(r["tool"], 9), r["id"]))

    with (W / "mutants.tsv").open("w", encoding="utf-8") as fh:
        fh.write("id\ttool\tmutation\tverdict\tcommand\tevidence\n")
        for r in rows:
            fh.write("\t".join(str(r[k]).replace("\t", " ") for k in
                               ("id", "tool", "mutation", "verdict", "command", "evidence")) + "\n")

    for f in sorted(LOGS.glob("*.json")):
        shutil.copy2(f, W / "logs" / f.name)
    for f in sorted(LOGS.glob("*.log")):
        shutil.copy2(f, W / "logs" / f.name)

    # per-mutant unified diff (pristine -> mutant) for every applied mutant
    diffs = 0
    for mid_dir in sorted((S / "mut").iterdir()):
        if not mid_dir.is_dir() or mid_dir.name.startswith("pristine"):
            continue
        mid = mid_dir.name
        tool = next(iter(mid_dir.glob("*.py")))
        if tool.name == "round67-worktree-landing-check.py":
            tool = next(p for p in mid_dir.glob("*.py")
                        if p.name != "round67-worktree-landing-check.py")
        pristine = TOOLS["gate"][1] if tool.name == "pre-report-gate.py" else \
            (TOOLS["round72-round-scope.py"][1] if "scope" in tool.name
             else TOOLS["round72-receipt-tip-binding.py"][1])
        out = subprocess.run(["diff", "-u", str(pristine), str(tool)],
                             capture_output=True, text=True).stdout
        (W / "logs" / f"{mid}.diff").write_text(out, encoding="utf-8")
        diffs += 1

    killed = sum(1 for r in rows if r["verdict"] == "killed")
    survived = [r for r in rows if r["verdict"] == "survived"]
    per_tool = {}
    for r in rows:
        per_tool.setdefault(r["tool"], [0, 0])
        per_tool[r["tool"]][0 if r["verdict"] == "killed" else 1] += 1
    print(f"rows={len(rows)} killed={killed} survived={len(survived)} diffs={diffs}")
    for tool, (k, sv) in per_tool.items():
        print(f"  {tool}: killed={k} survived={sv}")
    for r in survived:
        print(f"  SURVIVOR {r['id']}: {r['mutation']} :: {r['evidence']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
