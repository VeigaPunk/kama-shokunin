# Grid-row fragment for tests/report-audit/promisor-grid.py (CaseMissingFleetTree)
#
# Style: the helpers (init, commit, report, publish, pair, require, g, env)
# are those of tests/report-audit/repo-state-grid.py. Paste the builders and
# the three CASES rows into the new grid; nothing here depends on the
# auditor implementation.
#
# The case: the fleet history traversal that establishes a report's first-add
# cutoff diffs the tree of every commit on the path. When an ancestor tree is
# absent from the fleet object store the cutoff is unknown, and unknown is not
# absence: the audit must answer could-not-evaluate, never a verdict.

# --------------------------------------------------------------- builders

def _fleet_report_pair(tmp, marked):
    """lane: one cited round-1 commit. fleet: F1 adds the report, F2 is HEAD."""
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, report([lc]), when=2000)
    f1 = g(fleet, "rev-parse", "HEAD")
    commit(fleet, "fleet", 2100, "later note", "notes.txt", b"note\n")
    if marked:
        canary = init(Path(tmp, "canary"))
        commit(canary, "canary", 500, "canary sentinel")
        g(fleet, "config", "remote.origin.url", str(canary))
        g(fleet, "config", "remote.origin.promisor", "true")
        g(fleet, "config", "remote.origin.partialclonefilter", "blob:none")
        g(fleet, "config", "extensions.partialclone", "origin")
    return lane, fleet, lc, f1


def _drop_root_tree(fleet, commit_sha):
    """Delete one commit's root tree from the object store (loose object)."""
    tree = g(fleet, "rev-parse", f"{commit_sha}^{{tree}}")
    loose = Path(fleet, ".git/objects", tree[:2], tree[2:])
    require(loose.is_file(), f"root tree {tree} is not a loose object")
    loose.unlink()
    require(g(fleet, "cat-file", "-t", tree, check=False) != "tree",
            f"root tree {tree} is still resolvable")
    return tree


def _cutoff_traversal_fails(fleet):
    """The report traversal must need the missing tree, else the row is void."""
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                        "-C", str(fleet), "log", "--diff-filter=A",
                        "--format=%at", "--", REL],
                       capture_output=True, env=env())
    return p.returncode != 0


def f_missing_fleet_ancestor_tree(tmp):
    """Promisor-marked fleet, ancestor tree absent: the cutoff is unknown."""
    lane, fleet, lc, f1 = _fleet_report_pair(tmp, marked=True)
    _drop_root_tree(fleet, f1)
    require(_cutoff_traversal_fails(fleet),
            "the report traversal completed without the missing ancestor "
            "tree: the case would be vacuous")
    marker = Path(fleet, ".git/FETCH_HEAD")  # a transport would create it
    require(not marker.exists(), "FETCH_HEAD exists before the audit run")
    return lane, fleet, [], marker


def f_missing_fleet_ancestor_tree_unmarked(tmp):
    """Same missing tree, no promisor metadata: availability decides alone."""
    lane, fleet, lc, f1 = _fleet_report_pair(tmp, marked=False)
    _drop_root_tree(fleet, f1)
    require(_cutoff_traversal_fails(fleet),
            "the report traversal completed without the missing ancestor tree")
    return lane, fleet, [], None


def c_complete_fleet_promisor(tmp):
    """Promisor-marked fleet, every object present: the clean verdict."""
    lane, fleet, lc, f1 = _fleet_report_pair(tmp, marked=True)
    marker = Path(fleet, ".git/FETCH_HEAD")
    require(not marker.exists(), "FETCH_HEAD exists before the audit run")
    return lane, fleet, [], marker


# ------------------------------------------------------------------ rows
# expected exit, expected finding kinds. MFT-3 is a POLICY row: the frozen
# r23 base refuses it with exit 2 ("partial clone (remote.origin.promisor)")
# - the operability harm r24 repairs - while the repaired auditor must answer
# exit 0 with no findings. A grid that scores both arms against one
# expectation needs a per-arm expectation for this row.

#     ("MFT-1-missing-fleet-ancestor-tree-promisor", "fault",
#      f_missing_fleet_ancestor_tree, 2, None),
#     ("MFT-2-missing-fleet-ancestor-tree-unmarked", "control",
#      f_missing_fleet_ancestor_tree_unmarked, 2, None),
#     ("MFT-3-complete-fleet-promisor", "policy",
#      c_complete_fleet_promisor, 0, []),

# REASONS entries. A single substring cannot express "the refusal must name
# an unavailable object", because two sound implementations word it
# differently ("unable to read tree (...)" from git itself vs "... are missing
# locally" from an explicit closure check). The any-of extension below is
# proposed for the new grid; the same patch can go into repo-state-grid.py if
# the historical rows are re-used there.

#     "MFT-1-missing-fleet-ancestor-tree-promisor":
#         ("unable to read tree", "missing", "absent", "not provable",
#          "unavailable"),
#     "MFT-2-missing-fleet-ancestor-tree-unmarked":
#         ("unable to read tree", "missing", "absent", "not provable",
#          "unavailable"),

# Proposed REASONS any-of patch (repo-state-grid.py, run_case):
#
#     reason = REASONS.get(name)
#     if reason is None:
#         reason_ok = True
#     elif isinstance(reason, (tuple, list)):
#         reason_ok = any(r.encode() in err for r in reason)
#     else:
#         reason_ok = reason.encode() in err
#     met = (not timed_out and not traceback and not executed
#            and code == want_exit
#            and (want_kinds is None or kinds == sorted(want_kinds))
#            and reason_ok)
#
# The rows also need the no-transport assertion. The marker above is the
# fleet's FETCH_HEAD path: the grid's "executed" flag is then "a transport was
# attempted". The canary repository's refs are unchanged as well (checked in
# the standalone runner of this lane, not in the grid).
