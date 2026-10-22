#!/usr/bin/env python3
"""PG48 sensitivity control: the complement of PG48.

PG48 drops an UNUSED subtree ("d/") and expects exit 0.  The complement
drops the subtree that a required read actually needs ("corpus/", which
holds corpus/SOURCES.md) and must produce a content-derived could-not-
evaluate (exit 2) that names the missing object -- proving PG48's exit 0
is a consequence of the hole being unused, not of the auditor ignoring
missing trees generally.

Also: exact transport-verb filter over the PG48 git trace.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/repo")
AUDIT = REPO / "tools/report-landing-audit.py"
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/sens-root")
REL = ".ufo/reports/round-1/kama.md"


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    e.update(extra)
    return e


def git(repo, *args, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=env(**extra))
    if check and p.returncode:
        raise SystemExit(f"git {args}: {p.stderr.decode()}")
    return p.stdout.decode()


def git_dir(repo):
    return Path(git(repo, "rev-parse", "--absolute-git-dir").strip())


def drop(repo, sha):
    obj = git_dir(repo) / "objects" / sha[:2] / sha[2:]
    obj.unlink()
    return sha


def build(root, drop_corpus):
    shutil.rmtree(root, ignore_errors=True)
    lane = root / "lane"
    fleet = root / "fleet"
    lane.mkdir(parents=True)
    fleet.mkdir(parents=True)
    git(lane.parent, "init", "-q", "-b", "master", str(lane))
    git(fleet.parent, "init", "-q", "-b", "master", str(fleet))
    (lane / "corpus").mkdir()
    (lane / "corpus" / "SOURCES.md").write_text("# sources\n\nfixture: none\n")
    (lane / "f").write_text("fixture file\n")
    git(lane, "add", "--", "corpus/SOURCES.md", "f")
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: work", GIT_AUTHOR_NAME="kama-shokunin",
        GIT_COMMITTER_NAME="kama-shokunin", GIT_AUTHOR_DATE="@1000 +0000",
        GIT_COMMITTER_DATE="@1000 +0000")
    l1 = git(lane, "rev-parse", "HEAD").strip()
    # promisor metadata on the lane (same as the graded PG48 fixture)
    git(lane, "config", "remote.origin.promisor", "true")
    git(lane, "config", "extensions.partialclone", "origin")
    git(lane, "config", "remote.origin.url", str(root / "absent-remote.git"))
    dropped = None
    if drop_corpus:
        dropped = drop(lane, git(lane, "rev-parse", f"{l1}:corpus").strip())
    text = (f"# kama round 1\n\n## Landed changes\n\n- {l1}\n")
    (fleet / ".ufo" / "reports" / "round-1").mkdir(parents=True)
    (fleet / REL).write_text(text)
    git(fleet, "add", "--", REL)
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: report", GIT_AUTHOR_NAME="fleet",
        GIT_COMMITTER_NAME="fleet", GIT_AUTHOR_DATE="@2000 +0000",
        GIT_COMMITTER_DATE="@2000 +0000")
    return lane, fleet, l1, dropped


def run(lane, fleet, root):
    p = subprocess.run([sys.executable, str(AUDIT), "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1", "--json",
                        "--no-errata"], capture_output=True, env=env(),
                       cwd=str(root), timeout=60)
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


out = {}

# --- complement: the required subtree is the missing one
lane, fleet, l1, dropped = build(ROOT / "req", drop_corpus=True)
code, so, se = run(lane, fleet, ROOT / "req")
out["required_hole"] = {
    "missing_corpus_tree": dropped,
    "exit": code,
    "stderr": se.strip()[:600],
    "stdout_is_json": so.strip().startswith("{"),
    "reason_names_missing_tree": bool(dropped) and dropped in se,
    "reason_is_metadata_refusal": ("partial clone (" in se
                                   or "promisor pack" in se),
    "reason_class_unavailable": any(t in se.lower() for t in
                                    ("missing", "unavailable", "not available")),
}

# --- control: same fixture with nothing dropped
lane2, fleet2, l12, _ = build(ROOT / "ok", drop_corpus=False)
code2, so2, se2 = run(lane2, fleet2, ROOT / "ok")
out["no_hole_control"] = {
    "exit": code2,
    "stderr": se2.strip()[:300],
    "stdout_is_json": so2.strip().startswith("{"),
    "summary": (json.loads(so2)["summary"] if so2.strip().startswith("{")
                else None),
}

# --- transport-verb filter over the recorded PG48 trace
trace = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/"
             "ctrl-root/shim/git-calls.log")
verbs = ("fetch", "pull", "clone", "remote", "upload-pack", "ls-remote",
         "http", "ssh")
if trace.exists():
    calls = [c for c in trace.read_text(errors="replace").split("\n") if c]
    hits = []
    for c in calls:
        toks = c.split()
        for v in verbs:
            if v in toks:
                hits.append((v, c[:120]))
    out["transport_verb_hits"] = hits
    out["total_git_calls"] = len(calls)
else:
    out["transport_verb_hits"] = "trace file absent"

print(json.dumps(out, indent=1))
