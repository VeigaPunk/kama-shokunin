#!/usr/bin/env python3
"""MT01Mutants fixture builder: a GREEN C1 tree (round-42 reconciler met=True).

Fixture-only. Edits SCORECARD.md/PROVINCE.md to the recorded repair shape, applies
the reference run-fact harness repair (checkout at tip instead of a metadata-free
git-archive export) to tools/round41-scorecard-reconcile.py, commits in a clone.
"""
import os
import subprocess
import sys
import shutil

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
BASE = "0e14facd0c619f45a6461821d2bd80ddac9855b1"
S = "/fast/scratch/hyaku/kama-r70/MT01Mutants"
MODE = sys.argv[1] if len(sys.argv) > 1 else "nofact"
FX = os.path.join(S, "fixture-gl" if MODE == "nofact" else "fixture-coupling")
IDENT = ["-c", "user.name=mt01fixture", "-c", "user.email=mt01@fixture.invalid"]


def sh(*a, **kw):
    p = subprocess.run(a, capture_output=True, text=True, **kw)
    if p.returncode != 0:
        raise SystemExit(f"FAILED {a}: {p.stderr}")
    return p.stdout


def edit(path, pairs):
    t = open(path).read()
    for old, new in pairs:
        if t.count(old) != 1:
            raise SystemExit(f"{path}: expected exactly 1 occurrence of {old[:60]!r}, got {t.count(old)}")
        t = t.replace(old, new)
    open(path, "w").write(t)


