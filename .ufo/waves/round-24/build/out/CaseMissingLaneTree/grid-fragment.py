#!/usr/bin/env python3
"""Grid fragment for the round-24 oracle case: promisor-marked lane with an
unavailable reachable tree (expected exit 2, could-not-evaluate).

Written for tests/report-audit/promisor-grid.py (the round-24 grid named in
the preregistration). It follows the house style of
tests/report-audit/repo-state-grid.py: the builder returns
(lane, fleet, argv_extra, marker) and raises Premise when the fixture did
not establish its premise.

The case is the tree analogue of the "missing citation" case: in a
promisor-backed repository, an object that is not available locally is not
proof of absence. The commits of the lane are all present locally; one
reachable tree (the tip commit's tree) is not. The auditor must therefore
refuse to evaluate (exit 2) and must not report clean (0) nor failed (1).
"""

# --------------------------------------------------------------- the case

def f_missing_lane_tree(tmp):
    """Promisor-marked lane whose reachable tip tree is unavailable while
    every commit object is present locally.

    The tip tree is required evidence: the auditor reads the lane tip tree
    to find `corpus/SOURCES.md` (tools/report-landing-audit.py:258-268),
    and the presence of that registry decides how 40-hex tokens in the
    report are classified. Without the tree the verdict is undecidable, so
    the only honest outcome is exit 2.
    """
    lane, fleet = pair(tmp)
    c1 = commit(lane, "kama-shokunin", 1000, "round-1: work")
    c2 = commit(lane, "kama-shokunin", 1500, "round-1: more")
    publish(fleet, report([c1, c2]))
    tree = g(lane, "rev-parse", f"{c2}^{{tree}}")
    loose = Path(lane, ".git/objects", tree[:2], tree[2:])
    require(loose.is_file(), "tip tree is not a loose object")
    os.unlink(loose)
    # promisor metadata only. The remote path does not exist, so a lazy
    # fetch could neither succeed nor reach anything; no program is
    # configured, so no command can be executed.
    for k, v in (("extensions.partialClone", "origin"),
                 ("remote.origin.url", str(Path(tmp, "absent-promisor.git"))),
                 ("remote.origin.promisor", "true")):
        g(lane, "config", k, v)
    # premise: commits present, tree unavailable
    require(g(lane, "cat-file", "-t", c1) == "commit",
            "cited commit object is not present locally")
    require(g(lane, "cat-file", "-t", c2) == "commit",
            "tip commit object is not present locally")
    require(subprocess.run(["git", "--no-lazy-fetch", "-C", str(lane),
                            "cat-file", "-e", tree],
                           capture_output=True, env=env()).returncode != 0,
            "the tip tree is still readable")
    return lane, fleet, [], None


# ---------------------------------------------------------------- the row
# name, kind, builder, expected exit, expected defect kinds
CASE_ROW = ("F20-promisor-missing-lane-tree", "contract", f_missing_lane_tree,
             2, None)

# The r23 grid pins one reason substring for every exit-2 row
# (REASONS). This case must not be passed by the r23 metadata refusal, so
# the grid needs a "must not contain" list as well. Suggested extension:
#
#     REASONS_NOT = {
#         "F20-promisor-missing-lane-tree": (
#             "partial clone (promisor pack)",
#             "partial clone (extensions.partialclone",
#             "partial clone (remote.",
#         ),
#     }
#
# and in run_case():
#
#     not_met = reason.encode() in err
#     for bad in REASONS_NOT.get(name, ()):
#         not_met = not_met or bad.encode() in err
#     met = ... and not not_met
#
# Recommended (soft, not graded): the refusal should name the unavailable
# object, e.g. the 40-hex tree id, so the diagnostic is actionable.
REASONS_NOT = {
    "F20-promisor-missing-lane-tree": (
        "partial clone (promisor pack)",
        "partial clone (extensions.partialclone",
        "partial clone (remote.",
    ),
}

# Additional graded checks for this case (the r23 runner already checks
# "no traceback", "no timeout", "no marker executed"):
#   * stdout carries no verdict document (no "status" key, no "defects")
#   * the lane object store is unchanged after the run (nothing fetched)
#   * the tip tree is still unavailable after the run (no lazy fetch)
