"""Grid fragment for CaseMarkerFleet (round 24) — drop-in for
tests/report-audit/promisor-grid.py.

Self-contained: stdlib + git only. The builders reuse the repository-state
grid's idioms (fresh scratch lane/fleet per case, explicit identity and
dates, every git write checked).

Row model
---------
The r23 grid has ONE expected exit per case, applied to both arms. The
marker rows need PER-ARM expectations, because the base (frozen) auditor
refuses a promisor-marked repository (exit 2) while the repaired auditor
must evaluate it (exit 0/1). promisor-grid.py therefore needs an
`expected` shape like:

    {"frozen": (2, None, "partial clone"),      # exit, kinds, reason
     "current": (1, ["landed-omitted"], None)}

where `kinds` None means "do not grade the defect kinds" and `reason` pins
the refusal text so an unrelated startup error cannot pass as the intended
refusal (the r23 REASONS table).

Rows
----
P01-marker-fleet-clean      marker metadata, complete content, cited commit
P02-marker-fleet-omission   marker metadata, complete content, uncited
                             pre-cutoff lane commit -> landed-omitted
P03-plain-fleet-clean       ordinary twin of P01 (same object store)
P04-plain-fleet-omission    ordinary twin of P02 (same object store)

P03/P04 are the ordinary twins: the marker twins are byte-identical object
stores, so P01 must equal P03 and P02 must equal P04 — same exit, same
defect (kind, token) multiset, same report cutoff (2000), same required
count.

No transport is possible in any row: the marker's remote url names a path
that does not exist and protocol.allow=never forbids any transport. No
repo-configured program is installed anywhere in this fragment.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

REL = ".ufo/reports/round-1/kama.md"
ABSENT_ORIGIN = "/fast/scratch/hyaku/kama-r24/CaseMarkerFleet/absent-origin.git"


class Premise(Exception):
    """The fixture did not establish its fault: cannot evaluate."""


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args],
                       input=None if data is None else data.encode(),
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise Premise(f"git {' '.join(map(str, args))}: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path):
    g(path.parent, "init", "-q", "-b", "master", str(path))
    return path


def commit(repo, author, when, msg, path="f", content=None):
    target = Path(repo) / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(target, "ab") as fh:
            fh.write((msg + "\n").encode())
    else:
        target.write_bytes(content)
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def report(cites):
    return ("# kama round 1\n\n## Landed changes\n\n"
            + "".join(f"- {c}\n" for c in cites)).encode()


def publish(fleet, cites, when=2000):
    return commit(fleet, "fleet", when, "round-1: report", REL, report(cites))


def mark_as_promisor(repo):
    """Promisor marker metadata ONLY: no object is removed, none is missing."""
    g(repo, "config", "core.repositoryformatversion", "1")
    g(repo, "config", "extensions.partialclone", "origin")
    g(repo, "config", "remote.origin.url", ABSENT_ORIGIN)
    g(repo, "config", "remote.origin.promisor", "true")
    g(repo, "config", "remote.origin.partialclonefilter", "blob:none")
    g(repo, "config", "protocol.allow", "never")
    if Path(ABSENT_ORIGIN).exists():
        raise Premise(f"the absent origin exists: {ABSENT_ORIGIN}")
    for rel in ("objects/pack",):
        d = Path(g(repo, "rev-parse", "--git-path", rel))
        if d.is_dir() and any(p.suffix == ".promisor" for p in d.iterdir()):
            raise Premise("marker twin carries a promisor pack marker")
    missing = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo),
                               "rev-list", "--objects", "--all",
                               "--missing=print"], capture_output=True,
                              env=env()).stdout.decode()
    if any(line.startswith("?") for line in missing.split("\n")):
        raise Premise("marker twin is not complete: a required object is absent")
    return repo


def _fleet(tmp, omission, marker):
    lane = init(Path(tmp, "lane"))
    plain = init(Path(tmp, "fleet-plain"))
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    if omission:
        commit(lane, "kama-shokunin", 1500, "round-1: more")
    publish(plain, [lc])
    if not marker:
        return lane, plain
    twin = Path(tmp, "fleet-marker")
    shutil.copytree(plain, twin, symlinks=True)
    mark_as_promisor(twin)
    if g(plain, "rev-parse", "HEAD") != g(twin, "rev-parse", "HEAD"):
        raise Premise("marker twin has a different HEAD")
    return lane, twin


def c_marker_fleet_clean(tmp):
    return _fleet(tmp, omission=False, marker=True) + ([], None)


def c_marker_fleet_omission(tmp):
    return _fleet(tmp, omission=True, marker=True) + ([], None)


def c_plain_fleet_clean(tmp):
    return _fleet(tmp, omission=False, marker=False) + ([], None)


def c_plain_fleet_omission(tmp):
    return _fleet(tmp, omission=True, marker=False) + ([], None)


# name, kind, builder, per-arm expectation
#   expectation = (exit, kinds or None, reason or None)
CASES = [
    ("P01-marker-fleet-clean", "control", c_marker_fleet_clean,
     {"frozen": (2, None, "partial clone"),
      "current": (0, [], None)}),
    ("P02-marker-fleet-omission", "control", c_marker_fleet_omission,
     {"frozen": (2, None, "partial clone"),
      "current": (1, ["landed-omitted"], None)}),
    ("P03-plain-fleet-clean", "control", c_plain_fleet_clean,
     {"frozen": (0, [], None), "current": (0, [], None)}),
    ("P04-plain-fleet-omission", "control", c_plain_fleet_omission,
     {"frozen": (1, ["landed-omitted"], None),
      "current": (1, ["landed-omitted"], None)}),
]

# Equality the repaired arm must hold (P01 == P03, P02 == P04):
# same exit, same defect (kind, token) multiset, same cutoff (2000),
# same required count.
EQUALITY_PAIRS = [("P01-marker-fleet-clean", "P03-plain-fleet-clean"),
                  ("P02-marker-fleet-omission", "P04-plain-fleet-omission")]
