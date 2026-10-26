#!/usr/bin/env python3
"""S9Cap control C: a canonical row whose whole evidence cell names only missing files.

ctlA (one dead pointer beside two live ones) stays green because
tools/capability-repertoire-audit.py:148 is `any(path_exists(...))`: one existing
token substantiates the row. ctlC replaces the pin-watch evidence cell outright.
Usage: make-control-c.py <clone> <base-commit> <out-dir>
"""
import subprocess
import sys

clone, base, out = sys.argv[1:4]
G = ["git", "-C", clone]


def git(*a):
    return subprocess.run(G + list(a), check=True, capture_output=True, text=True).stdout.strip()


raw = subprocess.run(G + ["show", "%s:SCORECARD.md" % base],
                     capture_output=True, text=True, check=True).stdout
mark = raw.rindex("**Capabilities \u2014 canonical list as of round 48**")
head, block = raw[:mark], raw[mark:]
old = ("| pin-watch | List upstream release tags for each pinned serving engine (SGLang, vLLM, "
       "llama.cpp) and report, per pin, the newest release tag and how many releases sort above "
       "it; exit 1 flags a recheck trigger | `tools/pin-watch.py`; `registry/engine-pins.tsv`; "
       "`corpus/knowledge/engine-pin-watch.md` | 41 |")
assert old in block
new = old.replace("`tools/pin-watch.py`; `registry/engine-pins.tsv`; "
                  "`corpus/knowledge/engine-pin-watch.md`", "`tools/pin-watch-missing.py`")
open(clone + "/SCORECARD.md", "w", encoding="utf-8").write(head + block.replace(old, new))
git("add", "SCORECARD.md")
git("-c", "user.name=S9Cap", "-c", "user.email=s9cap@localhost", "commit", "-q",
    "-m", "S9Cap control C: canonical evidence cell names only missing files")
sha = git("rev-parse", "HEAD")
git("switch", "--detach", base)
with open(out + "/control-shas.txt", "a") as f:
    f.write("ctlC %s\n" % sha)
print("ctlC %s" % sha)
