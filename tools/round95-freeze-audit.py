#!/usr/bin/env python3
"""round95-freeze-audit.py - round-95 C3 (calibration) frozen counter.

PREDICATE (frozen: plans/round-95-claims.md section C3):

    `python3 tools/round95-freeze-audit.py --repo . --rev <F>` prints
    `FREEZE_AUDIT receipts=<n> present=<n> missing=0 tokens=<m> matching=<m> met=True`
    and exits 0 at the freeze commit F, the counter's bytes identical to that commit.

Why (round-94 closure, lesson M5/M6):
- M5: `plans/round-94-claims.md` named 12 receipt paths under `.ufo/waves/round-94/`; only three
  existed at the freeze commit. Eleven were never committed at all, so every "control executed
  before the freeze" sentence in that plan was unfalsifiable from the repo.
- M6: the frozen predicate quoted a metric the counter never prints (`entry_points=<e>` did not
  exist in `round94-setter-sweep.py`), so the predicate sentence and the instrument's output
  diverged and the closure had to grade the mismatch by hand.

What this counter enforces, over the plan text at --rev:
1. Every repo-relative path the plan names under `.ufo/waves/round-95/` exists at that revision
   (`git cat-file -e <rev>:<path>`). Prose mentions are excluded: only backticked paths count.
2. Every backticked command line the plan freezes as a predicate
   (`python3 tools/<tool>.py ...`) names a tool that exists at that revision, and every
   `TOKEN=<...>` / `TOKEN=0` assignment in that same predicate line appears literally in the
   tool's committed bytes (docstring or code). A predicate naming a metric its instrument never
   prints is `token-missing`.
3. Every `S###` id the plan cites as sourcing a claim exists as a Registry row in the committed
   `corpus/SOURCES.md` at --rev, and that row's `status` is `mined` or `queued` (never `rejected`).

Counts printed: receipts (paths named), present, missing, tokens (assignments checked), matching.
Exit 0 only when missing == 0, token-missing == 0 and cited rows unresolvable == 0.
`--selftest` runs the same checks against a table of synthetic plans with known answers and
prints `FREEZE_AUDIT_SELFTEST pass=<n> fail=<n>`.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

PATH_RE = re.compile(r"`(\.ufo/waves/round-\d+/[A-Za-z0-9._/-]+)`")
REL_RE = re.compile(r"`((?:controls|measured|w\d)/[A-Za-z0-9._/-]+\.[A-Za-z0-9]+)`")
TOOL_RE = re.compile(r"`python3 (tools/[A-Za-z0-9._-]+\.py)([^`]*)`")
TOKEN_RE = re.compile(r"\b([a-z_]+)=<([a-z_>]+)>|\b([a-z_]+)=(\d+|True|False)\b")
SID_RE = re.compile(r"\bS(\d{3,})\b")
SRC_ROW_RE = re.compile(r"^ {0,3}\| *(S\d{3,}) *\|")


class Fail(Exception):
    pass


def show(repo: Path, rev: str, path: str):
    p = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def exists(repo: Path, rev: str, path: str) -> bool:
    return subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{rev}:{path}"],
                          capture_output=True).returncode == 0


def sources_status(repo: Path, rev: str):
    text = show(repo, rev, "corpus/SOURCES.md")
    if text is None:
        raise Fail("corpus/SOURCES.md absent")
    out = {}
    for line in text.split("\n"):
        m = SRC_ROW_RE.match(line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 11:
            out[m.group(1)] = cells[8]
    return out


def audit(plan_text: str, repo: Path, rev: str, src_status, wave_dir: str):
    named = []
    for m in PATH_RE.finditer(plan_text):
        p = m.group(1)
        if p not in named:
            named.append(p)
    # Plans name their receipts relative to the round wave dir (`controls/c1-base.out`); the
    # round-94 plan did that and 11 of 12 named receipts were never committed (lesson M5).
    for m in REL_RE.finditer(plan_text):
        p = f"{wave_dir}/{m.group(1)}"
        if p not in named:
            named.append(p)
    present, missing_paths = 0, []
    for p in named:
        if exists(repo, rev, p):
            present += 1
        else:
            missing_paths.append(p)

    tokens_checked, token_missing, tool_missing = 0, [], []
    # A frozen predicate is a plan LINE that names a tool: the sentence quotes the counter's
    # output line in the same breath (round-94 M6 was exactly that sentence naming a token the
    # counter never prints), so the tokens are read from the whole line, not from the command span.
    for line in plan_text.split("\n"):
        tools = list(TOOL_RE.finditer(line))
        if not tools:
            continue
        for m in tools:
            tool = m.group(1)
            blob = show(repo, rev, tool)
            if blob is None:
                tool_missing.append(tool)
                continue
            for tm in TOKEN_RE.finditer(line):
                name = tm.group(1) or tm.group(3)
                if name in ("python3", "tools", "work", "repo", "rev", "scratch"):
                    continue
                tokens_checked += 1
                if name not in blob:
                    token_missing.append(f"{tool}:{name}")
    cited, unresolvable = 0, []
    for m in SID_RE.finditer(plan_text):
        sid = "S" + m.group(1)
        cited += 1
        st = src_status.get(sid)
        if st is None:
            unresolvable.append(sid)
        elif st == "rejected":
            unresolvable.append(sid + ":rejected")
    return {
        "receipts": len(named), "present": present, "missing_paths": missing_paths,
        "tokens": tokens_checked, "token_missing": token_missing, "tool_missing": tool_missing,
        "cited": cited, "unresolvable": unresolvable,
    }


def selftest() -> int:
    plan_bad = """controls: `.ufo/waves/round-95/controls/nope.out` and `.ufo/waves/round-95/controls/ok.out`
