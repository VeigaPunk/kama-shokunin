#!/usr/bin/env python3
"""K6Scope: run the frozen C2 parser over files OUTSIDE its SURFACES at the build commit."""
import importlib.util
import json
import subprocess
import sys

CLONE = "/fast/scratch/hyaku/kama-r53/K6Scope/lane"
TIP = "c22602bd8d83ab26349d1087e916ca537ee4f9d1"
FLEET = "/home/vgpnk/Projects/shokunin"

# Load the counter module exactly as it exists at the build commit.
src = subprocess.run(["git", "-C", CLONE, "show", f"{TIP}:tools/round53-cited-path-check.py"],
                     capture_output=True, check=True).stdout.decode("utf-8", "replace")
path = "/fast/scratch/hyaku/kama-r53/K6Scope/counter-at-build.py"
with open(path, "w") as fh:
    fh.write(src)
spec = importlib.util.spec_from_file_location("counter", path)
counter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(counter)

lane = counter.Repo(CLONE, TIP)
fleet = counter.Repo(FLEET, "HEAD")

# The files the seat spec asks about (counter SURFACES are SCORECARD/SHONEN/SKILL).
TARGETS = ["LOG.md", "corpus/README.md", "corpus/QUALITY.md"]
out = subprocess.run(["git", "-C", CLONE, "ls-tree", "-r", "--name-only", TIP, "corpus/knowledge", "corpus/lessons"],
                     capture_output=True, check=True).stdout.decode()
TARGETS += [p for p in out.split("\n") if p.endswith(".md")]

report = {}
grand = {"cited": 0, "unresolved": 0}
for f in sorted(TARGETS):
    text = counter.show(CLONE, TIP, f)
    if text is None:
        continue
    cited_l = unres_l = 0
    dead = []
    for n, tok, core, lo, hi in counter.citations(text):
        cited_l += 1
        r = counter.resolve(core, lo, hi, lane, fleet)
        bad = [(e, v) for e, v in r if v != "ok"]
        if bad:
            unres_l += 1
            dead.append({"line": n, "token": tok, "bad": bad})
    report[f] = {"cited": cited_l, "unresolved": unres_l, "dead": dead}
    grand["cited"] += cited_l
    grand["unresolved"] += unres_l

print(json.dumps({"grand": grand, "files": report}, indent=1))
