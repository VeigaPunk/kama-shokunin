#!/usr/bin/env python3
"""Round-71 live experiment for CRT01ReceiptAttack.

Clones the lane (shared, into S), checks out the defect-4 tip 7fb6cb4e, and neutralises only the
record's *non-receipt* citations (control .py scripts, seat .md reports, .tsv tables) by removing
the backticks around them, so the frozen C2 tool can reach the receipt grading instead of aborting
with RECEIPT_TIP_BINDING_UNREADABLE.  Nothing else is changed; the commit is made in the clone with
the fixture identity.  Then runs the frozen counting command against the clone.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r72/CRT01ReceiptAttack")
CLONE = S / "lane-clone"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
TOOL = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round72-receipt-tip-binding.py"
RECEIPT_EXTS = (".out", ".txt", ".log", ".json")
GITID = ["-c", "user.name=fixture", "-c", "user.email=fixture@invalid", "-c", "commit.gpgsign=false"]
TOKEN = re.compile(r"`([^`\n]+)`")
HEAD = re.compile(r"^##\s+Round[-\s]+#?(\d+)\b")


def sh(argv, cwd=None):
    return subprocess.run(argv, cwd=None if cwd is None else str(cwd), capture_output=True, text=True)


def git(*args, check=True):
    r = sh(["git", "-C", str(CLONE), *GITID, *args])
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} -> {r.returncode}\n{r.stdout}{r.stderr}")
    return r


def strip_section(text: str, round_no: int = 71) -> tuple[str, list[str]]:
    lines = text.splitlines(keepends=True)
    inside = False
    out, dropped = [], []
    for line in lines:
        if line.startswith("## "):
            m = HEAD.match(line)
            inside = bool(m and int(m.group(1)) == round_no)
        if not inside:
            out.append(line)
            continue

        def repl(match):
            tok = match.group(1)
            tail = tok.rsplit("/", 1)[-1]
            ext = ("." + tail.rsplit(".", 1)[-1].lower()) if "." in tail else ""
            if ext in RECEIPT_EXTS or not ("/" in tok or ext in (".py", ".md", ".tsv", ".sh", ".html")):
                return match.group(0)
            dropped.append(tok)
            return tok  # same text, no backticks
        out.append(TOKEN.sub(repl, line))
    return "".join(out), dropped


def main() -> int:
    S.mkdir(parents=True, exist_ok=True)
    if CLONE.exists():
        sh(["rm", "-rf", str(CLONE)])
    r = sh(["git", "clone", "--shared", "--quiet", LANE, str(CLONE)])
    if r.returncode != 0:
        raise SystemExit(f"clone failed: {r.stderr}")
    top = Path(git("rev-parse", "--show-toplevel").stdout.strip()).resolve()
    assert top == CLONE.resolve(), f"toplevel {top} != {CLONE}"
    git("checkout", "--quiet", "7fb6cb4e")

    sc = CLONE / "SCORECARD.md"
    text, dropped_sc = strip_section(sc.read_text(encoding="utf-8"))
    sc.write_text(text, encoding="utf-8")

    lesson = CLONE / "corpus/lessons/round-71.md"
    ltext, dropped_lesson = strip_section(lesson.read_text(encoding="utf-8"), round_no=_noop()) \
        if False else (lesson.read_text(encoding="utf-8"), [])
    # the lesson is graded whole: neutralise every non-receipt backticked token in it
    def repl_all(match):
        tok = match.group(1)
        tail = tok.rsplit("/", 1)[-1]
        ext = ("." + tail.rsplit(".", 1)[-1].lower()) if "." in tail else ""
        if ext in RECEIPT_EXTS:
            return match.group(0)
        if ext in (".py", ".md", ".tsv", ".sh", ".html"):
            dropped_lesson.append(tok)
            return tok
        return match.group(0)
    lesson.write_text(TOKEN.sub(repl_all, ltext), encoding="utf-8")

    git("add", "-A")
    git("commit", "--quiet", "-m", "r71 record with non-receipt citations neutralised (attack fixture)")
    tip = git("rev-parse", "HEAD").stdout.strip()

    run = sh([sys.executable, TOOL, "--repo", str(CLONE), "--round", "71", "--tip", tip])
    print("neutralised (SCORECARD §71):", len(dropped_sc), "tokens")
    for t in dropped_sc:
        print("   -", t)
    print("neutralised (lesson):", len(dropped_lesson), "tokens")
    for t in dropped_lesson:
        print("   -", t)
    print("fixture tip:", tip)
    print("--- tool stdout ---")
    print(run.stdout)
    print("--- tool stderr ---")
    print(run.stderr)
    print("exit:", run.returncode)
    return 0


def _noop():
    return 0


if __name__ == "__main__":
    sys.exit(main())
