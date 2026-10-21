#!/usr/bin/env python3
"""Round-24 (ScribeSkill) bounded probe 2: how a missing object behaves
under the auditor's own git isolation, and whether an availability check
can be made without contacting a promisor remote.

Synthetic offline fixtures only. Output: one JSON object on stdout.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPO = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
GRID = REPO / "tests/report-audit/repo-state-grid.py"

spec = importlib.util.spec_from_file_location("grid", GRID)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)

ISO = ["--no-replace-objects", "--no-lazy-fetch",
       "-c", "i18n.logOutputEncoding=UTF-8", "-c", "log.follow=false",
       "-c", "log.showRoot=true", "-c", "log.showSignature=false",
       "-c", "log.mailmap=false"]


def run(repo, *args, data=None):
    p = subprocess.run(["git", *ISO, "-C", str(repo), *args],
                       input=None if data is None else data.encode(),
                       capture_output=True, env=grid.env())
    return {"rc": p.returncode,
            "stdout": p.stdout.decode(errors="replace").strip()[:600],
            "stderr": p.stderr.decode(errors="replace").strip()[:400]}


def main():
    out = {"cases": {}}
    with tempfile.TemporaryDirectory(prefix="kama-r24-scribeskill2-") as tmp:
        tmp = Path(tmp)
        lane, fleet, lc = grid.base(tmp)
        blob = grid.g(lane, "rev-parse", f"{lc}:f")
        grid.g(lane, "config", "uploadpack.allowFilter", "true")
        clone = Path(tmp, "blobless")
        grid.g(tmp, "-c", "protocol.file.allow=always", "clone", "-q",
               "--no-checkout", "--filter=blob:none", "--no-local",
               f"file://{lane}", str(clone))
        # a promisor remote that cannot be reached: any fetch attempt shows up
        grid.g(clone, "config", "remote.origin.url", "file:///nonexistent/kama.git")
        grid.g(clone, "config", "remote.origin.promisor", "true")
        grid.g(clone, "config", "extensions.partialclone", "blob:none")

        out["cases"]["cat-file-batch-check-missing"] = run(
            clone, "cat-file", "--batch-check", data=f"{blob}\n")
        out["cases"]["cat-file-e-missing"] = run(clone, "cat-file", "-e", blob)
        out["cases"]["rev-list-missing-print"] = run(
            clone, "rev-list", "--objects", "--all", "--missing=print")
        out["cases"]["rev-list-missing-print-no-objects"] = run(
            clone, "rev-list", "--all", "--missing=print")
        out["cases"]["cat-file-commit-present"] = run(
            clone, "cat-file", "--batch-check", data=f"{lc}\n")
        # is the blob still absent, and did any fetch happen?
        out["cases"]["blob-still-absent"] = run(clone, "cat-file", "-e", blob)
        out["cases"]["objects-dir"] = sorted(
            str(p.relative_to(clone)) for p in clone.glob(".git/objects/pack/*"))
        out["cases"]["config"] = run(clone, "config", "--null", "--list")
    json.dump(out, sys.stdout, indent=1, sort_keys=True)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
