#!/usr/bin/env python3
"""Reproduce the RefRepair arm: append one CR31 correction per problem listed by
the frozen count-c2.py --list at the arm base, commit, then re-run the counter."""
import json
import subprocess
import sys

REPO = "/tmp/kama-r31w2/RevAdmissionEvidence/c2-arm"
BASE = "0e6f8ed6891c09d5208ac1fdcb294ed9a842832e"
LIST = "/tmp/kama-r31w2/RevAdmissionEvidence/c2-base-list.json"

problems = json.load(open(LIST))["problems"]
rows = "".join(
    f"| CR31:{i + 1:02d} | {p['row']} | {p['class']} | {p['observed']} |\n"
    for i, p in enumerate(problems))
block = ("\n## Round 31 — claim-row evidence corrections\n\n"
         "| id | row | class | observed |\n"
         "|---|---|---|---|\n" + rows)
with open(REPO + "/SCORECARD.md", "ab") as fh:
    fh.write(block.encode())
subprocess.run(["git", "-C", REPO, "add", "SCORECARD.md"], check=True)
subprocess.run(["git", "-C", REPO, "-c", "user.name=r31w2-rev",
                "-c", "user.email=rev@local", "commit", "-q", "-m",
                "RefRepair reproduction: 13 corrections"], check=True)
tip = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                     capture_output=True, check=True).stdout.decode().strip()
print("tip", tip)
r = subprocess.run(["/usr/bin/python3", REPO + "/.ufo/waves/round-31/count-c2.py",
                    "--repo", REPO, "--tip", tip, "--list",
                    "--out", "/tmp/kama-r31w2/RevAdmissionEvidence/c2-repro.json"])
print("counter exit", r.returncode)
