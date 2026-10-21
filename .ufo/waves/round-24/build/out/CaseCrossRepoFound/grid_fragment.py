#!/usr/bin/env python3
"""CANDIDATE GRID FRAGMENT — round-24 promisor grid (CaseCrossRepoFound).

Not production code.  Copy the builder and the row into
`tests/report-audit/promisor-grid.py` (owner of the adopting grid), or
adapt them to that grid's own helper names.

CASE UNDER SPECIFICATION
    "promisor-marked lane; a cited token is absent from the lane's local
     object store and present in the fleet's local object store -> the
     audit resolves it from the fleet and returns the full-clone twin's
     verdict (exit 0, no findings), instead of refusing the lane."

WHY THE EXPECTATION IS FIXED BEFORE IMPLEMENTATION
    The expected verdict is the FULL-CLONE TWIN's verdict: same upstream,
    same commits, same report, same fleet, same binary, same run; only the
    lane clone's filter and promisor metadata differ.  The twin is
    measured, not assumed (evidence: lane exit 2
    "partial clone (promisor pack)" / twin exit 0 "clean", base 0df800e).

GRADING
    `control` row: the promisor-marked lane must produce the SAME exit and
    the SAME finding set as its full-clone twin (exit 0, no findings).
    Equality with the twin — not merely "not exit 2" — is the requirement.

PAIRING REQUIREMENT (do not drop)
    This row MUST be graded in the same arm as a row whose lane genuinely
    lacks a required object that no other audited repository has (the
    round-23 `f_promisor_pack` row, repo-state-grid.py:195).  Measured
    (evidence-mutants.json, mutant M1): a repair that only removes the
    up-front promisor refusal makes this row pass while that row turns
    into a false `unresolved-full-hash` exit 1 — unavailable evidence
    turned into a proved absence.  With this row alone, that naive repair
    would pass; paired, the repair must add availability checking.

    Conversely, this row is what forbids the opposite over-correction: a
    repair that treats every lane-side miss as unknown (exit 2) or that
    stops consulting the fleet fails here (mutants M3 and M2).

SAFETY
    The only transport is the local `file://` clone that creates the
    partial clone; no host is contacted, no program is configured or run,
    and the audit itself must not fetch (the case asserts the lane's
    object inventory is unchanged and the cited blob is still absent
    after the run).
"""
from __future__ import annotations

import subprocess

# The cited source file is larger than this, so the clone's size filter
# leaves it out of the lane's local object store; every other blob (the
# empty errata file) stays local.
BLOB_LIMIT = 1024
BIG = ("cross-repo token evidence\n" + "x" * 4096 + "\n")


def _clone(env, origin, dest, *extra):
    subprocess.run(["git", "-c", "protocol.file.allow=always", "clone", "-q",
                    "--no-local", "--no-checkout", *extra,
                    f"file://{origin}", str(dest)],
                   check=True, capture_output=True, env=env)


