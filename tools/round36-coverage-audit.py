#!/usr/bin/env python3
"""Round-36 C2 counter. One new coverage-map entry citing a new S-id.

Predicate (identical in the preregistration, this file, and the receipt):
The round-36 coverage block names knowledge/sglang-native-route-deprecation.md, that file exists, and it cites an S-id present in corpus/SOURCES.md at the tip and absent at base e5a8ececf3d60fd53b36bb74299693a29e8f74b6; none of those three hold at that base.

A name outside the heading '## Coverage map — round 36 addition' does not count.
An S-id already present at the base does not count.
met is True only when named=1, file_exists=1, and cited_new=1.

Exit 0 when met is True, 1 when met is False, 2 on usage.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PREDICATE = (
    "The round-36 coverage block names "
    "knowledge/sglang-native-route-deprecation.md, that file exists, and it "
    "cites an S-id present in corpus/SOURCES.md at the tip and absent at base "
    "e5a8ececf3d60fd53b36bb74299693a29e8f74b6; none of those three hold at that base."
)
HEADING = "## Coverage map — round 36 addition"
ENTRY = "knowledge/sglang-native-route-deprecation.md"
ENTRY_REPO = "corpus/knowledge/sglang-native-route-deprecation.md"
BASE = "e5a8ececf3d60fd53b36bb74299693a29e8f74b6"


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


def score(readme: str, entry: str | None, tip_sources: str | None, base_sources: str | None) -> dict[str, int | bool]:
    named = block_names(readme)
    file_exists = 1 if entry is not None else 0
    cited_new = 0
    if entry is not None and tip_sources is not None and base_sources is not None:
        tip_ids = registry_ids(tip_sources)
        base_ids = registry_ids(base_sources)
        if any(sid in tip_ids and sid not in base_ids for sid in cited_ids(entry)):
            cited_new = 1
    met = named == 1 and file_exists == 1 and cited_new == 1
    return {"named": named, "file_exists": file_exists, "cited_new": cited_new, "met": met}


def load(repo: Path, tip: str) -> tuple[str, str | None, str | None, str | None]:
    readme = git_show(repo, tip, "corpus/README.md") or ""
    entry = git_show(repo, tip, ENTRY_REPO)
    sources = git_show(repo, tip, "corpus/SOURCES.md")
    base_sources = git_show(repo, BASE, "corpus/SOURCES.md")
    return readme, entry, sources, base_sources


def emit(result: dict[str, int | bool]) -> str:
    met = "True" if result["met"] else "False"
    return (
        f"named {result['named']} file_exists {result['file_exists']} "
        f"cited_new {result['cited_new']} met {met}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--tip", required=True)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        readme, entry, sources, base_sources = load(args.repo, args.tip)
        # The base arm must be the BASE state, not the tip's readme and entry
        # paired with the base registry: once the round lands, the tip's
        # README names the entry and the entry file exists, so mixing them
        # made the base arm report met True at a landed tip.
        base_readme, base_entry, base_sources2, _ = load(args.repo, BASE)
        base = score(base_readme, base_entry, base_sources2, base_sources2)
        outside = score(
            (base_readme or "") + f"\nsee {ENTRY} outside the block\n",
            "source: S328\n",
            "| S328 | x |\n",
            base_sources2 or "",
        )
        old_id = score(
            f"{HEADING}\n| {ENTRY} | x | 36 |\n",
            "source: S006\n",
            (base_sources or "") + "\n",
            base_sources or "",
        )
        base_ok = not base["met"] and base["named"] == 0 and base["file_exists"] == 0 and base["cited_new"] == 0
        outside_ok = outside["named"] == 0 and not outside["met"]
        old_ok = old_id["cited_new"] == 0 and not old_id["met"]
        print(
            f"SELFTEST base_met={base['met']} outside_met={outside['met']} "
            f"old_id_met={old_id['met']} pass={int(base_ok and outside_ok and old_ok)}"
        )
        print("base " + emit(base))
        return 0 if base_ok and outside_ok and old_ok else 1
    readme, entry, sources, base_sources = load(args.repo, args.tip)
    result = score(readme, entry, sources, base_sources)
    print(emit(result))
    return 0 if result["met"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — usage/env boundary
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
