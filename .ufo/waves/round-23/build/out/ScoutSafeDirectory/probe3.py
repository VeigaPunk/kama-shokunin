#!/usr/bin/env python3
"""Third probe: does a `.git` gitfile redirect turn a failed lane into a clean
one (GIT_DIR discovery), and is a subdir path distinguishable from the root?"""
import json
import os
import shutil
import subprocess
import sys

ROOT = "/tmp/kama-r23/ScoutSafeDirectory"
BASE = os.environ.get("AUDIT", os.path.join(ROOT, "base", "report-landing-audit-base.py"))
FX = os.path.join(ROOT, "fx3")
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


def audit(label, *args):
    p = subprocess.run([sys.executable, BASE, *args], capture_output=True,
                       text=True, env=dict(CLEAN), cwd=ROOT)
    summary = ""
    try:
        doc = json.loads(p.stdout)
        s = doc["summary"]
        r = doc["results"][0]
        kinds = [(d["kind"], d["token"][:12]) for d in r["defects"]]
        summary = (f"status={s['status']} cutoff={r['cutoff']} "
                   f"required={r['required']} kinds={kinds[:4]}")
    except Exception as exc:
        summary = f"parse={exc!r} stdout={p.stdout[:80]!r}"
    err = p.stderr.strip().splitlines()
    err0 = err[0][:180] if err else ""
    print(f"{label}\trc={p.returncode}\t{summary}\tstderr={err0}")
    return p.returncode, p.stdout


def main():
    shutil.rmtree(FX, ignore_errors=True)
    os.makedirs(FX)

    lane = os.path.join(FX, "lane")
    init(lane)
    commit(lane, "init", 900, author="someone")
    lane_sha = commit(lane, "round-1: work", 1000, author="kama-shokunin")

    decoy = os.path.join(FX, "decoy")
    init(decoy)
    commit(decoy, "init", 900, author="someone")
    decoy_sha = commit(decoy, "round-1: decoy work", 1000,
                       author="kama-shokunin")

    fleet = os.path.join(FX, "fleet")
    init(fleet)
    commit(fleet, "round-1: kama report", 1200, path=REPORT_REL,
           content=("## Landed changes\n- `" + decoy_sha[:9] + "` decoy\n"),
           author="kama-shokunin")

    print(f"lane_sha={lane_sha} decoy_sha={decoy_sha}")

    hijack = os.path.join(FX, "hijack")
    os.makedirs(hijack)
    with open(os.path.join(hijack, ".git"), "w", encoding="utf-8") as fh:
        fh.write(f"gitdir: {os.path.join(decoy, '.git')}\n")

    # the lane root itself with only its .git replaced by a gitfile
    landup = os.path.join(FX, "lane-gitfile")
    shutil.copytree(lane, landup)
    shutil.move(os.path.join(landup, ".git"), os.path.join(FX, "lane-gitdir"))
    with open(os.path.join(landup, ".git"), "w", encoding="utf-8") as fh:
        fh.write(f"gitdir: {os.path.join(decoy, '.git')}\n")

    audit("lane-root", "--lane-repo", lane, "--fleet-repo", fleet,
          "--rounds", "1", "--no-errata", "--json")
    audit("decoy-root", "--lane-repo", decoy, "--fleet-repo", fleet,
          "--rounds", "1", "--no-errata", "--json")
    audit("hijack-gitfile", "--lane-repo", hijack, "--fleet-repo", fleet,
          "--rounds", "1", "--no-errata", "--json")
    audit("lane-gitfile-swap", "--lane-repo", landup, "--fleet-repo", fleet,
          "--rounds", "1", "--no-errata", "--json")


if __name__ == "__main__":
    main()
