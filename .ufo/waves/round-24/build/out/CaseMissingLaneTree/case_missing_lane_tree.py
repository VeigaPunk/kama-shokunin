#!/usr/bin/env python3
"""Oracle case (round 24, C1 calibration 7->7): promisor-marked lane with an
unavailable reachable tree, every commit object present locally.

Expected outcome: exit 2 (could-not-evaluate). Never exit 0 (clean) and
never exit 1 (failed): a missing reachable tree is unavailable evidence, not
proof of absence.

The fixture is built offline: no network, no clone transport, no configured
program, no fetch. The promisor remote URL points at a non-existent local
path, so any lazy fetch would fail loudly and be visible in stderr; the
object store is compared before and after the run to prove nothing was
fetched.

The builder function `f_missing_lane_tree` is written in the house style of
tests/report-audit/repo-state-grid.py and is meant to be pasted into the
round-24 grid (tests/report-audit/promisor-grid.py) as one case.

Usage:
  case_missing_lane_tree.py --measure --arm PATH --out FILE
      Build the four fixture variants under a scratch root, run the auditor
      given by --arm on each, and write the measurement JSON to --out.
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
import tempfile

REL = ".ufo/reports/round-1/kama.md"
TIMEOUT = 30
ABSENT_REMOTE = "absent-promisor.git"


class Premise(Exception):
    """The fixture did not establish its premise: cannot evaluate."""


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


def report(cites, extra=b""):
    lines = b"".join(b"- " + c.encode() + b"\n" for c in cites)
    return b"# kama round 1\n\n## Landed changes\n\n" + lines + extra


def publish(fleet, text, when=2000, path=REL):
    commit(fleet, "fleet", when, "round-1: report", path, text)


def pair(tmp):
    lane, fleet = Path(tmp, "lane"), Path(tmp, "fleet")
    init(lane)
    init(fleet)
    return lane, fleet


def require(cond, what):
    if not cond:
        raise Premise(what)


# --------------------------------------------------------------- the case

def f_missing_lane_tree(tmp):
    """Promisor-marked lane whose reachable tip tree is unavailable while
    every commit object is present locally.

    Absence of a required object is not evidence: the audit must refuse to
    evaluate (exit 2), never report clean (0) and never report failed (1).
    The promisor metadata is not the reason and must not be the reason.
    """
    lane, fleet = pair(tmp)
    c1 = commit(lane, "kama-shokunin", 1000, "round-1: work")
    c2 = commit(lane, "kama-shokunin", 1500, "round-1: more")
    publish(fleet, report([c1, c2]))
    tree = g(lane, "rev-parse", f"{c2}^{{tree}}")
    loose = Path(lane, ".git/objects", tree[:2], tree[2:])
    require(loose.is_file(), "tip tree is not a loose object")
    os.unlink(loose)
    # promisor metadata only; the remote path does not exist, so a lazy
    # fetch could neither succeed nor contact anything
    for k, v in (("extensions.partialClone", "origin"),
                 ("remote.origin.url", str(Path(tmp, ABSENT_REMOTE))),
                 ("remote.origin.promisor", "true")):
        g(lane, "config", k, v)
    require(g(lane, "cat-file", "-t", c2) == "commit",
            "the tip commit object is not present locally")
    require(g(lane, "cat-file", "-t", c1) == "commit",
            "the cited commit object is not present locally")
    require(subprocess.run(["git", "--no-lazy-fetch", "-C", str(lane),
                            "cat-file", "-e", tree],
                           capture_output=True, env=env()).returncode != 0,
            "the tip tree is still readable")
    return lane, fleet, [], None


def build(root, *, promisor, missing_tree):
    """Variant builder shared by the case and its paired controls."""
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    lane, fleet = pair(root)
    c1 = commit(lane, "kama-shokunin", 1000, "round-1: work")
    c2 = commit(lane, "kama-shokunin", 1500, "round-1: more")
    publish(fleet, report([c1, c2]))
    tree = g(lane, "rev-parse", f"{c2}^{{tree}}")
    if missing_tree:
        loose = Path(lane, ".git/objects", tree[:2], tree[2:])
        require(loose.is_file(), "tip tree is not a loose object")
        os.unlink(loose)
    if promisor:
        for k, v in (("extensions.partialClone", "origin"),
                     ("remote.origin.url", str(root / ABSENT_REMOTE)),
                     ("remote.origin.promisor", "true")):
            g(lane, "config", k, v)
    return {"lane": lane, "fleet": fleet, "c1": c1, "c2": c2, "tree": tree,
            "root": root}


def object_store(repo):
    """Loose objects and pack files: a fetch would add to this set."""
    loose = sorted(p.name for p in (Path(repo) / ".git/objects").iterdir()
                   if p.is_dir() and len(p.name) == 2)
    packs = sorted(p.name for p in
                   (Path(repo) / ".git/objects/pack").glob("*"))
    return loose, packs


def missing_now(repo, oid):
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), "cat-file",
                        "-e", oid], capture_output=True, env=env())
    return p.returncode != 0


def run_auditor(auditor, lane, fleet, cwd):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata",
            "--json"]
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env(), cwd=str(cwd),
                            start_new_session=True)
    try:
        out, err = proc.communicate(timeout=TIMEOUT)
        code, timed_out = proc.returncode, False
    except subprocess.TimeoutExpired:
        import signal
        os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        code, timed_out = None, True
    kinds = None
    verdict = None
    if code in (0, 1):
        try:
            doc = json.loads(out)
            kinds = sorted({d["kind"] for r in doc["results"]
                            for d in r["defects"]})
            verdict = doc["summary"].get("status")
        except (ValueError, KeyError, TypeError):
            kinds = "unparseable"
    return {"exit": code, "timed_out": timed_out, "kinds": kinds,
            "verdict": verdict,
            "traceback": b"Traceback (most recent call last)" in err,
            "stdout": out.decode(errors="replace"),
            "stderr": err.decode(errors="replace").strip()}


VARIANTS = [
    ("case-promisor-missing-tree", True, True),
    ("control-promisor-complete", True, False),
    ("control-plain-missing-tree", False, True),
    ("control-plain-complete", False, False),
]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--arm", help="auditor to run (path to the script)")
    ap.add_argument("--out", help="measurement JSON output path")
    ap.add_argument("--scratch", default=None,
                    help="scratch root (default: a temp dir)")
    args = ap.parse_args(argv)
    if not args.measure:
        print("this module is a fixture builder; use --measure", file=sys.stderr)
        return 2
    if not args.arm or not args.out:
        print("--arm and --out are required", file=sys.stderr)
        return 2
    auditor = Path(args.arm).resolve()
    root = Path(args.scratch) if args.scratch else Path(
        tempfile.mkdtemp(prefix="missing-lane-tree-"))
    doc = {"arm": str(auditor),
           "auditor_sha256": hashlib.sha256(auditor.read_bytes()).hexdigest(),
           "scratch_root": str(root), "variants": {}}
    for name, promisor, missing in VARIANTS:
        vroot = root / name
        built = build(vroot, promisor=promisor, missing_tree=missing)
        loose_before, packs_before = object_store(built["lane"])
        res = run_auditor(auditor, built["lane"], built["fleet"], vroot)
        loose_after, packs_after = object_store(built["lane"])
        res["lane_objects_before"] = loose_before
        res["lane_objects_after"] = loose_after
        res["lane_packs_before"] = packs_before
        res["lane_packs_after"] = packs_after
        res["object_store_unchanged"] = (loose_before == loose_after
                                         and packs_before == packs_after)
        res["tree_still_missing"] = missing_now(built["lane"], built["tree"])
        res["commits_present"] = (
            g(built["lane"], "cat-file", "-t", built["c1"]) == "commit"
            and g(built["lane"], "cat-file", "-t", built["c2"]) == "commit")
        res["promisor"] = promisor
        res["missing_tree"] = missing
        res["tree"] = built["tree"]
        res["commits"] = [built["c1"], built["c2"]]
        res["stdout"] = res["stdout"][:4000]
        res["stderr"] = res["stderr"][:2000]
        doc["variants"][name] = res
    Path(args.out).write_text(json.dumps(doc, indent=1, sort_keys=True),
                              encoding="utf-8")
    for name, res in doc["variants"].items():
        print(f"{name} exit={res['exit']} kinds={res['kinds']} "
              f"verdict={res['verdict']} store_unchanged="
              f"{res['object_store_unchanged']} "
              f"tree_still_missing={res['tree_still_missing']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
