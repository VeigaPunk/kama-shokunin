#!/usr/bin/env python3
"""Rule-by-rule verification of the FROZEN counter bytes
(lane tools/round44-verdict-ledger-audit.py, sha256 1933e75b...) with module
constants FLEET_REV/BASE/ROUNDS patched to synthetic fixture repos, so every
branch (met=True, each invalid reason, table/summary/axes legs, exit codes)
is exercised on controlled data. Fixture commits use identity
r44-control@fixture.invalid inside /fast/scratch only."""
import contextlib, importlib.util, io, os, shutil, subprocess, sys

S = "/fast/scratch/hyaku/kama-r44/V2Code"
AUD = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round44-verdict-ledger-audit.py"
F = os.path.join(S, "syn-fleet")   # fixture fleet repo (self side)
L = os.path.join(S, "syn-lane")    # fixture lane repo (outside side + ledger + scorecard)
ID = ["-c", "user.name=r44-control", "-c", "user.email=r44-control@fixture.invalid"]

def git(repo, *a, check=True):
    p = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise SystemExit(f"git failed: {a}: {p.stderr}")
    return p.stdout.strip()

def init(path):
    shutil.rmtree(path, ignore_errors=True)
    subprocess.run(["git", "init", "-q", path], check=True)
    top = git(path, "rev-parse", "--show-toplevel")
    assert os.path.realpath(top) == os.path.realpath(path), top
    return path

def commit(repo, msg):
    subprocess.run(["git", "-C", repo, "add", "-A"], check=True)
    git(repo, *ID, "commit", "-qm", msg, "--allow-empty")
    return git(repo, "rev-parse", "HEAD")

def put(repo, rel, text):
    p = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(text)

init(F); init(L)
# --- synthetic side files -------------------------------------------------
fleet = {
 10: ["# Round 10", "expansion: improved", "quality: unprovable but better", "discernment: improved harmed"],
 11: ["# Round 11", "quality: unchanged", "expansion: unprovable", "discernment: nothing"],
 12: ["# Round 12", "expansion: unprovable-but-better"],
 13: ["# Round 13", "quality: unchanged"],
 # 14: fleet file intentionally MISSING (fidelity probe: self absent + missing file)
}
lane = {
 10: ["# Spot 10", "expansion: unchanged", "quality: unprovable-but-better", "discernment: harmed"],
 # 11: lane file intentionally MISSING (documented absent path)
 12: ["# Spot 12", "expansion: unprovable"],
 13: ["# Spot 13", "quality: unprovable-but-better"],
 14: ["# Spot 14", "expansion: improved"],
}
for r, ls in fleet.items():
    put(F, f".ufo/reports/round-{r}/kama.md", "\n".join(ls) + "\n")
for r, ls in lane.items():
    put(L, f"corpus/lessons/round-{r}-verifier-spotcheck.md", "\n".join(ls) + "\n")
FR = commit(F, "synthetic fleet reports")
BR = commit(L, "synthetic lane spotchecks")

spec = importlib.util.spec_from_file_location("c2", AUD)
c2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c2)
c2.FLEET_REV = FR; c2.BASE = BR; c2.ROUNDS = range(10, 15)

HDR = "round\ttrend\tside\tverdict\trepo\trev\tpath\tline\tnote"
FP = ".ufo/reports/round-{r}/kama.md"; LP = "corpus/lessons/round-{r}-verifier-spotcheck.md"
NOTE = "synthetic harness row for rule verification"
def row(r, t, side, v, ln):
    if side == "self":
        repo, rev, path = "fleet", FR, FP.format(r=r)
    else:
        repo, rev, path = "lane", BR, LP.format(r=r)
    return "\t".join([str(r), t, side, v, repo, rev, path, str(ln), NOTE])

AB = ("absent", "-")
rows = [
 row(10,"expansion","self","improved",2),        row(10,"expansion","outside","unchanged",2),
 row(10,"quality","self","unprovable-but-better",3), row(10,"quality","outside","unprovable-but-better",3),
 row(10,"discernment","self","mixed",4),         row(10,"discernment","outside","harmed",4),
 row(11,"expansion","self","unprovable",3),      row(11,"expansion","outside",*AB),
 row(11,"quality","self","unchanged",2),         row(11,"quality","outside",*AB),
 row(11,"discernment","self",*AB),               row(11,"discernment","outside",*AB),
 row(12,"expansion","self","unprovable-but-better",2), row(12,"expansion","outside","unprovable",2),
 row(12,"quality","self",*AB),                   row(12,"quality","outside",*AB),
 row(12,"discernment","self",*AB),               row(12,"discernment","outside",*AB),
 row(13,"expansion","self",*AB),                 row(13,"expansion","outside",*AB),
 row(13,"quality","self","unchanged",2),         row(13,"quality","outside","unprovable-but-better",2),
 row(13,"discernment","self",*AB),               row(13,"discernment","outside",*AB),
 row(14,"expansion","self",*AB),                 row(14,"expansion","outside","improved",2),
 row(14,"quality","self",*AB),                   row(14,"quality","outside",*AB),
 row(14,"discernment","self",*AB),               row(14,"discernment","outside",*AB),
]
TABLE = [
 "| 10 | expansion | improved | unchanged | overclaim |",
 "| 10 | discernment | mixed | harmed | other |",
 "| 12 | expansion | unprovable-but-better | unprovable | overclaim |",
 "| 13 | quality | unchanged | unprovable-but-better | underclaim |",
]
SUMMARY = "agreement=1/4 overclaim=2 underclaim=1 other=1 absent=10"
def scorecard(rows_tbl, summary, axes=True, heading="### Round-44 calibration ledger"):
    ax = "| calibration | 7 | registry/verdict-ledger.tsv |\n" if axes else "| calibration | 7 | (none) |\n"
    body = "".join(x + "\n" for x in rows_tbl) + (summary + "\n" if summary else "")
    return ("# Scorecard\n## Axes\n| axis | score | run |\n" + ax +
            "## Notes\n" + heading + "\n" + body + "## Next\n")

