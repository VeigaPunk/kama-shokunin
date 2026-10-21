"""Simulate the r24 repair's effect on the r23 mutation population.

The repair removes the two blanket promisor refusals. isolation-mutants.py
requires every replacement pattern to match EXACTLY ONCE in the auditor
source (tests/report-audit/isolation-mutants.py:119-122); a zero match is a
could-not-evaluate that aborts the whole mutant run.
"""
import re
src = open('tools/report-landing-audit.py').read()
mut = open('tests/report-audit/isolation-mutants.py').read()
ns = {}
exec(mut[mut.index('MUTANTS = ['):mut.index('\n]\n', mut.index('MUTANTS = ['))+3], ns)
M = ns['MUTANTS']

def strip_promisor(text):
    # variant A: raise -> pass (literal removed)
    a = text.replace('raise EvalError(f"{repo}: partial clone (promisor pack)")', 'pass')
    a = a.replace('raise EvalError(f"{repo}: partial clone ({key})")', 'pass')
    return a

def strip_block(text):
    # variant B: whole promisor detection block removed
    out = []
    skip = False
    for line in text.splitlines(True):
        if 'for rel in ("info/grafts", "objects/pack"):' in line:
            skip = True
        if skip and 'def grafts_effective' in line:
            skip = False
        if not skip:
            out.append(line)
    b = "".join(out)
    b = re.sub(r'    listing = git\(repo, "config", "--null", "--list",\n.*?\n.*?\n.*?\n.*?\n', '', b, flags=re.S)
    return b

for label, variant in (("A: raises->pass", strip_promisor(src)), ("B: block removed", strip_block(src))):
    print("== variant", label)
    zero = []
    for name, old, new in M:
        c = variant.count(old)
        if c != 1:
            zero.append((name, c))
    print("   patterns that no longer match exactly once:", zero if zero else "none")
