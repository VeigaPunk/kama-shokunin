#!/usr/bin/env python3
"""S9Cap controls: two mutations of the appended round-48 canonical table.

ctlA: the append-only-audit evidence pointer names a file that does not exist
      -> the audit must report unsubstantiated>=1, exit 1.
ctlB: the canonical row is renamed so the name the mirror and the earlier
      canonical tables carry is unlisted -> missing=1, exit 1.
Each control is committed on the clone (detached); the clone is returned to BASE.
Usage: make-controls.py <clone> <base-commit> <out-dir>
"""
import subprocess
import sys

clone, base, out = sys.argv[1:4]
G = ["git", "-C", clone]


def git(*a, **kw):
    return subprocess.run(G + list(a), check=kw.get("check", True),
                          capture_output=True, text=True).stdout.strip()


def commit(msg):
    git("add", "SCORECARD.md")
    git("-c", "user.name=S9Cap", "-c", "user.email=s9cap@localhost",
        "commit", "-q", "-m", msg)
    return git("rev-parse", "HEAD")


raw = subprocess.run(G + ["show", "%s:SCORECARD.md" % base],
                     capture_output=True, text=True, check=True).stdout
# the appended block starts at the last canonical marker
mark = raw.rindex("**Capabilities \u2014 canonical list as of round 48**")
head, block = raw[:mark], raw[mark:]

ctlA = block.replace("`tools/round48-append-audit-v3-check.py`",
                     "`tools/round48-append-audit-v3-check-missing.py`")
assert ctlA != block
open(clone + "/SCORECARD.md", "w", encoding="utf-8").write(head + ctlA)
shaA = commit("S9Cap control A: canonical evidence pointer names a missing file")

git("switch", "--detach", base)
open(clone + "/SCORECARD.md", "w", encoding="utf-8").write(raw)
ctlB = block.replace("| append-only-audit |", "| append-only-audit-v3 |")
assert ctlB != block
open(clone + "/SCORECARD.md", "w", encoding="utf-8").write(head + ctlB)
shaB = commit("S9Cap control B: canonical row renamed, earlier tables keep the name")

git("switch", "--detach", base)
open(out + "/control-shas.txt", "w").write("base %s\nctlA %s\nctlB %s\n" % (base, shaA, shaB))
print("ctlA %s ctlB %s" % (shaA, shaB))
