import os, subprocess, sys, shutil
from pathlib import Path
D = open("/fast/scratch/hyaku/kama-r100/RV01WordingC1/dpath.txt").read().strip()
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
COUNTER = os.path.join(LANE, "tools/round100-record-audit.py")
FILES = ["SCORECARD.md", "LOG.md", ".ufo/waves/round-100/r99-measured.json"]
OUT=[]
def run_audit(label, d):
    p = subprocess.run([sys.executable, COUNTER, "--repo", str(d), "--rev", "HEAD"], capture_output=True, text=True)
    mm=[l.split()[1] for l in p.stdout.splitlines() if l.startswith("RECORD_AUDIT100_MISMATCH")]
    OUT.append(f"{label:44} rc={p.returncode} mismatched={','.join(mm) or '-'}")
def clone_and_commit(name, edits):
    d = Path(D)/"fx6"/name
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
 ("E1 in-quote percent swaps 58->42", [("SCORECARD.md", '("58% attack")', '("42% attack")')]),
 ("E2 empty-phrase but line ok",     [("LOG.md", '`LOG.md@6776c667:4040` ("10 reported, 2 dead")', '`LOG.md@6776c667:4040` ("x")')]),
 ("E3 bound on nonexistent rev",     [("SCORECARD.md","`SCORECARD.md@6776c667:6500`","`SCORECARD.md@1234567:6500`")]),
 ("E4 bound file absent at rev",      [("SCORECARD.md","move: `LOG.md@6776c667:4040`","move: `corpus/lessons/round-99-verifier-spotcheck.md@6776c667:1`")]),
 ("E5 pointer punctuation variants",  [("SCORECARD.md","`SCORECARD.md@00394f3b:6431`","`SCORECARD.md@00394f3b:6431`")]),
]
for name, edits in probes:
    run_audit(name, clone_and_commit(name, edits))
print("\n".join(OUT))
Path("/fast/scratch/hyaku/kama-r100/RV01WordingC1/closeout.out").write_text("\n".join(OUT)+"\n")
