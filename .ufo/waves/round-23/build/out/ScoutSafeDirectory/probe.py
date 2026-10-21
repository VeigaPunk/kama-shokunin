#!/usr/bin/env python3
"""Probe repo-local discovery/ownership channels of report-landing-audit.py at base.

All fixtures are fresh repos under /tmp with GIT_CONFIG_GLOBAL=/dev/null and
GIT_CONFIG_NOSYSTEM=1. No fixture points at a network host.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = "/tmp/kama-r23/ScoutSafeDirectory"
BASE = os.environ.get("AUDIT", os.path.join(ROOT, "base", "report-landing-audit-base.py"))
FX = os.path.join(ROOT, "fx")
REPORT_REL = ".ufo/reports/round-1/kama.md"

CLEAN = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
CLEAN.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
IDENT = {"GIT_AUTHOR_NAME": "x", "GIT_AUTHOR_EMAIL": "a@x",
         "GIT_COMMITTER_NAME": "x", "GIT_COMMITTER_EMAIL": "a@x"}


def g(repo, *args, env=None, stdin=None, check=True):
    e = dict(CLEAN)
    e.update(env or {})
    p = subprocess.run(["git", "-C", repo, *args], input=stdin,
                       capture_output=True, text=True, env=e)
    if check and p.returncode:
        raise RuntimeError((repo, args, p.returncode, p.stderr))
    return p


def init(path):
    os.makedirs(path)
    g(path, "init", "-q", "-b", "master")


def commit(repo, msg, when, path="f", content=None, author="x",
           committed=None):
    env = dict(IDENT)
    env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = author
    env["GIT_AUTHOR_DATE"] = f"@{when} +0000"
    env["GIT_COMMITTER_DATE"] = f"@{committed or when} +0000"
    full = os.path.join(repo, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content if content is not None else msg + "\n")
    g(repo, "add", "--", path)
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg, env=env)
    return g(repo, "rev-parse", "HEAD").stdout.strip()


def audit(label, *args, env_extra=None):
    e = dict(CLEAN)
    e.update(env_extra or {})
    p = subprocess.run([sys.executable, BASE, *args], capture_output=True,
                       text=True, env=e, cwd=ROOT)
    doc = None
    summary = ""
    try:
        doc = json.loads(p.stdout)
        s = doc["summary"]
        summary = (f"status={s['status']} defects={s['defects']} "
                   f"required={s['required_commits']}")
        kinds = [(d["kind"], d["token"][:12])
                 for r in doc["results"] for d in r["defects"]]
        if kinds:
            summary += " kinds=" + repr(kinds[:6])
    except Exception:
        pass
    err = p.stderr.strip().splitlines()
    err0 = err[0][:220] if err else ""
    print(f"{label}\trc={p.returncode}\t{summary}\tstderr={err0}")
    return p.returncode, doc, p.stderr


def tree_state(path):
    h = hashlib.sha256()
    for dirpath, dirnames, filenames in sorted(os.walk(path)):
        dirnames.sort()
        for name in sorted(filenames):
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, path)
            st = os.stat(full)
            h.update(f"{rel}:{st.st_size}:{st.st_mtime_ns}\n".encode())
    return h.hexdigest()[:16]


def main():
    shutil.rmtree(FX, ignore_errors=True)
    os.makedirs(FX)

    lane = os.path.join(FX, "lane")
    init(lane)
    commit(lane, "init", 900, author="someone")
    lane_sha = commit(lane, "round-1: work", 1000, author="kama-shokunin")

    fleet = os.path.join(FX, "fleet")
    init(fleet)
    commit(fleet, "round-1: kama report", 1200, path=REPORT_REL,
           content="## Landed changes\nnone\n", author="kama-shokunin")

    decoy = os.path.join(FX, "decoy")
    init(decoy)
    commit(decoy, "init", 900, author="someone")
    d_sha = commit(decoy, "round-1: decoy work", 1000,
                   author="kama-shokunin")
    # decoy report cites the REAL lane commit, so it is clean when read from
    # the decoy while the real fleet report is not.
    commit(decoy, "round-1: decoy report", 1200, path=REPORT_REL,
           content=("## Work performed\nat " + lane_sha +
                    "\n## Landed changes\n- `" + lane_sha[:9] + "` work\n"),
           author="kama-shokunin")
    # a plain, not-a-repo subdirectory of the decoy worktree
    decoy_sub = os.path.join(decoy, "sub")
    os.makedirs(decoy_sub)

    enclosing = os.path.join(FX, "enclosing")
    init(enclosing)
    commit(enclosing, "init", 900, author="someone")
    enc_sub = os.path.join(enclosing, "sub")
    os.makedirs(enc_sub)

    plain = os.path.join(FX, "plain")
    os.makedirs(plain)

    hijack = os.path.join(FX, "hijack")
    os.makedirs(hijack)
    with open(os.path.join(hijack, ".git"), "w", encoding="utf-8") as fh:
        fh.write(f"gitdir: {os.path.join(decoy, '.git')}\n")

    print(f"fixture lane_sha={lane_sha} decoy_sha={d_sha}")

    # ---- controls: real repo roots
    audit("control-lane-fleet", "--lane-repo", lane, "--fleet-repo", fleet,
          "--rounds", "1", "--no-errata", "--json")
    audit("control-decoy-fleet", "--lane-repo", lane, "--fleet-repo", decoy,
          "--rounds", "1", "--no-errata", "--json")

    # ---- not-a-repo paths
    audit("plain-dir-lane", "--lane-repo", plain, "--fleet-repo", fleet,
          "--rounds", "1", "--no-errata", "--json")
    audit("plain-dir-fleet", "--lane-repo", lane, "--fleet-repo", plain,
          "--rounds", "1", "--no-errata", "--json")
    audit("nested-dir-lane", "--lane-repo", enc_sub, "--fleet-repo", fleet,
          "--rounds", "1", "--no-errata", "--json")
    audit("nested-dir-fleet", "--lane-repo", lane, "--fleet-repo", decoy_sub,
          "--rounds", "1", "--no-errata", "--json")
    audit("dotgit-file-lane", "--lane-repo", hijack, "--fleet-repo", fleet,
          "--rounds", "1", "--no-errata", "--json")
    audit("file-as-lane", "--lane-repo", os.path.join(lane, "f"),
          "--fleet-repo", fleet, "--rounds", "1", "--no-errata", "--json")

    # ---- environment GIT_DIR / GIT_WORK_TREE injection
    decoy_before = tree_state(os.path.join(decoy, ".git", "objects"))
    audit("env-GIT_DIR-decoy", "--lane-repo", lane, "--fleet-repo", fleet,
          "--rounds", "1", "--no-errata", "--json",
          env_extra={"GIT_DIR": os.path.join(decoy, ".git"),
                     "GIT_WORK_TREE": decoy})
    audit("env-GIT_DIR-missing", "--lane-repo", lane, "--fleet-repo", fleet,
          "--rounds", "1", "--no-errata", "--json",
          env_extra={"GIT_DIR": os.path.join(FX, "missing.git"),
                     "GIT_WORK_TREE": os.path.join(FX, "missing")})
    audit("env-config-injection", "--lane-repo", lane, "--fleet-repo", fleet,
          "--rounds", "1", "--no-errata", "--json",
          env_extra={"GIT_CONFIG_COUNT": "1",
                     "GIT_CONFIG_KEY_0": "core.repositoryFormatVersion",
                     "GIT_CONFIG_VALUE_0": "99",
                     "GIT_CEILING_DIRECTORIES": plain})
    decoy_after = tree_state(os.path.join(decoy, ".git", "objects"))
    print(f"decoy-objects-unchanged={decoy_before == decoy_after}")

    # ---- foreign ownership
    foreign = os.path.join(FX, "foreign")
    init(foreign)
    commit(foreign, "init", 900, author="someone")
    commit(foreign, "round-1: foreign work", 1000, author="kama-shokunin")
    g(foreign, "config", "safe.directory", "*")  # repo-local self-whitelist
    subprocess.run(["sudo", "-n", "chown", "-R", "root:root", foreign],
                   check=True)
    audit("foreign-lane", "--lane-repo", foreign, "--fleet-repo", fleet,
          "--rounds", "1", "--no-errata", "--json")

    foreign_fleet = os.path.join(FX, "foreign_fleet")
    shutil.copytree(fleet, foreign_fleet)
    subprocess.run(["sudo", "-n", "chown", "-R", "root:root", foreign_fleet],
                   check=True)
    audit("foreign-fleet", "--lane-repo", lane, "--fleet-repo",
          foreign_fleet, "--rounds", "1", "--no-errata", "--json")

    # nested path inside a foreign repo: discovery finds the foreign root
    foreign_sub = os.path.join(foreign, "sub")
    subprocess.run(["sudo", "-n", "mkdir", "-p", foreign_sub], check=True)
    audit("foreign-nested-lane", "--lane-repo", foreign_sub,
          "--fleet-repo", fleet, "--rounds", "1", "--no-errata", "--json")

    # isolate which directory's owner git checks
    wt = os.path.join(FX, "worktree-own")
    init(wt)
    commit(wt, "init", 900, author="someone")
    subprocess.run(["sudo", "-n", "chown", "root:root", wt], check=True)
    audit("worktree-dir-root-owned", "--lane-repo", wt, "--fleet-repo", fleet,
          "--rounds", "1", "--no-errata", "--json")

    gitd = os.path.join(FX, "gitdir-own")
    init(gitd)
    commit(gitd, "init", 900, author="someone")
    subprocess.run(["sudo", "-n", "chown", "-R", "root:root",
                    os.path.join(gitd, ".git")], check=True)
    audit("gitdir-root-owned", "--lane-repo", gitd, "--fleet-repo", fleet,
          "--rounds", "1", "--no-errata", "--json")


if __name__ == "__main__":
    main()
