#!/usr/bin/env python3
"""Round-24 promisor completeness grid for tools/report-landing-audit.py.

Local, offline, synthetic fixtures only.  No network transport, no execution
marker, no repository program: every fixture is built from fresh local git
repositories under one grid-owned root, and every premise is checked with
`git --no-lazy-fetch` plumbing before an auditor runs.

Views (see tests/report-audit/promisor-grid-expectations.json):

  frozen    the r23 base blob (0df800e896f6bce285a81e794ad4ae1d1e6c3a71)
            read from this repository with `git cat-file`, never from a live
            working-tree path.  Historical behaviour, never a target.
  original  the initial registration derived from preregistration.json
            expected_after[3].  Reported; withdrawn for the rows the L1
            amendment changes; never counted as achieved.
  amended   the live policy: .ufo/waves/round-24/oracle-amendment-1.json.
            This is the graded view.

Fixtures keep a blobless clone's local origin reachable on purpose: a lazy
fetch would succeed against it and acquire objects, which the per-run
before/after object inventory reports as `objects_acquired`.  A manual probe
with --keep must therefore keep the origin in place, must not disable or
delete it, and must run git with --no-lazy-fetch; removing the origin to
avoid a flag regression would hide the very regression the tripwire exists to
catch.

Usage:
  promisor-grid.py [--arm frozen|current|both] [--current PATH]
                    [--frozen-path PATH] [--case NAME]... [--json]
                    [--out DIR] [--selftest] [--keep]

Exit: 0 every graded row of every selected arm met its live expectation;
1 at least one did not; 2 could not evaluate (fixture premise, harness or
environment failure).  The original view's failures are reported as
withdrawn, not counted as violations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile

FROZEN = "0df800e896f6bce285a81e794ad4ae1d1e6c3a71"
AUDIT = "tools/report-landing-audit.py"
LANE_DIR = Path(__file__).resolve().parents[2]
EXPECT = "promisor-grid-expectations.json"
REL = ".ufo/reports/round-1/kama.md"
SOURCES = "# sources\n\nfixture: no registry rows\n"
FAKE = "0123456789abcdef0123456789abcdef01234567"
# the exact historical spliced tail: the round-20 errata token
# 0957ce619789d13d894ef21bc863486bcb35b56c is 40 hex, the first 15 hex
# are the real commit and the remaining 25 are the spliced part
HIST_TAIL = "d894ef21bc863486bcb35b56c"
# The fixture root follows the caller's TMPDIR.  There is no baked-in
# scratch path: parallel seats must not share one.
TIMEOUT = 30

REASON_CLASSES = {
    "metadata": ("partial clone", "promisor pack"),
    "unavailable": ("missing", "unavailable", "not available", "no such object",
                    "not found", "incomplete", "absent", "could not read",
                    "cannot read", "unable to read", "traverse parents",
                    "does not exist", "not a valid object", "bad object",
                    "bad file", "not a tree object", "not in 'head'",
                    "corrupt"),
    "unknown-citation": ("unknown", "unresolv", "not prov", "cannot",
                          "unproven", "indetermin", "absent", "missing",
                          "unavailable", "not found", "no such"),
    "unavailable-or-unknown": ("missing", "unavailable", "not available",
                               "no such object", "not found", "incomplete",
                               "absent", "could not read", "cannot read",
                               "unable to read", "traverse parents",
                               "does not exist", "not a valid object",
                               "bad object", "bad file", "not a tree object",
                               "not in 'head'", "corrupt", "unknown",
                               "unresolv", "not prov", "cannot", "unproven",
                               "indetermin"),
}
CNE_PREFIX = "could-not-evaluate:"


class Premise(Exception):
    """The fixture or the harness could not be established: exit 2."""


class Tampered(Exception):
    """The expectation manifest is not the pinned snapshot: exit 2."""


class ContractViolation(Premise):
    """A fixture contract was not established.

    The `reason` attribute names the violated clause ("initial-empty",
    "still-missing", "missing-object"), so a control can require the
    specific clause instead of accepting any failure.
    """

    def __init__(self, reason, message):
        super().__init__(message)
        self.reason = reason


class Unavailable(Exception):
    """The expectation manifest is missing or unreadable: exit 2.

    Without the bytes no tampering can be asserted, so this is a separate
    identity: snapshot_unavailable, never snapshot_tampered.
    """


# The expectation manifest is pinned byte for byte.  The 47 registered cells
# are the ones the L1 froze (the 44-case snapshot plus the three disclosed
# supplement cells); any byte change - a dropped case, a weakened names
# list, a rewritten expectation - is a tampered snapshot and the grid refuses
# to run rather than report a number against it.
MANIFEST_SHA256 = "d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1"
# the size of the pinned table is part of the contract: a dropped case is a
# structural change, caught by the attestation as well as by the byte pin
EXPECTED_CASES = 47
EXPECTED_OPEN_ROWS = 1


# --------------------------------------------------------------- environment

def env(**extra):
    """No inherited GIT_* variables, no user/system configuration."""
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    e.update(extra)
    return e


def git(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise Premise(f"git {' '.join(map(str, args))} in {repo}: rc="
                      f"{p.returncode} "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape")


def git_nofetch(repo, *args, **extra):
    """Plumbing with lazy fetching disabled: a missing object stays missing."""
    return git(repo, "--no-lazy-fetch", *args, **extra)


# ------------------------------------------------------------- fixture safety

def under(root, path):
    """True when path resolves inside root (the grid root)."""
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except (ValueError, OSError):
        return False


def fresh_root(root, path):
    """A fixture root is checked before any .git write happens there."""
    path = Path(path)
    if not under(root, path):
        raise Premise(f"fixture root {path} is outside the grid root {root}")
    if path.exists():
        if not path.is_dir():
            raise Premise(f"fixture root {path} is not a directory")
        if any(path.iterdir()):
            raise Premise(f"fixture root {path} is not empty")
    return path


def init_repo(root, path):
    path = fresh_root(root, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    git(path.parent, "init", "-q", "-b", "master", str(path))
    # r23 M4: a fixture write must never reach an enclosing repository
    top = git(path, "rev-parse", "--show-toplevel").strip()
    if Path(top).resolve() != path.resolve():
        raise Premise(f"{path}: git resolved a different top level {top}")
    return path


def git_dir(repo):
    """Absolute git dir, never `rev-parse --git-path` (r23 M4)."""
    out = git(repo, "rev-parse", "--absolute-git-dir").strip()
    return Path(out)


def write_under(root, path, data):
    path = Path(path)
    if not under(root, path):
        raise Premise(f"refusing to write outside the grid root: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        path.write_text(data, encoding="utf-8")
    else:
        path.write_bytes(data)


def commit(repo, author, when, msg, path, content):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    git(repo, "add", "--", path)
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
        GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
        GIT_AUTHOR_DATE=f"@{when} +0000", GIT_COMMITTER_DATE=f"@{when} +0000")
    return git(repo, "rev-parse", "HEAD").strip()


def publish(fleet, text, when, path=REL):
    """Commit the fleet report; its first add is the audit cutoff."""
    return commit(fleet, "fleet", when, "round-1: report", path, text)


def report_text(cites=(), notes=(), landed_blob=None):
    lines = [f"# kama round 1", "", "## Landed changes", ""]
    for c in cites:
        lines.append(f"- {c}")
    if landed_blob:
        lines.append(f"- {landed_blob}")
    if notes:
        lines.extend(["", "## Notes", ""])
        for n in notes:
            lines.append(n)
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------- marking

def mark_config(repo, tmp):
    """Promisor config only: no marker files, no filter remote."""
    git(repo, "config", "remote.origin.promisor", "true")
    git(repo, "config", "extensions.partialclone", "origin")
    git(repo, "config", "remote.origin.url", str(Path(tmp, "absent-remote.git")))


def mark_markers(root, repo):
    """Paired objects/pack/pack-<sha>.promisor next to its real .pack."""
    git(repo, "repack", "-a", "-d", "-q")
    packs = sorted((git_dir(repo) / "objects" / "pack").glob("*.pack"))
    if not packs:
        raise Premise(f"{repo}: repack produced no pack")
    for pack in packs:
        write_under(root, pack.parent / (pack.stem + ".promisor"), b"")


def blobless_clone(root, origin, dest, filtered=True):
    """A real file:// blobless partial clone (local transport, no network).

    `filtered=False` makes the deliberate negative control: a complete clone
    that claims to be a blobless one.
    """
    git(origin, "config", "uploadpack.allowFilter", "true")
    argv = ["git", "-c", "protocol.file.allow=always", "clone", "-q"]
    if filtered:
        argv.append("--filter=blob:none")
    argv += ["--no-checkout", f"file://{origin}", str(dest)]
    p = subprocess.run(argv, capture_output=True, env=env(), cwd=str(root))
    if p.returncode:
        raise Premise(f"blobless clone failed: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return Path(dest)


def hydrate(clone, origin):
    """Copy the origin's object files into the clone: offline, no transport."""
    src = git_dir(origin) / "objects"
    dst = git_dir(clone) / "objects"
    for d in sorted(src.iterdir()):
        if len(d.name) == 2 and d.is_dir():
            target = dst / d.name
            target.mkdir(parents=True, exist_ok=True)
            for f in sorted(d.iterdir()):
                if f.is_file():
                    shutil.copy2(f, target / f.name)


