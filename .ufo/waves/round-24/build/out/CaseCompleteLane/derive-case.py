#!/usr/bin/env python3
"""Bounded offline derivation for the PROM-COMPLETE-LANE oracle case.

Three parts, all local and offline:

 1. SIM-A  "naive removal" simulation: a scratch copy of the base auditor
          with ONLY the promisor-config refusal removed.  Against the
          complete promisor-marked lane it must reproduce the full-clone
          outcome (exit 0 / exit 1 landed-omitted).
 2. SIM-B  the same naive removal against a genuinely INCOMPLETE promisor
          repository (blobless clone, promisor config present, a cited
          blob missing).  It yields a guessed verdict (exit 1) where the
          contract demands exit 2 -> proves the repair needs an
          availability check, not merely the removal of the refusal.
 3. ESCAPE  containment evidence: every path the fixtures touch lies under
          /fast/scratch/hyaku/kama-r24/CaseCompleteLane; the production
          repository's tracked files are unchanged; /tmp gains no new
          entries.

The scratch copy of the auditor is a DERIVATION ARTIFACT, not a
candidate implementation: it is never installed into the production tree.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REPO = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
AUDIT = REPO / "tools/report-landing-audit.py"
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/CaseCompleteLane/derive")
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
    return twin


def blobless(source, twin):
    g(source, "config", "uploadpack.allowFilter", "true")
    g(source.parent, "-c", "protocol.file.allow=always", "clone", "-q",
      "--no-checkout", "--filter=blob:none", "--no-local", f"file://{source}",
      str(twin))
    return twin


def objects_state(repo):
    packs = sorted(p.name for p in
                   Path(g(repo, "rev-parse", "--git-path", "objects/pack"))
                   .glob("*"))
    count = subprocess.run(["git", "-C", str(repo), "count-objects", "-v"],
                           capture_output=True, env=env()).stdout.decode()
    return {"packs": packs, "count_objects": count.strip().splitlines()}


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


def naive_auditor(dest):
    """Scratch copy of the base auditor with the promisor-config refusal
    branch deleted (the promisor PACK refusal is kept)."""
    text = AUDIT.read_text(encoding="utf-8")
    old = """        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and git_bool(value)):
            raise EvalError(f"{repo}: partial clone ({key})")"""
    new = """        if key == "extensions.partialclone":
            raise EvalError(f"{repo}: partial clone ({key})")"""
    if old not in text:
        raise SystemExit("naive-patch anchor not found")
    dest.write_text(text.replace(old, new), encoding="utf-8")
    return dest


def main():
    tmp_before = set(os.listdir("/tmp"))
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)
    doc = {"derived_at": "offline, local fixtures only",
           "base_auditor_sha256": None, "cases": {}}
    import hashlib
    doc["base_auditor_sha256"] = hashlib.sha256(AUDIT.read_bytes()).hexdigest()

    naive = naive_auditor(SCRATCH / "audit-naive-no-promisor-refusal.py")
    doc["naive_auditor_sha256"] = hashlib.sha256(naive.read_bytes()).hexdigest()

    # --- PROM-CLEAN: complete promisor-marked lane, nothing omitted
    tmp = Path(SCRATCH, "PROM-CLEAN")
    tmp.mkdir()
    lane, fleet, lc, _ = build(tmp, omit=False)
    full = clone_full(lane, Path(tmp, "lane-full"))
    prom = mark_promisor(clone_full(lane, Path(tmp, "lane-promisor")))
    before = objects_state(prom)
    doc["cases"]["PROM-CLEAN"] = {
        "cited": lc,
        "base_promisor": audit(AUDIT, prom, fleet),
        "base_full": audit(AUDIT, full, fleet),
        "naive_promisor": audit(naive, prom, fleet),
        "objects_unchanged_after_audit": before == objects_state(prom),
    }

    # --- PROM-OMIT: complete promisor-marked lane, genuine omission
    tmp = Path(SCRATCH, "PROM-OMIT")
    tmp.mkdir()
    lane, fleet, lc, omitted = build(tmp, omit=True)
    full = clone_full(lane, Path(tmp, "lane-full"))
    prom = mark_promisor(clone_full(lane, Path(tmp, "lane-promisor")))
    before = objects_state(prom)
    doc["cases"]["PROM-OMIT"] = {
        "cited": lc, "omitted": omitted,
        "base_promisor": audit(AUDIT, prom, fleet),
        "base_full": audit(AUDIT, full, fleet),
        "naive_promisor": audit(naive, prom, fleet),
        "objects_unchanged_after_audit": before == objects_state(prom),
    }

    # --- SIM-B: genuinely INCOMPLETE promisor-backed lane.
    # The lane is a full clone whose origin is declared promisor, and the
    # ONE required evidence object (the blob the report cites) is removed
    # from the object store.  No .promisor pack marker exists, so only the
    # CONTENT of the store distinguishes this from PROM-COMPLETE-LANE.
    tmp = Path(SCRATCH, "INCOMPLETE")
    tmp.mkdir()
    lane, fleet, lc, _ = build(tmp, omit=False)
    blob = g(lane, "rev-parse", f"{lc}:f")
    rep = Path(fleet, REL)
    rep.write_text("# kama round 1\n\n## Landed changes\n\n- " + lc
                   + "\n\n## Notes\n\nblob " + blob + "\n", encoding="utf-8")
    g(fleet, "add", "--", REL)
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
      "round-1: report with blob citation", GIT_AUTHOR_NAME="fleet",
      GIT_COMMITTER_NAME="fleet", GIT_AUTHOR_DATE="@2000 +0000",
      GIT_COMMITTER_DATE="@2000 +0000")
    partial = Path(tmp, "lane-promisor")
    shutil.copytree(lane, partial)          # a copy keeps objects loose
    mark_promisor(partial)
    # remove the required evidence object from the local store only
    objdir = Path(g(partial, "rev-parse", "--absolute-git-dir")) / "objects"
    loose = objdir / blob[:2] / blob[2:]
    if loose.exists():
        loose.unlink()
    else:
        p = subprocess.run(["git", "-C", str(partial), "cat-file", "-e", blob],
                           capture_output=True, env=env())
        raise SystemExit("expected a loose object for the cited blob")
    gone = subprocess.run(["git", "-C", str(partial), "cat-file", "-e", blob],
                          capture_output=True, env=env()).returncode != 0
    packs = sorted(p.name for p in
                   Path(g(partial, "rev-parse", "--git-path", "objects/pack"))
                   .glob("*.promisor"))
    doc["cases"]["INCOMPLETE-PROMISOR"] = {
        "cited_blob": blob, "blob_locally_absent": gone,
        "promisor_pack_markers": packs,
        "base_promisor": audit(AUDIT, partial, fleet),
        "naive_promisor": audit(naive, partial, fleet),
        "contract_demands": "exit 2 could-not-evaluate (a required object "
                            "that is absent from a promisor-backed store is "
                            "unknown, never a guessed absence)",
    }

    # --- containment
    tmp_after = set(os.listdir("/tmp"))
    tracked = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain"],
                             capture_output=True,
                             env=env(GIT_DIR=str(REPO / ".git"),
                                     GIT_WORK_TREE=str(REPO))).stdout.decode()
    doc["containment"] = {
        "scratch_root": str(SCRATCH),
        "scratch_entries": sorted(p.name for p in SCRATCH.iterdir()),
        "tmp_new_entries": sorted(tmp_after - tmp_before),
        "production_status_porcelain": tracked.strip().splitlines(),
        "production_diff_stat": subprocess.run(
            ["git", "-C", str(REPO), "diff", "--stat"], capture_output=True,
            env=env()).stdout.decode().strip(),
        "production_head": g(REPO, "rev-parse", "HEAD"),
    }
    dest = REPO / ".ufo/waves/round-24/build/out/CaseCompleteLane/derivation.json"
    dest.write_text(json.dumps(doc, indent=1, sort_keys=True))
    print(json.dumps(doc, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
