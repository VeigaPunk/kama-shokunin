#!/usr/bin/env python3
"""Round-37 C2 counter. New coverage-map block naming three adopted entries,
each citing a new S-id.

Predicate (identical in the preregistration, this file, and the receipt):
The round-37 coverage block names each of
knowledge/kv-cache-reclamation-models.md,
knowledge/prefix-cache-reuse-models.md and
knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md,
every one of those files exists in corpus/knowledge/, and each cites an S-id
present in corpus/SOURCES.md at the tip and absent at base
6a4afdfe48b0b54239d127761d21a5cf21b5b0ea; none of those three holds at that
base.

A name outside the heading '## Coverage map — round 37 addition' does not
count. An S-id already present at the base does not count. met is True only
when named=3, files_exist=3, and cited_new=3.

Exit 0 when met is True, 1 when met is False, 2 on usage.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PREDICATE = (
    "The round-37 coverage block names each of "
    "knowledge/kv-cache-reclamation-models.md, "
    "knowledge/prefix-cache-reuse-models.md and "
    "knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md, every one of "
    "those files exists in corpus/knowledge/, and each cites an S-id present "
    "in corpus/SOURCES.md at the tip and absent at base "
    "6a4afdfe48b0b54239d127761d21a5cf21b5b0ea; none of those three holds at "
    "that base."
)
HEADING = "## Coverage map — round 37 addition"
ENTRIES = (
    "knowledge/kv-cache-reclamation-models.md",
    "knowledge/prefix-cache-reuse-models.md",
    "knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md",
)
BASE = "6a4afdfe48b0b54239d127761d21a5cf21b5b0ea"


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
    return sum(1 for entry in ENTRIES if entry in body)


def cited_ids(entry: str) -> list[str]:
    return re.findall(r"\bS[0-9]{3,}\b", entry)


def registry_ids(sources: str) -> set[str]:
    found = set()
    for line in sources.splitlines():
        m = re.match(r"^\s{0,3}\|\s*(S[0-9]{3,})\s*\|", line)
        if m:
            found.add(m.group(1))
    return found


def score(
    readme: str,
    entries: dict[str, str | None],
    tip_sources: str | None,
    base_sources: str | None,
) -> dict[str, int | bool]:
    named = block_names(readme)
    files_exist = sum(1 for e in ENTRIES if entries.get(e) is not None)
    tip_ids = registry_ids(tip_sources or "")
    base_ids = registry_ids(base_sources or "")
    cited_new = 0
    for e in ENTRIES:
        text = entries.get(e)
        if text is None:
            continue
        if any(sid in tip_ids and sid not in base_ids for sid in cited_ids(text)):
            cited_new += 1
    met = named == 3 and files_exist == 3 and cited_new == 3
    return {"named": named, "files_exist": files_exist, "cited_new": cited_new, "met": int(met)}


def load(repo: Path, tip: str) -> tuple[str, dict[str, str | None], str | None, str | None]:
    readme = git_show(repo, tip, "corpus/README.md") or ""
    entries = {e: git_show(repo, tip, f"corpus/{e}") for e in ENTRIES}
    tip_sources = git_show(repo, tip, "corpus/SOURCES.md")
    base_sources = git_show(repo, BASE, "corpus/SOURCES.md")
    return readme, entries, tip_sources, base_sources


def emit(result: dict[str, int | bool]) -> str:
    met = "True" if result["met"] else "False"
    return (
        f"named {result['named']} files_exist {result['files_exist']} "
        f"cited_new {result['cited_new']} met {met}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--tip", required=True)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        readme, entries, tip_sources, base_sources = load(args.repo, args.tip)
        # The base arm is the BASE state, never the tip's files paired with the
        # base registry — mixing them made the base arm green at a landed tip
        # in round 36.
        base_readme, base_entries, _, base_sources = load(args.repo, BASE)
        base = score(base_readme, base_entries, base_sources, base_sources)
        outside = score(
            (base_readme or "") + f"\nsee {ENTRIES[0]} outside the block\n",
            {ENTRIES[0]: "source: S330\n"},
            "| S330 | x |\n",
            base_sources or "",
        )
        old_id = score(
            f"{HEADING}\n| {ENTRIES[0]} | x | 37 |\n",
            {ENTRIES[0]: "source: S006\n"},
            (tip_sources or "") + "\n",
            base_sources or "",
        )
        missing = score(
            f"{HEADING}\n| {ENTRIES[0]} | x | 37 |\n| {ENTRIES[1]} | x | 37 |\n| {ENTRIES[2]} | x | 37 |\n",
            {ENTRIES[0]: "source: S330\n", ENTRIES[1]: "source: S347\n", ENTRIES[2]: None},
            "| S330 | x |\n| S347 | x |\n",
            base_sources or "",
        )
        base_ok = not base["met"] and base["named"] == 0 and base["files_exist"] == 0 and base["cited_new"] == 0
        outside_ok = outside["named"] == 0 and not outside["met"]
        old_ok = old_id["cited_new"] == 0 and not old_id["met"]
        missing_ok = missing["files_exist"] == 2 and not missing["met"]
        print(
            f"SELFTEST base_met={base['met']} outside_met={outside['met']} "
            f"old_id_met={old_id['met']} missing_met={missing['met']} "
            f"pass={int(base_ok and outside_ok and old_ok and missing_ok)}"
        )
        print("base " + emit(base))
        return 0 if base_ok and outside_ok and old_ok and missing_ok else 1
    readme, entries, tip_sources, base_sources = load(args.repo, args.tip)
    result = score(readme, entries, tip_sources, base_sources)
    print(emit(result))
    return 0 if result["met"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — usage/env boundary
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
