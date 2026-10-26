#!/usr/bin/env python3
"""Clause census by mutation, against the frozen build blob 74558c71.

For each mutation that reverts one v4 clause: run the as-built 30-case suite and the
suite plus the 5 proposed cases on the same mutant. A clause is unexercised when the
as-built suite passes the mutant; the proposed case is discriminating when it fails there.
"""
import os
import subprocess
import sys

S = "/fast/scratch/hyaku/kama-r49/X2SelftestPower"
env = {**os.environ, "TMPDIR": S}
blob = open(f"{S}/v4-74558c71.py", encoding="utf-8").read()
new = open(f"{S}/v4-newcases.py", encoding="utf-8").read()

MUTS = {
    "M1_wildcard_token_disabled": (
        '    if not wild and fnmatch.fnmatchcase(decl_path, pattern):\n        return True\n',
        '    if not wild and fnmatch.fnmatchcase(decl_path, pattern):\n        return True\n    if wild:\n        return False\n'),
    "M2_origin_none_exempt": (
        'if s in eligible and org.get(text, frozenset()) & titles:',
        'if s in eligible and ((org.get(text, frozenset()) & titles) or None in org.get(text, frozenset())):'),
    "M3_neg_window_2_words": ('(?:[\\s\\-]+[\\w\'’]+){0,3}?', '(?:[\\s\\-]+[\\w\'’]+){0,2}?'),
    "M4_no_curly_apostrophe": ("(?:[\\s\\-]+[\\w'’]+){0,3}?", "(?:[\\s\\-]+[\\w']+){0,3}?"),
    "M5_single_origin_only": (
        'if s in eligible and org.get(text, frozenset()) & titles:',
        'if s in eligible and (org.get(text, frozenset()) & titles) and len(org.get(text, frozenset())) == 1:'),
}


def run(path, tag):
    r = subprocess.run([sys.executable, path, "--selftest", "--scratch", f"{S}/st-{tag}"],
                       capture_output=True, text=True, env=env)
    fails = [l.split(":")[0][5:] for l in r.stdout.splitlines() if l.startswith("FAIL")]
    summ = [l for l in r.stdout.splitlines() if l.startswith("AOA_SELFTEST")]
    return r.returncode, (summ[0] if summ else r.stderr[-300:]), fails


for name, (old, newt) in MUTS.items():
    assert blob.count(old) == 1 and new.count(old) == 1, (name, blob.count(old), new.count(old))
    pb, pn = f"{S}/mut/{name}-blob.py", f"{S}/mut/{name}-new.py"
    open(pb, "w", encoding="utf-8").write(blob.replace(old, newt))
    open(pn, "w", encoding="utf-8").write(new.replace(old, newt))
    rb, rn = run(pb, f"{name}-b"), run(pn, f"{name}-n")
    print(f"{name}: {old!r} -> {newt!r}")
    print(f"  as-built 30 cases on mutant : exit={rb[0]} {rb[1]} failing={rb[2]}")
    print(f"  +5 proposed cases on mutant : exit={rn[0]} {rn[1]} failing={rn[2]}")