def run(label, ledger_rows, sc, tip=None, expect=None):
    put(L, "registry/verdict-ledger.tsv", HDR + "\n" + "".join(x + "\n" for x in ledger_rows))
    put(L, "SCORECARD.md", sc)
    tip = tip or commit(L, label)
    out = io.StringIO(); err = io.StringIO()
    old = sys.argv
    sys.argv = ["c2", "--repo", L, "--tip", tip, "--fleet", F, "--out", os.path.join(S, "harness-out.txt")]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = c2.main()
    finally:
        sys.argv = old
    text = out.getvalue()
    line2 = text.splitlines()[1] if len(text.splitlines()) > 1 else "(no output)"
    ok = "" if expect is None or rc == expect else f"  <<< EXPECTED exit {expect}"
    print(f"[{label}] exit={rc}{ok}\n    {line2}")
    det = [x for x in text.splitlines() if x.startswith("detail:")]
    for d in det[:6]:
        print("    " + d)
    if len(det) > 6:
        print(f"    ... {len(det)-6} more detail lines")
    if err.getvalue().strip():
        print("    stderr:", err.getvalue().strip().splitlines()[-1][:160])
    return rc, text

print("=== MAIN: expect met=True exit 0 (30 valid, agree=1 over=2 under=1 other=1 absent=10) ===")
run("main", rows, scorecard(TABLE, SUMMARY), expect=0)

print("=== M1 duplicate key ===")
run("m1", rows + [rows[0]], scorecard(TABLE, SUMMARY), expect=1)
print("=== M2 wrong rev on self row ===")
bad = list(rows); bad[0] = row(10,"expansion","self","improved",2).replace(FR, "0"*40)
run("m2", bad, scorecard(TABLE, SUMMARY), expect=1)
print("=== M3 line out of range (0 and len+1) ===")
bad = list(rows); bad[0] = row(10,"expansion","self","improved",0)
bad[1] = row(10,"expansion","outside","unchanged",99)
run("m3", bad, scorecard(TABLE, SUMMARY), expect=1)
print("=== M4 verdict outside vocabulary ===")
bad = list(rows); bad[0] = row(10,"expansion","self","better",2)
run("m4", bad, scorecard(TABLE, SUMMARY), expect=1)
print("=== M5 absent note too short ===")
bad = list(rows); bad[6] = row(11,"expansion","outside","absent","-").replace(NOTE, "short")
run("m5", bad, scorecard(TABLE, SUMMARY), expect=1)
print("=== M6 absent with numeric line ===")
bad = list(rows); bad[6] = row(11,"expansion","outside","absent",1)
run("m6", bad, scorecard(TABLE, SUMMARY), expect=1)
print("=== M7 absent but the file's line gives the trend a verdict ===")
bad = list(rows); bad[13] = row(12,"expansion","outside","absent","-")
run("m7", bad, scorecard(TABLE, SUMMARY), expect=1)
print("=== M8 mixed claimed but line has one word ===")
bad = list(rows); bad[4] = row(10,"discernment","self","mixed",2)  # line 2: expansion: improved -> no discernment
run("m8", bad, scorecard(TABLE, SUMMARY), expect=1)
print("=== M9 summary figure wrong ===")
run("m9", rows, scorecard(TABLE, "agreement=1/4 overclaim=3 underclaim=1 other=1 absent=10"), expect=1)
print("=== M10 extra table row ===")
run("m10", rows, scorecard(TABLE + ["| 11 | quality | unchanged | absent | x |"], SUMMARY), expect=1)
print("=== M11 missing table row ===")
run("m11", rows, scorecard(TABLE[1:], SUMMARY), expect=1)
print("=== M12 axes row without ledger path ===")
run("m12", rows, scorecard(TABLE, SUMMARY, axes=False), expect=1)
print("=== M13 heading typo ===")
run("m13", rows, scorecard(TABLE, SUMMARY, heading="### Round-44 calibration ledgar"), expect=1)
print("=== M16 mismatch row placed OUTSIDE the section ===")
sc = scorecard([], SUMMARY)  # empty section, rows appended after ## Next
sc += "| 10 | expansion | improved | unchanged | overclaim |\n| 10 | discernment | mixed | harmed | other |\n| 12 | expansion | unprovable-but-better | unprovable | overclaim |\n| 13 | quality | unchanged | unprovable-but-better | underclaim |\n"
run("m16", rows, sc, expect=1)
print("=== M15 unresolvable tip -> exit 2 ===")
run("m15", rows, scorecard(TABLE, SUMMARY), tip="0"*40, expect=2)
print("=== M17 fidelity probe: self absent with MISSING fleet file accepted inside met=True run ===")
out = io.StringIO()
sys.argv = ["c2", "--repo", L, "--tip", git(L, "rev-parse", "HEAD"), "--fleet", F]
with contextlib.redirect_stdout(out):
    rc = c2.main()
sys.argv = ["c2"]
txt = out.getvalue()
line14 = [x for x in txt.splitlines() if x.startswith("detail:") and "'14'" in x]
print("    r14 self rows flagged?", line14 if line14 else "NONE (accepted as valid/absent)")
print("done")
