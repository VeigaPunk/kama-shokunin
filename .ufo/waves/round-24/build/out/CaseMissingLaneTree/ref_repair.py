#!/usr/bin/env python3
"""Scratch reference repair of the r23 promisor refusal (NOT a candidate).

Purpose: prove the round-24 oracle case is satisfiable — that a plausible
repair (drop the metadata refusal, add a read-only availability check)
produces exit 2 for the missing-tree case and a real verdict for the
complete promisor control.

This file lives in scratch only. It is not a candidate implementation, it
is not part of the repository, and L1 must not integrate it.
"""
import re
import subprocess
import sys
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/CaseMissingLaneTree/base-audit.py")
OUT = Path("/fast/scratch/hyaku/kama-r24/CaseMissingLaneTree/ref-audit.py")

PATCHES = [
    # 1. drop the promisor-pack refusal
    ("""        if rel == "objects/pack" and path.is_dir() and any(
                p.suffix == ".promisor" and p.with_suffix(".pack").exists()
                for p in path.iterdir()):
            raise EvalError(f"{repo}: partial clone (promisor pack)")""",
     """        if rel == "objects/pack" and path.is_dir() and any(
                p.suffix == ".promisor" and p.with_suffix(".pack").exists()
                for p in path.iterdir()):
            pass"""),
    # 2. drop the promisor-config refusal
    ("""        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and git_bool(value)):
            raise EvalError(f"{repo}: partial clone ({key})")""",
     """        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and git_bool(value)):
            pass"""),
    # 3. add the availability check (read-only, no fetch, no network)
    ("""def grafts_effective(path):""",
     """def check_objects_available(repo, refs):
    \"\"\"Every object reachable from the audited refs must be present
    locally; a promisor-backed repository may lack them, and absence there
    is not evidence.\"\"\"
    for ref in refs:
        out = git(repo, "rev-list", "--objects", "--missing=print", ref)
        for line in out.split("\\n"):
            if line.startswith("?"):
                raise EvalError(f"{repo}: object {line[1:].split(' ')[0]} "
                                f"reachable from {ref} is not available "
                                f"locally; missing evidence, not absence")


def grafts_effective(path):"""),
    # 4. call it from run()
    ("""    for repo in (lane_repo, fleet_repo):
        check_history_repo(repo)""",
     """    for repo in (lane_repo, fleet_repo):
        check_history_repo(repo)
    check_objects_available(lane_repo, ["refs/heads/" + args.branch])
    check_objects_available(fleet_repo, ["HEAD"])"""),
]


def main():
    text = BASE.read_text(encoding="utf-8")
    for old, new in PATCHES:
        if old not in text:
            print(f"patch anchor not found:\n{old[:120]}", file=sys.stderr)
            return 2
        text = text.replace(old, new, 1)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
