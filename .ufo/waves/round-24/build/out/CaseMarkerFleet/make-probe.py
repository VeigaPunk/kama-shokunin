#!/usr/bin/env python3
"""Scratch-only satisfiability probe for CaseMarkerFleet.

NOT a production edit and NOT an integration candidate: it exists to show that
the preregistered oracle (marker arm == plain arm, marker arm never exit 2
while complete) is reachable from the base auditor without weakening the
exit-2 boundary (a required object that is genuinely unavailable must still
refuse, and a citation that cannot be resolved locally must stay *unknown*).

Two edits on a copy of the base blob:

  1. check_history_repo: promisor marker metadata no longer refuses; the
     repository is recorded as promisor-backed.
  2. lookup: a citation that is missing in every audited repository while
     some audited repository is promisor-backed is an EvalError (unknown),
     not a defect verdict.

Everything else is byte-identical to 0df800e.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys

SRC = Path("/fast/scratch/hyaku/kama-r24/CaseMarkerFleet/repo/tools/"
           "report-landing-audit.py")
DST = Path("/fast/scratch/hyaku/kama-r24/CaseMarkerFleet/build/auditor-probe.py")

OLD_CONFIG = '''        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and git_bool(value)):
            raise EvalError(f"{repo}: partial clone ({key})")
'''

NEW_CONFIG = '''        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and git_bool(value)):
            PROMISOR_REPOS.add(str(repo))
'''

OLD_LOOKUP_TAIL = '''            status[token] = "found"
    return status
'''

NEW_LOOKUP_TAIL = '''            status[token] = "found"
    if any(status[t] == "missing" for t in tokens) and any(
            str(repo) in PROMISOR_REPOS for repo in repos):
        raise EvalError("citation(s) not available locally in a "
                        "promisor-backed repository: unknown, not absent")
    return status
'''

OLD_GLOBAL = '''GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch",
'''

NEW_GLOBAL = '''PROMISOR_REPOS = set()

GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch",
'''


def main():
    text = SRC.read_text(encoding="utf-8")
    for old, new, name in ((OLD_CONFIG, NEW_CONFIG, "config refusal"),
                           (OLD_LOOKUP_TAIL, NEW_LOOKUP_TAIL, "lookup tail"),
                           (OLD_GLOBAL, NEW_GLOBAL, "global")):
        if text.count(old) != 1:
            print(f"could-not-evaluate: {name}: {text.count(old)} matches",
                  file=sys.stderr)
            return 2
        text = text.replace(old, new)
    DST.write_text(text, encoding="utf-8")
    print(f"wrote {DST} sha256={hashlib.sha256(DST.read_bytes()).hexdigest()}")
    print(f"base  sha256={hashlib.sha256(SRC.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
