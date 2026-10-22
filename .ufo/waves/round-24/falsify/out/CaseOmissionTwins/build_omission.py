#!/usr/bin/env python3
"""Independent rebuild of the OmissionTwins fixture family.

Written from the case notes in tests/report-audit/promisor-grid-expectations.json
(PG09/PG10/PG11/PG12) WITHOUT reusing promisor-grid.py's build() helper, so a
fixture flaw (accidental hole, accidental citation, wrong cut-off, wrong author,
promisor metadata that leaks into the verdict) shows up as a disagreement
between this construction and the grid's.

Offline only: local git plumbing, no network, no transport.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REL = ".ufo/reports/round-1/kama.md"
SOURCES = "# sources\n\nfixture: no registry rows\n"


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    e.update(extra)
    return e


def g(repo, *args, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=env(**extra))
    if check and p.returncode:
        raise SystemExit(f"git {' '.join(args)} in {repo}: rc={p.returncode} "
                         f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape")


def init(path):
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    g(path.parent, "init", "-q", "-b", "master", str(path))
    return path


def commit(repo, author, when, msg, path, content):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    g(repo, "add", "--", path)
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
      GIT_AUTHOR_DATE=f"@{when} +0000", GIT_COMMITTER_DATE=f"@{when} +0000")
    return g(repo, "rev-parse", "HEAD").strip()


def inventory(repo):
    out = g(repo, "--no-lazy-fetch", "cat-file", "--batch-all-objects",
            "--batch-check=%(objectname)")
    return set(out.split())


def missing(repo, root):
    out = g(repo, "--no-lazy-fetch", "rev-list", "--objects", "--missing=print",
            "--no-object-names", root)
    return sorted(l[1:] for l in out.split("\n") if l.startswith("?"))


def build_family(root, mark):
    """mark in {plain, lane_config, fleet_config, lane_marker}."""
    root = Path(root).resolve()
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    lane = init(root / "lane")
    fleet = init(root / "fleet")
    # lane: round-1 work at 1000, then a genuine extra round-1 commit at 1500
    (lane / "corpus").mkdir(parents=True, exist_ok=True)
    (lane / "corpus" / "SOURCES.md").write_text(SOURCES, encoding="utf-8")
    (lane / "f").write_text("fixture file\n", encoding="utf-8")
    g(lane, "add", "--", "corpus/SOURCES.md", "f")
    g(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: work",
      GIT_AUTHOR_NAME="kama-shokunin", GIT_COMMITTER_NAME="kama-shokunin",
      GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
      GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000")
    l1 = g(lane, "rev-parse", "HEAD").strip()
    l2 = commit(lane, "kama-shokunin", 1500, "round-1: more", "g", "more\n")
    # fleet: init, then the round-1 report at 2000 citing only l1
    commit(fleet, "fleet", 1900, "fleet: init", "notes.md", "notes\n")
    report = "\n".join(["# kama round 1", "", "## Landed changes", "",
                        f"- {l1}", ""])
    commit(fleet, "fleet", 2000, "round-1: report", REL, report)
    if mark == "lane_config":
        g(lane, "config", "remote.origin.promisor", "true")
        g(lane, "config", "extensions.partialclone", "origin")
        g(lane, "config", "remote.origin.url", str(root / "absent-remote.git"))
    elif mark == "fleet_config":
        g(fleet, "config", "remote.origin.promisor", "true")
        g(fleet, "config", "extensions.partialclone", "origin")
        g(fleet, "config", "remote.origin.url", str(root / "absent-remote.git"))
    elif mark == "lane_marker":
        g(lane, "repack", "-a", "-d", "-q")
        packs = sorted((Path(g(lane, "rev-parse", "--absolute-git-dir").strip())
                        / "objects" / "pack").glob("*.pack"))
        for pack in packs:
            pack.with_suffix(".promisor").write_bytes(b"")
    return {"lane": lane, "fleet": fleet, "l1": l1, "l2": l2, "mark": mark}


def facts(fx):
    lane, fleet = fx["lane"], fx["fleet"]
    out = {
        "mark": fx["mark"],
        "lane_log": g(lane, "log", "--format=%H %an %at %s", "master").split("\n"),
        "report_text": g(fleet, "show", f"HEAD:{REL}"),
        "report_first_add_at": g(fleet, "log", "--diff-filter=A", "--format=%at",
                                 "--", REL).split(),
        "lane_missing": missing(lane, "refs/heads/master"),
        "fleet_missing": missing(fleet, "HEAD"),
        "lane_promisor_config": g(lane, "config", "--get", "remote.origin.promisor",
                                  check=False).strip(),
        "fleet_promisor_config": g(fleet, "config", "--get", "remote.origin.promisor",
                                   check=False).strip(),
    }
    for name, sha in (("l1", fx["l1"]), ("l2", fx["l2"])):
        present = subprocess.run(
            ["git", "--no-lazy-fetch", "--no-replace-objects", "-C", str(lane),
             "cat-file", "-e", sha + "^{object}"], capture_output=True,
            env=env()).returncode == 0
        out[f"{name}_present"] = present
    out["remote_url"] = g(lane, "config", "--get", "remote.origin.url",
                          check=False).strip() or \
        g(fleet, "config", "--get", "remote.origin.url", check=False).strip()
    out["remote_exists"] = bool(out["remote_url"]) and \
        Path(out["remote_url"]).exists()
    return out


if __name__ == "__main__":
    root = Path(sys.argv[1])
    res = {}
    for mark in ("plain", "lane_config", "fleet_config", "lane_marker"):
        fx = build_family(root / mark, mark)
        res[mark] = facts(fx)
    print(json.dumps(res, indent=1))