def assert_blobless_contract(repo, root, hydrated, expect=None):
    """The blobless fixture must really be partial.

    After a genuine blobless clone the promised objects are missing, and the
    missing set is computed with lazy fetching disabled, so the absence is the
    clone's own and never a fetch.  A hydrated clone must end with an empty
    missing set; an unhydrated one must still miss the object the cell is
    about.  A filter that was ignored, or a hydration that happened silently,
    is a premise failure (exit 2), not a different fixture.
    """
    missing = missing_objects(repo, root)
    if hydrated:
        if missing:
            raise ContractViolation(
                "still-missing",
                f"{repo}: the hydrated clone still misses {missing}")
        return missing
    if not missing:
        raise ContractViolation(
            "initial-empty",
            f"{repo}: the blobless clone misses nothing: the filter was "
            f"ignored")
    if expect and expect not in missing:
        raise ContractViolation(
            "missing-object",
            f"{repo}: the blobless clone does not miss {expect} "
            f"(missing: {missing})")
    return missing


def drop_object(repo, sha):
    obj = git_dir(repo) / "objects" / sha[:2] / sha[2:]
    if not obj.exists():
        raise Premise(f"{repo}: object {sha} is not loose, cannot remove it")
    obj.unlink()
    return sha


# ------------------------------------------------------------------ premise

def promisor_facts(repo):
    """The promisor predicate of the r24 review (K3): config, filter remote
    or a paired .promisor marker."""
    facts = {"config": [], "filter": [], "promisor_true": [], "markers": []}
    for entry in git(repo, "config", "--null", "--list",
                     errors="surrogateescape").split("\0"):
        if not entry:
            continue
        key, _, value = entry.partition("\n")
        if key == "extensions.partialclone":
            facts["config"].append(key)
        elif re_fullmatch_remote(key, "promisor"):
            if git_bool(value):
                facts["promisor_true"].append(key)
        elif re_fullmatch_remote(key, "partialclonefilter"):
            facts["filter"].append(key)
    pack = git_dir(repo) / "objects" / "pack"
    if pack.is_dir():
        facts["markers"] = sorted(p.name for p in pack.glob("*.promisor")
                                  if p.with_suffix(".pack").exists())
    facts["promisor_backed"] = bool(facts["config"] or facts["filter"]
                                    or facts["promisor_true"]
                                    or facts["markers"])
    return facts


def re_fullmatch_remote(key, name):
    import re
    return re.fullmatch(rf"remote\..+\.{name}", key) is not None


def git_bool(value):
    v = value.strip().lower()
    if v in ("true", "yes", "on"):
        return True
    if v in ("false", "no", "off", ""):
        return False
    try:
        return int(v, 0) != 0
    except ValueError:
        return True  # git dies on an invalid boolean; treat as configured


def missing_objects(repo, root):
    """Objects the store claims but lacks, by --no-lazy-fetch traversal."""
    out = git_nofetch(repo, "rev-list", "--objects", "--missing=print",
                      "--no-object-names", root)
    return sorted(l[1:] for l in out.split("\n") if l.startswith("?"))


def object_exists(repo, sha):
    """Availability probe with the same isolation as the auditor: no lazy
    fetch, no replace substitution (a plain `cat-file -e` on a promisor
    store could reach the remote)."""
    p = subprocess.run(["git", "--no-lazy-fetch", "--no-replace-objects",
                        "-C", str(repo), "cat-file", "-e", sha + "^{object}"],
                       capture_output=True, env=env())
    return p.returncode == 0


def object_inventory(repo):
    """Every object id the store holds, for the no-acquisition pin."""
    out = git_nofetch(repo, "cat-file", "--batch-all-objects",
                      "--batch-check=%(objectname)")
    return set(out.split())


# ----------------------------------------------------------------- builders

