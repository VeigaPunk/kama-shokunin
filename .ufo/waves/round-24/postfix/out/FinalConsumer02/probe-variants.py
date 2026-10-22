#!/usr/bin/env python3
"""Bounded probes for the fleet-only-tree consumer.

P1: raw git answers for the fleet-held TREE token (bare, ^{commit}, ^{}).
P2: the same fixture with the tree REACHABLE from a fleet commit.
P3: the same fixture with the tree ABSENT from both stores.
Each run: before(2e254a17, sha ea51bc35) and after(92063cfc, sha b9be4f42).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer02")
CLONE = BASE / "clone"
AFTER = CLONE / "tools/report-landing-audit.py"
BEFORE_COMMIT = "2e254a1763a9c08aa07fc53081287f506c447d84"

GITENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
          "GIT_AUTHOR_NAME": "kama-shokunin",
          "GIT_COMMITTER_NAME": "kama-shokunin",
          "GIT_AUTHOR_EMAIL": "a@x", "GIT_COMMITTER_EMAIL": "a@x",
          "PATH": "/usr/bin:/bin"}


def git(repo, *args, stdin=None, check=True):
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                        "-C", str(repo), *args],
                       input=None if stdin is None else stdin.encode(),
                       capture_output=True, env=GITENV, timeout=30)
    if check and p.returncode != 0:
        raise SystemExit(f"git {args}: {p.stderr.decode()}")
    return p.stdout.decode("utf-8", "replace")


def build(tmp):
    tmp.mkdir(parents=True, exist_ok=True)
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


def run_tool(tool, lane, fleet, draft):
    cmd = [sys.executable, str(tool), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--rounds", "1",
           "--report", f"1={draft}", "--json", "--no-errata"]
    p = subprocess.run(cmd, capture_output=True, timeout=120)
    rec = {"exit": p.returncode,
           "stderr": p.stderr.decode("utf-8", "replace").strip()}
    try:
        doc = json.loads(p.stdout.decode("utf-8", "replace"))
        rec["kinds"] = sorted({d["kind"] for res in doc["results"]
                               for d in res["defects"]})
        rec["errata_invalid"] = doc["summary"].get("errata_invalid")
        rec["errata_rows"] = doc["summary"].get("errata_rows")
        rec["by_kind"] = doc["summary"].get("by_kind")
        rec["defects"] = [d for res in doc["results"] for d in res["defects"]]
        rec["required"] = [res.get("required") for res in doc["results"]]
    except Exception:
        rec["kinds"] = None
    return rec


def main():
    out = {}
    raw = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                          "-C", str(CLONE), "show",
                          f"{BEFORE_COMMIT}:tools/report-landing-audit.py"],
                         capture_output=True, env=GITENV, timeout=30).stdout
    with tempfile.TemporaryDirectory(prefix="fc02p-") as td:
        tmp = Path(td)
        bp = tmp / "before.py"
        bp.write_bytes(raw)
        out["before_sha256"] = hashlib.sha256(raw).hexdigest()
        out["after_sha256"] = hashlib.sha256(AFTER.read_bytes()).hexdigest()

        # P1 raw git answers
        lane, fleet, draft, a, blob, tree = build(tmp / "p1")
        out["p1_git_answers"] = {
            "tree": tree,
            "fleet_bare": git(fleet, "cat-file", "--batch-check",
                              stdin=tree + "\n").strip(),
            "fleet_peel_commit": git(fleet, "cat-file", "--batch-check",
                                     stdin=tree + "^{commit}\n").strip(),
            "fleet_deref": git(fleet, "cat-file", "--batch-check",
                               stdin=tree + "^{}\n").strip(),
            "lane_bare": git(lane, "cat-file", "--batch-check",
                             stdin=tree + "\n", check=False).strip(),
            "fleet_type": git(fleet, "cat-file", "-t", tree).strip(),
        }

        # P2 reachable tree in the fleet
        lane2, fleet2, draft2, a2, blob2, tree2 = build(tmp / "p2")
        commit2 = git(fleet2, "commit-tree", tree2,
                      stdin="tree holder\n").strip()
        git(fleet2, "update-ref", "refs/heads/master", commit2)
        out["p2_reachable_tree"] = {
            "tree": tree2, "fleet_commit": commit2,
            "reachable": tree2 in git(fleet2, "rev-list", "--objects", "--all"),
            "before": run_tool(bp, lane2, fleet2, draft2),
            "after": run_tool(AFTER, lane2, fleet2, draft2),
        }

        # P3 tree absent from both stores
        lane3, fleet3, draft3, a3, blob3, tree3 = build(tmp / "p3")
        objdir = Path(fleet3, git(fleet3, "rev-parse", "--git-path",
                                  "objects").strip())
        (objdir / tree3[:2] / tree3[2:]).unlink()
        out["p3_absent_tree"] = {
            "tree": tree3,
            "fleet_type_after_removal": git(fleet3, "cat-file", "-t", tree3,
                                            check=False).strip() or None,
            "before": run_tool(bp, lane3, fleet3, draft3),
            "after": run_tool(AFTER, lane3, fleet3, draft3),
        }
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
