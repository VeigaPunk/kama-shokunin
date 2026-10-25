#!/usr/bin/env python3
"""Round-42 separability controls: each claim's file set alone, scored by all three counters.

Usage: build_separability.py <lane clone> <base commit> <claim tip commit> <out dir>
Sandbox clone in mktemp (git -C "$D"); fixture identity never used outside it.
"""
import os, re, shutil, subprocess, sys, tempfile

lane, base, tip, out = sys.argv[1], sys.argv[2], sys.argv[3], os.path.abspath(sys.argv[4])
os.makedirs(out, exist_ok=True)
D = tempfile.mkdtemp(prefix="r42-sep-", dir="/fast/scratch/kama-r42/seats/R42A14")
def g(*a):
    return subprocess.run(["git", "-C", D, *a], check=True, capture_output=True, text=True).stdout
subprocess.run(["git", "clone", "-q", "--no-local", lane, D], check=True)
assert g("rev-parse", "--show-toplevel").strip() == os.path.realpath(D)
ID = ["-c", "user.name=r42-control", "-c", "user.email=r42-control@fixture.invalid"]
CTR = {"c1": "tools/round42-selfdesc-reconcile.py", "c2": "tools/round42-digest-audit.py", "c3": "tools/round42-capacity-audit.py"}

def commit(msg):
    g("add", "-A")
    subprocess.run(["git", "-C", D, *ID, "commit", "-q", "--allow-empty", "-m", msg], check=True)
    return g("rev-parse", "HEAD").strip()

def score(name, rev):
    for tag, rel in CTR.items():
        args = [sys.executable, os.path.join(lane, rel), "--repo", D, "--tip", rev, "--out", os.path.join(out, f"{name}.{tag}.out")]
        if tag == "c2": args += ["--seed", "42"]
        if tag == "c3": args += ["--base", base]
        p = subprocess.run(args, capture_output=True, text=True, cwd=lane)
        with open(os.path.join(out, f"{name}.{tag}.out"), "a") as f:
            f.write(f"exit={p.returncode}\n")
        print(name, tag, (p.stdout.splitlines() + [p.stderr.strip()])[1][:150], "exit", p.returncode)

C2_FILES = ["tools/digest-ledger.py", "registry/digest-ledger.tsv"]
C3_FILES = ["corpus/knowledge/context-capacity-engine-sides.md", "corpus/lessons/round-42.md"]
C3_DIRS = [".ufo/waves/round-42/c3", ".ufo/waves/round-42/assimilation"]

def show(rev, p):
    return subprocess.run(["git", "-C", lane, "cat-file", "-p", f"{rev}:{p}"], capture_output=True, text=True).stdout

# sepC1: claim tip minus every C2 and C3 file (SCORECARD, README, PROVINCE keep the claim text)
g("checkout", "-q", "--detach", tip)
for p in C2_FILES + C3_FILES:
    os.remove(os.path.join(D, p))
for d in C3_DIRS:
    shutil.rmtree(os.path.join(D, d))
for p in ("corpus/SOURCES.md", "corpus/README.md"):
    open(os.path.join(D, p), "w").write(show(base, p))
score("sep-c1-only", commit("sep: C1 files only"))
# sepC2: base + C2 files + canonical list row
g("checkout", "-q", "--detach", base)
for rel in CTR.values():
    shutil.copy(os.path.join(lane, rel), os.path.join(D, rel))
for p in C2_FILES + ["tools/round41-scorecard-reconcile.py", "tools/round41-pinwatch-audit.py"]:
    open(os.path.join(D, p), "w").write(show(tip, p))
sc = show(base, "SCORECARD.md") + ("\n**Capabilities — canonical list as of round 42**\n\n| Capability | What it can now do | Evidence pointer | First-working round |\n|---|---|---|---|\n"
                                  "| digest-ledger | classify cited digests | `tools/digest-ledger.py`; `registry/digest-ledger.tsv` | 42 |\n")
open(os.path.join(D, "SCORECARD.md"), "w").write(sc)
score("sep-c2-only", commit("sep: C2 files only"))
# sepC3: base + C3 files + SOURCES rows + README block
g("checkout", "-q", "--detach", base)
for rel in CTR.values():
    shutil.copy(os.path.join(lane, rel), os.path.join(D, rel))
for p in C3_FILES + ["corpus/SOURCES.md", "corpus/README.md"]:
    os.makedirs(os.path.dirname(os.path.join(D, p)), exist_ok=True)
    open(os.path.join(D, p), "w").write(show(tip, p))
for d in C3_DIRS:
    shutil.copytree(os.path.join(lane, d), os.path.join(D, d))
score("sep-c3-only", commit("sep: C3 files only"))
print("sandbox", D)