def build(root, tmp, **opt):
    """One fixture family.  Every case is a selection of these options."""
    lane = init_repo(root, Path(tmp, "lane"))
    fleet = init_repo(root, Path(tmp, "fleet"))
    shas = {}
    if opt.get("ancestor"):
        shas["ancestor"] = commit(lane, "kama-shokunin", 900,
                                   "round-1: earlier", "f", "ancestor\n")
    files = []
    if opt.get("sources", True):
        files.append(("corpus/SOURCES.md", SOURCES))
    files.append(("f", "fixture file\n"))
    if opt.get("unused_file"):
        files.append(("notes/unused.txt", "unused\n"))
    if opt.get("unused_tree"):
        files.append(("extra/leaf.txt", "unused tree\n"))
    if opt.get("opaque_tree"):
        files.append(("d/f", "opaque\n"))
    for pth, content in files:
        target = Path(lane, pth)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    git(lane, "add", "--", *[p for p, _ in files])
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: work",
        GIT_AUTHOR_NAME="kama-shokunin", GIT_COMMITTER_NAME="kama-shokunin",
        GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000")
    l1 = git(lane, "rev-parse", "HEAD").strip()
    shas["lane_commit"] = l1
    shas["f_blob"] = git(lane, "rev-parse", f"{l1}:f").strip()
    shas["blob"] = shas["f_blob"]
    shas["fake"] = FAKE
    if opt.get("sources", True):
        shas["sources_blob"] = git(lane, "rev-parse",
                                   f"{l1}:corpus/SOURCES.md").strip()
    shas["tip_tree"] = git(lane, "rev-parse", f"{l1}^{{tree}}").strip()
    if opt.get("omission"):
        shas["omitted"] = commit(lane, "kama-shokunin", 1500, "round-1: more",
                                 "g", "more\n")
    if opt.get("unselected_hole"):
        git(lane, "checkout", "-q", "-b", "side")
        side = commit(lane, "kama-shokunin", 1200, "side: file", "side.txt",
                      "side\n")
        shas["unselected_blob"] = git(lane, "rev-parse",
                                      f"{side}:side.txt").strip()
        git(lane, "checkout", "-q", "master")
    f0 = commit(fleet, "fleet", 1900, "fleet: init", "notes.md", "notes\n")
    shas["fleet_commit"] = f0
    cites = [l1]
    if opt.get("cross_repo"):
        # a citation that exists only in the SECOND audited repository: the
        # lane does not hold it, so the resolution can only come from the
        # fleet.  A lookup that consults the first repository alone must miss.
        cites.append(f0)
    notes = []
    if opt.get("cited_blob"):
        notes.append(f"blob {shas['f_blob']}")
    if opt.get("cited_hidden_blob"):
        shas["hidden_blob"] = git(lane, "rev-parse", f"{l1}:d/f").strip()
        notes.append(f"hidden blob {shas['hidden_blob']}")
    if opt.get("fake_landed"):
        cites.append(FAKE)
    if opt.get("fake_notes"):
        notes.append(f"fake {FAKE}")
    if opt.get("errata"):
        real = shas["lane_commit"]
        spliced = real[:15] + HIST_TAIL
        shas["spliced"] = spliced
        notes.append(f"spliced {spliced}")
    text = report_text(cites, notes, landed_blob=(
        shas["f_blob"] if opt.get("wrong_type") else None))
    publish(fleet, text, 2000)
    shas["report_blob"] = git(fleet, "rev-parse", f"HEAD:{REL}").strip()
    shas["fleet_tip_tree"] = git(fleet, "rev-parse", "HEAD^{tree}").strip()
    if opt.get("errata"):
        spliced = shas["spliced"]
        row = f"1\tunresolved-full-hash\t{spliced}\t{shas['lane_commit']}\tev\n"
        commit(lane, "fixture", 1600, "errata",
               "registry/report-landing-errata.tsv", row)
    # marks
    if opt.get("lane_mark") == "config":
        mark_config(lane, tmp)
    elif opt.get("lane_mark") == "marker":
        mark_markers(root, lane)
    if opt.get("fleet_mark") == "config":
        mark_config(fleet, tmp)
    elif opt.get("fleet_mark") == "marker":
        mark_markers(root, fleet)
    # removals
    for key in opt.get("drop", ()):
        target = {"sources_blob": lane, "tip_tree": lane, "ancestor": lane,
                  "unused_blob": lane, "unused_tree": lane,
                  "unselected_blob": lane, "cited_blob": lane,
                  "opaque_tree": lane, "hidden_blob": lane,
                  "report_blob": fleet, "fleet_tip_tree": fleet}[key]
        shas.setdefault(key, None)
        if key == "unused_blob":
            shas["unused_blob"] = git(lane, "rev-parse",
                                      f"{l1}:notes/unused.txt").strip()
        if key == "unused_tree":
            shas["unused_tree"] = git(lane, "rev-parse",
                                      f"{l1}:extra").strip()
        if key == "opaque_tree":
            shas["missing_subtree"] = git(lane, "rev-parse",
                                          f"{l1}:d").strip()
            shas["opaque_tree"] = shas["missing_subtree"]
        if key == "cited_blob":
            shas["cited_blob"] = shas["f_blob"]
        shas[key] = drop_object(target, shas[key])
        # the removal must really hold: the probe runs with lazy fetching
        # disabled, so a store that could serve the object again is a premise
        # failure (exit 2), never a silently different fixture
        if object_exists(target, shas[key]):
            raise Premise(f"{target}: the removed object {shas[key]} is "
                          f"still available")
    # blobless clones
    if opt.get("blobless_lane"):
        origin = Path(tmp, "lane-origin")
        shutil.move(str(lane), str(origin))
        lane = blobless_clone(root, origin, Path(tmp, "lane"),
                              filtered=not opt.get("complete_clone"))
        # the clone must already be partial: the contract is proved on the
        # clone itself, before any hydration, so a complete clone cannot pass
        # as a hydrated one
        assert_blobless_contract(lane, "refs/heads/master", hydrated=False,
                                  expect=shas.get("f_blob"))
        if opt.get("hydrate_lane"):
            hydrate(lane, origin)
            assert_blobless_contract(lane, "refs/heads/master",
                                      hydrated=True)
    if opt.get("blobless_fleet"):
        origin = Path(tmp, "fleet-origin")
        shutil.move(str(fleet), str(origin))
        fleet = blobless_clone(root, origin, Path(tmp, "fleet"),
                               filtered=not opt.get("complete_clone"))
        assert_blobless_contract(fleet, "HEAD", hydrated=False,
                                  expect=shas.get("report_blob"))
        if opt.get("hydrate_fleet"):
            hydrate(fleet, origin)
            assert_blobless_contract(fleet, "HEAD", hydrated=True)
    if opt.get("errata"):
        if len(shas["spliced"]) != 40:
            raise Premise(f"the spliced token is not a 40-hex sha: "
                          f"{shas['spliced']}")
        if object_exists(lane, shas["spliced"]) or \
                object_exists(fleet, shas["spliced"]):
            raise Premise("the spliced token exists in an audited repository")
    if opt.get("cited_hidden_blob"):
        # Match the supplement: both the subtree and its cited blob are
        # absent; a locally present blob would correctly resolve.
        if object_exists(lane, shas["hidden_blob"]) or \
                object_exists(fleet, shas["hidden_blob"]):
            raise Premise("the cited hidden blob is still present")
    if opt.get("cross_repo"):
        if object_exists(lane, f0):
            raise Premise("the cross-repository token is in the lane too")
        if not object_exists(fleet, f0):
            raise Premise("the cross-repository token is not in the fleet")
    premise = {
        "errata": bool(opt.get("errata")),
        "cross_repo_token": f0 if opt.get("cross_repo") else None,
        "lane_promisor": promisor_facts(lane)["promisor_backed"],
        "fleet_promisor": promisor_facts(fleet)["promisor_backed"],
        "lane_missing": missing_objects(lane, "refs/heads/master"),
        "fleet_missing": missing_objects(fleet, "HEAD"),
        "fake_present": object_exists(lane, FAKE) or object_exists(fleet, FAKE),
    }
    return {"lane": lane, "fleet": fleet, "shas": shas, "premise": premise,
            "errata": bool(opt.get("errata"))}


def c_complete_lane_config(root, tmp):
    return build(root, tmp, lane_mark="config")


def c_complete_fleet_config(root, tmp):
    return build(root, tmp, fleet_mark="config")


def c_complete_lane_marker(root, tmp):
    return build(root, tmp, lane_mark="marker")


def c_complete_fleet_marker(root, tmp):
    return build(root, tmp, fleet_mark="marker")


def c_hydrated_blobless_lane(root, tmp):
    return build(root, tmp, lane_mark="config", blobless_lane=True,
                 hydrate_lane=True)


def c_hydrated_blobless_fleet(root, tmp):
    return build(root, tmp, fleet_mark="config", blobless_fleet=True,
                 hydrate_fleet=True)


def c_complete_lane_plain(root, tmp):
    return build(root, tmp)


def c_complete_fleet_plain(root, tmp):
    return build(root, tmp)


def c_omission_lane_promisor(root, tmp):
    return build(root, tmp, lane_mark="config", omission=True)


def c_omission_lane_plain(root, tmp):
    return build(root, tmp, omission=True)


def c_omission_fleet_promisor(root, tmp):
    return build(root, tmp, fleet_mark="config", omission=True)


def c_omission_marker_lane(root, tmp):
    return build(root, tmp, lane_mark="marker", omission=True)


