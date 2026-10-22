#!/usr/bin/env python3
"""FinalConsumer01 repair-attribution probe (derived, same fixture).

Take the BEFORE auditor (pinned 2e254a17, sha256 ea51bc3...) and splice in
ONLY the store-scoped lookup repair taken from the AFTER source
(92063cf, sha256 b9be4f4...): the per-store `bare_objects` helper plus the
per-canonical-object reconciliation in `lookup`.  Nothing else is changed.

If the spliced variant turns the red-before (exit 2 could-not-evaluate)
into the corrected verdict (exit 1, kinds ['landed-unresolved']) on the very
same fixture, the discriminating change is the store-merge repair itself.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer01")
BEFORE = BASE / "out/before-report-landing-audit.py"
AFTER = BASE / "clone/tools/report-landing-audit.py"
OUT = BASE / "out/before-plus-store-repair.py"


def region(text, start_marker, end_marker):
    i = text.index(start_marker)
    j = text.index(end_marker, i + 1)
    return text[i:j]


def main():
    before = BEFORE.read_text(encoding="utf-8")
    after = AFTER.read_text(encoding="utf-8")
    # the after's bare_objects + lookup, as one contiguous block
    new_block = region(after, "def bare_objects(store, tokens):",
                       "def root_tree(repo, root, cause=None):")
    # replace the before's lookup with it
    old_block = region(before, "def lookup(stores, tokens, peel=\"\"):",
                       "def root_tree(repo, root):")
    patched = before.replace(old_block, new_block)
    assert patched != before
    assert "def bare_objects" in patched
    OUT.write_text(patched, encoding="utf-8")
    res = {}
    for name, tool in (("before_pinned", BEFORE),
                       ("before_plus_store_repair", OUT),
                       ("after_92063cf", AFTER)):
        cmd = [sys.executable, str(tool),
               "--lane-repo", str(BASE / "fixture/lane"),
               "--fleet-repo", str(BASE / "fixture/fleet"),
               "--branch", "master", "--rounds", "1",
               "--report", f"1={BASE / 'fixture/draft.md'}", "--json",
               "--no-errata"]
        p = subprocess.run(cmd, capture_output=True, timeout=120,
                           env={**os.environ, "TMPDIR": str(BASE / "tmp")})
        kinds, errata_invalid = [], None
        doc = None
        if p.returncode in (0, 1):
            try:
                doc = json.loads(p.stdout.decode("utf-8", "replace"))
                kinds = sorted({d["kind"] for res_ in doc["results"]
                                for d in res_["defects"]})
                errata_invalid = doc["summary"].get("errata_invalid")
            except Exception:
                pass
        res[name] = {
            "tool": str(tool),
            "tool_sha256": hashlib.sha256(Path(tool).read_bytes()).hexdigest(),
            "exit": p.returncode, "kinds": kinds,
            "errata_invalid": errata_invalid,
            "stderr": p.stderr.decode("utf-8", "replace").strip()[:300],
            "summary": doc.get("summary") if doc else None,
            "defects": ([d for r_ in doc["results"] for d in r_["defects"]]
                        if doc else None)}
    (BASE / "out/attribution.json").write_text(
        json.dumps(res, indent=1, sort_keys=True), encoding="utf-8")
    for k, v in res.items():
        print(k, "exit=", v["exit"], "kinds=", v["kinds"],
              "errata_invalid=", v["errata_invalid"],
              "|", v["stderr"][:120])


if __name__ == "__main__":
    main()
