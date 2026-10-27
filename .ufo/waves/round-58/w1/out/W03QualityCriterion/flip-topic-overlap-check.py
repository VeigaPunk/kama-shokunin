#!/usr/bin/env python3
"""flip-topic-overlap-check.py — draft KQ98 check (W03QualityCriterion, round 58).

Grades a SOURCES row rejected on an overlap/redundancy ground: for every topic
named in the row's flip condition, is that topic located in the *committed copy
of the overlapping source*?  A redundancy rejection is supported only when every
flip topic is located there.  Otherwise the rejected source holds scope the
overlap does not, and the rejection must be recorded as claim-scoped with the
flip delta named (`claim-scoped` and `flip-delta:` in the teaches cell), or the
row must be re-admitted with narrowed scope.

Exit: 0 = graded met=True, 1 = graded met=False, 2 = input/usage error.
No network, no writes; stdout only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SPLIT_TOPIC = re.compile(r",\s*|\s+or\s+")
LEAD = re.compile(r"^(a future claim about|a later claim on|a future claim on|or)\s+", re.I)


def fail(msg):
    print(json.dumps({"error": msg}, sort_keys=True))
    sys.exit(2)


def read_lines(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        fail(f"cannot read {path}: {exc}")


def parse_row(sources_path, row_id):
    lines = read_lines(sources_path)
    header = None
    header_at = None
    for idx, line in enumerate(lines):
        if line.startswith("| id |") and "teaches" in line:
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            header_at = idx
            break
    if header is None:
        fail(f"{sources_path}: no SOURCES header row found")
    for col in ("id", "teaches", "status", "anchor", "source"):
        if col not in header:
            fail(f"{sources_path}: header lacks column {col!r}")
    row = None
    for idx, line in enumerate(lines):
        if idx <= header_at or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != len(header):
            continue
        if cells[header.index("id")] == row_id:
            row = dict(zip(header, cells))
            row["_line"] = idx + 1
            break
    if row is None:
        fail(f"{sources_path}: row {row_id} not found")
    return row


def flip_topics(teaches):
    if "flip:" not in teaches:
        return []
    tail = teaches.split("flip:")[-1].split(";")[0].strip().rstrip(".")
    topics = []
    for part in SPLIT_TOPIC.split(tail):
        part = LEAD.sub("", part.strip().strip("`")).strip()
        if part:
            topics.append(part)
    return topics


def hits(lines, needles):
    found = []
    lowered = [line.lower() for line in lines]
    for needle in needles:
        needle = needle.lower()
        for idx, line in enumerate(lowered):
            if needle in line:
                found.append(idx + 1)
    return sorted(set(found))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True, help="committed corpus/SOURCES.md copy")
    ap.add_argument("--row-id", required=True)
    ap.add_argument("--needles", required=True,
                    help="JSON object: flip topic -> needle string or list of needles")
    ap.add_argument("--rejected-copy", required=True, help="committed copy of the rejected source")
    ap.add_argument("--overlap-copy", required=True, help="committed copy of the overlapping source")
    ap.add_argument("--overlap-row", default=None, help="expected overlapping row id")
    args = ap.parse_args()

    row = parse_row(args.sources, args.row_id)
    teaches = row["teaches"]
    status = row["status"]
    topics = flip_topics(teaches)
    try:
        needle_map = json.loads(args.needles)
    except json.JSONDecodeError as exc:
        fail(f"--needles is not JSON: {exc}")
    if not isinstance(needle_map, dict):
        fail("--needles must be a JSON object")

    rejected = read_lines(args.rejected_copy)
    overlap = read_lines(args.overlap_copy)

    missing = [t for t in topics if t not in needle_map]
    if missing:
        fail(f"no needle recorded for flip topic(s): {missing}")

    graded = []
    for topic in topics:
        raw = needle_map[topic]
        needles = [raw] if isinstance(raw, str) else list(raw)
        rec = {
            "topic": topic,
            "needles": needles,
            "rejected_hits": hits(rejected, needles),
            "overlap_hits": hits(overlap, needles),
        }
        if rec["overlap_hits"]:
            rec["class"] = "covered-by-overlap"
        elif rec["rejected_hits"]:
            rec["class"] = "delta"
        else:
            rec["class"] = "unlocated"
        graded.append(rec)

    delta = [g["topic"] for g in graded if g["class"] == "delta"]
    unlocated = [g["topic"] for g in graded if g["class"] == "unlocated"]
    supported = bool(graded) and all(g["class"] == "covered-by-overlap" for g in graded)
    claim_scoped = "claim-scoped" in teaches
    listed = []
    if "flip-delta:" in teaches:
        listed = [p.strip().strip(".") for p in SPLIT_TOPIC.split(teaches.split("flip-delta:")[-1].split(";")[0])]
        listed = [p for p in listed if p]
    delta_listed = bool(delta) and all(t in listed for t in delta)

    if status != "rejected":
        met, path, reason = False, "none", f"status={status} is not a rejection"
    elif not topics:
        met, path, reason = False, "none", "no-flip-to-check"
    elif unlocated:
        met, path, reason = False, "none", "unlocated:" + ",".join(unlocated)
    elif supported:
        met, path, reason = True, "redundancy", "every-flip-topic-covered-by-overlap"
    elif claim_scoped and delta_listed:
        met, path, reason = True, "claim-scoped", "delta-recorded"
    elif claim_scoped:
        met, path, reason = False, "none", "delta-not-recorded"
    else:
        met, path, reason = False, "none", "blanket-overlap-rejection"

    if args.overlap_row and args.overlap_row not in teaches:
        met, path, reason = False, "none", f"overlap-row-{args.overlap_row}-not-named"

    out = {
        "row": args.row_id,
        "row_line": row["_line"],
        "status": status,
        "overlap_row": args.overlap_row,
        "flip_topics": topics,
        "topics": graded,
        "supported_by_redundancy": supported,
        "delta": delta,
        "unlocated": unlocated,
        "claim_scoped": claim_scoped,
        "delta_listed": delta_listed,
        "path": path,
        "met": met,
        "reason": reason,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    print(f"row={args.row_id} status={status} topics={len(topics)} "
          f"supported={int(supported)} delta={len(delta)} unlocated={len(unlocated)} "
          f"path={path} met={met}")
    sys.exit(0 if met else 1)


if __name__ == "__main__":
    main()
