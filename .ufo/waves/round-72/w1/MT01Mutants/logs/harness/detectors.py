#!/usr/bin/env python3
"""Detectors + verdict logic for MT01Mutants.

Parsers key off the FROZEN predicate sentences in plans/round-72-claims.md, so a
mutant is scored on the observables the claim names, not on incidental text.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r72/MT01Mutants")
FIX = S / "fixtures"
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

SCOPE_LINE = re.compile(r"ROUND_SCOPE round=(\d+) cases=(\d+) findings=(\d+)")
SCOPE_FIND = re.compile(r"ROUND_SCOPE_FINDING (\S+)")
BIND_LINE = re.compile(
    r"RECEIPT_TIP_BINDING round=(\d+) cited=(\d+) bound=(\d+) unbound=(\d+) shifted=(\d+) stale=(\d+)")
BIND_FIND = re.compile(r"RECEIPT_TIP_FINDING (unbound|shifted|stale) (\S+)")
GATE_LINE = re.compile(r"PRE_REPORT round=(\d+) arms=(\d+) failed=(\d+) uncommitted=(\d+)")
GATE_SELF = re.compile(r"PRE_REPORT_SELFTEST pass=(\d+) fail=(\d+)")


def run(cmd, cwd=None, timeout=300):
    try:
        p = subprocess.run([str(c) for c in cmd], cwd=str(cwd) if cwd else None,
                           capture_output=True, text=True, env=ENV, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired as exc:
        return 124, f"TIMEOUT {timeout}s\n{exc.stdout or ''}{exc.stderr or ''}"
    except OSError as exc:
        return 127, f"SPAWN-FAIL {exc}"


def scope_obs(tool: Path) -> dict:
    out = {}
    for case in ("clean", "label-missing", "label-wrong", "stray", "ignored"):
        repo = FIX / f"scope-{case}" / "repo"
        rc, text = run([sys.executable, tool, "--repo", repo, "--round", 72, "--tip", "master"],
                       cwd=tool.parent)
        m = SCOPE_LINE.search(text)
        out[case] = {
            "exit": rc,
            "line": m.group(0) if m else None,
            "findings": int(m.group(3)) if m else None,
            "cases": sorted(set(SCOPE_FIND.findall(text))),
            "tail": text.strip().splitlines()[-3:],
        }
    return out


def bind_obs(tool: Path) -> dict:
    out = {}
    for case in ("clean", "unbound", "shifted", "stale"):
        repo = FIX / f"bind-{case}" / "repo"
        rc, text = run([sys.executable, tool, "--repo", repo, "--round", 72, "--tip", "master"],
                       cwd=tool.parent)
        m = BIND_LINE.search(text)
        classes = [c for c, _ in BIND_FIND.findall(text)]
        out[case] = {
            "exit": rc,
            "line": m.group(0) if m else None,
            "classes": sorted(set(classes)),
            "counts": tuple(int(x) for x in m.groups()[1:]) if m else None,
            "tail": text.strip().splitlines()[-3:],
        }
    return out


def expected_scope(obs: dict) -> list[str]:
    """Return the list of predicate violations present in obs ([] == conforming)."""
    bad = []
    for case, want_exit, want_finding in (
            ("clean", 0, None), ("label-missing", 1, "label"), ("label-wrong", 1, "label"),
            ("stray", 1, "stray"), ("ignored", 1, "ignored")):
        o = obs[case]
        if o["exit"] != want_exit:
            bad.append(f"{case}:exit={o['exit']}!={want_exit}")
        if want_finding and want_finding not in o["cases"]:
            bad.append(f"{case}:no-{want_finding}-finding")
        if o["findings"] is None:
            bad.append(f"{case}:no-verdict-line")
        elif want_finding is None and o["findings"] != 0:
            bad.append(f"{case}:findings={o['findings']}!=0")
    return bad


def expected_bind(obs: dict) -> list[str]:
    bad = []
    for case, want_exit, want_class in (
            ("clean", 0, None), ("unbound", 1, "unbound"), ("shifted", 1, "shifted"),
            ("stale", 1, "stale")):
        o = obs[case]
        if o["exit"] != want_exit:
            bad.append(f"{case}:exit={o['exit']}!={want_exit}")
        if want_class and want_class not in o["classes"]:
            bad.append(f"{case}:no-{want_class}-finding")
        if o["counts"] is None:
            bad.append(f"{case}:no-verdict-line")
    return bad


def gate_selftest(tool: Path) -> dict:
    rc, text = run([sys.executable, tool, "--selftest"], cwd=tool.parent, timeout=900)
    m = GATE_SELF.search(text)
    return {"exit": rc, "line": m.group(0) if m else None,
            "failed_list": (re.search(r"PRE_REPORT_SELFTEST_FAILED (\S+)", text) or [None, None])[1]
            if re.search(r"PRE_REPORT_SELFTEST_FAILED (\S+)", text) else None,
            "tail": text.strip().splitlines()[-6:]}


def gate_argv_probe(tool: Path, probe_dir: Path) -> dict:
    """Feed the gate a tools dir of argv-recording stubs and read back what it passed.

    The round-scope stub records its argv and prints a conforming verdict line. The
    gate must invoke it as `--round <N>` for the run to be a round-scope arm at all.
    """
    probe_dir.mkdir(parents=True, exist_ok=True)
    for name in ("round42-selfdesc-reconcile.py", "round69-newest-closure-counter.py",
                 "round68-receipt-pointer-audit.py"):
        (probe_dir / name).write_text("raise SystemExit(0)\n", encoding="utf-8")
    (probe_dir / "round67-worktree-landing-check.py").write_text(
        "raise SystemExit(0)\n", encoding="utf-8")
    (probe_dir / "probe-argv.txt").write_text("", encoding="utf-8")
    (probe_dir / "round72-round-scope.py").write_text(
        "import json, os, sys\n"
        "here = os.path.dirname(os.path.abspath(__file__))\n"
        "with open(os.path.join(here, 'probe-argv.txt'), 'a', encoding='utf-8') as fh:\n"
        "    fh.write(json.dumps(sys.argv[1:]) + chr(10))\n"
        "print('ROUND_SCOPE round=72 cases=3 findings=0')\n"
        "raise SystemExit(0)\n", encoding="utf-8")
    repo = FIX / "gate-probe" / "repo"
    if not (repo / ".git").exists():
        repo.mkdir(parents=True, exist_ok=True)
        run(["git", "init", "-q", "-b", "master", repo])
        (repo / "README.md").write_text("probe\n", encoding="utf-8")
        run(["git", "-C", repo, "add", "-A"])
        run(["git", "-C", repo, "-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
             "-c", "commit.gpgsign=false", "commit", "-q", "-m", "probe"])
    (probe_dir / "probe-argv.txt").write_text("", encoding="utf-8")
    rc, text = run([sys.executable, tool, "--repo", repo, "--round", 72, "--tip", "master",
                    "--tools-dir", probe_dir], cwd=tool.parent, timeout=300)
    calls = [ln for ln in (probe_dir / "probe-argv.txt").read_text(encoding="utf-8").splitlines()
             if ln.strip()]
    m = GATE_LINE.search(text)
    return {"exit": rc, "line": m.group(0) if m else None, "calls": calls,
            "tail": text.strip().splitlines()[-6:]}
