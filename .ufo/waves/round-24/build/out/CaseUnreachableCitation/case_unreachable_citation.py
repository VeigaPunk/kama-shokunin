#!/usr/bin/env python3
"""Round-24 oracle case (single, independent): a locally present but
branch-unreachable commit citation must stay resolvable in a promisor-marked
lane.

Offline only. Every repository is created from scratch under a scratch root
(/fast/scratch/hyaku/kama-r24/CaseUnreachableCitation/fixtures). The promisor
remote URL points at a NON-EXISTENT local path, so no transport can ever
reach the network; every git call in this script passes --no-lazy-fetch, so
no promisor fetch is attempted either. No program payload is configured (no
core.sshCommand, no filter transport hook, no signing program): the
transport check is payload-free and only asserts that no fetch error text
appears.

Arms (identical content; they differ only in the lane's promisor metadata):

  full      lane without promisor metadata  -- CONTROL
  promisor  the same lane, marked promisor by config only
            (extensions.partialClone, remote.origin.promisor,
             remote.origin.partialclonefilter), every object still local

Lane content (author kama-shokunin, round-1 subjects):

  C1  on master                     "round-1: work"
  C2  on master, child of C1        "round-1: more"
  X1  child of C2, NO ref anywhere   -> dangling: unreachable from every ref
  X2  child of C2, held by refs/keep/x2 -> reachable, but not from master

Fleet content: .ufo/reports/round-1/kama.md committed by "fleet", citing C1
by an unambiguous 9+-hex prefix and C2, X1, X2 by their full 40-hex ids.

Expected outcome (the target state, after the round-24 repair):

  full      exit 0, no defects   (control: unchanged by the repair)
  promisor  exit 0, no defects   (the repair must not refuse a complete
                                  promisor-marked lane, and must resolve
                                  X1/X2 because they are locally present)

Why this discriminates: a repair that decides "is this citation available?"
by REACHABILITY (rev-list of the branch, or of --all) instead of by object
existence (cat-file) mis-handles this fixture. X1 is in neither closure yet
is present locally; X2 is outside the branch closure but inside --all. Both
must resolve. Missing required object evidence stays exit 2; locally present
evidence must never be reported as unknown.

Expected BEFORE the repair (r23 base): the promisor arm exits 2 with
"partial clone (extensions.partialclone)" -- the harm being repaired -- and
the full arm exits 0 with no defects.

Usage:
  case_unreachable_citation.py [--out DIR] [--keep]
Exit: 0 the case ran and both premises held; 2 could not evaluate.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/CaseUnreachableCitation/fixtures")
LANE_REPO = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
AUDIT = "tools/report-landing-audit.py"
REL = ".ufo/reports/round-1/kama.md"
TIMEOUT = 60
# transport-error fingerprints: their absence is the payload-free proof that
# no fetch/transport was attempted
TRANSPORT_ERRORS = ("does not appear to be a git repository",
                    "Could not read from remote repository",
                    "unable to access",
                    "Could not resolve host")


class Premise(Exception):
    """The fixture did not establish what the case claims."""


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    """A git call with lazy fetch disabled; never inherits GIT_*."""
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), *args],
                       input=data, capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise Premise(f"git {' '.join(map(str, args))}: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    g(path.parent, "init", "-q", "-b", "master", str(path))
    g(path, "config", "gc.auto", "0")
    g(path, "config", "user.name", "fixture")
    g(path, "config", "user.email", "a@x")
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


def raw_commit(repo, tree, parents, message, when, author="kama-shokunin"):
    """Write a commit object; no ref points at it (dangling until a ref is
    added)."""
    body = b"tree " + tree.encode() + b"\n"
    for p in parents:
        body += b"parent " + p.encode() + b"\n"
    who = author.encode() + b" <a@x> " + str(when).encode() + b" +0000"
    body += b"author " + who + b"\ncommitter " + who + b"\n\n" + message
    return g(repo, "hash-object", "-t", "commit", "-w", "--stdin", data=body)


def citation_prefix(repo, sha):
    """Shortest >=9-hex prefix that is a checkable citation (has a digit and
    a letter) and is unambiguous in the lane. The auditor only checks a
    Landed token as a citation when it has both, so a prefix without them
    would silently stop being a citation."""
    for size in range(9, 41):
        token = sha[:size]
        if not (re.search(r"[0-9]", token) and re.search(r"[a-f]", token)):
            continue
        answer = g(repo, "cat-file", "--batch-check", data=(token + "\n").encode())
        if answer.startswith(sha) and "ambiguous" not in answer:
            return token
    return sha


def report(prefix, c2, x1, x2):
    return (
        "# kama round 1\n\n## Landed changes\n\n"
        f"- `{prefix}` work\n"
        f"- `{c2}` more\n"
        f"- `{x1}` dangling\n"
        f"- `{x2}` kept off-branch\n"
    ).encode()


def build(root: Path):
    lane, fleet = init(root / "lane"), init(root / "fleet")
    c1 = commit(lane, "kama-shokunin", 1000, "round-1: work")
    c2 = commit(lane, "kama-shokunin", 1500, "round-1: more", "f2")
    tree = g(lane, "rev-parse", f"{c2}^{{tree}}")
    x1 = raw_commit(lane, tree, [c2], b"round-1: dangling\n", 1600)
    x2 = raw_commit(lane, tree, [c2], b"round-1: kept\n", 1700)
    g(lane, "update-ref", "refs/keep/x2", x2)
    prefix = citation_prefix(lane, c1)
    commit(fleet, "fleet", 2000, "round-1: report", REL,
           report(prefix, c2, x1, x2))
    return {"lane": str(lane), "fleet": str(fleet), "c1": c1, "c2": c2,
            "x1": x1, "x2": x2, "c1_prefix": prefix,
            "x2_ref": "refs/keep/x2"}


def mark_promisor(lane: Path, absent_origin: Path):
    """Promisor metadata only; every object stays present locally."""
    g(lane, "config", "extensions.partialClone", "origin")
    g(lane, "config", "remote.origin.promisor", "true")
    g(lane, "config", "remote.origin.partialclonefilter", "blob:none")
    g(lane, "config", "remote.origin.url", str(absent_origin))
    g(lane, "config", "remote.origin.fetch",
      "+refs/heads/*:refs/remotes/origin/*")


def premise(facts, arm):
    lane, fleet = Path(facts["lane"]), Path(facts["fleet"])
    out = {"arm": arm}
    # 1. every cited object exists locally, as a commit
    for key in ("c1", "c2", "x1", "x2"):
        if g(lane, "cat-file", "-t", facts[key]) != "commit":
            raise Premise(f"{key} is not a commit object in the lane")
    out["all_four_cited_objects_present"] = True
    # 2. X1 and X2 are outside the master closure
    closure = g(lane, "rev-list", "master").split("\n")
    for key in ("x1", "x2"):
        if facts[key] in closure:
            raise Premise(f"{key} is inside the master closure")
    out["x1_x2_outside_master_closure"] = True
    # 3. X1 unreachable from every ref; X2 reachable, but off-branch
    allrefs = g(lane, "rev-list", "--all").split("\n")
    out["x1_unreachable_from_all_refs"] = facts["x1"] not in allrefs
    out["x2_reachable_only_off_branch"] = facts["x2"] in allrefs
    if not out["x1_unreachable_from_all_refs"]:
        raise Premise("x1 is reachable from some ref; it is not dangling")
    if not out["x2_reachable_only_off_branch"]:
        raise Premise("x2 is not reachable through refs/keep/x2")
    # 4. cat-file resolves both, plain and peeled
    for key in ("x1", "x2"):
        oid = facts[key]
        plain = g(lane, "cat-file", "--batch-check", data=(oid + "\n").encode())
        peeled = g(lane, "cat-file", "--batch-check",
                   data=(oid + "^{commit}\n").encode())
        for answer in (plain, peeled):
            if not answer.startswith(oid + " commit"):
                raise Premise(f"cat-file did not resolve {key}: {answer!r}")
            if any(word in answer for word in
                   ("missing", "dangling", "excluded", "ambiguous")):
                raise Premise(f"cat-file reported {key} as {answer!r}")
    out["cat_file_resolves_x1_x2"] = True
    # 5. the cited prefix is checkable and unambiguous in lane and fleet
    prefix = facts["c1_prefix"]
    if not (re.search(r"[0-9]", prefix) and re.search(r"[a-f]", prefix)):
        raise Premise(f"c1 prefix {prefix} is not a checkable citation")
    for repo in (lane, fleet):
        answer = g(repo, "cat-file", "--batch-check",
                   data=(prefix + "\n").encode())
        # "missing" in the fleet is correct: only the lane holds the commit.
        # "ambiguous" anywhere is fatal, and a hit must be the same commit.
        if "ambiguous" in answer:
            raise Premise(f"c1 prefix {prefix} is ambiguous in {repo}: "
                          f"{answer!r}")
        if "missing" not in answer and not answer.startswith(facts["c1"]):
            raise Premise(f"c1 prefix {prefix} names another object in "
                          f"{repo}: {answer!r}")
    out["c1_prefix_unique_in_both_repos"] = True
    # 6. the fleet report carries exactly the four citations
    text = g(fleet, "show", f"HEAD:{REL}")
    for oid in (facts["c2"], facts["x1"], facts["x2"]):
        if oid not in text:
            raise Premise(f"report does not cite {oid}")
    if facts["c1_prefix"] not in text:
        raise Premise("report does not cite c1 by prefix")
    out["report_cites_all_four"] = True
    # 7. promisor arm: metadata present, no promisor pack, nothing missing
    if arm == "promisor":
        cfg = g(lane, "config", "--list").lower()
        for key in ("extensions.partialclone", "remote.origin.promisor",
                    "remote.origin.partialclonefilter"):
            if key not in cfg:
                raise Premise(f"promisor metadata {key} not set")
        if list(Path(lane, ".git/objects/pack").glob("*.promisor")):
            raise Premise("unexpected promisor pack")
        for key in ("c1", "c2", "x1", "x2"):
            if g(lane, "cat-file", "-t", facts[key]) != "commit":
                raise Premise(f"{key} missing in the promisor arm")
        out["promisor_metadata_only"] = True
    listing = g(lane, "rev-list", "--objects", "--all", "--missing=print")
    if "?" in listing:
        raise Premise("lane has missing objects")
    out["lane_object_store_complete"] = True
    return out


def run_audit(facts, auditor: Path):
    argv = [sys.executable, str(auditor), "--lane-repo", facts["lane"],
            "--fleet-repo", facts["fleet"], "--rounds", "1", "--no-errata",
            "--json"]
    p = subprocess.run(argv, capture_output=True, env=env(), timeout=TIMEOUT,
                       cwd=facts["fleet"])
    kinds = None
    if p.returncode in (0, 1):
        try:
            doc = json.loads(p.stdout)
            kinds = sorted({d["kind"] for r in doc["results"]
                            for d in r["defects"]})
        except (ValueError, KeyError, TypeError):
            kinds = "unparseable"
    stderr = p.stderr.decode(errors="replace").strip()
    transport = [e for e in TRANSPORT_ERRORS if e in stderr]
    return {"exit": p.returncode, "kinds": kinds, "stderr": stderr,
            "transport_errors": transport,
            "stdout_head": p.stdout.decode(errors="replace")[:400]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(HERE))
    ap.add_argument("--keep", action="store_true",
                    help="keep the fixture trees for inspection")
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)
    absent_origin = SCRATCH / "absent-origin.git"   # deliberately never created
    doc = {"case": "CaseUnreachableCitation",
           "git": subprocess.run(["git", "--version"], capture_output=True)
           .stdout.decode().strip(),
           "python": sys.version.split()[0],
           "scratch_root": str(SCRATCH), "arms": {}}
    try:
        for arm in ("full", "promisor"):
            root = SCRATCH / arm
            facts = build(root)
            if arm == "promisor":
                mark_promisor(Path(facts["lane"]), absent_origin)
            prem = premise(facts, arm)
            res = run_audit(facts, LANE_REPO / AUDIT)
            doc["arms"][arm] = {"facts": facts, "premise": prem, "base": res}
    except Premise as exc:
        doc["error"] = f"could-not-evaluate: fixture premise: {exc}"
        (out / "observed-base.json").write_text(
            json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8")
        print(doc["error"], file=sys.stderr)
        return 2
    (out / "observed-base.json").write_text(
        json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8")
    if not args.keep:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    for arm, data in doc["arms"].items():
        b = data["base"]
        print(f"{arm}: exit={b['exit']} kinds={b['kinds']} "
              f"transport_errors={b['transport_errors']} "
              f"stderr={b['stderr'][:100]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
