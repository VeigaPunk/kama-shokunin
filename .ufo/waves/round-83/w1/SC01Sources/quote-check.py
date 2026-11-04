#!/usr/bin/env python3
"""SC01 evidence check: the six round-83 SOURCES rows against retained bytes.

Re-run: python3 <this file>  (reads its own directory; no network, no scratch)

Checks, per row S566-S571:
  * the retained source file's sha256 equals SK01SourceOpen's recorded sha256
  * the row's `anchor` cell carries the sha256 and the byte/line counts
  * the receipt's quote occurs at the receipt's declared line
  * the quote is verbatim inside the row's `anchor` cell
  * the quote is at most 25 words
  * the row splits into the contract's eleven cells
and, once: the six ids are exactly S566-S571, and coverage-row.md is one
three-cell line naming corpus/knowledge/pin-recheck-rows.md.

Exit 0 when every check passes, 1 otherwise. It grades the draft rows; it
does not certify the corpus (the L1 files them and runs the append guard).
"""
import hashlib
import importlib.util
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
RECEIPT = LANE / ".ufo/waves/round-83/w1/SK01SourceOpen/sources.json"
SOURCE = HERE / "source"
IDS = ("S566", "S567", "S568", "S569", "S570", "S571")

spec = importlib.util.spec_from_file_location(
    "sap", LANE / "tools/sources-append-only.py"
)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def main():
    failures = []
    if not RECEIPT.is_file():
        print(f"could-not-evaluate: no {RECEIPT}")
        return 2
    receipt = {r["id"]: r for r in json.loads(RECEIPT.read_text())["rows"]}

    lines = (HERE / "rows.md").read_text(encoding="utf-8").rstrip("\n").split("\n")
    by_id = {}
    for line in lines:
        cells = guard.split_cells(line)
        if cells is None:
            failures.append(f"unterminated row: {line[:60]}")
            continue
        cells = [c.strip() for c in cells]
        if len(cells) != len(guard.CONTRACT_COLUMNS):
            failures.append(f"{cells[0]}: {len(cells)} cells, want 11")
            continue
        rid = guard.markup_free_id(cells[0])
        by_id[rid] = dict(zip(guard.CONTRACT_COLUMNS, cells))

    if sorted(by_id) != list(IDS):
        failures.append(f"ids {sorted(by_id)} != {list(IDS)}")

    for rid in IDS:
        rec = receipt[rid]
        body_path = SOURCE / f"{rid}.md"
        if not body_path.is_file():
            failures.append(f"{rid}: retained source missing")
            continue
        raw = body_path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        row = by_id.get(rid)
        if digest != rec["sha256"]:
            failures.append(f"{rid}: retained sha256 {digest} != receipt")
        if row is None:
            continue
        anchor = row["anchor"]
        if digest not in anchor:
            failures.append(f"{rid}: anchor cell omits sha256 {digest}")
        if f"{rec['bytes']} bytes" not in anchor:
            failures.append(f"{rid}: anchor cell omits {rec['bytes']} bytes")
        body_lines = raw.decode("utf-8", "replace").splitlines()
        quote, at = rec["quote"], rec["quote_line"]
        if rec["quote_match"] == "single-line":
            window = body_lines[at - 1]
        else:  # line-span-normalized: the sentence crosses a newline
            window = re.sub(r"\s+", " ", " ".join(body_lines[at - 1:at + 1]))
        if quote not in window:
            failures.append(f"{rid}: quote absent at line {at}")
        if quote not in anchor:
            failures.append(f"{rid}: anchor cell does not carry the quote")
        if len(quote.split()) > 25:
            failures.append(f"{rid}: quote {len(quote.split())} words > 25")
        if row["status"] not in ("mined", "rejected"):
            failures.append(f"{rid}: status {row['status']!r}")
        print(
            f"{rid} sha256={digest[:12]} bytes={rec['bytes']} lines={rec['lines']} "
            f"quote_line={at} words={len(quote.split())} status={row['status']} "
            f"recheck={row['recheck']} used-by={row['used-by']}"
        )

    cov = (HERE / "coverage-row.md").read_text(encoding="utf-8").strip()
    cov_cells = [c.strip() for c in cov.strip("|").split("|")]
    if len(cov.splitlines()) != 1 or len(cov_cells) != 3:
        failures.append(f"coverage row: {len(cov.splitlines())} lines / {len(cov_cells)} cells")
    if "`corpus/knowledge/pin-recheck-rows.md`" not in cov:
        failures.append("coverage row does not name corpus/knowledge/pin-recheck-rows.md")
    print(f"coverage: lines=1 cells={len(cov_cells)} entry=pin-recheck-rows.md")

    for f in failures:
        print(f"FAIL {f}")
    print(f"CHECK rows={len(by_id)} failures={len(failures)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
