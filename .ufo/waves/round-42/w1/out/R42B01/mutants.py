#!/usr/bin/env python3
"""Harness positive control: three mutants of tools/digest-ledger.py.

Each mutant must make the fuzz harness report mismatches; a harness that
reports 0 mismatches against the real tool is only evidence if it can see a
divergence.
"""
import os

CLONE = "/fast/scratch/kama-r42/seats/R42B01/clone/tools/digest-ledger.py"
OUT = "/fast/scratch/kama-r42/seats/R42B01/mutants"
src = open(CLONE).read()

MUTANTS = {
    # blob tokens counted as unknown instead
    "mut-blob": ('            n["blob"] += 1', '            n["unknown"] += 1'),
    # never fail
    "mut-exit": ('    return 1 if n["ledger_bad"] + n["wrong_unflagged"] + n["unknown"] else 0',
                 '    return 0'),
    # accept upper-case hex as tokens
    "mut-upper": ('TOKEN = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")',
                  'TOKEN = re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])")'),
    # treat .tsv files as non-documents
    "mut-tsv": ('    return not rel.startswith(".ufo/") and rel != LEDGER and rel.endswith((".md", ".tsv"))',
                '    return not rel.startswith(".ufo/") and rel != LEDGER and rel.endswith(".md")'),
}

os.makedirs(OUT, exist_ok=True)
for name, (old, new) in MUTANTS.items():
    assert src.count(old) == 1, (name, src.count(old))
    path = os.path.join(OUT, name + ".py")
    with open(path, "w") as f:
        f.write(src.replace(old, new))
    print(path)