def c_promisor_lane_token_found_in_fleet(tmp):
    """A promisor-marked lane whose cited blob is absent locally but
    present in the fleet.  The audit must resolve it from the fleet.

    Returns (lane, fleet, argv_extra, marker_or_None).
    """
    import os
    from pathlib import Path

    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
               GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
               GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")

    origin = Path(tmp, "origin")
    subprocess.run(["git", "init", "-q", "-b", "master", str(origin)], check=True,
                   capture_output=True, env=env)
    g(origin, "config", "uploadpack.allowFilter", "true")
    lc = commit(origin, "kama-shokunin", 1000, "round-1: work", "notes.md",
                BIG.encode())
    commit(origin, "fixture", 1100, "registry: errata",
           "registry/report-landing-errata.tsv", b"")
    blob = g(origin, "rev-parse", f"{lc}:notes.md")

    lane = Path(tmp, "lane")
    _clone(env, origin, lane, f"--filter=blob:limit={BLOB_LIMIT}")

    fleet = Path(tmp, "fleet")
    init(fleet)
    fleet_commit = commit(fleet, "fleet", 1500, "round-1: evidence vendor",
                          "vendor/notes.md", BIG.encode())
    # The blob is cited in the report BODY, before the Landed section: a
    # token inside the Landed section is peeled with `^{commit}` and a
    # blob would then be an unresolvable "landed" citation.  The fleet's own
    # commit IS in the Landed section: it exercises the peeled lookup (bare
    # name first, then `<token>^{commit}`), whose bare recursion must not
    # refuse before the fleet has been read.
    publish(fleet, f"# kama round 1\n\nblob {blob}\n\n"
                  f"## Landed changes\n\n- {lc}\n- {fleet_commit}\n".encode())

    # premises: the lane is promisor-marked and lacks exactly the cited
    # blob; the fleet has that blob locally.
    keys = [line.split("\n")[0] for line in
            g(lane, "config", "--null", "--list").split("\0") if line]
    require("remote.origin.promisor" in keys, "lane is not promisor-marked")
    require(any(p.suffix == ".promisor" for p in
                Path(lane, ".git/objects/pack").glob("*.promisor")),
            "lane has no .promisor pack")
    missing = [l for l in g(lane, "rev-list", "--objects", "--all",
                            "--missing=print").splitlines()
               if l.startswith("?")]
    require(blob in [l[1:] for l in missing],
            "the cited blob is not absent from the lane")
    require(g(fleet, "cat-file", "-t", blob) == "blob",
            "the cited blob is not in the fleet")
    return lane, fleet, [], None


def c_promisor_lane_token_found_in_fleet_twin(tmp):
    """The full-clone twin of the row above: the same upstream, complete.
    Its verdict (exit 0, no findings) is the expected value of the row."""
    import os
    from pathlib import Path

    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
               GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
               GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")

    origin = Path(tmp, "origin")
    subprocess.run(["git", "init", "-q", "-b", "master", str(origin)], check=True,
                   capture_output=True, env=env)
    lc = commit(origin, "kama-shokunin", 1000, "round-1: work", "notes.md",
                BIG.encode())
    commit(origin, "fixture", 1100, "registry: errata",
           "registry/report-landing-errata.tsv", b"")

    twin = Path(tmp, "twin")
    subprocess.run(["git", "-c", "protocol.file.allow=always", "clone", "-q",
                    "--no-local", f"file://{origin}", str(twin)],
                   check=True, capture_output=True, env=env)

    fleet = Path(tmp, "fleet")
    init(fleet)
    blob = g(origin, "rev-parse", f"{lc}:notes.md")
    fleet_commit = commit(fleet, "fleet", 1500, "round-1: evidence vendor",
                          "vendor/notes.md", BIG.encode())
    publish(fleet, f"# kama round 1\n\nblob {blob}\n\n"
                  f"## Landed changes\n\n- {lc}\n- {fleet_commit}\n".encode())
    require(not [l for l in g(twin, "rev-list", "--objects", "--all",
                              "--missing=print").splitlines()
                 if l.startswith("?")], "the twin is not complete")
    return twin, fleet, [], None


# ------------------------------------------------------------------- rows
#
# name, kind, builder, expected exit, expected finding kinds
#
#   ("C16-promisor-lane-token-found-in-fleet", "control",
#    c_promisor_lane_token_found_in_fleet, 0, []),
#   ("C16-twin-full-clone", "control",
#    c_promisor_lane_token_found_in_fleet_twin, 0, []),
#
# The exit/kinds above are the twin's observed values (measured 2026-10-21,
# base 0df800e, evidence.json: lane exit 2 "partial clone (promisor pack)",
# twin exit 0 "clean").
#
# Grading must compare the two rows (promisor lane == full twin), not just
# the pinned exit: a repair that resolves the token from the fleet returns
# exit 0 with no findings in both rows.

# ------------------------------------------------------------------ helpers
# Expected to exist in the adopting grid (repo-state-grid.py:88-125):
#   pair(tmp), init(path), commit(repo, author, when, msg, path, content),
#   publish(fleet, text), report(cites), g(repo, *args), require(cond, msg)
#
# `commit` and `publish` in the round-23 grid write `msg + "\n"` when no
# content is given; this fragment always passes explicit content, so the
# two helpers agree on the blob OID (identical content => identical OID).
