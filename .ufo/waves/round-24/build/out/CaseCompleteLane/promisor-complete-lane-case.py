#!/usr/bin/env python3
"""Oracle case fragment: PROM-COMPLETE-LANE.

Round-24 repair-first, lane `CaseCompleteLane` (KamaR23-2.CaseCompleteLane-2).
Base: 0df800e896f6bce285a81e794ad4ae1d1e6c3a71.

Case family: a lane repository that is a *complete* local clone (every object
the audit reads is present) but whose origin remote is *declared* promisor
(`remote.origin.promisor=true`).  The declaration is metadata only: no
`.promisor` pack marker exists, no object is missing, and the origin URL is
an inert non-existent local path (no transport is reachable).

Preregistered expectations (fixed before any implementation exists):

  row        fixture                              exit  defect kinds
  PROM-CLEAN cited lane commit, nothing omitted   0     []
  PROM-OMIT  genuine pre-cutoff lane commit
             omitted from `## Landed changes`       1     ["landed-omitted"]

Both rows must reproduce their full-clone twins' exit code AND the exact
(kind, token) defect set.  Neither may be exit 2, hang, traceback, or run a
repository-configured program.  The full-clone twins are exactly the
round-23 control rows C01-clean and C02-real-omission of
`tests/report-audit/repo-state-grid.py`, so the expected values are not
invented here.

Observed at the base (this is the round-23 harm, and it is what the case
pins down): both rows exit 2 with
`could-not-evaluate: <repo>: partial clone (remote.origin.promisor)`,
raised at `tools/report-landing-audit.py:458-465` (config scan) from
`check_history_repo`, called at `:514-515` before any object lookup.

Non-goals for this fragment (other lanes own them): promisor *fleet*
repositories, `extensions.partialclone` marker repositories, blobless or
otherwise hydrated clones, and repositories whose required objects are
genuinely missing.

The fragment uses the helper names of `tests/report-audit/repo-state-grid.py`
(env, g, init, commit, pair, publish, base, report, require) so it can be
lifted into `tests/report-audit/promisor-grid.py` unchanged.

Liftable block: everything from the line `INERT_ORIGIN = ` to the end of
this file (everything above it is the module docstring and the imports,
which the grid module already provides).  The grid module supplies
`Path`, `subprocess`, `env`, `g`, `init`, `commit`, `base`, `report` and
`require`.
"""
from __future__ import annotations

from pathlib import Path
import subprocess

# Inert, non-existent local origin: no network transport is reachable even
# if a lazy fetch were attempted (the auditor also passes --no-lazy-fetch).
INERT_ORIGIN = "/nonexistent/kama-promisor-origin.git"


def _clone_all_objects(source, twin):
    """Full local clone: every object is copied, no .promisor pack.

    `--no-local` forces the file transport instead of hardlink borrowing, so
    the clone owns a complete, independent object store.
    """
    g(source.parent, "-c", "protocol.file.allow=always", "clone", "-q",
      "--no-hardlinks", "--no-local", str(source), str(twin))
    return twin


def _require_complete(twin, lane, required):
    """Premise: the twin really holds every object the audit reads."""
    gitdir = Path(g(twin, "rev-parse", "--absolute-git-dir"))
    packs = list((gitdir / "objects/pack").glob("*.promisor"))
    require(not packs, f"twin carries a .promisor pack: {packs}")
    missing = [line for line in
               g(twin, "rev-list", "--objects", "--all", "--missing=print")
               .splitlines() if line.startswith("?")]
    require(not missing, f"twin is missing objects: {missing}")
    for sha in required:
        probe = subprocess.run(["git", "-C", str(twin), "cat-file", "-e",
                                f"{sha}^{{commit}}"], capture_output=True,
                               env=env())
        require(probe.returncode == 0,
                f"required object {sha} is not local in the twin")
    require(g(twin, "rev-parse", "HEAD") == g(lane, "rev-parse", "HEAD"),
            "twin tip differs from the source lane tip")


def promisor_twin(lane, twin, required):
    """Clone `lane` completely, then declare the origin promisor.

    Only the remote metadata differs from the full clone; content, refs and
    object store are identical.
    """
    _clone_all_objects(lane, twin)
    g(twin, "config", "remote.origin.promisor", "true")
    g(twin, "config", "remote.origin.url", INERT_ORIGIN)
    g(twin, "config", "remote.origin.fetch",
      "+refs/heads/*:refs/remotes/origin/*")
    require(g(twin, "config", "--get", "remote.origin.promisor") == "true",
            "promisor declaration not in effect")
    _require_complete(twin, lane, required)
    return twin


def p_complete_lane_clean(tmp):
    """PROM-CLEAN: cited lane commit, promisor metadata, complete content."""
    lane, fleet, lc = base(tmp)
    twin = promisor_twin(lane, Path(tmp, "lane-promisor"), [lc])
    return twin, fleet, [], None


def p_complete_lane_omit(tmp):
    """PROM-OMIT: a genuine pre-cutoff lane commit the report omits."""
    lane, fleet, lc = base(tmp)
    omitted = commit(lane, "kama-shokunin", 1500, "round-1: more")
    twin = promisor_twin(lane, Path(tmp, "lane-promisor"), [lc, omitted])
    return twin, fleet, [], None


# Grid row entries (name, kind, builder, expected exit, expected kinds).
PROMISOR_CASES = [
    ("PROM-CLEAN", "control", p_complete_lane_clean, 0, []),
    ("PROM-OMIT", "control", p_complete_lane_omit, 1, ["landed-omitted"]),
]

# Both rows are graded CONTROL rows for the CURRENT arm: the current arm
# must produce the full-clone verdict.  For the FROZEN (r23 base) arm both
# rows exit 2 with the pinned reason below; the frozen arm is expected to
# fail these rows, exactly as it fails every other repaired row.
FROZEN_REASON = "partial clone (remote.origin.promisor)"
