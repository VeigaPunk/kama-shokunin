#!/usr/bin/env python3
"""M2Ctr function-level divergence harness for the counter's own binder.

Loads pristine.py and selected mutants as modules and compares token/says/binds
on crafted inputs. A divergence is the behavioral core of a proposed killing
case for a mutant that survives the golden pair (tip/base).
"""
import importlib.util
import os
import sys

S = "/fast/scratch/hyaku/kama-r49/M2Ctr"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


CASES = [
    # (label, text, pattern, decl_path)
    ("wild self-decl, text lacks dir token", "this file is append-only", "notes/*.md", "notes/a.md"),
    ("wild named decl, names dir", "files under notes/ are append-only", "notes/*.md", "README.md"),
    ("substring: catalog", "the catalog is append-only", "LOG.md", "NOTES.md:1"),
    ("v4-bound word token", "LOG.md is append-only", "LOG.md", "NOTES.md"),
    ("v3-binds negation (not strictly)", "SCORE.md is not strictly append-only", "SCORE.md", "NOTES.md"),
    ("negation gap 3 (v4 unbinds)", "SCORE.md is not in the least append-only", "SCORE.md", "NOTES.md"),
    ("negation gap 4 (v4 binds)", "SCORE.md is not in the least bit append-only", "SCORE.md", "NOTES.md"),
    ("negation gap 5 (v4 binds)", "SCORE.md is not in a way that is append-only", "SCORE.md", "NOTES.md"),
    ("negation via nor", "LOG.md is stale nor append-only anymore", "LOG.md", "NOTES.md"),
    ("negation via non", "a non append-only file is LOG.md", "LOG.md", "NOTES.md"),
    ("spaced never append only", "this file is never append only, LOG.md", "LOG.md", "NOTES.md"),
    ("NEG3 'no longer append' no only", "LOG.md does no longer append; it is append-only", "LOG.md", "NOTES.md"),
    ("token without extension (log)", "the log is append-only", "LOG.md", "NOTES.md"),
    ("digit-suffixed token (log2)", "the log2 is append-only", "LOG.md", "NOTES.md"),
    ("underscore-preceded token", "my_log is append-only", "LOG.md", "NOTES.md"),
    ("token in wildcard-parent form", "notes is append-only", "notes/*.md", "README.md"),
    ("apostrophe middle word", "LOG.md: not don't stop append-only", "LOG.md", "NOTES.md"),
    ("plain negative control", "nothing to see here", "LOG.md", "NOTES.md"),
]


def main():
    pris = load(os.path.join(S, "pristine.py"), "pristine")
    names = sys.argv[1:] or [f[:-3] for f in sorted(os.listdir(os.path.join(S, "mut")))]
    print(f"{'mutant':24s} {'case':40s} pristine -> mutant   (token/says/binds)")
    for name in names:
        mut = load(os.path.join(S, "mut", name + ".py"), name)
        for label, text, pat, decl in CASES:
            tp, sp, bp = pris.token(pat), pris.says(text.lower()), pris.binds(text, pat, decl)
            tm, sm, bm = mut.token(pat), mut.says(text.lower()), mut.binds(text, pat, decl)
            if (tp, sp, bp) != (tm, sm, bm):
                print(f"{name:24s} {label:40s} tok={tp!r}-> {tm!r}  says={sp}->{sm}  binds={bp}->{bm}")


if __name__ == "__main__":
    main()
