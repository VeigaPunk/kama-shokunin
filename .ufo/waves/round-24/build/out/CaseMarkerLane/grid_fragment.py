#!/usr/bin/env python3
"""CANDIDATE GRID FRAGMENT — round-24 promisor grid (KamaR23-2.CaseMarkerLane-2).

Not production code.  Copy the builders and the row into
`tests/report-audit/promisor-grid.py` (owner: KamaR23-2.GridOracle-2), or
adapt them to that grid's own helper names.

CASE UNDER SPECIFICATION
    "paired .promisor+.pack marker only in a COMPLETE lane, no promisor
     remote config -> the clean verdict of the otherwise identical full
     clone".

WHY THE EXPECTATION IS FIXED BEFORE IMPLEMENTATION
    The expected verdict is the FULL-CLONE TWIN's verdict: same commits,
    same report, same fleet, only the marker file differs.  The twin is
    audited by the same binary in the same run, so the expected exit and
    the expected finding set are observed, not assumed.  No candidate
    implementation is consulted to produce the expectation.

GRADING
    `control` row: the marked lane must produce the SAME exit and the SAME
    finding set as its full-clone twin (exit 0, no findings for the clean
    variant).  Equality with the twin, not just "not exit 2", is the
    requirement: "exit 0 with the right findings" is what the round-24
    contract asks for.

PAIRING REQUIREMENT (do not drop)
    This row MUST be graded in the same arm as a row whose lane genuinely
    lacks a required object (see `f_promisor_pack` in
    tests/report-audit/repo-state-grid.py:195, row F23 at :670).  Measured
    (evidence-naive-repair.json): if the repair only removes the marker
    refusal, the genuinely-incomplete F23 lane audits to exit 1
    `unresolved-full-hash` — unavailable evidence turned into a proved
    absence.  The contract truth for that row is exit 2
    could-not-evaluate.  With this row alone, that naive repair would
    pass.  Pinned, the repair must add availability checking, not just
    stop refusing.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

# ---------------------------------------------------------------- builders


def c_promisor_marker_complete_lane(tmp):
    """A COMPLETE lane that carries git's partial-clone pack marker and no
    promisor remote config.  The marker alone must not decide the verdict."""
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, report([lc]))
    # one real pack, so the marker is paired exactly as git writes it
    g(lane, "repack", "-a", "-d", "-q")
    pack = sorted(Path(lane, ".git/objects/pack").glob("pack-*.pack"))
    require(len(pack) == 1, "expected exactly one pack")
    marker = pack[0].with_suffix(".promisor")
    marker.write_bytes(b"")
    # premise: the lane is COMPLETE (nothing missing) and has no promisor
    # remote config; the marker file is the only difference from the twin
    missing = [l for l in g(lane, "rev-list", "--objects", "--all",
                            "--missing=print").splitlines()
               if l.startswith("?")]
    require(not missing, "lane is not complete: %r" % missing[:3])
    keys = [line.split("\n")[0] for line in
            g(lane, "config", "--null", "--list").split("\0") if line]
    require(not any("promisor" in k for k in keys),
            "lane has promisor config: %r" % keys)
    require(marker.is_file() and marker.with_suffix(".pack").is_file(),
            "promisor marker is not paired with a pack")
    return lane, fleet, [], None


def c_promisor_marker_complete_lane_omission(tmp):
    """Same marked lane, but one lane commit is left uncited: the marked
    lane must find the SAME omission the full clone finds."""
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    commit(lane, "kama-shokunin", 1500, "round-1: uncited")
    publish(fleet, report([lc]))
    g(lane, "repack", "-a", "-d", "-q")
    pack = sorted(Path(lane, ".git/objects/pack").glob("pack-*.pack"))
    pack[0].with_suffix(".promisor").write_bytes(b"")
    return lane, fleet, [], None


# ------------------------------------------------------------------- rows
#
# name, kind, builder, expected exit, expected finding kinds
#
#   ("C14-promisor-marker-complete-lane", "control",
#    c_promisor_marker_complete_lane, 0, []),
#   ("C15-promisor-marker-complete-lane-omission", "control",
#    c_promisor_marker_complete_lane_omission, 1, ["landed-omitted"]),
#
# The twin comparison is the authoritative check; the exit/kinds above are
# the twin's observed values (measured 2026-10-21, base 0df800e,
# evidence.json: A_full_clone_clean -> exit 0, kinds [];
# C_full_clone_omission -> exit 1, kinds ["landed-omitted"]).
#
# `f_promisor_pack` (F23, repo-state-grid.py:195) keeps exit 2 but its
# pinned reason ("promisor pack", REASONS at :704) must change: under
# round-24 the exit-2 reason is the unavailability of the required object,
# not the mere presence of a marker.  A reason pin that still names the
# marker would make the round-24 repair untestable.

# ------------------------------------------------------------------ helpers
# Expected to exist in the adopting grid (repo-state-grid.py:88-125):
#   pair(tmp), commit(repo, author, when, msg, path="f"), publish(fleet,
#   text), report(cites), g(repo, *args), require(cond, message)
#
# A twin comparison helper, if the adopting grid wants the strict form:
#
#   def twin_equal(build_marked, build_plain, tmp):
#       """Same binary, same run: the marked lane must equal its twin."""
#       a = run_case(auditor, build_marked(tmp), tmp)
#       b = run_case(auditor, build_plain(tmp), tmp)
#       return a["exit"] == b["exit"] and a["kinds"] == b["kinds"]
