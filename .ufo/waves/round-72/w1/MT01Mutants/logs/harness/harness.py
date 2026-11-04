#!/usr/bin/env python3
"""MT01Mutants harness: apply one textual mutant to a pristine tool copy, run the
same detector on pristine and mutant, record verdict.

Never touches lane bytes: pristine sources are read from LANE/tools and copied.
Every git mutation happens inside a fixture created under $S/fixtures/<id>/repo.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
S = Path("/fast/scratch/hyaku/kama-r72/MT01Mutants")
MUT = S / "mut"
FIX = S / "fixtures"
LOGS = S / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

PRistine = {
    "scope": LANE / "tools/round72-round-scope.py",
    "bind": LANE / "tools/round72-receipt-tip-binding.py",
    "gate": LANE / "tools/pre-report-gate.py",
}

ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GIT_TERMINAL_PROMPT="0")


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(cmd, cwd=None, timeout=300, env=None):
    try:
        p = subprocess.run(cmd, cwd=cwd, timeout=timeout, capture_output=True, text=True,
                           env=env or ENV)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired as exc:
        return 124, f"timeout after {timeout}s\n{exc.stdout or ''}{exc.stderr or ''}"
    except OSError as exc:
        return 127, f"spawn failed: {exc}"


def git(repo: Path, *args, commit=False, check=True):
    base = ["git", "-C", str(repo)]
    if commit:
        base += ["-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
                 "-c", "commit.gpgsign=false"]
    rc, out = run(base + list(args))
    if check and rc != 0:
        raise RuntimeError(f"git {' '.join(args)} rc={rc}: {out.strip()}")
    return rc, out


def assert_toplevel(repo: Path):
    rc, out = git(repo, "rev-parse", "--show-toplevel")
    top = out.strip()
    if Path(os.path.realpath(top)) != Path(os.path.realpath(str(repo))):
        raise RuntimeError(f"toplevel {top!r} != fixture {str(repo)!r}")
    return top


def fresh(name: str) -> Path:
    d = FIX / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    return d


def write(path: Path, data, mode=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data, encoding="utf-8")
    if mode:
        os.chmod(path, mode)


def mutate(src: Path, dst: Path, old: str, new: str, occurrences: int = 1):
    text = src.read_text(encoding="utf-8")
    n = text.count(old)
    if n != occurrences:
        raise RuntimeError(f"pre-image count {n} != {occurrences} for {old[:80]!r}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text.replace(old, new, occurrences), encoding="utf-8")
    rc, out = run([sys.executable, "-m", "py_compile", str(dst)])
    if rc != 0:
        raise RuntimeError(f"mutant does not compile: {out}")
    return dst


def unlink_pyc(dst: Path):
    cache = dst.parent / "__pycache__"
    if cache.exists():
        shutil.rmtree(cache, ignore_errors=True)


def diff_lines(src: Path, dst: Path, ctx: int = 0):
    rc, out = run(["diff", "-u", str(src), str(dst)])
    return out


class Row:
    def __init__(self, mid, tool, mutation, verdict, command, evidence):
        self.mid, self.tool, self.mutation = mid, tool, mutation
        self.verdict, self.command, self.evidence = verdict, command, evidence