def c_missing_lane_blob_promisor(root, tmp):
    return build(root, tmp, lane_mark="config", drop=("sources_blob",))


def c_missing_lane_blob_plain(root, tmp):
    return build(root, tmp, drop=("sources_blob",))


def c_missing_lane_tree_promisor(root, tmp):
    return build(root, tmp, lane_mark="config", drop=("tip_tree",))


def c_missing_lane_tree_plain(root, tmp):
    return build(root, tmp, drop=("tip_tree",))


def c_missing_fleet_report_promisor(root, tmp):
    return build(root, tmp, fleet_mark="config", drop=("report_blob",))


def c_missing_fleet_report_plain(root, tmp):
    return build(root, tmp, drop=("report_blob",))


def c_missing_fleet_tree_promisor(root, tmp):
    return build(root, tmp, fleet_mark="config", drop=("fleet_tip_tree",))


def c_missing_fleet_tree_plain(root, tmp):
    return build(root, tmp, drop=("fleet_tip_tree",))


def c_missing_ancestor_promisor(root, tmp):
    return build(root, tmp, lane_mark="config", ancestor=True,
                 drop=("ancestor",))


def c_unknown_citation_incomplete(root, tmp):
    return build(root, tmp, lane_mark="config", unused_file=True,
                 fake_landed=True, drop=("unused_blob",))


def c_unknown_citation_complete(root, tmp):
    return build(root, tmp, lane_mark="config", fake_landed=True)


def c_unknown_citation_fleet_promisor(root, tmp):
    return build(root, tmp, fleet_mark="config", fake_landed=True)


def c_unknown_citation_plain(root, tmp):
    return build(root, tmp, fake_landed=True)


def c_cross_repo_found_promisor(root, tmp):
    return build(root, tmp, lane_mark="config", cross_repo=True)


def c_cross_repo_found_plain(root, tmp):
    return build(root, tmp, cross_repo=True)


def c_unhydrated_blobless_lane(root, tmp):
    return build(root, tmp, lane_mark="config", sources=False,
                 blobless_lane=True)


def c_errata_corrected_missing_sha_plain(root, tmp):
    return build(root, tmp, errata=True)


def c_errata_corrected_missing_sha_promisor(root, tmp):
    return build(root, tmp, lane_mark="config", errata=True)


def c_missing_unselected_branch_promisor(root, tmp):
    return build(root, tmp, lane_mark="config", unselected_hole=True,
                 drop=("unselected_blob",))


def c_missing_unselected_branch_plain(root, tmp):
    return build(root, tmp, unselected_hole=True, drop=("unselected_blob",))


def c_missing_cited_blob_promisor(root, tmp):
    return build(root, tmp, lane_mark="config", cited_blob=True,
                 drop=("cited_blob",))


def c_missing_cited_blob_plain(root, tmp):
    return build(root, tmp, cited_blob=True, drop=("cited_blob",))


def c_unused_missing_blob_promisor(root, tmp):
    return build(root, tmp, lane_mark="config", unused_file=True,
                 drop=("unused_blob",))


def c_unused_missing_blob_plain(root, tmp):
    return build(root, tmp, unused_file=True, drop=("unused_blob",))


def c_unused_missing_blob_fabricated_plain(root, tmp):
    return build(root, tmp, unused_file=True, fake_landed=True,
                 drop=("unused_blob",))


def c_wrong_type_citation_plain(root, tmp):
    return build(root, tmp, wrong_type=True)


def c_wrong_type_citation_promisor(root, tmp):
    return build(root, tmp, lane_mark="config", fleet_mark="config",
                 wrong_type=True)


def c_unused_missing_blob_fabricated_notes_promisor(root, tmp):
    return build(root, tmp, lane_mark="config", unused_file=True,
                 fake_notes=True, drop=("unused_blob",))


def c_unused_missing_blob_fabricated_notes_plain(root, tmp):
    return build(root, tmp, unused_file=True, fake_notes=True,
                 drop=("unused_blob",))


def c_fleet_unhydrated_blobless(root, tmp):
    return build(root, tmp, fleet_mark="config", blobless_fleet=True)


def c_missing_unused_tree_promisor(root, tmp):
    return build(root, tmp, lane_mark="config", unused_tree=True,
                 drop=("unused_tree",))


def c_missing_unused_tree_plain(root, tmp):
    return build(root, tmp, unused_tree=True, drop=("unused_tree",))


def c_opaque_tree_hides_cited_blob(root, tmp):
    return build(root, tmp, lane_mark="config", opaque_tree=True,
                 cited_hidden_blob=True, drop=("opaque_tree", "hidden_blob"))


def c_opaque_tree_fabricated_token(root, tmp):
    return build(root, tmp, lane_mark="config", opaque_tree=True,
                 fake_notes=True, drop=("opaque_tree",))


def c_opaque_unused_tree_clean(root, tmp):
    return build(root, tmp, lane_mark="config", opaque_tree=True,
                 drop=("opaque_tree",))


def c_missing_cited_unselected_branch_promisor(root, tmp):
    return build(root, tmp, lane_mark="config", unselected_hole=True,
                 fake_landed=True, drop=("unselected_blob",))


BUILDERS = {name: obj for name, obj in list(globals().items())
            if name.startswith("c_") and callable(obj)}


# ------------------------------------------------------------------- runner

def resolve_token(token, shas):
    if not isinstance(token, str):
        return token
    if token.startswith("$"):
        return shas.get(token[1:], token)
    return token


def run_auditor(auditor, lane, fleet, tmp, use_errata=False):
    """--no-errata only when the cell does not exercise the ledger."""
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json"]
    if not use_errata:
        argv.append("--no-errata")
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env(), cwd=str(tmp),
                            start_new_session=True)
    try:
        out, err = proc.communicate(timeout=TIMEOUT)
        code, timed_out = proc.returncode, False
    except subprocess.TimeoutExpired:
        timed_out = True
        code = None
        out, err = b"", b""
    finally:
        # the auditor's own timeout is shorter than the grid's: always kill the
        # whole group, never only the auditor (r23 M7)
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            pass
    return code, out.decode(errors="replace"), err.decode(errors="replace"), \
        timed_out


def survivors(tmp):
    """Processes still bound to the case directory: a harness leak."""
    needle = str(tmp)
    alive = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            cmd = (entry / "cmdline").read_bytes().decode(errors="replace")
        except OSError:
            continue
        if needle in cmd:
            alive.append((entry.name, cmd.replace("\0", " ").strip()[:160]))
    return alive


def observed_defects(out):
    """(uncorrected, raw) defect pairs.  A defect corrected by an authorized
    errata row stays in the raw list and leaves the uncorrected list, so a
    clean exit can still carry a corrected defect."""
    try:
        doc = json.loads(out)
    except ValueError:
        return None, None
    raw, uncorrected = [], []
    for res in doc.get("results", []):
        for d in res.get("defects", []):
            pair = (d.get("kind"), d.get("token"))
            raw.append(pair)
            if not d.get("corrected_by"):
                uncorrected.append(pair)
    return sorted(uncorrected), sorted(raw)


def check_exit2_form(err, out, names, forbidden):
    """Every current-arm refusal: typed could-not-evaluate, no verdict
    document, a content-derived reason, and never the r23 metadata refusal."""
    problems = []
    if not err.startswith(CNE_PREFIX):
        problems.append("stderr does not start with could-not-evaluate:")
    if out.strip():
        try:
            json.loads(out)
            problems.append("stdout carries a verdict document")
        except ValueError:
            pass
    low = err.lower()
    if any(f in err for f in forbidden):
        problems.append("reason is the r23 metadata refusal")
    if not any(n and n in err for n in names):
        problems.append("reason does not name the unavailable object")
    return problems


