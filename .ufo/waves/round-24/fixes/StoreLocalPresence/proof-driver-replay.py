#!/usr/bin/env python3
"""Replay driver for the six consumer regressions, with a PINNED before.

The "before" side is extracted exactly from the pinned lane revision
2e254a17 (git 2e254a17:tools/report-landing-audit.py) with the auditor's own
isolation (--no-replace-objects --no-lazy-fetch) and its bytes are checked
against the known baseline sha256 before they are written to a temporary
file. The mutable production file is never read as the before side.

The lane repository root is derived from this file's location
(.ufo/waves/round-24/fixes/StoreLocalPresence/), not from a host path.

The "after" side is the tool to bind: --after PATH, by default the v4
proposal next to this driver.

Exit convention: 0 = the measurement completed (the JSON carries the
comparison with the independent expectation), 2 = an input error (a bad
option, an unreadable --after, a baseline that does not match). The driver
makes no admission claim: it measures.

Usage: python3 proof-driver-replay.py [--after PATH] [--only NAME] [--text]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
# .ufo/waves/round-24/fixes/StoreLocalPresence/ -> the lane repository root
LANE_ROOT = HERE.parents[4]
PINNED_COMMIT = "2e254a17"
PINNED_PATH = "tools/report-landing-audit.py"
BASELINE_SHA256 = "ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220"
DEFAULT_AFTER = HERE / "report-landing-audit-v6.py"

# the independent expectation per consumer (the contract, not the tool's say)
EXPECTED = {
    "fleet-only-blob": {"exit": 1, "kinds": ["landed-unresolved"]},
    "fleet-only-tree": {"exit": 1, "kinds": ["landed-unresolved"]},
    "fleet-only-tag": {"exit": 1, "kinds": ["landed-unresolved"]},
    "errata-fleet-only-blob": {"exit": 1, "kinds": ["landed-unresolved"],
                               "errata_invalid": 1},
    "same-tag-both-stores": {"exit": 1, "kinds": ["landed-unresolved"]},
    "unselected-invalid-correction": {"exit": 0, "kinds": []},
}
SCENARIOS = list(EXPECTED)


class InputError(Exception):
    """A bad input: the driver cannot measure."""


def git(repo, *args, stdin=None):
    env = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "kama-shokunin",
           "GIT_COMMITTER_NAME": "kama-shokunin", "GIT_AUTHOR_EMAIL": "a@x",
           "GIT_COMMITTER_EMAIL": "a@x", "PATH": "/usr/bin:/bin"}
    out = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                          "-C", str(repo), *args],
                         input=None if stdin is None else stdin.encode(),
                         capture_output=True, env=env, timeout=30)
    if out.returncode != 0:
        raise InputError(f"git {args} in {repo}: "
                         f"{out.stderr.decode('utf-8', 'replace').strip()}")
    return out.stdout.decode("utf-8", "replace")


def extract_before(directory):
    """The pinned before, verified before it is written anywhere."""
    raw = subprocess.run(
        ["git", "--no-replace-objects", "--no-lazy-fetch", "-C",
         str(LANE_ROOT), "show", f"{PINNED_COMMIT}:{PINNED_PATH}"],
        capture_output=True, timeout=30,
        env={"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
             "PATH": "/usr/bin:/bin"}).stdout
    if not raw:
        raise InputError(f"cannot read {PINNED_COMMIT}:{PINNED_PATH} from "
                         f"{LANE_ROOT}")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != BASELINE_SHA256:
        raise InputError(f"pinned before sha256 {digest} != baseline "
                         f"{BASELINE_SHA256}")
    path = directory / "before-report-landing-audit.py"
    path.write_bytes(raw)
    return path, digest


def scenario(tmp, name):
    """Build one offline fixture; return (lane, fleet, draft, errata)."""
    lane, fleet = Path(tmp, "lane"), Path(tmp, "fleet")
    for repo in (lane, fleet):
        repo.mkdir()
        git(repo, "init", "-q", "-b", "master")
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
        tree = git(fleet, "mktree", stdin=f"100644 blob {blob}\tf\n").strip()
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
        raise InputError(f"unknown scenario {name}")
    return lane, fleet, draft, errata


def run_version(version, lane, fleet, draft, errata):
    cmd = [sys.executable, str(version), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--rounds", "1",
           "--report", f"1={draft}", "--json"]
    cmd += ["--errata", str(errata)] if errata is not None else ["--no-errata"]
    proc = subprocess.run(cmd, capture_output=True, timeout=60)
    kinds, errata_invalid = [], None
    if proc.returncode in (0, 1):
        try:
            doc = json.loads(proc.stdout.decode("utf-8", "replace"))
            kinds = sorted({d["kind"] for res in doc["results"]
                            for d in res["defects"]})
            errata_invalid = doc["summary"].get("errata_invalid")
        except Exception:
            pass
    reason = ""
    if proc.returncode == 2:
        lines = proc.stderr.decode("utf-8", "replace").strip().splitlines()
        reason = lines[-1] if lines else ""
    return {"exit": proc.returncode, "kinds": kinds,
            "errata_invalid": errata_invalid, "reason": reason[:200]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--after", default=str(DEFAULT_AFTER),
                    help="the tool to bind as the after side")
    ap.add_argument("--only", choices=SCENARIOS, default=None)
    ap.add_argument("--json", action="store_true",
                    help="the JSON document is the default; this is an alias")
    ap.add_argument("--text", action="store_true")
    args = ap.parse_args(argv)
    try:
        after = Path(args.after).resolve()
        if not after.is_file():
            raise InputError(f"--after is not a file: {after}")
        if not (LANE_ROOT / ".git").exists() and \
                not (LANE_ROOT / ".jj").exists():
            raise InputError(f"lane root not derived: {LANE_ROOT}")
        names = [args.only] if args.only else SCENARIOS
        with tempfile.TemporaryDirectory(prefix="replay-") as tmp:
            before, before_sha = extract_before(Path(tmp))
            after_sha = hashlib.sha256(after.read_bytes()).hexdigest()
            rows = []
            for name in names:
                with tempfile.TemporaryDirectory(prefix="replay-case-") as case:
                    lane, fleet, draft, errata = scenario(case, name)
                    row = {"consumer": name,
                           "expected": EXPECTED[name],
                           "before": run_version(before, lane, fleet, draft,
                                                 errata),
                           "after": run_version(after, lane, fleet, draft,
                                                errata)}
                    row["before"]["matches_expectation"] = (
                        row["before"]["exit"] == EXPECTED[name]["exit"])
                    row["after"]["matches_expectation"] = (
                        row["after"]["exit"] == EXPECTED[name]["exit"])
                    rows.append(row)
    except InputError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2
    document = {
        "probe": "six-consumer-replay",
        "before": {"commit": PINNED_COMMIT, "path": PINNED_PATH,
                   "source_sha256": before_sha, "side": "pinned extraction"},
        "after": {"path": str(after), "source_sha256": after_sha},
        "consumers": len(rows),
        "scenarios": rows,
        "admission": "none: this probe measures, it does not gate",
    }
    if args.text:
        for row in rows:
            print(f"{row['consumer']}  expected exit={row['expected']['exit']} "
                  f"kinds={row['expected']['kinds']}")
            for side in ("before", "after"):
                cell = row[side]
                print(f"   {side:6s} exit={cell['exit']} kinds={cell['kinds']} "
                      f"errata_invalid={cell['errata_invalid']} "
                      f"match={cell['matches_expectation']} {cell['reason']}")
    else:
        print(json.dumps(document, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
