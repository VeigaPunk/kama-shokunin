#!/usr/bin/env python3
"""Grid-ready builder fragment for the round-24 CaseUnreachableCitation case.

Drop-in for tests/report-audit/promisor-grid.py (the round-24 measurement
harness) or for tests/report-audit/repo-state-grid.py. The builder follows
that harness's contract exactly:

    builder(tmp) -> (lane_repo, fleet_repo, argv_extra, marker_or_None)

where `lane_repo` and `fleet_repo` are repository paths, `argv_extra` is a
list of extra auditor arguments, and `marker` is a path whose existence
means a repository-local program was executed (None here: this fixture
configures no program, no transport and no payload).

Two cases are derived from one fixture family, differing only in the lane's
promisor metadata:

  P01-unreachable-citation-full       lane without promisor metadata
                                      CONTROL: exit 0, no defects
  P02-unreachable-citation-promisor   the same lane, marked promisor by
                                      config only, every object still local
                                      TARGET: exit 0, no defects

Expected exits/findings are fixed BEFORE implementation (see
advice/CaseUnreachableCitation.md). The r23 base returns exit 2 on P02 with
"partial clone (extensions.partialclone)"; that blanket refusal is the harm
the round-24 repair removes, while P01 must stay exactly as it is.

Offline guarantee: the promisor remote URL points at a NON-EXISTENT local
path under the scratch root, every git call in this fragment passes
--no-lazy-fetch, and no program payload (core.sshCommand, gpg.program,
filter transport hook) is configured. No fixture file is written outside the
scratch root.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess

ABSENT_ORIGIN_NAME = "absent-origin.git"   # deliberately never created


def _env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def _g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), *args],
                       input=data, capture_output=True, env=_env(**extra))
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(map(str, args))}: "
                           f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def _init(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    _g(path.parent, "init", "-q", "-b", "master", str(path))
    _g(path, "config", "gc.auto", "0")
    _g(path, "config", "user.name", "fixture")
    _g(path, "config", "user.email", "a@x")
    return path


def _commit(repo, author, when, msg, path="f", content=None):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(target, "ab") as fh:
            fh.write((msg + "\n").encode())
    else:
        target.write_bytes(content)
    _g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    _g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
       GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
       GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return _g(repo, "rev-parse", "HEAD")


def _raw_commit(repo, tree, parents, message, when, author="kama-shokunin"):
    """A commit object with no ref pointing at it."""
    body = b"tree " + tree.encode() + b"\n"
    for p in parents:
        body += b"parent " + p.encode() + b"\n"
    who = author.encode() + b" <a@x> " + str(when).encode() + b" +0000"
    body += b"author " + who + b"\ncommitter " + who + b"\n\n" + message
    return _g(repo, "hash-object", "-t", "commit", "-w", "--stdin", data=body)


def _prefix(repo, sha):
    """Shortest >=9-hex prefix that is checkable (digit AND letter) and
    unambiguous; the auditor only treats such a token as a citation."""
    for size in range(9, 41):
        token = sha[:size]
        if not (re.search(r"[0-9]", token) and re.search(r"[a-f]", token)):
            continue
        answer = _g(repo, "cat-file", "--batch-check",
                    data=(token + "\n").encode())
        if answer.startswith(sha) and "ambiguous" not in answer:
            return token
    return sha


def _mark_promisor(lane: Path, absent_origin: Path):
    _g(lane, "config", "extensions.partialClone", "origin")
    _g(lane, "config", "remote.origin.promisor", "true")
    _g(lane, "config", "remote.origin.partialclonefilter", "blob:none")
    _g(lane, "config", "remote.origin.url", str(absent_origin))
    _g(lane, "config", "remote.origin.fetch",
       "+refs/heads/*:refs/remotes/origin/*")


def _build(tmp, promisor: bool):
    tmp = Path(tmp)
    lane, fleet = _init(tmp / "lane"), _init(tmp / "fleet")
    c1 = _commit(lane, "kama-shokunin", 1000, "round-1: work")
    c2 = _commit(lane, "kama-shokunin", 1500, "round-1: more", "f2")
    tree = _g(lane, "rev-parse", f"{c2}^{{tree}}")
    x1 = _raw_commit(lane, tree, [c2], b"round-1: dangling\n", 1600)
    x2 = _raw_commit(lane, tree, [c2], b"round-1: kept\n", 1700)
    _g(lane, "update-ref", "refs/keep/x2", x2)
    prefix = _prefix(lane, c1)
    body = ("# kama round 1\n\n## Landed changes\n\n"
            f"- `{prefix}` work\n- `{c2}` more\n"
            f"- `{x1}` dangling\n- `{x2}` kept off-branch\n").encode()
    _commit(fleet, "fleet", 2000, "round-1: report",
            ".ufo/reports/round-1/kama.md", body)
    if promisor:
        _mark_promisor(lane, tmp / ABSENT_ORIGIN_NAME)
    return lane, fleet


def p01_unreachable_citation_full(tmp):
    """CONTROL: identical lane without promisor metadata. Exit 0, no
    defects; the repair must not change this arm."""
    lane, fleet = _build(tmp, promisor=False)
    return lane, fleet, [], None


def p02_unreachable_citation_promisor(tmp):
    """TARGET: the same lane marked promisor by config only, with every
    cited object still present locally. Exit 0, no defects -- NOT exit 2."""
    lane, fleet = _build(tmp, promisor=True)
    return lane, fleet, [], None


# Expected rows for a promisor-grid.py CASES table
# (name, kind, builder, expected exit, expected defect kinds).
EXPECTED_CASES = [
    ("P01-unreachable-citation-full", "control", p01_unreachable_citation_full,
     0, []),
    ("P02-unreachable-citation-promisor", "control",
     p02_unreachable_citation_promisor, 0, []),
]

# The r23 base auditor (blob cf706c52) returns exit 2 on P02 with
# "partial clone (extensions.partialclone)". If the round-24 harness keeps a
# frozen=r23-base arm, that arm is EXPECTED to exit 1 on P02 (a policy-row
# expectation change, documented in the preregistration), while P01 stays 0.
