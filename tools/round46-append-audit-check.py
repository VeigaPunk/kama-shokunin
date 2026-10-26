#!/usr/bin/env python3
"""round46-append-audit-check.py - kama round-46 C2 (calibration, capability acquisition) counter.

Question: at a lane revision, does the lane hold a working capability that sets
its own self-description - the five files it treats as append-only - against
its observed history: a tool that lists every commit deleting >= 20 lines from
one of those files, says how many of the deleted lines the file holds again at
the audited revision and which later commit first restored all of them, and
exits nonzero when a mass deletion is not restored; does that tool agree with
an independent recomputation on the lane's own history and on a fixture whose
content it cannot know in advance; and is the capability entered in the
SCORECARD capability table?

Origin: considerthese/2026-10-26.md proposal 1 ("Flag deletions in append-only
files"); round-45 commit 0718b6ab truncated four of these files and only a
same-round repair (82b5e9d3) caught it.

Frozen names (before data):
  tool       tools/append-only-audit.py
  files      SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md,
             corpus/SOURCES.md
  threshold  20 deleted lines per (commit, file)
Event definition (shared by the tool contract and this counter). Commits are
`git rev-list --topo-order --reverse <to>`; a commit's diff is against its
first parent (`git diff --no-renames -U0 <c>^1 <c> -- <file>`); the root commit
has no parent and no deletions. deleted = the number of `-` lines of that diff
(excluding the `---` header). An event is a (commit, file) with deleted >= 20.
restored_at_tip = how many of the deleted lines (exact text, newline removed)
occur as some line of <file> at <to> (each deleted line counted on its own;
duplicates may share one occurrence). status = restored when restored_at_tip ==
deleted, unrestored when 0, else partial. restored_by = the first commit after
the event commit in the same rev-list order at which <file> holds every
deleted line text again, else null.
Tool contract: `python3 tools/append-only-audit.py --repo R --to REV --json`
prints one JSON object with key `events`: a list of objects with keys commit
(40-hex), file, deleted, restored_at_tip, status, restored_by (40-hex or null);
exit 0 when no event is partial or unrestored, 1 when one is, 2 when it cannot
evaluate. `--selftest` prints a line `AOA_SELFTEST pass=<n> fail=<m>` and exits
0 only when m = 0.

Legs:
  selftest  the tool at --tip (`git show <tip>:<tool>` run from a temp file)
            with `--selftest` exits 0 and prints `AOA_SELFTEST pass=n fail=0`
            with n >= 6.
  fixture   this counter builds a fresh git repo under TMPDIR with random line
            content (os.urandom) - LOG.md: 60 lines; append 10; delete 30
            (event A); touch notes.md; restore the 30 (A's restorer); delete 25
            other lines (event B, never restored); delete 5 (below threshold);
            notes.md (not a declared file) loses 40 lines. The tool with
            `--json --to <last>` must report exactly A (restored, restored_by =
            the restoring commit) and B (unrestored, restored_by null) with
            their counts, and exit 1; with `--to <restorer>` exactly A
            (restored) and exit 0.
  lane      the tool on --repo at --tip (`--json --to <tip>`) reports exactly
            the events this counter recomputes on the lane: equal sets of
            (commit, file, deleted, restored_at_tip, status, restored_by), and
            an exit code that agrees with them.
  table     SCORECARD.md at --tip has a table line (starts with `|`) that names
            `append-only-audit` and whose last non-empty cell is `46`.
met = selftest and fixture and lane and table.
PREDICATE (same sentence in the preregistration): the append-only-audit
capability runs at the measured commit, passes its selftest, matches an
independent recomputation on a random fixture and on the lane's own history,
and is entered in the SCORECARD capability table; selftest=1 fixture=1 lane=1
table=1.

Output: `selftest=0|1 fixture=0|1 lane=0|1 table=0|1 lane_events=E
lane_unrestored=U lane_partial=P met=True|False`, then `detail:` lines.
Exit 0 met, 1 not met, 2 could not evaluate (git failure on --repo).
Read-only on --repo; fixtures live under TMPDIR and are removed on exit.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOL = "tools/append-only-audit.py"
FILES = ["SCORECARD.md", "LOG.md", "corpus/QUALITY.md", "corpus/README.md", "corpus/SOURCES.md"]
THRESHOLD = 20
KEYS = ("commit", "file", "deleted", "restored_at_tip", "status", "restored_by")


class EvalError(Exception):
    pass


def git(repo, *args, check=True, env=None):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, env=env)
    if check and p.returncode != 0:
        raise EvalError(f"git {' '.join(args)[:120]}: {p.stderr.strip()[:200]}")
    return p


def lines_at(repo, rev, path):
    p = git(repo, "show", f"{rev}:{path}", check=False)
    return set(p.stdout.split("\n")) if p.returncode == 0 else set()


def recompute(repo, to):
    commits = git(repo, "rev-list", "--topo-order", "--reverse", to).stdout.split()
    events = []
    for i, c in enumerate(commits):
        par = git(repo, "rev-parse", "--verify", "-q", c + "^1", check=False)
        if par.returncode != 0:
            continue
        p = par.stdout.strip()
        for f in FILES:
            d = git(repo, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", p, c, "--", f).stdout
            dele = [x[1:] for x in d.split("\n") if x.startswith("-") and not x.startswith("---")]
            if len(dele) < THRESHOLD:
                continue
            tip = lines_at(repo, to, f)
            k = sum(1 for x in dele if x in tip)
            status = "restored" if k == len(dele) else ("unrestored" if k == 0 else "partial")
            rb = None
            for c2 in commits[i + 1:]:
                have = lines_at(repo, c2, f)
                if all(x in have for x in dele):
                    rb = c2
                    break
            events.append({"commit": c, "file": f, "deleted": len(dele), "restored_at_tip": k,
                           "status": status, "restored_by": rb})
    return events


def norm(evs):
    out = set()
    for e in evs:
        out.add(tuple(e.get(k) for k in KEYS))
    return out


def run_tool(tool_path, args, env):
    p = subprocess.run([sys.executable, tool_path, *args], capture_output=True, text=True, env=env, timeout=1800)
    return p.returncode, p.stdout, p.stderr


def parse_events(stdout):
    try:
        return json.loads(stdout)["events"]
    except Exception:
        return None


def build_fixture(root):
    d = tempfile.mkdtemp(prefix="aoa-fix-", dir=root)
    git(d, "init", "-q")
    if os.path.realpath(git(d, "rev-parse", "--show-toplevel").stdout.strip()) != os.path.realpath(d):
        raise EvalError("fixture toplevel mismatch")
    ident = ["-c", "user.name=aoa-fixture", "-c", "user.email=aoa-fixture@invalid", "-c", "commit.gpgsign=false"]
    rnd = lambda: os.urandom(12).hex()
    log = [f"entry {rnd()}" for _ in range(60)]
    notes = [f"note {rnd()}" for _ in range(50)]
    shas = {}

    def commit(tag, files):
        for name, body in files.items():
            with open(os.path.join(d, name), "w") as fh:
                fh.write("\n".join(body) + "\n")
        git(d, "add", "-A")
        git(d, *ident, "commit", "-q", "-m", tag)
        shas[tag] = git(d, "rev-parse", "HEAD").stdout.strip()

    commit("c1", {"LOG.md": log, "notes.md": notes})
    log2 = log + [f"entry {rnd()}" for _ in range(10)]
    commit("c2", {"LOG.md": log2})
    log3 = log2[:5] + log2[35:]
    commit("c3", {"LOG.md": log3})                      # event A: 30 deleted
    commit("c4", {"notes.md": notes + [f"note {rnd()}"]})
    log5 = log2[:]                                      # restorer of A
    commit("c5", {"LOG.md": log5})
    log6 = log5[:40] + log5[65:]                        # event B: 25 deleted, never restored
    commit("c6", {"LOG.md": log6})
    log7 = log6[:-5]                                    # 5 deleted: below threshold
    commit("c7", {"LOG.md": log7, "notes.md": notes[40:]})  # notes.md: not declared
    return d, shas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--out")
    ap.add_argument("--scratch", help="fixture root (default $TMPDIR)")
    a = ap.parse_args()
    root = a.scratch or tempfile.gettempdir()
    os.makedirs(root, exist_ok=True)
    work = tempfile.mkdtemp(prefix="r46c2-", dir=root)
    env = dict(os.environ, TMPDIR=work)
    detail = []
    legs = {"selftest": 0, "fixture": 0, "lane": 0, "table": 0}
    lane_ev = []
    try:
        tip = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}").stdout.strip()
        body = git(a.repo, "show", f"{tip}:{TOOL}", check=False)
        if body.returncode != 0:
            detail.append(f"{TOOL} absent at tip")
            tool = None
        else:
            tool = os.path.join(work, "append-only-audit.py")
            with open(tool, "w") as fh:
                fh.write(body.stdout)
        if tool:
            rc, out, err = run_tool(tool, ["--selftest"], env)
            m = re.search(r"AOA_SELFTEST pass=(\d+) fail=(\d+)", out)
            if rc == 0 and m and int(m.group(2)) == 0 and int(m.group(1)) >= 6:
                legs["selftest"] = 1
            else:
                detail.append(f"selftest rc={rc} line={m.group(0) if m else None} err={err.strip()[:160]}")
            fx, shas = build_fixture(work)
            exp_full = {
                (shas["c3"], "LOG.md", 30, 30, "restored", shas["c5"]),
                (shas["c6"], "LOG.md", 25, 0, "unrestored", None),
            }
            exp_mid = {(shas["c3"], "LOG.md", 30, 30, "restored", shas["c5"])}
            rc1, out1, _ = run_tool(tool, ["--repo", fx, "--to", shas["c7"], "--json"], env)
            rc2, out2, _ = run_tool(tool, ["--repo", fx, "--to", shas["c5"], "--json"], env)
            e1, e2 = parse_events(out1), parse_events(out2)
            ok1 = e1 is not None and norm(e1) == exp_full and rc1 == 1
            ok2 = e2 is not None and norm(e2) == exp_mid and rc2 == 0
            if ok1 and ok2:
                legs["fixture"] = 1
            else:
                detail.append(f"fixture full ok={ok1} rc={rc1} got={sorted(map(str, norm(e1 or [])))[:4]}")
                detail.append(f"fixture mid ok={ok2} rc={rc2} got={sorted(map(str, norm(e2 or [])))[:4]}")
            lane_ev = recompute(a.repo, tip)
            rc3, out3, err3 = run_tool(tool, ["--repo", a.repo, "--to", tip, "--json"], env)
            e3 = parse_events(out3)
            bad = any(e["status"] != "restored" for e in lane_ev)
            if e3 is not None and norm(e3) == norm(lane_ev) and rc3 == (1 if bad else 0):
                legs["lane"] = 1
            else:
                got = norm(e3 or [])
                want = norm(lane_ev)
                detail.append(f"lane rc={rc3} missing={sorted(map(str, want - got))[:3]} "
                              f"extra={sorted(map(str, got - want))[:3]} err={err3.strip()[:120]}")
        else:
            lane_ev = recompute(a.repo, tip)
        sc = git(a.repo, "show", f"{tip}:SCORECARD.md", check=False).stdout
        for x in sc.splitlines():
            if x.lstrip().startswith("|") and "append-only-audit" in x:
                cells = [c.strip() for c in x.strip().strip("|").split("|") if c.strip()]
                if cells and cells[-1] == "46":
                    legs["table"] = 1
                    break
        if not legs["table"]:
            detail.append("no SCORECARD table line naming append-only-audit with last cell 46")
    except EvalError as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        shutil.rmtree(work, ignore_errors=True)
        return 2
    shutil.rmtree(work, ignore_errors=True)
    met = all(legs.values())
    unr = sum(1 for e in lane_ev if e["status"] == "unrestored")
    par = sum(1 for e in lane_ev if e["status"] == "partial")
    line = (f"selftest={legs['selftest']} fixture={legs['fixture']} lane={legs['lane']} table={legs['table']} "
            f"lane_events={len(lane_ev)} lane_unrestored={unr} lane_partial={par} met={met}")
    out = [f"tip={tip}", line] + [f"detail: {d}" for d in detail]
    out += [f"event: {e['commit'][:12]} {e['file']} deleted={e['deleted']} restored_at_tip={e['restored_at_tip']} "
            f"status={e['status']} restored_by={(e['restored_by'] or '-')[:12]}" for e in lane_ev]
    text = "\n".join(out) + "\n"
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text)
    sys.stdout.write(text)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
