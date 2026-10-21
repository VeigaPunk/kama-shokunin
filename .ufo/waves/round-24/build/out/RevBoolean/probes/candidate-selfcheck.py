#!/usr/bin/env python3
"""Bounded self-check of the candidate fragment: does promisor_backed()
agree with git's own behaviour (the ground truth measured in
promisor-classification-matrix.tsv)?

Runs in a scratch copy of the tree; the lane tree is untouched.
"""
import importlib.util
import os
import shutil
import subprocess
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/RevBoolean")
CLONE = BASE / "fixtures" / "clone" / "c2"
CAND = BASE / "applycheck" / "tools" / "report-landing-audit.py"
BLOB = "c2532a76d98b3de3ef230a5c37888aa5e951ae5c"

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
           GIT_NO_LAZY_FETCH="1")

spec = importlib.util.spec_from_file_location("cand", CAND)
cand = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cand)

ORIGIN = '[remote "origin"]\n\turl = file:///nowhere\n'
CASES = [
    ("promisor = true", ORIGIN + "\tpromisor = true\n", True),
    ("promisor = TRUE", ORIGIN + "\tpromisor = TRUE\n", True),
    ("promisor = false", ORIGIN + "\tpromisor = false\n", False),
    ("promisor = 0x1", ORIGIN + "\tpromisor = 0x1\n", True),
    ("promisor = (empty value)", ORIGIN + "\tpromisor =\n", False),
    ("promisor (valueless key)", ORIGIN + "\tpromisor\n", True),
    ("promisor = \"true\"", ORIGIN + '\tpromisor = "true"\n', True),
    ("promisor = 'true' (single quotes)", ORIGIN + "\tpromisor = 'true'\n", None),
    ("promisor = maybe (invalid)", ORIGIN + "\tpromisor = maybe\n", None),
    ("filter only", ORIGIN + "\tpartialclonefilter = blob:none\n", True),
    ("filter + promisor=false", ORIGIN + "\tpartialclonefilter = blob:none\n\tpromisor = false\n", True),
    ("extension only, no formatversion", ORIGIN + "[extensions]\n\tpartialclone = origin\n", False),
    ("extension + formatversion 1",
     "[core]\n\trepositoryformatversion = 1\n" + ORIGIN + "[extensions]\n\tpartialclone = origin\n", True),
    ("multivalue true then false", ORIGIN + "\tpromisor = true\n\tpromisor = false\n", True),
    ("no promisor config", ORIGIN, False),
]


def git_truth():
    p = subprocess.run(["git", "-C", str(CLONE), "log", "-p", "--all"],
                       capture_output=True, env=ENV, timeout=60)
    err = p.stderr.decode("utf-8", "replace")
    if "bad boolean config value" in err or "bad config line" in err:
        return "invalid"
    return "lazy fetching disabled" in err


rows = []
for label, cfg, expected in CASES:
    (CLONE / ".git" / "config").write_text(cfg)
    state, reasons = cand.promisor_backed(CLONE)
    truth = git_truth()
    truth_bool = True if truth is True else (False if truth is False else None)
    ok = (state == truth_bool) if expected is None else (state == expected)
    rows.append((label, state, truth_bool, expected, ok, reasons))

w = max(len(r[0]) for r in rows)
print(f"{'case'.ljust(w)}  candidate  git-truth  expected  agree")
for label, state, truth, expected, ok, reasons in rows:
    print(f"{label.ljust(w)}  {str(state).ljust(9)}  {str(truth).ljust(9)}  "
          f"{str(expected).ljust(8)}  {'OK' if ok else 'MISMATCH'}"
          + (f"   {reasons}" if reasons else ""))

bad = [r for r in rows if not r[4]]
print(f"\n{len(rows) - len(bad)}/{len(rows)} agree with git's own behaviour")
out = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/"
           "build/out/RevBoolean/candidate-selfcheck.tsv")
with out.open("w") as fh:
    fh.write("case\tcandidate_promisor_backed\tgit_truth\tagrees\n")
    for label, state, truth, expected, ok, reasons in rows:
        fh.write(f"{label}\t{state}\t{truth}\t{ok}\n")
print("wrote", out)
