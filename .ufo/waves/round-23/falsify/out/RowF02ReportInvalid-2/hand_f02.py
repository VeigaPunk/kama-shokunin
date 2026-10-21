#!/usr/bin/env python3
"""Hand-built F02-report-invalid-utf8 fixture (no import of repo-state-grid).

Creates fresh lane/fleet git repos, commits a report whose bytes after the
Landed section are not UTF-8, then runs the frozen blob and the committed
auditor. Prints exit, traceback flag, stderr tail, stdout tail.
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

FROZEN = Path("/tmp/kama-r23w2/frozen-audit.py")
CURRENT = Path("/tmp/kama-r23w2/RowF02ReportInvalid-2/tools/report-landing-audit.py")
REL = ".ufo/reports/round-1/kama.md"


def genv(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=genv(**extra))
    if check and p.returncode:
        raise SystemExit(f"git {' '.join(args)}: rc={p.returncode} "
                         f"{p.stderr.decode(errors='replace')}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path):
    g(path.parent, "init", "-q", "-b", "master", str(path))
    return path


def commit(repo, author, when, msg, path="f", content=None):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(target, "ab") as fh:
            fh.write((msg + "\n").encode())
    else:
        target.write_bytes(content)
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def report(cites, extra=b""):
    lines = b"".join(b"- " + c.encode() + b"\n" for c in cites)
    return b"# kama round 1\n\n## Landed changes\n\n" + lines + extra


def run(label, auditor, lane, fleet, extra_argv=(), cwd=None, json_mode=True,
        rounds="1"):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet)]
    if json_mode:
        argv.append("--json")
    argv += ["--rounds", rounds, "--no-errata", *extra_argv]
    p = subprocess.run(argv, capture_output=True, timeout=30, env=genv(),
                       cwd=str(cwd or Path(lane).parent))
    tb = b"Traceback (most recent call last)" in p.stderr
    print(f"== {label}: exit={p.returncode} traceback={tb}")
    print("   stderr:", p.stderr.decode(errors="replace").strip()[-400:]
          .replace("\n", "\n           "))
    print("   stdout:", p.stdout.decode(errors="replace").strip()[:300]
          .replace("\n", "\n           "))
    return p.returncode, tb, p.stdout, p.stderr


def build_f02(root):
    lane, fleet = Path(root, "lane"), Path(root, "fleet")
    init(lane)
    init(fleet)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    commit(fleet, "fleet", 2000, "round-1: report", REL,
           report([lc]) + b"\xff\xfe bad\n")
    return lane, fleet, lc


def main():
    root = Path(tempfile.mkdtemp(prefix="f02-hand-", dir="/tmp/kama-r23w2/f02"))
    print(f"# fixture root {root}")
    lane, fleet, lc = build_f02(root)
    print(f"# lane={lane} fleet={fleet} cited={lc}")
    raw = subprocess.run(["git", "-C", str(fleet), "show", f"HEAD:{REL}"],
                         capture_output=True, env=genv()).stdout
    print(f"# git show raw tail = {raw[-12:]!r}; utf8-valid="
          f"{_try(raw)}")
    run("frozen/json", FROZEN, lane, fleet)
    run("current/json", CURRENT, lane, fleet)
    run("frozen/text", FROZEN, lane, fleet, json_mode=False)
    run("current/text", CURRENT, lane, fleet, json_mode=False)


def _try(b):
    try:
        b.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


if __name__ == "__main__":
    main()
