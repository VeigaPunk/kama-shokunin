#!/usr/bin/env python3
"""CaseMissingLaneBlob — offline fixture builder for the r24 C1 axis.

One case, one axis: a lane repository that is **promisor-marked** (metadata
only: `remote.origin.promisor=true`, `remote.origin.partialclonefilter`,
a `.promisor` pack) but whose **committed `corpus/SOURCES.md` blob object is
absent from the local object store**, because the clone was made with
`--filter=blob:none` and was never fetched. The required registry evidence
is unavailable offline.

Expected outcome (r24 contract):
  * exit 2 (could-not-evaluate). Required evidence cannot be read, so the
    audit has no verdict — never exit 0 (clean), never exit 1 (failed).
  * "exemption" is the failure mode this case exists to catch: treating the
    unreadable committed SOURCES blob as the legacy "no registry" case
    makes `load_source_urls` return None, and the report's registered URL
    citation is then either scanned as an unresolved 40-hex token (exit 1,
    false `unresolved-full-hash`) or skipped (exit 0, false clean). Both are
    wrong: evidence that cannot be read is exit 2. Arm `legacy_exemption`
    below reproduces that exemption signature exactly.
  * the refusal reason must be a *content* reason (the committed blob for
    `corpus/SOURCES.md` cannot be read), not the metadata-only refusal
    ("partial clone ...") and never a transport/fetch error.

Arms (all from one origin lane + one fleet report):
  control_full_clone        complete local objects        -> exit 0, 0 defects
  treatment_promisor        promisor-marked, blob absent   -> exit 2
  probe_metadata_stripped   same repo, promisor metadata
                            removed, blob still absent     -> exit 2 (content
                            reason: this is the path the r24 repair must take)
  legacy_exemption          lane that never committed
                            corpus/SOURCES.md              -> exit 1
                            (unresolved-full-hash) — the exemption signature
  no_remote_variant         promisor-marked, remote URL
                            rewritten to a nonexistent local path -> exit 2 with
                            identical stderr (the remote is never contacted)

No network transport and no execution payload is used: the promisor remote
is a local `file://` path, and the no-fetch proof is exact — the set of
object ids in the clone's local object store is compared before and after
every audit run, and the missing SOURCES blob must never appear in it.

Usage:
    case_missing_lane_blob.py --workspace DIR --auditor PATH [--json]

`build(tmp)` returns the same tuple shape as the round-23 grid builders in
tests/report-audit/repo-state-grid.py, so that tests/report-audit/
promisor-grid.py can adopt it verbatim.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

REL = ".ufo/reports/round-1/kama.md"
SOURCES = "corpus/SOURCES.md"
FAKE_HEX = "1234567890abcdef1234567890abcdef12345678"
SOURCE_URL = f"https://example.invalid/fixture/blob/{FAKE_HEX}"
TIMEOUT = 60

SOURCES_MD = """# SOURCES — fixture registry

