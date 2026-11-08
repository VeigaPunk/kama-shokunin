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
    OUT.append(f"{label:44} rc={p.returncode} mismatched={','.join(mm) or '-'}")
def clone_and_commit(name, edits):
    d = Path(D)/"fx5"/name
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
# F1: proper label swap — both fraction strings still present, policy/ledger labels swapped.
# Anchor two lines: policy sentence then ledger sentence (SCORECARD.md block lines ~6545-6548).
probes = [
 ("F1 label-swap both present", [("SCORECARD.md", "roles (reviewer, critic, mutation-tester, labrat) were 4 of 12 (33%)", "roles (sentinel, connector) were 6 of 12 (50%)")]),
 ("F2 word-percent 58 percent", [("SCORECARD.md", '("58% attack") is arithmetic-wrong', '("58 percent attack") is arithmetic-wrong')]),
 ("F3 extra stray word-percent", [("SCORECARD.md", "The prefile ledger's attack roles (adding sentinel and connector) were\n  6 of 12 (50%)", "The prefile ledger's attack roles (adding sentinel and connector, 58 percent with the scribe) were\n  6 of 12 (50%)")]),
]
# F1 needs the LOG twin untouched and ledger sentence still carrying its fraction: to be a clean swap,
# also swap the ledger sentence's fraction back. Simpler: two-edit swap:
d = Path(D)/"fx5"/"F1-label-swap-both"
# do F1 as two edits on SCORECARD.md: policy line gets ledger fraction+label, ledger line gets policy fraction+label
t_edits = [("SCORECARD.md", "roles (reviewer, critic, mutation-tester, labrat) were 4 of 12 (33%)", "roles (sentinel, connector) were 6 of 12 (50%)"),
           ("SCORECARD.md", "6 of 12 (50%): the four above plus SN01Bounds and CN01Overlap", "4 of 12 (33%): the four above plus SN01Bounds and CN01Overlap")]
run_audit("F1 label-swap both present", clone_and_commit("F1-label-swap-both", t_edits))
for name, edits in probes[1:]:
    run_audit(name, clone_and_commit(name, edits))
print("\n".join(OUT))
Path("/fast/scratch/hyaku/kama-r100/RV01WordingC1/followup.out").write_text("\n".join(OUT)+"\n")
