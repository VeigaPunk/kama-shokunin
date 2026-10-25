#!/usr/bin/env python3
"""Round-41 freeze controls: build sandbox revisions and score both frozen counters.

Usage: build_controls.py <lane clone> <base commit> <out dir>
Every git write happens in a fresh mktemp sandbox clone (git -C "$D"), never
in the lane. The sandbox identity is fixture-only.
"""
import os, re, subprocess, sys, tempfile, shutil

lane, base, out = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3])
os.makedirs(out, exist_ok=True)
D = tempfile.mkdtemp(prefix="r41-controls-")
def g(*a, **k):
    return subprocess.run(["git", "-C", D, *a], check=True, capture_output=True, text=True, **k).stdout
subprocess.run(["git", "clone", "-q", "--no-local", lane, D], check=True)
assert g("rev-parse", "--show-toplevel").strip() == os.path.realpath(D), "sandbox toplevel mismatch"
g("checkout", "-q", "--detach", base)
ID = ["-c", "user.name=r41-control", "-c", "user.email=r41-control@fixture.invalid"]
C1 = "/tmp/R41A05-mut/m4-no-brace-expand.py"
C2 = os.path.join(lane, "tools/round41-pinwatch-audit.py")
TABLE = open(os.path.join(lane, ".ufo/waves/round-41/controls/axes-table-candidate.md")).read()

def commit(msg):
    g("add", "-A")
    subprocess.run(["git", "-C", D, *ID, "commit", "-q", "--allow-empty", "-m", msg], check=True)
    return g("rev-parse", "HEAD").strip()

def write(p, s):
    os.makedirs(os.path.dirname(os.path.join(D, p)) or D, exist_ok=True)
    open(os.path.join(D, p), "w").write(s)

def replace_axes_table(new_table):
    sc = open(os.path.join(D, "SCORECARD.md")).read().split("\n")
    i = sc.index("## Axes")
    j = i + 1
    while not sc[j].startswith("|"):
        j += 1
    k = j
    while k < len(sc) and sc[k].startswith("|"):
        k += 1
    old = sc[j:k]
    sc[j:k] = new_table.rstrip("\n").split("\n") + ["", "### Historical axes table (superseded round 41)", ""] + old
    open(os.path.join(D, "SCORECARD.md"), "w").write("\n".join(sc))

def apply_c2(stub=False, capability=True, sourced=True):
    for p in ("tools/pin-watch.py", "registry/engine-pins.tsv"):
        if stub and p == "tools/pin-watch.py":
            continue
        shutil.copy(os.path.join(lane, p), os.path.join(D, p))
    if stub:
        live = subprocess.run([sys.executable, os.path.join(lane, "tools/pin-watch.py"), "check", "--pins",
                               os.path.join(lane, "registry/engine-pins.tsv")], capture_output=True, text=True)
        write("tools/pin-watch.py", "import sys\nprint(%r, end='')\nsys.exit(%d)\n" % (live.stdout, live.returncode))
    if sourced:
        src = open(os.path.join(D, "corpus/SOURCES.md")).read().split("\n")
        last = max(i for i, l in enumerate(src) if re.match(r"^ {0,3}\| *S\d{3,} *\|", l))
        src.insert(last + 1, "| S999 | control row — https://git-scm.com/docs/git-ls-remote | docs | A | control | OUTPUT | control | mined | 2026-10-25 | 90d | corpus/knowledge/engine-pin-watch.md |")
        open(os.path.join(D, "corpus/SOURCES.md"), "w").write("\n".join(src))
        write("corpus/knowledge/engine-pin-watch.md", "# control\n\nsource: S999 control\nverified-at: 2026-10-25\nrecheck: 90d\n")
    if capability:
        sc = open(os.path.join(D, "SCORECARD.md")).read()
        sc += ("\n**Capabilities — canonical list as of round 41**\n\n| Capability | What it can now do | Evidence pointer | First-working round |\n|---|---|---|---|\n"
               "| pin-watch | control | `tools/pin-watch.py` | 41 |\n")
        open(os.path.join(D, "SCORECARD.md"), "w").write(sc)

def score(name, rev):
    for tag, ctr in (("c1", C1), ("c2", C2)):
        args = [sys.executable, ctr, "--repo", D, "--tip", rev, "--out", os.path.join(out, f"{name}.{tag}.out")]
        if tag == "c2":
            args += ["--seed", "41"]
        p = subprocess.run(args, capture_output=True, text=True)
        with open(os.path.join(out, f"{name}.{tag}.out"), "a") as f:
            f.write(f"exit={p.returncode}\n")
        print(name, tag, p.stdout.splitlines()[1] if len(p.stdout.splitlines()) > 1 else p.stderr.strip(), "exit", p.returncode)

score("base", base)
# freeze stand-in: base + the two frozen counters (the lane's freeze commit adds them)
g("checkout", "-q", "--detach", base)
for p in ("tools/round41-scorecard-reconcile.py", "tools/round41-pinwatch-audit.py"):
    shutil.copy(os.path.join(lane, p), os.path.join(D, p))
FREEZE = commit("freeze stand-in: counters")
score("freeze", FREEZE)
# positive controls
g("checkout", "-q", "--detach", FREEZE); replace_axes_table(TABLE); r = commit("c1 only"); score("pos-c1only", r)
g("checkout", "-q", "--detach", FREEZE); apply_c2(); r = commit("c2 only"); score("pos-c2only", r)
replace_axes_table(TABLE); r = commit("c1+c2"); score("pos-both", r)
# junk / shortcut controls
g("checkout", "-q", "--detach", FREEZE)
hollow = "\n".join(l if not l.startswith("| ") or l.startswith("| Axis") else re.sub(r"^(\| [^|]+\| [^|]+\|)[^|]+\|", r"\1 see rounds |", l) for l in TABLE.split("\n"))
replace_axes_table(hollow); r = commit("junk hollow table"); score("junk-c1-hollow", r)
g("checkout", "-q", "--detach", FREEZE)
sc = open(os.path.join(D, "SCORECARD.md")).read().replace("| **6 → 7** |", "| **6 → 8** |").replace("| 1 → 8 | `listener", "| 1 → 9 | `listener")
open(os.path.join(D, "SCORECARD.md"), "w").write(sc); r = commit("junk scores only"); score("junk-c1-scoresonly", r)
g("checkout", "-q", "--detach", FREEZE)
replace_axes_table(TABLE.replace("RESULT pass=30 fail=0", "RESULT pass=31 fail=0")); r = commit("junk false run line"); score("junk-c1-falserun", r)
g("checkout", "-q", "--detach", FREEZE); apply_c2(stub=True); r = commit("junk stub tool echoing live output"); score("junk-c2-stub", r)
g("checkout", "-q", "--detach", FREEZE); apply_c2(capability=False); r = commit("junk no capability row"); score("junk-c2-nocap", r)
g("checkout", "-q", "--detach", FREEZE); apply_c2(sourced=False); r = commit("junk unsourced"); score("junk-c2-unsourced", r)
print("sandbox", D)
