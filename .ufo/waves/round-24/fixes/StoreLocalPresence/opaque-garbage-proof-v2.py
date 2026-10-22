#!/usr/bin/env python3
"""Bounded proof v2 for the opaque-garbage case (CodePerRunCache F2).

v2 differs from v1 (opaque-garbage-proof.py, kept filed unmodified) in the
OBSERVER only:

* the match is STRICT: the exit AND the exact finding kinds must equal the
  declared expectation (v1 compared the exit alone);
* the before side is extracted from the FULL pinned commit
  2e254a1763a9c08aa07fc53081287f506c447d84 with the auditor's isolation
  (--no-replace-objects --no-lazy-fetch) and checked against the known
  baseline sha256 before it is written to a temporary file;
* `--after PATH` is REQUIRED: there is no default proposal to go stale;
* the fixture cites the valid work commit, so no unrelated
  `landed-omitted` finding can mask the finding under test;
* the JSON retains the raw kinds of both sides, both source sha256s and
  the CID of the deleted tree.

Fixture: the lane holds a dangling PRESENT commit that names a real tree
object the store cannot serve (the tree is deleted, its blob stays present).
No ref reaches the commit or the tree; the selected root is complete. The
report cites the valid work commit and an ordinary fabricated hash.

Expected (the original local contract): exit 1 with the fabricated hash as
the only `unresolved-full-hash` finding. The pinned 2e254a17 tool refuses
it (exit 2: the unreachable hole is treated as opaque); the candidate scopes
the opaque fallback to the audited root and reports the ordinary finding.

Usage: python3 opaque-garbage-proof-v2.py --after PATH [--json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
# .ufo/waves/round-24/fixes/StoreLocalPresence/ -> the lane repository root
LANE_ROOT = HERE.parents[4]
PINNED_COMMIT = "2e254a1763a9c08aa07fc53081287f506c447d84"
PINNED_PATH = "tools/report-landing-audit.py"
BASELINE_SHA256 = ("ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220")
FAKE = "1234567890abcdef1234567890abcdef12345678"
EXPECTED = {"exit": 1, "kinds": ["unresolved-full-hash"], "errata_invalid": 0}


def git(repo, *args, stdin=None):
    env = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "kama-shokunin",
           "GIT_COMMITTER_NAME": "kama-shokunin", "GIT_AUTHOR_EMAIL": "a@x",
           "GIT_COMMITTER_EMAIL": "a@x", "PATH": "/usr/bin:/bin"}
    out = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                          "-C", str(repo), *args],
                         input=None if stdin is None else stdin.encode(),
                         capture_output=True, env=env, timeout=30)
    if out.returncode != 0:
        raise SystemExit(f"git {args}: "
                         f"{out.stderr.decode('utf-8', 'replace').strip()}")
    return out.stdout.decode("utf-8", "replace")


def fixture(tmp):
    lane, fleet = Path(tmp, "lane"), Path(tmp, "fleet")
    for repo in (lane, fleet):
        repo.mkdir()
        git(repo, "init", "-q", "-b", "master")
    Path(lane, "f").write_text("work\n", encoding="utf-8")
    git(lane, "add", "f")
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: work")
    a = git(lane, "rev-parse", "HEAD").strip()
    report = fleet / ".ufo/reports/round-1/kama.md"
    report.parent.mkdir(parents=True)
    report.write_text("## Landed changes\n", encoding="utf-8")
    git(fleet, "add", ".ufo/reports/round-1/kama.md")
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: kama report")
    blob = git(lane, "hash-object", "-w", "--stdin", stdin="kept\n").strip()
    tree = git(lane, "mktree", stdin=f"100644 blob {blob}\tkeep\n").strip()
    commit = git(lane, "commit-tree", tree, "-m", "dangling").strip()
    objects = Path(lane, git(lane, "rev-parse", "--git-path",
                             "objects").strip())
    (objects / tree[:2] / tree[2:]).unlink()      # the tree cannot be served
    draft = Path(tmp, "draft.md")
    # the valid work commit is cited: the only finding is the fabricated hash
    draft.write_text("## Work performed\n" + FAKE + "\n"
                     "## Landed changes\n- `" + a + "` work\n",
                     encoding="utf-8")
    return lane, fleet, draft, tree, commit


def run_tool(tool, lane, fleet, draft):
    proc = subprocess.run(
        [sys.executable, str(tool), "--lane-repo", str(lane), "--fleet-repo",
         str(fleet), "--branch", "master", "--rounds", "1", "--report",
         f"1={draft}", "--no-errata", "--json"],
        capture_output=True, timeout=60)
    kinds, errata_invalid = [], None
    if proc.returncode in (0, 1):
        doc = json.loads(proc.stdout.decode("utf-8", "replace"))
        kinds = sorted({d["kind"] for res in doc["results"]
                        for d in res["defects"]})
        errata_invalid = doc["summary"].get("errata_invalid")
    reason = ""
    if proc.returncode == 2:
        lines = proc.stderr.decode("utf-8", "replace").strip().splitlines()
        reason = lines[-1] if lines else ""
    return {"exit": proc.returncode, "kinds": kinds,
            "errata_invalid": errata_invalid, "reason": reason[:200]}


def strict_match(observed, expected):
    """Every declared field must agree: the exit, the exact finding kinds
    and errata_invalid. An exit alone is not a match."""
    return (observed["exit"] == expected["exit"]
            and observed["kinds"] == sorted(expected["kinds"])
            and observed["errata_invalid"] == expected["errata_invalid"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--after", required=True,
                    help="the tool to bind as the after side (required)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    raw = subprocess.run(
        ["git", "--no-replace-objects", "--no-lazy-fetch", "-C", str(LANE_ROOT),
         "show", f"{PINNED_COMMIT}:{PINNED_PATH}"],
        capture_output=True, timeout=30,
        env={"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
             "PATH": "/usr/bin:/bin"}).stdout
    before_sha = hashlib.sha256(raw).hexdigest()
    if before_sha != BASELINE_SHA256:
        print(f"input error: pinned before sha256 {before_sha} != baseline "
              f"{BASELINE_SHA256}", file=sys.stderr)
        return 2
    after = Path(args.after).resolve()
    if not after.is_file():
        print(f"input error: --after is not a file: {after}", file=sys.stderr)
        return 2
    after_sha = hashlib.sha256(after.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="opaque-proof-v2-") as tmp:
        before = Path(tmp, "before.py")
        before.write_bytes(raw)
        lane, fleet, draft, tree, commit = fixture(tmp)
        row = {"case": "unreachable-opaque-garbage",
               "match_rule": "exit AND exact kinds AND errata_invalid",
               "expected": EXPECTED,
               "dangling_commit": commit, "deleted_tree": tree,
               "fabricated_hash": FAKE,
               "before": {"source_sha256": before_sha,
                          **run_tool(before, lane, fleet, draft)},
               "after": {"source_sha256": after_sha,
                         **run_tool(after, lane, fleet, draft)}}
    row["before"]["matches_expectation"] = strict_match(row["before"],
                                                         EXPECTED)
    row["after"]["matches_expectation"] = strict_match(row["after"], EXPECTED)
    if args.json:
        print(json.dumps(row, indent=1, sort_keys=True))
    else:
        print(f"{row['case']}: dangling commit {commit[:12]} names the "
              f"deleted tree {tree[:12]}")
        print(f"  expected exit={EXPECTED['exit']} kinds={EXPECTED['kinds']} "
              f"errata_invalid={EXPECTED['errata_invalid']}")
        for side in ("before", "after"):
            cell = row[side]
            print(f"  {side:6s} exit={cell['exit']} kinds={cell['kinds']} "
                  f"errata_invalid={cell['errata_invalid']} "
                  f"match={cell['matches_expectation']} {cell['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
