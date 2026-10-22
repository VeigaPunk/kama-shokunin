#!/usr/bin/env python3
"""End-to-end fixture for the cross-store order regression of lookup().

Same report text, same blob object in the SAME physical repository; only the
store order (run(): stores = (lane, fleet)) differs.

  repoX : holds the round-1 lane commit, the report file and the cited blob
  repoY : holds the report file only (no lane commit, no blob)

  arm 1: --lane-repo repoX --fleet-repo repoY   -> blob is in the FIRST store
  arm 2: --lane-repo repoY --fleet-repo repoX   -> blob is in the SECOND store

Offline only: no remote, no network, no promisor, no execution payload.
"""
import os
import subprocess
import sys
from pathlib import Path

TOOL = Path(sys.argv[1]).resolve()
ROOT = Path(sys.argv[2]).resolve()
os.environ["TMPDIR"] = str(ROOT)

GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch",
                 "-c", "i18n.logOutputEncoding=UTF-8",
                 "-c", "log.follow=false", "-c", "log.showRoot=true",
                 "-c", "log.showSignature=false", "-c", "log.mailmap=false")


def git(repo, *args, input=None, env=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    env.update(env or {})
    p = subprocess.run(["git", *GIT_ISOLATION, "-C", str(repo), *args],
                       capture_output=True, env=env, text=True, input=input)
    if p.returncode != 0:
        raise SystemExit(f"git {args} failed: {p.stderr}")
    return p.stdout


def commit(repo, msg, author, when, path=None, content=None):
    env = {"GIT_AUTHOR_NAME": author, "GIT_AUTHOR_EMAIL": "a@x",
           "GIT_COMMITTER_NAME": author, "GIT_COMMITTER_EMAIL": "a@x",
           "GIT_AUTHOR_DATE": f"@{when} +0000",
           "GIT_COMMITTER_DATE": f"@{when} +0000"}
    if path:
        target = Path(repo) / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        git(repo, "add", path, env=env)
    p = subprocess.run(["git", *GIT_ISOLATION, "-C", str(repo),
                        "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg],
                       capture_output=True, env={**env,
                                                  "GIT_CONFIG_GLOBAL": os.devnull,
                                                  "GIT_CONFIG_NOSYSTEM": "1"},
                       text=True)
    if p.returncode != 0:
        raise SystemExit(f"commit failed: {p.stderr}")
    return git(repo, "rev-parse", "HEAD").strip()


X = ROOT / "repoX"
Y = ROOT / "repoY"
for repo in (X, Y):
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, "init", "-q", "-b", "master")
    git(repo, "config", "user.email", "a@x")
    git(repo, "config", "user.name", "a")

# the cited blob: a known-present non-commit object, held by repoX only
blob = git(X, "hash-object", "-w", "--stdin", input="cited blob\n").strip()
lane_commit = commit(X, "round-1: work", "kama-shokunin", 1000, "f",
                     "work\n")
report = ("# round 1\n## Work performed\n"
          f"measured the blob {blob}\n"
          "## Landed changes\n"
          f"- `{lane_commit}` lane commit\n"
          f"- `{blob}` cited blob\n")
rel = ".ufo/reports/round-1/kama.md"
commit(X, f"add {rel}", "fleet-bot", 2000, rel, report)
commit(Y, f"add {rel}", "fleet-bot", 2000, rel, report)

print(f"lane_commit={lane_commit}")
print(f"blob={blob} (present in repoX only)")
print(f"report sha in repoX={git(X, 'rev-parse', 'HEAD').strip()}")

for label, lane, fleet in (("arm1 blob in FIRST store (lane=repoX)",
                            X, Y),
                           ("arm2 blob in SECOND store (lane=repoY)",
                            Y, X)):
    cmd = [sys.executable, str(TOOL), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--lane", "kama",
           "--rounds", "1", "--no-errata", "--json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    print(f"\n--- {label}")
    print(f"    cmd: {' '.join(cmd)}")
    print(f"    exit={proc.returncode}")
    print("    stdout: " + (proc.stdout.strip() or "<empty>"))
    print("    stderr: " + (proc.stderr.strip() or "<empty>"))

# errata path: the same correction token is looked up with peel "^{commit}"
errata = ROOT / "errata.tsv"
errata.write_text(f"1\tlanded-unresolved\t{blob}\t{blob}\tevidence\n")
print(f"\n=== errata arm (correction = the blob, {errata}) ===")
for label, lane, fleet in (("arm1 blob in FIRST store", X, Y),
                           ("arm2 blob in SECOND store", Y, X)):
    cmd = [sys.executable, str(TOOL), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--lane", "kama",
           "--rounds", "1", "--errata", str(errata)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    print(f"\n--- {label}")
    print(f"    cmd: {' '.join(cmd)}")
    print(f"    exit={proc.returncode}")
    print("    stdout: " + (proc.stdout.strip() or "<empty>"))
    print("    stderr: " + (proc.stderr.strip() or "<empty>"))

# errata path in isolation: the report does NOT cite the blob, only the
# errata correction names it
draft = ROOT / "draft-no-blob.md"
draft.write_text("# round 1\n## Work performed\nnothing else\n"
                 "## Landed changes\n"
                 f"- `{lane_commit}` lane commit\n")
errata2 = ROOT / "errata2.tsv"
errata2.write_text(f"1\tunresolved-full-hash\tdeadbee1\t{blob}\tevidence\n")
print("\n=== errata-only arm (draft without the blob, correction = the blob) ===")
for label, lane, fleet in (("arm1 blob in FIRST store", X, Y),
                           ("arm2 blob in SECOND store", Y, X)):
    cmd = [sys.executable, str(TOOL), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--lane", "kama",
           "--rounds", "1", "--report", f"1={draft}",
           "--errata", str(errata2)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    print(f"\n--- {label}")
    print(f"    cmd: {' '.join(cmd)}")
    print(f"    exit={proc.returncode}")
    print("    stdout: " + (proc.stdout.strip() or "<empty>"))
    print("    stderr: " + (proc.stderr.strip() or "<empty>"))
