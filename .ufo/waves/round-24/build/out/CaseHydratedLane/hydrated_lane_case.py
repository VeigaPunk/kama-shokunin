#!/usr/bin/env python3
"""Round-24 oracle case: a genuine file:// blob:none clone, hydrated
locally offline, must give the same substantive verdicts as a full clone.

CANDIDATE fixture builder for tests/report-audit/promisor-grid.py (round
24). Not production code; it changes nothing in the lane repository. The
grader's grid may adopt, amend or reject it.

Arms (one commit history, cloned and hydrated three ways):

  full        plain full clone of the origin on both sides (reference)
  hydrated    lane side is a real `--filter=blob:none` file:// clone whose
              promisor metadata is RETAINED and whose missing objects are
              supplied by an OFFLINE copy of the origin object store
              (no transport, no network, no program)
  unhydrated  the same blob:none clone, left incomplete
  partial     the same blob:none clone with only ONE of the two missing
              blobs supplied (a half-hydrated repository)
  fleet-hydrated    lane full, fleet side blob:none and hydrated
  fleet-unhydrated  lane full, fleet side blob:none, report blob missing

Expected verdicts (derived from the constructed history, not from a
candidate run):

  full/clean               exit 0, no defect
  full/omission            exit 1, defect landed-omitted
  hydrated/clean           exit 0, no defect        == full/clean
  hydrated/omission        exit 1, landed-omitted  == full/omission
  unhydrated/clean         exit 2 (never 0, never 1)
  unhydrated/omission      exit 2 (never 0, never 1)
  partial/clean            exit 2 (never 0, never 1)
  partial/omission         exit 2 (never 0, never 1)
  fleet-hydrated/clean     exit 0, no defect        == full/clean
  fleet-hydrated/omission  exit 1, landed-omitted  == full/omission
  fleet-unhydrated/clean   exit 2 (never 0, never 1)
  fleet-unhydrated/omission exit 2 (never 0, never 1)

The hydrated arms are the repair target: promisor metadata alone must not
refuse a repository whose content is complete. The unhydrated and partial
arms are the controls that separate a content-based rule from a
metadata-based one: a repair that merely deletes the metadata refusal would
return a clean verdict on incomplete evidence.

Fixture discipline:
  * every path is created under the caller-supplied scratch root and is
    asserted to stay there (no fixture escapes the scratch);
  * only local file:// transport is used, and only for the initial clone;
    hydration is a plain file copy of the origin object store;
  * no repository program is configured or invoked (no ssh command, no gpg,
    no hook, no filter helper): `program_surface` asserts this.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REL = ".ufo/reports/round-1/kama.md"
AUTHOR = "kama-shokunin"
EMAIL = "kama@shokunin.local"
HEX = set("0123456789abcdef")
ARMS = ("full", "marked", "hydrated", "unhydrated", "partial",
        "fleet-hydrated", "fleet-unhydrated", "fleet-marked")
SHAPES = ("clean", "omission")
# config keys that would make git run a program
PROGRAM_KEYS = ("core.sshcommand", "core.gitproxy", "diff.external",
                "diff.*.external", "filter.*.process", "filter.*.clean",
                "filter.*.smudge", "uploadpack.packobjectshook",
                "core.hookspath")


class Premise(Exception):
    """The fixture did not establish its property: cannot evaluate."""


# --------------------------------------------------------------------- git


def env(**extra):
    """No inherited GIT_* variables and no user/system config.

    GIT_ALLOW_PROTOCOL=file restricts every git call of the fixture to the
    local file protocol: an ssh/http/https fetch would fail loudly instead
    of reaching the network. The fixture therefore cannot use a network
    transport even by accident.
    """
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_ALLOW_PROTOCOL="file", **extra)
    return e


def run(args, data=None, check=True, cwd=None, **extra):
    """git with --no-lazy-fetch so a promisor remote can never be contacted."""
    p = subprocess.run(["git", "--no-lazy-fetch", *args], input=data,
                       capture_output=True, env=env(**extra), cwd=cwd)
    if check and p.returncode != 0:
        raise Premise(f"git {' '.join(args[:4])}: rc={p.returncode} "
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


def build_lane_origin(root, allow_filter=True):
    """Lane origin: two round-1 commits by kama-shokunin, fixed dates."""
    origin = Path(root) / "lane-origin"
    origin.mkdir(parents=True)
    run(["init", "-q", "-b", "master", str(origin)])
    if allow_filter:
        g(origin, "config", "uploadpack.allowFilter", "true")
    a = commit(origin, "round-1: work", 1000, "f", "work\n")
    b = commit(origin, "round-1: extra", 1500, "g", "extra\n")
    return origin, a, b


def build_fleet_origin(root, cited, allow_filter=True):
    """Fleet origin holding the round-1 kama report, authored at t=2000."""
    origin = Path(root) / "fleet-origin"
    origin.mkdir(parents=True)
    run(["init", "-q", "-b", "master", str(origin)])
    if allow_filter:
        g(origin, "config", "uploadpack.allowFilter", "true")
    body = "# kama round 1\n\n## Landed changes\n\n" + "".join(
        f"- `{sha}`\n" for sha in cited)
    target = Path(origin) / REL
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    g(origin, "add", REL)
    g(origin, "-c", "commit.gpgsign=false", "commit", "-q",
      "-m", "round-1: kama report",
      GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
      GIT_AUTHOR_EMAIL="fleet@shokunin.local",
      GIT_COMMITTER_EMAIL="fleet@shokunin.local",
      GIT_AUTHOR_DATE="@2000 +0000", GIT_COMMITTER_DATE="@2000 +0000")
    return origin, body


def clone_from(origin, dest, blob_none):
    """file:// clone; blob_none selects --filter=blob:none.

    A blobless clone is made with --no-checkout: checking out would ask the
    promisor remote for the tip blobs, which would hydrate the fixture and
    destroy the incompleteness the arm is about. The auditor reads only the
    object store and refs, never a worktree.
    """
    args = ["-c", "protocol.file.allow=always", "clone", "-q", "--no-local"]
    if blob_none:
        args += ["--filter=blob:none", "--no-checkout"]
    args += [f"file://{origin}", str(dest)]
    run(args, cwd=str(dest.parent))
    return Path(dest)


def config_map(repo):
    out = g(repo, "config", "--null", "--list")
    keys = {}
    for entry in filter(None, out.split("\0")):
        key, _, value = entry.partition("\n")
        keys[key] = value
    return keys


def promisor_config(repo):
    """The promisor metadata a genuine partial clone carries."""
    return {k: v for k, v in config_map(repo).items()
            if k == "extensions.partialclone"
            or k.startswith("remote.origin.promisor")
            or k.startswith("remote.origin.partialclonefilter")}


def program_surface(repo):
    """Configured git programs: a fixture that can execute something."""
    found = {}
    for key, value in config_map(repo).items():
        low = key.lower()
        for pattern in PROGRAM_KEYS:
            head = pattern.split("*")[0]
            if low == pattern or (pattern.endswith("*")
                                  and low.startswith(head)):
                found[key] = value
    hooks = Path(repo) / ".git" / "hooks"
    active = []
    if hooks.is_dir():
        active = sorted(p.name for p in hooks.iterdir()
                        if p.is_file() and os.access(p, os.X_OK)
                        and not p.name.endswith(".sample"))
    return {"config": found, "executable_hooks": active}


def hydrate_offline(origin, clone, limit=None):
    """Supply missing objects by copying the origin object store.

    No transport, no program: a plain file copy. The clone keeps every
    promisor marker, so the repository stays promisor-marked while its
    content becomes complete. `limit` copies at most that many objects
    (used by the half-hydrated arm).
    """
    src = Path(origin) / ".git" / "objects"
    dst = Path(clone) / ".git" / "objects"
    copied = []
    for entry in sorted(src.iterdir()):
        if entry.is_dir() and len(entry.name) == 2 \
                and all(c in HEX for c in entry.name):
            for blob in sorted(entry.iterdir()):
                target = dst / entry.name / blob.name
                if target.exists():
                    continue
                if limit is not None and len(copied) >= limit:
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(blob, target)
                copied.append(entry.name + blob.name)
        elif entry.is_dir() and entry.name == "pack":
            (dst / "pack").mkdir(parents=True, exist_ok=True)
            for pack in sorted(entry.iterdir()):
                if pack.suffix in (".pack", ".idx"):
                    target = dst / "pack" / pack.name
                    if not target.exists():
                        shutil.copyfile(pack, target)
                        copied.append(f"pack/{pack.name}")
    return copied


def closure(repo):
    """Reachable-object closure of every ref in the repository.

    `rev-list --objects --all` walks every object reachable from every ref;
    with --missing=print the objects it cannot find are listed as ?<oid>.
    The plain walk must succeed for a complete repository.
    """
    p = run(["-C", str(repo), "rev-list", "--objects", "--all",
             "--missing=print"], check=False)
    lines = p.stdout.decode("utf-8", errors="surrogateescape").splitlines()
    missing = sorted(line[1:] for line in lines if line.startswith("?"))
    reachable = sorted(line.split(" ")[0] for line in lines
                       if line and not line.startswith("?"))
    q = run(["-C", str(repo), "rev-list", "--objects", "--all"], check=False)
    return {
        "reachable": len(reachable),
        "missing": missing,
        "complete_walk_rc": q.returncode,
        "complete_walk_stderr": q.stderr.decode(errors="replace").strip(),
    }


def object_ids(repo):
    p = run(["-C", str(repo), "cat-file", "--batch-all-objects",
             "--batch-check=%(objectname)"], check=False)
    return set(p.stdout.decode("utf-8", errors="replace").split())


def side_fixture(origin, dest, blob_none, hydrate):
    """One audited side: clone, optionally hydrate, and prove its closure."""
    repo = clone_from(origin, dest, blob_none=blob_none)
    info = {
        "path": str(repo),
        "promisor_config": promisor_config(repo),
        "closure_before": closure(repo),
        "copied": [],
    }
    if hydrate == "full":
        info["copied"] = hydrate_offline(origin, repo)
    elif hydrate == "partial":
        info["copied"] = hydrate_offline(origin, repo, limit=1)
    info["closure_after"] = closure(repo)
    have = object_ids(repo)
    want = object_ids(origin)
    info["objects"] = len(have)
    info["origin_objects"] = len(want)
    info["covers_origin"] = want <= have
    info["programs"] = program_surface(repo)
    return info


def build_arm(root, arm, shape):
    """Build one arm; returns the fixture and its proofs."""
    root = Path(root).resolve()
    # "marked" arms ask for a filter from an origin that does not offer one:
    # the client records promisor metadata, the server sends everything.
    # The result is a COMPLETE repository that is marked as a partial clone.
    lane_filter = arm in ("marked", "hydrated", "unhydrated", "partial")
    lane_allows = arm != "marked"
    fleet_filter = arm in ("fleet-hydrated", "fleet-unhydrated",
                           "fleet-marked")
    fleet_allows = arm != "fleet-marked"
    lane_origin, a, b = build_lane_origin(root, allow_filter=lane_allows)
    cited = [a, b] if shape == "clean" else [a]
    fleet_origin, report_body = build_fleet_origin(root, cited,
                                                    allow_filter=fleet_allows)
    lane_hydrate = {"hydrated": "full", "partial": "partial"}.get(arm)
    fleet_hydrate = "full" if arm == "fleet-hydrated" else None
    lane = side_fixture(lane_origin, root / "lane", lane_filter,
                         lane_hydrate)
    fleet = side_fixture(fleet_origin, root / "fleet", fleet_filter,
                         fleet_hydrate)
    fixture = {
        "arm": arm,
        "shape": shape,
        "root": str(root),
        "commit_a": a,
        "commit_b": b,
        "cited": cited,
        "report": report_body,
        "lane": lane,
        "fleet": fleet,
        # escape guard: no fixture path may live outside the arm root
        "paths_inside_root": all(
            str(p).startswith(str(root) + os.sep)
            for p in (Path(lane["path"]), Path(fleet["path"]))),
    }
    return fixture


# ------------------------------------------------------------- expectations

# exit code -> verdict; kinds -> the defect kinds the verdict must contain.
# Derived from the constructed history above, not from any candidate run.
EXPECTED = {
    ("full", "clean"): {"exit": 0, "kinds": []},
    ("full", "omission"): {"exit": 1, "kinds": ["landed-omitted"]},
    ("marked", "clean"): {"exit": 0, "kinds": []},
    ("marked", "omission"): {"exit": 1, "kinds": ["landed-omitted"]},
    ("hydrated", "clean"): {"exit": 0, "kinds": []},
    ("hydrated", "omission"): {"exit": 1, "kinds": ["landed-omitted"]},
    ("unhydrated", "clean"): {"exit": 2, "kinds": None},
    ("unhydrated", "omission"): {"exit": 2, "kinds": None},
    ("partial", "clean"): {"exit": 2, "kinds": None},
    ("partial", "omission"): {"exit": 2, "kinds": None},
    ("fleet-hydrated", "clean"): {"exit": 0, "kinds": []},
    ("fleet-hydrated", "omission"): {"exit": 1, "kinds": ["landed-omitted"]},
    ("fleet-unhydrated", "clean"): {"exit": 2, "kinds": None},
    ("fleet-unhydrated", "omission"): {"exit": 2, "kinds": None},
    ("fleet-marked", "clean"): {"exit": 0, "kinds": []},
    ("fleet-marked", "omission"): {"exit": 1, "kinds": ["landed-omitted"]},
}

# A complete promisor-marked side must be indistinguishable from its
# full-clone pair in the substantive verdict, promisor metadata notwith-
# standing.
PAIRS = (("full", "marked"), ("full", "hydrated"), ("full", "fleet-hydrated"),
         ("full", "fleet-marked"))


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
    return {
        "exit": p.returncode,
        "kinds": sorted(kinds),
        "stderr": p.stderr.decode("utf-8", errors="replace").strip(),
        "summary": doc.get("summary", {}),
    }


def build_cases():
    """Grid-style case table: (name, kind, builder, exit, kinds)."""
    table = []
    for arm in ARMS:
        for shape in SHAPES:
            want = EXPECTED[(arm, shape)]
            table.append((f"P-{arm}-{shape}",
                          "promisor",
                          (lambda a=arm, s=shape: lambda root: build_arm(
                              root, a, s))(),
                          want["exit"], want["kinds"]))
    return table


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scratch", required=True,
                    help="scratch root; every fixture path stays inside it")
    ap.add_argument("--auditor", required=True,
                    help="path to a report-landing-audit.py to exercise")
    ap.add_argument("--out", help="write the evidence JSON here")
    ap.add_argument("--spec", action="store_true",
                    help="print the expectation table and exit")
    args = ap.parse_args(argv)
    if args.spec:
        print(json.dumps({f"{a}/{s}": v for (a, s), v in EXPECTED.items()},
                         indent=1, sort_keys=True))
        return 0
    if not Path(args.auditor).is_file():
        raise SystemExit(f"auditor not found: {args.auditor}")
    scratch = Path(args.scratch).resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    work = scratch / "work"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    rows = []
    for arm in ARMS:
        for shape in SHAPES:
            root = work / f"{arm}-{shape}"
            root.mkdir(parents=True)
            fixture = build_arm(root, arm, shape)
            observed = run_auditor(args.auditor, fixture["lane"]["path"],
                                   fixture["fleet"]["path"])
            want = EXPECTED[(arm, shape)]
            ok = observed["exit"] == want["exit"]
            if want["kinds"] is not None:
                ok = ok and observed["kinds"] == sorted(want["kinds"])
            rows.append({"arm": arm, "shape": shape, "expected": want,
                         "observed": observed,
                         "matches_expectation": ok, "fixture": fixture})
            print(f"{'ok  ' if ok else 'FAIL'} {arm}/{shape} "
                  f"exit={observed['exit']} kinds={observed['kinds']} "
                  f"(want exit={want['exit']} kinds={want['kinds']})")
            if observed["stderr"]:
                print(f"      stderr: {observed['stderr'][:160]}")
    pair_ok = {}
    for arm_a, arm_b in PAIRS:
        for shape in SHAPES:
            left = next(r for r in rows if r["arm"] == arm_a
                        and r["shape"] == shape)["observed"]
            right = next(r for r in rows if r["arm"] == arm_b
                         and r["shape"] == shape)["observed"]
            same = (left["exit"] == right["exit"]
                    and left["kinds"] == right["kinds"])
            pair_ok[f"{arm_a}/{shape}=={arm_b}/{shape}"] = same
            print(f"{'ok  ' if same else 'FAIL'} pair {arm_a}/{shape} "
                  f"vs {arm_b}/{shape}: {left['exit']}/{left['kinds']} vs "
                  f"{right['exit']}/{right['kinds']}")
    doc = {"auditor": str(Path(args.auditor).resolve()),
           "git_version": g(Path(args.scratch), "--version"),
           "scratch": str(scratch),
           "expectations": {f"{a}/{s}": v for (a, s), v in EXPECTED.items()},
           "pair_equality": pair_ok,
           "rows": rows}
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n",
                       encoding="utf-8")
        print(f"evidence: {out}")
    bad = [r for r in rows if not r["matches_expectation"]]
    bad += [k for k, v in pair_ok.items() if not v]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