def grade(view, arm_out, err, out, shas, names, forbidden, form_check=True):
    """Compare one observation with one expectation."""
    want = view
    problems = []
    code = arm_out["exit"]
    if want["exit"] is not None and code != want["exit"]:
        problems.append(f"exit {code} != {want['exit']}")
    defects, raw_defects = observed_defects(out)
    if want.get("kinds") is not None and code in (0, 1):
        got = sorted({k for k, _ in defects or []})
        if got != sorted(want["kinds"]):
            problems.append(f"kinds {got} != {sorted(want['kinds'])}")
    if want.get("defects") is not None and code in (0, 1):
        expect = sorted((d["kind"], resolve_token(d["token"], shas))
                        for d in want["defects"])
        if defects != expect:
            problems.append(f"defects {defects} != {expect}")
    if want.get("reason_class") and code == 2:
        terms = REASON_CLASSES[want["reason_class"]]
        if not any(t in err.lower() for t in terms):
            problems.append(f"reason not in class {want['reason_class']}")
    if code == 2 and form_check:
        problems += check_exit2_form(err, out, names, forbidden)
    if arm_out["traceback"]:
        problems.append("traceback")
    if arm_out.get("internal_error"):
        problems.append("the auditor reported an internal error, which is "
                        "not a refusal")
    if arm_out["timed_out"]:
        problems.append("timeout")
    if arm_out["leaked"]:
        problems.append("harness leak")
    acquired = arm_out.get("objects_acquired") or {}
    if any(acquired.get(k) for k in acquired):
        problems.append(f"the audit acquired objects: {acquired}")
    return problems


def run_case(auditor, built, expect, tmp, arm, shas):
    """Run one auditor against one built fixture and grade every view."""
    lane, fleet = built["lane"], built["fleet"]
    use_errata = bool(built.get("errata"))
    before = {"lane": object_inventory(lane), "fleet": object_inventory(fleet)}
    code, out, err, timed_out = run_auditor(auditor, lane, fleet, tmp,
                                            use_errata)
    after = {"lane": object_inventory(lane), "fleet": object_inventory(fleet)}
    acquired = {k: sorted(after[k] - before[k]) for k in after}
    obs = {"arm": arm, "exit": code,
           "traceback": "Traceback (most recent call last)" in err,
           # the auditor's catch-all ("could-not-evaluate: internal: ...") is
           # an error, not a refusal: it is read from the FULL stderr, because
           # the 300 character tail can truncate the identity
           "internal_error": "could-not-evaluate: internal:" in err,
           "timed_out": timed_out, "leaked": bool(survivors(tmp)),
           "objects_acquired": acquired,
           "stderr_tail": err.strip()[-300:]}
    names = [resolve_token(n, shas) for n in expect.get("names_any_of", [])]
    forbidden = expect.get("reason_forbidden", [])
    live = expect.get("amended", expect["original"])
    # the frozen column is the historical reproduction: it is scored without
    # the exit-2 form check, so the r23 metadata refusal still counts as met
    # and the 47/47 history stays intact
    # the actual grade problems are kept per named view: the graded view
    # (the historical frozen column for the frozen arm, the amended view for
    # the current arm) and the strict comparable amended target in both arms
    problems_frozen = (grade(expect["frozen"], obs, err, out, shas, names,
                             forbidden, form_check=False)
                       if arm == "frozen" else None)
    problems_amended = grade(live, obs, err, out, shas, names, forbidden,
                             form_check=True)
    problems_original = (grade(expect["original"], obs, err, out, shas, names,
                               forbidden)
                         if arm == "current" else None)
    obs["problems"] = (problems_frozen if arm == "frozen"
                       else problems_amended)
    obs["amended_problems"] = problems_amended
    obs["original_problems"] = problems_original
    obs["met_frozen"] = (not problems_frozen) if arm == "frozen" else None
    # the amended comparison must be identical in both arms: same exit, same
    # defect set, same reason class, same strong names pin, same no-verdict
    # and same acquisition rules.  The former loose exit/reason-only score is
    # kept beside it under its own label and is never conflated with it.
    obs["met_amended_frozen"] = ((not problems_amended)
                                 if arm == "frozen" else None)
    obs["met_amended_frozen_loose"] = (
        not grade(live, obs, err, out, shas, [], [], form_check=False)
        if arm == "frozen" else None)
    obs["met_original"] = ((not problems_original)
                           if arm == "current" else None)
    obs["met_amended"] = ((not problems_amended)
                          if arm == "current" else None)
    obs["defects"], obs["raw_defects"] = observed_defects(out)
    obs["kinds"] = (sorted({k for k, _ in obs["defects"]})
                    if obs["defects"] is not None else None)
    obs["raw_kinds"] = (sorted({k for k, _ in obs["raw_defects"]})
                        if obs["raw_defects"] is not None else None)
    obs["row_class"] = expect.get("kind")
    obs["met"] = (obs["met_amended"] if arm == "current" else obs["met_frozen"])
    obs["expected_exit"] = live.get("exit")
    obs["expected_kinds"] = live.get("kinds")
    obs["document"] = normalise_document(out, built)
    obs["expectation"] = {"frozen": expect["frozen"],
                           "original": expect["original"], "amended": live}
    return obs


def normalise_document(out, built):
    """The verdict document with the fixture paths replaced by placeholders,
    so a marked repository and its unmarked twin can be compared field by
    field."""
    try:
        doc = json.loads(out)
    except ValueError:
        return None
    text = json.dumps(doc, sort_keys=True)
    text = text.replace(str(built["fleet"]), "<fleet>")
    text = text.replace(str(built["lane"]), "<lane>")
    return json.loads(text)


def load_manifest():
    """Read the pinned expectation manifest, or refuse."""
    path = Path(__file__).resolve().parent / EXPECT
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise Unavailable(f"the expectation manifest is not readable: {exc}")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != MANIFEST_SHA256:
        raise Tampered(f"the expectation manifest bytes changed: {digest} "
                       f"!= {MANIFEST_SHA256}")
    return json.loads(raw.decode("utf-8")), digest


CASE_ID = re.compile(r"^PG[0-9]{2}-[a-z0-9-]+$")
TOKEN_KEYS = {"omitted", "fake", "blob", "cited_blob", "sources_blob",
              "tip_tree", "fleet_tip_tree", "report_blob", "ancestor",
              "hidden_blob", "missing_subtree", "spliced", "unused_blob",
              "unused_tree", "unselected_blob", "cross_repo_token"}
DEFECT_KINDS = {"unresolved-full-hash", "landed-unresolved", "landed-ambiguous",
                "landed-omitted", "landed-section-missing"}


