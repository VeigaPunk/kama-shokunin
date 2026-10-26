#!/usr/bin/env python3
"""V2Tool: NEG_WINDOW backtracking timing + binds() edge cases at tip."""
import importlib.util
import os
import re
import time

S = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("aoa", os.path.join(S, "lane", "tools", "append-only-audit.py"))
aoa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aoa)

print("== NEG_WINDOW timing (worst-ish inputs)")
cases = {
    "one-long-word": "no " + "a" * 400000 + " append-only",
    "no-match-long": "no " + "a" * 400000 + " z" * 10,
    "many-negations": " ".join(["not"] * 20000) + " append-only",
    "hyphen-runs": "no " + "-".join(["aa"] * 100000) + " append-only",
    "plain-line": "SCORECARD.md is not strictly append-only per the round",
}
for name, s in cases.items():
    t = time.perf_counter()
    m = bool(aoa.NEG_WINDOW.search(s))
    print(f"  {name}: len={len(s)} match={m} {1000*(time.perf_counter()-t):.1f} ms")

print("== binds() edges (tip)")
b = aoa.binds
P = "LOG.md"
checks = [
    ("LOG.md is append-only", P, "LOG.md", True, "exact path match binds"),
    ("the catalog is append-only", P, "NOTES.md", False, "substring 'log' in catalog refused"),
    ("blog is append-only", P, "NOTES.md", False, "blog refused"),
    ("catalogue is append-only", P, "NOTES.md", False, "catalogue refused"),
    ("log.txt is append-only", P, "NOTES.md", True, "token 'log' with '.' boundary binds"),
    ("log-2 rotation is append-only", P, "NOTES.md", True, "'log-' boundary binds"),
    ("_log is append-only", P, "NOTES.md", False, "underscore-preceded refused"),
    ("logging is append-only", P, "NOTES.md", False, "'logging' refused"),
    ("LOG.md is not strictly append-only", P, "NOTES.md", False, "3-word negation window"),
    ("LOG.md is not append-only", P, "NOTES.md", False, "v3 negation string"),
    ("LOG.md is no longer append-only", P, "NOTES.md", False, "no longer"),
    ("LOG.md is not-append-only", P, "NOTES.md", False, "hyphenated negation"),
    ("not at all really very append-only", P, "NOTES.md", True, "negation 4 words away binds"),
    ("append-only but not really", P, "NOTES.md", True, "post-negation binds (frozen def)"),
    ("this is a non append-only file", P, "NOTES.md", False, "standalone non"),
    ("LOG.md is aren't append-only", P, "NOTES.md", False, "aren't window"),
    ("the notes dir is append-only", "notes/*.md", "README.md", True, "wildcard named via dir token"),
    ("this file is append-only", "notes/*.md", "notes/a.md", False, "wildcard self-decl refused"),
    ("x is append-only", "doc[s]/a.md", "doc[s]/a.md", False, "bracket pattern: no path auto-bind"),
    ("a.md is append-only", "doc[s]/a.md", "README.md", False, "bracket token is whole base"),
    ("*.md rows are append-only", "*.md", "README.md", False, "no-dir wildcard tok empty never binds"),
]
bad = 0
for text, pat, dp, want, why in checks:
    got = b(text, pat, dp)
    ok = got == want
    bad += 0 if ok else 1
    print(f"  {'ok ' if ok else 'FAIL'} binds({text[:38]!r}, {pat!r}, {dp}) = {got} want {want}  # {why}")
print(f"binds edges: {len(checks)-bad}/{len(checks)}")
