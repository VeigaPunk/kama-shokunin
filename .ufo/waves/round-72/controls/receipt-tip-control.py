#!/usr/bin/env python3
"""receipt-tip-control.py - round-72 C2 control (frozen; plans/round-72-claims.md section C2).

Scores the shortcut the round-71 practice used with the frozen C2 counter's target: count the
receipt paths a round's self-record cites and accept when the count is non-zero. Three planted
defect fixtures (unbound receipt, shifted receipt whose delta touches tools/, stale receipt absent
at the tip) are each accepted by that shortcut, so the shortcut cannot satisfy the target.

    python3 .ufo/waves/round-72/controls/receipt-tip-control.py --work DIR

Output: `BINDING_CONTROL cited=3 accepted=3 rejected=0` and one `BINDING_FIXTURE <class> ...` line.
Exit 1 when the shortcut accepts all three (the claim's before-state), exit 0 when it rejects one
(the shortcut would already meet the target and the claim is wrong), 2 on an unbuildable fixture.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CITE_RE = re.compile(r"\.ufo/waves/round-72/[A-Za-z0-9._/-]+\.out")
FIXTURES = ("unbound", "shifted", "stale")


def run(argv, cwd):
    return subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True)


def build(work: Path, case: str) -> Path:
    root = work / case
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    (root / "tools").mkdir()
    (root / "corpus/lessons").mkdir(parents=True)
    (root / "corpus/lessons").mkdir(exist_ok=True)
    (root / "tools/probe.py").write_text("print('instrument v1')\n", encoding="utf-8")
    run(["git", "init", "-q"], root)
    run(["git", "-C", str(root), "config", "user.name", "control"], root)
    run(["git", "-C", str(root), "config", "user.email", "control@invalid"], root)
    receipt = root / ".ufo/waves/round-72/measured/a.out"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text("RESULT pass=1\n", encoding="utf-8")
    (root / "corpus/lessons/round-72.md").write_text(
        "receipt `.ufo/waves/round-72/measured/a.out`\n", encoding="utf-8")
    run(["git", "-C", str(root), "add", "-A"], root)
    run(["git", "-C", str(root), "commit", "-qm", "base"], root)
    first = run(["git", "-C", str(root), "rev-parse", "HEAD"], root).stdout.strip()
    if case == "stale":
        run(["git", "-C", str(root), "rm", "-q", "--cached", ".ufo/waves/round-72/measured/a.out"], root)
        receipt.unlink()
        run(["git", "-C", str(root), "commit", "-qm", "drop receipt"], root)
    if case in ("shifted", "unbound"):
        receipt.write_text("RESULT pass=1\n", encoding="utf-8")
        if case == "shifted":
            receipt.write_text(f"# tip={first}\nRESULT pass=1\n", encoding="utf-8")
            (root / "tools/probe.py").write_text("print('instrument v2')\n", encoding="utf-8")
        run(["git", "-C", str(root), "add", "-A"], root)
        run(["git", "-C", str(root), "commit", "-qm", "land"], root)
    return root


def shortcut(root: Path) -> tuple[int, list[str]]:
    text = (root / "corpus/lessons/round-72.md").read_text(encoding="utf-8")
    cited = sorted(set(CITE_RE.findall(text)))
    return len(cited), cited


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=None)
    args = ap.parse_args(argv)
    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="r72-binding-control-"))
    work.mkdir(parents=True, exist_ok=True)
    accepted = rejected = 0
    try:
        for case in FIXTURES:
            try:
                root = build(work, case)
            except (OSError, subprocess.SubprocessError) as exc:
                print(f"BINDING_CONTROL_UNEVALUABLE case={case} {exc}")
                return 2
            count, cited = shortcut(root)
            if count > 0:
                accepted += 1
                print(f"BINDING_FIXTURE {case} shortcut=accepted cited={count} {cited[0] if cited else '-'}")
            else:
                rejected += 1
                print(f"BINDING_FIXTURE {case} shortcut=rejected cited=0")
    finally:
        if args.work is None:
            shutil.rmtree(work, ignore_errors=True)
    print(f"BINDING_CONTROL cited=3 accepted={accepted} rejected={rejected}")
    return 1 if rejected == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
