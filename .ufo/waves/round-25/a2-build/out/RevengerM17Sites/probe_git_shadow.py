#!/usr/bin/env python3
"""Probe how git 2.56 resolves a token that a same-named ref shadows.

Runs only inside a throwaway repository under the scratch directory. The
predicate mirrors tools/report-landing-audit.py: a token is refused when the
object id git prints does not start with the token (`not startswith(token)`).
"""
import os
import pathlib
import shutil
import subprocess

SCRATCH = pathlib.Path("/fast/scratch/hyaku/kama-r25a2/RevengerM17Sites/gittest")
shutil.rmtree(SCRATCH, ignore_errors=True)
SCRATCH.mkdir(parents=True)
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@x",
           GIT_AUTHOR_DATE="2000-01-01T00:00:00Z", GIT_COMMITTER_DATE="2000-01-01T00:00:00Z")


def git(*args, stdin=None):
    data = stdin.encode() if isinstance(stdin, str) else None
    r = subprocess.run(["git", "-C", str(SCRATCH), "--no-optional-locks", *args],
                       input=data, capture_output=True, env=ENV)
    return r.returncode, r.stdout.decode(errors="replace").strip(), r.stderr.decode(errors="replace").strip()


print(subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip())
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
git("init", "-q")
_, C, _ = git("commit-tree", EMPTY_TREE, "-m", "C")
_, D, _ = git("commit-tree", EMPTY_TREE, "-m", "D")
print("C", C, "D", D)
print("C starts with deadbee1:", C.startswith("deadbee1"))
git("update-ref", "refs/tags/deadbee1", C)
git("update-ref", f"refs/tags/{C}", D)

print("\n## abbreviation shadowed by a tag (F13 shape)")
for tok in ["deadbee1", "deadbee1^{commit}"]:
    rc, out, err = git("cat-file", "--batch-check", stdin=f"{tok}\n")
    oid = out.split(" ")[0]
    print(f"token={tok!r} rc={rc} line={out!r} stderr={err[:90]!r}")
    print(f"  refusal predicate fires: {not oid.startswith('deadbee1') and not out.endswith('missing')}")

print("\n## full 40-hex token with a same-named tag pointing at D")
rc, out, err = git("cat-file", "--batch-check", stdin=f"{C}\n")
oid = out.split(" ")[0]
print(f"token=C rc={rc} line={out!r} oid==C:{oid == C} oid==D:{oid == D}")
print(f"  refusal predicate fires: {not oid.startswith(C)}")