predicate: `python3 tools/round95-freeze-audit.py --repo . --rev <F>` prints `FREEZE_AUDIT receipts=<n> present=<n> missing=0 ghost_token=0`
"""
    plan_good = """controls: `.ufo/waves/round-95/controls/ok.out`
predicate: `python3 tools/round95-freeze-audit.py --repo . --rev <F>` prints `FREEZE_AUDIT receipts=<n> present=<n> missing=0`
"""
    tmp = Path(tempfile.mkdtemp(prefix="r95-audit-selftest-"))
    try:
        repo = tmp / "repo"
        repo.mkdir()
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
        (repo / "tools").mkdir()
        (repo / "tools" / "round95-freeze-audit.py").write_text(
            "print('FREEZE_AUDIT receipts=1 present=1 missing=0')\n")
        (repo / ".ufo" / "waves" / "round-95" / "controls").mkdir(parents=True)
        (repo / ".ufo" / "waves" / "round-95" / "controls" / "ok.out").write_text("x\n")
        (repo / "corpus").mkdir()
        (repo / "corpus" / "SOURCES.md").write_text("| S001 | x | code | A | s | a | t | mined | 2026-01-01 | 90d | - |\n")
        subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t",
                        "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-qm", "seed"], check=True)
        st = sources_status(repo, "HEAD")
        r = audit(plan_bad, repo, "HEAD", st, ".ufo/waves/round-95")
        r2 = audit(plan_good, repo, "HEAD", st, ".ufo/waves/round-95")
        checks = [
            ("missing_path_detected", r["missing_paths"] == [".ufo/waves/round-95/controls/nope.out"]),
            ("present_counted", r["present"] == 1),
            ("ghost_token_detected", r["token_missing"] == ["tools/round95-freeze-audit.py:ghost_token"]),
            ("good_plan_clean", not r2["missing_paths"] and not r2["token_missing"]),
            ("good_plan_tokens", r2["tokens"] >= 3),
        ]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    fail = [n for n, ok in checks if not ok]
    print(f"FREEZE_AUDIT_SELFTEST pass={len(checks) - len(fail)} fail={len(fail)}")
    for n in fail:
        print(f"FREEZE_AUDIT_SELFTEST_FAIL {n}")
    return 0 if not fail else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path)
    ap.add_argument("--rev")
    ap.add_argument("--plan", default="plans/round-95-claims.md")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.repo or not a.rev:
        ap.error("--repo and --rev are required")
    try:
        plan = show(a.repo, a.rev, a.plan)
        if plan is None:
            raise Fail(f"{a.plan} absent at {a.rev}")
        st = sources_status(a.repo, a.rev)
    except Fail as e:
        print(f"FREEZE_AUDIT could-not-evaluate: {e}")
        return 2
    wave_dir = ".ufo/waves/round-" + (re.search(r"round-(\d+)", a.plan).group(1) if re.search(r"round-(\d+)", a.plan) else "95")
    r = audit(plan, a.repo, a.rev, st, wave_dir)
    for p in r["missing_paths"]:
        print(f"FREEZE_AUDIT_MISSING {p}")
    for t in r["tool_missing"]:
        print(f"FREEZE_AUDIT_TOOL_MISSING {t}")
    for t in r["token_missing"]:
        print(f"FREEZE_AUDIT_TOKEN_MISSING {t}")
    for s in r["unresolvable"]:
        print(f"FREEZE_AUDIT_SOURCE_UNRESOLVED {s}")
    met = not r["missing_paths"] and not r["token_missing"] and not r["tool_missing"] and not r["unresolvable"]
    print(f"FREEZE_AUDIT receipts={r['receipts']} present={r['present']} missing={len(r['missing_paths'])} "
          f"tokens={r['tokens']} matching={r['tokens'] - len(r['token_missing'])} "
          f"cited={r['cited']} unresolved={len(r['unresolvable'])} met={met}")
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