## Registry

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S001 | Fixture source — {url} | docs | A | fixture scope | fixture anchor | fixture teaches | mined | 2026-10-21 | on-release | - |
""".format(url=SOURCE_URL)


class Premise(Exception):
    """The fixture did not establish its state: cannot evaluate."""


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise Premise(f"git {' '.join(map(str, args))}: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path):
    g(path.parent, "init", "-q", "-b", "master", str(path))
    return path


def commit(repo, author, when, msg, path="f", content=None):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(target, "ab") as fh:
            fh.write((msg + "\n").encode())
    else:
        target.write_bytes(content)
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def report(lane_commit):
    return ("# kama round 1\n\n## Landed changes\n\n"
            f"- {lane_commit}\n\n## Notes\n\n"
            f"Fixture registry source: {SOURCE_URL}\n").encode()


# ------------------------------------------------------------------ fixture

def build_origin(tmp, with_registry=True):
    """Lane with one cited round-1 commit and (optionally) the committed
    registry blob; fleet holds the round-1 report citing the commit and the
    registry URL."""
    tmp = Path(tmp)
    lane, fleet = init(tmp / "lane"), init(tmp / "fleet")
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    if with_registry:
        commit(lane, "fixture", 1100, "registry", SOURCES, SOURCES_MD.encode())
    commit(fleet, "fleet", 2000, "round-1: report", REL, report(lc))
    return lane, fleet, lc


def build_promisor_clone(lane, dest, remote_url=None):
    """A blobless (blob:none) clone of the lane: promisor-marked, with every
    blob — including the committed corpus/SOURCES.md blob — absent locally."""
    dest = Path(dest)
    g(lane, "config", "uploadpack.allowFilter", "true")
    p = subprocess.run(["git", "-c", "protocol.file.allow=always", "clone",
                        "-q", "--no-checkout", "--filter=blob:none",
                        "--no-local", f"file://{lane}", str(dest)],
                       capture_output=True, env=env())
    if p.returncode:
        raise Premise("promisor clone failed: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    if remote_url is not None:
        g(dest, "config", "remote.origin.url", remote_url)
    return dest


def strip_promisor_metadata(repo):
    """Model the r24 repair's view of the same repository: promisor metadata
    is accepted, so it is removed, and the missing blob stays missing."""
    g(repo, "config", "--unset", "remote.origin.promisor")
    g(repo, "config", "--unset", "remote.origin.partialclonefilter")
    pack = Path(repo, ".git/objects/pack")
    if pack.is_dir():
        for marker in pack.glob("*.promisor"):
            marker.unlink()
    return repo


def sources_blob_oid(repo, tip):
    """The oid the committed tree names for corpus/SOURCES.md."""
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo),
                        "ls-tree", tip, "--", SOURCES],
                       capture_output=True, env=env())
    if p.returncode:
        raise Premise(f"{repo}: ls-tree {SOURCES}: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    entry = p.stdout.decode(errors="surrogateescape").strip()
    if not entry:
        raise Premise(f"{repo}: {SOURCES} not in the committed tree")
    meta, _, path = entry.partition("\t")
    fields = meta.split()
    if len(fields) != 3 or fields[1] != "blob" or path != SOURCES:
        raise Premise(f"{repo}: {SOURCES} is not a regular blob: {entry!r}")
    return fields[2]


def local_objects(repo):
    """Every object id in the local object store, without contacting any
    remote (`--batch-all-objects` never fetches; `--no-lazy-fetch` keeps
    git from trying)."""
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo),
                        "cat-file", "--batch-check", "--batch-all-objects",
                        "--unordered"], capture_output=True, env=env())
    if p.returncode:
        raise Premise(f"{repo}: cannot list local objects: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    oids = set()
    for line in p.stdout.decode(errors="replace").splitlines():
        oid = line.split(" ", 1)[0].strip()
        if oid:
            oids.add(oid)
    return oids


def blob_readable(repo, oid):
    """Can the blob be read offline? (`--no-lazy-fetch`: a missing promised
    object is an error, never a fetch.)"""
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo),
                        "cat-file", "-e", oid], capture_output=True, env=env())
    return p.returncode == 0


def promisor_metadata(repo):
    cfg = g(repo, "config", "--list")
    out = {"extensions.partialclone": None, "remote.origin.promisor": None,
           "remote.origin.partialclonefilter": None, "promisor_packs": []}
    for line in cfg.split("\n"):
        key, _, value = line.partition("=")
        if key in out and out[key] is None:
            out[key] = value
    pack = Path(repo, ".git/objects/pack")
    if pack.is_dir():
        out["promisor_packs"] = sorted(p.name for p in pack.glob("*.promisor"))
    return out


def require(cond, what):
    if not cond:
        raise Premise(what)


# ------------------------------------------------------------------- runner

def run_auditor(auditor, lane, fleet, extra=()):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--branch", "master", "--lane",
            "kama", "--rounds", "1-1", "--no-errata", "--json", *extra]
    before = local_objects(lane)
    started = time.monotonic()
    p = subprocess.run(argv, capture_output=True, env=env(), timeout=TIMEOUT)
    after = local_objects(lane)
    return {
        "argv": argv, "rc": p.returncode,
        "stdout": p.stdout.decode(errors="replace"),
        "stderr": p.stderr.decode(errors="replace"),
        "seconds": round(time.monotonic() - started, 3),
        "objects_before": len(before),
        "objects_after": len(after),
        "objects_added_by_audit": sorted(after - before),
    }


def build(tmp):
    """Grid-builder entry point: returns (lane, fleet, argv_extra, marker)."""
    tmp = Path(tmp)
    lane, fleet, _ = build_origin(tmp)
    promisor = build_promisor_clone(lane, tmp / "promisor-lane")
    tip = g(promisor, "rev-parse", "refs/heads/master")
    oid = sources_blob_oid(promisor, tip)
    require(oid not in local_objects(promisor),
            "the committed SOURCES blob is present in the promisor clone")
    require(promisor_metadata(promisor)["remote.origin.promisor"] == "true",
            "promisor metadata not established")
    return promisor, fleet, [], None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--auditor", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    ws = Path(args.workspace)
    if ws.exists():
        shutil.rmtree(ws)
    ws.mkdir(parents=True)

    lane, fleet, lc = build_origin(ws)
    tip = g(lane, "rev-parse", "refs/heads/master")
    oid = sources_blob_oid(lane, tip)
    require(oid in local_objects(lane), "origin lane lacks the SOURCES blob")

    promisor = build_promisor_clone(lane, ws / "promisor-lane")
    p_tip = g(promisor, "rev-parse", "refs/heads/master")
    p_oid = sources_blob_oid(promisor, p_tip)
    require(p_oid == oid, f"clone names a different blob oid: {p_oid} != {oid}")
    require(p_oid not in local_objects(promisor),
            "the committed SOURCES blob is present in the promisor clone")
    require(not blob_readable(promisor, p_oid),
            "the committed SOURCES blob is readable in the promisor clone")
    meta = promisor_metadata(promisor)
    require(meta["remote.origin.promisor"] == "true",
            "promisor metadata not established")
    require(bool(meta["promisor_packs"]), "no .promisor pack observed")

    # arm 1: complete local objects (control)
    control = run_auditor(args.auditor, lane, fleet)
    # arm 2: promisor-marked lane, committed SOURCES blob absent offline
    treatment = run_auditor(args.auditor, promisor, fleet)
    # arm 3: same repository with the promisor metadata removed and the blob
    # still missing — the path the r24 repair must take (content, not
    # metadata, decides).
    stripped = ws / "promisor-lane-stripped"
    shutil.copytree(promisor, stripped, symlinks=True)
    strip_promisor_metadata(stripped)
    require(p_oid not in local_objects(stripped),
            "the SOURCES blob is present in the metadata-stripped copy")
    probe = run_auditor(args.auditor, stripped, fleet)
    # arm 4: the exemption signature — a lane that never committed a
    # registry; the report's registered URL is then scanned as a token.
    legacy_dir = ws / "legacy"
    legacy_dir.mkdir()
    legacy, legacy_fleet, _ = build_origin(legacy_dir, with_registry=False)
    legacy_oid = g(legacy, "rev-parse", "refs/heads/master")
    legacy = run_auditor(args.auditor, legacy, legacy_fleet)
    # arm 5: promisor-marked, remote rewritten to a nonexistent local path;
    # identical stderr proves the remote was never contacted.
    noremote = build_promisor_clone(lane, ws / "promisor-lane-noremote",
                                    remote_url=str(ws / "nonexistent.git"))
    n_oid = sources_blob_oid(noremote, g(noremote, "rev-parse",
                                          "refs/heads/master"))
    require(n_oid not in local_objects(noremote),
            "SOURCES blob present in the no-remote clone")
    nofetch = run_auditor(args.auditor, noremote, fleet)

    def norm(text, repo):
        return text.replace(str(repo), "<repo>")

    out = {
        "case": "missing-lane-sources-blob",
        "git_version": subprocess.run(["git", "--version"],
                                      capture_output=True).stdout.decode().strip(),
        "origin": {"lane": str(lane), "fleet": str(fleet),
                   "lane_commit": lc, "sources_blob_oid": oid, "tip": tip},
        "promisor": {"lane": str(promisor), "tip": p_tip,
                     "sources_blob_oid": p_oid, "metadata": meta,
                     "blob_in_local_store": p_oid in local_objects(promisor),
                     "blob_readable_offline": blob_readable(promisor, p_oid)},
        "control_full_clone": control,
        "treatment_promisor": treatment,
        "probe_metadata_stripped": probe,
        "legacy_exemption": legacy,
        "treatment_no_remote": nofetch,
        "stderr_identical_without_remote":
            norm(treatment["stderr"], promisor)
            == norm(nofetch["stderr"], noremote),
        "no_object_added_by_any_audit": all(
            arm["objects_added_by_audit"] == []
            for arm in (control, treatment, probe, legacy, nofetch)),
    }
    if args.json:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        for key in ("control_full_clone", "treatment_promisor",
                    "probe_metadata_stripped", "legacy_exemption",
                    "treatment_no_remote"):
            arm = out[key]
            print(f"{key}: rc={arm['rc']} "
                  f"stderr={arm['stderr'].strip()[:160]}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Premise as exc:
        print(f"premise failed: {exc}", file=sys.stderr)
        sys.exit(2)
