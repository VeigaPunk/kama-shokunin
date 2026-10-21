#!/usr/bin/env python3
"""Round-24 lane oracle: multiple roots (--branch != HEAD).

Target under test
-----------------
`tools/report-landing-audit.py --branch B` selects lane branch B. The lane
repository's HEAD may point at a *different* branch with a different root.
Every completeness/availability decision must therefore be rooted at the
*selected branch*, never at HEAD:

  * the required-commit set (landed-omitted candidates) comes from the
    selected branch's history;
  * the availability/completeness walk of the lane repository starts at the
    selected branch tip;
  * object resolution (`cat-file`) is repository-wide: an object that exists
    locally is found even when it is only reachable from another branch.

Rows (each builds fresh, fully offline scratch repositories):

  MR-A  sibling roots: HEAD=master (own root), selected=feature (orphan
        root), all objects present          -> exit 0, no defect
  MR-H  selected branch behind HEAD: HEAD's extra round commit is not
        required evidence                  -> exit 0, no defect
  MR-E  selected branch ahead of HEAD by one uncited `round-1:` commit
                                          -> exit 1, landed-omitted
  MR-B  promisor-marked lane; a required object is missing on the selected
        branch's closure                  -> exit 2 (could-not-evaluate)
  MR-C  an object is missing only on HEAD's branch, selected branch complete
                                          -> exit 0, no defect
  MR-C2 promisor-marked MR-C                 -> exit 0, no defect
  MR-I  promisor-marked lane; the report cites a commit that exists only on
        HEAD's branch                     -> exit 0, no defect
  MR-F  promisor metadata only, every object present
                                          -> exit 0, no defect
  MR-G  promisor-marked lane; the report cites an object that exists in
        neither repository                -> exit 2 (unknown, not absent)

Rows that expect a verdict (exit 0/1) additionally forbid the r23 blanket
refusal text ("partial clone") in stderr: the repair must not silence the
audit with the refusal it is replacing.

Policy note (MR-B). Two readings of "required object" are possible and they
disagree on exactly one row:
  P1 closure  - every object reachable from the selected branch tip must be
                present locally; a missing one is unavailable evidence.
                MR-B -> exit 2.
  P2 evidence  - only the objects the audit actually reads must be present
                (walked commits, cited objects, SOURCES/errata/report blobs).
                MR-B -> exit 0 (the deleted blob is never read).
MR-B is marked `policy` in the row table and its expected exit is taken from
--policy (default P1). The candidate MUST declare which policy it implements;
this grid then discriminates it.

Nothing here touches the network: the promisor remote points at a local
directory that is not a git repository, and the auditor is expected to keep
--no-lazy-fetch (no object is ever fetched, so the object store is unchanged).

Usage: multiple-roots-grid.py --work DIR [--auditor PATH] [--policy P1|P2]
                               [--case NAME ...] [--json]
Exit: 0 every row met its expectation; 1 at least one did not; 2 could not
evaluate (fixture premise failed, git or auditor unusable).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile

AUDIT = "tools/report-landing-audit.py"
REL = ".ufo/reports/round-1/kama.md"
FAKE = "abcdefabcdefabcdefabcdefabcdefabcdefabcd"
TIMEOUT = 30
POLICIES = ("P1", "P2")


class Premise(Exception):
    """The fixture did not establish its premise: cannot evaluate."""


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
        raise Premise(f"git {' '.join(map(str, args))}: "
                      f"{p.stderr.decode(errors='replace').strip()}")
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


def orphan_commit(repo, when, msg, path="h", body=None):
    """A commit with no parent: a genuinely different root."""
    blob = g(repo, "hash-object", "-w", "--stdin",
             data=(body or (msg + "\n")).encode())
    tree = g(repo, "mktree", data=f"100644 blob {blob}\t{path}\n".encode())
    stamp = f"@{when} +0000"
    sha = g(repo, "commit-tree", tree, "-m", msg,
            GIT_AUTHOR_NAME="kama-shokunin", GIT_COMMITTER_NAME="kama-shokunin",
            GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return sha


def set_branch(repo, name, sha):
    g(repo, "update-ref", f"refs/heads/{name}", sha)


def delete_loose_object(repo, oid):
    """Remove a loose object from the store: it becomes genuinely missing."""
    p = Path(repo, ".git/objects") / oid[:2] / oid[2:]
    if not p.is_file():
        raise Premise(f"object {oid} is not a loose object")
    p.unlink()


def missing_from(repo, rev):
    """oids git reports as missing from the closure of rev."""
    out = g(repo, "rev-list", "--objects", "--missing=print", rev)
    return {line[1:].split()[0] for line in out.splitlines()
            if line.startswith("?")}


def report(cites, extra=b""):
    lines = b"".join(b"- " + c.encode() + b"\n" for c in cites)
    return b"# kama round 1\n\n## Work performed\n\nfixture\n\n" \
           b"## Landed changes\n\n" + lines + extra


def publish(fleet, text, when=2000, path=REL):
    commit(fleet, "fleet", when, "round-1: report", path, text)


def make_promisor(repo, donor):
    """Metadata-only promisor marking. The remote is a local directory that
    holds a complete copy of the history, so a lazy fetch would succeed
    offline and be observable (new files under .git/objects); with
    --no-lazy-fetch nothing is ever fetched."""
    g(repo, "config", "core.repositoryformatversion", "1")
    g(repo, "config", "extensions.partialclone", "origin")
    g(repo, "config", "remote.origin.url", str(donor))
    g(repo, "config", "remote.origin.promisor", "true")
    g(repo, "config", "remote.origin.partialclonefilter", "blob:none")


def clone_donor(lane, tmp):
    """A complete local copy of the lane repository, made before any object
    is deleted: the promisor remote for the promisor-marked rows."""
    donor = Path(tmp, "donor")
    subprocess.run(["cp", "-a", str(lane), str(donor)], check=True)
    return donor


# ------------------------------------------------------------------ builders
# Each builder returns (lane, fleet, argv_extra, facts).

def _roots(tmp):
    """lane: master (C1,C2) + orphan feature (C3); fleet report cites C3."""
    lane = init(Path(tmp, "lane"))
    fleet = init(Path(tmp, "fleet"))
    c1 = commit(lane, "kama-shokunin", 1000, "round-1: work", "f")
    c2 = commit(lane, "kama-shokunin", 1100, "round-1: master more", "g")
    c3 = orphan_commit(lane, 1200, "round-1: feature work", "h")
    set_branch(lane, "feature", c3)
    publish(fleet, report([c3]))
    donor = clone_donor(lane, tmp)
    return lane, fleet, {"c1": c1, "c2": c2, "c3": c3, "donor": str(donor)}


def mr_a(tmp):
    lane, fleet, f = _roots(tmp)
    return lane, fleet, [], f


def mr_e(tmp):
    """feature = master + one uncited round-1 commit."""
    lane = init(Path(tmp, "lane"))
    fleet = init(Path(tmp, "fleet"))
    c1 = commit(lane, "kama-shokunin", 1000, "round-1: work", "f")
    publish(fleet, report([c1]))
    extra = commit(lane, "kama-shokunin", 1300, "round-1: feature extra", "k")
    set_branch(lane, "feature", extra)
    return lane, fleet, [], {"c1": c1, "extra": extra}


def mr_b(tmp):
    """Promisor-marked lane; an object on the selected branch's closure is
    missing locally: unavailable evidence, never a verdict."""
    lane, fleet, f = _roots(tmp)
    make_promisor(lane, f["donor"])
    blob = g(lane, "rev-parse", f"{f['c3']}:h")
    delete_loose_object(lane, blob)
    if blob not in missing_from(lane, "feature"):
        raise Premise("deleted blob is not reported missing from feature")
    if missing_from(lane, "master"):
        raise Premise("master closure is not complete")
    f["missing"] = blob
    return lane, fleet, [], f


def mr_c(tmp):
    """An object on HEAD's branch is missing; the selected branch is whole."""
    lane, fleet, f = _roots(tmp)
    blob = g(lane, "rev-parse", f"{f['c2']}:g")
    delete_loose_object(lane, blob)
    if blob not in missing_from(lane, "master"):
        raise Premise("deleted blob is not reported missing from master")
    if missing_from(lane, "feature"):
        raise Premise("feature closure is not complete")
    f["missing"] = blob
    return lane, fleet, [], f


