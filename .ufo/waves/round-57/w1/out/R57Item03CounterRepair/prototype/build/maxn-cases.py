#!/usr/bin/env python3
"""Unit cases for the stale-maxN repair (scratch prototype only).

Compares two derivations over the same text:
  base  : max N over every raw line matching ^## Round (\\d+)   (the frozen counter)
  build : max N over lines outside fenced code blocks and HTML comments
          (`live_lines` in the patched copy), which preserves the canonical
          definition "greatest live `## Round N` heading".
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("build", os.path.join(HERE, "round42-selfdesc-reconcile.py"))
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


def base_maxn(text):
    rs = [int(m.group(1)) for l in text.split("\n")
          for m in [re.match(r"^## Round (\d+)", l)] if m]
    return max(rs) if rs else None


def build_maxn(text):
    rs = [int(m.group(1)) for l in build.live_lines(text)
          for m in [re.match(r"^## Round (\d+)", l)] if m]
    return max(rs) if rs else None


CASES = [
    ("plain live headings", "## Round 56\n## Round 12\n", 56, 56),
    ("five-backtick restored block",
     "## Round 56\n\n````text\n## Round 99 — stale\n````\n", 99, 56),
    ("nested three-fence inside five-fence",
     "## Round 56\n\n`````text\n```text\n## Round 99 — stale\n```\n`````\n", 99, 56),
    ("three-fence stale heading",
     "## Round 56\n\n```\n## Round 99 — stale\n```\n", 99, 56),
    ("tilde fence stale heading",
     "## Round 56\n\n~~~\n## Round 99 — stale\n~~~\n", 99, 56),
    ("html-comment stale heading",
     "## Round 56\n\n<!--\n## Round 98 — stale\n-->\n", 98, 56),
    ("unclosed fence hides the rest",
     "## Round 56\n\n````\n## Round 99 — stale\n", 99, 56),
    ("live heading after a closed fence wins",
     "## Round 56\n\n````\n## Round 99 — stale\n````\n## Round 60 — live\n", 99, 60),
    ("indented heading is not a heading",
     "## Round 56\n\n    ## Round 99 — indented\n", 56, 56),
    ("fence closer longer than opener",
     "## Round 56\n\n```\n## Round 99 — stale\n````\n## Round 60\n", 99, 60),
    ("inline comment line does not hide following heading",
     "## Round 56\n<!-- one line -->\n## Round 60\n", 60, 60),
]

fail = 0
print("case|base|build|want_base|want_build|ok")
for name, text, want_b, want_d in CASES:
    b, d = base_maxn(text), build_maxn(text)
    ok = (b == want_b and d == want_d)
    fail += 0 if ok else 1
    print(f"{name}|{b}|{d}|{want_b}|{want_d}|{ok}")

# Derived-key behaviour: which `### Planned (round N)` the counter demands.
text = "## Round 56\n\n````text\n## Round 99 — stale\n````\n\n### Planned (round 57)\n1. item\n"
print("planned_round_base=", base_maxn(text) + 1)
print("planned_round_build=", build_maxn(text) + 1)
print("cases_failed=", fail)
sys.exit(0 if fail == 0 else 1)
