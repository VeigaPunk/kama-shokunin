#!/usr/bin/env python3
"""Isolate the self-reference: does citing the gate as a run fact block the gate?

Operates only on the fixture copy S/fx/green (never the lane). Patches the
fixture's own SCORECARD.md citations (PROVINCE sha/lines, coverage count) to the
fixture's observed values, then compares two runs of the gate:
  A: row keeps `run python3 tools/pre-report-gate.py --repo . --round 71 --tip master`
  B: that citation clause is removed from the row
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

D = Path("/fast/scratch/hyaku/kama-r71/CRT01ClaimsAttack/fx/green")
SC = D / "SCORECARD.md"
CITE = ("run `python3 tools/pre-report-gate.py --repo . --round 71 --tip master` "
        "\u2192 `PRE_REPORT round=71 arms=5 failed=0 uncommitted=0` (exit 0); ")


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def patch_citations():
    text = SC.read_text(encoding="utf-8")
    data = (D / "PROVINCE.md").read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    lines = data.decode("utf-8").count("\n")
    text = re.sub(r"(PROVINCE\.md` sha256 `)[0-9a-f]{64}", r"\g<1>" + sha, text, count=1)
    text = re.sub(r"(PROVINCE\.md` sha256 `[0-9a-f]{64}` \()(\d+)( lines)", r"\g<1>" + str(lines) + r"\3", text, count=1)
    # coverage count: re-derive the cited integer in the glob command's arrow.
    rc, out = run([sys.executable, "-c",
                   "import glob;print(len([f for f in glob.glob('corpus/knowledge/*.md') "
                   "if 'engine-sides' not in f and 'processes' not in f]))"], D)
    observed = out.strip().splitlines()[-1] if rc == 0 else "?"
    text = re.sub(r"(python3 -c \"import glob;print\(len\(\[f for f in glob\.glob\('corpus/knowledge/\*\.md'\) "
                  r"if 'engine-sides' not in f and 'processes' not in f\]\)\)\"` \u2192 `)(\d+)(`)",
                  r"\g<1>" + observed + r"\3", text, count=1)
    SC.write_text(text, encoding="utf-8")
    return sha, lines, observed


def gate(label):
    rc, out = run([sys.executable, "tools/pre-report-gate.py", "--repo", ".", "--round", "71",
                   "--tip", "master"], D)
    print(f"--- {label}: gate exit={rc}")
    for ln in out.splitlines():
        print("   ", ln[:300])
    return rc, out


def main():
    sha, lines, observed = patch_citations()
    print(f"fixture PROVINCE sha256={sha} lines={lines} coverage_count={observed}")
    rc, out = run([sys.executable, "tools/round42-selfdesc-reconcile.py", "--repo", ".",
                   "--tip", "master"], D)
    print(f"reconciler WITH citation: exit={rc}")
    for ln in out.splitlines():
        print("   ", ln[:220])
    gate("A: row cites the gate")

    text = SC.read_text(encoding="utf-8")
    if CITE not in text:
        print("CITATION CLAUSE NOT FOUND — aborting variant B")
        return 1
    SC.write_text(text.replace(CITE, "", 1), encoding="utf-8")
    rc, out = run([sys.executable, "tools/round42-selfdesc-reconcile.py", "--repo", ".",
                   "--tip", "master"], D)
    print(f"reconciler WITHOUT citation: exit={rc}")
    for ln in out.splitlines():
        print("   ", ln[:220])
    rc, out = gate("B: row without the gate citation")
    # restore
    SC.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
