#!/usr/bin/env python3
"""Generate SCORECARD variants for the S03 self-description counter audit.

Reads a copy of SCORECARD.md and writes a variant. Modes:
  faithful   byte copy
  f1-empty   capability repertoire emptied in both the head `## Capabilities`
             mirror and the highest canonical list; §Retired and §Saturation
             adjusted so they stay self-consistent with an empty repertoire.
  f2-rename  one capability renamed in both the head mirror and the canonical
             list, so both surfaces still agree with each other.

Only SCORECARD text is transformed; every other fixture file is identical
across variants, so counter deltas isolate the capability checks.
"""
import re
import sys


def split_table(lines, start):
    """Indices of header, separator and data rows of the table starting at/after start."""
    i = start
    while i < len(lines) and not lines[i].startswith("|"):
        i += 1
    if i >= len(lines):
        raise SystemExit(f"no table at/after line {start}")
    j = i
    while j < len(lines) and lines[j].startswith("|"):
        j += 1
    return i, j


def drop_rows(lines, heading_re):
    out = []
    dropped = 0
    for idx, ln in enumerate(lines):
        out.append(ln)
    for m in list(re.finditer(heading_re, "\n".join(lines), re.M)):
        pass
    return out


def main():
    src, dst, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    text = open(src).read()
    lines = text.split("\n")
    if mode == "faithful":
        open(dst, "w").write(text)
        return

    if mode == "f1-empty":
        # highest canonical heading (round 49 on this lane)
        canon_idx = None
        for i, l in enumerate(lines):
            if re.search(r"canonical list as of round\s+(\d+)\*\*", l, re.I):
                if canon_idx is None or int(re.search(r"round\s+(\d+)", l, re.I).group(1)) > \
                        int(re.search(r"round\s+(\d+)", lines[canon_idx], re.I).group(1)):
                    canon_idx = i
        a, b = split_table(lines, canon_idx)
        n_canon = b - (a + 2)
        del lines[a + 2:b]
        # head mirror section
        cap_idx = next(i for i, l in enumerate(lines) if l.strip() == "## Capabilities")
        c, d = split_table(lines, cap_idx)
        n_head = d - (c + 2)
        del lines[c + 2:d]
        text = "\n".join(lines)
        before = text
        text = text.replace("6 axes and 11 capabilities", "6 axes and 0 capabilities")
        text = text.replace(
            "capability first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47",
            "capability first-working rounds (none)")
        assert text != before, "retired/saturation rewrites did not apply"
        open(dst, "w").write(text)
        print(f"f1-empty: dropped canonical rows={n_canon} head rows={n_head}")
        return

    if mode == "f3-maxn":
        # Fabricate a newer round heading with no measurement behind it, and let
        # the self-description surfaces agree with it.
        text = "\n".join(lines)
        n = int(re.search(r"Latest measured round: (\d+)", text).group(1))
        new = n + 42
        text = text.replace(f"Latest measured round: {n}", f"Latest measured round: {new}", 1)
        text = text.replace(f"### Planned (round {n + 1})", f"### Planned (round {new + 1})")
        text += (f"\n## Round {new} — fabricated heading, no measurement behind it\n\n"
                 f"No receipt, counter or commit measures this round.\n")
        open(dst, "w").write(text)
        print(f"f3-maxn: fabricated round {new}")
        return

    if mode == "f2-rename":
        before = text
        text = text.replace("| pin-watch |", "| pin-watch-renamed |")
        assert text.count("pin-watch-renamed") >= 2, "rename hit fewer than two tables"
        open(dst, "w").write(text)
        print(f"f2-rename: renamed rows={text.count('pin-watch-renamed')}")
        return

    raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    main()
