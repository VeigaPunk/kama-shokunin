#!/usr/bin/env python3
"""Proof driver for the six consumer regressions of the r24 C1 repair.

Runs each scenario against three versions of tools/report-landing-audit.py at
the CLI level (subprocess, exit code and stderr line), all offline and in
temporary directories:

  before-pinned   the production file the falsifiers read (lane 2e254a1)
  before-ca162    the producer version filed in this directory
  after-v3        this proposal

Usage: python3 proof-driver.py [--only N] [--json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERSIONS = {
    "before-pinned": Path("/home/vgpnk/Projects/shokunin/kama-shokunin/"
                          "tools/report-landing-audit.py"),
    "before-ca162": HERE / "report-landing-audit.py",
    "after-v3": HERE / "report-landing-audit-v3.py",
    "after-v4": HERE / "report-landing-audit-v4.py",
}


def git(repo, *args, stdin=None):
    env = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "kama-shokunin", "GIT_COMMITTER_NAME":
           "kama-shokunin", "GIT_AUTHOR_EMAIL": "a@x", "GIT_COMMITTER_EMAIL":
           "a@x", "PATH": "/usr/bin:/bin"}
    out = subprocess.run(["git", "-C", str(repo), *args],
                         input=None if stdin is None else stdin.encode(),
                         capture_output=True, env=env, timeout=30)
    if out.returncode != 0:
        raise SystemExit(f"git {args} in {repo}: "
                         f"{out.stderr.decode('utf-8', 'replace')}")
    return out.stdout.decode("utf-8", "replace")


def scenario(tmp, name):
    """Build one offline fixture; return (lane, fleet, report path, errata)."""
    lane, fleet = Path(tmp, "lane"), Path(tmp, "fleet")
    for repo in (lane, fleet):
        repo.mkdir()
        git(repo, "init", "-q", "-b", "master")
    a = git(lane, "rev-parse", "HEAD").strip() if False else None
    Path(lane, "f").write_text("work\n", encoding="utf-8")
    git(lane, "add", "f")
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: work")
    a = git(lane, "rev-parse", "HEAD").strip()
    report = fleet / ".ufo/reports/round-1/kama.md"
    report.parent.mkdir(parents=True)
    report.write_text("## Landed changes\n", encoding="utf-8")
    git(fleet, "add", ".ufo/reports/round-1/kama.md")
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: kama report")
    draft = Path(tmp, "draft.md")
    errata = None

    def obj(repo, oid):
        path = Path(repo, git(repo, "rev-parse", "--git-path",
                              "objects").strip(), oid[:2], oid[2:])
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    if name == "fleet-only-blob":
        blob = git(fleet, "hash-object", "-w", "--stdin",
                   stdin="fleet only blob\n").strip()
        draft.write_text("## Landed changes\n- `" + blob + "` blob\n",
                         encoding="utf-8")
    elif name == "fleet-only-tree":
        blob = git(fleet, "hash-object", "-w", "--stdin",
                   stdin="fleet only blob\n").strip()
        tree = git(fleet, "mktree",
                   stdin=f"100644 blob {blob}\tf\n").strip()
        draft.write_text("## Landed changes\n- `" + tree + "` tree\n",
                         encoding="utf-8")
    elif name == "fleet-only-tag":
        target = git(fleet, "hash-object", "-w", "--stdin",
                     stdin="fleet tag target\n").strip()
        tag = git(fleet, "mktag", stdin=f"object {target}\ntype blob\ntag t\n"
                                      f"tagger k <a@x> 1000 +0000\n\ntag\n"
                   ).strip()
        draft.write_text("## Landed changes\n- `" + tag + "` tag\n",
                         encoding="utf-8")
    elif name == "errata-fleet-only-blob":
        blob = git(fleet, "hash-object", "-w", "--stdin",
                   stdin="fleet only blob\n").strip()
        draft.write_text("## Landed changes\n- `" + blob + "` blob\n",
                         encoding="utf-8")
        errata = Path(tmp, "errata.tsv")
        errata.write_text(f"1\tlanded-unresolved\t{blob}\t{blob}\tev\n",
                          encoding="utf-8")
    elif name == "same-tag-both-stores":
        # the same tag object in both repositories; its target blob is
        # observable in the fleet only, so the lane cannot serve it
        target = git(fleet, "hash-object", "-w", "--stdin",
                     stdin="tag target\n").strip()
        tag = git(fleet, "mktag", stdin=f"object {target}\ntype blob\ntag t\n"
                                      f"tagger k <a@x> 1000 +0000\n\ntag\n"
                   ).strip()
        obj(lane, tag).write_bytes(obj(fleet, tag).read_bytes())
        draft.write_text("## Landed changes\n- `" + tag + "` tag\n",
                         encoding="utf-8")
    elif name == "unselected-invalid-correction":
        draft.write_text("## Landed changes\n- `" + a + "` work\n",
                         encoding="utf-8")
        errata = Path(tmp, "errata.tsv")
        errata.write_text("2\tunresolved-full-hash\t" + "0" * 40 + "\t"
                          + "0" * 40 + "\tev\n", encoding="utf-8")
    else:
        raise SystemExit(f"unknown scenario {name}")
    return lane, fleet, draft, errata


SCENARIOS = ["fleet-only-blob", "fleet-only-tree", "fleet-only-tag",
             "errata-fleet-only-blob", "same-tag-both-stores",
             "unselected-invalid-correction"]


def run_version(version, lane, fleet, draft, errata):
    cmd = [sys.executable, str(version), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--rounds", "1",
           "--report", f"1={draft}", "--json"]
    if errata is not None:
        cmd += ["--errata", str(errata)]
    else:
        cmd += ["--no-errata"]
    proc = subprocess.run(cmd, capture_output=True, timeout=60)
    kinds = []
    if proc.returncode == 1:
        try:
            doc = json.loads(proc.stdout.decode("utf-8", "replace"))
            kinds = sorted({d["kind"] for res in doc["results"]
                            for d in res["defects"]})
        except Exception:
            kinds = ["?"]
    reason = ""
    if proc.returncode == 2:
        reason = proc.stderr.decode("utf-8", "replace").strip().splitlines()
        reason = reason[-1][:110] if reason else ""
    return proc.returncode, kinds, reason


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    names = [args.only] if args.only else SCENARIOS
    rows = []
    for name in names:
        with tempfile.TemporaryDirectory(prefix="proof-") as tmp:
            lane, fleet, draft, errata = scenario(tmp, name)
            row = {"scenario": name}
            for label, version in VERSIONS.items():
                code, kinds, reason = run_version(version, lane, fleet,
                                                  draft, errata)
                row[label] = {"exit": code, "kinds": kinds, "reason": reason}
            rows.append(row)
    if args.json:
        print(json.dumps(rows, indent=1, sort_keys=True))
        return 0
    for row in rows:
        print(f"{row['scenario']}")
        for label in VERSIONS:
            cell = row[label]
            print(f"  {label:14s} exit={cell['exit']} kinds={cell['kinds']}"
                  f" {cell['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
