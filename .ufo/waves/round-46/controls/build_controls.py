#!/usr/bin/env python3
"""Round-46 controls: the cheapest ledgers/tools that skip the claimed work, scored by the frozen counters.

Each control is a commit on a scratch `git clone --shared` of the lane at the round-46 base, made with a
fixture identity and `git -C <clone>` only (toplevel verified). Outputs land beside this file as
<control>.c1.out / <control>.c2.out with the exit code appended. Every control must read met=False.
Usage: python3 build_controls.py <lane> <llama.cpp clone holding b11889 and b11906> <scratch dir>
"""
import csv
import json
import os
import shutil
import subprocess
import sys

LANE, UP, SCR = sys.argv[1], sys.argv[2], sys.argv[3]
BASE = "0163fea2dab3f282ebd70c71da9ab5de4cedf733"
REL, RELC = "b11906", "4d71b42fd87db24b8b7c808c151b713aa4459cfd"
HERE = os.path.dirname(os.path.abspath(__file__))
C1 = os.path.join(LANE, "tools/round46-release-recheck-audit.py")
C2 = os.path.join(LANE, "tools/round46-append-audit-check.py")
ID = ["-c", "user.name=r46-control", "-c", "user.email=r46-control@invalid", "-c", "commit.gpgsign=false"]


def g(d, *a):
    return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, check=True).stdout


def blob(rev, path):
    p = subprocess.run(["git", "-C", UP, "rev-parse", "--verify", "-q", f"{rev}:{path}"], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else "-"


os.makedirs(SCR, exist_ok=True)
D = os.path.join(SCR, "ctl-clone")
shutil.rmtree(D, ignore_errors=True)
subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", LANE, D], check=True)
assert os.path.realpath(g(D, "rev-parse", "--show-toplevel").strip()) == os.path.realpath(D)
g(D, "checkout", "-q", "--detach", BASE)

SECTION = "\n## Round-46 release re-verification (control)\n\ncontrol section\n"
ROW = (f"| S999 | https://github.com/ggml-org/llama.cpp/releases/tag/{REL} | docs | A | control | "
       f"{REL} {RELC} | control | 2026-10-26 | mined | 30d | - |\n")


def add_sources():
    p = os.path.join(D, "corpus/SOURCES.md")
    with open(p, "a") as fh:
        fh.write(SECTION)
    txt = open(p).read()
    # registry row appended right after the last registry row line
    lines = txt.split("\n")
    last = max(i for i, x in enumerate(lines) if x.startswith("| S"))
    lines.insert(last + 1, ROW.rstrip("\n"))
    open(p, "w").write("\n".join(lines))


def commit(tag):
    g(D, "add", "-A")
    g(D, *ID, "commit", "-q", "-m", f"control {tag}")
    return g(D, "rev-parse", "HEAD").strip()


def run(tag, rev, which):
    outs = {}
    if "c1" in which:
        p = subprocess.run([sys.executable, C1, "--repo", D, "--tip", rev, "--upstream", UP], capture_output=True, text=True)
        outs["c1"] = p.stdout + f"exit={p.returncode}\n"
    if "c2" in which:
        p = subprocess.run([sys.executable, C2, "--repo", D, "--tip", rev, "--scratch", os.path.join(SCR, "c2fx")],
                           capture_output=True, text=True)
        outs["c2"] = p.stdout + f"exit={p.returncode}\n"
    for k, v in outs.items():
        with open(os.path.join(HERE, f"{tag}.{k}.out"), "w") as fh:
            fh.write(v)
        print(tag, k, v.splitlines()[1] if len(v.splitlines()) > 1 else v)


old = list(csv.DictReader(open(os.path.join(LANE, "registry/release-recheck-b11889.tsv")), delimiter="\t"))
HDR = ["id", "path", "pin_commit", "release", "pin_blob", "release_blob", "changed", "pin_lines",
       "release_lines", "witness_pin", "witness_new", "verdict", "note"]


def write_ledger(rows):
    with open(os.path.join(D, f"registry/release-recheck-{REL}.tsv"), "w") as fh:
        fh.write("\t".join(HDR) + "\n")
        for r in rows:
            fh.write("\t".join(r[h] for h in HDR) + "\n")


# C1 control 1: carry the b11889 ledger forward (blobs re-derived, lines and verdicts kept, no reading)
g(D, "checkout", "-q", "--detach", BASE)
rows = []
for r in old:
    rb = blob(RELC, r["path"])
    n = dict(r, release=REL, release_blob=rb, changed="0" if rb == r["pin_blob"] else "1",
             witness_pin="-", witness_new="-")
    rows.append(n)
write_ledger(rows)
add_sources()
run("junk-c1-carryforward", commit("carryforward"), ["c1"])

# C1 control 2: every changed row filed holds-reworded with filler notes and boilerplate witnesses
g(D, "checkout", "-q", "--detach", BASE)
rows2 = []
for r in rows:
    n = dict(r)
    if n["changed"] == "1":
        n.update(verdict="holds-reworded", witness_pin="#include \"server-context.h\"",
                 witness_new="#include \"server-context.h\"",
                 note="statement still true at b11906 after a rewording of the anchored lines (filler)")
    rows2.append(n)
write_ledger(rows2)
add_sources()
run("junk-c1-massreworded", commit("massreworded"), ["c1"])

# C2 control 1: a tool that replays the lane's events from a list fixed at build time
g(D, "checkout", "-q", "--detach", BASE)
sys.path.insert(0, os.path.dirname(C2))
import importlib.util
spec = importlib.util.spec_from_file_location("c2", C2)
c2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c2)
lane_events = c2.recompute(LANE, BASE)
TABLE = "\n| append-only-audit | control | tools/append-only-audit.py | 46 |\n"
fixed = json.dumps({"events": lane_events})
bad = any(e["status"] != "restored" for e in lane_events)
hard = f'''import sys
if "--selftest" in sys.argv:
    print("AOA_SELFTEST pass=6 fail=0"); sys.exit(0)
print({fixed!r}); sys.exit({1 if bad else 0})
'''
os.makedirs(os.path.join(D, "tools"), exist_ok=True)
open(os.path.join(D, "tools/append-only-audit.py"), "w").write(hard)
open(os.path.join(D, "SCORECARD.md"), "a").write(TABLE)
run("junk-c2-hardcoded", commit("hardcoded"), ["c2"])

# C2 control 2: the counter's own event finder without restoration (every event unrestored)
g(D, "checkout", "-q", "--detach", BASE)
norest = f'''import json, sys, importlib.util
if "--selftest" in sys.argv:
    print("AOA_SELFTEST pass=6 fail=0"); sys.exit(0)
spec = importlib.util.spec_from_file_location("c2", {C2!r}); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
a = sys.argv; repo = a[a.index("--repo") + 1]; to = a[a.index("--to") + 1]
ev = m.recompute(repo, to)
for e in ev:
    e["status"] = "unrestored"; e["restored_at_tip"] = 0; e["restored_by"] = None
print(json.dumps({{"events": ev}})); sys.exit(1 if ev else 0)
'''
open(os.path.join(D, "tools/append-only-audit.py"), "w").write(norest)
open(os.path.join(D, "SCORECARD.md"), "a").write(TABLE)
run("junk-c2-norestore", commit("norestore"), ["c2"])

shutil.rmtree(D, ignore_errors=True)
shutil.rmtree(os.path.join(SCR, "c2fx"), ignore_errors=True)
