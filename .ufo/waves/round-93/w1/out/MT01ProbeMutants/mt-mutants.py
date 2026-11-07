#!/usr/bin/env python3
"""mt-mutants.py - build single-point mutants of the M1 probe's C1 memo code.

Source: tools/kama-probe.sh at fe5f031cb1b9d33e1160360d892149b8ac3c7771 (M1), read via
`git -C <repo> show M1:tools/kama-probe.sh`. Each mutant replaces exactly one behaviour-bearing
snippet of gguf_state / gguf_parse / the memo, asserted to occur exactly once. No other byte
of the probe changes; the output is byte-identical to M1 apart from the substitution.

Usage: mt-mutants.py --repo DIR --rev REV --out DIR
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

BLOCK = '''def gguf_state(path):
    try:
        st = os.stat(path)
    except OSError:
        return gguf_parse(path)
    if not stat.S_ISREG(st.st_mode) or os.path.realpath(path).startswith(NO_OPEN):
        return gguf_parse(path)
    key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)
    if key not in SEEN:
        SEEN[key] = gguf_parse(path)
    return SEEN[key]
'''

UNKNOWN = '''        except Unknown:
            return "-"
'''


def state_block(key_expr=None, oserror="-gguf", guard=True, memo=True, memo_cond="if key not in SEEN:",
                stmt="SEEN[key] = gguf_parse(path)", order="guard-first", st_call="os.stat"):
    """Emit a gguf_state variant; every parameter has its M1 value as default."""
    if key_expr is None:
        key_expr = "(st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)"
    lines = ["def gguf_state(path):", "    try:", f"        st = {st_call}(path)", "    except OSError:"]
    lines.append("        return gguf_parse(path)" if oserror == "-gguf" else '        return "-"')
    if guard:
        g = "    if not stat.S_ISREG(st.st_mode) or os.path.realpath(path).startswith(NO_OPEN):"
        if order == "guard-first":
            lines += [g, "        return gguf_parse(path)"]
    lines.append(f"    key = {key_expr}")
    if memo:
        lines += [f"    {memo_cond}", f"        {stmt}"]
    else:
        lines += ["    return gguf_parse(path)"]
        return "\n".join(lines) + "\n"
    if guard and order == "after-memo":
        lines += ["    if not stat.S_ISREG(st.st_mode) or os.path.realpath(path).startswith(NO_OPEN):",
                  "        return gguf_parse(path)"]
    lines.append("    return SEEN[key]")
    return "\n".join(lines) + "\n"


# name -> (needle, replacement)
MUTANTS = {
    # key fields dropped one at a time
    "m01-drop-dev": (BLOCK, state_block(key_expr="(st.st_ino, st.st_size, st.st_mtime_ns)")),
    "m02-drop-ino": (BLOCK, state_block(key_expr="(st.st_dev, st.st_size, st.st_mtime_ns)")),
    "m03-drop-size": (BLOCK, state_block(key_expr="(st.st_dev, st.st_ino, st.st_mtime_ns)")),
    "m04-drop-mtime": (BLOCK, state_block(key_expr="(st.st_dev, st.st_ino, st.st_size)")),
    # memo keyed by the path string instead of file identity (r92 F2 class)
    "m05-key-path": (BLOCK, state_block(key_expr="(path,)")),
    # no memo at all: every candidate parses its file
    "m06-no-memo": (BLOCK, state_block(memo=False)),
    # memo keeps only an `invalid` result (others are re-parsed on each hit)
    "m07-memo-invalid-only": (BLOCK, state_block(memo_cond='if SEEN.get(key) != "invalid":')),
    # the regular-file / NO_OPEN guard consulted only after the memo lookup
    "m08-noopen-after-memo": (BLOCK, state_block(order="after-memo")),
    # stat -> lstat in the fast path (a symlink alias gets its own identity)
    "m09-lstat": (BLOCK, state_block(st_call="os.lstat")),
    # a stat error is reported undecidable instead of deferred to the parser
    "m10-oserror-minus": (BLOCK, state_block(oserror="-")),
    # ctime instead of mtime in the identity
    "m12-mtime-to-ctime": (BLOCK, state_block(key_expr="(st.st_dev, st.st_ino, st.st_size, st.st_ctime_ns)")),
    # mtime at whole-second resolution
    "m13-mtime-seconds": (BLOCK, state_block(key_expr="(st.st_dev, st.st_ino, st.st_size, st.st_mtime)")),
    # the regular-file half of the guard dropped (non-regular files get memoized too)
    "m14-nonreg-memoized": (BLOCK, BLOCK.replace(
        "if not stat.S_ISREG(st.st_mode) or os.path.realpath(path).startswith(NO_OPEN):",
        "if os.path.realpath(path).startswith(NO_OPEN):")),
    # an undecidable parse graded invalid instead of loadable
    "m15-unknown-invalid": (UNKNOWN, UNKNOWN.replace('return "-"', 'return "invalid"')),
    # the per-call deadline removed from the read/seek budget
    "m16-deadline-ignored": ('''            if steps[0] > MAX_STEPS or (steps[0] & 0xFFF) == 0 and time.monotonic() > DEADLINE:
                raise Unknown()
''', '''            if steps[0] > MAX_STEPS:
                raise Unknown()
'''),
    # memo cleared before every candidate file: dedupe inside one candidate only
    "m11-seen-reset-per-candidate": (
        "    states = [gguf_state(p) for p in paths if os.path.isabs(p)]\n"
        "    for want in (\"missing\", \"invalid\"):",
        "    states = []\n"
        "    for p in paths:\n"
        "        if os.path.isabs(p):\n"
        "            SEEN.clear()\n"
        "            states.append(gguf_state(p))\n"
        "    for want in (\"missing\", \"invalid\"):"),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    src = subprocess.run(["git", "-C", str(a.repo), "show", f"{a.rev}:tools/kama-probe.sh"],
                         capture_output=True, check=True).stdout
    text = src.decode()
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "probe-M1.sh").write_bytes(src)
    print(f"M1 sha256={hashlib.sha256(src).hexdigest()} bytes={len(src)}")
    for name in sorted(MUTANTS):
        needle, repl = MUTANTS[name]
        n = text.count(needle)
        if n != 1:
            print(f"MUTANT {name} FAIL needle occurs {n} times")
            return 1
        out = text.replace(needle, repl, 1)
        if out == text:
            print(f"MUTANT {name} FAIL replacement is a no-op")
            return 1
        p = a.out / f"mut-{name}.sh"
        p.write_bytes(out.encode())
        print(f"MUTANT {name} sha256={hashlib.sha256(out.encode()).hexdigest()} "
              f"delta_bytes={len(out.encode()) - len(src)} file={p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
