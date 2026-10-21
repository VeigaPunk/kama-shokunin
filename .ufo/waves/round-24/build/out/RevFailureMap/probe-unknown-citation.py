#!/usr/bin/env python3
"""Unknown-citation disposition probe (local, offline, synthetic).

Arms:
  P  plain repos, citation resolves nowhere          -> proved absent
  Q  promisor-marked repos, citation resolves nowhere -> UNKNOWN (not proved
     absent): the promisor remote may hold it
  R  promisor-marked repos, citation resolves in the other audited repo
     -> resolved locally, not unknown

Arms Q and R are run against the MEASUREMENT COPY in which the metadata-only
promisor refusal has been removed (the repair under construction); they show
what the remaining code does once the blanket refusal is gone, i.e. which
sink the "missing" answer reaches.

Usage: probe-unknown-citation.py <tool-under-test> [<label>]
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
ABSENT = "0123456789abcdef0123456789abcdef01234567"


def git(repo, *args, date="@1000 +0000"):
    env = {**ENV, "GIT_AUTHOR_NAME": "kama-shokunin",
           "GIT_COMMITTER_NAME": "kama-shokunin", "GIT_AUTHOR_EMAIL": "a@x",
           "GIT_COMMITTER_EMAIL": "a@x", "GIT_AUTHOR_DATE": date,
           "GIT_COMMITTER_DATE": date}
    return subprocess.run(["git", "-C", str(repo), *args], env=env,
                          capture_output=True, text=True)


def build(root, citation, fleet_has_object=False):
    lane, fleet = root / "lane", root / "fleet"
    for repo in (lane, fleet):
        repo.mkdir(parents=True)
        git(repo, "init", "-q", "-b", "master")
    (lane / "f").write_text("work\n", encoding="utf-8")
    git(lane, "add", "f")
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: work")
    sha = git(lane, "rev-parse", "HEAD").stdout.strip()
    if fleet_has_object:
        (fleet / "g").write_text("other\n", encoding="utf-8")
        git(fleet, "add", "g")
        git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
            "round-1: other")
    rep = fleet / ".ufo/reports/round-1/kama.md"
    rep.parent.mkdir(parents=True)
    rep.write_text("# round 1\n## Work performed\nsee " + citation + "\n"
                   "## Landed changes\n- `" + sha + "` work\n",
                   encoding="utf-8")
    git(fleet, "add", ".ufo/reports/round-1/kama.md")
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: kama report", date="@1200 +0000")
    fleet_sha = git(fleet, "rev-parse", "HEAD").stdout.strip()
    return lane, fleet, fleet_sha


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


root = Path(tempfile.mkdtemp(prefix="rfm-unk-",
                             dir="/fast/scratch/hyaku/kama-r24"))
print(f"# tool={TOOL} ({LABEL})")
print(f"# scratch={root}")

for arm, promisor, cross in (
        ("P-plain-absent", False, False),
        ("Q-promisor-absent", True, False),
        ("R-promisor-found-elsewhere", True, True)):
    base = root / arm
    base.mkdir()
    lane, fleet, fleet_sha = build(base, ABSENT, fleet_has_object=cross)
    citation = fleet_sha if cross else ABSENT
    if cross:
        rep = fleet / ".ufo/reports/round-1/kama.md"
        body = rep.read_text(encoding="utf-8").replace(ABSENT, citation)
        rep.write_text(body, encoding="utf-8")
        git(fleet, "add", ".ufo/reports/round-1/kama.md")
        git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
            "round-1: kama report v2", date="@1300 +0000")
    if promisor:
        for repo in (lane, fleet):
            git(repo, "config", "remote.origin.promisor", "true")
            git(repo, "config", "remote.origin.url",
                "file:///nonexistent/promisor.git")
    rc, kinds, err = audit(lane, fleet)
    print(f"## arm {arm}")
    print(f"  exit={rc}")
    print(f"  defects={kinds}")
    print(f"  stderr={err!r}")