def mr_c2(tmp):
    """Promisor-marked lane; the missing object is only on HEAD's branch
    and the selected branch is whole: no refusal."""
    lane, fleet, f = _roots(tmp)
    make_promisor(lane, f["donor"])
    blob = g(lane, "rev-parse", f"{f['c2']}:g")
    delete_loose_object(lane, blob)
    if blob not in missing_from(lane, "master"):
        raise Premise("deleted blob is not reported missing from master")
    if missing_from(lane, "feature"):
        raise Premise("feature closure is not complete")
    f["missing"] = blob
    return lane, fleet, [], f


def mr_i(tmp):
    """Promisor-marked lane; the report cites a commit that lives only on
    HEAD's branch. Resolution is repository-wide, not branch-scoped."""
    lane, fleet, f = _roots(tmp)
    make_promisor(lane, f["donor"])
    publish(fleet, report([f["c3"], f["c1"]]), when=2100)
    return lane, fleet, [], f


def mr_h(tmp):
    """Selected branch behind HEAD: HEAD's extra round commit is not
    required evidence and must not be reported as landed-omitted."""
    lane = init(Path(tmp, "lane"))
    fleet = init(Path(tmp, "fleet"))
    c1 = commit(lane, "kama-shokunin", 1000, "round-1: work", "f")
    c2 = commit(lane, "kama-shokunin", 1100, "round-1: master more", "g")
    set_branch(lane, "feature", c1)
    publish(fleet, report([c1]), when=2100)
    return lane, fleet, [], {"c1": c1, "c2": c2}


