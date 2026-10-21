#!/usr/bin/env python3
"""Round-24 oracle case CA-1: a required lane ancestor commit that is not
available in a promisor-backed lane repository.

One fixture, three arms, one variable (is the required ancestor L1
available in the lane's local object store?):

  origin     a bare repository on the same filesystem holding the round-1
             lane history L0 (cited) - L1 (omitted by the report) - L2
             (cited) - L3 (post-report).  It is the only "remote" in the
             fixture: git's local path transport, no network.

  CA-1a  control  a real blobless partial clone of the origin
                  (remote.origin.promisor=true, .promisor pack); every
                  commit is available locally
  CA-1b  fault    the same partial clone with its pack rebuilt without L1:
                  the required ancestor is unavailable, the origin still
                  holds it, so a lazy fetch would restore it and be visible
  CA-1c  control  a full clone of the same origin, no promisor metadata

  The fleet report cites L0 and L2 and omits L1, so in the control arms the
  omission is genuine and must be reported, and in the fault arm the
  auditor cannot know whether L1 landed.

Preregistered expectations (from the round-24 preregistration and the base
tool's semantics, before any candidate exists):

  CA-1a  exit 1  defects ["landed-omitted"] token=<L1 sha>
                required=3  post_report=1        (must not be exit 2)
  CA-1b  exit 2  no verdict on stdout; stderr starts with
                "could-not-evaluate:"; L1 is still absent afterwards and
                the lane object store is unchanged (no lazy fetch)
  CA-1c  exit 1  findings identical to CA-1a (kinds, tokens, counts)

  CA-1a and CA-1c must agree exactly; CA-1b must be a could-not-evaluate
  and must not contain "landed-omitted", "landed-unresolved",
  "unresolved-full-hash" or a clean summary.

Why each arm exists:

  * CA-1a is the round-23 harm.  The round-23 base refuses a promisor
    repository on its metadata alone ("partial clone (promisor pack)"),
    so a complete repository with a genuine omission is never audited.
    Preregistration: a complete local promisor-marked clone must reach the
    same substantive findings as an otherwise identical full clone, and a
    genuine omitted pre-cutoff lane commit must remain landed-omitted
    exit 1 with promisor metadata.
  * CA-1b is the required outcome for an unavailable required object:
    exit 2 could-not-evaluate, never a verdict.  An auditor that enumerates
    the lane history with a tolerant reader (`rev-list --missing=print`, or
    one that ignores a traversal error) sees only L3 and L2 -- git stops at
    the missing ancestor -- and concludes "clean": a truncated-history
    verdict.  An auditor that lazily fetches the missing ancestor concludes
    "landed-omitted": a verdict built on evidence it may not obtain.
  * CA-1c is the reference full clone for CA-1a.

Everything is local and offline: no network transport, no repo-configured
program, no executed script, no payload.  The auditor runs as a subprocess
with its own environment (no inherited GIT_* variables, no user or system
config).

Usage:
  python3 case-missing-ancestor.py --json
  python3 case-missing-ancestor.py --auditor PATH --keep

Exit: 0 every arm met its expectation; 1 at least one did not; 2 the
fixture premise failed or the auditor was unusable.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

LANE_DIR = Path("/fast/scratch/hyaku/kama-r24/CaseMissingAncestor")
REL = ".ufo/reports/round-1/kama.md"
DEFAULT_AUDITOR = LANE_DIR / "tools/report-landing-audit.py"
DEFAULT_WORK = LANE_DIR / "work"
TIMEOUT = 60


class Premise(Exception):
    """The fixture did not establish its premise: cannot evaluate."""


def env(**extra):
    """No inherited GIT_* variables and no user/system config."""
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, check=True, data=None, **extra):
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


def report(cites):
    lines = b"".join(b"- " + c.encode() + b"\n" for c in cites)
    return b"# kama round 1\n\n## Landed changes\n\n" + lines


def publish(fleet, text, when=2000, path=REL):
    commit(fleet, "fleet", when, "round-1: report", path, text)


def present(repo, sha):
    """Is the object available locally?  --no-lazy-fetch: this check must
    never fetch the object it is looking for."""
    return subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo),
                           "cat-file", "-e", sha],
                          capture_output=True, env=env()).returncode == 0


def object_store(repo):
    """The set of loose and packed object files, for the no-fetch check."""
    base = Path(repo, ".git/objects")
    out = set()
    for d in base.iterdir():
        if d.is_dir():
            out.update(f"loose/{p.name}" for p in d.iterdir())
        elif d.name != "info":
            out.add(d.name)
    return out


def promisor_packs(repo):
    return sorted(p.name for p in Path(repo, ".git/objects/pack").iterdir()
                  if p.suffix == ".promisor")


def build_origin(tmp):
    """The lane history and the fleet report.  L1 is the required ancestor
    the report omits; L3 is post-report."""
    src = init(Path(tmp, "src"))
    l0 = commit(src, "kama-shokunin", 900, "round-1: base")
    l1 = commit(src, "kama-shokunin", 1000, "round-1: work")
    l2 = commit(src, "kama-shokunin", 1100, "round-1: measure")
    l3 = commit(src, "kama-shokunin", 2100, "round-1: late")
    origin = Path(tmp, "origin.git")
    g(tmp, "clone", "-q", "--bare", "--no-hardlinks", str(src), str(origin))
    g(origin, "config", "uploadpack.allowFilter", "true")
    fleet = init(Path(tmp, "fleet"))
    publish(fleet, report([l0, l2]))
    return origin, fleet, {"L0": l0, "L1": l1, "L2": l2, "L3": l3}


def clone(tmp, origin, name, partial):
    """Clone the origin.  partial=True gives a real blobless partial clone
    (promisor config plus a .promisor pack)."""
    lane = Path(tmp, name)
    argv = ["clone", "-q", "--no-checkout", "--no-local"]
    if partial:
        argv += ["--filter=blob:none"]
    argv += [f"file://{origin}", str(lane)]
    g(tmp, "-c", "protocol.file.allow=always", *argv)
    return lane


def drop_object_from_pack(lane, keep, drop):
    """Rebuild the lane's pack without `drop`, keeping every other object
    (`keep` are the commits that stay; their trees and blobs are listed
    explicitly, because a rev-list exclusion would also drop the ancestors
    of `drop`).  The lane keeps its .promisor marker, so it stays a
    promisor-backed repository whose ancestor is unavailable.
    """
    objs = []
    for sha in keep:
        objs.append(sha)
        objs.append(g(lane, "rev-parse", f"{sha}^{{tree}}"))
        for line in g(lane, "ls-tree", "-r", sha).split("\n"):
            if line.strip():
                objs.append(line.split()[2])
    objs = sorted(set(objs))
    if drop in objs:
        raise Premise("the dropped commit is in the kept object list")
    packed = subprocess.run(["git", "-C", str(lane), "pack-objects",
                              "--stdout"],
                             input="".join(f"{o}\n" for o in objs).encode(),
                             capture_output=True, env=env())
    if packed.returncode:
        raise Premise("pack-objects: "
                      f"{packed.stderr.decode(errors='replace').strip()}")
    for p in Path(lane, ".git/objects/pack").iterdir():
        p.unlink()
    indexed = subprocess.run(["git", "-C", str(lane), "index-pack", "--stdin"],
                             input=packed.stdout, capture_output=True,
                             env=env())
    if indexed.returncode:
        raise Premise("index-pack: "
                      f"{indexed.stderr.decode(errors='replace').strip()}")
    packs = sorted(Path(lane, ".git/objects/pack").iterdir())
    name = [p.name for p in packs if p.name.endswith(".pack")][0][:-5]
    Path(lane, ".git/objects/pack", name + ".promisor").write_bytes(b"")


# ---------------------------------------------------------------- the arms

def arm_control_promisor(tmp):
    """CA-1a: a real partial clone; every required object available."""
    origin, fleet, shas = build_origin(tmp)
    lane = clone(tmp, origin, "lane", partial=True)
    if not promisor_packs(lane):
        raise Premise("the promisor-marked clone has no .promisor pack")
    if not present(lane, shas["L1"]):
        raise Premise("L1 not available in the partial clone")
    return {"lane": lane, "fleet": fleet, "origin": origin, **shas}


def arm_fault_missing_ancestor(tmp):
    """CA-1b: the same partial clone, without the required ancestor."""
    origin, fleet, shas = build_origin(tmp)
    lane = clone(tmp, origin, "lane", partial=True)
    drop_object_from_pack(lane, [shas["L0"], shas["L2"], shas["L3"]],
                          shas["L1"])
    if present(lane, shas["L1"]):
        raise Premise("L1 is still available after the pack was rebuilt")
    for key in ("L0", "L2", "L3"):
        if not present(lane, shas[key]):
            raise Premise(f"{key} is missing from the fault lane: the arm "
                          "would not isolate the missing ancestor")
    if not present(origin, shas["L1"]):
        raise Premise("L1 is missing from the origin: the arm would not "
                      "detect a lazy fetch")
    if not promisor_packs(lane):
        raise Premise("the fault lane lost its .promisor pack")
    return {"lane": lane, "fleet": fleet, "origin": origin, **shas}


def arm_control_full_clone(tmp):
    """CA-1c: the same origin, cloned without a filter."""
    origin, fleet, shas = build_origin(tmp)
    lane = clone(tmp, origin, "lane", partial=False)
    if not present(lane, shas["L1"]):
        raise Premise("L1 not available in the full clone")
    return {"lane": lane, "fleet": fleet, "origin": origin, **shas}


ARMS = [
    ("CA-1a-promisor-complete", "control", arm_control_promisor,
     {"exit": 1, "kinds": ["landed-omitted"], "required": 3,
      "post_report": 1}),
    ("CA-1b-missing-required-ancestor", "fault", arm_fault_missing_ancestor,
     {"exit": 2, "kinds": None}),
    ("CA-1c-full-clone", "control", arm_control_full_clone,
     {"exit": 1, "kinds": ["landed-omitted"], "required": 3,
      "post_report": 1}),
]

FORBIDDEN_IN_FAULT = ("landed-omitted", "landed-unresolved",
                       "landed-ambiguous", "unresolved-full-hash",
                       "landed-section-missing")
# the r23 metadata refusal phrases: an exit 2 that carries one of them was
# decided by the promisor metadata, not by the unavailable evidence
FORBIDDEN_REASONS = ("partial clone (promisor pack)",
                     "partial clone (extensions.partialclone",
                     "partial clone (remote.")
# evidence language: the refusal must name what could not be read
EVIDENCE_REASONS = ("missing", "not available", "unavailable",
                    "unable to read", "could not read", "cannot read",
                    "failed to traverse", "incomplete", "not found",
                    "no such", "truncat")


def run_arm(auditor, name, kind, build, want, tmp):
    try:
        info = build(tmp)
        lane, fleet = info["lane"], info["fleet"]
        before_store = object_store(lane)
        before_head = g(lane, "rev-parse", "HEAD")
        before_fleet_head = g(fleet, "rev-parse", "HEAD")
        argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
                "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata",
                "--json"]
        proc = subprocess.run(argv, capture_output=True, env=env(), cwd=tmp,
                              timeout=TIMEOUT)
        out = proc.stdout.decode(errors="replace")
        err = proc.stderr.decode(errors="replace")
        code = proc.returncode
        doc = None
        if code in (0, 1):
            try:
                doc = json.loads(out)
            except ValueError:
                doc = None
        kinds, tokens, summary = None, [], None
        if doc:
            kinds = sorted({d["kind"] for r in doc["results"]
                            for d in r["defects"]})
            tokens = sorted({d["token"] for r in doc["results"]
                             for d in r["defects"]})
            summary = doc["summary"]
        after_store = object_store(lane)
        l1 = info["L1"]
        checks = {
            "exit_matches": code == want["exit"],
            "no_traceback": "Traceback (most recent call last)" not in err,
            "repo_unchanged": (g(lane, "rev-parse", "HEAD") == before_head
                               and g(fleet, "rev-parse", "HEAD")
                               == before_fleet_head),
            "no_object_fetched": after_store == before_store,
        }
        if want["kinds"] is None:
            checks["no_verdict_on_stdout"] = (
                doc is None and not any(k in out for k in FORBIDDEN_IN_FAULT))
            checks["cne_message"] = "could-not-evaluate" in err
            checks["reason_is_evidence"] = (
                any(t in err.lower() for t in EVIDENCE_REASONS)
                and not any(p in err for p in FORBIDDEN_REASONS))
            checks["missing_still_missing"] = not present(lane, l1)
            # recommended, not graded: the diagnostic should name the
            # unavailable object
            checks["_soft_names_the_object"] = l1 in err
        else:
            checks["kinds_match"] = kinds == sorted(want["kinds"])
            checks["token_match"] = tokens == [l1]
            checks["required_count"] = (
                (summary or {}).get("required_commits") == want["required"])
            checks["post_report_count"] = (
                (summary or {}).get("post_report_commits")
                == want["post_report"])
            checks["l1_still_present"] = present(lane, l1)
        met = all(v for k, v in checks.items() if not k.startswith("_"))
        return {"arm": name, "kind": kind, "exit": code, "kinds": kinds,
                "tokens": tokens, "summary": summary, "checks": checks,
                "met": met, "stderr": err.strip()[:600],
                "stdout": out.strip()[:600],
                "promisor_packs": promisor_packs(lane),
                "L0": info["L0"], "L1": l1, "L2": info["L2"], "L3": info["L3"]}
    except subprocess.TimeoutExpired:
        return {"arm": name, "kind": kind, "exit": None, "met": False,
                "checks": {"timeout": False},
                "stderr": f"auditor timed out after {TIMEOUT}s"}
    except Premise:
        raise
    except Exception as exc:  # errors are never case verdicts
        return {"arm": name, "kind": kind, "exit": None, "met": False,
                "checks": {"error": False},
                "stderr": f"{type(exc).__name__}: {exc}"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--auditor", action="append",
                    help="auditor to grade (default: the base tool)")
    ap.add_argument("--work", default=str(DEFAULT_WORK))
    ap.add_argument("--keep", action="store_true",
                    help="keep the fixture repositories")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    auditors = [str(Path(a).resolve()) for a in (args.auditor or
                                                        [str(DEFAULT_AUDITOR)])]
    work = Path(args.work)
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    doc = {"arms": {}, "expectations": {n: w for n, _, _, w in ARMS}}
    try:
        for auditor in auditors:
            rows = []
            for i, (name, kind, build, want) in enumerate(ARMS):
                tmp = work / Path(auditor).stem / f"{i:02d}-{name}"
                tmp.mkdir(parents=True)
                rows.append(run_arm(auditor, name, kind, build, want, tmp))
            doc["arms"][auditor] = rows
    except Premise as exc:
        print(f"could-not-evaluate: fixture premise: {exc}", file=sys.stderr)
        return 2
    if not args.keep:
        shutil.rmtree(work, ignore_errors=True)
    if args.json:
        print(json.dumps(doc, indent=1, sort_keys=True))
    else:
        for auditor, rows in doc["arms"].items():
            for r in rows:
                print(f"{Path(auditor).name} {r['arm']} {r['kind']} "
                      f"exit={r['exit']} kinds={r.get('kinds')} "
                      f"{'met' if r.get('met') else 'NOT-MET'}")
                for k, v in (r.get("checks") or {}).items():
                    if not v:
                        print(f"    failed check: {k}")
                if not r.get("met"):
                    print(f"    stderr: {r.get('stderr', '')[:300]}")
    bad = any(not r.get("met") for rows in doc["arms"].values() for r in rows)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
