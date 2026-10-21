#!/usr/bin/env python3
"""OracleLocalBlobType: independent fixture + measurement for the round-24
promisor repair, lane-local-blob-type case.

Case (independent oracle, built from the r23 base semantics at
0df800e896f6bce285a81e794ad4ae1d1e6c3a71):

  A fleet report cites, outside `## Landed changes`, a full 40-hex token that
  names a BLOB present in the lane object store.  The lane repository carries
  promisor *metadata* (config and/or paired .promisor pack marker) but every
  required object is present locally.

  Expected outcome (same as the otherwise identical full clone):
    exit 0, findings [] (no unresolved-full-hash, no landed-* defect)
  r23 base outcome: exit 2 (blanket promisor refusal) -- the harm being
  repaired.

Everything is offline: no clone, no transport, no network.  Promisor
metadata is added by config/pack-marker only; GIT_ALLOW_PROTOCOL=file
makes any accidental fetch impossible.

Usage: fixture.py            # build + measure, write artifacts
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/fast/scratch/hyaku/kama-r24/OracleLocalBlobType")
AUDIT = ("/home/vgpnk/Projects/shokunin/kama-shokunin/"
         "tools/report-landing-audit.py")
REL = ".ufo/reports/round-1/kama.md"
TIMEOUT = 30
GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch",
                 "-c", "i18n.logOutputEncoding=UTF-8",
                 "-c", "log.follow=false", "-c", "log.showRoot=true",
                 "-c", "log.showSignature=false", "-c", "log.mailmap=false")


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
             GIT_ALLOW_PROTOCOL="file")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise SystemExit(f"git {args}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path):
    path.parent.mkdir(parents=True, exist_ok=True)
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
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_EMAIL="a@x",
      GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def build_pair(root: Path, dangling: bool = False):
    """lane: one round-1 work commit by kama-shokunin holding a blob.
    fleet: the round-1 report citing that commit plus the blob hash outside
    `## Landed changes`."""
    lane = init(root / "lane")
    fleet = init(root / "fleet")
    body = b"local blob body\n"
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work", "f",
                b"round-1 work\n")
    # one more file in the SAME commit: the cited blob must be reachable from
    # the cited commit root, and must not create a second round-1 commit
    Path(lane, "corpus").mkdir(parents=True, exist_ok=True)
    Path(lane, "corpus/blob.txt").write_bytes(body)
    g(lane, "add", "--", "corpus/blob.txt")
    g(lane, "-c", "commit.gpgsign=false", "commit", "-q", "--amend", "--no-edit",
      GIT_AUTHOR_NAME="kama-shokunin", GIT_COMMITTER_NAME="kama-shokunin",
      GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000")
    lc = g(lane, "rev-parse", "HEAD")
    blob_sha = g(lane, "rev-parse", "HEAD:corpus/blob.txt")
    if dangling:
        # a blob that exists in the object store but is NOT reachable from
        # any commit root: closure-by-rev-list cannot see it
        blob_sha = g(lane, "hash-object", "-w", "--stdin", data=b"dangling blob\n")
    text = (b"# kama round 1\n\n## Landed changes\n\n- " + lc.encode()
            + b"\n\n## Notes\n\nlocal blob " + blob_sha.encode() + b"\n")
    commit(fleet, "fleet", 2000, "round-1: report", REL, text)
    return lane, fleet, lc, blob_sha


def mark_promisor_config(repo, url):
    g(repo, "config", "remote.origin.url", url)
    g(repo, "config", "remote.origin.promisor", "true")
    g(repo, "config", "remote.origin.partialclonefilter", "blob:none")
    g(repo, "config", "extensions.partialclone", "origin")
    return {"config": ["remote.origin.promisor",
                       "remote.origin.partialclonefilter",
                       "extensions.partialclone"]}


def mark_promisor_paired(repo):
    """paired marker: objects/pack/pack-*.promisor next to a real pack."""
    g(repo, "repack", "-a", "-d")
    packs = list(Path(repo, ".git/objects/pack").glob("*.pack"))
    if not packs:
        raise SystemExit("no pack produced")
    marker = packs[0].with_suffix(".promisor")
    marker.write_bytes(b"")
    return marker.name


def audit(lane, fleet):
    argv = [sys.executable, AUDIT, "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata",
            "--json"]
    try:
        p = subprocess.run(argv, capture_output=True, env=env(), timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return {"exit": None, "timed_out": True, "stderr_tail": "timeout"}
    doc = None
    if p.returncode in (0, 1):
        try:
            doc = json.loads(p.stdout)
        except ValueError:
            doc = None
    out = {"exit": p.returncode, "timed_out": False,
           "stderr_tail": p.stderr.decode(errors="replace").strip()[-300:]}
    if doc is not None:
        out["kinds"] = sorted({d["kind"] for r in doc["results"]
                               for d in r["defects"]})
        out["defects"] = [d for r in doc["results"] for d in r["defects"]]
        out["summary"] = doc["summary"]
    return out


def git_facts(repo, roots, blob_sha):
    """Closure and object-existence facts the repaired auditor needs."""
    facts = {}
    for root in roots:
        out = subprocess.run(
            ["git", *GIT_ISOLATION, "-C", str(repo), "rev-list", "--objects",
             "--missing=print", "--no-object-names", root],
            capture_output=True, env=env())
        lines = [l for l in out.stdout.decode().split("\n") if l]
        facts[f"closure:{root}"] = {
            "rc": out.returncode,
            "lines": len(lines),
            "missing": [l for l in lines if l.startswith("?")],
            "stderr": out.stderr.decode(errors="replace").strip()[:200]}
    batch = subprocess.run(
        ["git", *GIT_ISOLATION, "-C", str(repo), "cat-file", "--batch-check"],
        input=(blob_sha + "\n").encode(), capture_output=True, env=env())
    facts["cat-file-batch-check"] = {
        "rc": batch.returncode,
        "out": batch.stdout.decode().strip(),
        "err": batch.stderr.decode(errors="replace").strip()[:200]}
    return facts


def scenario(name, root, mutate=None, dangling=False):
    root.mkdir(parents=True, exist_ok=True)
    lane, fleet, lc, blob = build_pair(root, dangling=dangling)
    marked = {}
    if mutate:
        marked = mutate(lane, fleet) or {}
    res = {"scenario": name, "lane": str(lane), "fleet": str(fleet),
           "lane_commit": lc, "blob": blob,
           "blob_type": g(lane, "cat-file", "-t", blob),
           "marked": marked,
           "audit": audit(lane, fleet),
           "facts": git_facts(lane, [lc], blob)}
    # fleet-side facts too
    res["facts_fleet"] = git_facts(fleet, ["HEAD"], blob)
    return res


def main():
    base = ROOT / "cases"
    if base.exists():
        shutil.rmtree(base)
    results = []
    results.append(scenario("A-full-clone", base / "A"))
    results.append(scenario("B-promisor-config-lane",
                            base / "B",
                            lambda lane, fleet: mark_promisor_config(
                                lane, str(lane))))
    results.append(scenario("C-promisor-paired-marker-lane",
                            base / "C",
                            lambda lane, fleet: {
                                **mark_promisor_config(lane, str(lane)),
                                "paired_marker": mark_promisor_paired(lane)}))
    results.append(scenario("D-full-clone-dangling-blob", base / "D",
                            dangling=True))
    results.append(scenario("F-promisor-config-lane-and-fleet",
                            base / "F",
                            lambda lane, fleet: {
                                **mark_promisor_config(lane, str(lane)),
                                **mark_promisor_config(fleet, str(fleet))}))
    results.append(scenario("G-promisor-filter-only-lane",
                            base / "G",
                            lambda lane, fleet: (
                                g(lane, "config", "remote.origin.url",
                                  str(lane)),
                                g(lane, "config",
                                  "remote.origin.partialclonefilter",
                                  "blob:none"),
                                {"filter_only": True})[1]))
    results.append(scenario("I-promisor-paired-marker-only-lane",
                            base / "I",
                            lambda lane, fleet: {
                                "paired_marker": mark_promisor_paired(lane)}))
    results.append(scenario("E-promisor-config-lane-dangling-blob", base / "E",
                            lambda lane, fleet: mark_promisor_config(lane, str(lane)),
                            dangling=True))
    doc = {"audit_tool": AUDIT, "scenarios": results}
    twins = {"B-promisor-config-lane": "A-full-clone",
             "C-promisor-paired-marker-lane": "A-full-clone",
             "F-promisor-config-lane-and-fleet": "A-full-clone",
             "G-promisor-filter-only-lane": "A-full-clone",
             "I-promisor-paired-marker-only-lane": "A-full-clone",
             "E-promisor-config-lane-dangling-blob": "D-full-clone-dangling-blob"}
    by_name = {s["scenario"]: s for s in results}
    doc["twin_comparison"] = {}
    for name, twin in twins.items():
        s, t = by_name[name], by_name[twin]
        sa, ta = s["audit"], t["audit"]
        doc["twin_comparison"][name] = {
            "twin": twin,
            "same_exit": sa["exit"] == ta["exit"],
            "same_kinds": sa.get("kinds") == ta.get("kinds"),
            "same_defects": sa.get("defects") == ta.get("defects"),
            "same_summary": sa.get("summary") == ta.get("summary"),
            "base_exit": sa["exit"], "twin_base_exit": ta["exit"],
            "base_stderr": sa["stderr_tail"][:160]}
    out = ROOT / "measurements.json"
    out.write_text(json.dumps(doc, indent=1, sort_keys=True))
    for r in results:
        a = r["audit"]
        print(f"{r['scenario']}: exit={a['exit']} kinds={a.get('kinds')} "
              f"blob_type={r['blob_type']} marked={sorted(r['marked'])} "
              f"stderr={a['stderr_tail'][:120]}")
    print(f"written {out}")


if __name__ == "__main__":
    main()
