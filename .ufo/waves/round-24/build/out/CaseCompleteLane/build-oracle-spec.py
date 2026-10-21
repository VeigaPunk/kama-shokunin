#!/usr/bin/env python3
"""Final oracle specification + premise-effectiveness check for
PROM-COMPLETE-LANE (lane CaseCompleteLane, KamaR23-2.CaseCompleteLane-2).

Produces `.ufo/waves/round-24/build/out/CaseCompleteLane/oracle-spec.json`:

  * the preregistered expected exit / defect set of the case, written
    BEFORE any implementation exists (the base refuses this case today);
  * the observed base behaviour that pins the harm;
  * a premise-effectiveness assertion: the fixture must make the base
    refuse FOR THE PROMISOR REASON, otherwise the case would pass
    trivially against a full clone and would not discriminate.

All fixtures are local, offline and synthetic.  The promisor remote URL is
an inert non-existent local path, so no transport is reachable; no
repository-configured program is installed and none is executed.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REPO = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
AUDIT = REPO / "tools/report-landing-audit.py"
BASE = "0df800e896f6bce285a81e794ad4ae1d1e6c3a71"
OUT = REPO / ".ufo/waves/round-24/build/out/CaseCompleteLane"
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/CaseCompleteLane/oracle")
REL = ".ufo/reports/round-1/kama.md"
INERT = "/nonexistent/kama-promisor-origin.git"


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=env(**extra))
    if check and p.returncode:
        raise SystemExit(f"git {args}: {p.stderr.decode(errors='replace')}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path):
    g(path.parent, "init", "-q", "-b", "master", str(path))
    return path


def commit(repo, author, when, msg, path="f"):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "ab") as fh:
        fh.write((msg + "\n").encode())
    g(repo, "add", "--", path)
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=f"@{when} +0000", GIT_COMMITTER_DATE=f"@{when} +0000")
    return g(repo, "rev-parse", "HEAD")


def build(tmp, omit):
    lane = init(Path(tmp, "src-lane"))
    fleet = init(Path(tmp, "fleet"))
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    omitted = commit(lane, "kama-shokunin", 1500, "round-1: more") if omit \
        else None
    rep = Path(fleet, REL)
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_text("# kama round 1\n\n## Landed changes\n\n- " + lc + "\n",
                   encoding="utf-8")
    g(fleet, "add", "--", REL)
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
      "round-1: report", GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
      GIT_AUTHOR_DATE="@2000 +0000", GIT_COMMITTER_DATE="@2000 +0000")
    return lane, fleet, lc, omitted


def clone_full(source, twin):
    g(source.parent, "-c", "protocol.file.allow=always", "clone", "-q",
      "--no-hardlinks", "--no-local", str(source), str(twin))
    return twin


def mark_promisor(twin):
    g(twin, "config", "remote.origin.promisor", "true")
    g(twin, "config", "remote.origin.url", INERT)
    g(twin, "config", "remote.origin.fetch",
      "+refs/heads/*:refs/remotes/origin/*")
    return twin


def premise(twin, lane, required):
    packs = list(Path(g(twin, "rev-parse", "--absolute-git-dir"),
                      "objects/pack").glob("*.promisor"))
    missing = [l for l in g(twin, "rev-list", "--objects", "--all",
                             "--missing=print").splitlines()
               if l.startswith("?")]
    local = []
    for sha in required:
        r = subprocess.run(["git", "-C", str(twin), "cat-file", "-e",
                            f"{sha}^{{commit}}"], capture_output=True, env=env())
        local.append(r.returncode == 0)
    return {"promisor_pack_markers": len(packs),
            "missing_objects": missing,
            "required_objects_local": local,
            "promisor_declared": g(twin, "config", "--get",
                                    "remote.origin.promisor"),
            "origin_url": g(twin, "config", "--get", "remote.origin.url"),
            "tips_equal": g(twin, "rev-parse", "HEAD")
            == g(lane, "rev-parse", "HEAD")}


def audit(binary, lane, fleet):
    argv = [sys.executable, str(binary), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata",
            "--json"]
    p = subprocess.run(argv, capture_output=True, env=env(), cwd=str(fleet))
    defects = None
    if p.returncode in (0, 1):
        try:
            doc = json.loads(p.stdout)
            defects = sorted((d["kind"], d["token"])
                             for r in doc["results"] for d in r["defects"])
        except Exception:
            defects = "unparseable"
    return {"exit": p.returncode, "defects": defects,
            "stderr": p.stderr.decode(errors="replace").strip()[-300:]}


def main():
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)
    spec = {
        "case_family": "PROM-COMPLETE-LANE",
        "lane": "CaseCompleteLane",
        "author": "KamaR23-2.CaseCompleteLane-2",
        "base": BASE,
        "preregistered_before_implementation": True,
        "auditor_base_sha256": hashlib.sha256(AUDIT.read_bytes()).hexdigest(),
        "promisor_origin_url": INERT,
        "transport_used": "none (local synthetic fixtures only)",
        "rows": [],
    }
    for name, omit, want_exit, want_defects in (
            ("PROM-CLEAN", False, 0, []),
            ("PROM-OMIT", True, 1, ["landed-omitted"])):
        tmp = Path(SCRATCH, name)
        tmp.mkdir()
        lane, fleet, lc, omitted = build(tmp, omit)
        full = clone_full(lane, Path(tmp, "lane-full"))
        prom = mark_promisor(clone_full(lane, Path(tmp, "lane-promisor")))
        prem = premise(prom, lane, [lc] + ([omitted] if omitted else []))
        assert not prem["missing_objects"] and all(prem["required_objects_local"])
        assert prem["promisor_pack_markers"] == 0
        base_prom = audit(AUDIT, prom, fleet)
        base_full = audit(AUDIT, full, fleet)
        # premise effectiveness: the base must refuse THIS repository for
        # the promisor reason, otherwise the fixture did not discriminate.
        effective = (base_prom["exit"] == 2
                     and "partial clone (remote.origin.promisor)"
                     in base_prom["stderr"])
        spec["rows"].append({
            "name": name,
            "kind": "control",
            "cited_commit": lc,
            "omitted_commit": omitted,
            "expected_after_repair": {"exit": want_exit,
                                      "defect_kinds": want_defects,
                                      "equals_full_clone": True},
            "observed_base_promisor": base_prom,
            "observed_base_full_clone": base_full,
            "premise": prem,
            "premise_effective": effective,
        })
    dest = OUT / "oracle-spec.json"
    dest.write_text(json.dumps(spec, indent=1, sort_keys=True))
    print(json.dumps(spec, indent=1, sort_keys=True))
    ok = all(r["premise_effective"] for r in spec["rows"])
    print("premise_effective_all:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
