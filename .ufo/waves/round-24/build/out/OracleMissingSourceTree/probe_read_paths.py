#!/usr/bin/env python3
"""Enumerate the git read paths an implementation could use to find the
committed SOURCES.md, and record what each one observes when the SOURCES
parent subtree is absent, when the SOURCES blob is absent, and when the
path was never committed.

The point: an implementation must be able to tell "the path is not in the
tree" (absence -> legacy, a verdict is allowed) from "the tree or blob that
would hold the path cannot be read" (unavailability -> could-not-evaluate).

Usage: probe_read_paths.py FIXTURE_ROOT OUT.json
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

VARIANTS = ("A-corpus-tree-absent", "B-sources-blob-absent",
            "C-content-complete-control", "D-sources-path-never-committed",
            "E-tip-tree-absent")

PATHS = (
    ("ls-tree-path", ["ls-tree", "master", "--", "corpus/SOURCES.md"]),
    ("ls-tree-path-recursive", ["ls-tree", "-r", "master", "--",
                                "corpus/SOURCES.md"]),
    ("ls-tree-root", ["ls-tree", "master"]),
    ("ls-tree-corpus-dir", ["ls-tree", "master", "--", "corpus/"]),
    ("rev-parse-path", ["rev-parse", "master:corpus/SOURCES.md"]),
    ("rev-parse-verify-path", ["rev-parse", "--verify",
                               "master:corpus/SOURCES.md"]),
    ("cat-file-e-path", ["cat-file", "-e", "master:corpus/SOURCES.md"]),
    ("ls-tree-head-path", ["ls-tree", "HEAD", "--", "corpus/SOURCES.md"]),
    ("rev-list-objects", ["rev-list", "--objects", "--missing=print",
                          "--no-object-names", "master"]),
)


def env():
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return e


def run(repo, args, stdin=None):
    p = subprocess.run(["git", "-C", str(repo), "--no-lazy-fetch",
                        "--no-replace-objects", *args],
                       input=stdin, capture_output=True, env=env())
    return {"rc": p.returncode,
            "out": p.stdout.decode(errors="replace").strip()[:300],
            "err": p.stderr.decode(errors="replace").strip()[:220]}


def main(argv=None):
    argv = list(argv or sys.argv)
    if len(argv) < 3:
        print("usage: probe_read_paths.py FIXTURE_ROOT OUT.json",
              file=sys.stderr)
        return 2
    root, out_path = Path(argv[1]).resolve(), Path(argv[2]).resolve()
    doc = {"paths": {}, "variants": {}}
    for name, args in PATHS:
        doc["paths"][name] = args
    for variant in VARIANTS:
        lane = root / variant / "lane"
        entry = {}
        for name, args in PATHS:
            entry[name] = run(lane, args)
        # batch-check answers "missing" instead of failing: record it
        entry["cat-file-batch-check-path"] = run(
            lane, ["cat-file", "--batch-check"],
            stdin=b"master:corpus/SOURCES.md\n")
        entry["cat-file-batch-check-sha"] = run(
            lane, ["cat-file", "--batch-check"],
            stdin=b"HEAD^{tree}\n")
        doc["variants"][variant] = entry
    out_path.write_text(json.dumps(doc, indent=1, sort_keys=True),
                        encoding="utf-8")
    print(json.dumps(doc, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
