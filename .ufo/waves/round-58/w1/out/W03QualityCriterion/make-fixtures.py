#!/usr/bin/env python3
"""make-fixtures.py — regenerate the KQ98 control fixtures from committed bytes.

Usage: python3 make-fixtures.py <SOURCES.md dump at dcd69473> <rtld-audit.7.html dump> <outdir>

Writes SOURCES-{repaired,blanket,partial,unlocated}.md and rtld7-covered.html.
Only the S513 teaches cell changes, so every other row stays byte-identical.
"""
import sys
from pathlib import Path


def main():
    src_path, rtld_path, out = map(Path, sys.argv[1:4])
    src = src_path.read_text().splitlines()
    row_i = next(i for i, l in enumerate(src) if l.startswith("| S513 |"))
    cells = [c.strip() for c in src[row_i].strip().strip("|").split("|")]
    head, flip = cells[6].split("; flip: ")
    variants = {
        "repaired": head + "; this rejection is claim-scoped to the round-56 need; "
                    "flip-delta: secure-execution, dynamic string tokens, loader namespace semantics; "
                    "flip: " + flip,
        "blanket": head + "; this rejection is claim-scoped to the round-56 need; flip: " + flip,
        "partial": head + "; this rejection is claim-scoped to the round-56 need; "
                   "flip-delta: secure-execution, dynamic string tokens; flip: " + flip,
        "unlocated": "REJECTED: this broad loader manual overlaps the dedicated rtld-audit(7) source "
                     "S512 for the claim's only need (the LD_AUDIT variable loads auditor objects); "
                     "flip: a future claim about IFUNC resolver ordering",
    }
    out.mkdir(parents=True, exist_ok=True)
    for name, teaches in variants.items():
        c = list(cells)
        c[6] = teaches
        lines = list(src)
        lines[row_i] = "| " + " | ".join(c) + " |"
        (out / f"SOURCES-{name}.md").write_text("\n".join(lines) + "\n")
    rt = rtld_path.read_text().rstrip() + (
        "\n<p>Secure-execution mode details.</p>\n"
        "<p>Dynamic string tokens expand here.</p>\n"
        "<p>A separate linker namespace is used.</p>\n")
    (out / "rtld7-covered.html").write_text(rt)
    print("fixtures written to", out)


if __name__ == "__main__":
    main()