def validate_table(table):
    """Structural attestation of the expectation table.

    Returns the list of problems; an empty list means the table is sound.
    This is the negative capability the selftest exercises: a dropped case,
    a weakened names list and a dangling twin link must all be reported.
    """
    problems = []
    ids = [c["case"] for c in table["cases"]]
    if len(ids) != len(set(ids)):
        problems.append("duplicate case ids")
    if len(ids) != EXPECTED_CASES:
        problems.append(f"{len(ids)} graded cases, expected {EXPECTED_CASES}")
    if len(table.get("open_rows", [])) != EXPECTED_OPEN_ROWS:
        problems.append(f"{len(table.get('open_rows', []))} open rows, "
                        f"expected {EXPECTED_OPEN_ROWS}")
    known = set(ids) | {o["case"] for o in table.get("open_rows", [])}
    for case in table["cases"]:
        name = case["case"]
        if not CASE_ID.fullmatch(name):
            problems.append(f"{name}: malformed case id")
        if case["builder"] not in BUILDERS:
            problems.append(f"{name}: unknown builder {case['builder']}")
        if case.get("twin") and case["twin"] not in known:
            problems.append(f"{name}: twin {case['twin']} is not a case")
        for want in (case["frozen"], case["original"],
                     case.get("amended", case["original"])):
            if want.get("reason_class") not in (None, *REASON_CLASSES):
                problems.append(f"{name}: unknown reason class")
            for defect in (want.get("defects") or []):
                if defect.get("kind") not in DEFECT_KINDS:
                    problems.append(f"{name}: unknown defect kind")
                token = defect.get("token", "")
                if token.startswith("$") and token[1:] not in TOKEN_KEYS:
                    problems.append(f"{name}: unknown token key {token}")
        for token in case.get("names_any_of", []):
            if token.startswith("$") and token[1:] not in TOKEN_KEYS:
                problems.append(f"{name}: unknown names key {token}")
        live = case.get("amended", case["original"])
        if live.get("exit") == 2 and live.get("reason_class") not in (None,
                                                                     "metadata"):
            if not case.get("names_any_of"):
                problems.append(f"{name}: a content refusal without a "
                                f"names_any_of pin")
    for row in table.get("open_rows", []):
        if row["builder"] not in BUILDERS:
            problems.append(f"{row['case']}: unknown builder")
    return problems


def collect_failures(rows, graded, arm):
    """The unique graded cases that fail their graded view or the twin
    constraint, for the selected arm only.

    The graded view is the amended view for the current arm and the
    historical frozen column for the frozen arm.  A case that misses its own
    view and also breaks a twin is counted once.
    """
    key = "met_amended" if arm == "current" else "met_frozen"
    failed = set()
    for row in graded:
        if row.get("arm") != arm:
            continue
        if not row.get(key) or row.get("twin_equal") is False:
            failed.add(row["case"])
    return sorted(failed)


def population(table):
    rows = []
    for case in table["cases"]:
        rows.append([case["case"], case["kind"], case["builder"],
                     case["frozen"], case["original"],
                     case.get("amended", case["original"]),
                     case.get("twin")])
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


def selftest(table, root, manifest_digest):
    """Harness self-check with a real negative capability.

    The table is attested structurally, and three tampered copies of it must
    be rejected: a dropped case, a weakened names list and a dangling twin
    link.  The byte-level attestation is the manifest sha256 pin, exercised
    through the command line: a tampered manifest copy must exit 2 with
    snapshot_tampered, and an unknown --case selector must not be ignored.
    """
    cases = []
    problems = validate_table(table)
    cases.append(("table-valid", not problems))
    cases.append(("manifest-pinned", manifest_digest == MANIFEST_SHA256))
    # negative capability: a dropped case
    dropped = dict(table, cases=table["cases"][:-1])
    cases.append(("negative-dropped-case-rejected",
                  bool(validate_table(dropped))))
    # negative capability: a weakened names list
    weakened = json.loads(json.dumps(table))
    for case in weakened["cases"]:
        if case.get("names_any_of"):
            case["names_any_of"] = []
            break
    cases.append(("negative-weakened-names-rejected",
                  bool(validate_table(weakened))))
    # negative capability: a dangling twin link
    badtwin = json.loads(json.dumps(table))
    for case in badtwin["cases"]:
        if case.get("twin"):
            case["twin"] = "PG99-no-such-case"
            break
    cases.append(("negative-bad-twin-rejected",
                  bool(validate_table(badtwin))))
    # command-line controls: a tampered manifest copy and an unknown selector
    controls = cli_controls(root)
    for name, ok in controls:
        cases.append((name, ok))
    tmp = Path(root, "selftest")
    tmp.mkdir(parents=True, exist_ok=True)
    case = build(root, tmp, lane_mark="config")
    prem = case["premise"]
    cases.append(("premise-marks-lane", prem["lane_promisor"] is True))
    cases.append(("premise-fleet-plain", prem["fleet_promisor"] is False))
    cases.append(("premise-complete", prem["lane_missing"] == []))
    cases.append(("premise-fake-absent", prem["fake_present"] is False))
    broken = build(root, Path(root, "selftest2"), lane_mark="config",
                   unused_file=True, fake_landed=True, drop=("unused_blob",))
    cases.append(("premise-hole-detected",
                  len(broken["premise"]["lane_missing"]) == 1))
    cases.append(("premise-fake-still-absent",
                  broken["premise"]["fake_present"] is False))
    # a "blobless" clone that was not filtered must be refused before the
    # hydration: the negative fixture control
    try:
        build(root, Path(root, "selftest3"), lane_mark="config",
              sources=False, blobless_lane=True, hydrate_lane=True,
              complete_clone=True)
        cases.append(("negative-complete-clone-refused", False))
    except ContractViolation as exc:
        # the specific clause, not any failure: an unrelated setup error
        # must not green this control
        cases.append(("negative-complete-clone-refused",
                      exc.reason == "initial-empty"))
    # the valid path: a genuine partial clone is hydrated into a complete one
    try:
        genuine = build(root, Path(root, "selftest4"), lane_mark="config",
                        sources=False, blobless_lane=True, hydrate_lane=True)
        cases.append(("genuine-partial-clone-hydrated",
                      genuine["premise"]["lane_missing"] == []))
    except Premise:
        cases.append(("genuine-partial-clone-hydrated", False))
    # an asymmetric two-cell twin example must report two unique violating
    # cases, never five
    synthetic = [
        {"case": "PG23-x", "kind": "policy", "arm": "current",
         "met_amended": True, "met_frozen": None, "twin_equal": False},
        {"case": "PG24-y", "kind": "policy", "arm": "current",
         "met_amended": False, "met_frozen": None, "twin_equal": True},
        {"case": "PG01-z", "kind": "policy", "arm": "frozen",
         "met_amended": None, "met_frozen": False, "twin_equal": False},
    ]
    graded_syn = [r for r in synthetic if r["kind"] in ("policy", "control")]
    unique = collect_failures(synthetic, graded_syn, "current")
    cases.append(("unique-violations-per-arm", unique == ["PG23-x", "PG24-y"]))
    failed = [n for n, ok in cases if not ok]
    for name, ok in cases:
        print(f"{'ok' if ok else 'FAIL'} {name}")
    print(f"selftest cases={len(cases)} failed={len(failed)}")
    return 0 if not failed else 1


