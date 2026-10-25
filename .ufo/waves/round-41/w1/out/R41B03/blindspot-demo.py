#!/usr/bin/env python3
"""R41B03 blind-spot demos for the two surviving/half-surviving mutants.

M2 (peeled lines counted): a tag_regex that fullmatches a peeled name
    (`v(\\d+).*`) makes pristine and mutant differ -> the counter's fixture
    grammar (only `v(\\d+)\\.(\\d+)\\.(\\d+)` and `b(\\d+)`) can never do this.
M4 (exit precedence swapped): a pins file mixing a behind engine with a
    missing engine gives pristine exit 2 vs mutant exit 1 with byte-equal
    lines -> the selftest has no such mixed case.
"""
import os
import subprocess
import sys

BASE = "/tmp/R41B03"
VARIANTS = {
    "pristine": f"{BASE}/pristine-pin-watch.py",
    "M2": f"{BASE}/export-M2/tools/pin-watch.py",
    "M4": f"{BASE}/export-M4/tools/pin-watch.py",
}


def run(variant, demo):
    p = subprocess.run(
        [sys.executable, VARIANTS[variant], "check",
         "--pins", f"{BASE}/{demo}/pins.tsv", "--tags-dir", f"{BASE}/{demo}/tags"],
        capture_output=True, text=True)
    lines = [l for l in p.stdout.splitlines() if l.strip()]
    return p.returncode, lines


def main():
    d2 = f"{BASE}/m2demo"
    os.makedirs(f"{d2}/tags", exist_ok=True)
    with open(f"{d2}/pins.tsv", "w") as f:
        f.write("engine\trepo\ttag_regex\tpin\tsource\n")
        f.write("e\thttps://example.invalid/e.git\tv(\\d+).*\tv1.2.3\tS000\n")
    with open(f"{d2}/tags/e.txt", "w") as f:
        f.write("aaaa\trefs/tags/v1.2.3\nbbbb\trefs/tags/v1.2.3^{}\n")
    print("M2 demo (regex v(\\d+).* , annotated tag v1.2.3 + peeled line):")
    for v in VARIANTS:
        rc, lines = run(v, "m2demo")
        print(f"  {v}: exit {rc} {lines}")

    d4 = f"{BASE}/m4demo"
    os.makedirs(f"{d4}/tags", exist_ok=True)
    with open(f"{d4}/pins.tsv", "w") as f:
        f.write("engine\trepo\ttag_regex\tpin\tsource\n")
        f.write("e1\thttps://example.invalid/e1.git\tv(\\d+)\\.\\d+\tv1.0\tS000\n")
        f.write("e2\thttps://example.invalid/e2.git\tv(\\d+)\\.\\d+\tv9.9\tS000\n")
    with open(f"{d4}/tags/e1.txt", "w") as f:
        f.write("aaaa\trefs/tags/v1.0\nbbbb\trefs/tags/v2.0\n")
    with open(f"{d4}/tags/e2.txt", "w") as f:
        f.write("aaaa\trefs/tags/v1.0\n")
    print("M4 demo (engine e1 behind + engine e2 missing):")
    for v in VARIANTS:
        rc, lines = run(v, "m4demo")
        print(f"  {v}: exit {rc} {lines}")


if __name__ == "__main__":
    main()
