#!/usr/bin/env python3
"""FinalCase34 auxiliary probe: is the KNOWN missing-ID set restricted to the
selected root, or is it store-wide?

Target claim under test: restricting the opaque fallback to the selected root
must NOT restrict the known missing-ID set; an explicitly cited missing object
referenced by a PRESENT LOCAL OBJECT (not only by the audited root's history)
remains unknown (refusal, not proved absence).

Two arms over one fixture family, same pinned auditor, same argv as the grid:
  D1-referenced : a present DANGLING tree (not reachable from the audited
                  root) references the missing blob that the report cites.
                  Store-wide missing set -> exit 2 naming the blob.
                  Root-restricted missing set -> exit 1 (unresolved-full-hash).
  D1-unreferenced control : the identical fixture with the referencing tree
                  removed, so no present object references the missing blob.
                  Expected exit 1 (proved absence path) - it validates that
                  the D1 difference is caused by the reference, not by the
                  fixture.

Not a registered grid cell.  Grid helpers are imported from the pinned clone
so the fixture, the environment and the auditor argv are the grid's own.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase34/clone")
GRID = CLONE / "tests/report-audit/promisor-grid.py"
AUDITOR = CLONE / "tools/report-landing-audit.py"
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase34")
OUT = SCRATCH / "out"

spec = importlib.util.spec_from_file_location("pg", GRID)
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)


def build_fixture(root, tmp, dangling):
    lane = pg.init_repo(root, Path(tmp, "lane"))
    fleet = pg.init_repo(root, Path(tmp, "fleet"))
    # lane: one commit with a present file and the sources file
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
    # the blob the report cites, and which the store must not be able to serve
    m = pg.git(lane, "hash-object", "-w", "--stdin",
               data=b"dangling content\n").strip()
    premise = {}
    if dangling:
        # a PRESENT tree that is not reachable from the audited root and
        # references the missing blob
        t = pg.git(lane, "mktree", data=f"100644 blob {m}\tdangling\n".encode()).strip()
        premise["dangling_tree"] = t
    pg.drop_object(lane, m)
    premise["cited_blob"] = m
    premise["dangling_tree_present"] = (
        pg.object_exists(lane, premise["dangling_tree"]) if dangling else None)
    premise["cited_blob_served"] = pg.object_exists(lane, m)
    # fleet: the round-1 report cites the lane commit (Landed) and the missing
    # blob (Notes) - the same shape as the grid's c_missing_cited_blob_plain
    text = pg.report_text([l1], [f"blob {m}"])
    pg.publish(fleet, text, 2000)
    premise["lane_missing"] = pg.missing_objects(lane, "refs/heads/master")
    premise["fleet_missing"] = pg.missing_objects(fleet, "HEAD")
    premise["lane_promisor"] = pg.promisor_facts(lane)["promisor_backed"]
    premise["fleet_promisor"] = pg.promisor_facts(fleet)["promisor_backed"]
    return {"lane": lane, "fleet": fleet, "premise": premise}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    root = Path(pg.make_root())
    results = {}
    try:
        for name, dangling in (("D1-referenced", True),
                               ("D1-unreferenced-control", False)):
            tmp = Path(root, name)
            tmp.mkdir(parents=True, exist_ok=True)
            built = build_fixture(root, tmp, dangling)
            before = {"lane": pg.object_inventory(built["lane"]),
                      "fleet": pg.object_inventory(built["fleet"])}
            code, out, err, timed_out = pg.run_auditor(AUDITOR, built["lane"],
                                                       built["fleet"], tmp)
            after = {"lane": pg.object_inventory(built["lane"]),
                     "fleet": pg.object_inventory(built["fleet"])}
            acquired = {k: sorted(after[k] - before[k]) for k in after}
            try:
                doc = json.loads(out) if out.strip() else None
            except ValueError:
                doc = None
            kinds = None
            if doc:
                kinds = sorted({d["kind"] for r in doc.get("results", [])
                                for d in r.get("defects", [])})
            results[name] = {
                "argv": [sys.executable, str(AUDITOR), "--lane-repo",
                         str(built["lane"]), "--fleet-repo",
                         str(built["fleet"]), "--rounds", "1", "--json",
                         "--no-errata"],
                "auditor_sha256": pg.hashlib.sha256(
                    AUDITOR.read_bytes()).hexdigest(),
                "exit": code, "timed_out": timed_out,
                "stdout_bytes": len(out), "stderr": err.strip(),
                "kinds": kinds, "document": doc,
                "objects_acquired": acquired,
                "premise": built["premise"],
                "internal_error": "could-not-evaluate: internal:" in err,
                "traceback": "Traceback (most recent call last)" in err,
            }
    finally:
        shutil.rmtree(root, ignore_errors=True)
    (OUT / "probe-dangling.json").write_text(
        json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    for name, r in results.items():
        print("==", name, "exit", r["exit"], "kinds", r["kinds"],
              "acquired", r["objects_acquired"])
        print("   stderr:", r["stderr"][:400])
        print("   premise:", json.dumps(r["premise"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
