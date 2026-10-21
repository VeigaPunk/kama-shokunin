#!/usr/bin/env python3
"""MS-02 fix prototype: every `required=N` count token must name its revision.

Rule: a token must carry `@<rev>` on the same line, and N must equal the number
of rows in registry/required-citations.json at that revision. Same-line binding
is strict by design; paragraph-level revision references need adjudication.

usage: count_sweep.py --repo REPO DOC [DOC ...]
Exit 0 all tokens bound and equal; 1 unbound or mismatched token(s); 2 bad input.
"""
import json
import re
import subprocess
import sys

TOKEN = re.compile(r"required=(\d+)")
REV = re.compile(r"@([0-9a-f]{7,40})\b")


def rows_at(repo, rev, cache):
    if rev not in cache:
        proc = subprocess.run(
            ["git", "-C", repo, "show", f"{rev}:registry/required-citations.json"],
            capture_output=True)
        if proc.returncode:
            raise SystemExit(f"cannot read registry at {rev}")
        cache[rev] = len(json.loads(proc.stdout))
    return cache[rev]


def main(argv):
    if len(argv) < 4 or argv[1] != "--repo":
        print("usage: count_sweep.py --repo REPO DOC [DOC ...]", file=sys.stderr)
        return 2
    repo, docs = argv[2], argv[3:]
    cache, bad, total = {}, [], 0
    for doc in docs:
        try:
            with open(doc, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except (OSError, UnicodeDecodeError) as exc:
            print(exc, file=sys.stderr)
            return 2
        for n, line in enumerate(lines, 1):
            for match in TOKEN.finditer(line):
                total += 1
                claimed = int(match.group(1))
                rev = REV.search(line)
                if rev is None:
                    bad.append(f"{doc}:{n}: required={claimed} has no @<rev> on its line")
                    continue
                actual = rows_at(repo, rev.group(1), cache)
                if actual != claimed:
                    bad.append(f"{doc}:{n}: required={claimed}@{rev.group(1)} "
                               f"but registry has {actual} rows")
    for item in bad:
        print("VIOLATION " + item)
    print(f"{total} count token(s), {len(bad)} violation(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
