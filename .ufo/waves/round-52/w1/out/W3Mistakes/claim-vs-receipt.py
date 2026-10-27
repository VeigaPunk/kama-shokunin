#!/usr/bin/env python3
"""claim-vs-receipt.py - proposed check for the round-52 lesson's Mistakes row 2.

Question: does a measured-results sentence that asserts a pointer verdict name the
receipt that shows it, and does that receipt read `met=True`?

Rule: in SCORECARD.md at --tip, inside every `### Round-N measured results` section,
split each line into sentences at `. `; a sentence that contains `pointer` and a
verdict word (`resolves`, `met=True`, `met=False`) must cite a backticked `.ufo/...`
receipt in that same sentence. A plain path must exist at --tip and its last `met=`
token must equal the sentence's word (True when the sentence says `resolves`); a
glob must expand to >= 1 receipt and at least one must read the sentence's word.
No citation, a missing receipt, or a receipt reading the other way is a violation
(the round-51 D3 shape: a sentence firmed up against receipts that do not read that
way).

Exit: 0 every pointer verdict is receipted and true; 1 at least one is not; 2 could
not evaluate. This is a proposal in the seat's out directory.
"""
import argparse
import fnmatch
import re
import subprocess
import sys


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {p.stderr.decode()[:200]}")
    return p.stdout.decode("utf-8", "replace")


def verdict_of(repo, rev, path):
    p = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True)
    if p.returncode:
        return None
    ets = re.findall(r"met=(True|False)", p.stdout.decode("utf-8", "replace"))
    return ets[-1] if ets else "none"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    a = ap.parse_args()
    tree = [p for p in git(a.repo, "ls-tree", "-r", "--name-only", a.tip).split("\n") if p]
    lines = git(a.repo, "show", f"{a.tip}:SCORECARD.md").split("\n")
    insec = None
    bad = 0
    for n, line in enumerate(lines, 1):
        m = re.match(r"^### Round-(\d+) measured results", line)
        if m:
            insec = m.group(1)
            continue
        if line.startswith("### ") or line.startswith("## "):
            insec = None
            continue
        if insec is None or "pointer" not in line.lower():
            continue
        for sent in re.split(r"(?<=\.)\s+", line):
            if "pointer" not in sent.lower():
                continue
            if re.search(r"met=False", sent):
                want = "False"
            elif re.search(r"met=True|resolves?", sent, re.I):
                want = "True"
            else:
                continue
            cited = [t for t in re.findall(r"`([^`]+)`", sent)
                     if t.startswith(".ufo/") and "." in t.rsplit("/", 1)[-1]]
            if not cited:
                bad += 1
                print(f"UNCITED SCORECARD.md:{n} round={insec} want=met={want}: {sent.strip()[:150]}")
                continue
            for tok in cited:
                paths = fnmatch.filter(tree, tok) if any(c in tok for c in "*?[") else [tok]
                if not paths:
                    bad += 1
                    print(f"MISSING SCORECARD.md:{n} {tok} matches no path")
                    continue
                got = {p: verdict_of(a.repo, a.tip, p) for p in paths}
                if want not in got.values():
                    bad += 1
                    print(f"VERDICT SCORECARD.md:{n} wants met={want}; {tok} -> "
                          f"{ {k: v for k, v in list(got.items())[:3]} }")
    print(f"claim-vs-receipt tip={a.tip[:12]} violations={bad} met={'False' if bad else 'True'}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
