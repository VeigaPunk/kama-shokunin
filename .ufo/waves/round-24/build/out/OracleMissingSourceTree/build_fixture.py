#!/usr/bin/env python3
"""Build the OracleMissingSourceTree fixtures: a promisor-marked lane clone
whose SOURCES evidence is unavailable, and a content-complete control.

Offline only: no clone transport, no fetch, no network. The promisor remote
is an unroutable ssh URL whose core.sshCommand is a marker script, so any
attempted transport is recorded instead of attempted.

Usage: build_fixture.py ROOT
Writes ROOT/<variant>/{lane,fleet} and prints a JSON receipt on stdout.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

FOREIGN = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"
REL = ".ufo/reports/round-1/kama.md"
SOURCE_URL = ("https://github.com/ggml-org/llama.cpp/blob/" + FOREIGN
              + "/tools/server/README.md/#readme")
SOURCES_MD = (
    "## Registry\n"
    "| id | source | kind | tier | scope | anchor | teaches | status | "
    "opened | recheck | used-by |\n"
    "|---|---|---|---|---|---|---|---|---|---|---|\n"
    "| S001 | upstream — " + SOURCE_URL
    + " | code | A | fixture scope | fixture anchor | fixture teaches | mined "
    "| 2026-10-21 | on-release | — |\n")


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def git(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(map(str, args))}: "
                           f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path):
    path.mkdir(parents=True, exist_ok=True)
    git(path.parent, "init", "-q", "-b", "master", str(path))
    return path


def commit(repo, author, when, msg, path, content):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    git(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
        GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
        GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return git(repo, "rev-parse", "HEAD")


def build(root, variant, drop, with_sources=True):
    """drop: None | 'corpus-tree' | 'sources-blob'"""
    base = Path(root, variant)
    base.mkdir(parents=True, exist_ok=True)
    lane, fleet = init(base / "lane"), init(base / "fleet")
    l1 = commit(lane, "kama-shokunin", 1000, "round-1: work", "f",
                "work\n")
    # not a lane round commit: author is not <lane>-shokunin, so it is not a
    # required landed commit; it only carries the SOURCES tree.
    if with_sources:
        l2 = commit(lane, "fixture", 1100, "sources: registry",
                    "corpus/SOURCES.md", SOURCES_MD)
    else:
        l2 = l1
    corpus_tree = (git(lane, "rev-parse", f"{l2}:corpus") if with_sources
                   else None)
    sources_blob = (git(lane, "rev-parse", f"{l2}:corpus/SOURCES.md")
                    if with_sources else None)
    report = ("# kama round 1\n\n## Work performed\nmeasured at " + l1
              + "\nupstream " + SOURCE_URL + "\n\n"
              "## Landed changes\n- `" + l1 + "` work\n")
    commit(fleet, "fleet", 2000, "round-1: kama report", REL, report)
    # promisor metadata: config-only marking (no .promisor pack pair).
    # core.sshCommand records any transport attempt instead of performing it.
    marker = base / "transport-ran"
    script = base / "fake-ssh.sh"
    script.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 1\n", encoding="utf-8")
    script.chmod(0o755)
    git(lane, "config", "extensions.partialClone", "origin")
    git(lane, "config", "remote.origin.url", "ssh://example.invalid/x.git")
    git(lane, "config", "remote.origin.promisor", "true")
    git(lane, "config", "remote.origin.partialclonefilter", "blob:none")
    git(lane, "config", "core.sshCommand", str(script))
    dropped = None
    if drop:
        if drop == "corpus-tree":
            sha = corpus_tree
        elif drop == "sources-blob":
            sha = sources_blob
        elif drop == "root-tree":
            sha = git(lane, "rev-parse", "master^{tree}")
        else:
            raise RuntimeError(f"unknown drop kind {drop}")
        path = Path(lane, ".git/objects", sha[:2], sha[2:])
        if not path.exists():
            raise RuntimeError(f"{variant}: object {sha} is not loose")
        path.unlink()
        dropped = {"kind": drop, "sha": sha,
                   "path": str(path.relative_to(lane))}
    return lane, fleet, {"l1": l1, "l2": l2, "corpus_tree": corpus_tree,
                         "sources_blob": sources_blob, "dropped": dropped,
                         "report": REL, "source_url": SOURCE_URL,
                         "foreign": FOREIGN}


def probe(lane, fleet, info):
    """Record the git behavior the auditor depends on."""
    out = {}
    def run(*args, **kw):
        p = subprocess.run(["git", "-C", str(lane), "--no-lazy-fetch",
                            "--no-replace-objects", *args],
                           capture_output=True, env=env())
        return {"rc": p.returncode,
                "out": p.stdout.decode(errors="replace").strip()[:400],
                "err": p.stderr.decode(errors="replace").strip()[:300]}
    out["ls-tree-sources"] = run("ls-tree", "master", "--",
                                  "corpus/SOURCES.md")
    out["ls-tree-root"] = run("ls-tree", "master")
    out["rev-parse-sources-path"] = run("rev-parse",
                                        "master:corpus/SOURCES.md")
    if info["sources_blob"]:
        out["cat-file-sources-blob"] = run("cat-file", "blob",
                                           info["sources_blob"])
        out["cat-file-corpus-tree"] = run("cat-file", "-t",
                                          info["corpus_tree"])
    out["rev-list-missing"] = run("rev-list", "--objects", "--missing=print",
                                  "--no-object-names", "master")
    out["log-format"] = run("log", "-z", "--format=%H%x00%an%x00%at%x00%s",
                             "master")
    out["cat-file-cited-commit"] = run("cat-file", "-t", info["l1"])
    out["show-object-format"] = run("rev-parse", "--show-object-format")
    out["show-prefix"] = run("rev-parse", "--show-prefix")
    out["is-shallow"] = run("rev-parse", "--is-shallow-repository")
    out["config-list"] = run("config", "--null", "--list")
    p = subprocess.run(["git", "-C", str(fleet), "show",
                        f"HEAD:.ufo/reports/round-1/kama.md"],
                       capture_output=True, env=env())
    out["fleet-report"] = {"rc": p.returncode,
                           "out": p.stdout.decode(errors="replace")[:200]}
    return out


def main(argv=None):
    if len(argv) < 2:
        print("usage: build_fixture.py ROOT", file=sys.stderr)
        return 2
    root = Path(argv[1]).resolve()
    root.mkdir(parents=True, exist_ok=True)
    receipt = {"root": str(root), "variants": {}}
    plan = (("A-corpus-tree-absent", "corpus-tree", True),
            ("B-sources-blob-absent", "sources-blob", True),
            ("C-content-complete-control", None, True),
            ("D-sources-path-never-committed", None, False),
            ("E-tip-tree-absent", "root-tree", True))
    for variant, drop, with_sources in plan:
        lane, fleet, info = build(root, variant, drop, with_sources)
        info["lane"] = str(lane)
        info["fleet"] = str(fleet)
        info["probe"] = probe(lane, fleet, info)
        info["transport_marker_present"] = (
            Path(root, variant, "transport-ran").exists())
        receipt["variants"][variant] = info
    print(json.dumps(receipt, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
