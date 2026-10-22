#!/usr/bin/env python3
"""FinalCase34 probe arm D2: the same question for a second kind of present
local object - a present TAG object (not reachable from the audited root)
that references the missing blob the report cites.

  D2-tag-referenced : present dangling tag -> missing blob cited by the
                      report.  Store-wide missing set -> exit 2 naming the
                      blob.  Root-restricted set -> exit 1.
  D2-tag-control    : the same fixture with the tag object removed, so no
                      present object references the missing blob -> exit 1.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase34/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDITOR = CLONE / "tools/report-landing-audit.py"
OUT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase34/out")

spec = importlib.util.spec_from_file_location("pg", GRID)
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)


def build_fixture(root, tmp, with_tag):
    lane = pg.init_repo(root, Path(tmp, "lane"))
    fleet = pg.init_repo(root, Path(tmp, "fleet"))
    for pth, content in (("corpus/SOURCES.md", pg.SOURCES), ("f", "fixture file\n")):
        target = Path(lane, pth)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    pg.git(lane, "add", "--", "corpus/SOURCES.md", "f")
    pg.git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
           "round-1: work", GIT_AUTHOR_NAME="kama-shokunin",
           GIT_COMMITTER_NAME="kama-shokunin", GIT_AUTHOR_DATE="@1000 +0000",
           GIT_COMMITTER_DATE="@1000 +0000")
    l1 = pg.git(lane, "rev-parse", "HEAD").strip()
    m = pg.git(lane, "hash-object", "-w", "--stdin",
               data=b"tagged content\n").strip()
    tag = None
    if with_tag:
        tag = pg.git(lane, "mktag", data=(
            f"object {m}\ntype blob\ntag dangling\n"
            "tagger k <a@x> 1000 +0000\n\ntag\n").encode()).strip()
    pg.drop_object(lane, m)
    premise = {"cited_blob": m, "tag": tag,
               "tag_present": pg.object_exists(lane, tag) if tag else None,
               "cited_blob_served": pg.object_exists(lane, m),
               "lane_missing_root": pg.missing_objects(lane, "refs/heads/master")}
    text = pg.report_text([l1], [f"blob {m}"])
    pg.publish(fleet, text, 2000)
    return {"lane": lane, "fleet": fleet, "premise": premise}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    root = Path(pg.make_root())
    results = {}
    try:
        for name, with_tag in (("D2-tag-referenced", True),
                               ("D2-tag-control", False)):
            tmp = Path(root, name)
            tmp.mkdir(parents=True, exist_ok=True)
            built = build_fixture(root, tmp, with_tag)
            before = {"lane": pg.object_inventory(built["lane"]),
                      "fleet": pg.object_inventory(built["fleet"])}
            code, out, err, timed_out = pg.run_auditor(AUDITOR, built["lane"],
                                                       built["fleet"], tmp)
            after = {"lane": pg.object_inventory(built["lane"]),
                     "fleet": pg.object_inventory(built["fleet"])}
            results[name] = {
                "exit": code, "timed_out": timed_out,
                "stdout_bytes": len(out), "stdout_raw": out,
                "stderr": err.strip(),
                "objects_acquired": {k: sorted(after[k] - before[k])
                                     for k in after},
                "premise": built["premise"],
                "internal_error": "could-not-evaluate: internal:" in err,
                "traceback": "Traceback (most recent call last)" in err,
            }
    finally:
        shutil.rmtree(root, ignore_errors=True)
    (OUT / "probe-dangling-tag.json").write_text(
        json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    for name, r in results.items():
        print("==", name, "exit", r["exit"], "stdout_bytes", r["stdout_bytes"],
              "acquired", r["objects_acquired"])
        print("   stderr:", r["stderr"][:400])
        print("   premise:", json.dumps(r["premise"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
