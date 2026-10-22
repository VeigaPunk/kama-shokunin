#!/usr/bin/env python3
"""Two bounded static/local checks for the CitedHole family.

1. acquisition: a full .git tree fingerprint (every file, size, mtime_ns and
   sha256) of both audited repositories before and after the current arm, so a
   transport attempt, a lazy fetch, a pack write or a FETCH_HEAD is visible
   even if it created no object.
2. mutation contract: a STATIC check that the PM02/PM03/PM04 mutant
   alternatives of tests/report-audit/promisor-mutants.py actually match the
   pinned source of tools/report-landing-audit.py (a mutant whose patch does
   not apply is silently skipped and kills nothing).  No mutant is executed.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseCitedHole")
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/"
           "falsify/out/CaseCitedHole")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def fingerprint(repo: Path):
    """Every file under .git: relative path, size, mtime_ns, sha256."""
    gitdir = Path(subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--absolute-git-dir"],
        capture_output=True, text=True).stdout.strip())
    items = {}
    for p in sorted(gitdir.rglob("*")):
        if p.is_file():
            data = p.read_bytes()
            items[str(p.relative_to(gitdir))] = {
                "size": len(data),
                "mtime_ns": p.stat().st_mtime_ns,
                "sha256": hashlib.sha256(data).hexdigest()}
    return items


def main():
    grid = load(CLONE / "tests/report-audit/promisor-grid.py",
                "grid_local2")
    root = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseCitedHole/tmp-acq")
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    auditor = CLONE / "tools/report-landing-audit.py"
    report = {"acquisition": {}}

    for case, builder in (("PG33-missing-cited-blob-promisor",
                           "c_missing_cited_blob_promisor"),
                          ("PG34-missing-cited-blob-plain",
                           "c_missing_cited_blob_plain")):
        tmp = root / case
        tmp.mkdir(parents=True, exist_ok=True)
        built = grid.BUILDERS[builder](root, tmp)
        lane, fleet = built["lane"], built["fleet"]
        before = {"lane": fingerprint(lane), "fleet": fingerprint(fleet)}
        code, out, err, to = grid.run_auditor(auditor, lane, fleet, tmp, False)
        after = {"lane": fingerprint(lane), "fleet": fingerprint(fleet)}
        rec = {"exit": code, "timed_out": to}
        for side in ("lane", "fleet"):
            added = sorted(set(after[side]) - set(before[side]))
            removed = sorted(set(before[side]) - set(after[side]))
            changed = sorted(k for k in set(before[side]) & set(after[side])
                             if before[side][k]["sha256"] != after[side][k]
                             ["sha256"])
            rec[side] = {"files_added": added, "files_removed": removed,
                         "files_content_changed": changed,
                         "identical": before[side] == after[side],
                         "file_count": len(after[side])}
        report["acquisition"][case] = rec

    # --- static mutation-contract applicability --------------------------
    src = (CLONE / "tools/report-landing-audit.py").read_text()
    import re
    mut = (CLONE / "tests/report-audit/promisor-mutants.py").read_text()
    checks = {
        "PM02-insert-anchor": 'if __name__ == "__main__":' in src,
        "PM03-missing-set-empty": bool(re.search(
            r'self\._missing = set\(missing_reachable\(\s*self\.path, '
            r'self\.root\)\)', src)),
        "PM03-missing-set-tuple": bool(re.search(
            r'self\._missing = missing_reachable\(\s*self\.path, '
            r'self\.root\)', src)),
        "PM04-unknown-citation-loop": bool(re.search(
            r'def unknown_citation\(stores, token\):.*?for store in stores:',
            src, re.S)),
        "PM04-unknown-citation-return": bool(re.search(
            r'def unknown_citation\(stores, token\):.*?\n    return None\n',
            src, re.S)),
        "PM10-opaque-hole-def": "def opaque_hole(stores):" in src,
        "PM11-repo-store-missing": "self._missing" in src,
    }
    # which mutant rows are expected to be killed by the two CitedHole rows
    m = json.loads(json.dumps(grid.__dict__.get("MUTANTS", [])))
    manifest = []
    for entry in m:
        rows = entry.get("expect_rows", [])
        manifest.append({"id": entry.get("id"),
                         "kills_PG33": "PG33" in rows,
                         "kills_PG34": "PG34" in rows,
                         "execution": entry.get("execution")})
    report["mutation_static"] = {"patch_targets_present": checks,
                                  "manifest_rows": manifest,
                                  "note": "static only: no mutant executed"}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "acquisition-and-mutants.json").write_text(
        json.dumps(report, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=1))
    shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
