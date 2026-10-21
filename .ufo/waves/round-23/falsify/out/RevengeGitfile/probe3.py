#!/usr/bin/env python3
"""RevengeGitfile control probes (scratch: /tmp/gitfile-r23-run/fx3).

(1) Control: a FIFO `.git/HEAD` in a PLAIN repository (no gitfile, no linked worktree).
    If it hangs too, the admin-FIFO hang is git's HEAD read, not a linked-worktree effect.
(2) Preflight: the proposed check refuses the plain FIFO HEAD before any git call.
(3) Orphans: after the timeout kill, no git process is left on the fixture paths.
"""
import os
import shutil
import sys
from pathlib import Path

import probe as pr

pr.ROOT = Path("/tmp/gitfile-r23-run/fx3")
R = pr.ROOT


def pgrep_count(pattern):
    rc, out, _ = pr.run(["pgrep", "-fc", pattern])
    return out.strip() or "0"


def main():
    if R.exists():
        shutil.rmtree(R)
    R.mkdir(parents=True)
    P = pr.build()  # fixtures for fleet_ok etc. under fx3 (builds all, reused below)
    plain = R / "plainfifo"
    pr.git(R, "clone", "-q", "--no-hardlinks", str(P["main"]), str(plain))
    (plain / ".git" / "HEAD").unlink()
    os.mkfifo(plain / ".git" / "HEAD")
    print("## C1 control: FIFO .git/HEAD in a PLAIN repository")
    print(f"  lstype(.git/HEAD) = {pr.lstype(plain / '.git' / 'HEAD')}")
    res = pr.audit(plain, P["fleet_ok"], timeout=15)
    print(f"  auditor: { {k: v for k, v in res.items() if k != 'json'} }")
    print(f"  orphan git processes on plainfifo: {pgrep_count(str(plain))}")

    print("\n## C2 proposed preflight on the same plain repo (no git call before refusal)")
    dotgit = plain / ".git"
    bad = [n for n in ("HEAD", "commondir", "gitdir")
           if (dotgit / n).exists() or (dotgit / n).is_symlink()
           if pr.lstype(dotgit / n) != "file"]
    print(f"  preflight refuses: {bool(bad)} {bad}")

    print("\n## C3 orphan check after timeout kill on linked admin FIFO (correct pattern)")
    hm = pr.init(R / "hm")
    pr.commit(hm, 1000, "round-1: work")
    pr.commit(hm, 1100, "round-1: measure")
    pr.git(hm, "worktree", "add", "-q", str(R / "hw1"), "-b", "hw1")
    adm = hm / ".git" / "worktrees" / "hw1"
    (adm / "HEAD").unlink()
    os.mkfifo(adm / "HEAD")
    res = pr.audit(R / "hw1", P["fleet_ok"], timeout=10)
    print(f"  auditor: { {k: v for k, v in res.items() if k != 'json'} }")
    print(f"  orphan git processes with -C {R / 'hw1'}: {pgrep_count(str(R / 'hw1'))}")


if __name__ == "__main__":
    main()
