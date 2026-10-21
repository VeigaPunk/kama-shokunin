#!/usr/bin/env python3
"""Second probe: fleet-subdir prefix mismatch, safe.directory suppression,
core.worktree, and the rev-parse discriminators for discovery."""
import json
import os
import shutil
import subprocess
import sys

ROOT = "/tmp/kama-r23/ScoutSafeDirectory"
BASE = os.environ.get("AUDIT", os.path.join(ROOT, "base", "report-landing-audit-base.py"))
FX = os.path.join(ROOT, "fx2")
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
        r = doc["results"][0]
        kinds = [(d["kind"], d["token"][:12]) for d in r["defects"]]
        summary = (f"status={s['status']} cutoff={r['cutoff']} "
                   f"required={r['required']} kinds={kinds[:4]}")
    except Exception:
        pass
    err = p.stderr.strip().splitlines()
    err0 = err[0][:200] if err else ""
    print(f"{label}\trc={p.returncode}\t{summary}\tstderr={err0}")
    return p


def show(label, repo, *args):
    p = g(repo, *args)
    print(f"rev\t{label}\t{args}\trc=0\t{p.stdout.strip()!r}")


def main():
    shutil.rmtree(FX, ignore_errors=True)
    os.makedirs(FX)

    lane = os.path.join(FX, "lane")
    init(lane)
    commit(lane, "init", 900, author="someone")
    lane_sha = commit(lane, "round-1: work", 1000, author="kama-shokunin")
    os.makedirs(os.path.join(lane, "sub"))

    # R: root report added at 500, sub/.ufo report added at 1200
    r = os.path.join(FX, "prefixrepo")
    init(r)
    commit(r, "root report", 500, path=REPORT_REL,
           content="## Landed changes\nnone\n", author="kama-shokunin")
    commit(r, "sub report", 1200, path="sub/" + REPORT_REL,
           content="## Landed changes\n- `deadbeef` decoy\n",
           author="kama-shokunin")
    print(f"fixture lane_sha={lane_sha}")
    print("rev\tr-root-cutoff\t" +
          g(r, "log", "--diff-filter=A", "--format=%at", "--",
            REPORT_REL).stdout.strip())
    print("rev\tr-sub-cutoff\t" +
          g(os.path.join(r, "sub"), "log", "--diff-filter=A",
            "--format=%at", "--", REPORT_REL).stdout.strip())
    print("rev\tr-sub-show\t" +
          repr(g(os.path.join(r, "sub"), "show",
                 f"HEAD:{REPORT_REL}").stdout.strip()))

    audit("prefixrepo-root", "--lane-repo", lane, "--fleet-repo", r,
          "--rounds", "1", "--no-errata", "--json")
    audit("prefixrepo-sub", "--lane-repo", lane,
          "--fleet-repo", os.path.join(r, "sub"),
          "--rounds", "1", "--no-errata", "--json")

    # core.worktree in the fleet repo config
    cw = os.path.join(FX, "fleet-cw")
    init(cw)
    commit(cw, "round-1: kama report", 1200, path=REPORT_REL,
           content="## Landed changes\nnone\n", author="kama-shokunin")
    g(cw, "config", "core.worktree", os.path.join(FX, "somewhere-else"))
    audit("fleet-core.worktree", "--lane-repo", lane, "--fleet-repo", cw,
          "--rounds", "1", "--no-errata", "--json")

    # ownership vs a global safe.directory that the audit replaces
    foreign = os.path.join(FX, "foreign")
    init(foreign)
    commit(foreign, "init", 900, author="someone")
    subprocess.run(["sudo", "-n", "chown", "-R", "root:root", foreign],
                   check=True)
    conf = os.path.join(FX, "global.conf")
    with open(conf, "w", encoding="utf-8") as fh:
        fh.write("[safe]\n\tdirectory = *\n")
    p = g(foreign, "rev-parse", "HEAD", env={"GIT_CONFIG_GLOBAL": conf})
    print(f"plain-git-global-safe-directory\trc={p.returncode}\t"
          f"{p.stdout.strip()}")
    audit("foreign-with-global-safe", "--lane-repo", foreign,
          "--fleet-repo", cw, "--rounds", "1", "--no-errata", "--json",
          env_extra={"GIT_CONFIG_GLOBAL": conf})

    # discovery discriminators
    show("lane-root-prefix", lane, "rev-parse", "--show-prefix")
    show("lane-sub-prefix", os.path.join(lane, "sub"), "rev-parse",
         "--show-prefix")
    show("lane-sub-toplevel", os.path.join(lane, "sub"), "rev-parse",
         "--show-toplevel")
    show("lane-sub-gitdir", os.path.join(lane, "sub"), "rev-parse",
         "--absolute-git-dir")

    hijack = os.path.join(FX, "hijack")
    os.makedirs(hijack)
    with open(os.path.join(hijack, ".git"), "w", encoding="utf-8") as fh:
        fh.write(f"gitdir: {os.path.join(r, '.git')}\n")
    show("hijack-prefix", hijack, "rev-parse", "--show-prefix")
    show("hijack-toplevel", hijack, "rev-parse", "--show-toplevel")
    show("hijack-gitdir", hijack, "rev-parse", "--absolute-git-dir")
    print(f"hijack-.git-target={r}/.git")


if __name__ == "__main__":
    main()
