#!/usr/bin/env python3
"""Round-35 C2 counter. Coverage-map surface for one new probe-convention entry.

Predicate (identical in the preregistration, this file, and the receipt):
The round-35 coverage block names knowledge/endpoint-health-probe-conventions.md,
that file exists, and it cites an S-id present in corpus/SOURCES.md; none of
those three hold at base 719655f12517a9ce6b1a5ca44316897fed8420b0.

A name outside the heading '## Coverage map — round 35 addition' does not count.
met is True only when named=1, file_exists=1, and cited_row=1.

Exit 0 when met is True, 1 when met is False, 2 on usage.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PREDICATE = (
    "The round-35 coverage block names "
    "knowledge/endpoint-health-probe-conventions.md, that file exists, and "
    "it cites an S-id present in corpus/SOURCES.md; none of those three hold "
    "at base 719655f12517a9ce6b1a5ca44316897fed8420b0."
)
HEADING = "## Coverage map — round 35 addition"
ENTRY = "knowledge/endpoint-health-probe-conventions.md"
ENTRY_REPO = "corpus/knowledge/endpoint-health-probe-conventions.md"
BASE = "719655f12517a9ce6b1a5ca44316897fed8420b0"


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


def block_names(readme: str) -> int:
    if HEADING not in readme:
        return 0
    body = readme.split(HEADING, 1)[1]
    body = body.split("\n## ", 1)[0]
    return body.count(ENTRY)


def cited_ids(entry: str) -> list[str]:
    return re.findall(r"\bS[0-9]{3,}\b", entry)


def registry_ids(sources: str) -> set[str]:
    found = set()
    for line in sources.splitlines():
        match = re.match(r"^ {0,3}\|\s*(S[0-9]+)\s*\|", line)
        if match:
            found.add(match.group(1))
    return found


def score(readme: str, entry: str | None, sources: str | None) -> dict[str, int | bool]:
    named = block_names(readme)
    file_exists = 1 if entry is not None else 0
    cited = 0
    if entry is not None and sources is not None:
        ids = cited_ids(entry)
        known = registry_ids(sources)
        if any(sid in known for sid in ids):
            cited = 1
    met = named == 1 and file_exists == 1 and cited == 1
    return {"named": named, "file_exists": file_exists, "cited_row": cited, "met": met}


def load(repo: Path, tip: str | None) -> tuple[str, str | None, str | None]:
    if tip:
        readme = git_show(repo, tip, "corpus/README.md") or ""
        entry = git_show(repo, tip, ENTRY_REPO)
        sources = git_show(repo, tip, "corpus/SOURCES.md")
        return readme, entry, sources
    readme_path = repo / "corpus/README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.is_file() else ""
    entry_path = repo / ENTRY_REPO
    entry = entry_path.read_text(encoding="utf-8") if entry_path.is_file() else None
    sources_path = repo / "corpus/SOURCES.md"
    sources = sources_path.read_text(encoding="utf-8") if sources_path.is_file() else None
    return readme, entry, sources


def emit(result: dict[str, int | bool]) -> str:
    met = "True" if result["met"] else "False"
    return (
        f"named {result['named']} file_exists {result['file_exists']} "
        f"cited_row {result['cited_row']} met {met}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--tip", default=None)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        base_readme, base_entry, base_sources = load(args.repo, BASE)
        base = score(base_readme, base_entry, base_sources)
        junk = score(
            base_readme + f"\nsee {ENTRY} outside the block\n",
            "source: S327\n",
            "| S327 | x |\n",
        )
        outside_ok = junk["named"] == 0 and not junk["met"]
        base_ok = not base["met"] and base["named"] == 0 and base["file_exists"] == 0
        print(f"SELFTEST base_met={base['met']} junk_met={junk['met']} pass={int(base_ok and outside_ok)}")
        print("base " + emit(base))
        return 0 if base_ok and outside_ok else 1
    readme, entry, sources = load(args.repo, args.tip)
    result = score(readme, entry, sources)
    print(emit(result))
    return 0 if result["met"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — usage/env boundary
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
