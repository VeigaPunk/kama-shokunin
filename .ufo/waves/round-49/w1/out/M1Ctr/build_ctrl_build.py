#!/usr/bin/env python3
"""Fake-witness control at the BUILD tip: clone $S/lane (HEAD 74558c71), detach
at the build commit, swap tools/kama-live-replay.py for FAKE_REPLAY, commit.
The control's only failure then is the witness leg (exe check), isolating the
K2Cheat shape against the measured build.
"""
import ast
import os
import subprocess

LANE = "/fast/scratch/hyaku/kama-r49/M1Ctr/lane"
SCR = "/fast/scratch/hyaku/kama-r49/M1Ctr/ctrl"
TARGET = "74558c71c38ceaeace15fd4cf8aa9d84977584b1"
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
d = os.path.join(SCR, "junk-c1b")
if os.path.isdir(d):
    import shutil
    shutil.rmtree(d)
sh("git", "clone", "-q", "--shared", "--no-checkout", LANE, d)
sh("git", "-C", d, "checkout", "-q", "--detach", TARGET)
top = sh("git", "-C", d, "rev-parse", "--show-toplevel").strip()
assert os.path.realpath(top) == os.path.realpath(d), (top, d)
with open(os.path.join(d, "tools/kama-live-replay.py"), "w") as fh:
    fh.write(fake_replay_text())
sh("git", "-C", d, "add", "-A")
sh("git", "-C", d, *IDENT, "commit", "-q", "-m", "control: fake witness replay (build tip)")
tip = sh("git", "-C", d, "rev-parse", "HEAD").strip()
print("control tip:", tip)
print("toplevel:", top)
