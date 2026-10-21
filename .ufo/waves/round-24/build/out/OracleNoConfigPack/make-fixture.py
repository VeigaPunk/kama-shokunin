#!/usr/bin/env python3
"""Round-24 oracle fixture recipe: promisor pack marker, no remotes, all local.

Builds a set of lane/fleet repository pairs under a root directory. Every
repository is created locally with `git init` + local commits; no clone, no
remote, no network, no transport process, no payload. The only difference
between a `full-*` arm and its `promisor-*` twin is one empty
`.git/objects/pack/pack-*.promisor` file next to the real pack.

Arms
  full-clean / promisor-clean          one cited lane commit
  full-omission / promisor-omission    plus one uncited pre-cutoff commit
  full-fabricated / promisor-fabricated report cites a nonexistent 40-hex
  tok-bool-maybe                       remote.origin.promisor=<invalid bool>
  tok-filter                           remote.origin.partialclonefilter=blob:none
  tok-extensions                       extensions.partialClone=origin

Usage: make-fixture.py --root DIR [--arms a,b,...] [--json]
Exit: 0 every built arm verified its premise; 2 a premise failed.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REL = ".ufo/reports/round-1/kama.md"
LANE = "kama"
FAKE = "1234567890abcdef1234567890abcdef12345678"
CITE_TIME = 1000
OMIT_TIME = 1500
REPORT_TIME = 2000


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


class Premise(Exception):
    pass


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


def canonical(root, omission=False, fabricated=False):
    """Lane with one cited round-1 commit; fleet report citing it."""
    lane, fleet = init(root / "lane"), init(root / "fleet")
    c1 = commit(lane, f"{LANE}-shokunin", CITE_TIME, "round-1: work")
    c2 = None
    if omission:
        c2 = commit(lane, f"{LANE}-shokunin", OMIT_TIME, "round-1: more")
    body = report([c1])
    if fabricated:
        body += b"\n## Notes\n\nsee " + FAKE.encode() + b"\n"
    commit(fleet, "fleet", REPORT_TIME, "round-1: report", REL, body)
    return {"lane": lane, "fleet": fleet, "cited": c1, "omitted": c2}


def repack(repo):
    """Local object packing only; no transport, no remote."""
    g(repo, "repack", "-a", "-d")
    packs = sorted((Path(repo) / ".git/objects/pack").glob("pack-*.pack"))
    if len(packs) != 1:
        raise Premise(f"{repo}: expected exactly one pack, got {packs}")
    return packs[0]


def add_marker(repo):
    """Paired promisor marker: an empty .promisor file beside the real pack.

    An empty promise list is what git itself writes when a promisor pack
    promises no missing object: every object of the pack is local."""
    pack = repack(repo)
    marker = pack.with_suffix(".promisor")
    marker.write_bytes(b"")
    return marker


def closure_missing(repo, rev="HEAD"):
    """Object ids the repo cannot serve for `rev` (promisor-aware listing)."""
    out = g(repo, "-c", "core.quotePath=false", "rev-list", "--objects",
            "--missing=print", "--no-object-names", rev, check=False)
    return [line for line in out.split("\n") if line.startswith("?")]


def add_missing_blob(repo, path="unrelated.txt", subject="unrelated note",
                     when=3000):
    """A post-report commit whose blob is removed again.

    The commit and its tree stay readable; only the blob is gone, so the
    object closure of the pinned root has exactly one hole and the audit
    never reads that file."""
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("unrelated payload\n", encoding="utf-8")
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", subject,
      GIT_AUTHOR_NAME="other", GIT_COMMITTER_NAME="other",
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    blob = g(repo, "rev-parse", f"HEAD:{path}")
    loose = Path(repo, ".git/objects", blob[:2], blob[2:])
    if not loose.exists():
        raise Premise(f"{repo}: blob {blob} is not loose")
    loose.unlink()
    return blob


def add_missing_report_blob(fleet):
    """The committed fleet report blob is removed: a required object.

    The report is rewritten once (a fresh loose blob) and that blob is
    deleted; the first-add commit and the cutoff stay as they were."""
    report = Path(fleet, REL)
    report.write_bytes(report.read_bytes() + b"\n## Notes\n\nrewritten\n")
    g(fleet, "add", "--", REL)
    stamp = f"@{2500} +0000"
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
      "round-1: report rewrite", GIT_AUTHOR_NAME="fleet",
      GIT_COMMITTER_NAME="fleet", GIT_AUTHOR_DATE=stamp,
      GIT_COMMITTER_DATE=stamp)
    blob = g(fleet, "rev-parse", f"HEAD:{REL}")
    loose = Path(fleet, ".git/objects", blob[:2], blob[2:])
    if not loose.exists():
        raise Premise(f"{fleet}: report blob {blob} is not loose")
    loose.unlink()
    return blob


def verify(arm, lane, fleet, marker_expected, tokens=(),
           missing_repos=(), missing_blobs=()):
    """Premise checks: the arm really is what it claims to be."""
    for repo in (lane, fleet):
        top = g(repo, "rev-parse", "--show-toplevel")
        if Path(top).resolve() != Path(repo).resolve():
            raise Premise(f"{repo}: not a repository top level")
        if g(repo, "rev-parse", "--is-shallow-repository") != "false":
            raise Premise(f"{repo}: shallow")
        if g(repo, "rev-parse", "--show-object-format") != "sha1":
            raise Premise(f"{repo}: not sha1")
        if repo not in missing_repos:
            remotes = g(repo, "config", "--get-regexp", "^remote\\.",
                        check=False)
            if remotes:
                raise Premise(f"{repo}: unexpected remote config {remotes!r}")
            if closure_missing(repo):
                raise Premise(f"{repo}: closure incomplete: "
                              f"{closure_missing(repo)}")
        else:
            if not closure_missing(repo):
                raise Premise(f"{repo}: expected a missing object")
    for repo, blob in missing_blobs:
        rc = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", blob],
                            capture_output=True, env=env()).returncode
        if rc == 0:
            raise Premise(f"{repo}: blob {blob} is still present")
    packdir = Path(lane) / ".git/objects/pack"
    markers = sorted(p.name for p in packdir.glob("*.promisor"))
    if marker_expected:
        if len(markers) != 1:
            raise Premise(f"{lane}: expected one .promisor marker, got {markers}")
        if not Path(packdir, markers[0].replace(".promisor", ".pack")).exists():
            raise Premise(f"{lane}: marker {markers[0]} is unpaired")
    elif markers:
        raise Premise(f"{lane}: unexpected .promisor marker {markers}")
    for key, value in tokens:
        g(lane, "config", key, value)
    return {"markers": markers}


ARMS = {
    # primary: paired promisor marker, no remotes, all contents local
    "full-clean": dict(omission=False, fabricated=False, marker=False),
    "promisor-clean": dict(omission=False, fabricated=False, marker=True),
    "full-omission": dict(omission=True, fabricated=False, marker=False),
    "promisor-omission": dict(omission=True, fabricated=False, marker=True),
    "full-fabricated": dict(omission=False, fabricated=True, marker=False),
    "promisor-fabricated": dict(omission=False, fabricated=True, marker=True),
    # unknown / misleading promisor tokens, no remote, all contents local
    "tok-bool-maybe": dict(omission=False, fabricated=False, marker=False,
                           tokens=(("remote.origin.promisor", "maybe"),)),
    "tok-filter": dict(omission=False, fabricated=False, marker=False,
                       tokens=(("remote.origin.partialclonefilter", "blob:none"),)),
    "tok-extensions": dict(omission=False, fabricated=False, marker=False,
                           tokens=(("extensions.partialClone", "origin"),)),
    # adjacent safety arm: promisor state plus a transport that must not run
    "promisor-hostile-ssh": dict(omission=False, fabricated=False, marker=True,
                                 hostile=True),
    # adjacent calibration probes: an unavailable object
    "full-missing-unrelated-blob": dict(omission=False, fabricated=False,
                                        marker=False, missing_blob=True),
    "promisor-missing-unrelated-blob": dict(omission=False, fabricated=False,
                                            marker=True, missing_blob=True),
    "promisor-missing-report-blob": dict(omission=False, fabricated=False,
                                         marker=True, missing_report=True),
}


def build(root, name):
    spec = ARMS[name]
    arm = root / name
    if arm.exists():
        shutil.rmtree(arm)
    arm.mkdir(parents=True)
    info = canonical(arm, omission=spec["omission"],
                     fabricated=spec["fabricated"])
    lane, fleet = info["lane"], info["fleet"]
    if spec["marker"]:
        add_marker(lane)
        add_marker(fleet)
    else:
        repack(lane)
        repack(fleet)
    missing_blobs = []
    missing_repos = []
    if spec.get("missing_blob"):
        blob = add_missing_blob(lane)
        missing_blobs.append((lane, blob))
        missing_repos.append(lane)
    if spec.get("missing_report"):
        blob = add_missing_report_blob(fleet)
        missing_blobs.append((fleet, blob))
        missing_repos.append(fleet)
    tokens = list(spec.get("tokens", ()))
    marker_file = None
    if spec.get("hostile"):
        marker_file = arm / "transport-ran"
        tokens += [("remote.origin.url", "ssh://example.invalid/x.git"),
                   ("remote.origin.promisor", "true"),
                   ("extensions.partialClone", "origin"),
                   ("core.sshCommand", f"touch {marker_file}; false")]
    facts = verify(name, lane, fleet, spec["marker"], tokens,
                   missing_repos, missing_blobs)
    facts.update({"arm": name, "lane": str(lane), "fleet": str(fleet),
                  "cited": info["cited"], "omitted": info["omitted"],
                  "fake": FAKE,
                  "missing_blobs": [b for _, b in missing_blobs],
                  "transport_marker": str(marker_file) if marker_file else None,
                  "tokens": [list(t) for t in tokens]})
    return facts


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True)
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    facts = []
    try:
        for name in args.arms.split(","):
            facts.append(build(root, name.strip()))
    except Premise as exc:
        print(f"could-not-evaluate: fixture premise: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(facts, indent=1, sort_keys=True))
    else:
        for f in facts:
            print(f"{f['arm']}: lane={f['lane']} fleet={f['fleet']} "
                  f"cited={f['cited']} omitted={f['omitted']} "
                  f"markers={f['markers']} tokens={f['tokens']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
