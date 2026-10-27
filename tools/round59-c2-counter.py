#!/usr/bin/env python3
"""Round-59 calibration counter: re-derive closure metadata from the measured tree."""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROW = re.compile(r"^\|\s*(?:\*\*)?calibration(?:\*\*)?\s*\|", re.I)
SPOT = re.compile(r"^corpus/lessons/round-(\d+)-verifier-spotcheck\.md$")
POINTER = re.compile(r"latest outside closure `corpus/lessons/round-(\d+)-verifier-spotcheck\.md` \(([^)]+)\)")
INCL = re.compile(r"including round (\d+)")


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True)


def axes_row(text):
    inside = False
    for line in text.splitlines():
        if line.startswith("## "):
            if inside:
                break
            inside = line.strip() == "## Axes"
        elif inside and ROW.match(line):
            return line
    return ""


def evaluate(repo, tip, fleet, fleet_ref):
    rev = git(repo, "rev-parse", "--verify", f"{tip}^{{commit}}")
    frev = git(fleet, "rev-parse", "--verify", f"{fleet_ref}^{{commit}}")
    if rev.returncode or frev.returncode:
        raise ValueError("unresolvable lane tip or fleet ref")
    tip, frev = rev.stdout.decode().strip(), frev.stdout.decode().strip()
    sc = git(repo, "show", f"{tip}:SCORECARD.md")
    tree = git(repo, "ls-tree", "--name-only", tip, "corpus/lessons/")
    man = git(fleet, "show", f"{frev}:MANIFEST.json")
    if sc.returncode or tree.returncode or man.returncode:
        raise ValueError("missing SCORECARD, lessons tree, or MANIFEST")
    try:
        rounds = json.loads(man.stdout)["rounds"]
    except (ValueError, KeyError, TypeError) as exc:
        raise ValueError("MANIFEST unreadable") from exc
    names = [p for p in tree.stdout.decode().splitlines() if SPOT.fullmatch(p)]
    nums = [int(SPOT.fullmatch(p).group(1)) for p in names]
    if not nums:
        raise ValueError("no verifier-spotcheck files")
    maxn = max(nums)
    row = axes_row(sc.stdout.decode("utf-8", "replace"))
    pointer = POINTER.search(row)
    including = INCL.search(row)
    closures = [r for r in rounds if r.get("type") == "closure" and r.get("lane") == "kama"
                and r.get("lane_round") == maxn]
    verdict = closures[-1].get("verdict") if closures else None
    typed_count = bool(re.search(r"\b\d+`?\s+\(outside closures on record", row))
    pinned_rev = bool(re.search(r"\b[0-9a-f]{40}\b", row))
    count_command = "tools/round59-c2-counter.py" in row and "--fleet-ref" in row
    mismatches = {
        "row_missing": int(not row),
        "typed_count": int(typed_count),
        "pinned_fleet_revision": int(pinned_rev),
        "pointer_missing": int(pointer is None),
        "pointer_round": int(pointer is not None and int(pointer.group(1)) != maxn),
        "pointer_verdict": int(pointer is not None and (verdict is None or pointer.group(2) != verdict)),
        "including_round": int(including is None or int(including.group(1)) != maxn),
        "count_command": int(not count_command),
    }
    return tip, frev, maxn, verdict, mismatches


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--fleet-repo", default="/home/vgpnk/Projects/shokunin")
    ap.add_argument("--fleet-ref", default="HEAD")
    ap.add_argument("--out")
    a = ap.parse_args()
    try:
        tip, frev, maxn, verdict, mismatches = evaluate(a.repo, a.tip, a.fleet_repo, a.fleet_ref)
    except ValueError as exc:
        print(f"could-not-evaluate: {exc}")
        return 2
    total = sum(mismatches.values())
    text = (f"tip={tip} fleet={frev} maxN={maxn} manifest={verdict}\n"
            f"rows={len([p for p in git(a.repo, 'ls-tree', '--name-only', tip, 'corpus/lessons/').stdout.decode().splitlines() if SPOT.fullmatch(p)])} "
            f"mismatches={total} met={total == 0}\n" +
            " ".join(f"{k}={v}" for k, v in mismatches.items()) + "\n")
    print(text, end="")
    if a.out:
        Path(a.out).write_text(text)
    return 0 if total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
