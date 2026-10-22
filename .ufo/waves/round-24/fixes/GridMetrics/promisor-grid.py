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
SCRATCH = Path("/fast/scratch/hyaku/kama-r24")
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
# the r23 blanket refusal must never be the reason of a current-arm refusal
METADATA_REFUSAL = ("partial clone (", "promisor pack")
CNE_PREFIX = "could-not-evaluate:"


class Premise(Exception):
    """The fixture or the harness could not be established: exit 2."""


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


def blobless_clone(root, origin, dest):
    """A real file:// blobless partial clone (local transport, no network)."""
    git(origin, "config", "uploadpack.allowFilter", "true")
    p = subprocess.run(["git", "-c", "protocol.file.allow=always", "clone", "-q",
                        "--filter=blob:none", "--no-checkout",
                        f"file://{origin}", str(dest)],
                       capture_output=True, env=env(), cwd=str(root))
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
        lane = blobless_clone(root, origin, Path(tmp, "lane"))
        if opt.get("hydrate_lane"):
            hydrate(lane, origin)
    if opt.get("blobless_fleet"):
        origin = Path(tmp, "fleet-origin")
        shutil.move(str(fleet), str(origin))
        fleet = blobless_clone(root, origin, Path(tmp, "fleet"))
        if opt.get("hydrate_fleet"):
            hydrate(fleet, origin)
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
    if code == 2 and arm_out["arm"] == "current" and form_check:
        problems += check_exit2_form(err, out, names, forbidden)
    if arm_out["traceback"]:
        problems.append("traceback")
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
           "timed_out": timed_out, "leaked": bool(survivors(tmp)),
           "objects_acquired": acquired,
           "stderr_tail": err.strip()[-300:]}
    names = [resolve_token(n, shas) for n in expect.get("names_any_of", [])]
    forbidden = expect.get("reason_forbidden", [])
    live = expect.get("amended", expect["original"])
    obs["met_frozen"] = (not grade(expect["frozen"], obs, err, out, shas, names,
                                    forbidden)) if arm == "frozen" else None
    # the frozen arm is scored against the amended view too: that score is the
    # historical baseline the repair is measured against, not a target
    obs["met_amended_frozen"] = (
        not grade(live, obs, err, out, shas, [], [], form_check=False)
        if arm == "frozen" else None)
    obs["met_original"] = (not grade(expect["original"], obs, err, out, shas,
                                     names, forbidden)) if arm == "current" else None
    obs["met_amended"] = (not grade(live, obs, err, out, shas, names,
                                    forbidden)) if arm == "current" else None
    obs["defects"], obs["raw_defects"] = observed_defects(out)
    obs["kinds"] = (sorted({k for k, _ in obs["defects"]})
                    if obs["defects"] is not None else None)
    obs["raw_kinds"] = (sorted({k for k, _ in obs["raw_defects"]})
                        if obs["raw_defects"] is not None else None)
    # the mutation runner grades rows by kind: the manifest's "policy" rows
    # are declared behaviour contracts, the "control" rows are no-harm twins
    obs["kind"] = "contract" if expect.get("kind") == "policy" else "control"
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


def population(table):
    rows = []
    for case in table["cases"]:
        rows.append([case["case"], case["kind"], case["builder"],
                     case["frozen"], case["original"],
                     case.get("amended", case["original"]),
                     case.get("twin")])
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


def selftest(table, root):
    """Harness self-check: the table, the builders, the premise machinery."""
    cases = []
    names = [c["case"] for c in table["cases"]]
    cases.append(("unique-case-ids", len(names) == len(set(names))))
    cases.append(("builders-present",
                  all(c["builder"] in BUILDERS for c in table["cases"])))
    cases.append(("open-builders-present",
                  all(o["builder"] in BUILDERS for o in table["open_rows"])))
    cases.append(("reason-classes-known",
                  all(w.get("reason_class") in (None, *REASON_CLASSES)
                      for c in table["cases"]
                      for w in (c["frozen"], c["original"],
                                c.get("amended", c["original"])))))
    cases.append(("population-stable", population(table) == population(table)))
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
    failed = [n for n, ok in cases if not ok]
    for name, ok in cases:
        print(f"{'ok' if ok else 'FAIL'} {name}")
    print(f"selftest cases={len(cases)} failed={len(failed)}")
    return 0 if not failed else 1


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
    table = json.loads((Path(__file__).resolve().parent / EXPECT)
                       .read_text(encoding="utf-8"))
    if args.selftest:
        root = make_root()
        try:
            return selftest(table, root)
        finally:
            if not args.keep:
                shutil.rmtree(root, ignore_errors=True)
    arms = ("frozen", "current") if args.arm == "both" else (args.arm,)
    wanted = set(args.case or [])
    known = {c["case"] for c in table["cases"]}
    known |= {o["case"] for o in table["open_rows"]}
    unknown = sorted(wanted - known)
    if unknown:
        print(f"could-not-evaluate: unknown case(s): {', '.join(unknown)}",
              file=sys.stderr)
        return 2
    cases = [c for c in table["cases"]
             if not wanted or c["case"] in wanted]
    opens = [o for o in table["open_rows"]
             if not wanted or o["case"] in wanted]
    doc = {"grid": "promisor-grid", "frozen_revision": FROZEN,
           "expectations_sha256": hashlib.sha256(
               (Path(__file__).resolve().parent / EXPECT).read_bytes()
           ).hexdigest(),
           "population_sha256": population(table),
           "population_size": len(table["cases"]),
           "timeout_seconds": TIMEOUT, "arms": {}}
    root = make_root()
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
            live_fail = [r for r in graded
                         if not r["met_amended"] if r["arm"] == "current"]
            frozen_fail = [r for r in graded
                           if not r["met_frozen"] if r["arm"] == "frozen"]
            # the twin comparison is computed above: a mismatch is a failure
            live_fail += [r for r in graded
                          if r.get("twin_equal") is False]
            frozen_fail += [r for r in graded
                            if r.get("twin_equal") is False]
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
                "violations": len(live_fail) + len(frozen_fail),
                "violating_cases": [r["case"] for r in live_fail + frozen_fail],
                "amended_view_met": len(baseline),
                "amended_view_total": len(graded),
                "amended_view_unmet": amended_unmet,
                "amended_view_measured_on": arm,
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
    """One grid-owned root per run, under /fast/scratch (never /tmp)."""
    base = os.environ.get("TMPDIR")
    if base:
        candidate = Path(base).resolve()
        if SCRATCH not in candidate.parents and candidate != SCRATCH:
            base = None
    else:
        base = None
    root = Path(tempfile.mkdtemp(prefix="promisor-grid-",
                                 dir=str(base or SCRATCH)))
    return root


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
