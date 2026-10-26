#!/usr/bin/env python3
"""Round-44 L1 integration: merge seat fragments into the claim ledgers and
compare them with the independent attack seats.

  merge.py c1 -> writes registry/release-recheck-b11889.tsv candidate to stdout
               dir and prints executor-vs-critic disagreements
  merge.py c2 -> same for registry/verdict-ledger.tsv vs reviewer verdicts

Fragments: w1/out/X1R*/fragment.tsv (c1), w1/out/X2V*/fragment.tsv (c2).
Attack tables: w1/out/K1J*/verdicts.tsv (c1: id verdict release_lines reason),
w1/out/R2A*/verdicts.tsv (c2: round trend side verdict line reason).
Draft rows fill any key no fragment carries (reported as `draft-kept`).
"""
import glob
import os
import sys

WD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(WD, "w1", "out")


def tsv(path):
    rows = [x.rstrip("\n").split("\t") for x in open(path) if x.strip()]
    return rows[0], rows[1:]


def merge(claim):
    nkey = 1 if claim == "c1" else 3
    hdr, draft = tsv(os.path.join(WD, claim, "draft-ledger.tsv"))
    pat = "X1R*" if claim == "c1" else "X2V*"
    got, src = {}, {}
    for f in sorted(glob.glob(os.path.join(OUT, pat, "fragment.tsv"))):
        h, rows = tsv(f)
        if h != hdr:
            print(f"# header mismatch {f}", file=sys.stderr)
            continue
        for r in rows:
            k = tuple(r[:nkey])
            if k in got and got[k] != r:
                print(f"# conflict {k} {src[k]} vs {f}", file=sys.stderr)
            got[k], src[k] = r, os.path.basename(os.path.dirname(f))
    out = [hdr]
    kept = []
    for r in draft:
        k = tuple(r[:nkey])
        if k in got:
            out.append(got.pop(k))
        else:
            out.append(r)
            kept.append(k)
    for k, r in got.items():
        print(f"# fragment key not in draft {k}", file=sys.stderr)
    print(f"# draft-kept {len(kept)}: {kept}", file=sys.stderr)
    return out, src


def attacks(claim, ledger):
    nkey = 1 if claim == "c1" else 3
    led = {tuple(r[:nkey]): r for r in ledger[1:]}
    pat = "K1J*" if claim == "c1" else "R2A*"
    vcol = 1 if claim == "c1" else 3
    lvcol = 9 if claim == "c1" else 3
    dis = []
    for f in sorted(glob.glob(os.path.join(OUT, pat, "verdicts.tsv"))):
        rows = [x.rstrip("\n").split("\t") for x in open(f) if x.strip()]
        for r in rows[1:] if rows and not rows[0][0].startswith(("S", "1", "2", "3", "4")) else rows:
            if len(r) <= vcol:
                continue
            k = tuple(r[:nkey])
            if k not in led:
                continue
            a, b = r[vcol].strip(), led[k][lvcol]
            if a != b:
                dis.append((k, b, a, os.path.basename(os.path.dirname(f)), r[-1][:200]))
    return dis


def main():
    claim = sys.argv[1]
    out, src = merge(claim)
    dest = sys.argv[2] if len(sys.argv) > 2 else None
    if dest:
        open(dest, "w").write("\n".join("\t".join(r) for r in out) + "\n")
    for d in attacks(claim, out):
        print("DISAGREE", *d, sep="\t")


if __name__ == "__main__":
    main()
