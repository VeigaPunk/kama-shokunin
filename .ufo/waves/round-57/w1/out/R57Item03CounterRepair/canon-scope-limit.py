#!/usr/bin/env python3
"""Scope limit: the maxN repair does not repair canon() (canonical-row) selection.

The frozen counter's canon() scans the raw text for the highest
`canonical list as of round N` heading; a restored fenced block carrying a
higher-numbered canonical table is still selected after the maxN repair.
This is recorded as a limit, not implemented here (out of the assigned scope).
"""
import importlib.util
import os
import subprocess

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "b89bdab2cc114735ec5d331c6c610134258f7864"
spec = importlib.util.spec_from_file_location(
    "build", os.path.join(HERE, "prototype/build/round42-selfdesc-reconcile.py"))
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

text = subprocess.run(["git", "-C", LANE, "show", f"{BASE}:SCORECARD.md"],
                      capture_output=True, text=True, check=True).stdout
round_before, rows_before = build.canon(text)
text2 = text + ("\n`````text\n**Capabilities — canonical list as of round 99**\n\n"
                "| Capability | What | Evidence | First-working round |\n"
                "|---|---|---|---|\n| `fake-capability` | fixture | `tools/fake.py` | 99 |\n`````\n")
round_after, rows_after = build.canon(text2)
print(f"canon_round_before={round_before} rows={len(rows_before)}")
print(f"canon_round_after_fenced_stale_block={round_after} rows={len(rows_after)}")
print(f"fenced_stale_canon_selected={round_after == 99 and any(r[0].strip('` *') == 'fake-capability' for r in rows_after)}")
print("maxN_after_same_text=", max(int(m.group(1)) for line in build.live_lines(text2)
                                   for m in [__import__('re').match(r"^## Round (\d+)", line)] if m))
raise SystemExit(0 if (round_before == 49 and round_after == 99) else 1)
