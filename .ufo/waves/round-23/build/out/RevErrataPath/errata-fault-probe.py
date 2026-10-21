#!/usr/bin/env python3
"""Errata-path fault probe for tools/report-landing-audit.py (reviewer RevErrataPath).

Builds throwaway lane/fleet fixtures under --work (fresh temp repos only; the
real lane and fleet are never passed to git as targets), runs a frozen and a
current copy of the auditor on each, and prints one JSON document with exit
code, last summary line, last stderr line, and marker/log side effects.
Fixtures use GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1; the promisor
probe points at ssh://example.invalid and a marker script replaces ssh.

Usage:
  errata-fault-probe.py --frozen FROZEN.py --current CURRENT.py [--work DIR]
"""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys

MASH = "1234567890abcdef1234567890abcdef12345678"  # fabricated 40-hex, no object
FAKE = "fabc0123456789abcdef0123456789abcdef0123"  # fabricated correction, no object
ERRATA = "registry/report-landing-errata.tsv"
ENV0 = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV0.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")


def genv(**extra):
    env = dict(ENV0)
    env.update(extra)
    return env


def run(args, env=None, input=None, check=True):
    p = subprocess.run(args, env=env or ENV0, input=input, capture_output=True,
                       timeout=120)
    if check and p.returncode:
        raise RuntimeError(f"rc={p.returncode} {args[:5]}: "
                           f"{p.stderr.decode(errors='replace')[:300]}")
    return p


def git(repo, *args, env=None, input=None):
    return run(["git", "-C", str(repo), *args], env=env, input=input)


def gout(repo, *args, env=None, input=None):
    return git(repo, *args, env=env, input=input).stdout.decode().strip()


def commit(repo, msg, author, when, files):
    for path, data in files.items():
        p = pathlib.Path(repo, path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.is_symlink() or p.exists():
            p.unlink()
        if isinstance(data, tuple):
            os.symlink(data[1], p)
        else:
            p.write_bytes(data)
        git(repo, "add", "--", path)
    ts = f"@{when} +0000"
    env = genv(GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
               GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
               GIT_AUTHOR_DATE=ts, GIT_COMMITTER_DATE=ts)
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty",
        "-m", msg, env=env)
    return gout(repo, "rev-parse", "HEAD")


def build(work, name, errata, cite_c1=True):
    """Lane: round-1 commit by kama-shokunin, then a ledger commit.
    Fleet: round-1 report citing c1 (unless cite_c1=False) plus MASH."""
    root = work / "fx" / name
    lane, fleet = root / "lane", root / "fleet"
    lane.mkdir(parents=True)
    fleet.mkdir(parents=True)
    git(lane, "init", "-q", "-b", "master")
    git(fleet, "init", "-q", "-b", "master")
    c1 = commit(lane, "round-1: lane work", "kama-shokunin", 1700000000,
                {"f.txt": b"one\n"})
    commit(lane, "lead: errata ledger", "lead", 1700000100,
           {ERRATA: errata(c1, lane, root)})
    cite = f"- {c1[:12]} round-1: lane work\n" if cite_c1 else "- none\n"
    text = ("# kama round 1 report\n## Work performed\n"
            f"Measured tree {MASH} is cited here.\n"
            "## Landed changes\n" + cite)
    commit(fleet, "round-1: kama report", "kama-shokunin", 1700000200,
           {".ufo/reports/round-1/kama.md": text.encode()})
    return root, lane, fleet, c1


def ok_row(c1, lane, root):
    return f"1\tunresolved-full-hash\t{MASH}\t{c1}\tbaseline\n".encode()


def empty_ledger(c1, lane, root):
    return b"# ledger only\n"


