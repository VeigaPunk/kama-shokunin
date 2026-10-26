#!/usr/bin/env python3
"""Merge seat fragments into the round-45 ledgers (L1 integration helper).

  merge_rows.py c1 <out>/<seat>/row(s).tsv ... > registry/recheck-r45.tsv
  merge_rows.py c2 <out>/<seat>/rows.tsv ...   > registry/claim-outcome-ledger.tsv

Rows keep the counter's population order; a key present in two fragments is an
error (the L1 resolves it by hand), a key missing from all fragments is listed
on stderr.
"""
import importlib.util
import sys

L = "/home/vgpnk/Projects/shokunin/kama-shokunin"


def load(path):
    spec = importlib.util.spec_from_file_location("m", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    claim, frags = sys.argv[1], sys.argv[2:]
    if claim == "c1":
        m = load(f"{L}/tools/round45-recheck-audit.py")
        keys = list(m.POP)
        kf = lambda f: f[0]
    else:
        m = load(f"{L}/tools/round45-claim-outcome-audit.py")
        keys = [(r, c, s) for r, c in m.KEYS for s in ("self", "outside")]
        kf = lambda f: tuple(f[:3])
    rows, src = {}, {}
    for fp in frags:
        ls = [x for x in open(fp).read().splitlines() if x.strip()]
        if not ls or ls[0].split("\t") != m.HEADER:
            sys.exit(f"{fp}: header mismatch")
        for x in ls[1:]:
            f = x.split("\t")
            k = kf(f)
            if k in rows and rows[k] != x:
                sys.exit(f"conflict {k}: {src[k]} vs {fp}")
            rows[k], src[k] = x, fp
    out = ["\t".join(m.HEADER)]
    for k in keys:
        if k in rows:
            out.append(rows[k])
        else:
            print(f"missing {k}", file=sys.stderr)
    extra = set(rows) - set(keys)
    for k in sorted(extra):
        print(f"extra {k} from {src[k]}", file=sys.stderr)
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
