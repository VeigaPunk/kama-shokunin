#!/usr/bin/env python3
"""Tree mutants for the C2 closure-pointer/reconciler conjunct (seat MT37WorkAndClosure).
Applies one SCORECARD edit per mutant, commits in the scratch clone, runs the
UNMUTATED counter at that tip, prints the one-line output, then restores the clone."""
import hashlib, os, subprocess, sys, shutil

S = "/fast/scratch/hyaku/kama-r64/f/MT37WorkAndClosure"
D = os.path.join(S, "clone")
BASE = "23b3fdb1a925129a9961cf551f6d40bf251602cb"
PTR = ("latest outside closure `corpus/lessons/round-63-verifier-spotcheck.md` "
       "(rejected-honest-stop), including round 63")

def git(*a, **k):
    return subprocess.run(["git", "-C", D, *a], capture_output=True, text=True, **k)

def run(cmd, cwd=None):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)

def counter(tip, work):
    c = os.path.join(D, "tools", "round64-c2-counter.py")
    r = run([sys.executable, c, "--repo", D, "--tip", tip, "--work", work],
            cwd=os.path.join(D, "tools"))
    return r

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def reset():
    git("reset", "--hard", BASE)
    git("clean", "-fd")

MUT = {}

# B1: calibration row names two `latest outside closure` pointers
MUT["B1-two-pointers"] = [("SCORECARD.md", lambda t: t.replace(
    PTR + ";",
    PTR + "; second pointer latest outside closure `corpus/lessons/round-62-verifier-spotcheck.md` (older);", 1))]

# B2: different backtick style (double backticks) around the pointer path
MUT["B2-backtick-style"] = [("SCORECARD.md", lambda t: t.replace(
    PTR, "latest outside closure ``corpus/lessons/round-63-verifier-spotcheck.md`` (rejected-honest-stop), including round 63", 1))]

# B3: pointer moved into the historical table's calibration row (removed from the live row)
def _b3(t):
    t = t.replace(PTR + ";", "the latest outside closure is re-derived at the measured tip by the named counter;", 1)
    lines = t.split("\n")
    assert lines[28].startswith("| calibration | 1 → 7 |")
    lines[28] = lines[28].replace(
        "| calibration | 1 → 7 | ",
        "| calibration | 1 → 7 | " + PTR + "; ", 1)
    return "\n".join(lines)
MUT["B3-pointer-in-historical"] = [("SCORECARD.md", _b3)]

# B4: pointer names round-063 (a file that does not exist at the tip)
MUT["B4-round-063"] = [("SCORECARD.md", lambda t: t.replace(
    PTR, "latest outside closure `corpus/lessons/round-063-verifier-spotcheck.md` (rejected-honest-stop), including round 63", 1))]

# B5: newest spotcheck file (round-64) added in the same commit as the pointer repair
ROUND64 = """# Round 64 verifier spotcheck

Round 64 measured tip: 23b3fdb1a925129a9961cf551f6d40bf251602cb. This outside closure
records the wave-f falsification of the round-64 claims; the counter receipts are in the
wave ledger. Nothing in this file is asserted by the C2 instrument beyond its existence.

"""
def _b5(t):
    t = t.replace(PTR, "latest outside closure `corpus/lessons/round-64-verifier-spotcheck.md` (rejected-honest-stop), including round 64", 1)
    return t
MUT["B5-round64-same-commit"] = [("SCORECARD.md", _b5),
                                 ("corpus/lessons/round-64-verifier-spotcheck.md", lambda t: ROUND64)]

# B6: round-64 file added but the pointer NOT repaired (stale) - the freeze's warned case
MUT["B6-round64-stale"] = [("corpus/lessons/round-64-verifier-spotcheck.md", lambda t: ROUND64)]

# B7: stale `including round` clause (pointer correct, inclusion clause stale)
MUT["B7-including-stale"] = [("SCORECARD.md", lambda t: t.replace(
    PTR, "latest outside closure `corpus/lessons/round-63-verifier-spotcheck.md` (rejected-honest-stop), including round 62", 1))]

only = sys.argv[1:] or sorted(MUT)
sc_path = os.path.join(D, "SCORECARD.md")
pristine_sc = open(sc_path).read()
assert hashlib.sha256(pristine_sc.encode()).hexdigest() == sha(sc_path)

for name in only:
    reset()
    for path, fn in MUT[name]:
        p = os.path.join(D, path)
        if fn is not None:
            cur = open(p).read() if os.path.exists(p) else ""
            new = fn(cur)
            if new == cur and os.path.exists(p):
                print(f"{name}: EDIT DID NOT APPLY to {path}", file=sys.stderr); sys.exit(2)
            open(p, "w").write(new)
        else:
            open(p, "w").write(fn and "" or "")
    git("add", "-A")
    c = git("commit", "-q", "-m", "wip")
    if c.returncode != 0:
        print(f"{name}: commit failed {c.stderr}", file=sys.stderr); sys.exit(2)
    T = git("rev-parse", "HEAD").stdout.strip()
    work = os.path.join(S, "work-" + name)
    r = counter(T, work)
    line = [l for l in r.stdout.splitlines() if l.startswith("tip=")]
    print(f"### {name}  tip={T[:12]}  exit={r.returncode}")
    print((line[0] if line else r.stdout.strip()[:200])[:400])
    shutil.rmtree(work, ignore_errors=True)

reset()
assert open(sc_path).read() == pristine_sc
print("restored:", sha(sc_path)[:16], "counter:",
      hashlib.sha256(open(os.path.join(D, "tools", "round64-c2-counter.py"), "rb").read()).hexdigest()[:16])
