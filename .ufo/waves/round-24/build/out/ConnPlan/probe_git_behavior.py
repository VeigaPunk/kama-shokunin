#!/usr/bin/env python3
"""Bounded offline probe of the git primitives the round-24 promisor repair
depends on.  No network: every repository is created locally, no remote is
ever contacted, and no promisor remote is configured (only the *metadata*
that marks a store as promisor-backed).  No command that could execute a
transport program is used.

Questions:
  Q1  cat-file --batch-check on an object deleted from a promisor-marked
      store: "missing" line (absence reported) or hard error?
  Q2  a deleted *unrelated* blob: does `git log -- <path>` still produce the
      path history (i.e. is whole-repo closure necessary)?
  Q3  a deleted *tree* needed by the path history: does `git log -- <path>`
      fail loudly (exit 2 for free) or silently truncate?
  Q4  a deleted *ancestor commit*: does `git log <tip>` fail loudly or
      silently truncate the history?
  Q5  `git rev-list --objects --missing=print --no-object-names <root>`
      output format for missing objects.
  Q6  does a missing object make `git cat-file --batch-check` attempt a
      lazy fetch under --no-lazy-fetch?  (marker file must stay absent)
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ISOLATION = ("--no-replace-objects", "--no-lazy-fetch",
             "-c", "i18n.logOutputEncoding=UTF-8",
             "-c", "log.follow=false", "-c", "log.showRoot=true",
             "-c", "log.showSignature=false", "-c", "log.mailmap=false")


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", **extra)
    return e


def g(repo, *args, stdin=None):
    p = subprocess.run(["git", *ISOLATION, "-C", str(repo), *args],
                       input=stdin.encode() if stdin else None,
                       capture_output=True, env=env(), timeout=30)
    return p.returncode, p.stdout.decode("utf-8", "replace"), \
        p.stderr.decode("utf-8", "replace").strip()


def gplain(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, env=env(), timeout=30)
    return p.returncode, p.stdout.decode("utf-8", "replace"), \
        p.stderr.decode("utf-8", "replace").strip()


def build(tmp, name):
    """repo with: f.txt (blob), d/g.txt (subtree), report path."""
    repo = Path(tmp, name)
    repo.mkdir(parents=True)
    gplain(repo, "init", "-q", "-b", "master")
    gplain(repo, "config", "user.name", "probe")
    gplain(repo, "config", "user.email", "probe@example.invalid")
    (repo / "f.txt").write_text("one\n")
    (repo / "d").mkdir()
    (repo / "d" / "g.txt").write_text("two\n")
    rep = repo / ".ufo" / "reports" / "round-1"
    rep.mkdir(parents=True)
    (rep / "kama.md").write_text("# r1\n## Landed changes (commits)\n- `deadbee1` x\n")
    for path in ("f.txt", "d/g.txt", ".ufo/reports/round-1/kama.md"):
        gplain(repo, "add", path)
    gplain(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: work")
    (repo / "f.txt").write_text("one\ntwo\n")
    gplain(repo, "add", "f.txt")
    gplain(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: more")
    # mark the store promisor-backed (metadata only; no remote is configured)
    gplain(repo, "config", "extensions.partialClone", "origin")
    gplain(repo, "config", "remote.origin.promisor", "true")
    return repo


def loose_path(repo, oid):
    return Path(repo, ".git", "objects", oid[:2], oid[2:])


def delete_object(repo, oid):
    p = loose_path(repo, oid)
    if not p.exists():
        return False
    p.unlink()
    return True


def show(label, value):
    print(f"--- {label}")
    print(value.rstrip() or "(empty)")


def main():
    out = []
    with tempfile.TemporaryDirectory(prefix="connplan-probe-") as tmp:
        # ---------- Q1/Q2: missing unrelated blob --------------------------
        repo = build(tmp, "blobless")
        rc, out_txt, _ = gplain(repo, "rev-parse", "--verify", "HEAD:f.txt")
        blob = out_txt.strip()
        rc, tree_txt, _ = gplain(repo, "rev-parse", "--verify", "HEAD^{tree}")
        ok = delete_object(repo, blob)
        print(f"Q1 setup: deleted blob {blob} ({ok})")
        rc, o, e = g(repo, "cat-file", "--batch-check", stdin=f"{blob}\n")
        show("Q1 cat-file --batch-check (deleted blob, promisor-marked)",
             f"rc={rc}\nstdout={o}\nstderr={e}")
        rc, o, e = g(repo, "log", "--diff-filter=A", "--format=%at", "--",
                    ".ufo/reports/round-1/kama.md")
        show("Q2 git log -- <report path> with unrelated blob deleted",
             f"rc={rc}\nstdout={o}\nstderr={e}")
        rc, o, e = g(repo, "log", "-z", "--format=%H%x00%an%x00%at%x00%s", "master")
        show("Q2b git log <tip> with unrelated blob deleted",
             f"rc={rc}\nstdout={o!r}\nstderr={e}")

        # ---------- Q3: missing tree needed by the path history ------------
        repo3 = build(tmp, "treeless")
        root = gplain(repo3, "rev-parse", "--verify", "HEAD^{tree}")[1].strip()
        ok = delete_object(repo3, root)
        print(f"Q3 setup: deleted root tree {root} ({ok})")
        rc, o, e = g(repo3, "log", "--diff-filter=A", "--format=%at", "--",
                     ".ufo/reports/round-1/kama.md")
        show("Q3 git log -- <report path> with root tree deleted",
             f"rc={rc}\nstdout={o}\nstderr={e}")
        rc, o, e = g(repo3, "log", "-z", "--format=%H%x00%an%x00%at%x00%s",
                     "master")
        show("Q3b git log <tip> (no path) with root tree deleted",
             f"rc={rc}\nstdout={o!r}\nstderr={e}")

        # ---------- Q4: missing ancestor commit ----------------------------
        repo4 = build(tmp, "commitless")
        rc, all_objs, _ = gplain(repo4, "rev-list", "--objects", "HEAD")
        commits = gplain(repo4, "rev-list", "HEAD")[1].split()
        oldest = commits[-1]
        ok = delete_object(repo4, oldest)
        print(f"Q4 setup: deleted ancestor commit {oldest} ({ok})")
        rc, o, e = g(repo4, "log", "-z", "--format=%H%x00%an%x00%at%x00%s",
                     "master")
        show("Q4 git log <tip> with ancestor commit deleted",
             f"rc={rc}\nstdout={o!r}\nstderr={e}")
        rc, o, e = g(repo4, "rev-list", "--objects", "--missing=print",
                     "--no-object-names", "master")
        show("Q5 rev-list --objects --missing=print --no-object-names",
             f"rc={rc}\nstdout={o}\nstderr={e}")

        # ---------- Q6: no transport program runs --------------------------
        repo6 = build(tmp, "trap")
        marker = Path(tmp, "TRANSPORT-RAN")
        gplain(repo6, "config", "core.sshCommand", f"touch {marker}")
        gplain(repo6, "config", "remote.origin.url", "ssh://example.invalid/x.git")
        rc, o, e = g(repo6, "cat-file", "--batch-check", stdin="0" * 40 + "\n")
        show("Q6 cat-file --batch-check of absent oid under --no-lazy-fetch",
             f"rc={rc}\nstdout={o}\nstderr={e}\nmarker_exists={marker.exists()}")
        rc, o, e = g(repo6, "log", "--diff-filter=A", "--format=%at", "--",
                     ".ufo/reports/round-1/kama.md")
        show("Q6b git log -- path (present objects)",
             f"rc={rc}\nstdout={o}\nstderr={e}\nmarker_exists={marker.exists()}")

        # ---------- Q7: cat-file batch-check of a *present* blob + peel ----
        rc, o, e = g(repo6, "cat-file", "--batch-check",
                     stdin=f"{blob}^{{commit}}\n")
        show("Q7 cat-file --batch-check <blob>^{commit} (type mismatch)",
             f"rc={rc}\nstdout={o}\nstderr={e}")
        rc, o, e = g(repo6, "cat-file", "--batch-check",
                     stdin=f"{commits[0]}^{{commit}}\n")
        show("Q7b cat-file --batch-check <commit>^{commit}",
             f"rc={rc}\nstdout={o}\nstderr={e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
