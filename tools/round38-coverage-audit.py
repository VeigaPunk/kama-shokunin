#!/usr/bin/env python3
"""Round-38 C2 counter. New coverage-map block naming two adopted entries,
each citing new S-ids on its source: lines.

Predicate (identical in the preregistration, this file, and the receipt):
The round-38 coverage block names each of knowledge/sglang-docs-version-pinning.md
and knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md, every one of
those files exists in corpus/knowledge/, and each cites an S-id present in
corpus/SOURCES.md at the tip and absent at base
2a4a97dc890fe393035986c951797c5d65b6cc69 on its source: lines; none of those
two holds at that base. Cited ids are read from source: lines only and are
validated against the registry's rows (CORPUS.md rule 3, KQ46).

A name outside the heading '## Coverage map — round 38 addition' does not
count. An S-id already present at the base does not count. met is True only
when named=2, files_exist=2, and cited_new=3.

Exit 0 when met is True, 1 when met is False, 2 on usage.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PREDICATE = (
    "The round-38 coverage block names each of "
    "knowledge/sglang-docs-version-pinning.md and "
    "knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md, every one "
    "of those files exists in corpus/knowledge/, and each cites an S-id "
    "present in corpus/SOURCES.md at the tip and absent at base "
    "2a4a97dc890fe393035986c951797c5d65b6cc69 on its source: lines; none of "
    "those two holds at that base."
)
HEADING = "## Coverage map — round 38 addition"
ENTRIES = (
    "knowledge/sglang-docs-version-pinning.md",
    "knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md",
)
BASE = "2a4a97dc890fe393035986c951797c5d65b6cc69"
ID_RE = re.compile(r"\bS[0-9]{3,}\b")


def git_show(repo: Path, rev: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", f"{rev}:{path}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def registry_ids(repo: Path, rev: str) -> set[str]:
    src = git_show(repo, rev, "corpus/SOURCES.md")
    if src is None:
        return set()
    return set(ID_RE.findall(src))


def entry_source_ids(repo: Path, rev: str, entry: str) -> set[str]:
    """Ids on source: lines only (provenance trio), registry-validated."""
    text = git_show(repo, rev, entry)
    if text is None:
        return set()
    ids: set[str] = set()
    for line in text.splitlines():
        if line.strip().lower().startswith("source:"):
            ids |= set(ID_RE.findall(line))
    return ids


def evaluate(repo: Path, tip: str) -> dict:
    readme = git_show(repo, tip, "corpus/README.md") or ""
    if HEADING in readme:
        block = readme.split(HEADING, 1)[1]
        named = sum(1 for e in ENTRIES if e in block)
    else:
        named = 0
    files_exist = 0
    for e in ENTRIES:
        proc = subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", f"{tip}:{e}"],
            check=False, capture_output=True,
        )
        if proc.returncode == 0:
            files_exist += 1
    tip_reg = registry_ids(repo, tip)
    base_reg = registry_ids(repo, BASE)
    cited: set[str] = set()
    for e in ENTRIES:
        cited |= entry_source_ids(repo, tip, e)
    cited &= tip_reg  # registry-validated (KQ46)
    cited_new = len(cited - base_reg)
    met = (named == 2 and files_exist == 2 and cited_new == 3)
    return dict(named=named, files_exist=files_exist, cited_new=cited_new,
                met=met, cited=sorted(cited - base_reg))


def main() -> int:
    ap = argparse.ArgumentParser(description=PREDICATE)
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--tip", required=True)
    args = ap.parse_args()
    r = evaluate(args.repo, args.tip)
    print(
        f"named {r['named']} files_exist {r['files_exist']} "
        f"cited_new {r['cited_new']} met {str(r['met']).lower()}"
    )
    if r["cited"]:
        print(f"new ids: {', '.join(r['cited'])}")
    return 0 if r["met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
