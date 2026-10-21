#!/usr/bin/env python3
"""Paste-in case fragment for tests/report-audit/promisor-grid.py.

Case CA-1 (round 24): a required lane ancestor commit that is not available
in a promisor-backed lane repository.

  CA-1a  control  a real blobless partial clone of the origin; every
                  required object is available locally; the report omits one
                  required pre-cutoff commit -> exit 1, landed-omitted
  CA-1b  fault    the same partial clone with its pack rebuilt without that
                  required ancestor -> exit 2, could-not-evaluate, never a
                  verdict (no truncated history, no guessed omission)
  CA-1c  control  a full clone of the same origin -> the same findings as
                  CA-1a

The builders below use only the helpers that
tests/report-audit/repo-state-grid.py already provides (g, init, commit,
report, publish) and the case protocol of that file: a builder returns
(lane, fleet, extra, marker).  They build everything offline: the only
"remote" is a bare repository on the same filesystem, reached through git's
local path transport.  No network, no repo-configured program, no script.

Deterministic object ids (author kama-shokunin, fixed author/committer
times, one file "f" appended per commit):

  L0 "round-1: base"    @900   cited by the report
  L1 "round-1: work"    @1000  required, NOT cited  <- the omitted commit
  L2 "round-1: measure" @1100  cited by the report
  L3 "round-1: late"    @2100  post-report
  fleet report commit   @2000  cutoff

  L0 f2a3f555fec1893ef9fcc26a1ae3b8fe834f660d
  L1 adf2a3a5f286862c96099b7cd59457c6cd88621c
  L2 e51bbdbc7eb8ba2e2fbba826088b87ba77c44fe1
  L3 ad057c4cf6f92d0190911731fbfa51d0ff5e8453
"""
from __future__ import annotations

from pathlib import Path
import subprocess


def _ca1_origin(tmp):
    """The lane history, the bare origin and the fleet report."""
    src = init(Path(tmp, "src"))
    l0 = commit(src, "kama-shokunin", 900, "round-1: base")
    l1 = commit(src, "kama-shokunin", 1000, "round-1: work")
    l2 = commit(src, "kama-shokunin", 1100, "round-1: measure")
    l3 = commit(src, "kama-shokunin", 2100, "round-1: late")
    origin = Path(tmp, "origin.git")
    g(tmp, "clone", "-q", "--bare", "--no-hardlinks", str(src), str(origin))
    g(origin, "config", "uploadpack.allowFilter", "true")
    fleet = init(Path(tmp, "fleet"))
    publish(fleet, report([l0, l2]))
    return origin, fleet, l0, l1, l2, l3


def _ca1_clone(tmp, origin, partial):
    lane = Path(tmp, "lane")
    argv = ["clone", "-q", "--no-checkout", "--no-local"]
    if partial:
        argv += ["--filter=blob:none"]
    argv += [f"file://{origin}", str(lane)]
    g(tmp, "-c", "protocol.file.allow=always", *argv)
    return lane


def _ca1_drop(lane, keep, drop):
    """Rebuild the lane's pack without `drop`.

    The object list is explicit: a rev-list exclusion (`^drop`) would also
    drop the ancestors of `drop`, which are needed here (L0 is cited by the
    report and is an ancestor of the dropped commit).
    """
    objs = []
    for sha in keep:
        objs.append(sha)
        objs.append(g(lane, "rev-parse", f"{sha}^{{tree}}"))
        for line in g(lane, "ls-tree", "-r", sha).split("\n"):
            if line.strip():
                objs.append(line.split()[2])
    objs = sorted(set(objs))
    require(drop not in objs, "the dropped commit is in the kept object list")
    packed = subprocess.run(["git", "-C", str(lane), "pack-objects",
                              "--stdout"],
                             input="".join(f"{o}\n" for o in objs).encode(),
                             capture_output=True, env=env())
    require(packed.returncode == 0, "pack-objects failed")
    for p in Path(lane, ".git/objects/pack").iterdir():
        p.unlink()
    indexed = subprocess.run(["git", "-C", str(lane), "index-pack", "--stdin"],
                             input=packed.stdout, capture_output=True,
                             env=env())
    require(indexed.returncode == 0, "index-pack failed")
    packs = sorted(Path(lane, ".git/objects/pack").iterdir())
    name = [p.name for p in packs if p.name.endswith(".pack")][0][:-5]
    Path(lane, ".git/objects/pack", name + ".promisor").write_bytes(b"")


