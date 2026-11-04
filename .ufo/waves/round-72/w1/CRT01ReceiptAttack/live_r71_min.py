#!/usr/bin/env python3
"""Minimal r71 defect-4 experiment: real history, real receipt bytes, one citation.

Second clone of the lane at 7fb6cb4e.  The round-71 self-record is replaced by one line each in
SCORECARD §Round 71 and corpus/lessons/round-71.md that cites the motivating receipt
`measured/after/pre-report-at-tip.out`.  The receipt itself is the lane's committed blob, header
`# tip=4b284653...`, and the new tip is 4b284653..tip record-only.  Then the frozen counting
command runs against it.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r72/CRT01ReceiptAttack")
CLONE = S / "lane-clone-min"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
TOOL = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round72-receipt-tip-binding.py"
GITID = ["-c", "user.name=fixture", "-c", "user.email=fixture@invalid", "-c", "commit.gpgsign=false"]


def sh(argv):
    return subprocess.run(argv, capture_output=True, text=True)


def git(*args, check=True):
    r = sh(["git", "-C", str(CLONE), *GITID, *args])
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} -> {r.returncode}\n{r.stdout}{r.stderr}")
    return r


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

    # keep only the one citation in the round-71 section; everything else in the file is untouched
    sc = CLONE / "SCORECARD.md"
    lines = sc.read_text(encoding="utf-8").splitlines(keepends=True)
    start = next(i for i, ln in enumerate(lines) if ln.startswith("## Round 71"))
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    lines[start + 1:end] = [
        "\nC1 counter: `measured/after/pre-report-at-tip.out`.\n\n"]
    sc.write_text("".join(lines), encoding="utf-8")

    lesson = CLONE / "corpus/lessons/round-71.md"
    lesson.write_text("# Round 71 lesson (minimal fixture)\n\n"
                      "Receipt: `.ufo/waves/round-71/measured/after/pre-report-at-tip.out`\n",
                      encoding="utf-8")

    git("add", "-A")
    git("commit", "--quiet", "-m", "r71 minimal record citing the motivating receipt (attack fixture)")
    tip = git("rev-parse", "HEAD").stdout.strip()
    header = git("show", "7fb6cb4e:.ufo/waves/round-71/measured/after/pre-report-at-tip.out").stdout.splitlines()[0]
    delta = git("diff", "--name-only", "4b284653", tip).stdout.strip()
    anc = sh(["git", "-C", str(CLONE), "merge-base", "--is-ancestor", "4b284653", tip]).returncode

    run = sh([sys.executable, TOOL, "--repo", str(CLONE), "--round", "71", "--tip", tip])
    print("receipt header line:", header)
    print("merge-base --is-ancestor 4b284653 <tip> ->", anc)
    print("delta 4b284653..<tip> paths:")
    for p in delta.splitlines():
        print("   ", p)
    print("--- tool stdout ---")
    print(run.stdout)
    print("--- tool stderr ---")
    print(run.stderr)
    print("exit:", run.returncode)
    return 0


if __name__ == "__main__":
    sys.exit(main())
