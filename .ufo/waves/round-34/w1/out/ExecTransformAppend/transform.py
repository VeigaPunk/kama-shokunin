# Round-34 ExecTransformAppend scratch normalizer.
# Contract: read the staged served-name/alias rows, emit an 11-column append block,
# mirror the lane corpus plus the three admitted entries in this seat, and record
# stripped recheck prose. Never writes the lane's real corpus or VCS state.
# Exit codes: 0 success; 1 source/schema/collision rejection; 2 missing input or I/O setup failure.

from __future__ import annotations

import hashlib
import json
import re
import shutil
from collections import OrderedDict
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SEAT = LANE / ".ufo/waves/round-34/w1/out/ExecTransformAppend"
STAGED = Path("/home/vgpnk/Projects/shokuknow/merge/kama")
STAGED_REGISTRY = STAGED / "SOURCES.append.md"
STAGED_ENTRIES = STAGED / "knowledge/corpus/knowledge"
ENTRY_NAMES = (
    "serving-alias-contract.md",
    "served-model-id-resolution.md",
    "served-model-id-resolution-amendment-2026-10-24-r7.md",
)
HEADERS = (
    "id",
    "source",
    "kind",
    "tier",
    "scope",
    "anchor",
    "teaches",
    "status",
    "opened",
    "recheck",
    "used-by",
)
ROW_START = re.compile(r"^ {0,3}\|\s*S[0-9]{3,}\s*\|")
SOURCE_ID = re.compile(r"\bS[0-9]{3,}\b")
CADENCE = re.compile(r"(?:[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]+d|[A-Za-z][A-Za-z0-9 _-]*)\Z")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_row(line: str) -> list[str]:
    # Staged recheck commands escape their shell pipes as \|; those are cell data,
    # not Markdown delimiters, and are checked again after normalization.
    fields = re.split(r"(?<!\\)\|", line.strip())
    if len(fields) != 13 or fields[0].strip() or fields[-1].strip():
        raise ValueError(f"expected 11 columns, got {len(fields) - 2}: {line}")
    return [field.strip() for field in fields[1:-1]]


def registry_rows(path: Path) -> OrderedDict[str, list[str]]:
    rows: OrderedDict[str, list[str]] = OrderedDict()
    for line in path.read_text(encoding="utf-8").splitlines():
        if ROW_START.match(line):
            cells = split_row(line)
            row_id = cells[0]
            if row_id in rows:
                raise ValueError(f"duplicate id in {path}: {row_id}")
            rows[row_id] = cells
    return rows