def _ca1_present(repo, sha):
    """--no-lazy-fetch: the presence check must never fetch the object."""
    return subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo),
                           "cat-file", "-e", sha],
                          capture_output=True, env=env()).returncode == 0


def c_ca1_promisor_complete(tmp):
    """CA-1a: promisor-marked lane, every required object available; the
    genuine omission must still be reported (exit 1, landed-omitted)."""
    origin, fleet, l0, l1, l2, l3 = _ca1_origin(tmp)
    lane = _ca1_clone(tmp, origin, partial=True)
    require(_ca1_present(lane, l1), "L1 missing from the partial clone")
    return lane, fleet, [], None


def f_ca1_missing_required_ancestor(tmp):
    """CA-1b: the required ancestor L1 is unavailable in a promisor-backed
    lane.  The origin still holds it, so a lazy fetch would restore it and
    be visible.  Expected: exit 2, could-not-evaluate, no verdict."""
    origin, fleet, l0, l1, l2, l3 = _ca1_origin(tmp)
    lane = _ca1_clone(tmp, origin, partial=True)
    _ca1_drop(lane, [l0, l2, l3], l1)
    require(not _ca1_present(lane, l1), "L1 still available")
    require(_ca1_present(origin, l1), "L1 missing from the origin")
    return lane, fleet, [], None


def c_ca1_full_clone(tmp):
    """CA-1c: the same origin cloned without a filter; the findings must be
    identical to CA-1a."""
    origin, fleet, l0, l1, l2, l3 = _ca1_origin(tmp)
    lane = _ca1_clone(tmp, origin, partial=False)
    require(_ca1_present(lane, l1), "L1 missing from the full clone")
    return lane, fleet, [], None


# CASES rows to append to tests/report-audit/promisor-grid.py
CA1_CASES = [
    ("CA-1a-promisor-complete", "control", c_ca1_promisor_complete, 1,
     ["landed-omitted"]),
    ("CA-1b-missing-required-ancestor", "fault",
     f_ca1_missing_required_ancestor, 2, None),
    ("CA-1c-full-clone", "control", c_ca1_full_clone, 1,
     ["landed-omitted"]),
]

# REASONS entry.  The grid's REASONS map holds one required substring; for
# the fault row the *evidence-based* reason must be required, not the r23
# metadata refusal.  The base refuses with "partial clone (promisor pack)";
# a strict read answers "could not read <oid>" / "Failed to traverse
# parents of commit <oid>"; an availability check answers "not available
# locally".  The three-word difference needs an any-of check, which the
# sibling case CaseMissingFleetTree already proposes for this grid; until
# then, pin the generic prefix and check the reason outside the grid:
CA1_REASONS = {
    "CA-1b-missing-required-ancestor": "could-not-evaluate",
}

# Additional assertions that the grid protocol cannot express (run them
# beside the grid rows, or fold them into the case runner):
#   * stderr of CA-1b must NOT contain "partial clone (promisor pack)",
#     "partial clone (extensions.partialclone" or "partial clone (remote."
#     -- an exit 2 decided by the promisor metadata is not the required
#     could-not-evaluate.
#   * stderr of CA-1b should (recommended, soft) name the unavailable
#     object id adf2a3a5f286862c96099b7cd59457c6cd88621c.
#   * the lane object store must be byte-identical before and after the run
#     and L1 must still be absent afterwards: no lazy fetch.
#   * CA-1a and CA-1c must agree on exit, kinds, tokens and the summary
#     counts (required_commits=3, post_report_commits=1).
