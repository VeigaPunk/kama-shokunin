#!/usr/bin/env python3
"""Field-by-field comparison of C1 receipts.

Volatile fields (pids, ports, inodes, nonces) differ by design and are
normalised away; every other field must agree exactly.
"""
import re
import sys

VOLATILE = [
    (re.compile(r"\bpid \d+"), "pid <N>"),
    (re.compile(r"\bport \d+"), "port <N>"),
    (re.compile(r"inode \d+"), "inode <N>"),
    (re.compile(r"nonce '[^']*'"), "nonce '<X>'"),
    (re.compile(r"00:01:\d+"), "00:01:<N>"),
    (re.compile(r"seals \d+"), "seals <N>"),
    (re.compile(r"dev \S+"), "dev <D>"),
]


def norm(text):
    for rx, rep in VOLATILE:
        text = rx.sub(rep, text)
    return text


def load(path):
    with open(path) as fh:
        return fh.read().rstrip("\n").split("\n")


def leg_line(lines):
    return lines[1]


def detail_map(lines):
    out = {}
    for ln in lines[2:]:
        if not ln.startswith("detail: "):
            continue
        body = ln[len("detail: "):]
        key, _, rest = body.partition(": ")
        out.setdefault(key, []).append(rest)
    return out


def compare(a_path, b_path, label_a, label_b):
    a, b = load(a_path), load(b_path)
    print(f"### {label_a}  vs  {label_b}")
    print(f"  A: {a_path}")
    print(f"  B: {b_path}")
    na, nb = norm("\n".join(a)), norm("\n".join(b))
    la, lb = leg_line(a), leg_line(b)
    print(f"  leg line A: {la}")
    print(f"  leg line B: {lb}")
    print(f"  leg line (normalised) equal: {na.split(chr(10))[1] == nb.split(chr(10))[1]}")
    da, db = detail_map(a), detail_map(b)
    keys = sorted(set(da) | set(db))
    bad = 0
    for k in keys:
        va = [norm(x) for x in da.get(k, [])]
        vb = [norm(x) for x in db.get(k, [])]
        if va != vb:
            bad += 1
            print(f"  DIFF detail[{k}]:")
            for x in va:
                print(f"    A: {x}")
            for x in vb:
                print(f"    B: {x}")
        else:
            print(f"  same detail[{k}]: {len(va)} entr(ies)")
    # tip line
    print(f"  tip line A: {a[0]}")
    print(f"  tip line B: {b[0]}")
    print(f"  detail keys equal set: {set(da)==set(db)}  differing keys: {bad}")
    print(f"  whole receipt (normalised) equal: {na == nb}")
    print()
    return bad, na == nb


def main():
    problems = 0
    for pair in sys.argv[1:]:
        a, b, la, lb = pair.split("|", 3)
        bad, _ = compare(a, b, la, lb)
        problems += bad
    print(f"TOTAL differing non-volatile detail groups: {problems}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
