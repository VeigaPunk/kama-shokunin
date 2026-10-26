#!/usr/bin/env python3
"""Round-46 seat helper: score a C1 ledger fragment with the frozen counter.

  check-fragment.py <fragment.tsv> <scratch dir> [<llama.cpp clone>]

The fragment is a TSV with the exact C1 ledger header line (13 columns) and only
the rows the seat owns. The helper clones the lane (git clone --shared) into
<scratch>/clone at the freeze commit, writes the fragment as
registry/release-recheck-b11906.tsv, commits inside that clone only (fixture
identity; isolation checked), runs the frozen counter
tools/round46-release-recheck-audit.py against the llama.cpp clone (default: the
L1's read-only bare clone below; it holds every pin and b11906), and prints, for
each fragment id, `VALID <id> <verdict>` or the counter's reason. Section,
newrow and flags legs are not scored here. The clone is removed on exit.
Never run it with <scratch> inside the lane.
"""
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FREEZE = "5790944350ae41bfe2ce50934bba59e086e747f4"
UPSTREAM = "/fast/scratch/hyaku/kama-r46/L1/llama.git"
LEDGER = "registry/release-recheck-b11906.tsv"
COUNTER = "tools/round46-release-recheck-audit.py"
HEADER = "\t".join(["id", "path", "pin_commit", "release", "pin_blob", "release_blob", "changed", "pin_lines",
                    "release_lines", "witness_pin", "witness_new", "verdict", "note"])


def main():
    if len(sys.argv) not in (3, 4):
        print(__doc__)
        return 2
    frag, scratch = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    up = sys.argv[3] if len(sys.argv) == 4 else UPSTREAM
    if os.path.realpath(scratch).startswith(os.path.realpath(LANE)):
        print("refusing: scratch inside the lane")
        return 2
    d = os.path.join(scratch, "clone")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(scratch, exist_ok=True)
    try:
        subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", LANE, d], check=True)
        subprocess.run(["git", "-C", d, "checkout", "-q", "--detach", FREEZE], check=True)
        top = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True).stdout.strip()
        if os.path.realpath(top) != os.path.realpath(d):
            print("isolation check failed")
            return 2
        fr = [x for x in open(frag).read().splitlines() if x.strip()]
        if not fr or fr[0] != HEADER:
            print("fragment header differs from the ledger header:\n" + HEADER)
            return 2
        ids = [x.split("\t")[0] for x in fr[1:]]
        verdict = {x.split("\t")[0]: (x.split("\t")[11] if len(x.split("\t")) > 11 else "?") for x in fr[1:]}
        os.makedirs(os.path.dirname(os.path.join(d, LEDGER)), exist_ok=True)
        open(os.path.join(d, LEDGER), "w").write("\n".join(fr) + "\n")
        subprocess.run(["git", "-C", d, "add", "-A"], check=True)
        subprocess.run(["git", "-C", d, "-c", "user.name=r46-seat-check", "-c",
                        "user.email=r46-seat-check@fixture.invalid", "-c", "commit.gpgsign=false",
                        "commit", "-qm", "fragment check"], check=True)
        tip = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        p = subprocess.run([sys.executable, os.path.join(d, COUNTER), "--repo", d, "--tip", tip, "--upstream", up],
                           capture_output=True, text=True)
        lines = p.stdout.splitlines()
        if p.returncode == 2:
            print("counter could not evaluate:", p.stderr.strip()[:300])
            return 2
        for i in ids:
            hits = [x for x in lines if x.startswith(f"detail: {i} ")]
            print("\n".join(hits) if hits else f"VALID {i} {verdict.get(i)}")
        bad = ["bad ledger line", "ledger header mismatch"]
        for x in lines:
            if any(b in x for b in bad):
                print(x)
        return 0
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
