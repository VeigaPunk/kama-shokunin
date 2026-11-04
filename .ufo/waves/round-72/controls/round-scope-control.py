#!/usr/bin/env python3
"""round-scope-control.py - round-72 C1 control (frozen; plans/round-72-claims.md section C1).

Scores the BASE state with the frozen C1 counter's target: build the three defect fixtures the
claim names (missing round prompt, one uncommitted path outside the wave dir, one git-ignored
path inside the wave dir), run the base pre-report gate's cleanliness-arm command on each, and
report how many the base state catches.

    python3 .ufo/waves/round-72/controls/round-scope-control.py --work DIR [--base-rev REV]

Output: `SCOPE_CONTROL cases=3 base_green=<g> killed=<k>` and one `SCOPE_FIXTURE <case> base=<...>`
line per fixture. Exit 0 when the base state already kills at least one case (the claim would be
wrong about the base), exit 1 when all three are vacuous green under the base bytes (the claim's
before-state), exit 2 when a fixture cannot be built.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ARM_ARGV = ["git", "status", "--porcelain", "-uall", "--", ".ufo/waves/round-72"]
WHOLE_ARGV = ["git", "status", "--porcelain", "-uall"]
WAVE_PATHS = {
    "SCORECARD.md": "# scorecard\n\n## Axes\n\n| axis | score |\n|---|---|\n| calibration | 7 |\n",
    "LOG.md": "# log\n",
    "SKILL.md": "# skill\n",
    "PROVINCE.md": "# province\n",
    "corpus/SOURCES.md": "# sources\n",
    ".gitignore": ".ufo/waves/round-72/*.log\n",
    ".ufo/prompts/kama-round-72.md": "# prompt\n",
    ".ufo/waves/round-72/evidence.txt": "committed evidence\n",
}
EXPECTED = {"prompt": "skip-prompt", "stray": "skip-whole-repo", "ignored": "skip-ignored"}


def run(argv, cwd):
    return subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True)


def fixture(work: Path, case: str) -> Path:
    root = work / case
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    for rel, body in WAVE_PATHS.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    if case == "prompt":
        (root / ".ufo/prompts/kama-round-72.md").unlink()
    run(["git", "init", "-q"], root)
    run(["git", "-C", str(root), "config", "user.name", "control"], root)
    run(["git", "-C", str(root), "config", "user.email", "control@invalid"], root)
    if run(["git", "-C", str(root), "rev-parse", "--show-toplevel"], root).stdout.strip() != str(root):
        raise SystemExit(f"fixture toplevel mismatch at {root}")
    if run(["git", "-C", str(root), "add", "-A"], root).returncode != 0:
        raise SystemExit(f"git add failed at {root}")
    if run(["git", "-C", str(root), "commit", "-qm", "fixture"], root).returncode != 0:
        raise SystemExit(f"git commit failed at {root}")
    if case == "stray":
        (root / "stray-note.md").write_text("uncommitted round work outside the wave dir\n",
                                            encoding="utf-8")
    if case == "ignored":
        (root / ".ufo/waves/round-72/scratch.log").write_text("ignored evidence\n", encoding="utf-8")
    return root


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=None, help="scratch dir (default: TMPDIR)")
    ap.add_argument("--base-rev", default="d30a8696", help="revision this control describes")
    args = ap.parse_args(argv)
    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="r72-scope-control-"))
    work.mkdir(parents=True, exist_ok=True)
    green = killed = 0
    try:
        for case in ("prompt", "stray", "ignored"):
            try:
                root = fixture(work, case)
            except SystemExit as exc:
                print(f"SCOPE_CONTROL_UNEVALUABLE {exc}")
                return 2
            arm = run(ARM_ARGV, root)
            if arm.returncode != 0:
                print(f"SCOPE_CONTROL_UNEVALUABLE case={case} git exit={arm.returncode} "
                      f"{arm.stderr.strip()[:160]}")
                return 2
            records = [ln for ln in arm.stdout.splitlines() if ln.strip()]
            whole = run(WHOLE_ARGV, root)
            whole_records = [ln for ln in whole.stdout.splitlines() if ln.strip()]
            if records:
                killed += 1
                print(f"SCOPE_FIXTURE {case} base=caught arm_records={len(records)} "
                      f"whole_records={len(whole_records)}")
            else:
                green += 1
                print(f"SCOPE_FIXTURE {case} base=vacuous-green arm_records=0 "
                      f"whole_records={len(whole_records)}")
    finally:
        if args.work is None:
            shutil.rmtree(work, ignore_errors=True)
    print(f"SCOPE_CONTROL base_rev={args.base_rev} cases=3 base_green={green} killed={killed}")
    return 1 if green == 3 else 0


if __name__ == "__main__":
    sys.exit(main())
