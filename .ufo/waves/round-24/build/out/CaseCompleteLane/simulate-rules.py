#!/usr/bin/env python3
"""Bounded local simulation: is the PROM-COMPLETE-LANE oracle SATISFIABLE?

Three candidate rules are simulated as scratch copies of the base auditor
(never installed into the production tree):

  R0  base (0df800e, unmodified)
      refuses any repository whose config declares a promisor remote.

  R1  "naive removal" -- the promisor-config refusal branch deleted.
      Satisfies PROM-CLEAN and PROM-OMIT, but it also converts a genuinely
      missing required object into a guessed verdict (exit 1) where the
      contract demands exit 2.

  R2  "content-based" -- the promisor declaration is recorded instead of
      refused; a required object that cannot be read from the audited
      repositories raises EvalError (exit 2).  Satisfies PROM-CLEAN,
      PROM-OMIT and the incomplete case simultaneously.

R2 shows the oracle is not over-constrained: one rule satisfies all three
rows, so PROM-CLEAN/PROM-OMIT are jointly satisfiable with the contract's
exit-2 requirement for unavailable evidence.

Fixtures: local synthetic repositories only.  The promisor origin URL is an
inert non-existent local path, so no transport is reachable; no
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
OUT = REPO / ".ufo/waves/round-24/build/out/CaseCompleteLane"
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/CaseCompleteLane/simulate")
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


def build(tmp, omit, cite_blob=False):
    lane = init(Path(tmp, "src-lane"))
    fleet = init(Path(tmp, "fleet"))
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    omitted = commit(lane, "kama-shokunin", 1500, "round-1: more") if omit \
        else None
    blob = g(lane, "rev-parse", f"{lc}:f")
    body = "# kama round 1\n\n## Landed changes\n\n- " + lc + "\n"
    if cite_blob:
        body += "\n## Notes\n\nblob " + blob + "\n"
    rep = Path(fleet, REL)
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_text(body, encoding="utf-8")
    g(fleet, "add", "--", REL)
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
      "round-1: report", GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
      GIT_AUTHOR_DATE="@2000 +0000", GIT_COMMITTER_DATE="@2000 +0000")
    return lane, fleet, lc, omitted, blob


def clone_full(source, twin):
    g(source.parent, "-c", "protocol.file.allow=always", "clone", "-q",
      "--no-hardlinks", "--no-local", str(source), str(twin))
    return twin


def mark_promisor(twin):
    g(twin, "config", "remote.origin.promisor", "true")
    g(twin, "config", "remote.origin.url", INERT)
    return twin


def drop_object(repo, sha):
    gitdir = Path(g(repo, "rev-parse", "--absolute-git-dir"))
    loose = gitdir / "objects" / sha[:2] / sha[2:]
    assert loose.exists(), f"no loose object {sha}"
    loose.unlink()
    r = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", sha],
                       capture_output=True, env=env())
    return r.returncode != 0


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
            "stderr": p.stderr.decode(errors="replace").strip()[-260:]}


def rule_r1(text):
    """Naive removal of the promisor-config refusal branch."""
    old = """        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and git_bool(value)):
            raise EvalError(f"{repo}: partial clone ({key})")"""
    new = """        if key == "extensions.partialclone":
            raise EvalError(f"{repo}: partial clone ({key})")"""
    assert old in text
    return text.replace(old, new)


def rule_r2(text):
    """Content-based rule: record the promisor declaration instead of
    refusing on it; a required object that is unreadable raises EvalError.

    The simulation is deliberately minimal: it replaces the config-scan
    refusal with a marker and makes `lookup` treat a 'missing' token in a
    promisor-backed repository as unavailable evidence (exit 2).
    """
    old = """        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and git_bool(value)):
            raise EvalError(f"{repo}: partial clone ({key})")"""
    new = """        if key == "extensions.partialclone":
            raise EvalError(f"{repo}: partial clone ({key})")
        if re.fullmatch(r"remote\\..+\\.promisor", key) and git_bool(value):
            PROMISOR_REPOS.add(str(repo))"""
    assert old in text
    text = text.replace(old, new)
    text = text.replace(
        "class EvalError(Exception):",
        "PROMISOR_REPOS = set()\n\n\nclass EvalError(Exception):", 1)
    old_lookup = """    defects += [{"kind": "unresolved-full-hash", "token": t}
                for t, s in full.items() if s != "found"]"""
    new_lookup = """    if any(str(r) in PROMISOR_REPOS for r in repos) and any(
            s != "found" for s in full.values()):
        raise EvalError("promisor-backed repository: a required object is "
                        "not available locally")
    defects += [{"kind": "unresolved-full-hash", "token": t}
                for t, s in full.items() if s != "found"]"""
    assert old_lookup in text
    return text.replace(old_lookup, new_lookup)


def main():
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)
    base_text = AUDIT.read_text(encoding="utf-8")
    r1 = SCRATCH / "rule-r1-naive-removal.py"
    r2 = SCRATCH / "rule-r2-content-based.py"
    r1.write_text(rule_r1(base_text), encoding="utf-8")
    r2.write_text(rule_r2(base_text), encoding="utf-8")
    doc = {"simulations": {
        "R0-base": {"sha256": hashlib.sha256(base_text.encode()).hexdigest()},
        "R1-naive-removal": {
            "sha256": hashlib.sha256(r1.read_bytes()).hexdigest()},
        "R2-content-based": {
            "sha256": hashlib.sha256(r2.read_bytes()).hexdigest()}},
        "rows": []}

    def row(name, omit, cite_blob, drop):
        tmp = Path(SCRATCH, name)
        tmp.mkdir()
        lane, fleet, lc, omitted, blob = build(tmp, omit, cite_blob)
        prom = mark_promisor(clone_full(lane, Path(tmp, "lane-promisor")))
        full = clone_full(lane, Path(tmp, "lane-full"))
        if drop:
            # a clone packs its objects; work on a copy that keeps them
            # loose so the single required object can be removed
            shutil.rmtree(prom)
            shutil.copytree(lane, prom)
            mark_promisor(prom)
            assert drop_object(prom, blob)
        out = {"name": name, "cited": lc, "omitted": omitted,
               "cited_blob": blob if cite_blob else None}
        for label, binary in (("R0-base", AUDIT), ("R1-naive-removal", r1),
                              ("R2-content-based", r2)):
            out[label] = {"promisor": audit(binary, prom, fleet),
                          "full_clone": audit(binary, full, fleet)}
        doc["rows"].append(out)

    row("PROM-CLEAN", omit=False, cite_blob=False, drop=False)
    row("PROM-OMIT", omit=True, cite_blob=False, drop=False)
    row("INCOMPLETE-PROMISOR", omit=False, cite_blob=True, drop=True)

    dest = OUT / "simulation.json"
    dest.write_text(json.dumps(doc, indent=1, sort_keys=True))
    print(json.dumps(doc, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
