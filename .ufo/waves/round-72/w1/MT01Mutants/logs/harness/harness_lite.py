#!/usr/bin/env python3
"""Shared helpers: pristine copies, exact-once textual mutation, row emission."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
S = Path("/fast/scratch/hyaku/kama-r72/MT01Mutants")
MUT = S / "mut"
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pristine_copy() -> Path:
    dst = MUT / "pristine"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LANE / "tools/pre-report-gate.py", dst / "pre-report-gate.py")
    shutil.copy2(LANE / "tools/round67-worktree-landing-check.py",
                 dst / "round67-worktree-landing-check.py")
    return dst / "pre-report-gate.py"


def apply(pristine: Path, mid: str, old: str, new: str, name: str | None = None) -> Path:
    text = pristine.read_text(encoding="utf-8")
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"pre-image count {n} != 1 for {old[:70]!r}")
    dst = MUT / mid / (name or pristine.name)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text.replace(old, new), encoding="utf-8")
    for sibling in pristine.parent.glob("round*.py"):
        if sibling.name != pristine.name:
            shutil.copy2(sibling, dst.parent / sibling.name)
    p = subprocess.run([sys.executable, "-m", "py_compile", str(dst)], capture_output=True,
                       text=True, env=ENV)
    if p.returncode != 0:
        raise RuntimeError(f"mutant does not compile: {p.stderr}")
    cache = dst.parent / "__pycache__"
    if cache.exists():
        shutil.rmtree(cache, ignore_errors=True)
    return dst


class Row:
    def __init__(self, mid, tool, mutation, verdict, command, evidence):
        self.mid, self.tool, self.mutation = mid, tool, mutation
        self.verdict, self.command, self.evidence = verdict, command, evidence

    def as_dict(self):
        return {"id": self.mid, "tool": self.tool, "mutation": self.mutation,
                "verdict": self.verdict, "command": self.command, "evidence": self.evidence}


def write_row(rows, path: Path):
    with Path(path).open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r.as_dict()) + "\n")