def audit(script, lane, fleet, extra=(), env_extra=None):
    env = genv(LC_ALL="C.UTF-8")
    env.update(env_extra or {})
    try:
        p = run([sys.executable, str(script), "--lane-repo", str(lane),
                 "--fleet-repo", str(fleet), "--branch", "master",
                 "--lane", "kama", "--rounds", "1", *extra],
                env=env, check=False)
    except subprocess.TimeoutExpired:
        return {"rc": "TIMEOUT"}
    out = [x for x in p.stdout.decode(errors="replace").splitlines() if x.strip()]
    err = [x for x in p.stderr.decode(errors="replace").splitlines() if x.strip()]
    return {"rc": p.returncode, "summary": out[-1][:120] if out else "",
            "err": err[-1][:140] if err else ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frozen", required=True)
    ap.add_argument("--current", required=True)
    ap.add_argument("--work", default="/tmp/kama-r23-rev-errata-probe")
    args = ap.parse_args()
    work = pathlib.Path(args.work)
    if work.exists():
        shutil.rmtree(work)
    (work / "bin").mkdir(parents=True)
    (work / "fx").mkdir()
    marker = work / "marker.log"
    (work / "bin" / "ssh-marker.sh").write_text(
        f'#!/bin/sh\necho "invoked: $*" >> "{marker}"\nexit 1\n')
    scripts = {"frozen": args.frozen, "current": args.current}
    results = {}

    def both(case, lane, fleet, extra=(), env_extra=None, logs=()):
        arms = {}
        for who in ("frozen", "current"):
            marker.unlink(missing_ok=True)
            for lg in logs:
                lg.unlink(missing_ok=True)
            arm = audit(scripts[who], lane, fleet, extra, env_extra)
            arm["marker"] = marker.read_text()[:120] if marker.exists() else None
            arm["logs"] = [lg.name for lg in logs if lg.exists()]
            arms[who] = arm
        results[case] = arms

    # A0 control: valid ledger
    _, lane, fleet, _ = build(work, "A0", ok_row)
    both("A0 control valid committed ledger", lane, fleet)

    # A1 committed ledger is not UTF-8
    _, lane, fleet, _ = build(work, "A1", lambda c1, l, r:
        f"1\tunresolved-full-hash\t{MASH}\t{c1}\tev\xe9\n".encode("latin-1"))
    both("A1 non-UTF-8 committed ledger, C.UTF-8", lane, fleet)

    # A2 valid UTF-8 ledger under ASCII locale without coercion or UTF-8 mode
    _, lane, fleet, _ = build(work, "A2", lambda c1, l, r:
        f"1\tunresolved-full-hash\t{MASH}\t{c1}\t\u00e9vidence\n".encode("utf-8"))
    both("A2 valid UTF-8 ledger, ASCII locale", lane, fleet,
         env_extra={"LC_ALL": "C", "PYTHONCOERCECLOCALE": "0", "PYTHONUTF8": "0"})

    # A3 refs/replace on the committed ledger blob supplies a forged row
    _, lane, fleet, c1 = build(work, "A3", empty_ledger)
    c2 = gout(lane, "rev-parse", "master")
    blob = gout(lane, "rev-parse", f"{c2}:{ERRATA}")
    forged = gout(lane, "hash-object", "-w", "--stdin", input=(
        f"1\tunresolved-full-hash\t{MASH}\t{c1}\tforged-by-replace\n").encode())
    git(lane, "update-ref", f"refs/replace/{blob}", forged)
    both("A3 refs/replace on ledger blob", lane, fleet)

    # A4 fabricated correction made to resolve through refs/replace
    _, lane, fleet, c1 = build(work, "A4", lambda c1, l, r:
        f"1\tunresolved-full-hash\t{MASH}\t{FAKE}\tev\n".encode())
    git(lane, "update-ref", f"refs/replace/{FAKE}", c1)
    both("A4 refs/replace makes fabricated correction resolve", lane, fleet)

    # A5 valid correction (unreachable commit) made non-commit by refs/replace
    state = {}

    def side_row(c1, l, r):
        tree = gout(l, "rev-parse", f"{c1}^{{tree}}")
        state["side"] = gout(l, "commit-tree", tree, "-m", "side", env=genv(
            GIT_AUTHOR_NAME="s", GIT_COMMITTER_NAME="s",
            GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x"))
        return f"1\tunresolved-full-hash\t{MASH}\t{state['side']}\tside\n".encode()

    _, lane, fleet, c1 = build(work, "A5", side_row)
    blob_f = gout(lane, "rev-parse", f"{c1}:f.txt")
    git(lane, "update-ref", f"refs/replace/{state['side']}", blob_f)
    both("A5 refs/replace turns unreachable correction into a blob", lane, fleet)

    # A18 same unreachable correction without any replace ref
    _, lane, fleet, c1 = build(work, "A18", side_row)
    both("A18 unreachable (dangling) commit as correction, no replace", lane, fleet)

    # A6 promisor lazy fetch on fabricated correction (ssh marker)
    _, lane, fleet, c1 = build(work, "A6", lambda c1, l, r:
        f"1\tunresolved-full-hash\t{MASH}\t{FAKE}\tev\n".encode())
    for key, val in (("core.repositoryformatversion", "1"),
                     ("extensions.partialclone", "origin"),
                     ("remote.origin.url", "ssh://example.invalid/none.git"),
                     ("remote.origin.promisor", "true"),
                     ("remote.origin.partialclonefilter", "blob:none"),
                     ("core.sshCommand", f"sh {work}/bin/ssh-marker.sh")):
        git(lane, "config", key, val)
    both("A6 promisor lazy fetch on correction lookup", lane, fleet)

    # A6b promisor remote without extensions.partialclone
    _, lane, fleet, c1 = build(work, "A6b", lambda c1, l, r:
        f"1\tunresolved-full-hash\t{MASH}\t{FAKE}\tev\n".encode())
    for key, val in (("remote.origin.url", "ssh://example.invalid/none.git"),
                     ("remote.origin.promisor", "true"),
                     ("remote.origin.partialclonefilter", "blob:none"),
                     ("core.sshCommand", f"sh {work}/bin/ssh-marker.sh")):
        git(lane, "config", key, val)
    both("A6b promisor remote config only", lane, fleet)

    # A7 textconv + smudge attached to the ledger path (repo-local)
    root, lane, fleet, c1 = build(work, "A7", empty_ledger)
    forged = root / "forged-row.tsv"
    forged.write_bytes(f"1\tunresolved-full-hash\t{MASH}\t{c1}\tforged\n".encode())
    (root / "tc.sh").write_text(f'#!/bin/sh\necho tc >> "{root}/tc.log"\ncat "{forged}"\n')
    (root / "fl.sh").write_text(f'#!/bin/sh\necho fl >> "{root}/fl.log"\ncat\n')
    (lane / ".git" / "info" / "attributes").write_text(f"{ERRATA} diff=tc filter=fl\n")
    git(lane, "config", "diff.tc.textconv", f"sh {root}/tc.sh")
    git(lane, "config", "filter.fl.smudge", f"sh {root}/fl.sh")
    both("A7 textconv/smudge attached to ledger path", lane, fleet,
         logs=[root / "tc.log", root / "fl.log"])

    # A8 textconv attached to the fleet report path
    root, lane, fleet, c1 = build(work, "A8", empty_ledger)
    clean = (f"# kama round 1 report\n## Work performed\nMeasured tree withdrawn.\n"
             f"## Landed changes\n- {c1[:12]} round-1: lane work\n")
    (root / "clean-report.md").write_text(clean)
    (root / "tc2.sh").write_text(f'#!/bin/sh\necho tc2 >> "{root}/tc2.log"\ncat "{root}/clean-report.md"\n')
    (fleet / ".git" / "info" / "attributes").write_text(".ufo/reports/round-1/kama.md diff=tc2\n")
    git(fleet, "config", "diff.tc2.textconv", f"sh {root}/tc2.sh")
    both("A8 textconv attached to fleet report path", lane, fleet,
         logs=[root / "tc2.log"])

    # A9 info/grafts hides the omitted round commit; A9b is the no-graft control
    _, lane, fleet, c1 = build(work, "A9b", ok_row, cite_c1=False)
    both("A9b omitted round commit, no graft (control)", lane, fleet)
    _, lane, fleet, c1 = build(work, "A9", ok_row, cite_c1=False)
    (lane / ".git" / "info" / "grafts").write_text(f"{gout(lane, 'rev-parse', 'master')}\n")
    both("A9 info/grafts hides omitted round commit", lane, fleet)

    # A10 non-ASCII token printed under ASCII stdout; A10c UTF-8 control
    def nonascii(c1, lane, root):
        return (f"1\tunresolved-full-hash\t{MASH}\t{c1}\tok\n"
                f"1\tlanded-section-missing\t\u00e9\t-\tev\n").encode("utf-8")

    _, lane, fleet, _ = build(work, "A10", nonascii)
    both("A10 ASCII stdout, non-ASCII unmatched token", lane, fleet,
         env_extra={"PYTHONIOENCODING": "ascii"})
    both("A10c control UTF-8 stdout", lane, fleet,
         env_extra={"PYTHONIOENCODING": "utf-8"})

    # A11 --errata file that is not UTF-8
    root, lane, fleet, c1 = build(work, "A11", ok_row)
    bad = root / "bad.tsv"
    bad.write_bytes(f"1\tunresolved-full-hash\t{MASH}\t{c1}\tev\xe9\n".encode("latin-1"))
    both("A11 --errata non-UTF-8 file", lane, fleet, extra=["--errata", str(bad)])

    # A12 UTF-8 BOM before a comment line
    _, lane, fleet, _ = build(work, "A12", lambda c1, l, r:
        b"\xef\xbb\xbf# ledger\n" + f"1\tunresolved-full-hash\t{MASH}\t{c1}\tev\n".encode())
    both("A12 UTF-8 BOM ledger", lane, fleet)

    # A13 ledger path is a symlink whose target text is the row
    _, lane, fleet, _ = build(work, "A13", lambda c1, l, r:
        ("symlink", f"1\tunresolved-full-hash\t{MASH}\t{c1}\tsym"))
    both("A13 symlink ledger blob", lane, fleet)

    # A14 symbolic correction HEAD
    _, lane, fleet, _ = build(work, "A14", lambda c1, l, r:
        f"1\tunresolved-full-hash\t{MASH}\tHEAD\tev\n".encode())
    both("A14 symbolic correction HEAD", lane, fleet)

    # A15 refs/replace hides the fabricated report token itself
    _, lane, fleet, c1 = build(work, "A15", empty_ledger)
    git(lane, "update-ref", f"refs/replace/{MASH}", c1)
    both("A15 refs/replace hides fabricated report token", lane, fleet)

    # A16 bare CR inside one committed ledger line yields two tool rows
    _, lane, fleet, c1 = build(work, "A16", lambda c1, l, r:
        (f"1\tunresolved-full-hash\t{MASH}\t{c1}\tev\r"
         f"1\tlanded-omitted\t{c1}\t{c1}\thidden\n").encode(), cite_c1=False)
    results["A16 git-visible line count of ledger"] = gout(lane, "show", f"master:{ERRATA}").count("\n") + 1
    both("A16 CR splits one git line into two rows", lane, fleet)

    # A17 correction object reachable only through objects/info/alternates
    donor = work / "fx" / "A17-donor"
    donor.mkdir(parents=True)
    git(donor, "init", "-q", "-b", "master")
    xc = commit(donor, "outside work", "x", 1700000050, {"o.txt": b"outside\n"})
    _, lane, fleet, _ = build(work, "A17", lambda c1, l, r:
        f"1\tunresolved-full-hash\t{MASH}\t{xc}\tev\n".encode())
    (lane / ".git" / "objects" / "info" / "alternates").write_text(
        str(donor / ".git" / "objects") + "\n")
    both("A17 correction reachable only via alternates", lane, fleet)

    print(json.dumps({"scripts": {k: str(v) for k, v in scripts.items()},
                      "results": results}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
