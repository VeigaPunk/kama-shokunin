#!/usr/bin/env python3
"""Hand-built equivalent of grid row C04-landed-section-missing, plus
near-variant fixtures.  Imports nothing from tests/report-audit/; builds
lane and fleet repositories from scratch with git commands and runs the
frozen auditor blob and a current auditor as subprocesses.

Usage:
  repro.py --clone /path/to/kama-clone [--out results.txt]

The clone must be at 245a37f69628c2c6bb29bbf17897d8fb5946c857 (or at least
contain blob 4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/
report-landing-audit.py).  The current auditor is <clone>/tools/
report-landing-audit.py.  Fixtures live in a fresh temporary directory.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FROZEN = "4fe9339f8fc3a4a4a479d9c938a850da12f1124d"
AUDIT = "tools/report-landing-audit.py"
REL = ".ufo/reports/round-1/kama.md"

BASE = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
BASE.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
            GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")


def run(argv, cwd=None, **envx):
    env = dict(BASE)
    env.update(envx)
    return subprocess.run(argv, cwd=cwd, capture_output=True, env=env)


def git(repo, *args, **envx):
    p = run(["git", "-C", str(repo), *args], **envx)
    if p.returncode:
        raise SystemExit(f"git {' '.join(args)}: {p.stderr.decode()}")
    return p.stdout


def init(path):
    path.mkdir(parents=True, exist_ok=True)
    git(path.parent, "init", "-q", "-b", "master", str(path))
    return path


def commit(repo, author, when, message, path="f", content=None):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(target, "ab") as fh:
            fh.write((message + "\n").encode())
    else:
        target.write_bytes(content)
    git(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", message,
        GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
        GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return git(repo, "rev-parse", "HEAD").decode().strip()


def make_case(root, name, text_fn):
    case = Path(root, name)
    lane, fleet = init(case / "lane"), init(case / "fleet")
    sha = commit(lane, "kama-shokunin", 1000, "round-1: work")
    commit(fleet, "fleet", 2000, "round-1: report", REL, text_fn(sha))
    return case, sha


def audit(auditor, case):
    argv = [sys.executable, str(auditor), "--lane-repo", str(case / "lane"),
            "--fleet-repo", str(case / "fleet"), "--json", "--rounds", "1",
            "--no-errata"]
    p = run(argv, cwd=case)
    try:
        doc = json.loads(p.stdout)
        kinds = sorted({d["kind"] for r in doc["results"]
                        for d in r["defects"]})
        detail = [(d["kind"], d.get("token", "")[:12],
                   d.get("cited_elsewhere")) for r in doc["results"]
                  for d in r["defects"]]
    except (ValueError, KeyError, TypeError):
        kinds, detail = "unparseable", None
    return p.returncode, kinds, detail


def build(aligned):
    return {
        "C04-hand-no-section": lambda s: b"# kama round 1\n\nno section\n",
        "V0-proper-section": lambda s: (
            "# kama round 1\n\n## Landed changes\n\n- " + s + " work\n"
        ).encode(),
        "V1-fenced-template-with-citation": lambda s: (
            "# kama round 1\n\nNothing landed this round.\n\n```md\n"
            "## Landed changes\n- " + s + " work\n```\n").encode(),
        "V4-html-comment-with-citation": lambda s: (
            "# kama round 1\n\n<!-- example:\n## Landed changes\n- " + s
            + " work\n-->\n").encode(),
        "V5-fenced-heading-no-citation": lambda s: (
            "# kama round 1\n\n```md\n## Landed changes\n```\n\n"
            "Nothing landed.\n").encode(),
        "V2-fenced-h2-inside-section": lambda s: (
            "# kama round 1\n\n## Landed changes\n\nThe command printed:\n\n"
            "```\n## notes\n```\n\n- " + s + " work\n").encode(),
        "V11-comment-h2-inside-section": lambda s: (
            "# kama round 1\n\n## Landed changes\n\n<!--\n## notes\n-->\n\n- "
            + s + " work\n").encode(),
        "V10-fenced-template-before-real-section": lambda s: (
            "# kama round 1\n\nFormat reminder:\n\n```md\n## Landed changes\n"
            "```\n\n## Landed changes\n\n- " + s + " work\n").encode(),
        "V3-indented-heading": lambda s: (
            "# kama round 1\n\n  ## Landed changes\n\n- " + s + " work\n"
        ).encode(),
        "V7-setext-h2": lambda s: (
            "# kama round 1\n\nLanded changes\n--------------\n\n- " + s
            + " work\n").encode(),
        "V6-two-spaces-after-hashes": lambda s: (
            "# kama round 1\n\n##  Landed changes\n\n- " + s + " work\n"
        ).encode(),
        "V8-tab-after-hashes": lambda s: (
            "# kama round 1\n\n##\tLanded changes\n\n- " + s + " work\n"
        ).encode(),
        "V9-unterminated-fence-example": lambda s: (
            "# kama round 1\n\nExample:\n\n```\n## Landed changes\n- " + s
            + " work\n").encode(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", required=True)
    ap.add_argument("--out")
    args = ap.parse_args()
    clone = Path(args.clone)
    out = []

    def emit(line=""):
        print(line)
        out.append(line)

    head = git(clone, "rev-parse", "HEAD").decode().strip()
    frozen = Path(tempfile.mkdtemp(prefix="c04-frozen-")) / "frozen-audit.py"
    frozen.write_bytes(git(clone, "cat-file", "blob",
                           f"{FROZEN}:{AUDIT}"))
    current = clone / AUDIT
    emit(f"clone HEAD: {head}")
    emit(f"frozen sha256: {__import__('hashlib').sha256(frozen.read_bytes()).hexdigest()}")
    emit(f"current sha256: {__import__('hashlib').sha256(current.read_bytes()).hexdigest()}")

    root = tempfile.mkdtemp(prefix="c04-fixtures-")
    try:
        # First build once to learn the generated sha, then rebuild all
        # cases so every fixture has its own lane sha.
        for name, fn in build(None).items():
            case, sha = make_case(root, name, fn)
            rep = git(case / "fleet", "show", f"HEAD:{REL}")
            f = audit(frozen, case)
            c = audit(current, case)
            emit(f"\n## {name}  lane={sha[:12]}  heading_in_report="
                 f"{b'## Landed changes' in rep}")
            emit(f"  frozen : exit={f[0]} kinds={f[1]} defects={f[2]}")
            emit(f"  current: exit={c[0]} kinds={c[1]} defects={c[2]}")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    if args.out:
        Path(args.out).write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
