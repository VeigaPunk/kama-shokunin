#!/usr/bin/env python3
"""Probe 3: is the `--all` root on rev-list --stdin order/blank-line
sensitive?  (Mechanism detail of the canonical PM07 operator.)

Throwaway local repository under the seat scratch; no network, no promisor.
"""
import shutil
import subprocess
from pathlib import Path

ROOT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM07/work/probe-git3")
if ROOT.exists():
    shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)

def g(repo, *args, stdin=None):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       input=stdin, text=True)
    return p.returncode, p.stdout, p.stderr

repo = ROOT / "r"
repo.mkdir()
g(repo, "init", "-q", "-b", "master", ".")
(repo / "f").write_text("x\n")
g(repo, "add", "--", "f")
g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "c1")
master = g(repo, "rev-parse", "HEAD")[1].strip()
g(repo, "checkout", "-q", "-b", "side")
(repo / "s").write_text("y\n")
g(repo, "add", "--", "s")
g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "c2")
side = g(repo, "rev-parse", "HEAD")[1].strip()
g(repo, "checkout", "-q", "master")
gd = g(repo, "rev-parse", "--absolute-git-dir")[1].strip()
obj = Path(gd) / "objects" / side[:2] / side[2:]
assert obj.exists()
obj.unlink()

cases = {
    "root-oid then --all (no blank line)": master + "\n--all\n",
    "root-oid, BLANK line, then --all": master + "\n\n--all\n",
    "--all only": "--all\n",
}
for label, stdin in cases.items():
    rc, out, err = g(repo, "rev-list", "--objects", "--missing=print",
                     "--no-object-names", "--stdin", stdin=stdin)
    print(f"[{label}] rc={rc} missing_reported="
          f"{[l for l in out.split(chr(10)) if l.startswith('?')]} "
          f"err={err.strip()!r}")
print("absent side commit:", side)
