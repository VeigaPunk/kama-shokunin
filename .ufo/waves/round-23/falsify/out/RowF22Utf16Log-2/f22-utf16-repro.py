#!/usr/bin/env python3
"""Hand-built reproducer for grid row F22-utf16-log-cutoff (round 23) and a
near variant on the same channel: repository-local i18n.commitEncoding=UTF-16.

No import of tests/report-audit/repo-state-grid.py: every fixture is created
here with explicit git commands, GIT_CONFIG_GLOBAL=/dev/null and
GIT_CONFIG_NOSYSTEM=1.

Usage:
  python3 f22-utf16-repro.py --lane /tmp/kama-r23w2/<clone>
      [--frozen 4fe9339f8fc3a4a4a479d9c938a850da12f1124d] [--out run.txt]

The audited "current" auditor is <lane>/tools/report-landing-audit.py; the
"frozen" arm is that path's blob at --frozen, extracted with git cat-file.
Exit 0 always; the printed table is the observation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


ISO = ("--no-replace-objects", "--no-lazy-fetch",
       "-c", "i18n.logOutputEncoding=UTF-8", "-c", "log.follow=false",
       "-c", "log.showRoot=true", "-c", "log.showSignature=false",
       "-c", "log.mailmap=false")


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(args)}: "
                           f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout


def init(path):
    g(path.parent, "init", "-q", "-b", "master", str(path))
    return path


def commit(repo, when, msg, author="fixture"):
    g(repo, "add", "-A")
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=f"@{when} +0000",
      GIT_COMMITTER_DATE=f"@{when} +0000")
    return g(repo, "rev-parse", "HEAD").decode().strip()


def run_auditor(auditor, lane, fleet, cwd):
    p = subprocess.run([sys_executable(), str(auditor),
                        "--lane-repo", str(lane), "--fleet-repo", str(fleet),
                        "--json", "--rounds", "1", "--no-errata"],
                       capture_output=True, env=env(), cwd=str(cwd),
                       timeout=60)
    cutoff = kinds = None
    if p.returncode in (0, 1):
        try:
            doc = json.loads(p.stdout)
            r = doc["results"][0]
            cutoff = r["cutoff"]
            kinds = sorted({d["kind"] for d in r["defects"]})
        except (ValueError, KeyError, IndexError):
            kinds = "unparseable"
    return {"exit": p.returncode, "traceback":
            b"Traceback (most recent call last)" in p.stderr,
            "cutoff": cutoff, "kinds": kinds,
            "stderr_tail": p.stderr.decode(errors="replace").strip()[-140:]}


def sys_executable():
    import sys
    return sys.executable


# ---------------------------------------------------------------- F22 shape
def f22_fixture(root):
    """Grid F22 by hand: clean lane + committed fleet report, fleet-local
    i18n.logOutputEncoding=UTF-16."""
    lane, fleet = init(root / "lane"), init(root / "fleet")
    (lane / "f").write_text("w\n")
    lc = commit(lane, 1000, "round-1: work", "kama-shokunin")
    rel = fleet / ".ufo/reports/round-1/kama.md"
    rel.parent.mkdir(parents=True)
    rel.write_text(f"# kama round 1\n\n## Landed changes\n\n- {lc}\n")
    g(fleet, "config", "i18n.logOutputEncoding", "UTF-16")
    commit(fleet, 2000, "round-1: report")
    raw = subprocess.run(["git", "-C", str(fleet), "log", "--diff-filter=A",
                          "--format=%at", "--",
                          ".ufo/reports/round-1/kama.md"],
                         capture_output=True, env=env()).stdout
    return lane, fleet, raw


# ------------------------------------------------- near variant: commitEncoding
def flip_fixture(root, use_cfg):
    """Same history both arms. Report first added at 2000 while the fleet
    repo-local i18n.commitEncoding is UTF-16 (when use_cfg); lane commit
    2500 is authored after the report (post_report); the report is deleted
    at 2900 and identically re-added at 3000."""
    lane, fleet = init(root / "lane"), init(root / "fleet")
    (lane / "f").write_text("w\n")
    lc1 = commit(lane, 1000, "round-1: work", "kama-shokunin")
    report = f"# kama round 1\n\n## Landed changes\n\n- {lc1}\n"
    rel = fleet / ".ufo/reports/round-1/kama.md"
    rel.parent.mkdir(parents=True)
    rel.write_text(report)
    if use_cfg:
        g(fleet, "config", "i18n.commitEncoding", "UTF-16")
    commit(fleet, 2000, "round-1: report")
    (lane / "f").write_text("w\nlater\n")
    lc2 = commit(lane, 2500, "round-1: later", "kama-shokunin")
    g(fleet, "rm", "-q", ".ufo/reports/round-1/kama.md")
    commit(fleet, 2900, "drop report")
    rel.parent.mkdir(parents=True, exist_ok=True)
    rel.write_text(report)
    commit(fleet, 3000, "restore report")
    raw = subprocess.run(["git", "-C", str(fleet), "log",
                          "--diff-filter=A", "--format=%at", "--",
                          ".ufo/reports/round-1/kama.md"],
                         capture_output=True, env=env()).stdout
    iso_out = subprocess.run(["git", *ISO, "-C", str(fleet), "log",
                              "--diff-filter=A", "--format=%at", "--",
                              ".ufo/reports/round-1/kama.md"],
                             capture_output=True, env=env()).stdout
    return lane, fleet, lc2, (raw, iso_out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--frozen", default="4fe9339f8fc3a4a4a479d9c938a850da"
                                       "12f1124d")
    args = ap.parse_args()
    lane_repo = Path(args.lane).resolve()
    current = lane_repo / "tools/report-landing-audit.py"
    with tempfile.TemporaryDirectory(prefix="f22-repro-") as tmp:
        tmp = Path(tmp)
        frozen = tmp / "frozen-audit.py"
        frozen.write_bytes(subprocess.run(
            ["git", "-C", str(lane_repo), "cat-file", "blob",
             f"{args.frozen}:tools/report-landing-audit.py"],
            capture_output=True, check=True).stdout)
        print("lane HEAD:", subprocess.run(
            ["git", "-C", str(lane_repo), "rev-parse", "HEAD"],
            capture_output=True).stdout.decode().strip())
        print("current sha256:", hashlib.sha256(
            current.read_bytes()).hexdigest())
        print("frozen  sha256:", hashlib.sha256(
            frozen.read_bytes()).hexdigest())

        f22 = tmp / "f22"
        f22.mkdir()
        lane, fleet, raw = f22_fixture(f22)
        print("\nF22 premise: fleet i18n.logOutputEncoding=UTF-16 -> "
              "git log --format=%at bytes:", raw)
        for name, aud in (("frozen", frozen), ("current", current)):
            print("F22", name, run_auditor(aud, lane, fleet, f22))

        for label, use_cfg in (("control (no i18n config)", False),
                               ("near variant i18n.commitEncoding=UTF-16",
                                True)):
            root = tmp / ("flip-" + str(use_cfg))
            root.mkdir()
            lane, fleet, lc2, query = flip_fixture(root, use_cfg)
            print(f"\n{label}")
            print("  cutoff query bytes (repo config):", query[0])
            print("  cutoff query bytes (isolated):   ", query[1])
            for name, aud in (("frozen", frozen), ("current", current)):
                print("  ", name, run_auditor(aud, lane, fleet, root))
            print("  lane post-report commit:", lc2)
            shas = subprocess.run(
                ["git", *ISO, "-C", str(fleet), "log", "--diff-filter=A",
                 "--format=%H", "--", ".ufo/reports/round-1/kama.md"],
                capture_output=True, env=env()).stdout.decode().split()
            for sha in shas:
                body = g(fleet, "cat-file", "commit", sha)
                headers = [ln.decode() for ln in body.split(b"\n")
                           if ln.startswith(b"author ")]
                print("   add-record", sha, headers)


if __name__ == "__main__":
    main()
