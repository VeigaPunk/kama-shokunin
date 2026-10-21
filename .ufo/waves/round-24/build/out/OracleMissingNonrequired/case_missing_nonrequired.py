#!/usr/bin/env python3
"""Drop-in oracle case for the r24 promisor grid: incomplete object in an
unrelated, unselected branch.

Case N01-missing-object-unselected-branch
  Lane repository: partial-clone metadata (remote.origin.promisor=true,
  remote.origin.partialclonefilter=blob:none, extensions.partialclone=origin,
  remote.origin.url=<nonexistent local path>) plus a genuinely incomplete
  object: the blob of an `side` branch that the audit never selects.
  Fleet repository: ordinary, commits the round-1 report citing the lane
  commit.

  Expected: exit 0, no findings - the SAME substantive verdict as an
  otherwise identical repository without the partial-clone metadata
  (the unmarked twin in the same fixture builder).  A missing object outside
  the audit's evidence roots is not required evidence and must not become
  could-not-evaluate.

Case N02-missing-object-fleet-unselected-branch
  Same, with the incomplete object in the fleet repository's unselected
  branch.  Expected: exit 0, no findings.

Case N03-missing-object-selected-branch (discriminating control)
  Same metadata, but the incomplete object IS reachable from the selected
  lane branch.  Expected: exit 2 (could-not-evaluate) - never a clean or
  failed verdict.

The builder is self-contained (no dependency on the r23 grid module) and
uses only local git: no clone, no transport, no network.  The incomplete
object is produced by deleting one loose object file, which is exactly what
a blobless clone that was never hydrated looks like.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess

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


def loose(repo, sha):
    return Path(repo, ".git", "objects", sha[:2], sha[2:])


def mark_promisor(repo, root):
    """Partial-clone metadata only: no remote is reachable, no transport is
    ever invoked (the URL is a nonexistent local path)."""
    g(repo, "config", "remote.origin.promisor", "true")
    g(repo, "config", "remote.origin.partialclonefilter", "blob:none")
    g(repo, "config", "remote.origin.url", str(Path(root, "nonexistent.git")))
    g(repo, "config", "extensions.partialclone", "origin")


def build_case(tmp, missing_side="lane", selected_missing=False):
    """Return (lane, fleet, extra, marker) in the r23 grid builder shape."""
    tmp = Path(tmp)
    lane = init(tmp / "lane")
    fleet = init(tmp / "fleet")

    cited = commit(lane, "kama-shokunin", 1000, "round-1: work", "f", b"w\n")
    lane_blob = g(lane, "rev-parse", f"{cited}:f")
    g(lane, "checkout", "-q", "-b", "side")
    side = commit(lane, "other", 1500, "side work", "side.txt", b"side\n")
    side_blob = g(lane, "rev-parse", f"{side}:side.txt")
    g(lane, "checkout", "-q", "master")

    report = "# kama round 1\n\n## Landed changes\n\n- " + cited + "\n"
    commit(fleet, "fleet", 2000, "round-1: report", REL, report.encode())

    fleet_blob = None
    if missing_side == "fleet":
        g(fleet, "checkout", "-q", "-b", "side")
        fs = commit(fleet, "other", 1600, "fleet side work", "side.txt",
                    b"fleet side\n")
        fleet_blob = g(fleet, "rev-parse", f"{fs}:side.txt")
        g(fleet, "checkout", "-q", "master")

    mark_promisor(lane, tmp)
    if missing_side == "fleet":
        mark_promisor(fleet, tmp)

    if selected_missing:
        owner, target = lane, lane_blob
    elif missing_side == "fleet":
        owner, target = fleet, fleet_blob
    else:
        owner, target = lane, side_blob
    path = loose(owner, target)
    if not path.exists():
        raise RuntimeError(f"{path} is not a loose object")
    path.unlink()

    # premise: the object is gone, the cited commit is present, and the
    # missing object is NOT reachable from the selected lane tip
    assert subprocess.run(["git", "-C", str(owner), "cat-file", "-e", target],
                          capture_output=True,
                          env=env()).returncode != 0, "object still present"
    assert subprocess.run(["git", "-C", str(lane), "cat-file", "-e", cited],
                          capture_output=True,
                          env=env()).returncode == 0, "cited commit missing"
    rooted = g(lane, "rev-list", "--objects", "--missing=print",
               "--no-object-names", "master")
    if selected_missing:
        assert f"?{target}" in rooted.split("\n"), \
            "selected-branch incompleteness not observed"
    else:
        assert f"?{target}" not in rooted.split("\n"), \
            "rooted walk must not see the unselected branch's object"
    return lane, fleet, [], None


# grid rows: (name, kind, builder-kwargs, expected exit, expected kinds)
ROWS = [
    ("N01-missing-object-unselected-branch", "contract",
     dict(missing_side="lane"), 0, []),
    ("N02-missing-object-fleet-unselected-branch", "contract",
     dict(missing_side="fleet"), 0, []),
    ("N03-missing-object-selected-branch", "contract",
     dict(missing_side="lane", selected_missing=True), 2, None),
]


def build(tmp):
    return build_case(tmp)


if __name__ == "__main__":
    import json
    import sys
    lane, fleet, extra, marker = build(sys.argv[1])
    print(json.dumps({"lane": str(lane), "fleet": str(fleet)}, indent=1))
