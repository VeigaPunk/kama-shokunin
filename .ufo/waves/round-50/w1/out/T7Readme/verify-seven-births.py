#!/usr/bin/env python3
"""T7Readme verification: births of SCORECARD.md's seven head `## Capabilities` rows.

Read-only on the lane. Imports the build commit's own v5 definitions (key/sections)
from its `tools/append-only-audit.py` blob, so the birth rule used here is the measured
tool's, not a re-implementation.

Usage: TMPDIR=<scratch> python3 verify-seven-births.py [<lane> <build-commit>]
"""
import os
import subprocess
import sys
import tempfile

LANE = sys.argv[1] if len(sys.argv) > 1 else "/home/vgpnk/Projects/shokunin/kama-shokunin"
TIP = sys.argv[2] if len(sys.argv) > 2 else "97c864bead3ee4a2f629574e77263d33834ec98a"
PARENT_REV = "21945c61"          # SCORECARD.md parent of 0718b6abbda6
PARENT_LINES = range(121, 128)   # the seven rows (round-49 README:1149-1153)


def git(*a):
    return subprocess.run(["git", "-C", LANE, *a], capture_output=True, check=True).stdout


def main():
    work = tempfile.mkdtemp(prefix="t7-births-", dir=os.environ.get("TMPDIR"))
    with open(os.path.join(work, "aoa_v5.py"), "wb") as fh:
        fh.write(git("show", f"{TIP}:tools/append-only-audit.py"))
    sys.path.insert(0, work)
    import aoa_v5 as A

    revs = git("rev-list", "--topo-order", "--reverse", "--parents", TIP).decode().split("\n")
    commits, parents = [], {}
    for ln in revs:
        p = ln.split()
        if p:
            commits.append(p[0])
            parents[p[0]] = p[1:]

    pb = git("show", f"{PARENT_REV}:SCORECARD.md").split(b"\n")
    targets = {A.key(l): (i + 1, l) for i, l in enumerate(pb) if (i + 1) in PARENT_LINES}
    if len(targets) != 7:
        raise SystemExit(f"expected 7 rows, read {len(targets)}")

    blob = {}
    for c in commits:
        r = subprocess.run(["git", "-C", LANE, "rev-parse", f"{c}:SCORECARD.md"], capture_output=True)
        blob[c] = r.stdout.decode().strip() if r.returncode == 0 else None
    uniq = sorted({b for b in blob.values() if b})
    raw = subprocess.run(["git", "-C", LANE, "cat-file", "--batch"],
                         input=("\n".join(uniq) + "\n").encode(), capture_output=True, check=True).stdout
    data, pos = {}, 0
    while pos < len(raw):
        nl = raw.index(b"\n", pos)
        hdr = raw[pos:nl].decode().split()
        data[hdr[0]] = raw[nl + 1:nl + 1 + int(hdr[2])]
        pos = nl + 1 + int(hdr[2]) + 1
    lines, keys = {}, {}
    for sha, b in data.items():
        t = b.split(b"\n")
        lines[sha] = t
        keys[sha] = [A.key(x) for x in t]

    found = {k: set() for k in targets}
    for c in commits:
        b = blob[c]
        if b is None:
            continue
        ks = keys[b]
        kset = set(ks)
        pset = set()
        for q in parents[c]:
            qb = blob.get(q)
            if qb is None:
                continue
            if qb == b:
                pset = set(kset)
                break
            pset |= set(keys[qb])
        if pset == kset:
            continue
        secs = A.sections(lines[b])
        for i, kk in enumerate(ks):
            if kk in targets and kk not in pset:
                found[kk].add((c[:8], secs[i]))

    print(f"tip={TIP} parent={PARENT_REV} rows={len(targets)}")
    for k, (ln, text) in sorted(targets.items(), key=lambda kv: kv[1][0]):
        births = sorted(found[k])
        caps = [b for b in births if b[1] == "## Capabilities"]
        print(f"line {ln}: {text[:48].decode(errors='replace')!r} births={len(births)} "
              f"head_birth={[b[0] for b in caps]} all={births}")


if __name__ == "__main__":
    main()
