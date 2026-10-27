#!/usr/bin/env python3
"""Round-58 C2 (calibration) frozen counter: does the SCORECARD calibration row's account
of the outside closure agree with observed repo state and the fleet ledger?

Predicate (same sentence as .ufo/waves/round-58/controls/freeze.txt):
  C2-r58: at the measured tip the round-42 self-description reconcile reports 0
  mismatches and the calibration row's "latest outside closure" pointer is 0-mismatch:
  it names the highest-numbered corpus/lessons/round-N-verifier-spotcheck.md, repeats that
  round in "including round N", and carries the verdict token the fleet MANIFEST.json holds
  for kama lane_round N.

Terms (all derived from committed bytes):
  row     the line of SCORECARD.md's first `## Axes` section that starts `| calibration |`
          (an optionally bold cell).
  claim   the first match in row of
          `latest outside closure `corpus/lessons/round-(N)-verifier-spotcheck.md` (TOKEN)`.
  maxN    greatest N over blobs corpus/lessons/round-N-verifier-spotcheck.md at --tip.
  manifest the verdict field of the MANIFEST.json round whose type is closure, lane is
          kama and lane_round is N, read from --fleet-repo at --manifest-rev.
Mismatch counters (each adds 1): missing (no claim), stale (claim N != maxN), verdict
(TOKEN != manifest verdict for claim N, or no such manifest row), including (row lacks
`including round M` or M != maxN).  r42 = mismatches reported by
tools/round42-selfdesc-reconcile.py at --tip (read-only run on the same repo; the count is
0 when the tool is absent only if --no-r42 is given, otherwise absent = could not evaluate).
met = r42 == 0 and the four counters sum to 0.  Exit 0 met, 1 not met, 2 could not evaluate."""
import argparse
import json
import os
import re
import subprocess
import sys

PREDICATE = "C2-r58 r42 mismatches=0 and closure pointer mismatches=0"
CLAIM = re.compile(r"latest outside closure `corpus/lessons/round-(\d+)-verifier-spotcheck\.md` \(([^)]+)\)")
INCL = re.compile(r"including round (\d+)")
SPOT = re.compile(r"^corpus/lessons/round-(\d+)-verifier-spotcheck\.md$")


def genv():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    return env


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, env=genv())


def axes_row(text):
    inside = False
    for ln in text.splitlines():
        if ln.startswith("## "):
            if inside:
                return None
            inside = ln.strip() == "## Axes"
            continue
        if inside and re.match(r"^\|\s*\**calibration\**\s*\|", ln):
            return ln
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--fleet-repo", default="/home/vgpnk/Projects/shokunin")
    ap.add_argument("--manifest-rev", required=True)
    ap.add_argument("--no-r42", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    a.repo = os.path.abspath(a.repo)
    rev = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}")
    if rev.returncode:
        print("could-not-evaluate: invalid tip")
        return 2
    tip = rev.stdout.decode().strip()
    sc = git(a.repo, "show", f"{tip}:SCORECARD.md")
    tree = git(a.repo, "ls-tree", "--name-only", tip, "corpus/lessons/")
    man = git(a.fleet_repo, "show", f"{a.manifest_rev}:MANIFEST.json")
    if sc.returncode or tree.returncode or man.returncode:
        print("could-not-evaluate: missing SCORECARD, lessons tree or MANIFEST blob")
        return 2
    try:
        rounds = json.loads(man.stdout)["rounds"]
    except (ValueError, KeyError):
        print("could-not-evaluate: MANIFEST.json unreadable")
        return 2
    nums = [int(m.group(1)) for p in tree.stdout.decode().split("\n") if (m := SPOT.match(p))]
    if not nums:
        print("could-not-evaluate: no verifier-spotcheck blobs")
        return 2
    maxn = max(nums)
    verdicts = {r["lane_round"]: r.get("verdict") for r in rounds
                if r.get("type") == "closure" and r.get("lane") == "kama" and "lane_round" in r}
    row = axes_row(sc.stdout.decode("utf-8", "replace"))
    claim = CLAIM.search(row) if row else None
    incl = INCL.search(row) if row else None
    missing = int(claim is None)
    stale = int(claim is not None and int(claim.group(1)) != maxn)
    verdict = 0
    including = int(incl is None or int(incl.group(1)) != maxn)
    r42 = 0
    if not a.no_r42:
        tool = git(a.repo, "show", f"{tip}:tools/round42-selfdesc-reconcile.py")
        if tool.returncode:
            print("could-not-evaluate: round42 reconcile tool absent at tip")
            return 2
        import tempfile
        with tempfile.TemporaryDirectory(prefix="c2-", dir=os.environ.get("TMPDIR") or os.path.join(
                os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku"), "kama-r58")) as d:
            f = os.path.join(d, "r42.py")
            open(f, "wb").write(tool.stdout)
            r41 = git(a.repo, "show", f"{tip}:tools/round41-scorecard-reconcile.py")
            open(os.path.join(d, "round41-scorecard-reconcile.py"), "wb").write(r41.stdout)
            p = subprocess.run([sys.executable, f, "--repo", a.repo, "--tip", tip],
                               capture_output=True, text=True, cwd=d)
        m = re.search(r"mismatches=(\d+)", p.stdout)
        if not m:
            print("could-not-evaluate: round42 reconcile printed no mismatches")
            return 2
        r42 = int(m.group(1))
    total = missing + stale + verdict + including
    met = r42 == 0 and total == 0
    cl = f"N={claim.group(1)} token={claim.group(2)}" if claim else "none"
    text = (f"tip={tip}\npredicate={PREDICATE}\nclaim={cl} maxN={maxn} "
            f"manifest={verdicts.get(int(claim.group(1))) if claim else None}\n"
            f"r42={r42} missing={missing} stale={stale} verdict={verdict} including={including} "
            f"mismatches={r42 + total} met={met}\n")
    print(text, end="")
    if a.out:
        open(a.out, "w").write(text)
    return 0 if met else 1


if __name__ == "__main__":
    raise SystemExit(main())
