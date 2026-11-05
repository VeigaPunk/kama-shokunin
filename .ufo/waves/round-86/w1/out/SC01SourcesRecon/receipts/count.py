#!/usr/bin/env python3
"""Frozen round-86 counting command (kama r86). Three claims, one entry point each.

  c1  calibration  rendered-cell identity of the live self-assessment cells
  c2  operability  mutant -> owning-arm map plus summary/failure-line cardinality
  c3  freshness    pin-recheck rows corroborated against live source bytes

Every leg reads committed bytes at --rev and delegates to the committed instrument; the
counter prints the instrument's own verdict line unchanged so the plan, the counter and
the receipt carry the same sentence.
"""
import argparse
import pathlib
import subprocess
import sys

# c3's subject is the capability itself: at a revision where the instrument is not
# committed the leg is could-not-evaluate (exit 2), never a green re-measurement.
REQUIRES_AT_REV = {"c3": "tools/round86-pin-origin.py"}

LEGS = {
    "c1": ("tools/round86-rendered-cells.py", ["--repo", "{repo}", "--rev", "{rev}"]),
    "c2": ("tools/round86-mutant-owners.py", ["--repo", "{repo}", "--rev", "{rev}",
                                             "--work", "{work}/mutants"]),
    "c3": ("tools/round86-pin-origin.py", ["--repo", "{repo}", "--rev", "{rev}",
                                           "--rows", "registry/pin-recheck-rows.tsv"]),
}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("claim", choices=sorted(LEGS))
    parser.add_argument("--repo", default=".")
    parser.add_argument("--rev", default="master")
    parser.add_argument("--work", required=True)
    args = parser.parse_args(argv)
    pathlib.Path(args.work).mkdir(parents=True, exist_ok=True)
    required = REQUIRES_AT_REV.get(args.claim)
    if required is not None:
        present = subprocess.run(["git", "-C", str(pathlib.Path(args.repo).resolve()),
                                  "cat-file", "-e", f"{args.rev}:{required}"],
                                 capture_output=True).returncode == 0
        if not present:
            print(f"could-not-evaluate: no {required} at {args.rev}", file=sys.stderr)
            return 2
    script, tail = LEGS[args.claim]
    command = [sys.executable, str(pathlib.Path(args.repo).resolve() / script)] + [
        cell.format(repo=args.repo, rev=args.rev, work=args.work) for cell in tail]
    run = subprocess.run(command, text=True, capture_output=True,
                         env={"TMPDIR": args.work, "PATH": "/usr/local/bin:/usr/bin:/bin"})
    sys.stdout.write(run.stdout)
    sys.stderr.write(run.stderr)
    return run.returncode


if __name__ == "__main__":
    sys.exit(main())
