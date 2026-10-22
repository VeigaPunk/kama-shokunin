#!/usr/bin/env python3
"""Independent reconstruction of the fleet-only-tree fixture.

Rebuilds the driver scenario WITHOUT importing the driver, so the fixture's
actual Git object types and presence are observed directly, and runs both
the pinned BEFORE (2e254a17) and the pinned AFTER (92063cfc) tool on it with
raw --json output.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer02")
CLONE = BASE / "clone"
AFTER = CLONE / "tools/report-landing-audit.py"
BEFORE_COMMIT = "2e254a1763a9c08aa07fc53081287f506c447d84"
BEFORE_PATH = "tools/report-landing-audit.py"
BASELINE_SHA256 = "ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220"

GITENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
          "GIT_AUTHOR_NAME": "kama-shokunin",
          "GIT_COMMITTER_NAME": "kama-shokunin",
          "GIT_AUTHOR_EMAIL": "a@x", "GIT_COMMITTER_EMAIL": "a@x",
          "PATH": "/usr/bin:/bin"}


def git(repo, *args, stdin=None):
    out = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                          "-C", str(repo), *args],
                         input=None if stdin is None else stdin.encode(),
                         capture_output=True, env=GITENV, timeout=30)
    if out.returncode != 0:
        raise SystemExit(f"git {args} failed: {out.stderr.decode()}")
    return out.stdout.decode()


def cat_type(repo, oid):
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                        "-C", str(repo), "cat-file", "-t", oid],
                       capture_output=True, env=GITENV, timeout=30)
    if p.returncode != 0:
        return None
    return p.stdout.decode().strip()


def cat_body(repo, oid):
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                        "-C", str(repo), "cat-file", "-p", oid],
                       capture_output=True, env=GITENV, timeout=30)
    if p.returncode != 0:
        return None
    return p.stdout.decode("utf-8", "replace")


def build(tmp):
    lane, fleet = tmp / "lane", tmp / "fleet"
    for repo in (lane, fleet):
        repo.mkdir()
        git(repo, "init", "-q", "-b", "master")
    (lane / "f").write_text("work\n", encoding="utf-8")
    git(lane, "add", "f")
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: work")
    a = git(lane, "rev-parse", "HEAD").strip()
    report = fleet / ".ufo/reports/round-1/kama.md"
    report.parent.mkdir(parents=True)
    report.write_text("## Landed changes\n", encoding="utf-8")
    git(fleet, "add", ".ufo/reports/round-1/kama.md")
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: kama report")
    blob = git(fleet, "hash-object", "-w", "--stdin",
               stdin="fleet only blob\n").strip()
    tree = git(fleet, "mktree", stdin=f"100644 blob {blob}\tf\n").strip()
    draft = tmp / "draft.md"
    draft.write_text("## Landed changes\n- `" + a + "` work\n- `" + tree
                     + "` under test\n", encoding="utf-8")
    return lane, fleet, draft, a, blob, tree


def run_tool(tool, lane, fleet, draft, extra):
    cmd = [sys.executable, str(tool), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--rounds", "1",
           "--report", f"1={draft}", "--json"] + extra
    p = subprocess.run(cmd, capture_output=True, timeout=120)
    doc = None
    try:
        doc = json.loads(p.stdout.decode("utf-8", "replace"))
    except Exception:
        pass
    return p.returncode, p.stdout.decode("utf-8", "replace"), \
        p.stderr.decode("utf-8", "replace"), doc


def main():
    out = {"note": "independent fixture reconstruction; driver not imported"}
    raw = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                          "-C", str(CLONE), "show",
                          f"{BEFORE_COMMIT}:{BEFORE_PATH}"],
                         capture_output=True, env=GITENV, timeout=30).stdout
    out["before_source_sha256"] = hashlib.sha256(raw).hexdigest()
    out["before_source_sha256_matches_contract"] = \
        out["before_source_sha256"] == BASELINE_SHA256
    out["after_source_sha256"] = hashlib.sha256(AFTER.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="fc02-") as td:
        tmp = Path(td)
        before_path = tmp / "before-report-landing-audit.py"
        before_path.write_bytes(raw)
        lane, fleet, draft, a, blob, tree = build(tmp)
        out["fixture"] = {
            "lane_commit_a": a,
            "fleet_blob": blob,
            "fleet_tree": tree,
            "draft": draft.read_text(encoding="utf-8"),
            "tree_type_in_fleet": cat_type(fleet, tree),
            "tree_type_in_lane": cat_type(lane, tree),
            "blob_type_in_fleet": cat_type(fleet, blob),
            "blob_type_in_lane": cat_type(lane, blob),
            "lane_commit_type_in_lane": cat_type(lane, a),
            "lane_commit_type_in_fleet": cat_type(fleet, a),
            "tree_body_in_fleet": cat_body(fleet, tree),
            "tree_reachable_from_fleet_head": git(
                fleet, "rev-list", "--objects", "--all").find(tree) >= 0,
            "fleet_head": git(fleet, "rev-parse", "HEAD").strip(),
            "lane_head": git(lane, "rev-parse", "HEAD").strip(),
        }
        for label, tool in (("before", before_path), ("after", AFTER)):
            rc, so, se, doc = run_tool(tool, lane, fleet, draft, ["--no-errata"])
            rec = {"exit": rc, "stdout": so, "stderr": se}
            if doc is not None:
                rec["summary"] = doc.get("summary")
                rec["results"] = doc.get("results")
                rec["kinds"] = sorted({d["kind"] for res in doc.get("results", [])
                                       for d in res.get("defects", [])})
                rec["errata_invalid"] = doc.get("summary", {}).get("errata_invalid")
            out[label] = rec
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
