#!/usr/bin/env python3
"""Corrected V21 (lazy blockquote continuation) and V22 (row under a later '## Axes')
using a REAL ancestor revision R = the freeze commit, so the gate fact is not
confounded by a non-existent revision. cwd = fixture repo clone."""
import os
import pathlib
import subprocess
import sys

RECEIPTS = pathlib.Path(os.environ["RECEIPTS"])
R = "c07e1f909414aafb2d8de5605a81fd3bd4e3550e"  # real ancestor of every fixture commit
R85 = "PRE_REPORT round=85 arms=13 failed=1 uncommitted=0"
CMD85 = "`python3 tools/pre-report-gate.py --repo . --round 85 --tip master`"
AUTH85 = (f"**Current authority (round 85):** assigned axes are operability + calibration; "
          f"Latest measured round: 85. Terminal gate measured at `{R}`: {CMD85} printed `{R85}`, "
          f"exit0; receipt `.ufo/waves/round-85/measured/after/gate.out`.")
AUTH84 = (f"**Current authority (round 84):** assigned axes are operability + calibration; "
          f"Latest measured round: 84. Terminal gate measured at `{R}`: "
          f"`python3 tools/pre-report-gate.py --repo . --round 84 --tip master` printed "
          f"`PRE_REPORT round=84 arms=13 failed=0 uncommitted=0`, exit0; receipt "
          f"`.ufo/waves/round-84/measured/after/gate-final-green.out`.")
ROW85 = (f"| calibration | **7** | terminal `SELFRECORD_R85` at `{R}`; latest outside closure "
         f"`corpus/lessons/round-85-verifier-spotcheck.md` (round85 rejected-honest-stop; "
         f"round84 rejected-honest-stop) | score round1 |")
ROW84 = (f"| calibration | **7** | terminal `SELFRECORD_R84` at `{R}`; latest outside closure "
         f"`corpus/lessons/round-84-verifier-spotcheck.md` (round84 rejected-honest-stop) | score round1 |")
SUPPORT = {
    ".ufo/waves/round-85/measured/after/gate.out": R85 + "\n",
    ".ufo/waves/round-84/measured/after/gate-final-green.out": "PRE_REPORT round=84 arms=13 failed=0 uncommitted=0\n",
    "corpus/lessons/round-85-verifier-spotcheck.md": "# round 85\n\nVerdict: rejected-honest-stop.\n",
    "corpus/lessons/round-84-verifier-spotcheck.md": "# round 84\n\nVerdict: rejected-honest-stop.\n",
}


def run(cmd, **kw):
    return subprocess.run(cmd, text=True, capture_output=True, **kw)


def write(path, text):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def commit_and_grade(name, text):
    for path, body in SUPPORT.items():
        write(path, body)
    write("SCORECARD.md", text)
    top = run(["git", "rev-parse", "--show-toplevel"]).stdout.strip()
    assert top == os.getcwd(), f"toplevel guard failed {top!r}"
    run(["git", "add", "-A"])
    c = run(["git", "-c", "user.name=EX01", "-c", "user.email=ex01@scratch.invalid",
             "-c", "commit.gpgsign=false", "commit", "-q", "-m", f"fixture {name}"])
    assert c.returncode == 0, c.stderr
    sha = run(["git", "rev-parse", "HEAD"]).stdout.strip()
    anc = run(["git", "merge-base", "--is-ancestor", R, sha]).returncode
    g = run([sys.executable, "tools/round86-rendered-cells.py", "--repo", ".", "--rev", sha])
    (RECEIPTS / f"{name}.out").write_text(g.stdout)
    (RECEIPTS / f"{name}.err").write_text(g.stderr)
    (RECEIPTS / f"{name}.exit").write_text(str(g.returncode) + "\n")
    (RECEIPTS / f"{name}.sha").write_text(sha + f"\nR-is-ancestor-exit={anc}\n")
    print(f"== {name} rev={sha[:12]} R-ancestor-exit={anc} exit={g.returncode}")
    print(g.stdout.rstrip())
    if g.stderr:
        print("[stderr] " + g.stderr.rstrip())
    return g.returncode


def main():
    res = {}
    # V21 lazy continuation: the quote's paragraph has no blank line before the cells, so in
    # CommonMark 0.31.2 (4.1 / 5.1 paragraph continuation) the cells are quote text, not a
    # fence; the selector sees them at column 0.
    res["V21-lazy-blockquote-shadow-green-over-stale"] = commit_and_grade(
        "V21-lazy-blockquote-shadow-green-over-stale",
        "# fixture\n\n> quoted note on the round\n" + AUTH85 + "\n" + AUTH84 + "\n\n"
        "## Axes\n\n> quoted note on the calibration row\n" + ROW85 + "\n" + ROW84 + "\n")
    # V21 control: same layout, no quote; stale live cells remain stale -> must be red
    res["V21c-no-quote-control-stale"] = commit_and_grade(
        "V21c-no-quote-control-stale",
        "# fixture\n\n" + AUTH85 + "\n" + AUTH84 + "\n\n## Axes\n\n" + ROW85 + "\n" + ROW84 + "\n")
    # V22 a calibration row under a LATER '## Axes' while the first '## Axes' has none; the
    # live authority is correct (round 85). The frozen spec grades the first section only.
    res["V22-row-from-later-axes-section"] = commit_and_grade(
        "V22-row-from-later-axes-section",
        "# fixture\n\n" + AUTH85 + "\n\n## Axes\n\n| operability | **8** | x | y |\n\n"
        "## Retired\n\nnone\n\n## Axes\n\n" + ROW85 + "\n")
    # V22 control: first '## Axes' carries the stale row -> must be red
    res["V22c-first-axes-stale-control"] = commit_and_grade(
        "V22c-first-axes-stale-control",
        "# fixture\n\n" + AUTH85 + "\n\n## Axes\n\n" + ROW84 + "\n\n## Retired\n\nnone\n\n"
        "## Axes\n\n" + ROW85 + "\n")
    print("\n== summary ==")
    for k, v in res.items():
        print(f"{k}\texit={v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
