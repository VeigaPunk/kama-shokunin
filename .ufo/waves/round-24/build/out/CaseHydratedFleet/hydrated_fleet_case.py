#!/usr/bin/env python3
"""Round-24 oracle case: a genuine file:// blob:none FLEET clone, hydrated
offline by explicit local copying, must be auditable with the same report
bytes, the same cutoff and the same substantive verdict as a full clone.

This is a CANDIDATE fixture builder for the round-24 promisor grid. It is not
production code; it changes nothing in the lane repository. The grader's own
grid may adopt, adapt or reject it.

What the case fixes (one variable: the audited FLEET side)

  The audited LANE side is always a plain, complete, non-promisor local
  repository, so the only thing that varies between arms is the fleet
  repository the auditor reads the report from.

  arms (fleet side)
    full          a plain full clone of the fleet origin (reference)
    hydrated      a real `--filter=blob:none --no-local --no-checkout`
                  file:// clone whose promisor metadata
                  (remote.origin.promisor, remote.origin.partialclonefilter,
                  the .promisor pack marker) is RETAINED, and whose missing
                  blobs are supplied by an OFFLINE copy of the origin's
                  object store (plain file copy: no transport, no network,
                  no program, no repository hook)
    unhydrated    the same blob:none clone, left incomplete
    gap           the same blob:none clone, hydrated EXCEPT for one
                  unrelated blob (an object no evidence depends on)

  shapes (report content, decided before any candidate runs)
    clean         the report cites every pre-cutoff lane commit
    omission      the report cites one of the two pre-cutoff lane commits

Expected outcomes, derived from the constructed history (see EXPECTED_BASE
and EXPECTED_CANDIDATE). The base column is the r23 behaviour: a promisor
repository is refused on its metadata alone, which is the harm this wave
repairs. The candidate column is the calibrated expectation:

    full/clean         exit 0, no defect
    full/omission      exit 1, defect landed-omitted
    hydrated/clean     exit 0, no defect              == full/clean
    hydrated/omission  exit 1, defect landed-omitted  == full/omission
    unhydrated/*       exit 2 could-not-evaluate      (never 0, never 1)
    gap/*              exit 0 / exit 1 as full/*      (advisory: see below)

`gap` is advisory, not a kill row: the preregistration says "content
completeness AND availability of required evidence determine the outcome",
which reads as required-evidence availability. A candidate that instead
requires whole-repository closure would refuse `gap`; that is a policy
difference the wave must document, not a silent kill.

Fixtures discipline:
  * every path is created under the caller-supplied scratch root, and the
    builder asserts that no fixture path escapes it;
  * the only transport used is the initial local file:// clone of the two
    local origins; the fleet origin is DELETED before the audit runs, so a
    lazy fetch would fail loudly instead of succeeding silently;
  * no repository program is configured or invoked (no sshCommand, no gpg,
    no hook, no filter helper): there is nothing to execute;
  * every git call that touches the fixture uses --no-lazy-fetch, so no
    fixture can fetch anything even if the audit did try.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REL = ".ufo/reports/round-1/kama.md"
EXTRA = "notes.txt"
AUTHOR = "kama-shokunin"
EMAIL = "kama@shokunin.local"
ARMS = ("full", "hydrated", "unhydrated", "gap")
SHAPES = ("clean", "omission")
HEX = set("0123456789abcdef")


class Premise(Exception):
    """The fixture did not establish its property: cannot evaluate."""


# --------------------------------------------------------------------- git


def env(**extra):
    """No inherited GIT_* variables and no user/system config."""
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", **extra)
    return e


def run(args, data=None, check=True, cwd=None, **extra):
    """git with --no-lazy-fetch: a promisor remote can never be contacted."""
    p = subprocess.run(["git", "--no-lazy-fetch", *args], input=data,
                       capture_output=True, env=env(**extra), cwd=cwd)
    if check and p.returncode != 0:
        raise Premise(f"git {' '.join(args[:5])}: rc={p.returncode} "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return p


def g(repo, *args, data=None, check=True, **extra):
    p = run(["-C", str(repo), *args], data=data, check=check, **extra)
    return p.stdout.decode("utf-8", errors="surrogateescape").strip()


def commit(repo, msg, when, path, content, author=AUTHOR):
    target = Path(repo) / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    g(repo, "add", path)
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_EMAIL=EMAIL, GIT_COMMITTER_EMAIL=EMAIL,
      GIT_AUTHOR_DATE=f"@{when} +0000", GIT_COMMITTER_DATE=f"@{when} +0000")
    return g(repo, "rev-parse", "HEAD")


# ----------------------------------------------------------------- fixture


def build_lane(root):
    """Audited lane: a plain complete local repo, two round-1 commits.

    Author times 1000 and 1500 are both earlier than the fleet report's
    first add (2000), so both commits are required and are candidates for
    the landed-omitted defect.
    """
    lane = Path(root) / "lane"
    lane.mkdir(parents=True)
    run(["init", "-q", "-b", "master", str(lane)])
    a = commit(lane, "round-1: work", 1000, "f", "work\n")
    b = commit(lane, "round-1: extra", 1500, "g", "extra\n")
    return lane, a, b


def build_fleet_origin(root, cited, extra_file):
    """Fleet origin holding the round-1 kama report, authored at t=2000."""
    origin = Path(root) / "fleet-origin"
    origin.mkdir(parents=True)
    run(["init", "-q", "-b", "master", str(origin)])
    g(origin, "config", "gc.auto", "0")
    g(origin, "config", "uploadpack.allowFilter", "true")
    body = "# kama round 1\n\n## Landed changes\n\n" + "".join(
        f"- `{sha}`\n" for sha in cited)
    target = Path(origin) / REL
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    if extra_file:
        (Path(origin) / EXTRA).write_text("unrelated note\n", encoding="utf-8")
    g(origin, "add", "-A")
    g(origin, "-c", "commit.gpgsign=false", "commit", "-q",
      "-m", "round-1: kama report",
      GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
      GIT_AUTHOR_EMAIL="fleet@shokunin.local",
      GIT_COMMITTER_EMAIL="fleet@shokunin.local",
      GIT_AUTHOR_DATE="@2000 +0000", GIT_COMMITTER_DATE="@2000 +0000")
    return origin, body


def clone_fleet(origin, dest, blobless):
    """file:// clone of the fleet origin.

    A blobless clone is made with --no-checkout: checking out would ask the
    promisor remote for the tip blobs, which would hydrate the fixture and
    destroy the incompleteness the arm is about. --no-local forces the
    file:// transport so the filter is actually applied instead of being
    ignored by a local hardlink copy.

    For the blobless arms `extensions.partialclone` is also written
    explicitly. git 2.56 writes only `remote.origin.promisor` and
    `remote.origin.partialclonefilter` on clone, so a candidate that
    removed only the pack-marker detector (and kept the config-key one)
    would still refuse every arm; and a candidate that removed only the
    config-key detector would still refuse on the pack marker. Writing
    both keys exercises both detectors on every blobless arm, so the case
    cannot be passed by fixing only one of them.
    """
    args = ["-c", "protocol.file.allow=always", "clone", "-q", "--no-local"]
    if blobless:
        args += ["--filter=blob:none", "--no-checkout"]
    args += [f"file://{origin}", str(dest)]
    run(args, cwd=str(Path(dest).parent))
    repo = Path(dest)
    if blobless:
        g(repo, "config", "extensions.partialclone", "blob")
    return repo


def config_map(repo):
    out = g(repo, "config", "--null", "--list")
    keys = {}
    for entry in filter(None, out.split("\0")):
        key, _, value = entry.partition("\n")
        keys[key] = value
    return keys


def promisor_metadata(repo):
    """The promisor metadata a genuine partial clone carries."""
    return {k: v for k, v in config_map(repo).items()
            if k == "extensions.partialclone"
            or k.startswith("remote.origin.promisor")
            or k.startswith("remote.origin.partialclonefilter")}


def program_surface(repo):
    """Configured git programs and executable hooks: anything executable."""
    found = {}
    for key, value in config_map(repo).items():
        low = key.lower()
        for pattern in ("core.sshcommand", "core.gpgsign", "gpg.program",
                        "gpg.ssh.program", "diff.*.textconv", "filter.*",
                        "core.sshkeycommand", "credential.helper"):
            head = pattern.split("*")[0]
            if low == pattern or (pattern.endswith("*") and low.startswith(head)):
                found[key] = value
    hooks = Path(repo) / ".git" / "hooks"
    active = []
    if hooks.is_dir():
        active = sorted(p.name for p in hooks.iterdir()
                        if p.is_file() and os.access(p, os.X_OK)
                        and not p.name.endswith(".sample"))
    return {"config": found, "executable_hooks": active}


def loose_path(repo, oid):
    return Path(repo) / ".git" / "objects" / oid[:2] / oid[2:]


def hydrate_offline(origin, clone, exclude=()):
    """Supply missing objects by copying the origin's object store.

    No transport, no program: a plain file copy of loose object files. The
    clone keeps every promisor marker, so the repository stays
    promisor-marked while its content becomes complete. `exclude` leaves
    the named objects out (the `gap` arm).
    """
    src = Path(origin) / ".git" / "objects"
    dst = Path(clone) / ".git" / "objects"
    copied = []
    for entry in sorted(src.iterdir()):
        if not (entry.is_dir() and len(entry.name) == 2
                and all(c in HEX for c in entry.name)):
            continue
        for blob in sorted(entry.iterdir()):
            oid = entry.name + blob.name
            if oid in exclude:
                continue
            target = dst / entry.name / blob.name
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(blob, target)
            copied.append(oid)
    # A packed origin would hide its blobs from the loose-object walk above.
    src_pack = src / "pack"
    if src_pack.is_dir():
        (dst / "pack").mkdir(parents=True, exist_ok=True)
        for pack in sorted(src_pack.iterdir()):
            if pack.suffix not in (".pack", ".idx"):
                continue
            target = dst / "pack" / pack.name
            if target.exists():
                continue
            shutil.copyfile(pack, target)
            copied.append("pack/" + pack.name)
    return copied


def closure(repo):
    """Reachable-object closure of every ref in the repository.

    `rev-list --objects --all --missing=print` lists objects git cannot
    find as ?<oid>; a complete repository has none.
    """
    p = run(["-C", str(repo), "rev-list", "--objects", "--all",
             "--missing=print"], check=False)
    lines = p.stdout.decode("utf-8", errors="surrogateescape").splitlines()
    missing = sorted(line[1:] for line in lines if line.startswith("?"))
    reachable = sorted(line.split(" ")[0] for line in lines
                       if line and not line.startswith("?"))
    return {"reachable": len(reachable), "missing": missing}


def object_ids(repo):
    p = run(["-C", str(repo), "cat-file", "--batch-all-objects",
             "--batch-check=%(objectname)"], check=False)
    return set(p.stdout.decode("utf-8", errors="replace").split())


def pack_listing(repo):
    pack = Path(repo) / ".git" / "objects" / "pack"
    if not pack.is_dir():
        return []
    return sorted(p.name for p in pack.iterdir())


def report_bytes(repo):
    """The committed report bytes, read exactly as the auditor reads them."""
    p = run(["-C", str(repo), "show", f"HEAD:{REL}"], check=False)
    if p.returncode != 0:
        return None, p.returncode, p.stderr.decode(errors="replace").strip()
    return p.stdout, 0, ""


def report_cutoff(repo):
    """The fleet cutoff: author time of the commit that first added the
    report. The auditor computes exactly this."""
    out = g(repo, "log", "--diff-filter=A", "--format=%at", "--", REL)
    return int(out.split()[-1]) if out else None


# ------------------------------------------------------------------- arms


def build_arm(root, arm, shape):
    """Build one arm under its own directory and return the fixture proof."""
    root = Path(root).resolve()
    arm_root = root / arm / shape
    arm_root.mkdir(parents=True, exist_ok=True)

    lane, a, b = build_lane(arm_root)
    cited = [a, b] if shape == "clean" else [a]
    origin, body = build_fleet_origin(arm_root, cited,
                                      extra_file=(arm == "gap"))
    fleet = clone_fleet(origin, arm_root / "fleet", blobless=arm != "full")

    report_oid = g(origin, "rev-parse", f"HEAD:{REL}")
    extra_oid = g(origin, "rev-parse", f"HEAD:{EXTRA}") if arm == "gap" else None

    before = closure(fleet)
    copied = []
    if arm in ("hydrated", "gap"):
        exclude = (extra_oid,) if arm == "gap" else ()
        copied = hydrate_offline(origin, fleet, exclude=exclude)
    after = closure(fleet)

    # The fleet origin is removed before any audit: a lazy fetch would then
    # fail loudly instead of silently succeeding over file://.
    shutil.rmtree(origin)
    origin_removed = True

    bytes_before, rc_before, err_before = report_bytes(fleet)
    fixture = {
        "arm": arm,
        "shape": shape,
        "root": str(arm_root),
        "lane": str(lane),
        "fleet": str(fleet),
        "fleet_origin_removed": origin_removed,
        "lane_commits": {"a": a, "b": b},
        "cited": cited,
        "report_body": body,
        "report_oid": report_oid,
        "extra_oid": extra_oid,
        "copied_objects": copied,
        "promisor_metadata": promisor_metadata(fleet),
        "programs": program_surface(fleet),
        "closure_before": before,
        "closure_after": after,
        "report_readable": bytes_before is not None,
        "report_read_rc": rc_before,
        "report_read_stderr": err_before,
        "report_bytes": (bytes_before.decode("utf-8", "replace")
                         if bytes_before is not None else None),
        "report_sha256": (hashlib.sha256(bytes_before).hexdigest()
                          if bytes_before is not None else None),
        "cutoff": report_cutoff(fleet),
        "packs": pack_listing(fleet),
        "objects": len(object_ids(fleet)),
    }
    return fixture


def escape_check(root, fixture):
    """No fixture path may live outside the scratch root."""
    root = Path(root).resolve()
    inside = all(str(Path(fixture[k]).resolve()).startswith(str(root) + os.sep)
                 for k in ("lane", "fleet", "root"))
    stray = []
    for dirpath, dirnames, filenames in os.walk(root):
        for name in list(dirnames) + list(filenames):
            p = Path(dirpath) / name
            if not str(p.resolve()).startswith(str(root) + os.sep):
                stray.append(str(p))
    return {"inside_root": inside, "stray_paths": sorted(stray)}


# --------------------------------------------------------------- premises


def check_premises(fixture):
    """Assert the arm actually has the property it claims."""
    arm = fixture["arm"]
    fleet = Path(fixture["fleet"])
    lane = Path(fixture["lane"])
    meta = fixture["promisor_metadata"]
    problems = []
    # The audited lane is always plain and complete: the fleet side is the
    # only variable in this case.
    if promisor_metadata(lane):
        problems.append("the audited lane carries promisor metadata")
    if program_surface(lane)["config"] or program_surface(lane)["executable_hooks"]:
        problems.append("the audited lane configures an executable program")
    if closure(lane)["missing"]:
        problems.append("the audited lane is incomplete")
    if arm == "full":
        if meta:
            problems.append("full clone carries promisor metadata")
        if any(n.endswith(".promisor") for n in fixture["packs"]):
            problems.append("full clone carries a .promisor marker")
    else:
        for key in ("remote.origin.promisor", "remote.origin.partialclonefilter",
                    "extensions.partialclone"):
            if key not in meta:
                problems.append(f"missing promisor metadata {key}")
        if not any(n.endswith(".promisor") for n in fixture["packs"]):
            problems.append("missing .promisor pack marker")
    if arm == "hydrated":
        if fixture["closure_after"]["missing"]:
            problems.append("hydrated clone still has missing objects")
        if not fixture["report_readable"]:
            problems.append("hydrated clone cannot read the report blob")
    if arm == "gap":
        missing = fixture["closure_after"]["missing"]
        if not fixture["extra_oid"]:
            problems.append("gap arm has no extra blob")
        elif fixture["extra_oid"] not in missing:
            problems.append("gap arm did not leave the extra blob missing")
        elif len(missing) != 1:
            problems.append(f"gap arm is missing more than the extra blob: "
                            f"{missing}")
        if not fixture["report_readable"]:
            problems.append("gap clone cannot read the report blob")
    if arm == "unhydrated":
        if fixture["closure_before"]["missing"] == []:
            problems.append("unhydrated clone is unexpectedly complete")
        if fixture["report_readable"]:
            problems.append("unhydrated clone can read the report blob")
    if arm == "gap":
        if not fixture["extra_oid"]:
            problems.append("gap arm has no extra blob")
        elif fixture["extra_oid"] not in fixture["closure_after"]["missing"]:
            problems.append("gap arm did not leave the extra blob missing")
    if fixture["programs"]["config"] or fixture["programs"]["executable_hooks"]:
        problems.append("fixture configures an executable program")
    if fixture["cutoff"] != 2000:
        problems.append(f"unexpected fleet cutoff {fixture['cutoff']}")
    if fixture["lane_commits"]["a"][:7] == fixture["lane_commits"]["b"][:7]:
        problems.append("lane commit prefixes collide")
    return problems


# ------------------------------------------------------------ expectations

# Derived from the constructed history, not from any candidate run:
#   lane commits a(t=1000) and b(t=1500) are both pre-cutoff (cutoff 2000)
#   clean  : the report cites a and b -> no defect
#   omission: the report cites a only -> b is landed-omitted
# The base (r23) refuses every promisor-marked repository on its metadata,
# so every blobless arm is exit 2 there; the candidate must calibrate.
EXPECTED_BASE = {
    ("full", "clean"): {"exit": 0, "kinds": []},
    ("full", "omission"): {"exit": 1, "kinds": ["landed-omitted"]},
    ("hydrated", "clean"): {"exit": 2, "kinds": None},
    ("hydrated", "omission"): {"exit": 2, "kinds": None},
    ("unhydrated", "clean"): {"exit": 2, "kinds": None},
    ("unhydrated", "omission"): {"exit": 2, "kinds": None},
    ("gap", "clean"): {"exit": 2, "kinds": None},
    ("gap", "omission"): {"exit": 2, "kinds": None},
}

EXPECTED_CANDIDATE = {
    ("full", "clean"): {"exit": 0, "kinds": []},
    ("full", "omission"): {"exit": 1, "kinds": ["landed-omitted"]},
    ("hydrated", "clean"): {"exit": 0, "kinds": []},
    ("hydrated", "omission"): {"exit": 1, "kinds": ["landed-omitted"]},
    ("unhydrated", "clean"): {"exit": 2, "kinds": None},
    ("unhydrated", "omission"): {"exit": 2, "kinds": None},
    ("gap", "clean"): {"exit": 0, "kinds": []},
    ("gap", "omission"): {"exit": 1, "kinds": ["landed-omitted"]},
}

# The `gap` arm is ADVISORY: it never fails the run. The preregistration
# says "content completeness AND availability of required evidence determine
# the outcome" and separately "an unavailable REQUIRED commit/tree/blob/
# report object: exit2". The gap arm's missing blob (notes.txt) is not
# required by the audit, so a candidate that requires only the required
# evidence answers exit 0/1 like the full clone, while a candidate that
# demands whole-repository closure answers exit 2. Both readings are
# defensible; the wave must declare which one it implements. This case
# reports the gap arm and its disagreement with `full` and leaves the
# policy to the wave.
ADVISORY_ARMS = ("gap",)

# Arms whose verdict must equal their full-clone pair's verdict.
# `gap` is excluded: it is advisory (see ADVISORY_ARMS).
PAIRS = (("full", "hydrated"),)


def refusal_markers(text):
    """Substrings that mean the auditor REFUSED the repository outright."""
    markers = ("partial clone", "shallow repository", "rewrites history",
               "not sha1", "not a repository top level", "could-not-evaluate")
    return [m for m in markers if m in text]


def run_auditor(auditor, lane, fleet):
    p = subprocess.run([sys.executable, str(auditor),
                        "--lane-repo", str(lane), "--fleet-repo", str(fleet),
                        "--rounds", "1", "--no-errata", "--json"],
                       capture_output=True)
    doc = {}
    kinds = []
    if p.stdout:
        try:
            doc = json.loads(p.stdout.decode("utf-8", errors="replace"))
        except ValueError:
            doc = {}
    for res in doc.get("results", []):
        for d in res.get("defects", []):
            kinds.append(d.get("kind"))
    res = (doc.get("results") or [{}])[0]
    return {
        "exit": p.returncode,
        "kinds": sorted(kinds),
        "stderr": p.stderr.decode("utf-8", errors="replace").strip(),
        "summary": doc.get("summary", {}),
        "cutoff": res.get("cutoff"),
        "required": res.get("required"),
        "report_committed": res.get("report_committed"),
    }


def remote_is_dead(fleet):
    """Prove the promisor remote can no longer be contacted.

    The fleet origin is deleted before the audit, so `ls-remote` against the
    configured origin must fail. A lazy fetch during the audit could then
    not have succeeded: it would have raised, not silently repaired the
    repository.
    """
    url = config_map(fleet).get("remote.origin.url")
    if not url:
        return {"url": None, "reachable": None, "stderr": "no origin url"}
    p = run(["-C", str(fleet), "ls-remote", "origin"], check=False)
    return {
        "url": url,
        "reachable": p.returncode == 0,
        "rc": p.returncode,
        "stderr": p.stderr.decode(errors="replace").strip()[:200],
    }


def fetch_attempts(fleet, before_packs, before_objects):
    """Direct evidence that the audit did not fetch anything.

    Two independent observations after the audit:
      * the pack set is unchanged: a fetch would add a .pack/.idx pair;
      * the object count is unchanged: a fetch would add objects.
    The fleet origin has been deleted, so a lazy fetch would also have
    failed outright rather than succeeding quietly.
    """
    after_packs = pack_listing(fleet)
    after_objects = len(object_ids(fleet))
    return {
        "packs_before": sorted(before_packs),
        "packs_after": sorted(after_packs),
        "packs_changed": sorted(before_packs) != sorted(after_packs),
        "objects_before": before_objects,
        "objects_after": after_objects,
        "objects_changed": before_objects != after_objects,
        "remote": remote_is_dead(fleet),
        "fetched": (sorted(before_packs) != sorted(after_packs)
                    or before_objects != after_objects),
    }


def byte_and_cutoff_comparison(rows):
    """Compare the report bytes and the cutoff across the arms of a shape.

    The target of the case: a hydrated promisor-marked fleet must yield the
    SAME report bytes and the SAME cutoff as the full clone, with no lazy
    fetch. The unhydrated arm must yield no readable bytes at all.
    """
    out = []
    by_shape = {}
    for row in rows:
        by_shape.setdefault(row["shape"], {})[row["arm"]] = row["fixture"]
    for shape, arms in sorted(by_shape.items()):
        full = arms.get("full")
        if not full:
            continue
        for arm in sorted(arms):
            fx = arms[arm]
            same_bytes = (fx["report_sha256"] == full["report_sha256"]
                          and fx["report_sha256"] is not None)
            same_exact = fx["report_bytes"] == full["report_bytes"]
            same_cutoff = fx["cutoff"] == full["cutoff"]
            out.append({
                "shape": shape,
                "arm": arm,
                "report_sha256": fx["report_sha256"],
                "full_report_sha256": full["report_sha256"],
                "same_report_bytes": same_bytes,
                "same_report_bytes_exact": same_exact,
                "cutoff": fx["cutoff"],
                "full_cutoff": full["cutoff"],
                "same_cutoff": same_cutoff,
                "readable": fx["report_readable"],
            })
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True,
                    help="scratch root; every fixture path stays under it")
    ap.add_argument("--tool", required=True,
                    help="report-landing-audit.py to exercise")
    ap.add_argument("--expect", choices=("base", "candidate"), default="base")
    ap.add_argument("--out", help="write the evidence JSON here")
    ap.add_argument("--arm", action="append", choices=ARMS)
    ap.add_argument("--shape", action="append", choices=SHAPES)
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    arms = args.arm or list(ARMS)
    shapes = args.shape or list(SHAPES)
    table = EXPECTED_BASE if args.expect == "base" else EXPECTED_CANDIDATE

    rows = []
    failures = []
    escapes = []
    for shape in shapes:
        for arm in arms:
            fixture = build_arm(root, arm, shape)
            problems = check_premises(fixture)
            escape = escape_check(root, fixture)
            fixture["escape"] = escape
            if not escape["inside_root"] or escape["stray_paths"]:
                problems.append("fixture escaped the scratch root")
                escapes.append({"arm": arm, "shape": shape, **escape})
            got = run_auditor(args.tool, fixture["lane"], fixture["fleet"])
            fetch = fetch_attempts(fixture["fleet"], fixture["packs"],
                                   fixture["objects"])
            fixture["fetch"] = fetch
            if fetch["fetched"]:
                problems.append("the audit fetched objects into the clone")
            want = table[(arm, shape)]
            advisory = arm in ADVISORY_ARMS
            # The hydrated arm must not merely reach the right exit code: it
            # must not be REFUSED at all. A refusal that happens to carry the
            # right exit code is the r23 harm in another guise.
            refusal = refusal_markers(got["stderr"])
            if arm == "hydrated" and refusal:
                problems.append(f"hydrated arm was refused: {refusal}")
            if arm == "unhydrated" and not refusal:
                problems.append("unhydrated arm exited 2 without a refusal")
            ok = (not problems and got["exit"] == want["exit"]
                  and (want["kinds"] is None or got["kinds"] == want["kinds"]))
            if advisory:
                ok = not problems  # the verdict itself is not a kill row
            if not ok:
                failures.append({"arm": arm, "shape": shape,
                                 "want": want, "got": got,
                                 "advisory": advisory,
                                 "refusal_markers": refusal,
                                 "premises": problems})
            rows.append({"arm": arm, "shape": shape, "want": want,
                         "got": got, "premises": problems, "ok": ok,
                         "fixture": fixture})

    # Pair equality: a hydrated fleet must be indistinguishable from its
    # full-clone pair in the substantive verdict.
    pair_failures = []
    by_key = {(r["arm"], r["shape"]): r for r in rows}
    for full_arm, other in PAIRS:
        for shape in shapes:
            left = by_key.get((full_arm, shape))
            right = by_key.get((other, shape))
            if not left or not right:
                continue
            same = (left["got"]["exit"] == right["got"]["exit"]
                    and left["got"]["kinds"] == right["got"]["kinds"]
                    and left["got"]["cutoff"] == right["got"]["cutoff"])
            if not same:
                pair_failures.append({"pair": [full_arm, other],
                                      "shape": shape,
                                      "full": left["got"],
                                      "other": right["got"]})

    comparison = byte_and_cutoff_comparison(rows)
    byte_failures = [c for c in comparison
                     if c["arm"] == "hydrated"
                     and not (c["same_report_bytes_exact"] and c["same_cutoff"])]

    evidence = {
        "tool": str(Path(args.tool).resolve()),
        "tool_sha256": hashlib.sha256(
            Path(args.tool).read_bytes()).hexdigest(),
        "expect": args.expect,
        "root": str(root),
        "rows": rows,
        "comparison": comparison,
        "byte_failures": byte_failures,
        "escapes": escapes,
        "pair_failures": pair_failures,
        "failures": failures,
    }
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(evidence, indent=1,
                                             sort_keys=True),
                                  encoding="utf-8")
    for r in rows:
        mark = "ok" if r["ok"] else "FAIL"
        print(f"{mark} {r['arm']}/{r['shape']} exit={r['got']['exit']} "
              f"kinds={r['got']['kinds']} cutoff={r['got']['cutoff']} "
              f"want={r['want']} premises={r['premises']}")
        if r["got"]["stderr"]:
            print(f"    stderr: {r['got']['stderr'][:200]}")
    for f in pair_failures:
        print(f"FAIL pair {f['pair'][0]} vs {f['pair'][1]} shape={f['shape']}")
    for c in byte_failures:
        print(f"FAIL bytes/cutoff {c['arm']}/{c['shape']} "
              f"same_bytes={c['same_report_bytes']} "
              f"same_cutoff={c['same_cutoff']}")
    for e in escapes:
        print(f"FAIL escape {e['arm']}/{e['shape']} stray={e['stray_paths']}")
    bad = len(failures) + len(pair_failures) + len(byte_failures) + len(escapes)
    print(f"arms={len(rows)} failures={bad} expect={args.expect}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
