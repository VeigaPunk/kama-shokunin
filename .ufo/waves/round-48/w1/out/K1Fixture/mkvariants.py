#!/usr/bin/env python3
"""Generate v3 tool variants (each wrong in exactly one definition clause) from the
canonical append-only-audit.py at lane commit 380bcdff9c8af06997c482f6eb03db926a794a2b."""
import os, re

SRC = "/fast/scratch/hyaku/kama-r48/K1Fixture/aoa-canonical.py"
OUT = "/fast/scratch/hyaku/kama-r48/K1Fixture/var"
os.makedirs(OUT, exist_ok=True)
base = open(SRC).read()

def patch(name, old, new, count=1):
    n = base.count(old)
    assert n == count, f"{name}: anchor found {n} != {count}"
    src = base.replace(old, new)
    path = os.path.join(OUT, name + ".py")
    open(path, "w").write(src)
    print(name, len(src))

# V-A: exempt-title match uses startswith instead of exact equality
patch("va_startswith_title",
      "                if s in eligible:\n                    continue\n",
      "                if s is not None and any(t is not None and s.startswith(t) for t in eligible):\n                    continue\n")

# V-B: regions come from the LAST matching row only (union broken)
patch("vb_last_row_only",
      """def file_regions(rows, f):
    \"\"\"(exempt titles, only prefixes) for a file from every contract row whose pattern matches it.\"\"\"
    titles, prefixes = set(), []
    for row in rows:
        if fnmatch.fnmatchcase(f, row[0]):
            region = row[3]
            if region[0] == "exempt":
                titles |= set(region[1])
            elif region[0] == "only":
                prefixes.append(region[1])
    return titles, prefixes
""",
      """def file_regions(rows, f):
    \"\"\"(exempt titles, only prefixes) for a file from the LAST contract row whose pattern matches it.\"\"\"
    titles, prefixes = set(), []
    for row in rows:
        if fnmatch.fnmatchcase(f, row[0]):
            titles, prefixes = set(), []
            region = row[3]
            if region[0] == "exempt":
                titles |= set(region[1])
            elif region[0] == "only":
                prefixes.append(region[1])
    return titles, prefixes
""")

# V-C: window excludes the event commit itself
patch("vc_window_excludes_event",
      "            window = commits[i:]\n",
      "            window = commits[i + 1:]\n")

# V-D: eligibility uses count at the event commit, not the window maximum
patch("vd_eligibility_at_event",
      """            eligible = {t for t in titles
                        if max(r.section_counts(wb[f"{x}:{f}"])[t] if wb[f"{x}:{f}"] else 0 for x in window)
                        >= pcount[t]}
""",
      """            eligible = {t for t in titles
                        if (r.section_counts(wb[f"{c}:{f}"])[t] if wb[f"{c}:{f}"] else 0)
                        >= pcount[t]}
""")

# V-E: vanished paths are never detected
patch("ve_vanished_ignored",
      "        gone = vanished(repo_path, to_full, patterns, set(files))\n",
      "        gone = []\n")

# V-F: a binary change becomes a phantom event instead of being skipped
patch("vf_binary_as_event",
      """            if ns[f] is None:
                binary.append({"commit": c, "file": f})
                continue
""",
      """            if ns[f] is None:
                binary.append({"commit": c, "file": f})
                events.append({"commit": c, "file": f, "deleted": 0, "graded": 0, "ungraded": 0,
                               "restored_max": 0, "restored_best": None, "restored_by": None,
                               "held_at_to": 0, "status": "ungraded"})
                continue
""")

# V-G: regressed fires when held_at_to <= restored_max (non-strict)
patch("vg_regressed_nonstrict",
      '               "regressed": sum(e["status"] in ("restored", "partial") and e["held_at_to"] < e["restored_max"]\n',
      '               "regressed": sum(e["status"] in ("restored", "partial") and e["held_at_to"] <= e["restored_max"]\n')

# V-H: only-region pointer must also say re-derived
patch("vh_only_pointer_rederived",
      '    elif not binds(text, pat, pp) or region[1][3:].strip().lower() not in low:\n',
      '    elif not binds(text, pat, pp) or "re-derived" not in low or region[1][3:].strip().lower() not in low:\n')

# V-I: an empty region cell is tolerated as `*`
patch("vi_empty_region_star",
      '    if cell == "*":\n        return ("*",)\n',
      '    if cell == "*" or cell == "":\n        return ("*",)\n')

# V-J: held counts over D (all deleted) instead of G (graded)
patch("vj_held_over_d",
      "                h = sum(min(n, max(0, M[l] - K[l])) for l, n in G.items())\n",
      "                h = sum(min(n, max(0, M[l] - K[l])) for l, n in D.items())\n")

# V-L: unmatched patterns enter the exit code
patch("vl_exit_on_unmatched",
      "                 or s[\"bad_declarations\"]) else 0\n",
      "                 or s[\"bad_declarations\"] or s[\"unmatched\"]) else 0\n")
