#!/usr/bin/env python3
"""Bounded local runner for the PROM-COMPLETE-LANE oracle case.

Runs the *base* auditor (0df800e, unmodified) against two fixture pairs
built offline in scratch:

  full      a plain complete lane clone (the reference outcome)
  promisor  the same history cloned completely, with the origin remote
            declared promisor (metadata only; no .promisor pack, no
            missing object)

Expected (preregistered): promisor and full agree in exit code and in the
exact (kind, token) defect set.  The base is expected to REFUSE the
promisor pair (exit 2) - that refusal is the round-23 harm this case
pins down.

No network transport is used: the promisor remote URL is an inert
non-existent local path and no remote command is ever invoked.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

AUDIT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/tools/"
              "report-landing-audit.py")
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/CaseCompleteLane/run")
REL = ".ufo/reports/round-1/kama.md"


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
        raise SystemExit(f"git {args}: {p.stderr.decode(errors='replace')}")
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
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=f"@{when} +0000", GIT_COMMITTER_DATE=f"@{when} +0000")
    return g(repo, "rev-parse", "HEAD")


def report(cites):
    lines = b"".join(b"- " + c.encode() + b"\n" for c in cites)
    return b"# kama round 1\n\n## Landed changes\n\n" + lines


def build(tmp, omit):
    lane = init(Path(tmp, "src-lane"))
    fleet = init(Path(tmp, "fleet"))
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    omitted = None
    if omit:
        omitted = commit(lane, "kama-shokunin", 1500, "round-1: more")
    g(fleet, "add", "--", ".")
    rep = Path(fleet, REL)
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_bytes(report([lc]))
    g(fleet, "add", "--", REL)
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: report",
      GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
      GIT_AUTHOR_DATE="@2000 +0000", GIT_COMMITTER_DATE="@2000 +0000")
    return lane, fleet, lc, omitted


def clone_full(source, twin):
    g(source.parent, "-c", "protocol.file.allow=always", "clone", "-q",
      "--no-hardlinks", "--no-local", str(source), str(twin))
    return twin


def mark_promisor(twin):
    g(twin, "config", "remote.origin.promisor", "true")
    g(twin, "config", "remote.origin.url", "/nonexistent/kama-promisor-origin.git")
    g(twin, "config", "remote.origin.fetch",
      "+refs/heads/*:refs/remotes/origin/*")
    return twin


def premise(twin, required):
    packs = list(Path(g(twin, "rev-parse", "--git-path", "objects/pack"))
                 .glob("*.promisor"))
    assert not packs, f"promisor pack present: {packs}"
    missing = [l for l in g(twin, "rev-list", "--objects", "--all",
                             "--missing=print").splitlines()
               if l.startswith("?")]
    assert not missing, f"missing objects: {missing}"
    for sha in required:
        r = subprocess.run(["git", "-C", str(twin), "cat-file", "-e",
                            f"{sha}^{{commit}}"], capture_output=True, env=env())
        assert r.returncode == 0, f"{sha} not local"
    assert g(twin, "config", "--get", "remote.origin.promisor") == "true"
    assert g(twin, "rev-parse", "HEAD") == g(twin, "rev-parse", "HEAD")
    return {"promisor_packs": len(packs), "missing_objects": missing,
            "promisor": g(twin, "config", "--get", "remote.origin.promisor"),
            "url": g(twin, "config", "--get", "remote.origin.url")}


def run_audit(lane, fleet):
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata",
            "--json"]
    p = subprocess.run(argv, capture_output=True, env=env(), cwd=str(fleet))
    kinds, tokens = None, None
    if p.returncode in (0, 1):
        try:
            doc = json.loads(p.stdout)
            pairs = sorted((d["kind"], d["token"])
                           for r in doc["results"] for d in r["defects"])
            kinds = sorted({k for k, _ in pairs})
            tokens = pairs
        except Exception as exc:
            kinds, tokens = "unparseable", str(exc)
    return {"exit": p.returncode, "kinds": kinds, "defects": tokens,
            "stderr": p.stderr.decode(errors="replace").strip()[-400:]}


def main():
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)
    out = {"auditor": str(AUDIT), "cases": {}}
    for name, omit in (("PROM-CLEAN", False), ("PROM-OMIT", True)):
        tmp = Path(SCRATCH, name)
        tmp.mkdir()
        lane, fleet, lc, omitted = build(tmp, omit)
        required = [lc] + ([omitted] if omitted else [])
        full = clone_full(lane, Path(tmp, "lane-full"))
        prom = clone_full(lane, Path(tmp, "lane-promisor"))
        mark_promisor(prom)
        prem = premise(prom, required)
        out["cases"][name] = {
            "cited": lc, "omitted": omitted,
            "premise": prem,
            "full": run_audit(full, fleet),
            "promisor": run_audit(prom, fleet),
        }
        out["cases"][name]["agree"] = (
            out["cases"][name]["full"]["exit"]
            == out["cases"][name]["promisor"]["exit"]
            and out["cases"][name]["full"]["defects"]
            == out["cases"][name]["promisor"]["defects"])
    dest = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/"
                "round-24/build/out/CaseCompleteLane/base-observation.json")
    dest.write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
