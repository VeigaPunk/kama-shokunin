#!/usr/bin/env python3
"""Rebuild the round-49 junk-c1 fake-witness control in scratch (mirrors
controls/build_controls.py's clone/commit recipe; outputs land in scratch, never
in the lane).  A lane clone at BASE 438127bc + a commit that swaps in the
FAKE_REPLAY replay tool.
"""
import ast
import os
import subprocess
import sys

LANE = "/fast/scratch/hyaku/kama-r49/M1Ctr/lane"
SCR = "/fast/scratch/hyaku/kama-r49/M1Ctr/ctrl"
BASE = "438127bc01ff3b99f98468549d58046f932490ef"
CTRL_BUILDER = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/controls/build_controls.py"
IDENT = ["-c", "user.name=r49-control", "-c", "user.email=r49-control@invalid",
         "-c", "commit.gpgsign=false"]


def sh(*argv, cwd=None):
    p = subprocess.run(argv, capture_output=True, text=True, cwd=cwd)
    if p.returncode != 0:
        raise SystemExit(f"{argv[:5]}: {p.stderr[-500:]}")
    return p.stdout


def fake_replay_text():
    src = open(CTRL_BUILDER).read()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "FAKE_REPLAY" for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("FAKE_REPLAY not found")


os.makedirs(SCR, exist_ok=True)
d = os.path.join(SCR, "junk-c1")
if os.path.isdir(d):
    shutil.rmtree(d) if (shutil := __import__("shutil")) else None
sh("git", "clone", "-q", "--shared", "--no-checkout", LANE, d)
sh("git", "-C", d, "checkout", "-q", "--detach", BASE)
top = sh("git", "-C", d, "rev-parse", "--show-toplevel").strip()
assert os.path.realpath(top) == os.path.realpath(d), (top, d)
# mirror the archived recipe: counters present at tip
for c in ("round49-replay-witness-audit.py", "round49-append-audit-v4-check.py"):
    sh("cp", os.path.join(LANE, "tools", c), os.path.join(d, "tools", c))
with open(os.path.join(d, "tools/kama-live-replay.py"), "w") as fh:
    fh.write(fake_replay_text())
sh("git", "-C", d, "add", "-A")
sh("git", "-C", d, *IDENT, "commit", "-q", "-m", "control: fake witness replay")
tip = sh("git", "-C", d, "rev-parse", "HEAD").strip()
print("control tip:", tip)
print("toplevel:", top)
