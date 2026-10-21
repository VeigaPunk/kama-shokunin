#!/usr/bin/env python3
"""Deterministic builder for the round-24 CaseUnknownCitation oracle case.

Scenario (one case, three arms):
  A-main    promisor-marked lane (filter-only promisor remote) + fleet report
            that cites a full 40-hex commit which is absent from BOTH audited
            repositories but PRESENT in the lane's promisor remote.
  B-control the same promisor lane + the same fleet report with the unknown
            citation removed.  Paired with A-main it proves that the exit-2
            of A-main is caused by the unknown citation and not by the
            promisor metadata (B-control must be a clean exit 0).
  C-full    promisor-marked lane (canonical `extensions.partialclone` +
            `remote.origin.promisor=true` + `remote.origin.partialclonefilter`)
            + the same unknown citation.  Same required outcome as A-main.

Everything is local and offline: no network transport, no script execution,
no fetch.  The promisor remote URL points at the local `origin/` repository,
which is never contacted; the audit must not fetch (asserted by the runner:
the lane must still lack O2 after the audit, and no new pack/FETCH_HEAD).

Usage: build_case.py --root DIR [--reset]

Every write goes through guard(), which refuses any path that is not under
the fixture root, so no fixture can escape the scratch tree.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

# ---- fixture constants (fixed so every build is byte-identical) -----------
O1_SUBJECT = "round-1: work"
O2_SUBJECT = "round-1: more"
O1_AUTHOR = "kama-shokunin"
O1_WHEN = 1000
O2_WHEN = 1500
FLEET_WHEN = 2000
REPORT_REL = ".ufo/reports/round-1/kama.md"
LANE = "kama"
ROUND = "1"


class BuildError(Exception):
    """The fixture could not be built as specified."""


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
             GIT_TERMINAL_PROMPT="0", GIT_ASKPASS="/bin/false",
             GIT_ALLOW_PROTOCOL="file")
    e.update(extra)
    return e


def git(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise BuildError(f"git {' '.join(map(str, args))} in {repo}: "
                         f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


class Builder:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.written = []

    def guard(self, path):
        """Refuse any write outside the fixture root."""
        p = Path(path).resolve()
        if p != self.root and self.root not in p.parents:
            raise BuildError(f"write escapes fixture root: {p}")
        return p

    def note(self, path):
        self.written.append(str(self.guard(path)))

    # -- git helpers ------------------------------------------------------
    def init(self, path):
        path = self.guard(path)
        if path.exists():
            raise BuildError(f"refusing to write into existing path: {path}")
        path.mkdir(parents=True)
        self.note(path)
        git(path, "-c", "init.defaultBranch=master", "init", "-q",
            "-b", "master", ".")
        git(path, "config", "user.name", "fixture")
        git(path, "config", "user.email", "a@x")
        git(path, "config", "commit.gpgsign", "false")
        git(path, "config", "core.hooksPath", "/dev/null")
        return path

    def commit(self, repo, author, when, subject, path="f", content=None):
        repo = Path(repo)
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        self.note(target)
        if content is None:
            with open(target, "ab") as fh:
                fh.write((subject + "\n").encode())
        else:
            target.write_bytes(content)
        git(repo, "add", "--", path)
        stamp = f"@{when} +0000"
        git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", subject,
            GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
            GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
        return git(repo, "rev-parse", "HEAD")

    def clone_dir(self, src, dst):
        """Local directory copy (no git transport, no hardlinks)."""
        src, dst = Path(src), self.guard(dst)
        if dst.exists():
            raise BuildError(f"refusing to write into existing path: {dst}")
        shutil.copytree(src, dst, symlinks=True)
        for p in sorted(dst.rglob("*")):
            self.note(p)
        return dst

    # -- fixture parts ----------------------------------------------------
    def build_origin(self):
        origin = self.init(self.root / "origin")
        o1 = self.commit(origin, O1_AUTHOR, O1_WHEN, O1_SUBJECT)
        return origin, o1

    def build_lane(self, origin, o1):
        """Lane repository holding O1 only; O2 is never fetched into it."""
        lane = self.clone_dir(origin, self.root / "lane")
        o2 = self.commit(origin, O1_AUTHOR, O2_WHEN, O2_SUBJECT)
        return lane, o2

    def mark_promisor(self, lane, origin, full):
        """Give the lane a promisor remote.

        full=True  -> canonical partial-clone configuration.
        full=False -> `remote.origin.partialclonefilter` only (git treats a
                      remote with a partialclone filter as a promisor remote:
                      a missing-object lookup would lazily fetch from it).
        """
        lane = Path(lane)
        git(lane, "config", "remote.origin.url", f"file://{origin}")
        git(lane, "config", "remote.origin.partialclonefilter", "blob:none")
        if full:
            git(lane, "config", "extensions.partialclone", "origin")
            git(lane, "config", "remote.origin.promisor", "true")
        return lane

    def side_commit(self, lane, tree):
        """A commit object that is in the lane's store but NOT reachable from
        the pinned root: `cat-file` resolves it, `rev-list --missing=print`
        never mentions it.

        This is the witness object for the store-positive / closure-negative
        citation: an implementation that decides "unknown citation" by
        enumerating the pinned-root closure instead of consulting the local
        object store answers exit 2 here, where the correct answer is
        "found" (a substantive verdict, no defect).
        """
        body = (f"tree {tree}\n"
                "author fixture <a@x> 900 +0000\n"
                "committer fixture <a@x> 900 +0000\n"
                "\nside object: present in the store, unreachable from master\n"
                ).encode()
        sha = git(lane, "hash-object", "-t", "commit", "-w", "--stdin",
                  data=body)
        return sha

    def build_fleet(self, name, report_text):
        fleet = self.init(self.root / name)
        self.commit(fleet, "fleet", FLEET_WHEN, "round-1: report",
                    REPORT_REL, report_text.encode())
        return fleet

    # -- report text ------------------------------------------------------
    @staticmethod
    def report(o1, extra_sha=None):
        head = (f"# kama round {ROUND}\n\n## Landed changes\n\n"
                f"- {o1} {O1_SUBJECT}\n")
        if extra_sha is None:
            return head + "\n## Notes\n\nno further citation\n"
        return head + f"\n## Notes\n\nalso cited commit {extra_sha}\n"


def build(root, reset=False):
    root = Path(root).resolve()
    if root.exists():
        if not reset:
            raise BuildError(f"fixture root exists: {root} (use --reset)")
        shutil.rmtree(root)
    root.mkdir(parents=True)
    b = Builder(root)
    origin, o1 = b.build_origin()
    lane, o2 = b.build_lane(origin, o1)

    lane_filter = b.clone_dir(lane, root / "lane-filter")
    lane_full = b.clone_dir(lane, root / "lane-full")
    b.mark_promisor(lane_filter, origin, full=False)
    b.mark_promisor(lane_full, origin, full=True)

    report_main = Builder.report(o1, o2)
    report_clean = Builder.report(o1, None)
    fleet_main = b.build_fleet("fleet", report_main)
    fleet_clean = b.build_fleet("fleet-clean", report_clean)

    # store-positive / closure-negative witness: the same body in both lanes
    # yields the same object id, so one fleet report can serve both.
    tree = git(lane_filter, "rev-parse", f"{o1}^{{tree}}")
    side_filter = b.side_commit(lane_filter, tree)
    side_full = b.side_commit(lane_full, tree)
    if side_filter != side_full:
        raise BuildError("side commit is not identical in both lanes")
    report_side = Builder.report(o1, side_filter)
    fleet_side = b.build_fleet("fleet-side", report_side)

    manifest = {
        "root": str(root),
        "o1_cited_local": o1,
        "o2_unknown_citation": o2,
        "side_commit_store_positive": side_filter,
        "report_rel": REPORT_REL,
        "arms": {
            "A-main": {"lane": str(lane_filter), "fleet": str(fleet_main),
                       "report": report_main},
            "B-control": {"lane": str(lane_filter),
                          "fleet": str(fleet_clean),
                          "report": report_clean},
            "C-full": {"lane": str(lane_full), "fleet": str(fleet_main),
                       "report": report_main},
            "D-store-lane": {"lane": str(lane_filter),
                             "fleet": str(fleet_side),
                             "report": report_side},
            "E-store-full": {"lane": str(lane_full),
                             "fleet": str(fleet_side),
                             "report": report_side},
        },
        "written_paths": sorted(set(b.written)),
    }
    (root / "manifest.json").write_text(json.dumps(manifest, indent=1,
                                                    sort_keys=True) + "\n")
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True)
    ap.add_argument("--reset", action="store_true")
    args = ap.parse_args(argv)
    try:
        m = build(args.root, args.reset)
    except BuildError as exc:
        print(f"build-error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({k: m[k] for k in ("root", "o1_cited_local",
                                        "o2_unknown_citation")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
