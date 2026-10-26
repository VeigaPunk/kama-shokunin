#!/usr/bin/env python3
"""S2Events recount - header-aware deletion/restoration count for the frozen C2 events.

Read-only. Same diff definition as tools/append-only-audit.py (first parent,
--no-renames -U0), but drops only the real `--- <prefix>/<path>` header line
instead of every line whose text begins `---`, so deleted content lines that
begin `--` (e.g. `--out ...`, `--tip ...`) are counted.

Usage: python3 recount.py <repo> <tip>
Prints, per event in the tool's list: counted deleted/held, the frozen tool's
numbers, and the deleted lines absent at tip.
"""
import subprocess
import sys

EVENTS = [
    ("dd9f5dc6c0e63d038bdd070094d7f38290eeee1b", "SCORECARD.md"),
    ("0718b6abbda6afa6b0ce586f46739fbb92c7cf9c", "SCORECARD.md"),
    ("0718b6abbda6afa6b0ce586f46739fbb92c7cf9c", "LOG.md"),
    ("0718b6abbda6afa6b0ce586f46739fbb92c7cf9c", "corpus/QUALITY.md"),
    ("0718b6abbda6afa6b0ce586f46739fbb92c7cf9c", "corpus/README.md"),
]


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)}: {p.stderr.strip()}")
    return p.stdout


def deleted_lines(repo, commit, path):
    parent = git(repo, "rev-parse", commit + "^1").strip()
    d = git(repo, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", parent, commit, "--", path)
    lines = d.split("\n")
    out = []
    for i, x in enumerate(lines):
        if x.startswith("---") and i + 1 < len(lines) and lines[i + 1].startswith("+++"):
            continue  # the real file header
        if x.startswith("-"):
            out.append(x[1:])
    return out


def main():
    repo, tip = sys.argv[1], sys.argv[2]
    for commit, path in EVENTS:
        dele = deleted_lines(repo, commit, path)
        have = set(git(repo, "show", f"{tip}:{path}").split("\n"))
        held = sum(1 for x in dele if x in have)
        print(f"{commit[:12]} {path}: header-aware deleted={len(dele)} held_at_tip={held} "
              f"unique={len(set(dele))} unique_held={len(set(dele) & have)}")
        if held < len(dele):
            missing = [x for x in dele if x not in have]
            for x in missing:
                print(f"  absent: {x[:160]}")


if __name__ == "__main__":
    main()