def main() -> int:
    required = [STAGED_REGISTRY, LANE / "corpus/SOURCES.md"]
    required.extend(STAGED_ENTRIES / name for name in ENTRY_NAMES)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        print(json.dumps({"error": "missing inputs", "paths": missing}))
        return 2

    real_sources = LANE / "corpus/SOURCES.md"
    real_hash_before = sha256(real_sources)
    existing = registry_rows(real_sources)
    staged = registry_rows(STAGED_REGISTRY)

    citations: OrderedDict[str, list[str]] = OrderedDict()
    cited_ids: list[str] = []
    for name in ENTRY_NAMES:
        entry_path = STAGED_ENTRIES / name
        used_by = f"corpus/knowledge/{name}"
        ids: list[str] = []
        for line in entry_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("source:"):
                for row_id in SOURCE_ID.findall(line):
                    if row_id not in ids:
                        ids.append(row_id)
                    if row_id not in cited_ids:
                        cited_ids.append(row_id)
        citations[used_by] = ids

    absent = [row_id for row_id in cited_ids if row_id not in staged]
    collisions = [row_id for row_id in cited_ids if row_id in existing]
    if absent or collisions:
        print(json.dumps({"absent_staged_ids": absent, "id_collisions": collisions}))
        return 1

    append_rows: list[str] = []
    stripped: OrderedDict[str, dict[str, str]] = OrderedDict()
    used_by_changes: OrderedDict[str, dict[str, str]] = OrderedDict()
    pipe_violations: list[str] = []
    payload_absent: list[str] = []

    for row_id in cited_ids:
        cells = list(staged[row_id])
        original_recheck = cells[9]
        if " — " in original_recheck:
            cadence, prose = original_recheck.split(" — ", 1)
        else:
            cadence, prose = original_recheck, ""
        cadence = cadence.strip()
        if not CADENCE.fullmatch(cadence):
            raise ValueError(f"invalid normalized recheck for {row_id}: {cadence}")
        cells[9] = cadence
        cells[7] = "mined"
        admitted_users = [path for path, ids in citations.items() if row_id in ids]
        if not admitted_users:
            raise ValueError(f"no admitted entry cites {row_id}")
        original_used_by = cells[10]
        cells[10] = ", ".join(admitted_users)
        used_by_changes[row_id] = {"from": original_used_by, "to": cells[10]}
        stripped[row_id] = {
            "cadence": cadence,
            "prose": prose,
            "original_recheck": original_recheck,
        }
        if any(not cells[index] for index in (1, 4, 5, 6)):
            payload_absent.append(row_id)
        for header, cell in zip(HEADERS, cells):
            if "|" in cell or "\\|" in cell:
                pipe_violations.append(f"{row_id}:{header}")
        if len(cells) != 11:
            raise AssertionError(row_id)
        append_rows.append("| " + " | ".join(cells) + " |")

    if pipe_violations or payload_absent:
        print(json.dumps({"pipe_violations": pipe_violations, "payload_absent": payload_absent}))
        return 1

    # Parse the emitted rows once more before any mirror insertion.
    for line in append_rows:
        reparsed = split_row(line)
        if len(reparsed) != 11 or any("|" in cell or "\\|" in cell for cell in reparsed):
            raise ValueError(f"emitted row failed normalization: {line}")

    block = "\n".join(
        (
            "<!-- Scratch only: normalized rows for the three round-34 served-name/alias entries. -->",
            "| " + " | ".join(HEADERS) + " |",
            "|" + "|".join("---" for _ in HEADERS) + "|",
            *append_rows,
            "",
        )
    )
    (SEAT / "SOURCES.append.md").write_text(block, encoding="utf-8")

    stripped_md = ["# Stripped staged recheck prose", ""]
    for row_id, record in stripped.items():
        stripped_md.extend(
            (
                f"## {row_id} — normalized recheck `{record['cadence']}`",
                "",
                "```text",
                record["prose"],
                "```",
                "",
            )
        )
    (SEAT / "stripped-recheck.md").write_text("\n".join(stripped_md), encoding="utf-8")

    mirror_corpus = SEAT / "validate/corpus"
    if mirror_corpus.exists():
        shutil.rmtree(mirror_corpus)
    mirror_corpus.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(LANE / "corpus", mirror_corpus)
    mirror_knowledge = mirror_corpus / "knowledge"
    for name in ENTRY_NAMES:
        shutil.copy2(STAGED_ENTRIES / name, mirror_knowledge / name)

    real_hash_after = sha256(real_sources)
    if real_hash_after != real_hash_before:
        raise RuntimeError("real lane corpus/SOURCES.md changed during scratch transformation")

    receipt = {
        "scratch_only": True,
        "admitted_entries": list(citations),
        "cited_ids_in_order": cited_ids,
        "row_count": len(append_rows),
        "column_count": 11,
        "id_collisions": collisions,
        "absent_staged_ids": absent,
        "pipe_violations": pipe_violations,
        "payload_absent": payload_absent,
        "used_by_changes": used_by_changes,
        "stripped_recheck": stripped,
        "append_block": str(SEAT / "SOURCES.append.md"),
        "mirror_sources_pending_insertion": str(mirror_corpus / "SOURCES.md"),
        "mirror_admitted_entries": [str(mirror_knowledge / name) for name in ENTRY_NAMES],
        "real_sources_sha256_before": real_hash_before,
        "real_sources_sha256_after": real_hash_after,
    }
    (SEAT / "transform-receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "rows": len(append_rows),
                "ids": cited_ids,
                "id_collisions": collisions,
                "pipe_violations": pipe_violations,
                "payload_absent": payload_absent,
                "real_sources_unchanged": real_hash_before == real_hash_after,
                "mirror": str(mirror_corpus),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, AssertionError) as exc:
        print(f"transform error: {exc}")
        raise SystemExit(1)
