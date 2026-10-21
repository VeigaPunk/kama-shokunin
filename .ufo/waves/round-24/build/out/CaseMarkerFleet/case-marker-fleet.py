#!/usr/bin/env python3
"""CaseMarkerFleet — paired marker-only complete fleet oracle case (round 24).

Two fleet arms over one lane repository:

  plain   ordinary complete fleet clone, no promisor metadata
  marker  byte-identical object store + promisor marker metadata only
          (extensions.partialclone=origin, remote.origin.promisor=true,
           remote.origin.partialclonefilter=blob:none), every object present

The oracle expectation (written before this builder existed) is
out/CaseMarkerFleet/oracle-case-marker-fleet.json in the lane repo.

Everything is local and offline: the marker's remote url names a path that
does not exist, protocol.allow=never forbids any transport, and no
repo-configured program is installed. All fixtures live under
/fast/scratch/hyaku/kama-r24/CaseMarkerFleet.
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
import time

ROOT = Path("/fast/scratch/hyaku/kama-r24/CaseMarkerFleet")
REL = ".ufo/reports/round-1/kama.md"
ABSENT_ORIGIN = ROOT / "absent-origin.git"      # never created
TIMEOUT = 30


class Premise(Exception):
    """The fixture did not establish what it claims: cannot evaluate."""


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args],
                       input=None if data is None else data.encode(),
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise Premise(f"git {' '.join(map(str, args))} in {repo}: "
                      f"rc={p.returncode} "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path):
    g(path.parent, "init", "-q", "-b", "master", str(path))
    return path


def commit(repo, author, when, msg, path="f", content=None):
    target = Path(repo) / path
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


def report(cites):
    body = "".join(f"- {c}\n" for c in cites)
    return f"# kama round 1\n\n## Landed changes\n\n{body}".encode()


def publish(fleet, text, when=2000):
    return commit(fleet, "fleet", when, "round-1: report", REL, text)


# ----------------------------------------------------------------- fixtures

def build_variant(work, variant):
    """Lane + plain fleet; the marker twin is a byte copy of the plain fleet."""
    lane = init(work / "lane")
    fleet = init(work / "fleet-plain")
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    if variant == "V2-omission":
        commit(lane, "kama-shokunin", 1500, "round-1: more")
    publish(fleet, report([lc]))
    marker = work / "fleet-marker"
    shutil.copytree(fleet, marker, symlinks=True)
    # promisor marker metadata only: no object is removed, none is missing
    g(marker, "config", "core.repositoryformatversion", "1")
    g(marker, "config", "extensions.partialclone", "origin")
    g(marker, "config", "remote.origin.url", str(ABSENT_ORIGIN))
    g(marker, "config", "remote.origin.promisor", "true")
    g(marker, "config", "remote.origin.partialclonefilter", "blob:none")
    g(marker, "config", "protocol.allow", "never")
    return lane, fleet, marker, lc


def object_count(repo):
    out = subprocess.run(["git", "-C", str(repo), "cat-file",
                          "--batch-all-objects", "--batch-check"],
                         capture_output=True, env=env()).stdout
    return len([line for line in out.split(b"\n") if line.strip()])


def pack_files(repo):
    d = Path(g(repo, "rev-parse", "--git-path", "objects/pack"))
    return sorted(p.name for p in d.iterdir()) if d.is_dir() else []


def missing_objects(repo):
    """Objects reachable from every ref but absent locally (promisor holes)."""
    out = subprocess.run(["git", "-C", str(repo), "rev-list", "--objects",
                          "--all", "--missing=print"],
                         capture_output=True, env=env())
    return sorted(line.split()[0] for line in out.stdout.decode().split("\n")
                  if line.startswith("?"))


def fsck_ok(repo):
    p = subprocess.run(["git", "-C", str(repo), "fsck", "--connectivity-only",
                        "--no-progress"], capture_output=True, env=env())
    return p.returncode, p.stderr.decode(errors="replace").strip()


def premises(lane, plain, marker, lc, variant):
    """Every premise the oracle depends on; a false premise is exit 2."""
    checks = {}

    def check(name, cond, detail=""):
        checks[name] = {"ok": bool(cond), "detail": detail}
        if not cond:
            raise Premise(f"{name}: {detail}")

    # 1. the two fleet arms hold the same objects
    check("same-head", g(plain, "rev-parse", "HEAD")
          == g(marker, "rev-parse", "HEAD"),
          g(marker, "rev-parse", "HEAD"))
    check("same-object-count", object_count(plain) == object_count(marker),
          f"plain={object_count(plain)} marker={object_count(marker)}")
    check("same-commit-graph",
          g(plain, "rev-list", "--all", "--format=%H %T %at %an %s")
          == g(marker, "rev-list", "--all", "--format=%H %T %at %an %s"), "")

    # 2. the marker arm really carries the marker metadata
    listing = g(marker, "config", "--null", "--list")
    keys = {entry.split("\n", 1)[0] for entry in listing.split("\0") if entry}
    check("marker-extensions-partialclone", "extensions.partialclone" in keys,
          str(sorted(keys)))
    check("marker-remote-promisor", "remote.origin.promisor" in keys,
          str(sorted(keys)))
    check("marker-filter", "remote.origin.partialclonefilter" in keys, "")
    plain_keys = {e.split("\n", 1)[0]
                  for e in g(plain, "config", "--null", "--list").split("\0")
                  if e}
    check("plain-has-no-marker",
          not any(k.startswith("extensions.partialclone")
                  or k.startswith("remote.") and k.endswith(".promisor")
                  for k in plain_keys), str(sorted(plain_keys)))

    # 3. the marker arm is COMPLETE: nothing is missing, nothing is promisor
    check("no-missing-objects", missing_objects(marker) == [],
          str(missing_objects(marker)))
    check("no-promisor-pack", not any(n.endswith(".promisor")
                                       for n in pack_files(marker)),
          str(pack_files(marker)))
    rc, err = fsck_ok(marker)
    check("fsck-connectivity-clean", rc == 0, err[:400])
    check("report-present-locally",
          subprocess.run(["git", "-C", str(marker), "cat-file", "-e",
                          f"HEAD:{REL}"], capture_output=True,
                         env=env()).returncode == 0, "")
    check("cited-commit-present-in-lane",
          subprocess.run(["git", "-C", str(lane), "cat-file", "-e", lc],
                         capture_output=True, env=env()).returncode == 0, "")
    check("lane-complete", missing_objects(lane) == [],
          str(missing_objects(lane)))

    # 4. the transport is impossible, not merely unused
    check("absent-origin-absent", not ABSENT_ORIGIN.exists(), str(ABSENT_ORIGIN))
    check("protocol-never",
          g(marker, "config", "--get", "protocol.allow") == "never", "")
    check("lane-has-no-remote",
          g(lane, "config", "--null", "--list").find("remote.") < 0, "")

    # 5. the report cutoff the oracle names
    check("plain-cutoff-2000",
          g(plain, "log", "--diff-filter=A", "--format=%at", "--", REL)
          .split()[-1] == "2000", "")
    check("marker-cutoff-2000",
          g(marker, "log", "--diff-filter=A", "--format=%at", "--", REL)
          .split()[-1] == "2000", "")
    checks["variant"] = variant
    return checks


# -------------------------------------------------------------------- runs

def run_auditor(auditor, lane, fleet, work):
    before = {"objects": object_count(fleet), "packs": pack_files(fleet),
              "fetch_head": (Path(fleet) / ".git/FETCH_HEAD").exists()}
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata",
            "--json"]
    proc = subprocess.run(argv, capture_output=True, env=env(), cwd=str(work),
                          timeout=TIMEOUT)
    out = proc.stdout.decode(errors="replace")
    doc = None
    try:
        doc = json.loads(out)
    except ValueError:
        doc = None
    after = {"objects": object_count(fleet), "packs": pack_files(fleet),
             "fetch_head": (Path(fleet) / ".git/FETCH_HEAD").exists()}
    res = {"exit": proc.returncode,
           "stderr": proc.stderr.decode(errors="replace").strip(),
           "summary": None, "results": None,
           "store_before": before, "store_after": after}
    if doc:
        res["summary"] = doc.get("summary")
        res["results"] = doc.get("results")
    return res


def substantive(run):
    """The verdict-bearing part of a run, free of filesystem paths."""
    if not run.get("results"):
        return None
    r = run["results"][0]
    return {"exit": run["exit"],
            "cutoff": r["cutoff"],
            "required": r["required"],
            "round_commits": r["round_commits"],
            "report_committed": r["report_committed"],
            "defects": sorted((d["kind"], d["token"]) for d in r["defects"]),
            "post_report": sorted(r["post_report"]),
            "status": run["summary"]["status"] if run["summary"] else None}


def boundary_probe(work, auditor):
    """Discriminating boundary: the same marker metadata with one required
    object genuinely absent. There the verdict must not be produced at all
    (exit 2), and no fetch may be attempted while checking."""
    lane = init(work / "lane")
    fleet = init(work / "fleet-plain")
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, report([lc]))
    marker = work / "fleet-marker"
    shutil.copytree(fleet, marker, symlinks=True)
    g(marker, "config", "core.repositoryformatversion", "1")
    g(marker, "config", "extensions.partialclone", "origin")
    g(marker, "config", "remote.origin.url", str(ABSENT_ORIGIN))
    g(marker, "config", "remote.origin.promisor", "true")
    g(marker, "config", "remote.origin.partialclonefilter", "blob:none")
    g(marker, "config", "protocol.allow", "never")
    blob = g(marker, "rev-parse", f"HEAD:{REL}")
    loose = Path(marker) / ".git" / "objects" / blob[:2] / blob[2:]
    if not loose.exists():
        raise Premise(f"report blob is not loose: {loose}")
    loose.unlink()
    absent = subprocess.run(["git", "-C", str(marker), "cat-file", "-e", blob],
                            capture_output=True, env=env()).returncode != 0
    if not absent:
        raise Premise("removing the report blob did not create a hole")
    hole = subprocess.run(["git", "--no-lazy-fetch", "-C", str(marker),
                           "rev-list", "--objects", "--all", "--missing=print"],
                          capture_output=True, env=env())
    fsck = subprocess.run(["git", "--no-lazy-fetch", "-C", str(marker), "fsck",
                           "--connectivity-only", "--no-progress"],
                          capture_output=True, env=env())
    run = run_auditor(auditor, lane, marker, work)
    return {"hole_blob": blob, "hole_observed": absent,
            "rev_list_missing_print_rc": hole.returncode,
            "rev_list_missing_print_stdout": hole.stdout.decode()[:400],
            "rev_list_missing_print_stderr": hole.stderr.decode()[:200],
            "fsck_rc": fsck.returncode,
            "fsck_stderr": fsck.stderr.decode(errors="replace")[:400],
            "run": run,
            "expectation": "exit 2 (could-not-evaluate), never a clean or "
                           "failed verdict, and no fetch attempt"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--auditor", required=True,
                    help="path to the auditor under test")
    ap.add_argument("--oracle", required=True, help="preregistered oracle JSON")
    ap.add_argument("--out", help="write the observation JSON here")
    args = ap.parse_args(argv)
    oracle = json.loads(Path(args.oracle).read_text())
    auditor = Path(args.auditor).resolve()
    doc = {"case": oracle["case"], "auditor": str(auditor),
           "auditor_sha256": hashlib.sha256(auditor.read_bytes()).hexdigest(),
           "oracle_sha256": hashlib.sha256(
               Path(args.oracle).read_bytes()).hexdigest(),
           "git_version": g(".", "--version"), "variants": {}}
    work_root = ROOT / "run" / time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    work_root.mkdir(parents=True, exist_ok=True)
    doc["work_root"] = str(work_root)
    for variant in ("V1-clean", "V2-omission"):
        expect = next(v for v in oracle["variants"] if v["id"] == variant)
        work = work_root / variant
        work.mkdir(parents=True, exist_ok=True)
        lane, plain, marker, lc = build_variant(work, variant)
        prem = premises(lane, plain, marker, lc, variant)
        runs = {}
        for arm, repo in (("plain", plain), ("marker", marker)):
            runs[arm] = run_auditor(auditor, lane, repo, work)
        sub = {arm: substantive(runs[arm]) for arm in runs}
        plain_ok = (sub["plain"] is not None
                    and sub["plain"]["exit"] == expect["expected"]["exit"]
                    and sub["plain"]["cutoff"] == expect["expected"]["cutoff"]
                    and sub["plain"]["required"] == expect["expected"]["required"]
                    and sorted({k for k, _ in sub["plain"]["defects"]})
                    == sorted(expect["expected"]["defect_kinds"]))
        marker_ok = (sub["marker"] == sub["plain"])
        no_transport = all(
            runs[arm]["store_before"]["objects"] == runs[arm]["store_after"]["objects"]
            and runs[arm]["store_before"]["packs"] == runs[arm]["store_after"]["packs"]
            and not runs[arm]["store_after"]["fetch_head"] for arm in runs)
        doc["variants"][variant] = {
            "premises": prem, "runs": runs, "substantive": sub,
            "expectation": expect["expected"],
            "plain_arm_matches_expectation": plain_ok,
            "marker_arm_equals_plain_arm": marker_ok,
            "no_transport_no_new_objects": no_transport,
            "base_marker_refused": (runs["marker"]["exit"] == 2
                                    and "partial clone" in runs["marker"]["stderr"]),
        }
    boundary_work = work_root / "B1-marker-missing-blob"
    boundary_work.mkdir(parents=True, exist_ok=True)
    doc["boundary"] = boundary_probe(boundary_work, auditor)
    text = json.dumps(doc, indent=1, sort_keys=True)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Premise as exc:
        print(f"could-not-evaluate: fixture premise: {exc}", file=sys.stderr)
        sys.exit(2)
