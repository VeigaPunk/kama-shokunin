#!/usr/bin/env python3
"""Compare my independent receipts with the L1's battery receipts, line by line.

Volatile values (pids, ports, inodes, nonces, tmp dir names, scratch prefixes,
commit tips) are normalized; anything else that differs is reported as a
divergence with the exact two lines.
"""
import os
import re
import sys

L1 = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/c1/battery"
MINE = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X7BatteryReplay"
NAMES = ["control", "m-ldpreload", "m-text-flip", "m-member-flip", "m-ldaudit-foreign"]


def norm(text, scratch):
    t = text
    t = t.replace(scratch, "<SCRATCH>")
    t = re.sub(r"r53c1-[a-z0-9_]+", "<TMPDIR>", t)
    t = re.sub(r"^tip=[0-9a-f]{40}$", "tip=<TIP>", t, flags=re.M)
    t = re.sub(r"pid \d+", "pid <PID>", t)
    t = re.sub(r"port \d+", "port <PORT>", t)
    t = re.sub(r"inode \d+", "inode <INODE>", t)
    t = re.sub(r"\b\d{6,}\b", "<NUM>", t)
    t = re.sub(r"nonce '[^']*'", "nonce <NONCE>", t)
    t = re.sub(r"0[0-9]:[0-9]{2,5}", "<DEV>", t)
    t = re.sub(r"dev [0-9]+:[0-9]+", "dev <DEV>", t)
    t = re.sub(r"digest [0-9a-f]{64}", "digest <SHA>", t)
    t = re.sub(r"!= [0-9a-f]{64}", "!= <SHA>", t)
    t = re.sub(r"\b[0-9a-f]{64}\b", "<SHA>", t)
    return t


def main():
    scratch = sys.argv[1] if len(sys.argv) > 1 else "/fast/scratch/hyaku/kama-r55/c1/battery"
    mine_scratch = sys.argv[2] if len(sys.argv) > 2 else "/fast/scratch/hyaku/kama-r55/w1/X7BatteryReplay"
    bad = 0
    for name in NAMES:
        a = os.path.join(L1, f"{name}.out")
        b = os.path.join(MINE, f"{name}.out")
        if not (os.path.isfile(a) and os.path.isfile(b)):
            print(f"== {name}: MISSING receipt (l1={os.path.isfile(a)} mine={os.path.isfile(b)})")
            bad += 1
            continue
        la = norm(open(a).read(), scratch).splitlines()
        lb = norm(open(b).read(), mine_scratch).splitlines()
        # detail line order differs between runs (leg ordering is stable, but detail
        # blocks per run are emitted in leg order); compare as multisets of
        # normalized lines AND report the first-line (summary) difference.
        print(f"== {name}: l1_lines={len(la)} mine_lines={len(lb)}")
        if la[0] != lb[0]:
            print(f"   SUMMARY-TIP differs (expected: different fixture commits)")
        if la[1] != lb[1]:
            print(f"   VERDICT DIVERGENCE\n     l1  : {la[1]}\n     mine: {lb[1]}")
            bad += 1
        from collections import Counter
        ca, cb = Counter(la[2:]), Counter(lb[2:])
        only_a = ca - cb
        only_b = cb - ca
        if only_a or only_b:
            print(f"   detail divergence: {sum(only_a.values())} l1-only, {sum(only_b.values())} mine-only")
            for ln, n in sorted(only_a.items()):
                print(f"     L1-ONLY (x{n}): {ln}")
            for ln, n in sorted(only_b.items()):
                print(f"     MINE-ONLY (x{n}): {ln}")
        else:
            print("   details identical after normalization")
    print(f"\nverdict divergences: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