def mr_f(tmp):
    """Promisor metadata only; every object is present locally."""
    lane, fleet, f = _roots(tmp)
    make_promisor(lane, f["donor"])
    return lane, fleet, [], f


def mr_g(tmp):
    """Promisor-marked lane; the report cites an object that exists in
    neither repository: unknown, never proved absent."""
    lane, fleet, f = _roots(tmp)
    make_promisor(lane, f["donor"])
    publish(fleet, report([f["c3"], FAKE]), when=2100)
    f["fake"] = FAKE
    return lane, fleet, [], f


# name, kind, builder, expected {P1: exit, P2: exit}, expected kinds,
# forbidden stderr fragments (a refusal path that must not be used)
CASES = [
    ("MR-A-multi-root-complete", "control", mr_a, 0, 0, [], []),
    ("MR-H-selected-behind-head", "control", mr_h, 0, 0, [], []),
    ("MR-E-selected-ahead-uncited", "control", mr_e, 1, 1,
     ["landed-omitted"], []),
    ("MR-B-missing-on-selected-root", "policy", mr_b, 2, 0, None,
     ["partial clone"]),
    ("MR-C-missing-on-head-root", "control", mr_c, 0, 0, [], []),
    ("MR-C2-promisor-missing-on-head-root", "control", mr_c2, 0, 0, [],
     ["partial clone"]),
    ("MR-I-citation-outside-selected-root", "control", mr_i, 0, 0, [],
     ["partial clone"]),
    ("MR-F-promisor-metadata-only", "control", mr_f, 0, 0, [],
     ["partial clone"]),
    ("MR-G-promisor-unknown-citation", "control", mr_g, 2, 2, None,
     ["partial clone"]),
]

BRANCH = "feature"


def store_snapshot(repo):
    """Relative paths of everything under .git/objects: a fetch would add
    entries here."""
    root = Path(repo, ".git/objects")
    if not root.is_dir():
        return set()
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


def run_case(auditor, case, tmp):
    name, kind, build, p1, p2, want_kinds, forbidden = case
    lane, fleet, extra, facts = build(tmp)
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--branch", BRANCH,
            "--rounds", "1", "--no-errata", "--json"]
    before = store_snapshot(lane)
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env(), cwd=tmp,
                            start_new_session=True)
    try:
        out, err = proc.communicate(timeout=TIMEOUT)
        code, timed_out = proc.returncode, False
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        code, timed_out = None, True
    fetched = sorted(store_snapshot(lane) - before)
    kinds = None
    required = None
    if code in (0, 1):
        try:
            doc = json.loads(out)
            kinds = sorted({d["kind"] for r in doc["results"]
                            for d in r["defects"]})
            required = doc["summary"].get("required_commits")
        except (ValueError, KeyError, TypeError):
            kinds = "unparseable"
    traceback = b"Traceback (most recent call last)" in err
    text = err.decode(errors="replace")
    refused = [frag for frag in forbidden if frag in text]
    return {"case": name, "kind": kind, "exit": code, "kinds": kinds,
            "required": required, "traceback": traceback,
            "timed_out": timed_out, "fetched_objects": fetched,
            "forbidden_reason_seen": refused, "facts": facts,
            "stderr_tail": text.strip()[-300:]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--work", required=True,
                    help="scratch directory for the fixtures")
    ap.add_argument("--auditor", required=True,
                    help="path to report-landing-audit.py under test")
    ap.add_argument("--policy", choices=POLICIES, default="P1")
    ap.add_argument("--case", action="append")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    rows = []
    try:
        root = Path(args.work)
        root.mkdir(parents=True, exist_ok=True)
        auditor = Path(args.auditor).resolve()
        if not auditor.is_file():
            raise Premise(f"auditor not found: {auditor}")
        for i, case in enumerate(CASES):
            if args.case and case[0] not in args.case:
                continue
            tmp = root / f"{i:02d}-{case[0]}"
            tmp.mkdir(parents=True, exist_ok=True)
            row = run_case(auditor, case, tmp)
            want_exit = case[3] if args.policy == "P1" else case[4]
            want_kinds = case[5]
            row["expected_exit"] = want_exit
            row["expected_kinds"] = want_kinds
            row["met"] = (not row["timed_out"] and not row["traceback"]
                          and not row["fetched_objects"]
                          and not row["forbidden_reason_seen"]
                          and row["exit"] == want_exit
                          and (want_kinds is None
                               or row["kinds"] == sorted(want_kinds)))
            rows.append(row)
    except Premise as exc:
        print(f"could-not-evaluate: fixture premise: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # errors are never grid verdicts
        print(f"could-not-evaluate: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"policy": args.policy, "rows": rows}, indent=1,
                         sort_keys=True))
    else:
        for r in rows:
            print(f"{r['case']:38s} {r['kind']:8s} exit={r['exit']} "
                  f"(want {r['expected_exit']}) kinds={r['kinds']} "
                  f"required={r['required']} "
                  f"{'met' if r['met'] else 'NOT-MET'}")
    return 0 if all(r["met"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
