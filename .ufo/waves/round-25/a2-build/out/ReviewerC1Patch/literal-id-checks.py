#!/usr/bin/env python3
"""Literal, id, and site checks for the round-25 C1 patch (seat ReviewerC1Patch).

Reads the pinned clone at 1fc41e346853afd98cbd7010af5db4e54dc877f7 and the
parent 5388b7cf (the registry before the patch). Read-only: git show and python
string checks; writes nothing.
"""
import ast
import importlib.util as u
import re
import subprocess

CL = "/fast/scratch/hyaku/kama-r25a2/ReviewerC1Patch/clone"
TIP = "1fc41e346853afd98cbd7010af5db4e54dc877f7"
PARENT = "5388b7cf1d5bad9c228da6f95c40f323414be2f1"
BASE = "147f5bdd3228ab712520b5f377346cb2d9a64769"
R23 = "e876b95"
AUD = "tools/report-landing-audit.py"
MUT = "tests/report-audit/isolation-mutants.py"


def gshow(rev, path):
    r = subprocess.run(["git", "-C", CL, "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8") if r.returncode == 0 else None


def load(text):
    g = {"__file__": f"{CL}/{MUT}", "__name__": "under_test"}
    exec(compile(text, MUT, "exec"), g)
    return g


def enclosing(src, idx):
    name = None
    for mm in re.finditer(r"^def (\w+)\(", src, re.M):
        if mm.start() <= idx:
            name = mm.group(1)
        else:
            break
    return name


def line_of(src, idx):
    return src.count("\n", 0, idx) + 1


tip_src = gshow(TIP, AUD)
tip = load(gshow(TIP, MUT))
par = load(gshow(PARENT, MUT))
tm = {n: (o, nw) for n, o, nw in tip["MUTANTS"]}
pm = {n: (o, nw) for n, o, nw in par["MUTANTS"]}

ids = [n for n, _, _ in tip["MUTANTS"]]
print("entries", len(ids), "unique", len(set(ids)) == len(ids), "sorted", ids == sorted(ids))
print("added", [n for n in ids if n not in pm], "removed", [n for n in pm if n not in tm])
print("changed tuples", [n for n in pm if n in tm and pm[n] != tm[n]])
ret = [r[0] for r in tip["RETIRED"]]
nums = {int(re.match(r"M(\d+)-", n).group(1)) for n in ids + ret}
print("retired", ret, "numbers absent from MUTANTS and RETIRED", [i for i in range(1, 34) if i not in nums])
print("parent stale vs tip auditor", [n for n, o, _ in par["MUTANTS"] if tip_src.count(o) != 1])

for n, o, nw in tip["MUTANTS"]:
    c = tip_src.count(o)
    info = ""
    if c == 1:
        i = tip_src.find(o)
        info = f"line {line_of(tip_src, i)} in {enclosing(tip_src, i)}"
        try:
            ast.parse(tip_src.replace(o, nw))
            info += " mutant-parses"
        except SyntaxError as exc:
            info += f" MUTANT-SYNTAX line {exc.lineno}: {exc.msg}"
    print(f"{n}: count={c} {info}")

print("M11 anchor", repr(tm["M11-listing-surrogates"][0]))
print("M17 anchor", repr(tm["M17-ref-shadow"][0]))
print("M33 anchor", repr(tm["M33-ref-shadow-bare-objects"][0]))

lines = tip_src.split("\n")
for a, b in [(681, 683), (212, 214), (275, 277)]:
    for k in range(a, b + 1):
        print("tip", k, repr(lines[k - 1]))

print("names-a-ref sites", [(line_of(tip_src, m.start()), enclosing(tip_src, m.start()))
                             for m in re.finditer(r"names a ref", tip_src)])
print("startswith(token) sites", [(line_of(tip_src, m.start()), enclosing(tip_src, m.start()))
                                  for m in re.finditer(r"startswith\(token\)", tip_src)])
print("bare_objects calls", [(line_of(tip_src, m.start()), enclosing(tip_src, m.start()))
                             for m in re.finditer(r"bare_objects\(", tip_src)])
print("lookup calls", [(line_of(tip_src, m.start()), enclosing(tip_src, m.start()))
                       for m in re.finditer(r"lookup\(", tip_src)])

s23 = gshow(R23, AUD)
i = s23.find("if not peel and not parts[0].startswith(token):")
print("R23 guard line", line_of(s23, i), "in", enclosing(s23, i))
i = s23.find('"--", ".ufo/reports", errors="surrogateescape"')
print("R23 M11 call line", line_of(s23, i), "in", enclosing(s23, i))
i = s23.find("if peel:\n        bare = lookup(repos, tokens)")
print("R23 recursive no-peel bare lookup (found)", i >= 0, "line", line_of(s23, i) if i >= 0 else None)

for rev in ["e0f0434", "34b2376", "e876b95", "ed1cc3a", "92063cf", BASE, TIP]:
    mt = gshow(rev, MUT)
    if mt is None:
        continue
    print(rev, "mutant ids", re.findall(r'\("(M\d\d)-', mt))
