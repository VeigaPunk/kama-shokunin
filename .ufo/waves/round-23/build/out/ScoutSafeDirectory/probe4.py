#!/usr/bin/env python3
"""Fourth probe: non-repo sentinels, GIT_CEILING_DIRECTORIES suppression,
symlinks, and an empty .git directory."""
import json
import os
import shutil
import subprocess
import sys

ROOT = "/tmp/kama-r23/ScoutSafeDirectory"
BASE = os.environ.get("AUDIT", os.path.join(ROOT, "base", "report-landing-audit-base.py"))
FX = os.path.join(ROOT, "fx4")
REPORT_REL = ".ufo/reports/round-1/kama.md"

CLEAN = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
CLEAN.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
IDENT = {"GIT_AUTHOR_NAME": "x", "GIT_AUTHOR_EMAIL": "a@x",
         "GIT_COMMITTER_NAME": "x", "GIT_COMMITTER_EMAIL": "a@x"}


def g(repo, *args, env=None, check=True):
    e = dict(CLEAN)
    e.update(env or {})
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True,
                       text=True, env=e)
    if check and p.returncode:
        raise RuntimeError((repo, args, p.returncode, p.stderr))
    return p


def init(path):
    os.makedirs(path)
    g(path, "init", "-q", "-b", "master")


def commit(repo, msg, when, path="f", content=None, author="x"):
    env = dict(IDENT)
    env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = author
    env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"@{when} +0000"
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
    summary = ""
    try:
        doc = json.loads(p.stdout)
        s = doc["summary"]
        summary = f"status={s['status']} defects={s['defects']}"
    except Exception:
        pass
    err = p.stderr.strip().splitlines()
    err0 = err[0][:170] if err else ""
    print(f"{label}\trc={p.returncode}\t{summary}\tstderr={err0}")


def main():
    shutil.rmtree(FX, ignore_errors=True)
    os.makedirs(FX)

    lane = os.path.join(FX, "lane")
    init(lane)
    commit(lane, "init", 900, author="someone")
    commit(lane, "round-1: work", 1000, author="kama-shokunin")

    fleet = os.path.join(FX, "fleet")
    init(fleet)
    commit(fleet, "round-1: kama report", 1200, path=REPORT_REL,
           content="## Landed changes\nnone\n", author="kama-shokunin")

    enclosing = os.path.join(FX, "enclosing")
    init(enclosing)
    commit(enclosing, "init", 900, author="someone")
    os.makedirs(os.path.join(enclosing, "sub"))

    emptygit = os.path.join(FX, "emptygit")
    os.makedirs(os.path.join(emptygit, ".git"))

    symlink = os.path.join(FX, "link")
    os.symlink(os.path.join(enclosing, "sub"), symlink)

    audit("nonexistent-lane", "--lane-repo", os.path.join(FX, "does-not-exist"),
          "--fleet-repo", fleet, "--rounds", "1", "--no-errata", "--json")
    audit("empty-dotgit-lane", "--lane-repo", emptygit,
          "--fleet-repo", fleet, "--rounds", "1", "--no-errata", "--json")
    audit("symlink-nested-lane", "--lane-repo", symlink, "--fleet-repo",
          fleet, "--rounds", "1", "--no-errata", "--json")
    audit("nested-lane-ceiling-ignored", "--lane-repo",
          os.path.join(enclosing, "sub"), "--fleet-repo", fleet,
          "--rounds", "1", "--no-errata", "--json",
          env_extra={"GIT_CEILING_DIRECTORIES": enclosing})
    p = g(os.path.join(enclosing, "sub"), "rev-parse", "HEAD",
          env={"GIT_CEILING_DIRECTORIES": enclosing}, check=False)
    print(f"direct-git-ceiling\trc={p.returncode}\t"
          f"stderr={p.stderr.strip().splitlines()[0] if p.stderr else ''}")


if __name__ == "__main__":
    main()
