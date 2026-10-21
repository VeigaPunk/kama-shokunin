#!/usr/bin/env python3
"""Offline partial-clone availability probe (benign, local, file:// only).

Question the round-24 repair must answer: in a promisor-backed repository,
what does the closure check's own git invocation observe for an object that is
not available locally, and does it observe it WITHOUT fetching?

Setup: a local origin repo, then `git clone --filter=blob:none` (blobless) and
`git clone --filter=tree:0` (treeless) from it over file://. No network host,
no repo-configured program, no credential, no marker script. The promisor URL
is a local directory that is *removed* after the clone, so a lazy fetch could
not succeed even if attempted -- which makes "did it try?" observable.

Measured with exactly the tool's isolation flags:
  git --no-replace-objects --no-lazy-fetch -c ... -C <repo> ...
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ISOLATION = ["--no-replace-objects", "--no-lazy-fetch",
             "-c", "i18n.logOutputEncoding=UTF-8",
             "-c", "log.follow=false", "-c", "log.showRoot=true",
             "-c", "log.showSignature=false", "-c", "log.mailmap=false"]
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull,
       "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_AUTHOR_NAME": "x", "GIT_COMMITTER_NAME": "x",
       "GIT_AUTHOR_EMAIL": "a@x", "GIT_COMMITTER_EMAIL": "a@x",
       "GIT_AUTHOR_DATE": "@1000 +0000", "GIT_COMMITTER_DATE": "@1000 +0000"}
TMP = Path(sys.argv[1] if len(sys.argv) > 1 else
           "/fast/scratch/hyaku/kama-r24")
TMP.mkdir(parents=True, exist_ok=True)


def run(argv, cwd=None, env=ENV, stdin=None):
    if isinstance(stdin, str):
        stdin = stdin.encode()
    return subprocess.run(argv, cwd=cwd, env=env, capture_output=True,
                          input=stdin)


def g(repo, *args, stdin=None):
    return run(["git", *ISOLATION, "-C", str(repo), *args], stdin=stdin)


root = Path(tempfile.mkdtemp(prefix="rfm-partial-", dir=TMP))
origin = root / "origin"
origin.mkdir()
run(["git", "init", "-q", "-b", "master", str(origin)])
(origin / "data.txt").write_text("payload\n", encoding="utf-8")
run(["git", "-C", str(origin), "add", "data.txt"])
run(["git", "-C", str(origin), "-c", "commit.gpgsign=false", "commit", "-q",
     "-m", "round-1: work"])
blob = run(["git", "-C", str(origin), "rev-parse", "HEAD:data.txt"]).stdout
blob = blob.decode().strip()
# a second commit changes the file, so the checkout needs only the NEW blob
# and the OLD blob stays absent from a blobless clone
(origin / "data.txt").write_text("payload v2\n", encoding="utf-8")
run(["git", "-C", str(origin), "add", "data.txt"])
run(["git", "-C", str(origin), "-c", "commit.gpgsign=false", "commit", "-q",
     "-m", "round-1: more"])
newblob = run(["git", "-C", str(origin), "rev-parse", "HEAD:data.txt"]).stdout
newblob = newblob.decode().strip()
tip = run(["git", "-C", str(origin), "rev-parse", "HEAD"]).stdout.decode().strip()
oldtree = run(["git", "-C", str(origin), "rev-parse",
               "8467bd682fa8b9ce97f8fa1eec27096d3c0158b6^{tree}"]).stdout
oldtree = oldtree.decode().strip()
print(f"# origin tip={tip}")
print(f"# origin blob(old, checkout does not need it)={blob}")
print(f"# origin blob(new, checkout needs it)={newblob}")
print(f"# scratch={root}")
print()

# clone first, then remove the promisor payload, so that any lazy fetch
# attempted during the probes must fail
run(["git", "-C", str(origin), "config", "uploadpack.allowFilter", "true"])
run(["git", "-C", str(origin), "config", "uploadpack.allowAnySHA1InWant",
     "true"])
clone = root / "blobless"
rc = run(["git", "clone", "-q", "--filter=blob:none", "--no-local",
          f"file://{root}/origin", str(clone)])
print(f"# blobless clone rc={rc.returncode} "
      f"stderr={rc.stderr.decode(errors='replace').strip()[:160]!r}")
clone2 = root / "treeless"
rc = run(["git", "clone", "-q", "--filter=tree:0", "--no-local",
          f"file://{root}/origin", str(clone2)])
print(f"# treeless clone rc={rc.returncode} "
      f"stderr={rc.stderr.decode(errors='replace').strip()[:160]!r}")

# remove the promisor payload so that any lazy fetch must fail
shutil.rmtree(origin)
print("# origin removed: a lazy fetch could not succeed even if attempted")
print()


def packs(repo):
    d = Path(repo, ".git/objects/pack")
    return sorted(p.name for p in d.iterdir()) if d.is_dir() else []


def probe(label, repo, kind):
    print(f"## {label} ({repo.name})")
    cfg = run(["git", "-C", str(repo), "config", "--local", "--list"]).stdout
    for line in cfg.decode(errors="replace").splitlines():
        if "promisor" in line or "partialclone" in line or "repositoryformat" \
                in line:
            print(f"  config: {line}")
    before = packs(repo)
    print(f"  packs before: {before}")
    if kind == "blob":
        pr = g(repo, "cat-file", "--batch-check", stdin=f"{blob}\n")
        print(f"  cat-file --batch-check(old blob) rc={pr.returncode} "
              f"stdout={pr.stdout.decode(errors='replace').strip()!r} "
              f"stderr={pr.stderr.decode(errors='replace').strip()[:80]!r}")
        pr3 = g(repo, "cat-file", "--batch-check", stdin=f"{newblob}\n")
        print(f"  cat-file --batch-check(new blob) rc={pr3.returncode} "
              f"stdout={pr3.stdout.decode(errors='replace').strip()!r}")
        pr2 = g(repo, "cat-file", "--batch-check", stdin=f"{tip}\n")
        print(f"  cat-file --batch-check(commit) rc={pr2.returncode} "
              f"stdout={pr2.stdout.decode(errors='replace').strip()!r}")
    else:
        pr = g(repo, "log", "-z", "--format=%H%x00%an%x00%at%x00%s", "master")
        print(f"  git log rc={pr.returncode} "
              f"stdout={pr.stdout.decode(errors='replace')[:120]!r} "
              f"stderr={pr.stderr.decode(errors='replace').strip()[:120]!r}")
        pr2 = g(repo, "cat-file", "--batch-check", stdin=f"{blob}\n")
        print(f"  cat-file --batch-check(blob) rc={pr2.returncode} "
              f"stdout={pr2.stdout.decode(errors='replace').strip()!r} "
              f"stderr={pr2.stderr.decode(errors='replace').strip()[:80]!r}")
        pr3 = g(repo, "ls-tree", "master", "--", "data.txt")
        print(f"  ls-tree rc={pr3.returncode} "
              f"stdout={pr3.stdout.decode(errors='replace').strip()!r} "
              f"stderr={pr3.stderr.decode(errors='replace').strip()[:80]!r}")
        # report_cutoff()'s exact command: path-limited log needs trees
        pr4 = g(repo, "log", "--diff-filter=A", "--format=%at", "--",
                "data.txt")
        print(f"  report_cutoff-shaped log rc={pr4.returncode} "
              f"stdout={pr4.stdout.decode(errors='replace').strip()!r} "
              f"stderr={pr4.stderr.decode(errors='replace').strip()[:80]!r}")
        # audit_round()'s fleet-report read: git show HEAD:<rel>
        pr5 = g(repo, "show", "HEAD:data.txt")
        print(f"  git show HEAD:<rel> rc={pr5.returncode} "
              f"stdout={pr5.stdout.decode(errors='replace').strip()[:60]!r} "
              f"stderr={pr5.stderr.decode(errors='replace').strip()[:80]!r}")
        # the older commit's tree: is it locally available?
        pr6 = g(repo, "cat-file", "--batch-check", stdin=f"{oldtree}\n")
        print(f"  old commit tree {oldtree} -> rc={pr6.returncode} "
              f"stdout={pr6.stdout.decode(errors='replace').strip()!r}")
    after = packs(repo)
    print(f"  packs after:  {after}")
    print(f"  fetch attempted (pack count grew): {len(after) > len(before)}")
    print()


clone = root / "blobless"
run(["git", "clone", "-q", "--filter=blob:none", "--no-local",
     f"file://{root}/origin", str(clone)])
probe("blobless partial clone", clone, "blob")

clone2 = root / "treeless"
run(["git", "clone", "-q", "--filter=tree:0", "--no-local",
     f"file://{root}/origin", str(clone2)])
probe("treeless partial clone", clone2, "tree")
