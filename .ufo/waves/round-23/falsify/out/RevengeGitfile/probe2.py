#!/usr/bin/env python3
"""RevengeGitfile round-23 follow-ups (run after probe.py). Scratch: /tmp/gitfile-r23-run/fx2.

Tests: (1) strace positive controls that git's child programs are captured; (2) FIFO
admin entries (HEAD, commondir) for hang; (3) ablation of each consistency check on
legit, copied and forged linked worktrees; (4) symlinked lane alias; (5) authenticity:
a foreign-side core.worktree forgery and an attacker-owned linked worktree, both of
which the consistency checks accept.
"""
import os
import re
import sys
from pathlib import Path

import probe as pr

pr.ROOT = Path("/tmp/gitfile-r23-run/fx2")
R = pr.ROOT


def fmt(res):
    return {k: v for k, v in res.items() if k != "json"}


def strace_progs(argv):
    trace = R / "out" / "pc.strace"
    trace.parent.mkdir(parents=True, exist_ok=True)
    pr.run(["strace", "-f", "-e", "trace=execve", "-o", str(trace), *argv])
    progs = set()
    for line in trace.read_text().splitlines():
        m = re.search(r'execve\("([^"]+)"', line)
        if m and line.rstrip().endswith("= 0"):
            progs.add(m.group(1))
    return sorted(progs)


def preflight(gitdir):
    """Admin entries must be regular files BEFORE any git call (git may block on FIFOs)."""
    bad = []
    for name in ("HEAD", "commondir", "gitdir"):
        p = Path(gitdir, name)
        if p.exists() or p.is_symlink():
            kind = pr.lstype(p)
            if kind != "file":
                bad.append(f"{name} is {kind}")
    return bad


def classify_pre(lane):
    lane = os.path.abspath(str(lane))
    dotgit = os.path.join(lane, ".git")
    if pr.lstype(dotgit) == "file":
        try:
            target = pr.gitdir_target(dotgit)
        except pr.Refuse as exc:
            return f"REFUSE: {exc}"
        bad = preflight(target)
        if bad:
            return f"REFUSE (preflight, no git call): admin {', '.join(bad)}"
    return pr.classify(lane)


def ablation(lane):
    lane = os.path.abspath(str(lane))
    dotgit = os.path.join(lane, ".git")
    target = pr.gitdir_target(dotgit)
    cd = os.path.realpath(pr.gitp(lane, "rev-parse", "--path-format=absolute",
                                  "--git-common-dir"))
    back = open(os.path.join(target, "gitdir"), encoding="utf-8").readline().strip()
    back = os.path.realpath(back if os.path.isabs(back) else os.path.join(target, back))
    listed = {os.path.realpath(line[len("worktree "):])
              for line in pr.gitp(None, "worktree", "list", "--porcelain", gitdir=cd).splitlines()
              if line.startswith("worktree ")}
    return {
        "backlink_names_this_gitfile": back == os.path.realpath(dotgit),
        "admin_is_under_common_worktrees": os.path.realpath(os.path.dirname(target))
        == os.path.realpath(os.path.join(cd, "worktrees")),
        "common_lists_this_worktree": os.path.realpath(lane) in listed,
    }


def main():
    P = pr.build()
    print("## F1 positive controls: do strace and marks see git's child programs?")
    pr.clear_marks()
    progs = strace_progs(["git", "-C", str(P["front_h"]), "status", "--porcelain"])
    print(f"  status via front_h (strace): programs={progs} marks={pr.marks()}")
    pr.clear_marks()
    pr.run(["git", "-C", str(P["front_h"]), "diff", "HEAD~1", "HEAD"])
    print(f"  diff via front_h (porcelain): marks={pr.marks()}")
    pr.clear_marks()
    pr.run(["git", "-C", str(P["front_h"]), "log", "-p", "--ext-diff", "-1", "--format=%H"])
    print(f"  log -p --ext-diff via front_h: marks={pr.marks()}")
    pr.clear_marks()
    audit_argv = [sys.executable, str(pr.AUDIT), "--lane-repo", str(P["front_h"]),
                  "--fleet-repo", str(P["fleet_ok"]), "--rounds", "1", "--no-errata", "--json"]
    print(f"  auditor via front_h (strace): programs={strace_progs(audit_argv)} marks={pr.marks()}")

    print("\n## F2 FIFO admin entries (hang?) on a fresh linked worktree pair")
    hm = pr.init(R / "hm")
    pr.commit(hm, 1000, "round-1: work")
    pr.commit(hm, 1100, "round-1: measure")
    pr.git(hm, "worktree", "add", "-q", str(R / "hw1"), "-b", "hw1")
    pr.git(hm, "worktree", "add", "-q", str(R / "hw2"), "-b", "hw2")
    a1 = hm / ".git" / "worktrees" / "hw1"
    (a1 / "HEAD").unlink()
    os.mkfifo(a1 / "HEAD")
    a2 = hm / ".git" / "worktrees" / "hw2"
    (a2 / "commondir").unlink()
    os.mkfifo(a2 / "commondir")
    for label, lane in (("HEAD FIFO (hw1)", R / "hw1"), ("commondir FIFO (hw2)", R / "hw2")):
        print(f"  {label}: classify_pre -> {classify_pre(lane)}")
        print(f"  {label}: auditor -> {fmt(pr.audit(lane, P['fleet_ok'], timeout=20))}")
    print(f"  leftover git processes for hw2 admin: {pr.run(['pgrep', '-fc', str(a2)])[1].strip() or '0'}")

    print("\n## F3 ablation of consistency checks")
    for label, lane in (("linked wt (legit)", P["wt"]), ("linked wtrel (legit)", P["wtrel"]),
                        ("copied wt-copy", P["wt_copy"]), ("forged atk-wt", P["atk_wt"])):
        print(f"  {label:<22} {ablation(lane)}")

    print("\n## F4 symlinked lane alias (legit linked worktree behind a symlink)")
    alias = R / "wt-alias"
    os.symlink(P["wt"], alias)
    print(f"  classify: {classify_pre(alias)}")
    print(f"  auditor: {fmt(pr.audit(alias, P['fleet_ok']))}")

    print("\n## F5 authenticity: consistency checks are not identity checks")
    forged = R / "forged"
    decoy_f = R / "decoy_f"
    pr.git(R, "clone", "-q", "--no-hardlinks", str(P["main"]), str(decoy_f))
    pr.git(decoy_f, "config", "core.worktree", str(forged))
    pr.gitfile(forged, decoy_f / ".git")
    print(f"  foreign repo with forged core.worktree -> classify: {classify_pre(forged)}")
    print(f"  top-level from forged lane: "
          f"{pr.run(['git', '-C', str(forged), 'rev-parse', '--show-toplevel'])[1].strip()}")
    print(f"  auditor on forged lane + fleet_e: {fmt(pr.audit(forged, P['fleet_e']))}")
    am = pr.init(R / "am")
    pr.commit(am, 1000, "unrelated attacker history")
    pr.git(am, "worktree", "add", "-q", str(R / "aw"), "-b", "aw")
    print(f"  attacker-owned linked worktree -> classify: {classify_pre(R / 'aw')}")


if __name__ == "__main__":
    main()
