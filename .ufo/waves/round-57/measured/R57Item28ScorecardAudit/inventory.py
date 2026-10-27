#!/usr/bin/env python3
"""case49-inventory.py -- inventory of SCORECARD calibration assertions at a tip.

Reads SCORECARD.md at a git tip (never the working tree) and prints, for each
calibration-relevant assertion, the asserted token beside the derivation the
SCORECARD itself names.  Read-only.

  usage: case49-inventory.py <lane-repo> <tip>
"""
import re
import subprocess
import sys


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)}: {p.stderr.strip()}")
    return p.stdout


def main():
    repo, tip = sys.argv[1], sys.argv[2]
    tip = git(repo, "rev-parse", "--verify", tip + "^{commit}").strip()
    sc = git(repo, "show", f"{tip}:SCORECARD.md")
    lines = sc.split("\n")
    rounds = [int(m.group(1)) for l in lines for m in [re.match(r"^## Round (\d+)", l)] if m]
    print(f"tip={tip}")
    print(f"round_headings={len(rounds)} distinct_rounds={len(set(rounds))} maxN={max(rounds)}")
    for i, l in enumerate(lines, 1):
        if "maxN=46" in l:
            print(f"literal_maxN46_at_line={i}")
    canon = [(int(m.group(1)), i) for i, l in enumerate(lines, 1)
             for m in [re.search(r"canonical list as of round\s+(\d+)\*\*", l, re.I)] if m]
    top_round, top_line = max(canon)
    rows = 0
    for l in lines[top_line:]:
        if l.startswith("|"):
            rows += 1
        elif rows:
            break
    print(f"canon_highest_round={top_round} canon_table_line={top_line} "
          f"canon_rows={rows - 2} canon_tables={len(canon)}")
    calib = next(l for l in lines if l.startswith("| calibration |"))
    spot = re.search(r"verifier-spotcheck\.md'\)\)\)\"`\s*→\s*`(\d+)`", calib)
    print(f"calib_claim_spotcheck={spot.group(1) if spot else None}")
    for pat in (r"\((\d+) rows, self against outside for rounds 10–43",
                r"agreement=([\d/]+ overclaim=\d+ underclaim=\d+ other=\d+ absent=\d+)",
                r"\((\d+) rows, the (\d+) claims of rounds 10–44",
                r"agreement=([\d/]+ overclaim=\d+ underclaim=\d+ other=\d+ absent=\d+)"):
        for m in re.finditer(pat, calib):
            print("calib_token:", " ".join(m.groups()))
    sat = next(l for l in lines if l.startswith("Saturation line"))
    m = re.search(r"kept current in round (\d+)", sat)
    print(f"saturation_kept_current_round={m.group(1) if m else None} vs maxN={max(rounds)}")
    retired = next(l for l in lines if l.startswith("None. 6 axes"))
    print("retired_line:", retired[:120])
    print(f"latest_outside_closure_round56_blob="
          f"{git(repo, 'cat-file', '-e', f'{tip}:corpus/lessons/round-56-verifier-spotcheck.md').strip() or 'exists'}")


if __name__ == "__main__":
    main()
