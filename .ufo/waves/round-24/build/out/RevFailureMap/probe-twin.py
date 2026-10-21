#!/usr/bin/env python3
"""Twin probe: complete local clone vs the same clone carrying promisor metadata.

Both arms contain every object locally. The only difference is that the
second arm's repositories carry `remote.origin.promisor=true` (and, in a third
arm, a `.promisor` pack marker). The report cites the lane commit, so the
correct verdict in every arm is the same substantive verdict.

This is the round-24 acceptance point in executable form:
  arm A (plain)        -> the reference verdict
  arm B (config marker)-> must equal arm A
  arm C (pack marker)  -> must equal arm A

Local, offline, synthetic. No remote, no network, no fetch.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = Path(sys.argv[1] if len(sys.argv) > 1 else
            "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/"
            "report-landing-audit.py")
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull,
       "GIT_CONFIG_NOSYSTEM": "1"}


def git(repo, *args, **kw):
    env = {**ENV, "GIT_AUTHOR_NAME": kw.get("author", "kama-shokunin"),
           "GIT_COMMITTER_NAME": kw.get("author", "kama-shokunin"),
           "GIT_AUTHOR_EMAIL": "a@x", "GIT_COMMITTER_EMAIL": "a@x",
           "GIT_AUTHOR_DATE": kw.get("date", "@1000 +0000"),
           "GIT_COMMITTER_DATE": kw.get("date", "@1000 +0000")}
    return subprocess.run(["git", "-C", str(repo), *args], env=env,
                          capture_output=True, text=True)


def build(root):
    lane, fleet = root / "lane", root / "fleet"
    for repo in (lane, fleet):
        repo.mkdir(parents=True)
        git(repo, "init", "-q", "-b", "master")
    (lane / "f").write_text("work\n", encoding="utf-8")
    git(lane, "add", "f")
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: work")
    sha = git(lane, "rev-parse", "HEAD").stdout.strip()
    rep = fleet / ".ufo/reports/round-1/kama.md"
    rep.parent.mkdir(parents=True)
    rep.write_text(
        "# round 1\n## Work performed\nmeasured\n"
        "## Landed changes\n- `" + sha + "` work\n", encoding="utf-8")
    git(fleet, "add", ".ufo/reports/round-1/kama.md")
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: kama report", date="@1200 +0000")
    return lane, fleet, sha


def audit(lane, fleet):
    p = subprocess.run([sys.executable, str(TOOL), "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1",
                        "--no-errata", "--json"],
                       env=ENV, capture_output=True, text=True)
    doc = None
    if p.returncode in (0, 1):
        try:
            doc = json.loads(p.stdout)
        except json.JSONDecodeError:
            doc = None
    kinds = None
    if doc:
        kinds = sorted((d["kind"], d["token"])
                       for r in doc["results"] for d in r["defects"])
    return p.returncode, kinds, p.stderr.strip()[:200]


root = Path(tempfile.mkdtemp(prefix="rfm-twin-",
                             dir="/fast/scratch/hyaku/kama-r24"))
print(f"# scratch={root}")
print()

arms = {}
for arm in ("A-plain", "B-config-marker", "C-pack-marker",
            "D-extensions-marker"):
    base = root / arm
    base.mkdir()
    lane, fleet, sha = build(base)
    if arm == "B-config-marker":
        for repo in (lane, fleet):
            git(repo, "config", "remote.origin.promisor", "true")
            git(repo, "config", "remote.origin.url",
                "file:///nonexistent/promisor.git")
    if arm == "C-pack-marker":
        for repo in (lane, fleet):
            # a real pack, then a .promisor marker next to it: metadata
            # only, every object itself is present locally
            git(repo, "repack", "-adq")
            packs = list((repo / ".git/objects/pack").glob("*.pack"))
            print(f"  [arm C] {repo.name}: packs={[p.name for p in packs]}")
            for p in packs:
                p.with_suffix(".promisor").write_bytes(b"")
    if arm == "D-extensions-marker":
        for repo in (lane, fleet):
            git(repo, "config", "extensions.partialclone", "blob:none")
    rc, kinds, err = audit(lane, fleet)
    arms[arm] = (rc, kinds)
    print(f"## arm {arm}")
    print(f"  exit={rc}")
    print(f"  defects={kinds}")
    print(f"  stderr={err!r}")
    print()

ref = arms["A-plain"]
print("## comparison with arm A (plain, complete)")
ok = True
for arm, (rc, kinds) in arms.items():
    same = (rc, kinds) == ref
    ok = ok and same
    print(f"  {arm:<18} exit={rc} defects={kinds} -> "
          f"{'SAME as A' if same else 'DIFFERENT from A'}")
print()
print(f"## {sum(1 for a in arms if arms[a] == ref)}/{len(arms)} arms equal the "
      f"plain arm")
print("## required after repair: all four arms equal (no exit2 for metadata "
      "alone)")
shutil.rmtree(root, ignore_errors=True)
sys.exit(0 if ok else 1)
