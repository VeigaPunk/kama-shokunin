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
validated against the registry's rows (CORPUS.md rule 3, KQ46): an id counts
only when the registry row's pinned artifact is the artifact the entry names.

A name outside the heading '## Coverage map — round 38 addition' (read until
the next ## heading) does not count. An S-id already present at the base does
not count. met is True only when named=2, files_exist=2, files_absent_base=2,
entry_new=2 (each entry cites at least one new id) and cited_new=3.

Exit 0 when met is True, 1 when met is False, 2 on usage.

Instrument repair note (round 38, wave 1): the committed counter looked the
entries up as knowledge/... at the repo root instead of corpus/knowledge/,
counted any S-id anywhere in SOURCES.md as registry-held, never checked base
absence of the files, and pooled ids across entries. The repair implements the
frozen predicate literally; PREDICATE is unchanged and the measurement line
keeps the same shape. Repair receipts: .ufo/waves/round-38/w1/out/
ReviewKQ46Behavior.md, ScoutLearned.md, ScribeLesson.md, ScribeAppendBlock.md.
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
    "corpus/knowledge/sglang-docs-version-pinning.md",
    "corpus/knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md",
)
BASE = "2a4a97dc890fe393035986c951797c5d65b6cc69"
ID_RE = re.compile(r"\bS[0-9]{3,}\b")
ROW_RE = re.compile(r"^ {0,3}\|\s*S[0-9]{3,}\s*\|")


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


def at_rev(repo: Path, rev: str, path: str) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", f"{rev}:{path}"],
        check=False, capture_output=True,
    )
    return proc.returncode == 0


def urls_in(text: str) -> set[str]:
    return set(re.findall(r"https?://\S+", text))


def registry_rows(repo: Path, rev: str) -> dict[str, str]:
    """Row id -> source cell (or '') for table rows only."""
    src = git_show(repo, rev, "corpus/SOURCES.md")
    out: dict[str, str] = {}
    if src is None:
        return out
    for line in src.splitlines():
        if not ROW_RE.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 11:
            continue
        _id, source = cells[0], cells[1]
        if ID_RE.fullmatch(_id):
            out[_id] = source
    return out


def entry_source_ids(repo: Path, rev: str, entry: str) -> dict[str, str]:
    """Ids on source: lines only, with the line text that names them."""
    text = git_show(repo, rev, entry)
    out: dict[str, str] = {}
    if text is None:
        return out
    for line in text.splitlines():
        if not line.strip().lower().startswith("source:"):
            continue
        for i in ID_RE.findall(line):
            out.setdefault(i, line.strip())
    return out


def evaluate(repo: Path, tip: str) -> dict:
    readme = git_show(repo, tip, "corpus/README.md") or ""
    if HEADING in readme:
        after = readme.split(HEADING, 1)[1]
        block = after.split("\n## ", 1)[0]
        named = sum(1 for e in ENTRIES if e in block)
    else:
        named = 0
    files_exist = sum(1 for e in ENTRIES if at_rev(repo, tip, e))
    files_absent_base = sum(1 for e in ENTRIES if not at_rev(repo, BASE, e))
    tip_rows = registry_rows(repo, tip)
    base_rows = registry_rows(repo, BASE)
    entry_new = 0
    new_ids: set[str] = set()
    for e in ENTRIES:
        cited = entry_source_ids(repo, tip, e)
        ok: set[str] = set()
        for i, line in cited.items():
            row_cell = tip_rows.get(i)
            # KQ46: the registry row's pinned artifact must be the artifact that
            # the source: line names — URL intersection.
            if row_cell and urls_in(row_cell) & urls_in(line):
                ok.add(i)
        new = ok - set(base_rows)
        new_ids |= new
        if new:
            entry_new += 1
    cited_new = len(new_ids)
    met = (
        named == 2
        and files_exist == 2
        and files_absent_base == 2
        and entry_new == 2
        and cited_new == 3
    )
    return dict(named=named, files_exist=files_exist,
                files_absent_base=files_absent_base, entry_new=entry_new,
                cited_new=cited_new, met=met,
                new_ids=sorted(new_ids))


def main() -> int:
    ap = argparse.ArgumentParser(description=PREDICATE)
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--tip", required=True)
    args = ap.parse_args()
    r = evaluate(args.repo, args.tip)
    print(
        f"named {r['named']} files_exist {r['files_exist']} "
        f"cited_new {r['cited_new']} met {str(r['met']).capitalize()}"
    )
    if r["new_ids"]:
        print(f"new ids: {', '.join(r['new_ids'])}")
    return 0 if r["met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
