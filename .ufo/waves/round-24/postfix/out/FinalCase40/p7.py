#!/usr/bin/env python3
"""P7: prefix-collision boundary of the token-scoped missing-object rule.

The lane holds an unused file whose blob is removed.  The Landed section
cites the 7-hex abbreviation of that missing blob.  The candidate must
refuse (the citation names content the store cannot serve), and the
refusal must name the token: the rule is name-scoped, not a blanket
hole precondition.  A second variant cites a DIFFERENT 7-hex
abbreviation that no missing object matches: it must keep the ordinary
landed-unresolved finding.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase40")
AUDIT = ROOT / "clone" / "tools" / "report-landing-audit.py"
REL = ".ufo/reports/round-1/kama.md"
SOURCES = "# sources\n\nfixture: no registry rows\n"


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    e.update(extra)
    return e


def git(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(map(str,args))} rc={p.returncode}: "
                           f"{p.stderr.decode(errors='replace')}")
    return p.stdout.decode(errors="replace")


def run(mode, name):
    tmp = ROOT / "probes" / name
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    lane, fleet = tmp / "lane", tmp / "fleet"
    for p in (lane, fleet):
        p.mkdir(parents=True)
        git(tmp, "init", "-q", "-b", "master", str(p))
    for pth, content in (("corpus/SOURCES.md", SOURCES), ("f", "fixture\n"),
                         ("notes/unused.txt", "unused\n")):
        t = Path(lane, pth)
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(content, encoding="utf-8")
    git(lane, "add", "--", "corpus/SOURCES.md", "f", "notes/unused.txt")
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "work",
        GIT_AUTHOR_NAME="kama-shokunin", GIT_COMMITTER_NAME="kama-shokunin",
        GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000")
    l1 = git(lane, "rev-parse", "HEAD").strip()
    blob = git(lane, "rev-parse", f"{l1}:notes/unused.txt").strip()
    git(fleet, "config", "user.name", "fleet")
    Path(fleet, "notes.md").write_text("notes\n", encoding="utf-8")
    git(fleet, "add", "-A")
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "init",
        GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
        GIT_AUTHOR_DATE="@1900 +0000", GIT_COMMITTER_DATE="@1900 +0000")
    cited_token = blob[:7] if mode == "prefix" else "deadbee1"
    report = f"# kama round 1\n\n## Landed changes\n\n- {cited_token}\n"
    t = Path(fleet, REL)
    t.parent.mkdir(parents=True, exist_ok=True)
    t.write_text(report, encoding="utf-8")
    git(fleet, "add", "--", REL)
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "report",
        GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
        GIT_AUTHOR_DATE="@2000 +0000", GIT_COMMITTER_DATE="@2000 +0000")
    # remove the unused blob (the hole)
    gd = Path(git(lane, "rev-parse", "--absolute-git-dir").strip())
    (gd / "objects" / blob[:2] / blob[2:]).unlink()
    # promisor-mark the lane
    git(lane, "config", "remote.origin.promisor", "true")
    git(lane, "config", "extensions.partialclone", "origin")
    git(lane, "config", "remote.origin.url", str(tmp / "absent-remote.git"))
    before = set(git(lane, "--no-lazy-fetch", "cat-file", "--batch-all-objects",
                     "--batch-check=%(objectname)").split())
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    proc = subprocess.run(argv, capture_output=True, env=env(), cwd=str(tmp),
                          timeout=30)
    after = set(git(lane, "--no-lazy-fetch", "cat-file", "--batch-all-objects",
                    "--batch-check=%(objectname)").split())
    doc = None
    try:
        doc = json.loads(proc.stdout.decode(errors="replace"))
    except ValueError:
        pass
    defects = [[d.get("kind"), d.get("token")]
               for res in (doc or {}).get("results", [])
               for d in res.get("defects", [])]
    rec = {"probe": name, "cited_token": cited_token, "missing_blob": blob,
           "exit": proc.returncode, "document_present": doc is not None,
           "defects": defects,
           "status": (doc or {}).get("summary", {}).get("status"),
           "stderr_tail": proc.stderr.decode(errors="replace").strip()[-400:],
           "objects_acquired": sorted(after - before),
           "argv": argv}
    (tmp / "probe-result.json").write_text(json.dumps(rec, indent=1))
    print(f"== {name}: exit={proc.returncode} document={doc is not None} "
          f"defects={defects} acquired={rec['objects_acquired']}")
    if rec["stderr_tail"]:
        print("   stderr:", rec["stderr_tail"][-250:])
    return rec


def main():
    recs = [run("prefix", "p7-prefix-of-missing-blob")]
    # a 7-hex abbreviation that matches no missing object: it must keep the
    # ordinary finding, not a refusal
    recs.append(run("deadbee1", "p7-unrelated-abbrev"))
    (ROOT / "out" / "probes-p7.json").write_text(json.dumps(recs, indent=1))


if __name__ == "__main__":
    main()
