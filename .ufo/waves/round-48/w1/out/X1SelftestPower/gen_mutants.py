#!/usr/bin/env python3
"""gen_mutants.py - regenerate the four v3 mutants used for the round-48 X1SelftestPower kill matrix.

Reads the lane's tools/append-only-audit.py (read-only) and writes the mutants beside this script:
  mutant-M1-no-exemption.py            region exemption disabled          (line 417)
  mutant-M2-preheading-exempt.py       pre-heading region treated exempt  (after line 411)
  mutant-M3-exit-ignores-regressed.py  exit_code ignores regressed        (line 473)
  mutant-M4-no-clamp.py                clamp removed from the count       (line 424)
Then: python3 <mutant> --selftest --scratch <dir>   (one dir per mutant)
"""
import sys

SRC = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py"


def main(argv=None):
    src = open(SRC).read()

    m2_old = '''            eligible = {t for t in titles
                        if max(r.section_counts(wb[f"{x}:{f}"])[t] if wb[f"{x}:{f}"] else 0 for x in window)
                        >= pcount[t]}
'''
    m3_old = '''    return 1 if (s["partial"] or s["unrestored"] or s["regressed"] or s["vanished"]'''
    m3_new = '''    return 1 if (s["partial"] or s["unrestored"] or s["vanished"]'''
    m1_old = '''                if s in eligible:
                    continue'''
    m1_new = '''                if False:   # M1: exemptions disabled
                    continue'''
    m4_old = '''                h = sum(min(n, max(0, M[l] - K[l])) for l, n in G.items())'''
    m4_new = '''                h = sum(min(n, M[l] - K[l]) for l, n in G.items())'''

    for old in (m2_old, m3_old, m1_old, m4_old):
        if src.count(old) != 1:
            print(f"anchor not unique in {SRC}: {old.splitlines()[0]!r}", file=sys.stderr)
            return 2

    mutants = {
        "mutant-M1-no-exemption.py": src.replace(m1_old, m1_new),
        "mutant-M2-preheading-exempt.py": src.replace(
            m2_old, m2_old + '''            if titles:
                eligible.add(None)   # M2: the head region counts as exempt too
'''),
        "mutant-M3-exit-ignores-regressed.py": src.replace(m3_old, m3_new),
        "mutant-M4-no-clamp.py": src.replace(m4_old, m4_new),
    }
    for name, text in mutants.items():
        with open(name, "w") as fh:
            fh.write(text)
        print("wrote", name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
