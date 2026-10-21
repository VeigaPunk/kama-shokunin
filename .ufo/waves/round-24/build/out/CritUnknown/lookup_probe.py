#!/usr/bin/env python3
"""Offline probe: the auditor's lookup() over hand-built promisor fixtures,
plus a short-prefix blob/commit collision to show how a commit that exists
only on the promisor side changes the peeled answer. Usage: ROOT PROBE_ROOT"""
import hashlib
import importlib.util
import itertools
import os
from pathlib import Path
import shutil
import subprocess
import sys

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
spec = importlib.util.spec_from_file_location(
    "audit", LANE / "tools/report-landing-audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

root, probe = Path(sys.argv[1]), Path(sys.argv[2])
G = lambda repo, *a, **k: audit.git(repo, *a, **k)


def ids(repo):
    rp = lambda r: G(repo, "rev-parse", r).strip()
    return {"C1": rp("HEAD~2"), "C2": rp("HEAD~1"), "BA": rp("HEAD:a"),
            "TAG": rp("t1"), "TREE": rp("HEAD^{tree}"),
            "NEVER": "0123456789abcdef0123456789abcdef01234567"}


o = ids(probe / "Lfull")
print("## lookup() over probe fixtures (bare, then ^{commit})")
for name in ("Lfull", "Lmark", "Lc1", "Ltag", "Lbare"):
    repo = probe / name
    toks = {k: v for k, v in o.items()}
    toks["BA9"] = o["BA"][:9]
    inv = {v: k for k, v in toks.items()}
    bare = audit.lookup((repo,), list(toks.values()))
    peel = audit.lookup((repo,), list(toks.values()), "^{commit}")
    print(name, "bare:", {inv[t]: s for t, s in sorted(bare.items(), key=lambda x: inv[x[0]])})
    print(name, "peel:", {inv[t]: s for t, s in sorted(peel.items(), key=lambda x: inv[x[0]])})
# second repository: Lc1 lacks C1, Lfull holds it
print("cross-repo (Lc1, Lfull) peel C1:",
      audit.lookup((probe / "Lc1", probe / "Lfull"), [o["C1"]], "^{commit}"))
print("cross-repo (Lc1, Lfull) bare BA^{commit} wrongtype:",
      audit.lookup((probe / "Lc1", probe / "Lfull"), [o["BA"]], "^{commit}"))

print("\n## short-prefix collision: blob + commit sharing a 5-hex prefix")
col = root / "collide"
shutil.rmtree(col, ignore_errors=True)
G(root, "init", "-q", "-b", "main", str(col))
assert G(col, "rev-parse", "--show-toplevel").strip() == str(col)
env = audit.git_env(GIT_AUTHOR_NAME="kama-shokunin", GIT_COMMITTER_NAME="kama-shokunin",
                    GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
                    GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000")
(col / "f").write_text("x\n")
G(col, "add", "f", env=env)
G(col, "-c", "commit.gpgsign=false", "commit", "-qm", "round-1: base", env=env)
base = G(col, "rev-parse", "HEAD").strip()
tree = G(col, "rev-parse", "HEAD^{tree}").strip()
# a dangling commit (not on the branch) whose prefix a blob will share
body = (f"tree {tree}\nparent {base}\nauthor kama-shokunin <a@x> 1500 +0000\n"
        f"committer kama-shokunin <a@x> 1500 +0000\n\nround-1: side\n").encode()
side = G(col, "hash-object", "-t", "commit", "-w", "--stdin",
         stdin=body.decode()).strip()
P = 5
pfx = side[:P]
for n in itertools.count():
    data = f"collide {n}\n".encode()
    if hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest().startswith(pfx):
        break
blob = G(col, "hash-object", "-w", "--stdin", stdin=data.decode()).strip()
assert blob.startswith(pfx) and blob != side
print("side commit", side, "blob", blob, "prefix", pfx)
print("full clone bare:", audit.lookup((col,), [pfx]))
print("full clone peel:", audit.lookup((col,), [pfx], "^{commit}"))
# drop the side commit into "promised" state: repack without it, mark promisor
pd = col / ".git/objects/pack"
G(col, "repack", "-adq")
keep = [l for l in G(col, "cat-file", "--batch-all-objects",
                     "--batch-check=%(objectname)").split() if l != side]
new = root / "collide.new"
shutil.rmtree(new, ignore_errors=True)
new.mkdir()
h = G(col, "pack-objects", "-q", str(new / "pack"), stdin="\n".join(keep) + "\n").strip()
for p in pd.glob("pack-*"):
    p.unlink()
for p in new.glob("pack-*"):
    p.rename(pd / p.name)
for d in (col / ".git/objects").iterdir():
    if len(d.name) == 2:
        shutil.rmtree(d)
assert audit.lookup((col,), [side]) == {side: "missing"}
(pd / f"pack-{h}.promisor").write_bytes(b"")
G(col, "config", "remote.origin.url", "/nonexistent")
G(col, "config", "remote.origin.promisor", "true")
G(col, "config", "extensions.partialclone", "origin")
print("promisor clone bare:", audit.lookup((col,), [pfx]))
print("promisor clone peel:", audit.lookup((col,), [pfx], "^{commit}"))
r = subprocess.run(["git", *audit.GIT_ISOLATION, "-C", str(col), "cat-file",
                    "--batch-check"], input=f"{pfx}^{{commit}}\n".encode(),
                   capture_output=True, env=audit.git_env())
print("promisor clone raw peel stdout:", r.stdout.decode().strip(),
      "| stderr:", r.stderr.decode().strip())
