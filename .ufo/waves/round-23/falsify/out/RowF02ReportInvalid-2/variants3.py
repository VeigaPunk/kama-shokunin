#!/usr/bin/env python3
"""Can a committed report path that is NOT a regular blob be audited as a
clean report? (same read path as F02: git show HEAD:<rel>)"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

FROZEN = Path("/tmp/kama-r23w2/frozen-audit.py")
CURRENT = Path("/tmp/kama-r23w2/RowF02ReportInvalid-2/tools/report-landing-audit.py")
REL = ".ufo/reports/round-1/kama.md"


def genv(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=genv(**extra))
    if check and p.returncode:
        raise SystemExit(f"git {' '.join(args)}: rc={p.returncode} "
                         f"{p.stderr.decode(errors='replace')}")
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


def run(label, auditor, lane, fleet, extra=()):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--json", "--rounds", "1",
            "--no-errata", *extra]
    p = subprocess.run(argv, capture_output=True, timeout=30, env=genv(),
                       cwd=str(Path(lane).parent))
    tb = b"Traceback (most recent call last)" in p.stderr
    kinds = ""
    if p.returncode in (0, 1) and p.stdout:
        try:
            doc = json.loads(p.stdout)
            kinds = sorted({d["kind"] for r in doc["results"]
                            for d in r["defects"]})
        except Exception as exc:
            kinds = f"UNPARSEABLE {exc}"
    print(f"== {label}: exit={p.returncode} tb={tb} kinds={kinds}")
    print("   stderr:", (p.stderr.decode(errors="replace").strip()[-200:]
                         or "<empty>").replace("\n", " | "))
    return p.returncode


def base(root):
    lane, fleet = Path(root, "lane"), Path(root, "fleet")
    init(lane)
    init(fleet)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    return lane, fleet, lc


def main():
    root = Path(tempfile.mkdtemp(prefix="f02-link-", dir="/tmp/kama-r23w2/f02"))
    print(f"# root {root}")

    # S1: symlink target text IS a valid report citing the commit
    d = Path(root, "s1"); d.mkdir()
    lane, fleet, lc = base(d)
    target = "## Landed changes\n\n- " + lc + "\n"
    link = Path(fleet, REL)
    link.parent.mkdir(parents=True)
    os.symlink(target, link)
    g(fleet, "add", "--", REL)
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
      "round-1: report", GIT_AUTHOR_DATE="@2000 +0000",
      GIT_COMMITTER_DATE="@2000 +0000")
    print("# s1 ls-tree:", g(fleet, "ls-tree", "HEAD", "--", REL))
    shown = subprocess.run(["git", "-C", str(fleet), "show", f"HEAD:{REL}"],
                           capture_output=True, env=genv()).stdout
    print(f"# s1 git-show bytes: {shown!r}")
    print("# s1 worktree is symlink:", link.is_symlink(),
          "exists(target):", Path(fleet, REL).exists())
    run("s1-symlink-report-shape/current", CURRENT, lane, fleet)
    run("s1-symlink-report-shape/frozen", FROZEN, lane, fleet)

    # S2: regular blob control with identical bytes
    d = Path(root, "s2"); d.mkdir()
    lane, fleet, lc = base(d)
    commit(fleet, "fleet", 2000, "round-1: report", REL, target.encode())
    run("s2-regular-blob-control/current", CURRENT, lane, fleet)

    # S3: gitlink (submodule-like mode 160000) at the report path
    d = Path(root, "s3"); d.mkdir()
    lane, fleet, lc = base(d)
    g(fleet, "update-index", "--add", "--cacheinfo",
      f"160000,{lc},{REL}")
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
      "round-1: report", GIT_AUTHOR_DATE="@2000 +0000",
      GIT_COMMITTER_DATE="@2000 +0000")
    print("# s3 ls-tree:", g(fleet, "ls-tree", "HEAD", "--", REL))
    run("s3-gitlink-report/current", CURRENT, lane, fleet)


if __name__ == "__main__":
    main()
