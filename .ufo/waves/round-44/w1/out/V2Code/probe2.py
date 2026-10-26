#!/usr/bin/env python3
"""probe2.py - absent-rule, vocabulary and axes-shape probes against the FROZEN
counter bytes with FLEET_REV/BASE/ROUNDS patched to synthetic fixtures
(reuses the syn-fleet/syn-lane repos built by harness.py; identity
r44-control@fixture.invalid inside /fast/scratch only)."""
import contextlib, importlib.util, io, os, subprocess, sys
S = "/fast/scratch/hyaku/kama-r44/V2Code"
AUD = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round44-verdict-ledger-audit.py"
F = os.path.join(S, "syn-fleet"); L = os.path.join(S, "syn-lane")
ID = ["-c", "user.name=r44-control", "-c", "user.email=r44-control@fixture.invalid"]
def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout.strip()
def commit(msg):
    subprocess.run(["git", "-C", L, "add", "-A"], check=True)
    git(L, *ID, "commit", "-qm", msg, "--allow-empty")
    return git(L, "rev-parse", "HEAD")
def put(repo, rel, text):
    p = os.path.join(repo, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(text)
spec = importlib.util.spec_from_file_location("c2", AUD)
c2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c2)
FR = git(F, "rev-parse", "HEAD"); BR = git(L, "rev-parse", "HEAD")
c2.FLEET_REV = FR; c2.BASE = BR; c2.ROUNDS = range(10, 15)
HDR = "round\ttrend\tside\tverdict\trepo\trev\tpath\tline\tnote"
FP = ".ufo/reports/round-{r}/kama.md"; LP = "corpus/lessons/round-{r}-verifier-spotcheck.md"
NOTE = "synthetic harness row for rule verification"
def row(r, t, side, v, ln, note=NOTE):
    if side == "self": repo, rev, path = "fleet", FR, FP.format(r=r)
    else: repo, rev, path = "lane", BR, LP.format(r=r)
    return "\t".join([str(r), t, side, v, repo, rev, path, str(ln), note])
AB = ("absent", "-")
rows = [
 row(10,"expansion","self","improved",2), row(10,"expansion","outside","unchanged",2),
 row(10,"quality","self","unprovable-but-better",3), row(10,"quality","outside","unprovable-but-better",3),
 row(10,"discernment","self","mixed",4), row(10,"discernment","outside","harmed",4),
 row(11,"expansion","self","unprovable",3), row(11,"expansion","outside","absent","-"),
 row(11,"quality","self","unchanged",2), row(11,"quality","outside","absent","-"),
 row(11,"discernment","self","absent","-"), row(11,"discernment","outside","absent","-"),
 row(12,"expansion","self","unprovable-but-better",2), row(12,"expansion","outside","unprovable",2),
 row(12,"quality","self","absent","-"), row(12,"quality","outside","absent","-"),
 row(12,"discernment","self","absent","-"), row(12,"discernment","outside","absent","-"),
 row(13,"expansion","self","absent","-"), row(13,"expansion","outside","absent","-"),
 row(13,"quality","self","unchanged",2), row(13,"quality","outside","unprovable-but-better",2),
 row(13,"discernment","self","absent","-"), row(13,"discernment","outside","absent","-"),
 row(14,"expansion","self","absent","-"), row(14,"expansion","outside","improved",2),
 row(14,"quality","self","absent","-"), row(14,"quality","outside","absent","-"),
 row(14,"discernment","self","absent","-"), row(14,"discernment","outside","absent","-"),
]
TABLE = ["| 10 | expansion | improved | unchanged | overclaim |", "| 10 | discernment | mixed | harmed | other |",
 "| 12 | expansion | unprovable-but-better | unprovable | overclaim |", "| 13 | quality | unchanged | unprovable-but-better | underclaim |"]
SUMMARY = "agreement=1/4 overclaim=2 underclaim=1 other=1 absent=10"
def scorecard(tbl=TABLE, summ=SUMMARY, axes=True, heading="### Round-44 calibration ledger", axrow=None):
    ax = (axrow if axrow is not None else
          ("| calibration | 7 | registry/verdict-ledger.tsv |\n" if axes else "| calibration | 7 | (none) |\n"))
    return "# Scorecard\n## Axes\n| axis | score | run |\n" + ax + "## Notes\n" + heading + "\n" + \
           "".join(x + "\n" for x in tbl) + (summ + "\n" if summ else "") + "## Next\n"
def run(label, lr, sc, expect=None):
    put(L, "registry/verdict-ledger.tsv", HDR + "\n" + "\n".join(lr) + "\n"); put(L, "SCORECARD.md", sc)
    tip = commit(label)
    out = io.StringIO(); err = io.StringIO(); old = sys.argv
    sys.argv = ["c2", "--repo", L, "--tip", tip, "--fleet", F]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = c2.main()
    finally:
        sys.argv = old
    txt = out.getvalue(); lines = txt.splitlines()
    print(f"[{label}] exit={rc}" + ("" if expect is None or rc == expect else f"  <<< EXPECTED {expect}"))
    print("    " + (lines[1] if len(lines) > 1 else "(none)"))
    for d in [x for x in lines if x.startswith("detail:")][:4]:
        print("    " + d)
    return rc
print("=== M5 fixed: outside absent row with note too short (index 7) ===")
bad = list(rows); bad[7] = row(11, "expansion", "outside", "absent", "-", "short")
run("m5fix", bad, scorecard(), expect=1)
print("=== M6 fixed: outside absent row with numeric line (index 7) ===")
bad = list(rows); bad[7] = row(11, "expansion", "outside", "absent", 1)
run("m6fix", bad, scorecard(), expect=1)
print("=== M18 verdict capitalization ('Improved') rejected ===")
bad = list(rows); bad[0] = row(10, "expansion", "self", "Improved", 2)
run("m18", bad, scorecard(), expect=1)
print("=== M19 exactly-20-char note accepted for absent ===")
bad = list(rows); bad[7] = row(11, "expansion", "outside", "absent", "-", "x" * 20)
run("m19", bad, scorecard(), expect=0)
print("=== M20 axes row in the real SCORECARD shape (bold score, long run cell) accepted ===")
real_ax = "| calibration | **7** | run `python3 tools/capability-repertoire-audit.py --selftest`; this table's counters; registry/verdict-ledger.tsv cited | score round 1 |\n"
run("m20", rows, scorecard(axrow=real_ax), expect=0)
