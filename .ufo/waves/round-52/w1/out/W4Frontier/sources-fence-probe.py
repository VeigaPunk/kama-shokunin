#!/usr/bin/env python3
"""W4Frontier round-52 probe: does tools/sources-append-only.py accept a registry-shaped
row that was re-appended verbatim (as C2 would, inside a five-backtick fence) at the end of
corpus/SOURCES.md?

Reads corpus/SOURCES.md at the build tip from git (read-only), appends a fenced block holding
one live S-row, and calls the lane tool's own parse_registry() on both texts.
Exit 0 if the appended text parses (i.e. the A-row rows could be restored by append without
a parser change), 1 if the tool refuses; prints the refusal.
"""
import importlib.util
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
TIP = "5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8"

spec = importlib.util.spec_from_file_location("sao", LANE + "/tools/sources-append-only.py")
sao = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sao)

text = subprocess.run(["git", "-C", LANE, "show", f"{TIP}:corpus/SOURCES.md"],
                      capture_output=True, check=True).stdout.decode()
rows, _ = sao.parse_registry(text, "base")
print(f"base: parsed {len(rows)} registry rows")

row = [ln for ln in text.splitlines() if ln.startswith("| S500 ")][0]
appended = (text + "\n## Restored rows (round 53)\n\n"
            "Restored verbatim from a deleting commit (probe).\n\n"
            "`````text\n" + row + "\n`````\n")
try:
    sao.parse_registry(appended, "appended")
except sao.ParseError as exc:
    print(f"appended: ParseError: {exc}")
    sys.exit(1)
print("appended: parsed; a fenced verbatim row would be registry data")
sys.exit(0)
