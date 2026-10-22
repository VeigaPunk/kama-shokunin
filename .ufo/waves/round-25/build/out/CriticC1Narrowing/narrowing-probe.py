#!/usr/bin/env python3
"""Critic probe for round-25 C1 (read-only against the lane tree).

Part 1 (static): shows that the registered C1 counting command reaches
"stale 0" under narrowing edits the non-narrowing rules forbid.
Part 2 (--grid): builds candidate re-anchored M11 and per-site M17 mutants in
a scratch directory and runs the round-23 grid's current arm on each, using
the instrument's own grid() helper. No lane file is written.
"""
import importlib.util as u
import json
from pathlib import Path
import sys

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SCRATCH = Path("/fast/scratch/hyaku/kama-r25/CriticC1Narrowing/probe")
SCRATCH.mkdir(parents=True, exist_ok=True)

spec = u.spec_from_file_location(
    "m", LANE / "tests/report-audit/isolation-mutants.py")
m = u.module_from_spec(spec)
spec.loader.exec_module(m)
src = (LANE / "tools/report-landing-audit.py").read_text(encoding="utf-8")


def stale(mutants, source=src):
    bad = [n for n, o, _ in mutants if source.count(o) != 1]
    return len(mutants), len(bad), bad


M11_OLD = dict((n, o) for n, o, _ in m.MUTANTS)["M11-listing-surrogates"]
M17_OLD = dict((n, o) for n, o, _ in m.MUTANTS)["M17-ref-shadow"]
base = [x for x in m.MUTANTS]
drop = [x for x in base if x[0] not in ("M11-listing-surrogates",
                                         "M17-ref-shadow")]

# same element, reflowed literal (the honest repair for M11)
M11_SAME = ('"HEAD", "--", ".ufo/reports",\n'
            '                             errors="surrogateescape")',
            '"HEAD", "--", ".ufo/reports")')
# a different element / no-op target that still matches exactly once
M11_DOCSTRING = ("report path listing) pass surrogateescape.",
                 "report path listing) pass strict.")
# M17 per call site: site 1 = bare_objects (peel path), site 2 = lookup
# (no-peel path); each literal is made unique by its preceding line
M17_SITE1 = ('result[token] = ("excluded", None)\n        else:\n'
             '            parts = line.split(" ")\n'
             '            if len(parts) != 3 or not re.fullmatch(r"[0-9a-f]{40}", parts[0]):\n'
             '                raise EvalError(f"cat-file in {store.path}: unexpected {line!r}")\n'
             '            if not parts[0].startswith(token):\n'
             '                # git resolved a same-named ref before the object prefix\n'
             '                raise EvalError(f"{store.path}: citation {token} names a ref")',
             None)
M17_SITE2 = ('            if not peel and not parts[0].startswith(token):\n'
             '                # git resolved a same-named ref before the object prefix\n'
             '                raise EvalError(f"{store.path}: citation {token} names a ref")',
             None)


def site_mutant(literal):
    return literal.replace(
        'raise EvalError(f"{store.path}: citation {token} names a ref")',
        "pass")


variants = {
    "as-registered": base,
    "drop-M11-and-M17": drop,
    "retire-M11-and-M17-unproved": drop,
    "M11-docstring-reanchor+M17-site2-only": drop + [
        ("M11-listing-surrogates", *M11_DOCSTRING),
        ("M17-ref-shadow", M17_SITE2[0], site_mutant(M17_SITE2[0]))],
    "M11-same-element+M17-site1-only": drop + [
        ("M11-listing-surrogates", *M11_SAME),
        ("M17-ref-shadow", M17_SITE1[0], site_mutant(M17_SITE1[0]))],
}

report = {"static": {}}
for name, muts in variants.items():
    n, k, bad = stale(muts)
    report["static"][name] = {"registered": n, "stale": k, "bad": bad}
report["static_counts"] = {
    "M11_old": src.count(M11_OLD), "M17_old": src.count(M17_OLD),
    "M11_same_element": src.count(M11_SAME[0]),
    "M11_docstring": src.count(M11_DOCSTRING[0]),
    "M17_site1": src.count(M17_SITE1[0]),
    "M17_site2": src.count(M17_SITE2[0]),
}
# the command reads m.AUDIT, which the instrument itself defines
report["command_reads"] = str(m.AUDIT)
# RETIRED literals are never checked by the counting command
report["retired_literal_counts"] = {r[0]: src.count(r[1]) for r in m.RETIRED}
report["retire_M17_literal_count_if_moved"] = src.count(M17_OLD)

if "--grid" in sys.argv:
    cands = {
        "pristine": src,
        "M11-same-element": src.replace(*M11_SAME),
        "M11-docstring": src.replace(*M11_DOCSTRING),
        "M17-site1-bare_objects": src.replace(
            M17_SITE1[0], site_mutant(M17_SITE1[0])),
        "M17-site2-lookup-nopeel": src.replace(
            M17_SITE2[0], site_mutant(M17_SITE2[0])),
        "M17-both-sites": src.replace(
            M17_OLD, "pass"),
    }
    report["grid"] = {}
    for name, text in cands.items():
        p = SCRATCH / f"{name}.py"
        p.write_text(text, encoding="utf-8")
        rc, failed, err = m.grid(p)
        report["grid"][name] = {"grid_exit": rc, "failed_rows": failed,
                                "error": err,
                                "differs_from_pristine": text != src}
        print(name, rc, failed, err, file=sys.stderr, flush=True)

print(json.dumps(report, indent=1, sort_keys=True))
