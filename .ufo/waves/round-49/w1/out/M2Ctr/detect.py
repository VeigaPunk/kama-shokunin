#!/usr/bin/env python3
"""M2Ctr detector: compare each mutant's golden-pair output against pristine."""
import glob
import os

S = "/fast/scratch/hyaku/kama-r49/M2Ctr"


def load(stem):
    with open(os.path.join(S, "runs", stem + ".out"), "rb") as fh:
        out = fh.read()
    with open(os.path.join(S, "runs", stem + ".exit")) as fh:
        code = fh.read().strip()
    return code, out


def sig(v, tag):
    return load(f"{v.replace('/', '_')}.{tag}")


pris = {tag: sig("pristine", tag) for tag in ("tip", "base")}
print(f"pristine tip: exit {pris['tip'][0]}, {len(pris['tip'][1])}B, met={b'met=True' in pris['tip'][1]}")
print(f"pristine base: exit {pris['base'][0]}, {len(pris['base'][1])}B, met={b'met=True' in pris['base'][1]}")
rows = []
for path in sorted(glob.glob(os.path.join(S, "mut", "*.py"))):
    name = os.path.basename(path)[:-3]
    diffs = {}
    for tag in ("tip", "base"):
        c, o = sig(f"mut/{name}", tag)
        if (c, o) != pris[tag]:
            pc, po = pris[tag]
            kind = "crash" if c not in ("0", "1", "2") or b"Traceback" in o else (
                f"exit {pc}->{c}" if c != pc else "text")
            diffs[tag] = kind
    rows.append((name, diffs))
    print(f"{name:28s} " + ("KILLED  " + ",".join(f"{t}:{k}" for t, k in diffs.items())
                             if diffs else "survived (goldens identical)"))
killed = sum(1 for _, d in rows if d)
print(f"\n{killed}/{len(rows)} killed by the golden pair")
