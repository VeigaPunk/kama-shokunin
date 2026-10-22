#!/usr/bin/env python3
"""Bounded offline fixture: cross-repository merging of lookup() in
tools/report-landing-audit.py at pinned commit 2e254a1763a9c08aa07fc53081287f506c447d84.

Two throwaway repos (A = stands for the lane store, first in stores order;
B = stands for the fleet store, second). Facts placed deliberately:
  * B holds a blob (known-present, fails commit peeling)      -> wrongtype
  * B holds an annotated tag pointing at that blob            -> wrongtype
  * B holds an annotated tag whose target commit was deleted -> unknown
  * B holds a plain commit                                   -> found
  * A holds an ambiguous 4-hex prefix, B resolves it uniquely
No network, no transport, no execution payloads, no production tree touched.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

TOOL = Path(sys.argv[1]).resolve()
ROOT = Path(sys.argv[2]).resolve()
os.environ["TMPDIR"] = str(ROOT)
os.environ["GIT_CONFIG_GLOBAL"] = os.devnull
os.environ["GIT_CONFIG_NOSYSTEM"] = "1"

spec = importlib.util.spec_from_file_location("rla", TOOL)
rla = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rla)


def git(repo, *args, **kw):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(rla.git_env(**kw.get("env", {})))
    p = subprocess.run(["git", *rla.GIT_ISOLATION, "-C", str(repo), *args],
                       capture_output=True, env=env, text=True,
                       input=kw.get("input"))
    if p.returncode != 0:
        raise SystemExit(f"git {args} failed: {p.stderr}")
    return p.stdout


A = ROOT / "A"
B = ROOT / "B"
for repo in (A, B):
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, "init", "-q", "-b", "master")
    git(repo, "config", "user.email", "a@x")
    git(repo, "config", "user.name", "a")
    (repo / "f").write_text("hello\n")
    git(repo, "add", "f")
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "c1")

# A: an ambiguous 4-hex prefix (two blobs sharing the first 4 hex chars)
ids = []
for i in range(3000):
    ids.append(git(A, "hash-object", "-w", "--stdin", input=f"ambig {i}\n").strip())
seen = {}
ambig = None
ambig_pair = []
for i, oid in enumerate(ids):
    if oid[:4] in seen and seen[oid[:4]] != oid:
        ambig = oid[:4]
        ambig_pair = [(seen[ambig[:4]], None), (oid, i)]
        break
    seen[oid[:4]] = oid
# one of the two colliding objects is copied into B (same content -> same sha):
# B then resolves the prefix uniquely while A stays ambiguous
if ambig:
    first_oid = seen[ambig[:4]]
    first_idx = ids.index(first_oid)
    git(B, "hash-object", "-w", "--stdin", input=f"ambig {first_idx}\n")
    print(f"B holds a copy of A's colliding object {first_oid} "
          f"(prefix {ambig})")

# B: a plain blob (known-present, not a commit)
blob = git(B, "hash-object", "-w", "--stdin", input="just a blob\n").strip()
# B: annotated tag -> blob  (wrong type under a commit peel)
git(B, "tag", "-a", "-m", "tag-to-blob", "v-blob", blob)
tag_blob = git(B, "rev-parse", "v-blob").strip()
# B: annotated tag -> commit whose object is then deleted (unreadable target)
target = git(B, "commit-tree", git(B, "rev-parse", "HEAD^{tree}").strip(),
             "-m", "target").strip()
git(B, "tag", "-a", "-m", "tag-to-gone", "v-gone", target)
tag_gone = git(B, "rev-parse", "v-gone").strip()
objdir = Path(git(B, "rev-parse", "--git-path", "objects").strip())
objdir = (B / objdir) if not objdir.is_absolute() else objdir
(objdir / target[:2] / target[2:]).unlink()
commit_b = git(B, "rev-parse", "HEAD").strip()
commit_a = git(A, "rev-parse", "HEAD").strip()

print("== fixture facts ==")
for name, val in (("A-commit", commit_a), ("B-commit", commit_b),
                  ("B-blob", blob), ("B-tag->blob", tag_blob),
                  ("B-tag->gone-commit", tag_gone), ("A-ambiguous-4hex", ambig)):
    print(f"{name}={val}")

print("\n== raw git cat-file --batch-check probes (store B) ==")
for expr in (blob, f"{blob}^{{commit}}", f"{blob}^{{}}", tag_blob,
             f"{tag_blob}^{{commit}}", f"{tag_blob}^{{}}", tag_gone,
             f"{tag_gone}^{{commit}}", f"{tag_gone}^{{}}", commit_b,
             f"{commit_b}^{{commit}}"):
    out = git(B, "cat-file", "--batch-check", input=expr + "\n").strip()
    print(f"  {expr!r:60} -> {out!r}")
print("  (B) absent token:", repr(git(B, "cat-file", "--batch-check",
                                    input="0" * 40 + "\n").strip()))
print("  (A) ambiguous prefix bare:",
      repr(git(A, "cat-file", "--batch-check", input=ambig + "\n").strip()))
print("  (A) ambiguous prefix peeled:",
      repr(git(A, "cat-file", "--batch-check",
               input=f"{ambig}^{{commit}}\n").strip()))

# a dangling (unreachable but present) commit in A
dangling = git(A, "commit-tree", git(A, "rev-parse", "HEAD^{tree}").strip(),
               "-m", "dangling").strip()
print("  (A) dangling commit bare:",
      repr(git(A, "cat-file", "--batch-check", input=dangling + "\n").strip()))
print("  (A) dangling commit peeled:",
      repr(git(A, "cat-file", "--batch-check",
               input=f"{dangling}^{{commit}}\n").strip()))

storeA = rla.RepoStore(A, commit_a)
storeB = rla.RepoStore(B, commit_b)
AB = (storeA, storeB)
BA = (storeB, storeA)

cases = [
    ("blob-only-in-B (expect wrongtype)", [blob]),
    ("tag->blob-only-in-B (expect wrongtype)", [tag_blob]),
    ("tag->gone-only-in-B (expect unknown)", [tag_gone]),
    ("commit-only-in-B (expect found)", [commit_b]),
    ("ambiguous-in-A-only (expect ambiguous)", [ambig]),
    ("ambiguous-in-A-one-copy-in-B", [ambig]),
    ("ambiguous-in-A-resolved-in-B", [ambig]),
    ("dangling-commit-in-A (expect found)", [dangling]),
]
print("\n== lookup() results ==")
for label, tokens in cases:
    print(f"-- {label}")
    for order_name, order in (("stores=(A,B)", AB), ("stores=(B,A)", BA)):
        for peel in ("", "^{commit}"):
            try:
                res = rla.lookup(order, tokens, peel)
            except rla.EvalError as exc:
                res = f"EvalError: {exc}"
            print(f"   {order_name} peel={peel!r:10} -> {res}")

print("\n== verdict consequence of lookup() state ==")
for label, tokens in cases:
    for order_name, order in (("stores=(A,B)", AB), ("stores=(B,A)", BA)):
        for peel in ("", "^{commit}"):
            try:
                status = rla.lookup(order, tokens, peel)
            except rla.EvalError as exc:
                print(f"   {label} {order_name} peel={peel!r}: EvalError {exc}")
                continue
            try:
                rla.refuse_unknown(1, status, AB)
                effect = "no refusal"
            except rla.EvalError as exc:
                effect = f"REFUSE exit2: {exc}"
            print(f"   {label} {order_name} peel={peel!r}: {status} -> {effect}")

print("\n== end-to-end audit of a landed citation of the blob (fleet-only blob) ==")
print("   (the fleet store is the second store in run(): stores = (lane, fleet))")