def cli_controls(root):
    """Command-line controls for the attestation.

    A copy of the runner with a tampered manifest must refuse to run
    (snapshot_tampered, exit 2) - that covers a dropped case and a weakened
    names list at the byte level - and an unknown --case selector must be
    refused rather than ignored, also with --selftest.
    """
    here = Path(__file__).resolve()
    manifest = here.parent / EXPECT
    raw = manifest.read_bytes()
    work = Path(root, "controls")
    work.mkdir(parents=True, exist_ok=True)
    results = []
    for label, mutate in (("dropped-case", "drop"), ("weakened-names",
                                                    "weaken")):
        copy = work / label
        copy.mkdir(parents=True, exist_ok=True)
        shutil.copy2(here, copy / here.name)
        table = json.loads(raw.decode("utf-8"))
        if mutate == "drop":
            table["cases"] = table["cases"][:-1]
        else:
            for case in table["cases"]:
                if case.get("names_any_of"):
                    case["names_any_of"] = []
                    break
        (copy / EXPECT).write_text(json.dumps(table, indent=1) + "\n",
                                   encoding="utf-8")
        proc = subprocess.run([sys.executable, str(copy / here.name),
                               "--selftest"], capture_output=True, env=env(),
                              cwd=str(copy))
        err = proc.stderr.decode(errors="replace")
        results.append((f"cli-{label}-refused",
                        proc.returncode == 2 and "snapshot_tampered" in err))
    proc = subprocess.run([sys.executable, str(here), "--selftest",
                           "--case", "PG99-no-such-case"],
                          capture_output=True, env=env(),
                          cwd=str(work))
    err = proc.stderr.decode(errors="replace")
    results.append(("cli-unknown-selector-refused",
                    proc.returncode == 2 and "unknown case" in err))
    # stand-in auditors, driven behaviourally: a legitimate content-derived
    # refusal must MEET, the same refusal carrying the internal identity must
    # NOT meet, and the identity must be read from the full stderr even when
    # the 300 character tail no longer holds the prefix.
    valid = ("could-not-evaluate: unavailable required object: "
             "corpus/SOURCES.md is missing")
    filler = "x" * 400
    stand_ins = (
        # a legitimate refusal: the correct reason class and the correct
        # names, no internal identity -> it must meet
        ("content-refusal-meets", "import sys\n"
         "sys.stderr.write('" + valid + "\\n')\nsys.exit(2)\n",
         lambda row: row.get("met") is True
         and row.get("internal_error") is False),
        # the same valid reason and names, plus the internal identity, with a
        # body long enough to push the prefix out of the tail -> it must not
        # meet, and the identity must still be seen
        ("internal-same-reason-does-not-meet", "import sys\n"
         "sys.stderr.write('could-not-evaluate: internal: ValueError: "
         "boom\\n" + filler + "\\n" + valid + "\\n')\nsys.exit(2)\n",
         lambda row: row.get("met") is False
         and row.get("internal_error") is True
         and "could-not-evaluate: internal:" not in (row.get("stderr_tail")
                                                      or "")),
        # a traceback is an error too
        ("traceback-detected", "import sys\n"
         "sys.stderr.write('Traceback (most recent call last):\\n  "
         "boom\\nValueError: boom\\n')\nsys.exit(2)\n",
         lambda row: row.get("traceback") is True
         and row.get("met") is False),
    )
    for label, body, check in stand_ins:
        stand_in = work / f"stand-in-{label}.py"
        stand_in.write_text(body, encoding="utf-8")
        proc = subprocess.run([sys.executable, str(here), "--arm", "current",
                               "--current", str(stand_in), "--json",
                               "--case", "PG13-missing-lane-blob-promisor"],
                              capture_output=True, env=env(), cwd=str(work))
        try:
            doc = json.loads(proc.stdout.decode(errors="replace"))
            row = doc["arms"]["current"]["rows"][0]
        except (ValueError, KeyError, IndexError):
            row = {}
        results.append((f"stand-in-{label}", check(row)))
    # the caller's TMPDIR is honoured, and an unavailable requested scratch is
    # a could-not-evaluate in both the normal and the selftest mode
    asked = work / "asked-scratch"
    asked.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run([sys.executable, str(here), "--arm", "current",
                           "--case", "PG07-complete-lane-plain", "--keep"],
                          capture_output=True, env=env(TMPDIR=str(asked)),
                          cwd=str(work))
    honoured = any(p.name.startswith("promisor-grid-")
                   for p in asked.iterdir())
    results.append(("requested-root-honoured",
                    proc.returncode in (0, 1) and honoured))
    for mode, extra in (("normal", []), ("selftest", ["--selftest"])):
        absent = work / f"absent-scratch-{mode}"
        proc = subprocess.run([sys.executable, str(here), *extra],
                              capture_output=True,
                              env=env(TMPDIR=str(absent)), cwd=str(work))
        err = proc.stderr.decode(errors="replace")
        results.append((f"unavailable-root-{mode}-refused",
                        proc.returncode == 2
                        and "could-not-evaluate" in err))
    # a runner copy without its companion manifest: the external oracle is
    # unavailable, which is a could-not-evaluate and not a tampering claim
    bare = work / "no-manifest"
    bare.mkdir(parents=True, exist_ok=True)
    shutil.copy2(here, bare / here.name)
    proc = subprocess.run([sys.executable, str(bare / here.name), "--selftest"],
                          capture_output=True, env=env(), cwd=str(bare))
    err = proc.stderr.decode(errors="replace")
    results.append(("cli-missing-manifest-refused",
                    proc.returncode == 2 and "snapshot_unavailable" in err))
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arm", choices=("frozen", "current", "both"),
                    default="both")
    ap.add_argument("--current", default=str(LANE_DIR / AUDIT))
    ap.add_argument("--frozen-path", default=None)
    ap.add_argument("--case", action="append", help="run only these cases")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", default=None, help="write population.json and candidate.json")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args(argv)
    try:
        table, manifest_digest = load_manifest()
    except Tampered as exc:
        print(f"could-not-evaluate: snapshot_tampered: {exc}", file=sys.stderr)
        return 2
    except Unavailable as exc:
        print(f"could-not-evaluate: snapshot_unavailable: {exc}", file=sys.stderr)
        return 2
    wanted = set(args.case or [])
    known = {c["case"] for c in table["cases"]}
    known |= {o["case"] for o in table["open_rows"]}
    unknown = sorted(wanted - known)
    if unknown:
        # an invalid selector is never ignored, not even with --selftest
        print(f"could-not-evaluate: unknown case(s): {', '.join(unknown)}",
              file=sys.stderr)
        return 2
    if args.selftest:
        try:
            root = make_root()
        except Premise as exc:
            print(f"could-not-evaluate: {exc}", file=sys.stderr)
            return 2
        try:
            return selftest(table, root, manifest_digest)
        finally:
            if not args.keep:
                shutil.rmtree(root, ignore_errors=True)
    arms = ("frozen", "current") if args.arm == "both" else (args.arm,)
    cases = [c for c in table["cases"]
             if not wanted or c["case"] in wanted]
    opens = [o for o in table["open_rows"]
             if not wanted or o["case"] in wanted]
    doc = {"grid": "promisor-grid", "frozen_revision": FROZEN,
           "grid_sha256": hashlib.sha256(
               Path(__file__).resolve().read_bytes()).hexdigest(),
           "expectations_sha256": manifest_digest,
           "population_sha256": population(table),
           "population_size": len(table["cases"]),
           "timeout_seconds": TIMEOUT, "arms": {}}
    try:
        root = make_root()
    except Premise as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    try:
        auditors = {}
        if "frozen" in arms:
            auditors["frozen"] = frozen_auditor(root, args.frozen_path)
        if "current" in arms:
            auditors["current"] = Path(args.current).resolve()
            if not auditors["current"].is_file():
                raise Premise(f"no auditor at {auditors['current']}")
        doc["auditor_sha256"] = {a: hashlib.sha256(
            Path(auditors[a]).read_bytes()).hexdigest() for a in arms}
        for arm in arms:
            rows = []
            for index, case in enumerate(cases):
                tmp = Path(root, arm, f"{index:03d}")
                tmp.mkdir(parents=True, exist_ok=True)
                built = BUILDERS[case["builder"]](root, tmp)
                obs = run_case(auditors[arm], built, case, tmp, arm,
                               built["shas"])
                obs["case"] = case["case"]
                obs["kind"] = case["kind"]
                obs["twin"] = case.get("twin")
                rows.append(obs)
            graded = [r for r in rows if r["kind"] in ("policy", "control")]
            by_case = {r["case"]: r for r in rows}
            twin_links = set()
            for c in cases:
                if c.get("twin"):
                    twin_links.add(frozenset((c["case"], c["twin"])))
            reverse = {}
            for c in cases:
                if c.get("twin"):
                    reverse.setdefault(c["twin"], []).append(c["case"])
            for r in rows:
                partners = []
                if r.get("twin"):
                    partners.append(r["twin"])
                partners += reverse.get(r["case"], [])
                seen = set()
                results = {}
                for partner in partners:
                    if partner in seen or partner == r["case"]:
                        continue
                    seen.add(partner)
                    other = by_case.get(partner)
                    if other is None:
                        continue
                    if r["document"] is None or other["document"] is None:
                        results[partner] = None
                    else:
                        results[partner] = r["document"] == other["document"]
                if results:
                    r["twins"] = results
                    r["twin_equal"] = (all(v for v in results.values()
                                           if v is not None)
                                       if any(v is not None
                                              for v in results.values())
                                       else None)
            graded = [r for r in rows if r["kind"] in ("policy", "control")]
            # unique graded cases that fail their graded view OR the twin
            # constraint, for the selected arm only: a twin mismatch and an
            # individual miss in the same cell count once, and the other
            # arm's failures never leak in
            failed = collect_failures(rows, graded, arm)
            # the amended view is scored per arm: the frozen arm against its
            # own history (met_amended_frozen), the current arm against the
            # live view (met_amended).  A single counter mixed both and
            # reported 0 for the current arm.
            amended_key = ("met_amended_frozen" if arm == "frozen"
                           else "met_amended")
            baseline = [r for r in graded
                        if r["arm"] == arm and r[amended_key]]
            amended_unmet = sorted(r["case"] for r in graded
                                   if r["arm"] == arm and not r[amended_key])
            loose = [r for r in graded
                     if r["arm"] == arm
                     and r.get("met_amended_frozen_loose")]
            loose_unmet = sorted(
                r["case"] for r in graded
                if r["arm"] == arm
                and r.get("met_amended_frozen_loose") is False)
            # a row is withdrawn only when the amendment changed its
            # expectation; an unmet row whose original and amended views
            # agree is an ordinary failure, not a withdrawal
            changed = {c["case"] for c in cases
                       if json.dumps(c["original"], sort_keys=True)
                       != json.dumps(c.get("amended", c["original"]),
                                     sort_keys=True)}
            original_unmet = [r["case"] for r in rows
                              if r["arm"] == "current"
                              and r["met_original"] is False]
            withdrawn = [c for c in original_unmet if c in changed]
            doc["arms"][arm] = {
                "rows": rows,
                "graded": len(graded),
                "violations": len(failed),
                "violating_cases": failed,
                "amended_view_met": len(baseline),
                "amended_view_total": len(graded),
                "amended_view_unmet": amended_unmet,
                "amended_view_measured_on": arm,
                "amended_view_rules": "identical in both arms: exit, defect "
                                      "set, reason class, strong names pin, "
                                      "no-verdict and acquisition rules",
                "amended_view_met_loose_exit_reason_only": len(loose),
                "amended_view_unmet_loose_exit_reason_only": loose_unmet,
                "original_view_unmet": original_unmet,
                "withdrawn_original_failures": withdrawn,
                "amendment_changed_cases": sorted(changed),
                "twin_pairs_in_manifest": len(twin_links),
                "twin_compared": sum(r.get("twin_equal") is not None
                                     for r in rows),
                "twin_pairs_compared": sorted(
                    {p for r in rows for p, v in (r.get("twins") or {}).items()
                     if v is not None}),
                "twin_mismatch": [r["case"] for r in rows
                                  if r.get("twin_equal") is False],
                "tracebacks": sum(bool(r["traceback"]) for r in rows),
                "timeouts": sum(bool(r["timed_out"]) for r in rows),
                "harness_leaks": sum(bool(r["leaked"]) for r in rows),
            }
        if opens and "current" in arms:
            rows = []
            for index, case in enumerate(opens):
                tmp = Path(root, "open", f"{index:03d}")
                tmp.mkdir(parents=True, exist_ok=True)
                built = BUILDERS[case["builder"]](root, tmp)
                obs = run_case(auditors["current"], built, case, tmp,
                               "current", built["shas"])
                obs["case"] = case["case"]
                obs["kind"] = "open"
                obs["not_graded_because"] = case["not_graded_because"]
                rows.append(obs)
            doc["open_rows"] = rows
    except Premise as exc:
        print(f"could-not-evaluate: fixture premise: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        if exc.errno in (28, 122):  # ENOSPC / EDQUOT: environmental
            print(f"could-not-evaluate: environment: {exc}", file=sys.stderr)
            return 2
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # errors are never grid verdicts
        print(f"could-not-evaluate: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 2
    finally:
        if not args.keep:
            shutil.rmtree(root, ignore_errors=True)
        else:
            doc["grid_root"] = str(root)
    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "population.json").write_text(json.dumps({
            "population_sha256": doc["population_sha256"],
            "expectations_sha256": doc["expectations_sha256"],
            "population_size": doc["population_size"],
            "cases": table["cases"], "open_rows": table["open_rows"],
        }, indent=1, sort_keys=False) + "\n", encoding="utf-8")
        (out / "candidate.json").write_text(
            json.dumps(doc, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(doc, indent=1, sort_keys=False))
    else:
        for arm, res in doc["arms"].items():
            for r in res["rows"]:
                mark = "met" if (r["met_amended"] if arm == "current"
                                 else r["met_frozen"]) else "NOT-MET"
                print(f"{arm} {r['case']} {r['kind']} exit={r['exit']} "
                      f"defects={r['defects']} {mark}")
            print(f"{arm} graded={res['graded']} violations={res['violations']} "
                  f"withdrawn={len(res['withdrawn_original_failures'])} "
                  f"tracebacks={res['tracebacks']} timeouts={res['timeouts']} "
                  f"leaks={res['harness_leaks']}")
    return 1 if any(res["violations"] for res in doc["arms"].values()) else 0


def make_root():
    """One grid-owned root per run.

    The caller's TMPDIR is honoured.  An explicitly requested scratch that is
    not usable is a could-not-evaluate (exit 2) before any fixture or
    auditor exists - never a silent fallback elsewhere and never a traceback.
    With no TMPDIR the standard temporary-directory selection is used.
    """
    base = os.environ.get("TMPDIR")
    if base:
        root_dir = Path(base)
        if not root_dir.is_dir() or not os.access(root_dir, os.W_OK):
            raise Premise(f"the requested scratch {base} is unavailable")
        try:
            return Path(tempfile.mkdtemp(prefix="promisor-grid-", dir=base))
        except OSError as exc:
            raise Premise(f"the requested scratch {base} is unavailable: "
                          f"{exc}")
    try:
        return Path(tempfile.mkdtemp(prefix="promisor-grid-"))
    except OSError as exc:
        raise Premise(f"no temporary directory is available: {exc}")


def frozen_auditor(root, explicit):
    if explicit:
        return Path(explicit).resolve()
    p = subprocess.run(["git", "-C", str(LANE_DIR), "cat-file", "blob",
                        f"{FROZEN}:{AUDIT}"], capture_output=True, env=env())
    if p.returncode:
        raise Premise(f"cannot read the frozen auditor blob: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    path = Path(root, "frozen-audit.py")
    path.write_bytes(p.stdout)
    return path


if __name__ == "__main__":
    sys.exit(main())
