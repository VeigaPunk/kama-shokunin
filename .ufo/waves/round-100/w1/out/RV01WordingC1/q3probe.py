import os, subprocess, sys, shutil
from pathlib import Path
D = open("/fast/scratch/hyaku/kama-r100/RV01WordingC1/dpath.txt").read().strip()
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
COUNTER = os.path.join(LANE, "tools/round100-record-audit.py")
FILES = ["SCORECARD.md", "LOG.md", ".ufo/waves/round-100/r99-measured.json"]
OUT=[]
def run_audit(label, d):
    p = subprocess.run([sys.executable, COUNTER, "--repo", str(d), "--rev", "HEAD"], capture_output=True, text=True)
    last=[l for l in p.stdout.splitlines() if l.startswith("RECORD_AUDIT100 ")]
    mm=[l.split()[1] for l in p.stdout.splitlines() if l.startswith("RECORD_AUDIT100_MISMATCH")]
    OUT.append(f"{label:40} rc={p.returncode} mismatched={','.join(mm) or '-'} :: {last[0].split()[2:4] if last else p.stdout[-120:]!r}")
def clone_and_commit(name, edits):
    d = Path(D)/"fx3"/name
    d.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["git","clone","-q","--shared","--no-checkout", LANE, str(d)], capture_output=True, text=True)
    assert r.returncode==0, r.stderr
    top = subprocess.run(["git","-C",str(d),"rev-parse","--show-toplevel"],capture_output=True,text=True).stdout.strip()
    assert Path(top).resolve()==d, top
    subprocess.run(["git","-C",str(d),"checkout","-q","6776c667372a0da8635ebfbda6cbc92d8fb17304"],check=True)
    for f in FILES:
        (d/f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Path(LANE)/f, d/f)
    for (f,a,b) in edits:
        t=(d/f).read_text()
        if t.count(a)!=1: OUT.append(f"ANCHOR-FAIL {name} count={t.count(a)} anchor={a!r}")
        else: (d/f).write_text(t.replace(a,b,1))
    env=dict(os.environ, GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@scratch.invalid", GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="fixture@scratch.invalid")
    subprocess.run(["git","-C",str(d),"add","--",*FILES],check=True)
    c=subprocess.run(["git","-C",str(d),"commit","-q","-m",name],capture_output=True,text=True,env=env); assert c.returncode==0, c.stderr
    return d
probes = [
 ("W8 wrong n in words, right pct",    [("SCORECARD.md","6 of 12 (50%)","seven of 12 (50%)")]),
 ("W8b wrong n in words (all words)",  [("SCORECARD.md","were\n  6 of 12 (50%)","were\n  seven of 12 (50%)")]),
 ("W9 decimal pct 49.9%",              [("SCORECARD.md","6 of 12 (50%)","6 of 12 (49.9%)")]),
 ("W10 decimal pct 50.0%",             [("SCORECARD.md","6 of 12 (50%)","6 of 12 (50.0%)")]),
 ("W11 decimal pct 50.5%",             [("SCORECARD.md","6 of 12 (50%)","6 of 12 (50.5%)")]),
 ("W12 seats wrong keep shares",       [("SCORECARD.md","had 12 seats, 0 dead","had 19 seats, 0 dead")]),
 ("W13 contradicts share in words",    [("SCORECARD.md","The prefile ledger's attack roles","The prefile ledger's attack roles — seven seats, more than half")]),
 ("W14 heading em-dash vs hyphen",      [("SCORECARD.md","## Round 100 correction \u2014 round-99 records","## Round 100 correction - round-99 records")]),
 ("W15 heading twice",                  [("SCORECARD.md","The LOG twin did not\n  move:","The LOG twin did not\n  move: ## Round 100 correction \u2014 round-99 records")]),
 ("W16 heading then extra ## early",    [("SCORECARD.md","- **Measured values.**","## Notes\n- **Measured values.**")]),
 ("W17 file:line inside prose dash",    [("SCORECARD.md","because an unbound `file:line`","because an unbound `SCORECARD.md:6431`")]),
 ("W18 lessons pointer unbound",        [("SCORECARD.md","Routed by `corpus/lessons/round-99-verifier-spotcheck.md`","Routed by corpus/lessons/round-99-verifier-spotcheck.md:3")]),
 ("W19 bound phrase moved line",        [("SCORECARD.md","`SCORECARD.md@6776c667:6446`","`SCORECARD.md@6776c667:6447`")]),
 ("W20 bound>=3 diluted: 9 bogus",      [("SCORECARD.md","move: `LOG.md@6776c667:4040`","move: `LOG.md@6776c667:4040` `SCORECARD.md@6776c667:6500`")]),
]
for name, edits in probes:
    run_audit(name, clone_and_commit(name, edits))
print("\n".join(OUT))
Path("/fast/scratch/hyaku/kama-r100/RV01WordingC1/q3.out").write_text("\n".join(OUT)+"\n")
