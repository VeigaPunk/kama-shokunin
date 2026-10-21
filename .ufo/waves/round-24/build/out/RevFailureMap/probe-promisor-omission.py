#!/usr/bin/env python3
"""Genuine-omission disposition in a promisor-marked lane.

The round-24 contract keeps a genuine omitted pre-cutoff lane commit as
`landed-omitted` exit 1, even when the lane carries promisor metadata. A
repair that turns "promisor-marked" into a blanket exit 2 would break this.

Arms:
  O-plain-omission        plain lane, one uncited round-1 commit
  P-promisor-omission     same, plus remote.origin.promisor=true
  Q-promisor-metadata-only  same as P, but the citation is present and
                          complete: must be the same verdict as the plain
                          twin

Local, offline, synthetic.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = Path(sys.argv[1])
LABEL = sys.argv[2] if len(sys.argv) > 2 else TOOL.name
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def git(repo, *args, date="@1000 +0000"):
    env = {**ENV, "GIT_AUTHOR_NAME": "kama-shokunin",
           "GIT_COMMITTER_NAME": "kama-shokunin", "GIT_AUTHOR_EMAIL": "a@x",
           "GIT_COMMITTER_EMAIL": "a@x", "GIT_AUTHOR_DATE": date,
           "GIT_COMMITTER_DATE": date}
    return subprocess.run(["git", "-C", str(repo), *args], env=env,
                          capture_output=True, text=True)


def build(root, cite_second):
    lane, fleet = root / "lane", root / "fleet"
    for repo in (lane, fleet):
        repo.mkdir(parents=True)
        git(repo, "init", "-q", "-b", "master")
    (lane / "f").write_text("one\n", encoding="utf-8")
    git(lane, "add", "f")
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: work")
    first = git(lane, "rev-parse", "HEAD").stdout.strip()
    (lane / "f").write_text("two\n", encoding="utf-8")
    git(lane, "add", "f")
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: more", date="@1100 +0000")
    second = git(lane, "rev-parse", "HEAD").stdout.strip()
    cited = second if cite_second else first
    rep = fleet / ".ufo/reports/round-1/kama.md"
    rep.parent.mkdir(parents=True)
    rep.write_text("# round 1\n## Work performed\nx\n## Landed changes\n- `"
                   + cited + "` cited\n", encoding="utf-8")
    git(fleet, "add", ".ufo/reports/round-1/kama.md")
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: kama report", date="@1200 +0000")
    return lane, fleet, first, second


def audit(lane, fleet):
    p = subprocess.run([sys.executable, str(TOOL), "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1",
                        "--no-errata", "--json"], env=ENV, capture_output=True,
                       text=True)
    kinds = None
    if p.returncode in (0, 1):
        try:
            doc = json.loads(p.stdout)
            kinds = sorted((d["kind"], d["token"])
                           for r in doc["results"] for d in r["defects"])
        except json.JSONDecodeError:
            kinds = "<unparsable>"
    return p.returncode, kinds, p.stderr.strip()[:160]


root = Path(tempfile.mkdtemp(prefix="rfm-omit-",
                             dir="/fast/scratch/hyaku/kama-r24"))
print(f"# tool={TOOL} ({LABEL})")
print(f"# scratch={root}")
for arm, promisor, cite_second in (
        ("O-plain-omission", False, False),
        ("P-promisor-omission", True, False),
        ("Q-promisor-complete", True, True)):
    base = root / arm
    base.mkdir()
    lane, fleet, first, second = build(base, cite_second)
    if promisor:
        for repo in (lane, fleet):
            git(repo, "config", "remote.origin.promisor", "true")
            git(repo, "config", "remote.origin.url",
                "file:///nonexistent/promisor.git")
    rc, kinds, err = audit(lane, fleet)
    print(f"## arm {arm} (uncited lane commit={first[:12]}…)")
    print(f"  exit={rc}")
    print(f"  defects={kinds}")
    print(f"  stderr={err!r}")
