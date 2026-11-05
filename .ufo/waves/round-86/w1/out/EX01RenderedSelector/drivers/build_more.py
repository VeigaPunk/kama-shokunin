#!/usr/bin/env python3
"""Second-wave fixtures: lazy blockquote continuation (V21), a calibration row
under a second '## Axes' section while the first has none (V22), and the coupled
gate fact's 'receipt bytes at R' clause (V23a/V23b). cwd = fixture repo clone."""
import os
import pathlib
import subprocess
import sys

RECEIPTS = pathlib.Path(os.environ["RECEIPTS"])
R85 = "PRE_REPORT round=85 arms=13 failed=1 uncommitted=0"
GREEN85 = "PRE_REPORT round=85 arms=13 failed=0 uncommitted=0"
CMD85 = "`python3 tools/pre-report-gate.py --repo . --round 85 --tip master`"
CLOSE85 = "`corpus/lessons/round-85-verifier-spotcheck.md`"
CLOSE84 = "`corpus/lessons/round-84-verifier-spotcheck.md`"
AUTH84 = "**Current authority (round 84):** Latest measured round: 84. Terminal gate measured at `{rev}`: `python3 tools/pre-report-gate.py --repo . --round 84 --tip master` printed `PRE_REPORT round=84 arms=13 failed=0 uncommitted=0`, exit0; receipt `.ufo/waves/round-84/measured/after/gate-final-green.out`."
AUTH85 = "**Current authority (round 85):** Latest measured round: 85. Terminal gate measured at `{rev}`: {cmd} printed `{tok}`, exit0; receipt `.ufo/waves/round-85/measured/after/gate.out`."
ROW_LIVE_STALE = "| calibration | **7** | terminal `SELFRECORD_R84` at `{rev}`; latest outside closure " + CLOSE84 + " (round84 rejected-honest-stop) | score round1 |"
ROW_GOOD = "| calibration | **7** | terminal `SELFRECORD_R85` at `{rev}`; latest outside closure " + CLOSE85 + " (round85 rejected-honest-stop; round84 rejected-honest-stop) | score round1 |"
SUPPORT85 = {
    ".ufo/waves/round-85/measured/after/gate.out": R85 + "\n",
    ".ufo/waves/round-84/measured/after/gate-final-green.out": "PRE_REPORT round=84 arms=13 failed=0 uncommitted=0\n",
    "corpus/lessons/round-85-verifier-spotcheck.md": "# round 85\n\nVerdict: rejected-honest-stop.\n",
    "corpus/lessons/round-84-verifier-spotcheck.md": "# round 84\n\nVerdict: rejected-honest-stop.\n",
}


def run(cmd, **kw):
    return subprocess.run(cmd, text=True, capture_output=True, **kw)


def commit(msg):
    top = run(["git", "rev-parse", "--show-toplevel"]).stdout.strip()
    assert top == os.getcwd(), f"toplevel guard failed {top!r}"
    run(["git", "add", "-A"])
    c = run(["git", "-c", "user.name=EX01", "-c", "user.email=ex01@scratch.invalid",
             "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg])
    assert c.returncode == 0, c.stderr
    return run(["git", "rev-parse", "HEAD"]).stdout.strip()


def grade(name, sha):
    g = run([sys.executable, "tools/round86-rendered-cells.py", "--repo", ".", "--rev", sha])
    (RECEIPTS / f"{name}.out").write_text(g.stdout)
    (RECEIPTS / f"{name}.err").write_text(g.stderr)
    (RECEIPTS / f"{name}.exit").write_text(str(g.returncode) + "\n")
    (RECEIPTS / f"{name}.sha").write_text(sha + "\n")
    print(f"== {name} rev={sha[:12]} exit={g.returncode}")
    print(g.stdout.rstrip())
    if g.stderr:
        print("[stderr] " + g.stderr.rstrip())
    return g.returncode


def write(path, text):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def supports():
    for path, text in SUPPORT85.items():
        write(path, text)


def main():
    results = {}
    # V21 lazy continuation: a block quote paragraph whose next line lacks '>' is a
    # lazy continuation of the quote in CommonMark; the stale cell sits there at col 0.
    supports()
    body = ("# fixture\n\n> quoted note about the round\n"
            + AUTH85.format(rev="c" * 40, cmd=CMD85, tok=R85) + "\n\n## Axes\n\n"
            + ROW_GOOD.format(rev="c" * 40) + "\n")
    # keep the live stale head AFTER the lazy shadow: the first col-0 cell is the shadow
    body = ("# fixture\n\n> quoted note about the round\n"
            + AUTH85.format(rev="c" * 40, cmd=CMD85, tok=R85) + "\n\n"
            + AUTH84.format(rev="c" * 40) + "\n\n## Axes\n\n"
            + ROW_LIVE_STALE.format(rev="c" * 40) + "\n")
    write("SCORECARD.md", body)
    sha = commit("fixture V21 lazy blockquote continuation")
    results["V21-lazy-blockquote"] = grade("V21-lazy-blockquote", sha)

    # V22 second '## Axes': the first Axes section carries no calibration row; a
    # later '## Axes' section (outside any fence) carries the newest-naming row.
    body = ("# fixture\n\n" + AUTH84.format(rev="c" * 40) + "\n\n## Axes\n\n"
            "| operability | **8** | x | y |\n\n## Retired\n\nnone\n\n## Axes\n\n"
            + ROW_GOOD.format(rev="c" * 40) + "\n")
    write("SCORECARD.md", body)
    sha = commit("fixture V22 second Axes section supplies the row")
    results["V22-second-axes-row"] = grade("V22-second-axes-row", sha)

    # V23a: the coupled gate fact reads the receipt at R. commit A: receipt lacks the
    # token; commit B (tip): the same path gains it. Cell names A.
    supports()
    write(".ufo/waves/round-85/measured/after/gate.out", "PRE_REPORT_ARM selfdesc exit=0 ok\n")
    body_a = "# fixture\n\n" + AUTH85.format(rev="PLACEHOLDER", cmd=CMD85, tok=R85) + "\n\n## Axes\n\n" + ROW_GOOD.format(rev="PLACEHOLDER") + "\n"
    write("SCORECARD.md", body_a)
    sha_a = commit("fixture V23 commit A: receipt without token")
    body_a = body_a.replace("PLACEHOLDER", sha_a)
    write("SCORECARD.md", body_a)
    sha_a = commit("fixture V23 commit A cell names A")
    # commit B: receipt at the same path gains the exact token, SCORECARD unchanged
    write(".ufo/waves/round-85/measured/after/gate.out", R85 + "\n")
    sha_b = commit("fixture V23 commit B: receipt gains token at tip")
    results["V23a-receipt-token-only-at-tip"] = grade("V23a-receipt-token-only-at-tip", sha_b)

    # V23b control: same cell, receipt carries the token at A too -> must be green
    write(".ufo/waves/round-85/measured/after/gate.out", R85 + "\n")
    body_c = "# fixture\n\n" + AUTH85.format(rev="PLACEHOLDER", cmd=CMD85, tok=R85) + "\n\n## Axes\n\n" + ROW_GOOD.format(rev="PLACEHOLDER") + "\n"
    write("SCORECARD.md", body_c)
    sha_c0 = commit("fixture V23b control commit with token at A")
    body_c = body_c.replace("PLACEHOLDER", sha_c0)
    write("SCORECARD.md", body_c)
    sha_c = commit("fixture V23b control cell names A")
    results["V23b-control-token-at-A"] = grade("V23b-control-token-at-A", sha_c)

    print("\n== summary ==")
    for k, v in results.items():
        print(f"{k}\texit={v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
