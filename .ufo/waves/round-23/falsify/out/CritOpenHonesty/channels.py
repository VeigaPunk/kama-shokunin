#!/usr/bin/env python3
"""CritOpenHonesty: probe repository-local channels not named in the round-23
lesson boundaries or the auditor docstring. Each case builds a fresh /tmp
lane+fleet pair, runs the auditor once on the baseline and once with exactly
one repository-local mutation, and prints both exits plus defect lines.

usage: channels.py AUDITOR [case ...]   (cases: disambiguate loose graph renames)
"""
import hashlib
import multiprocessing as mp
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

AUDITOR = Path(sys.argv[1]).resolve()
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")


def g(repo, *args, when=None, stdin=None):
    env = dict(ENV, GIT_AUTHOR_NAME="kama-shokunin", GIT_AUTHOR_EMAIL="k@x",
               GIT_COMMITTER_NAME="kama-shokunin", GIT_COMMITTER_EMAIL="k@x")
    if when is not None:
        env.update(GIT_AUTHOR_DATE=f"@{when} +0000",
                   GIT_COMMITTER_DATE=f"@{when} +0000")
    p = subprocess.run(["git", "-C", str(repo), *args], env=env, input=stdin,
                       capture_output=True, text=True)
    if p.returncode:
        sys.exit(f"premise failed: git {args}: {p.stderr.strip()}")
    return p.stdout.strip()


def commit(repo, msg, when, path="f"):
    with open(Path(repo, path), "a") as fh:
        fh.write(msg + "\n")
    g(repo, "add", path)
    g(repo, "commit", "-q", "-m", msg, when=when)
    return g(repo, "rev-parse", "HEAD")


def pair(tmp):
    lane, fleet = Path(tmp, "lane"), Path(tmp, "fleet")
    for r in (lane, fleet):
        r.mkdir()
        g(r, "init", "-q", "-b", "master")
    return lane, fleet


def report(fleet, body, when=1200, path=".ufo/reports/round-1/kama.md"):
    p = Path(fleet, path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)
    g(fleet, "add", path)
    g(fleet, "commit", "-q", "-m", "round-1: report", when=when)


def audit(lane, fleet):
    p = subprocess.run([sys.executable, str(AUDITOR), "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1",
                        "--no-errata"], env=ENV, capture_output=True,
                       text=True, timeout=60)
    return p.returncode, (p.stdout + p.stderr).strip().replace("\n", " | ")


def show(case, before, after, note):
    print(f"[{case}] baseline exit={before[0]} :: {before[1]}")
    print(f"[{case}] mutated  exit={after[0]} :: {after[1]}")
    print(f"[{case}] {'VERDICT CHANGED' if before[0] != after[0] else 'same exit'}"
          f" -- {note}")


# ---------------------------------------------------------------- collision
def _search(args):
    target, start, step = args
    nib = len(target)
    want = bytes.fromhex(target[:nib - nib % 2])
    odd = int(target[-1], 16) if nib % 2 else None
    base = hashlib.sha1(b"blob 22\0collide-")
    n = start
    while True:
        h = base.copy()
        h.update(b"%012d\n" % n)
        d = h.digest()
        if d.startswith(want) and (odd is None or d[len(want)] >> 4 == odd):
            return n
        n += step


def collide_blob(prefix):
    """Content of a blob whose OID starts with `prefix` (brute force)."""
    jobs = mp.cpu_count()
    with mp.Pool(jobs) as pool:
        for n in pool.imap_unordered(_search, [(prefix, i, jobs)
                                               for i in range(jobs)]):
            pool.terminate()
            return b"collide-%012d\n" % n


# ---------------------------------------------------------------- cases
def case_disambiguate(tmp):
    """core.disambiguate in the lane config resolves an ambiguous Landed
    abbreviation to the commit: landed-ambiguous disappears."""
    lane, fleet = pair(tmp)
    a = commit(lane, "round-1: work", 1000)
    short = a[:7]
    if not any(c.isalpha() for c in short) or not any(c.isdigit() for c in short):
        short = a[:8]
    blob = collide_blob(short)
    oid = g(lane, "hash-object", "-w", "--stdin", stdin=blob.decode())
    assert oid.startswith(short), (oid, short)
    assert g(lane, "cat-file", "-t", a) == "commit"
    report(fleet, f"## Landed changes\n- `{short}` work\n")
    before = audit(lane, fleet)
    g(lane, "config", "core.disambiguate", "committish")
    after = audit(lane, fleet)
    show("disambiguate", before, after,
         f"lane .git/config core.disambiguate=committish; {short} = commit {a[:12]} + blob {oid[:12]}")


def case_loose(tmp):
    """A loose object file stored under a foreign name: cat-file
    --batch-check reads only its header, so an uncited/unresolvable full
    hash in the report becomes 'found'."""
    lane, fleet = pair(tmp)
    a = commit(lane, "round-1: work", 1000)
    fake = "c0ffee" + "0" * 33 + "1"
    report(fleet, f"## Work performed\nmeasured at {fake}\n"
                  f"## Landed changes\n- `{a[:10]}` work\n")
    before = audit(lane, fleet)
    src = Path(lane, ".git/objects", a[:2], a[2:])
    dst = Path(lane, ".git/objects", fake[:2], fake[2:])
    dst.parent.mkdir(exist_ok=True)
    shutil.copyfile(src, dst)
    after = audit(lane, fleet)
    show("loose", before, after,
         f"lane .git/objects/{fake[:2]}/{fake[2:]} = copy of loose commit {a[:12]}")


def _rewrite_graph(path, child, new_parent):
    """Point `child`'s first parent at `new_parent` in a commit-graph file
    and refresh the trailing SHA-1."""
    data = bytearray(path.read_bytes())
    assert data[:4] == b"CGPH"
    nchunks = data[6]
    toc = {}
    for i in range(nchunks + 1):
        cid, off = struct.unpack(">4sQ", data[8 + 12 * i:8 + 12 * i + 12])
        toc[cid] = off
    fanout, oids, cdat = toc[b"OIDF"], toc[b"OIDL"],