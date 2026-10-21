#!/usr/bin/env python3
"""MS-01 fix prototype: flag seat-executed commands that touch forbidden roots
or prohibited commands. Input: one executed command per line (a seat transcript
export). Exit 0: no violation. Exit 1: at least one violation. Exit 2: unreadable.

Exclusion flags are not access: `--exclude-dir=interactive-sessions` is removed
before matching, so the form the round-16 lesson prescribes passes.
"""
import sys

FORBIDDEN_ROOTS = (
    "interactive-sessions", "~/.omp", "/.omp/", "~/.config", "/.config/",
    "~/.ssh", "/tmp/kama-r",
)
PROHIBITED = (
    "measure.py", "check-receipt.py --selftest", "check.py --selftest",
    "kama-llamacpp-live.py", "llama-server", "strace",
)
EXCLUSION = "--exclude-dir=interactive-sessions"


def hits(command):
    scrubbed = command.replace(EXCLUSION, "")
    found = [root for root in FORBIDDEN_ROOTS if root in scrubbed]
    found += [cmd for cmd in PROHIBITED if cmd in command]
    return found


def main(path):
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"unreadable: {exc}", file=sys.stderr)
        return 2
    commands = [(n, line) for n, line in enumerate(lines, 1)
                if line.strip() and not line.lstrip().startswith("#")]
    bad = []
    for n, line in commands:
        found = hits(line)
        if found:
            bad.append((n, found, line))
    for n, found, line in bad:
        print(f"VIOLATION line {n}: {found} :: {line}")
    print(f"{len(commands)} command(s) scanned, {len(bad)} violation(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: bound_scan.py TRANSCRIPT_COMMANDS.txt", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
