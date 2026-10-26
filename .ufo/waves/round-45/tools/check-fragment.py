#!/usr/bin/env python3
"""Round-45 seat helper: score a ledger fragment with the frozen counter.

  check-fragment.py c1|c2 <fragment.tsv> <scratch dir>

The fragment is a TSV with the claim's exact ledger header line and only the
rows the seat owns. The helper clones the lane (git clone --shared) into
<scratch>/clone at the freeze commit, writes the fragment as the claim's ledger,
copies into the clone every lane-relative evidence path the C1 fragment names
(pin_copy, new_copy files, or the live receipt directory) from the lane working
tree, commits inside that clone only (fixture identity; isolation checked), runs
the frozen counter, and prints the counter's summary line plus the detail lines
for the fragment's keys; a key with no detail prints `VALID <key>`.
C1 keys that need registry rows (newrows, flags) are not scored here: only the
per-key detail lines matter for a fragment. The clone is removed on exit.
Never run it with <scratch> inside the lane.
"""
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FREEZE = "1641aa076647754b0b6b7017cd4a86b7501ecb8c"
FLEET = "/home/vgpnk/Projects/shokunin"
SPEC = {
    "c1": ("registry/recheck-r45.tsv", "tools/round45-recheck-audit.py", [], 1),
    "c2": ("registry/claim-outcome-ledger.tsv", "tools/round45-claim-outcome-audit.py", ["--fleet", FLEET], 3),
}
HEADERS = {
    "c1": "key\tid\tkind\tpin_ref\tnew_ref\tpin_copy\tnew_copy\twitness_pin\twitness_new\tclass\tnote",
    "c2": "round\tclaim\tside\toutcome\trepo\trev\tpath\tline\tnote",
}


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in SPEC:
        print(__doc__)
        return 2
    claim, frag, scratch = sys.argv[1], os.path.abspath(sys.argv[2]), os.path.abspath(sys.argv[3])
    if os.path.realpath(scratch).startswith(os.path.realpath(LANE)):
        print("refusing: scratch inside the lane")
        return 2
    target, counter, extra, nkey = SPEC[claim]
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
        if not fr or fr[0] != HEADERS[claim]:
            print("fragment header differs from the ledger header:\n" + HEADERS[claim])
            return 2
        if claim == "c1":
            for x in fr[1:]:
                f = x.split("\t")
                for rel in (f[5], f[6]) if len(f) > 6 else ():
                    if rel in ("", "-") or rel.startswith("/") or ".." in rel.split("/"):
                        continue
                    src, dst = os.path.join(LANE, rel), os.path.join(d, rel)
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    elif os.path.isfile(src):
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copyfile(src, dst)
        os.makedirs(os.path.dirname(os.path.join(d, target)), exist_ok=True)
        open(os.path.join(d, target), "w").write("\n".join(fr) + "\n")
        subprocess.run(["git", "-C", d, "add", "-A"], check=True)
        subprocess.run(["git", "-C", d, "-c", "user.name=r45-seat-check", "-c",
                        "user.email=r45-seat-check@fixture.invalid", "commit", "-qm", "fragment check"], check=True)
        tip = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        p = subprocess.run([sys.executable, os.path.join(d, counter), "--repo", d, "--tip", tip, *extra],
                           capture_output=True, text=True)
        lines = p.stdout.splitlines()
        print(next((x for x in lines if "met=" in x), p.stderr.strip()))
        for x in fr[1:]:
            k = tuple(x.split("\t")[:nkey])
            label = k[0] if claim == "c1" else repr(k)
            hits = [y for y in lines if y.startswith("detail: ") and
                    ((claim == "c1" and y.split()[1] == k[0]) or (claim == "c2" and repr(k) in y))]
            print("\n".join(hits) if hits else f"VALID {label}")
        return 0
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
