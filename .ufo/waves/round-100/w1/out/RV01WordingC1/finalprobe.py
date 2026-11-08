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
    OUT.append(f"{label:42} rc={p.returncode} mismatched={','.join(mm) or '-'}")
def clone_and_commit(name, edits):
    d = Path(D)/"fx4"/name
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
H = "## Round 100 correction \u2014 round-99 records"
probes = [
 # G1 substring superstring: numerator 14 contains "4 of 12 (33%)" as substring
 ("G1a 14-of-12-33pct",      [("SCORECARD.md","were 4 of 12 (33%)","were 14 of 12 (33%)")]),
 ("G1b 16-of-12-50pct",      [("SCORECARD.md","were\n  6 of 12 (50%)","were\n  16 of 12 (50%)")]),
 # G2 seat superstring: 112 contains "12 seats, 0 dead"
 ("G2 112-seats",            [("SCORECARD.md","had 12 seats, 0 dead","had 112 seats, 0 dead")]),
 # G4 swapped policy/ledger labels
 ("G4 swapped-labels",       [("SCORECARD.md","the policy attack\n  roles (reviewer, critic, mutation-tester, labrat) were 4 of 12 (33%)","the prefix attack\n  roles (sentinel, connector) were 6 of 12 (50%)")]),
 # corrected double-heading: insert a second heading line at line start
 ("D1 double-heading",       [("SCORECARD.md","Routed by `corpus/lessons/round-99-verifier-spotcheck.md`", H + "\n\nRouted by `corpus/lessons/round-99-verifier-spotcheck.md`")]),
 # G3b #L form in isolation
 ("G3b hash-L form",         [("SCORECARD.md","move: `LOG.md@6776c667:4040`","move: LOG.md#L4040")]),
]
for name, edits in probes:
    run_audit(name, clone_and_commit(name, edits))
print("\n".join(OUT))
Path("/fast/scratch/hyaku/kama-r100/RV01WordingC1/final.out").write_text("\n".join(OUT)+"\n")
