#!/usr/bin/env python3
"""Offline fixture builder for the missing-committed-lane-errata-blob oracle.

Synthetic, local-only, no network transport: every remote-shaped URL written
into a fixture points at a repository on this disk (file://) or at a
nonexistent local path. No program is executed, no payload is fetched, no
remote host is contacted.

Tripwire: where a promisor-marked arm has a real local origin, a lazy fetch
would silently restore the missing object and change the verdict, so the
runner re-probes object availability after every run and reports a fetch if
the object reappeared.

Arms (each builds a lane repo with one cited round-1 commit, one omitted
round-1 commit, one committed errata ledger blob, and a fleet repo whose
round-1 report cites only the first commit; fleet first-add cutoff 2000):

  E1  ledger-present-complete
        complete repos; the errata ledger blob is committed and present, and
        its row names the omitted commit, so the omission is corrected.
  E2  ledger-committed-blob-missing-promisor
        a full clone marked promisor whose committed errata blob object was
        deleted locally; every other object is present; the local origin
        could serve the deleted blob if the auditor ever lazy-fetched.
  E3  ledger-committed-blob-missing-blobless
        a blob:none clone in which every blob except the errata blob was
        copied back from the source, so the errata blob is the single
        unavailable object.
  E4  ledger-absent-from-tree
        complete repos; the ledger path was never committed (absent, not
        unavailable).
  E5  ledger-committed-blob-missing-no-promisor
        complete repos, no promisor metadata, only the errata blob object is
        absent locally.
  E6  ledger-present-row-mismatch
        the ledger blob is present but its row names a different token, so
        the omission stays uncorrected.
  E7  promisor-marked-complete
        lane and fleet are promisor-marked (extensions.partialclone,
        remote.*.promisor, remote.*.partialclonefilter) but every object is
        present locally: metadata-only declaration, complete content.
  E8  promisor-marked-ledger-correction-object-missing
        promisor-marked lane whose ledger names, as the correction for an
        unresolved-full-hash defect, a commit object that is absent locally
        but still present in the local origin (promised, not absent).
  E9  ledger-correction-object-missing-no-promisor
        the same ledger row in a non-promisor lane where the named
        correction commit never existed in the audited repositories, so its
        absence is evidence.
  E10 promisor-marked-ledger-missing-no-defects
        the report cites every required commit, so the ledger's only row
        (a round-2 row, outside the selected round) changes nothing: with
        the blob present the audit is clean. With the blob missing the
        auditor cannot know that, so a silent empty-ledger fallback would
        emit exit 0 clean -- a clean verdict from missing evidence.
  E11 promisor-marked-ledger-present-no-defects
        the E10 twin with the blob present: exit 0 clean, errata_rows=1,
        no unmatched or invalid row (the round-2 row is ignored).
  E12 ledger-missing-no-defects-no-promisor
        the E10 twin without promisor metadata: the committed errata blob is
        missing locally in an ordinary repository, and the report cites
        every required commit. An empty-ledger fallback would emit exit 0
        clean; the required evidence is unavailable, so it must be exit 2.
  E13 errata-corrected-missing-sha-plain
        the historical shape of an errata-corrected missing SHA: the report
        cites a spliced 40-hex that is no object in any audited repository
        (the first 20 hex of a real commit plus the last 20 hex of another)
        outside the Landed section, and the lane's committed ledger carries
        the correcting row (round 1, unresolved-full-hash, token=<spliced
        sha>, correction=<real lane commit>). The defect is corrected, so
        the audit is clean.
  E14 errata-corrected-missing-sha-promisor
        the E13 twin with a promisor-marked, content-complete lane. The
        authorized errata matching must still happen: the defect is
        corrected and the audit is clean, exactly like the plain twin.
        Metadata alone must not refuse it.
  E15 blobless-lane-ledger-hydrated
        a blob:none clone whose ledger blob was copied back, so every
        object the audit actually reads is present locally while the
        repository still carries a promisor pack and promisor metadata.
        The verdict must equal the plain twin E1 (exit 0 clean, defects 1,
        corrected 1): a promisor pack is a declaration, not a defect, and
        refusing it would be a blanket precondition.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REL = ".ufo/reports/round-1/kama.md"
ERRATA = "registry/report-landing-errata.tsv"
FAKE = "1234567890abcdef1234567890abcdef12345678"


class Premise(Exception):
    """The fixture did not establish its state."""


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
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
    path = Path(path).resolve()
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


def orphan_commit(repo, author, when, msg):
    """A root commit with no parents and an empty tree: unreachable from
    master, so deleting its object cannot break history traversal."""
    tree = g(repo, "mktree", data=b"")
    stamp = f"@{when} +0000"
    sha = g(repo, "-c", "commit.gpgsign=false", "commit-tree", tree, "-m", msg,
            GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
            GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return sha


def report(cites, extra=b""):
    lines = b"".join(b"- " + c.encode() + b"\n" for c in cites)
    return b"# kama round 1\n\n## Landed changes\n\n" + lines + extra


def mark_promisor(repo, url):
    for key, value in (("extensions.partialclone", "origin"),
                       ("remote.origin.promisor", "true"),
                       ("remote.origin.partialclonefilter", "blob:none")):
        g(repo, "config", key, value)
    g(repo, "config", "remote.origin.url", url)


def has_local(repo, oid):
    """True when the object is present locally. Never fetches."""
    rc = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo),
                          "cat-file", "-e", oid], capture_output=True,
                         env=env()).returncode
    return rc == 0


def delete_loose(repo, oid):
    loose = Path(repo, ".git/objects", oid[:2], oid[2:])
    if not loose.exists():
        raise Premise(f"object {oid} is not loose at {loose}")
    loose.unlink()
    if has_local(repo, oid):
        raise Premise(f"object {oid} still present after deletion")


def build(tmp, arm):
    tmp = Path(tmp).resolve()
    lane = init(tmp / "lane")
    fleet = init(tmp / "fleet")
    cited = commit(lane, "kama-shokunin", 1000, "round-1: work")
    omitted = commit(lane, "kama-shokunin", 1500, "round-1: more")
    report_path = Path(fleet, REL)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    body = report([cited])
    if arm.startswith(("E8", "E9")):
        body += b"\n## Notes\n\nsee " + FAKE.encode() + b"\n"
    if arm.startswith(("E13", "E14")):
        # every required commit is cited in the Landed section, so the only
        # defect is the spliced SHA in the Notes: exactly the PG29 shape
        body = report([cited, omitted])
        spliced = cited[:20] + omitted[20:]
        body += ("\n## Notes\n\nmeasured at " + spliced + "\n").encode()
    report_path.write_bytes(body)
    g(fleet, "add", "--", REL)
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
      "round-1: kama report",
      GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
      GIT_AUTHOR_DATE="@2000 +0000", GIT_COMMITTER_DATE="@2000 +0000")

    errata_blob = None
    correction = None
    donor = None
    if arm.startswith(("E10", "E11", "E12")):
        # the report cites every required commit: no defects at all, so the
        # ledger's only row (round 2, outside the selected round) is
        # ignored. A silent empty-ledger fallback on a missing blob would
        # produce the same exit 0 clean -- indistinguishable, which is the
        # point of the arm.
        report_path.write_bytes(report([cited, omitted]))
        g(fleet, "add", "--", REL)
        g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
          "round-1: kama report (revised)",
          GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
          GIT_AUTHOR_DATE="@2100 +0000", GIT_COMMITTER_DATE="@2100 +0000")
    if arm != "E4-ledger-absent-from-tree":
        if arm.startswith(("E8", "E9")):
            donor = init(tmp / "donor")
            correction = orphan_commit(donor, "fixture", 1700, "decoy")
            row = f"1\tunresolved-full-hash\t{FAKE}\t{correction}\tev\n"
        elif arm.startswith(("E10", "E11")):
            row = f"2\tlanded-omitted\t{omitted}\t{omitted}\tev\n"
        elif arm.startswith(("E13", "E14")):
            spliced = cited[:20] + omitted[20:]
            row = (f"1\tunresolved-full-hash\t{spliced}\t{cited}\toffline "
                   f"fixture\n")
        else:
            row_token = ("0" * 40) if arm.startswith("E6") else omitted
            row = (f"1\tlanded-omitted\t{row_token}\t{row_token}\toffline "
                   f"fixture\n")
        commit(lane, "fixture", 1600, "errata", ERRATA, row.encode())
        errata_blob = g(lane, "rev-parse", f"HEAD:{ERRATA}")

    present = True
    if arm.startswith("E2"):
        src = lane
        clone = tmp / "clone"
        g(tmp, "clone", "-q", "--no-hardlinks", str(src), str(clone))
        lane = clone
        delete_loose(lane, errata_blob)
        present = False
        mark_promisor(lane, f"file://{src}")
    elif arm.startswith("E3"):
        src = lane
        g(lane, "config", "uploadpack.allowFilter", "true")
        clone = tmp / "blobless"
        g(tmp, "-c", "protocol.file.allow=always", "clone", "-q",
          "--filter=blob:none", "--no-local", "--no-checkout",
          f"file://{src}", str(clone))
        lane = clone
        listing = g(lane, "--no-lazy-fetch", "rev-list", "--objects",
                    "--all", check=False)
        for line in listing.split("\n"):
            parts = line.split(" ")
            if len(parts) != 2 or parts[0] == errata_blob:
                continue
            if g(lane, "--no-lazy-fetch", "cat-file", "-t", parts[0],
                 check=False) != "blob":
                continue
            data = subprocess.run(
                ["git", "--no-lazy-fetch", "-C", str(src), "cat-file",
                 "blob", parts[0]], capture_output=True, env=env())
            if data.returncode:
                raise Premise(f"cannot read source blob {parts[0]}")
            g(lane, "hash-object", "-w", "--stdin", data=data.stdout)
        present = False
    elif arm.startswith("E5"):
        delete_loose(lane, errata_blob)
        present = False
    elif arm.startswith("E7"):
        mark_promisor(lane, "file:///nonexistent/local-only")
        mark_promisor(fleet, "file:///nonexistent/local-only")
    elif arm.startswith("E8"):
        # the correction commit lives in the donor, which serves it as the
        # promisor origin: copy it into the lane, then delete it locally, so
        # the object is promised by the origin and absent locally.
        g(donor, "update-ref", "refs/heads/promised", correction)
        blob = subprocess.run(
            ["git", "--no-lazy-fetch", "-C", str(donor), "cat-file", "commit",
             correction], capture_output=True, env=env())
        if blob.returncode:
            raise Premise("cannot read donor correction commit")
        g(lane, "hash-object", "-t", "commit", "-w", "--stdin",
          data=blob.stdout)
        delete_loose(lane, correction)
        mark_promisor(lane, f"file://{donor}")
    elif arm.startswith("E10"):
        mark_promisor(lane, "file:///nonexistent/local-only")
        mark_promisor(fleet, "file:///nonexistent/local-only")
        delete_loose(lane, errata_blob)
        present = False
    elif arm.startswith("E11"):
        mark_promisor(lane, "file:///nonexistent/local-only")
        mark_promisor(fleet, "file:///nonexistent/local-only")
    elif arm.startswith("E12"):
        delete_loose(lane, errata_blob)
        present = False
    elif arm.startswith("E14"):
        mark_promisor(lane, "file:///nonexistent/local-only")
        mark_promisor(fleet, "file:///nonexistent/local-only")
    elif arm.startswith("E15"):
        # a blob:none clone with the ledger blob copied back: every object
        # the audit reads is present, but the repository still carries a
        # promisor pack and promisor metadata
        src = lane
        g(lane, "config", "uploadpack.allowFilter", "true")
        clone = tmp / "blobless"
        g(tmp, "-c", "protocol.file.allow=always", "clone", "-q",
          "--filter=blob:none", "--no-local", "--no-checkout",
          f"file://{src}", str(clone))
        lane = clone
        data = subprocess.run(
            ["git", "--no-lazy-fetch", "-C", str(src), "cat-file", "blob",
             errata_blob], capture_output=True, env=env())
        if data.returncode:
            raise Premise("cannot read source ledger blob")
        g(lane, "hash-object", "-w", "--stdin", data=data.stdout)

    # ---- premises -------------------------------------------------------
    if errata_blob is not None and (has_local(lane, errata_blob) != present):
        raise Premise(f"errata blob availability premise failed for {arm}")
    if correction is not None and has_local(lane, correction):
        raise Premise(f"correction object premise failed for {arm}")
    for repo in (lane, fleet):
        if g(repo, "rev-parse", "--show-object-format") != "sha1":
            raise Premise("repo is not sha1")
        if g(repo, "rev-parse", "--is-shallow-repository") != "false":
            raise Premise("repo is shallow")
        if g(repo, "rev-parse", "--show-prefix"):
            raise Premise("repo is not a top level")
    for oid in (cited, omitted):
        if g(lane, "cat-file", "-t", oid) != "commit":
            raise Premise(f"lane commit {oid} missing")
    if g(lane, "log", "--format=%H", "master") == "":
        raise Premise("audited history unreadable")
    if g(fleet, "cat-file", "-t", f"HEAD:{REL}") != "blob":
        raise Premise("fleet report blob missing")
    if g(fleet, "log", "--diff-filter=A", "--format=%at", "--", REL) != "2000":
        raise Premise("fleet first-add cutoff is not 2000")
    return {"arm": arm, "lane": str(lane), "fleet": str(fleet),
            "cited": cited, "omitted": omitted, "errata_blob": errata_blob,
            "errata_present": present, "correction": correction,
            "fake": FAKE}


ARMS = [
    "E1-ledger-present-complete",
    "E2-ledger-committed-blob-missing-promisor",
    "E3-ledger-committed-blob-missing-blobless",
    "E4-ledger-absent-from-tree",
    "E5-ledger-committed-blob-missing-no-promisor",
    "E6-ledger-present-row-mismatch",
    "E7-promisor-marked-complete",
    "E8-promisor-marked-ledger-correction-object-missing",
    "E9-ledger-correction-object-missing-no-promisor",
    "E10-promisor-marked-ledger-missing-no-defects",
    "E11-promisor-marked-ledger-present-no-defects",
    "E12-ledger-missing-no-defects-no-promisor",
    "E13-errata-corrected-missing-sha-plain",
    "E14-errata-corrected-missing-sha-promisor",
    "E15-blobless-lane-ledger-hydrated",
]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    out = Path(argv[0] if argv else "fixtures").resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    index = {}
    for arm in ARMS:
        tmp = out / arm
        tmp.mkdir()
        index[arm] = build(tmp, arm)
    (out / "index.json").write_text(
        json.dumps(index, indent=1, sort_keys=True) + "\n")
    print(json.dumps(index, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
