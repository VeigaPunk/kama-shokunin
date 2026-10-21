#!/usr/bin/env python3
"""Bounded offline fixture for the r24 oracle lane `OracleMissingNonrequired`.

Case: a lane repository that is promisor-marked (partial-clone metadata) and
holds a genuinely incomplete object (a missing blob) that is reachable ONLY
from an unselected, unrelated branch (`side`). The selected branch (`master`)
and the fleet repository are complete.

Question under test: must the audit refuse (exit 2) because the object graph
behind `--all` contains a missing object?  Expected answer: NO.  The audit's
evidence roots are the pinned selected lane branch tip and the pinned fleet
HEAD; a missing object outside those roots is not required evidence, so the
audit must return the same substantive verdict as an otherwise identical
complete repository (exit 0, clean, no findings).

The builder also emits an unmarked twin (identical content, promisor metadata
removed) which fixes the substantive expected verdict independently of any
candidate implementation, and a full-clone twin.

Nothing here touches the network: the "promisor" remote URL is a nonexistent
local path, all objects are created locally, and the incomplete object is
produced by deleting one loose object file.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REL = ".ufo/reports/round-1/kama.md"


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(map(str, args))}: "
                           f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    g(path.parent, "init", "-q", "-b", "master", str(path))
    return path


def commit(repo, author, when, msg, path, content):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def loose_path(repo, sha):
    return Path(repo, ".git", "objects", sha[:2], sha[2:])


def build(root: Path, marked: bool, fleet_marked: bool = False,
          missing_side: str = "lane", selected_missing: bool = False) -> dict:
    """Build lane+fleet.

    marked          partial-clone metadata on the lane repository
    fleet_marked    partial-clone metadata on the fleet repository
    missing_side    "lane" | "fleet": which repository owns the incomplete
                    object on its unselected `side` branch
    selected_missing put the incomplete object on the SELECTED lane branch
                    (master) instead of the unselected one: the discriminating
                    control for the root choice
    """
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    lane = init(root / "lane")
    fleet = init(root / "fleet")

    # the cited lane commit (author time 1000)
    cited = commit(lane, "kama-shokunin", 1000, "round-1: work", "f",
                   b"work\n")
    lane_blob = g(lane, "rev-parse", f"{cited}:f")
    # an unrelated branch with its own object, later made incomplete
    g(lane, "checkout", "-q", "-b", "side")
    side_commit = commit(lane, "other-author", 1500, "side work", "side.txt",
                         b"unrelated side payload\n")
    side_blob = g(lane, "rev-parse", f"{side_commit}:side.txt")
    g(lane, "checkout", "-q", "master")

    # fleet report (author time 2000 -> first-add cutoff 2000)
    report = ("# kama round 1\n\n## Landed changes\n\n- " + cited + "\n")
    commit(fleet, "fleet", 2000, "round-1: report", REL, report.encode())

    # an unrelated fleet branch, for the fleet-side variant
    fleet_side_blob = None
    if missing_side == "fleet":
        g(fleet, "checkout", "-q", "-b", "side")
        fs = commit(fleet, "other-author", 1600, "fleet side work",
                    "side.txt", b"unrelated fleet payload\n")
        fleet_side_blob = g(fleet, "rev-parse", f"{fs}:side.txt")
        g(fleet, "checkout", "-q", "master")

    info = {"root": str(root), "lane": str(lane), "fleet": str(fleet),
            "cited_commit": cited, "side_commit": side_commit,
            "side_blob": side_blob, "lane_blob": lane_blob,
            "fleet_side_blob": fleet_side_blob, "report_rel": REL,
            "missing_side": missing_side,
            "selected_missing": selected_missing}

    if marked:
        # partial-clone metadata: a promisor remote that cannot be reached
        # (nonexistent local path, no transport is ever attempted) and the
        # extensions.partialclone marker git writes for such a clone.
        g(lane, "config", "remote.origin.promisor", "true")
        g(lane, "config", "remote.origin.partialclonefilter", "blob:none")
        g(lane, "config", "remote.origin.url", str(root / "nonexistent.git"))
        g(lane, "config", "extensions.partialclone", "origin")
    if fleet_marked:
        g(fleet, "config", "remote.origin.promisor", "true")
        g(fleet, "config", "remote.origin.partialclonefilter", "blob:none")
        g(fleet, "config", "remote.origin.url", str(root / "nonexistent.git"))
        g(fleet, "config", "extensions.partialclone", "origin")

    # make the chosen object genuinely incomplete: delete the loose blob.
    # The commit and tree stay; only the blob bytes are gone, exactly like a
    # blobless clone that was never hydrated.
    if selected_missing:
        owner, target = lane, lane_blob
        info["missing_object"] = "lane-selected-branch"
    elif missing_side == "fleet":
        owner, target = fleet, fleet_side_blob
        info["missing_object"] = "fleet-unselected-branch"
    else:
        owner, target = lane, side_blob
        info["missing_object"] = "lane-unselected-branch"
    blob_path = loose_path(owner, target)
    if not blob_path.exists():
        raise RuntimeError(f"{blob_path} is not a loose object")
    blob_path.unlink()
    info["missing_blob"] = target
    info["missing_blob_owner"] = str(owner)
    info["missing_blob_path"] = str(blob_path)
    return info


def premises(info: dict) -> dict:
    """Verify the fixture premise with plain git (no auditor involved)."""
    lane, fleet = info["lane"], info["fleet"]
    missing = info["missing_blob"]
    owner = info["missing_blob_owner"]
    out = {"missing_object": info["missing_object"],
           "missing_blob": missing, "missing_owner": owner}

    def run(repo, *args):
        p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                           env=env())
        return p.returncode, p.stdout.decode(errors="replace"), \
            p.stderr.decode(errors="replace")

    def missing_lines(repo, *rev):
        rc, sout, serr = run(repo, "rev-list", "--objects", "--missing=print",
                             "--no-object-names", *rev)
        return rc, sorted(ln for ln in sout.split("\n") if ln.startswith("?"))

    rc, _, _ = run(owner, "cat-file", "-e", missing)
    out["missing_blob_absent"] = rc != 0
    rc, _, _ = run(lane, "cat-file", "-e", info["cited_commit"])
    out["cited_commit_present"] = rc == 0
    rc, _, _ = run(lane, "cat-file", "-e", f"{info['cited_commit']}^{{commit}}")
    out["cited_commit_peels"] = rc == 0

    # all-refs walk: the unrelated branch's missing object shows up
    rc, sout, _ = run(lane, "rev-list", "--objects", "--missing=print", "--all")
    out["rev_list_all_rc"] = rc
    out["rev_list_all_missing_lines"] = sorted(
        ln for ln in sout.split("\n") if ln.startswith("?"))
    out["rev_list_all_reports_missing"] = any(
        ln.lstrip("?") == missing for ln in sout.split("\n"))
    rc, fout, _ = run(fleet, "rev-list", "--objects", "--missing=print",
                       "--all")
    out["rev_list_all_fleet_rc"] = rc
    out["rev_list_all_fleet_missing_lines"] = sorted(
        ln for ln in fout.split("\n") if ln.startswith("?"))

    # rooted walks at the audit's evidence roots: lane tip and fleet HEAD
    rc, lines = missing_lines(lane, "master")
    out["rev_list_lane_root_rc"] = rc
    out["rev_list_lane_root_missing_lines"] = lines
    out["rev_list_lane_root_clean"] = not lines
    rc, lines = missing_lines(fleet, "HEAD")
    out["rev_list_fleet_root_rc"] = rc
    out["rev_list_fleet_root_missing_lines"] = lines
    out["rev_list_fleet_root_clean"] = not lines

    rc, sout, _ = run(lane, "log", "--format=%H", "master")
    out["lane_log_master_rc"] = rc
    out["lane_log_master_commits"] = len(
        [ln for ln in sout.split("\n") if ln.strip()])

    rc, _, _ = run(lane, "merge-base", "--is-ancestor", info["side_commit"],
                   "master")
    out["side_is_ancestor_of_master"] = rc == 0
    rc, sout, _ = run(lane, "branch", "--list")
    out["lane_branches"] = sorted(sout.split("\n"))

    p = subprocess.run(["git", "-C", fleet, "log", "--diff-filter=A",
                        "--format=%at", "--", REL], capture_output=True,
                       env=env())
    out["fleet_cutoff"] = p.stdout.decode().split()[-1] if p.stdout.split() \
        else None
    return out


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1
                else "/fast/scratch/hyaku/kama-r24/OracleMissingNonrequired/"
                     "fixture")
    variants = {
        # the case under test: marked lane, incomplete object only on an
        # unselected, unrelated branch
        "marked": dict(marked=True),
        # twin: identical content, partial-clone metadata removed; it fixes
        # the substantive verdict independently of any candidate
        "unmarked_twin": dict(marked=False),
        # the same, with the incomplete object in the fleet repository
        "fleet_marked": dict(marked=True, missing_side="fleet"),
        # discriminating control: the incomplete object IS on the selected
        # lane branch, so a root-scoped closure check must report it
        "selected_missing": dict(marked=True, selected_missing=True),
    }
    doc = {}
    for name, kwargs in variants.items():
        info = build(root / name, **kwargs)
        doc[name] = {**info, "premises": premises(info)}
    print(json.dumps(doc, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
