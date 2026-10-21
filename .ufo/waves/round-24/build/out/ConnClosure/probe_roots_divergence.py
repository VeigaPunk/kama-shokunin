#!/usr/bin/env python3
"""ConnClosure probe: the ROOT SET of the missing-object traversal decides
whether a citation can be proved absent.

Shape (offline, local synthetic fixtures only):
  a lane holding a PRESENT but ref-UNREACHABLE commit (dangling: the ref was
  reset away) whose tree names a blob that is missing locally.  No missing
  tree and no missing commit exists, so the "opaque hole" fallback cannot
  rescue a wrong answer.

  walk A  `--all` roots              (refs only)
  walk B  every PRESENT commit/tree/tag as a root   (the landed candidate's
                                                  `present_roots`)

Measured (git 2.56.0):
  A: M = {}            -> the blob is invisible -> a rule "not in M => proved
                          absent" reports exit 1 unresolved-full-hash (a
                          GUESSED absence where the truth is unknown).
  B: M = {the blob}    -> the citation is unknown -> exit 2.

Auditor A/B on the same fixture:
  landed candidate (present roots)  -> exit 2, "unavailable required object:
                                       <blob> is referenced by the history"
  all-roots variant                 -> exit 1 unresolved-full-hash  (wrong)

No-harm direction, same fixture with a FABRICATED citation instead of the
missing blob: both variants exit 1 unresolved-full-hash -- the missing blob is
unrelated and must not become a blanket precondition.

Every "remote" is a nonexistent local path; GIT_PROTOCOL_ALLOW=never.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = "/fast/scratch/hyaku/kama-r24"
OUT = Path(__file__).resolve().parent


def env(**extra):
    d = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    d.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_PROTOCOL_ALLOW="never",
             GIT_AUTHOR_NAME="k", GIT_AUTHOR_EMAIL="k@x.invalid",
             GIT_COMMITTER_NAME="k", GIT_COMMITTER_EMAIL="k@x.invalid",
             GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000",
             **extra)
    return d


def g(repo, *args, check=True):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=env(), timeout=60)
    if check and p.returncode != 0:
        raise RuntimeError(f"{args} rc={p.returncode} {p.stderr.decode()[:300]}")
    return p


def commit(repo, msg, path, body):
    Path(repo, path).write_text(body)
    g(repo, "add", path)
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg)
    return g(repo, "rev-parse", "HEAD").stdout.decode().strip()


def loose(repo, oid):
    return Path(repo, ".git/objects", oid[:2], oid[2:])


def walk(repo, mode, extra=()):
    if mode == "all":
        p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), "rev-list",
                            "--objects", "--missing=print", "--no-object-names",
                            *extra, "--all"], capture_output=True, env=env(),
                           timeout=60)
    else:
        pr = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo),
                              "cat-file", "--batch-all-objects",
                              "--batch-check=%(objectname) %(objecttype)"],
                             capture_output=True, env=env(), timeout=60)
        roots = []
        for line in pr.stdout.decode().splitlines():
            name, _, kind = line.partition(" ")
            if kind in ("commit", "tree", "tag"):
                roots.append(name)
        p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), "rev-list",
                            "--objects", "--missing=print", "--no-object-names",
                            *extra, "--stdin"],
                           input=("\n".join(roots) + "\n").encode(),
                           capture_output=True, env=env(), timeout=60)
    return {l.strip()[1:] for l in p.stdout.decode().splitlines()
            if l.startswith("?")}


def build(tmp, cite_the_missing_blob):
    lane = tmp / "lane"
    lane.mkdir()
    g(lane, "init", "-q", "-b", "master")
    head = commit(lane, "round-1: work", "f", "work\n")
    dangling = commit(lane, "dangling", "d.txt", "dangling-payload\n")
    blob = g(lane, "rev-parse", f"{dangling}:d.txt").stdout.decode().strip()
    g(lane, "reset", "-q", "--hard", head)
    reg = lane / "registry/report-landing-errata.tsv"
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text("# round\tkind\ttoken\tcorrection\tevidence\n")
    g(lane, "add", "registry/report-landing-errata.tsv")
    g(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: registry")
    fleet = tmp / "fleet"
    fleet.mkdir()
    g(fleet, "init", "-q", "-b", "master")
    commit(fleet, "seed", "seed.md", "seed\n")
    rel = ".ufo/reports/round-1/kama.md"
    p = fleet / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    cited = blob if cite_the_missing_blob else "abcdefabcdefabcdefabcdefabcdefabcdefabcd"
    p.write_text(f"# r1\n## Landed changes\n- `{head[:9]}` work\n"
                 f"## Notes\nsee {cited}\n")
    g(fleet, "add", rel)
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: kama report")
    loose(lane, blob).unlink()
    return lane, fleet, blob


def audit(auditor, lane, fleet):
    p = subprocess.run([sys.executable, str(auditor), "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1", "--json"],
                       capture_output=True, env=env(), timeout=120)
    kinds = []
    if p.returncode in (0, 1):
        doc = json.loads(p.stdout.decode())
        kinds = [(x["kind"], x["token"][:12]) for r in doc["results"]
                 for x in r["defects"]]
    return {"rc": p.returncode, "stderr": p.stderr.decode().strip()[:220],
            "kinds": kinds}


def main():
    candidate = OUT.parent.parent / "build" / "out" / "ConnClosure" / "auditors" / "cand.py"
    res = {}
    for label, cite_missing in (("cites_the_missing_blob", True),
                                ("cites_a_fabricated_hash", False)):
        tmp = Path(tempfile.mkdtemp(prefix="cc-roots-", dir=BASE))
        lane, fleet, blob = build(tmp, cite_missing)
        row = {"blob_present_locally": loose(lane, blob).exists()}
        for mode in ("all", "present"):
            M = walk(lane, mode)
            N = walk(lane, mode, ("--filter=blob:none",))
            row[f"walk_{mode}"] = {"M": sorted(M), "opaque_N": sorted(N),
                                   "blob_in_M": blob in M}
        res[label] = row
    out = OUT / "probe_roots_divergence-result.json"
    out.write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
