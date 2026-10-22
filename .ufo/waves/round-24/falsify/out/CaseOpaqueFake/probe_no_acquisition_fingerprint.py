#!/usr/bin/env python3
"""Variant E: no-acquisition proof by full .git fingerprint on the PG47 shape.

Fingerprints every file under both .git directories (relative path, size,
mtime_ns, sha256) before and after the auditor run, and compares.
Benign offline fixture: local git repos only, no network, no transport.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

AUDIT = ("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueFake/repo/"
         "tools/report-landing-audit.py")
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueFake/probeE")
REL = ".ufo/reports/round-1/kama.md"
SOURCES = "# sources\n\nfixture: no registry rows\n"
FAKE = "0123456789abcdef0123456789abcdef01234567"


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    e.update(extra)
    return e


def git(repo, *args, **extra):
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), *args],
                       capture_output=True, env=env(**extra))
    if p.returncode:
        raise SystemExit(f"git {' '.join(map(str,args))} rc={p.returncode} "
                         f"{p.stderr.decode(errors='replace')}")
    return p.stdout.decode(errors="surrogateescape")


def fingerprint(repo):
    gitdir = Path(git(repo, "rev-parse", "--absolute-git-dir").strip())
    out = {}
    for p in sorted(gitdir.rglob("*")):
        if p.is_file():
            st = p.stat()
            out[str(p.relative_to(gitdir))] = (
                st.st_size, st.st_mtime_ns,
                hashlib.sha256(p.read_bytes()).hexdigest())
    return out


def drop_object(repo, sha):
    obj = Path(git(repo, "rev-parse", "--absolute-git-dir").strip()) / \
        "objects" / sha[:2] / sha[2:]
    obj.unlink()


def main():
    shutil.rmtree(ROOT, ignore_errors=True)
    ROOT.mkdir(parents=True)
    lane, fleet = ROOT / "lane", ROOT / "fleet"
    git(ROOT, "init", "-q", "-b", "master", str(lane))
    git(ROOT, "init", "-q", "-b", "master", str(fleet))
    for pth, content in (("corpus/SOURCES.md", SOURCES),
                         ("f", "fixture file\n"), ("d/f", "opaque\n")):
        t = lane / pth
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(content, encoding="utf-8")
    git(lane, "add", "--", "corpus/SOURCES.md", "f", "d/f")
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: work",
        GIT_AUTHOR_NAME="kama-shokunin", GIT_COMMITTER_NAME="kama-shokunin",
        GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000")
    l1 = git(lane, "rev-parse", "HEAD").strip()
    subtree = git(lane, "rev-parse", f"{l1}:d").strip()
    hidden_blob = git(lane, "rev-parse", f"{l1}:d/f").strip()
    text = ("# kama round 1\n\n## Landed changes\n\n"
            f"- {l1}\n\n## Notes\n\nfake {FAKE}\n")
    p = fleet / REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    git(fleet, "add", "--", REL)
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: report", GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
        GIT_AUTHOR_DATE="@2000 +0000", GIT_COMMITTER_DATE="@2000 +0000")
    git(lane, "config", "remote.origin.promisor", "true")
    git(lane, "config", "extensions.partialclone", "origin")
    git(lane, "config", "remote.origin.url", str(ROOT / "absent-remote.git"))
    drop_object(lane, subtree)
    before = {"lane": fingerprint(lane), "fleet": fingerprint(fleet)}
    pr = subprocess.run([sys.executable, AUDIT, "--lane-repo", str(lane),
                         "--fleet-repo", str(fleet), "--rounds", "1", "--json",
                         "--no-errata"], capture_output=True, env=env(),
                        cwd=str(ROOT))
    after = {"lane": fingerprint(lane), "fleet": fingerprint(fleet)}
    diffs = {}
    for k in ("lane", "fleet"):
        b, a = before[k], after[k]
        added = sorted(set(a) - set(b))
        removed = sorted(set(b) - set(a))
        changed = sorted(p for p in set(a) & set(b) if a[p] != b[p])
        diffs[k] = {"added": added, "removed": removed, "changed": changed,
                    "files_before": len(b), "files_after": len(a)}
    res = {"variant": "E-no-acquisition-fingerprint",
           "exit": pr.returncode,
           "stderr": pr.stderr.decode(errors="replace").strip(),
           "stdout_len": len(pr.stdout),
           "fingerprint_diff": diffs,
           "missing_tree_oid": subtree, "hidden_blob_oid": hidden_blob}
    print(json.dumps(res, indent=1))
    (ROOT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
