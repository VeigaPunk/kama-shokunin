#!/usr/bin/env python3
"""FinalCase40 independent probes: the two-root missing-object diagnosis.

Each probe builds a fresh local pair of git repositories under the probe
root (no network, no transport, no fixture reuse), runs the PINNED
tools/report-landing-audit.py against them with a controlled environment,
and records premise, exit, stdout document, stderr, and the object
inventory before/after (objects_acquired).

Nothing here edits the pinned repository, the expectation manifest or any
production path.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase40")
CLONE = ROOT / "clone"
AUDIT = CLONE / "tools" / "report-landing-audit.py"
REL = ".ufo/reports/round-1/kama.md"
SOURCES = "# sources\n\nfixture: no registry rows\n"
FAKE = "0123456789abcdef0123456789abcdef01234567"
TIMEOUT = 30


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_DATE="@1000 +0000",
             GIT_COMMITTER_DATE="@1000 +0000")
    e.update(extra)
    return e


def git(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(map(str,args))} rc={p.returncode}: "
                           f"{p.stderr.decode(errors='replace')}")
    return p.stdout.decode(errors="replace")


def commit(repo, author, when, msg, path, content):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    git(repo, "add", "--", path)
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
        GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
        GIT_AUTHOR_DATE=f"@{when} +0000", GIT_COMMITTER_DATE=f"@{when} +0000")
    return git(repo, "rev-parse", "HEAD").strip()


def report_text(cites=(), notes=()):
    lines = ["# kama round 1", "", "## Landed changes", ""]
    for c in cites:
        lines.append(f"- {c}")
    if notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(notes)
    return "\n".join(lines) + "\n"


def mark_promisor(repo, tmp):
    git(repo, "config", "remote.origin.promisor", "true")
    git(repo, "config", "extensions.partialclone", "origin")
    git(repo, "config", "remote.origin.url", str(Path(tmp, "absent-remote.git")))


def drop(repo, sha):
    obj = Path(git(repo, "rev-parse", "--absolute-git-dir").strip()) / \
        "objects" / sha[:2] / sha[2:]
    if not obj.exists():
        raise RuntimeError(f"{sha} is not loose")
    obj.unlink()
    return sha


def inventory(repo):
    out = git(repo, "--no-lazy-fetch", "cat-file", "--batch-all-objects",
              "--batch-check=%(objectname)")
    return set(out.split())


def build(tmp, *, lane_files=(), drop_lane=(), drop_fleet=(), cites=(),
          notes=(), mark=(), fleet_notes_file=True):
    tmp = Path(tmp)
    lane = tmp / "lane"
    fleet = tmp / "fleet"
    for path in (lane, fleet):
        path.mkdir(parents=True, exist_ok=True)
        git(path.parent, "init", "-q", "-b", "master", str(path))
    files = [("corpus/SOURCES.md", SOURCES), ("f", "fixture file\n")]
    files += list(lane_files)
    for pth, content in files:
        target = Path(lane, pth)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    git(lane, "add", "--", *[p for p, _ in files])
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: work", GIT_AUTHOR_NAME="kama-shokunin",
        GIT_COMMITTER_NAME="kama-shokunin")
    l1 = git(lane, "rev-parse", "HEAD").strip()
    f_blob = git(lane, "rev-parse", f"{l1}:f").strip()
    commit(fleet, "fleet", 1900, "fleet: init", "notes.md", "notes\n")
    def sub(seq):
        return [str(x).replace("@F_BLOB@", f_blob) for x in seq]
    text = report_text(sub(cites) if cites else [l1], sub(notes))
    if fleet_notes_file:
        target = Path(fleet, REL)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        git(fleet, "add", "--", REL)
        git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
            "round-1: report", GIT_AUTHOR_NAME="fleet",
            GIT_COMMITTER_NAME="fleet", GIT_AUTHOR_DATE="@2000 +0000",
            GIT_COMMITTER_DATE="@2000 +0000")
    else:
        # fleet report committed without an extra file: reuse the same commit
        git(fleet, "add", "-A")
        git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
            "round-1: report", GIT_AUTHOR_NAME="fleet",
            GIT_COMMITTER_NAME="fleet")
    shas = {"lane_commit": l1, "f_blob": f_blob}
    for key, repo in (("unused_blob", lane), ("unused_tree", lane),
                      ("side_blob", lane), ("fleet_unused_blob", fleet)):
        if key in drop_lane or key in drop_fleet:
            if key == "unused_blob":
                sha = git(lane, "rev-parse", f"{l1}:notes/unused.txt").strip()
            elif key == "unused_tree":
                sha = git(lane, "rev-parse", f"{l1}:extra").strip()
            elif key == "side_blob":
                sha = git(lane, "rev-parse", f"side:side.txt").strip()
            else:
                sha = git(fleet, "rev-parse", "HEAD:notes.md").strip()
            shas[key] = drop(repo, sha)
    if "mark" == "lane":
        mark_promisor(lane, tmp)
    elif "mark" == "fleet":
        mark_promisor(fleet, tmp)
    elif mark == "both":
        mark_promisor(lane, tmp)
        mark_promisor(fleet, tmp)
    return lane, fleet, shas


def run_auditor(lane, fleet, cwd):
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    proc = subprocess.run(argv, capture_output=True, env=env(), cwd=str(cwd),
                          timeout=TIMEOUT)
    return proc.returncode, proc.stdout.decode(errors="replace"), \
        proc.stderr.decode(errors="replace")


def probe(name, expectation, **opts):
    tmp = ROOT / "probes" / name
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    lane, fleet, shas = build(tmp, **opts)
    before = {"lane": inventory(lane), "fleet": inventory(fleet)}
    code, out, err = run_auditor(lane, fleet, tmp)
    after = {"lane": inventory(lane), "fleet": inventory(fleet)}
    acquired = {k: sorted(after[k] - before[k]) for k in after}
    doc = None
    try:
        doc = json.loads(out)
    except ValueError:
        doc = None
    defects = []
    if doc:
        for res in doc.get("results", []):
            for d in res.get("defects", []):
                defects.append([d.get("kind"), d.get("token")])
    rec = {"probe": name, "expectation": expectation, "argv": [
        sys.executable, str(AUDIT), "--lane-repo", "<lane>",
        "--fleet-repo", "<fleet>", "--rounds", "1", "--json", "--no-errata"],
        "exit": code, "document_present": doc is not None,
        "defects": defects,
        "status": (doc or {}).get("summary", {}).get("status"),
        "stderr_tail": err.strip()[-400:],
        "objects_acquired": acquired,
        "shas": shas,
        "stdout": out, "stderr": err,
    }
    (tmp / "probe-result.json").write_text(json.dumps(rec, indent=1))
    print(f"== {name}: exit={code} document={doc is not None} "
          f"defects={defects} status={rec['status']} "
          f"acquired={acquired}")
    if err.strip():
        print(f"   stderr: {err.strip()[-300:]}")
    return rec


def main():
    outdir = ROOT / "out"
    outdir.mkdir(parents=True, exist_ok=True)
    recs = []
    # P1 two-root: the unrelated hole lives in the FLEET root, the
    # fabricated citation lives in the fleet report; the lane is
    # promisor-marked.  A hole-as-precondition would refuse here.
    recs.append(probe("p1-fleet-root-unrelated-hole",
                      "exit 1, one unresolved-full-hash defect, no refusal",
                      lane_files=[("notes/unused.txt", "unused\n")],
                      drop_fleet=("fleet_unused_blob",),
                      notes=[f"fake {FAKE}"], mark="lane"))
    # P2 unselected hole: a side branch that the audit does not read.
    tmp = ROOT / "probes" / "p2-unselected-hole"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    lane, fleet, shas = build(tmp, notes=[f"fake {FAKE}"], mark="lane")
    git(lane, "checkout", "-q", "-b", "side")
    commit(lane, "kama-shokunin", 1200, "side: file", "side.txt", "side\n")
    side = git(lane, "rev-parse", "HEAD:side.txt").strip()
    shas["side_blob"] = drop(lane, side)
    git(lane, "checkout", "-q", "master")
    before = {"lane": inventory(lane), "fleet": inventory(fleet)}
    code, out, err = run_auditor(lane, fleet, tmp)
    after = {"lane": inventory(lane), "fleet": inventory(fleet)}
    doc = None
    try:
        doc = json.loads(out)
    except ValueError:
        pass
    defects = [[d.get("kind"), d.get("token")]
               for res in (doc or {}).get("results", [])
               for d in res.get("defects", [])]
    rec = {"probe": "p2-unselected-hole",
           "expectation": "exit 1, one unresolved-full-hash defect, no refusal",
           "exit": code, "document_present": doc is not None,
           "defects": defects,
           "status": (doc or {}).get("summary", {}).get("status"),
           "stderr_tail": err.strip()[-400:],
           "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
           "shas": shas, "stdout": out, "stderr": err}
    (tmp / "probe-result.json").write_text(json.dumps(rec, indent=1))
    print(f"== p2-unselected-hole: exit={code} document={doc is not None} "
          f"defects={defects} status={rec['status']} "
          f"acquired={rec['objects_acquired']}")
    recs.append(rec)
    # P3 opaque (non-leaf) unused hole + unresolved fabricated token: the
    # registered refusal path must still bind and must be content-derived.
    recs.append(probe("p3-opaque-tree-unresolved-token",
                      "exit 2 content-derived refusal naming the missing tree",
                      lane_files=[("extra/leaf.txt", "unused tree\n")],
                      drop_lane=("unused_tree",),
                      notes=[f"fake {FAKE}"], mark="lane"))
    # P4 the same opaque hole with every citation resolved: no blanket
    # closure precondition, the clean verdict stands.
    recs.append(probe("p4-opaque-tree-clean",
                      "exit 0 clean, no refusal",
                      lane_files=[("extra/leaf.txt", "unused tree\n")],
                      drop_lane=("unused_tree",), mark="lane"))
    # P5 a conclusively wrong-type citation keeps its finding next to an
    # unrelated hole.
    recs.append(probe("p5-wrongtype-keeps-finding",
                      "exit 1, landed-unresolved for the known blob, no refusal",
                      lane_files=[("notes/unused.txt", "unused\n")],
                      drop_lane=("unused_blob",), mark="lane",
                      cites=["@F_BLOB@"]))
    # P6 a resolved full-hash citation keeps the clean verdict next to an
    # unrelated hole.
    recs.append(probe("p6-resolved-citation-clean",
                      "exit 0 clean, no refusal",
                      lane_files=[("notes/unused.txt", "unused\n")],
                      drop_lane=("unused_blob",), mark="lane",
                      notes=["@F_BLOB@"]))
    (outdir / "probes.json").write_text(json.dumps(recs, indent=1))
    print(f"wrote {outdir / 'probes.json'}")


if __name__ == "__main__":
    main()
