#!/usr/bin/env python3
"""Round-44 seat helper: score a ledger fragment with the frozen counter.

  check-fragment.py c1|c2 <fragment.tsv> <scratch dir>

The fragment is a TSV with the claim's ledger header and only the rows the seat
owns. The helper clones the lane (git clone --shared) into <scratch>/clone at
the freeze commit, writes the round's draft ledger with the fragment's rows
replacing the draft rows of the same key, commits inside that clone only
(fixture identity; isolation checked), runs the frozen counter, and prints the
counter's summary line plus the detail lines for the fragment's keys. Rows the
seat owns print `VALID <key>` when the counter reports no detail for them.
The clone is removed on exit. Never run it with <scratch> inside the lane.
"""
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FREEZE = "77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40"
UP = "/fast/scratch/hyaku/kama-r44/shared/llama.cpp"
FLEET = "/home/vgpnk/Projects/shokunin"
SPEC = {
    "c1": ("registry/release-recheck-b11889.tsv", ".ufo/waves/round-44/c1/draft-ledger.tsv",
           "tools/round44-release-recheck-audit.py", ["--upstream", UP], 1),
    "c2": ("registry/verdict-ledger.tsv", ".ufo/waves/round-44/c2/draft-ledger.tsv",
           "tools/round44-verdict-ledger-audit.py", ["--fleet", FLEET], 3),
}


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in SPEC:
        print(__doc__)
        return 2
    claim, frag, scratch = sys.argv[1], os.path.abspath(sys.argv[2]), os.path.abspath(sys.argv[3])
    if os.path.realpath(scratch).startswith(os.path.realpath(LANE)):
        print("refusing: scratch inside the lane")
        return 2
    target, draft, counter, extra, nkey = SPEC[claim]
    d = os.path.join(scratch, "clone")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(scratch, exist_ok=True)
    try:
        subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", LANE, d], check=True)
        subprocess.run(["git", "-C", d, "checkout", "-q", FREEZE], check=True)
        top = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True).stdout.strip()
        if os.path.realpath(top) != os.path.realpath(d):
            print("isolation check failed")
            return 2
        base = open(os.path.join(LANE, draft)).read().splitlines()
        fr = [x for x in open(frag).read().splitlines() if x.strip()]
        if not fr or fr[0] != base[0]:
            print("fragment header differs from the ledger header:\n" + base[0])
            return 2
        key = lambda x: tuple(x.split("\t")[:nkey])
        mine = {key(x): x for x in fr[1:]}
        out = [base[0]] + [mine.pop(key(x), x) for x in base[1:]] + list(mine.values())
        os.makedirs(os.path.dirname(os.path.join(d, target)), exist_ok=True)
        open(os.path.join(d, target), "w").write("\n".join(out) + "\n")
        subprocess.run(["git", "-C", d, "add", "-A"], check=True)
        subprocess.run(["git", "-C", d, "-c", "user.name=r44-seat-check", "-c",
                        "user.email=r44-seat-check@fixture.invalid", "commit", "-qm", "fragment check"], check=True)
        tip = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        p = subprocess.run([sys.executable, os.path.join(d, counter), "--repo", d, "--tip", tip, *extra],
                           capture_output=True, text=True)
        lines = p.stdout.splitlines()
        print(lines[1] if len(lines) > 1 else p.stderr.strip())
        keys = [key(x) for x in fr[1:]]
        for k in keys:
            label = k[0] if claim == "c1" else repr(k)
            hits = [x for x in lines if x.startswith("detail: ") and
                    ((claim == "c1" and x.split()[1] == k[0]) or (claim == "c2" and repr(k) in x))]
            print("\n".join(hits) if hits else f"VALID {label}")
        return 0
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