def main():
    if os.path.exists(FX):
        shutil.rmtree(FX)
    sh("git", "clone", "-q", "--shared", LANE, FX)
    top = sh("git", "-C", FX, "rev-parse", "--show-toplevel").strip()
    if os.path.realpath(top) != os.path.realpath(FX):
        raise SystemExit(f"fixture toplevel is {top}, not {FX}")
    sh("git", "-C", FX, "checkout", "-q", "--detach", BASE)

    # --- self-description repair (fixture content) ---
    cal = [l for l in open(os.path.join(FX, "SCORECARD.md")).read().split("\n")
           if l.startswith("| calibration | **7**")]
    if len(cal) != 1:
        raise SystemExit("expected one calibration row")
    sc_edits = [
        # head Planned pointer: maxN becomes 70, so the live plan is round 71
        ("The live plan is `### Planned (round 65)` below (§Round 64)",
         "The live plan is `### Planned (round 71)` below (§Round 70)"),
        # retired: canon has 15 capability rows
        ("None. 6 axes and 13 capabilities remain active.",
         "None. 6 axes and 15 capabilities remain active."),
        # closure pointer: newest spotcheck at tip is round-69
        ("latest outside closure `corpus/lessons/round-68-verifier-spotcheck.md`",
         "latest outside closure `corpus/lessons/round-69-verifier-spotcheck.md`"),
        ("scores held), including round 68",
         "scores held), including round 69"),
    ]
    edit(os.path.join(FX, "SCORECARD.md"), sc_edits)

    # head-scoped banner repair: only the text before the first "## " line
    scp = os.path.join(FX, "SCORECARD.md")
    sc = open(scp).read()
    head, sep, rest = sc.partition("\n## ")
    if head.count("Latest measured round: 68") != 1:
        raise SystemExit("head banner: expected one 'Latest measured round: 68'")
    head = head.replace("Latest measured round: 68, closed",
                        "Latest measured round: 70, with round 69 closed")
    sc = head + sep + rest
    # the calibration row's newest-closure fact cites an elided marker ("..."),
    # which exact-line matching can never satisfy; fixture form: count the marker
    old_fact = ("run `python3 tools/round69-newest-closure-counter.py --since-round 63` "
                "\u2192 `NEWEST_CLOSURE \u2026 row_current=true`")
    # NB: the fact command must not contain "|" - axes_table splits cells on "|"
    # and a pipe silently truncates the evidence cell.
    new_fact = ("run `python3 tools/round69-newest-closure-counter.py --since-round 63` "
                "\u2192 `NEWEST_CLOSURE newest=corpus/lessons/round-69-verifier-spotcheck.md "
                "date=2026-11-01 round=69 "
                "row_names=corpus/lessons/round-69-verifier-spotcheck.md row_current=true`")
    if sc.count(old_fact) != 1:
        raise SystemExit("round69 fact: not found exactly once")
    if MODE == "nofact":
        # The fact's truth is a function of the very calibration row the selftest
        # plants: planting a stale pointer makes the fact fail too (+2 per planted
        # arm), which breaks the selftest's exactly-one-mismatch assertion. The
        # selftest-green fixture drops the fact and keeps the row-independent ones.
        sc = sc.replace("; " + old_fact, "")
    else:
        sc = sc.replace(old_fact, new_fact)
    open(scp, "w").write(sc)

    with open(os.path.join(FX, "SCORECARD.md"), "a") as f:
        f.write("\n## Round 70 — fixture round (2030-01-01)\n\n"
                "Scratch fixture only: this section exists so maxN derives to 70.\n\n"
                "### Planned (round 71)\n\n"
                "1. Append the next measured round here.\n")

    with open(os.path.join(FX, "PROVINCE.md"), "a") as f:
        f.write("\n**Round-70 capability instruments (fixture registration):** "
                "`tools/round67-worktree-landing-check.py`, "
                "`tools/round68-receipt-pointer-audit.py`, "
                "`registry/receipt-pointer-resolutions.tsv`, "
                "`tools/round69-newest-closure-counter.py`.\n")

    # re-anchor the coverage row to the edited PROVINCE.md (sha256 + line count)
    import hashlib
    pv = open(os.path.join(FX, "PROVINCE.md"), "rb").read()
    new_sha = hashlib.sha256(pv).hexdigest()
    new_lines = pv.count(b"\n")
    sc2 = open(scp).read()
    old_anchor = ("surface list `PROVINCE.md` sha256 "
                  "`f0aaae9ccfd0ecb6641ad1646934f4ff5555fcc45d2e397670b2eb5ff083e8a6` (270 lines")
    new_anchor = f"surface list `PROVINCE.md` sha256 `{new_sha}` ({new_lines} lines"
    if sc2.count(old_anchor) != 1:
        raise SystemExit("coverage PROVINCE anchor: not found exactly once")
    open(scp, "w").write(sc2.replace(old_anchor, new_anchor))
    print(f"PROVINCE re-anchor: sha256={new_sha} lines={new_lines}")

    # --- reference run-fact harness repair (round-70 shape) ---
    r41 = os.path.join(FX, "tools", "round41-scorecard-reconcile.py")
    edit(r41, [(
        '                arc = git(repo, "archive", "--format=tar", tip, binary=True)\n'
        '                subprocess.run(["tar", "-x", "-C", export], input=arc, check=True)\n',
        '                subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout",\n'
        '                                repo, export], check=True)\n'
        '                subprocess.run(["git", "-C", export, "checkout", "-q", "--detach", tip],\n'
        '                               check=True)\n')])

    sh("git", "-C", FX, "add", "-A")
    sh("git", "-C", FX, *IDENT, "commit", "-q", "-m", "fixture: round-70 green C1 tree + reference harness repair")
    rev = sh("git", "-C", FX, "rev-parse", "HEAD").strip()
    # the reference harness clones this repo again; a detached HEAD would give
    # the nested clone no local master and defeat gate-registry-check's lane-tip arm
    sh("git", "-C", FX, "branch", "-f", "master", rev)
    sh("git", "-C", FX, "checkout", "-q", "master")
    print(rev)
    print(sh("git", "-C", FX, "status", "--porcelain") or "(clean)")
    print(sh("git", "-C", FX, "rev-parse", "--show-toplevel").strip())


if __name__ == "__main__":
    main()
