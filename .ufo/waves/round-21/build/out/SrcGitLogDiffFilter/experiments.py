#!/usr/bin/env python3
"""Reproduce the round-21 SrcGitLogDiffFilter scratch experiments (source scout, S066 draft).

Scratch-only: everything is created under /tmp/kama-r21-SrcGitLogDiffFilter (removed first).
The lane and fleet repositories are touched read-only (git clone / show / log / rev-parse).
Exit 0 = every step ran. Commit times come from the clock, so values differ between runs.
"""
import importlib.util
import os
import pathlib
import re
import shutil
import subprocess
import sys

SCRATCH = pathlib.Path("/tmp/kama-r21-SrcGitLogDiffFilter")
LANE_SRC = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "a29bb84abbb8b4d328f5970a89e448330a3a42ac"
LANE = SCRATCH / "lane"

CMDS = [
    r"""grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md""",
    r"""awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END{print n+0}' corpus/SOURCES.md""",
    r"""awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {t=$5; gsub(/[[:space:]]/,"",t); n[t]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md""",
    r"""awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {s=$9; gsub(/[[:space:]]/,"",s); n[s]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md""",
    r"""awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {i=$2; gsub(/[[:space:]]/,"",i); print i}' corpus/SOURCES.md | sort | uniq -d""",
    r"""awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF==13 {i=$2;k=$4;t=$5;s=$9; gsub(/[[:space:]]/,"",i); gsub(/[[:space:]]/,"",k); gsub(/[[:space:]]/,"",t); gsub(/[[:space:]]/,"",s); if (t !~ /^[ABC]$/) print "tier", i, t; if (s !~ /^(queued|mined|rejected)$/) print "status", i, s; if (k !~ /^(spec|docs|paper|code|tool|dataset|talk|book|community|own-work)$/) print "kind", i, k; if (t=="A" && k=="community") print "tier-inflation", i}' corpus/SOURCES.md""",
    r"""awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF==13 {s=$9; gsub(/[[:space:]]/,"",s); if (s=="mined") {n=split($12, a, /[,;]/); for (j=1;j<=n;j++) {p=a[j]; gsub(/^[[:space:]]+|[[:space:]]+$/,"",p); if (p!="" && p!="—") print p}}}' corpus/SOURCES.md | while read -r p; do [ -e "$p" ] || echo "missing: $p"; done""",
]

ROW = ('| S066 | git-log manual (Git 2.56.0) — https://git-scm.com/docs/git-log | docs | A | '
       'committer timestamp and added-path selection that a git-log report-cutoff reads; not commit rewriting and not any audit\'s correctness | '
       '§PRETTY FORMATS, placeholder `%ct` ("committer date, UNIX timestamp"); §DIFF FORMATTING, `--diff-filter` ("Select only files that are Added (A), Copied (C), Deleted (D), Modified (M), Renamed (R)"); '
       'page "last updated in 2.56.0"; local `man git-log` (Git 2.56.0) carries the same wording; opened 2026-10-21 | '
       '`git log --diff-filter=A --format=%ct -- <path>` prints the committer date of each commit that adds the path, newest first by default; `%ct` is committer time, not author time (`%at`). | '
       'queued | 2026-10-21 | on-release | — |')


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def env_base(extra=None):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(HOME=str(SCRATCH / "home"), GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1",
             LC_ALL="C", GIT_AUTHOR_NAME="a", GIT_AUTHOR_EMAIL="a@x",
             GIT_COMMITTER_NAME="c", GIT_COMMITTER_EMAIL="c@x")
    e.update(extra or {})
    return e


def g(repo, *args, a=None, c=None):
    """git inside repo with optional pinned author/committer epoch seconds; returns (rc, text)."""
    env = env_base()
    if a is not None:
        env["GIT_AUTHOR_DATE"] = f"@{a} +0000"
    if c is not None:
        env["GIT_COMMITTER_DATE"] = f"@{c} +0000"
    r = subprocess.run(["git", "-c", "commit.gpgsign=false", *args], cwd=repo,
                       env=env, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def fmt(repo, *args):
    return g(repo, "log", "--format=%h|%at|%ct|%s", *args)


def cutoff(repo, rel):
    rc, out = g(repo, "log", "--diff-filter=A", "--format=%ct", "--", rel)
    vals = out.split()
    return {"rc": rc, "ct_lines": out.split("\n") if out else [],
            "cutoff(split()[-1])": int(vals[-1]) if vals else None}


def commit(repo, msg, a, c, content, fname="f.txt"):
    (repo / fname).write_text(content)
    g(repo, "add", "-A")
    return g(repo, "commit", "-q", "-m", msg, a=a, c=c)


def new_repo(name):
    p = SCRATCH / "exp" / name
    p.mkdir(parents=True)
    g(p, "init", "-q", "-b", "main")
    return p


def part_experiments():
    e1 = new_repo("e1")
    commit(e1, "one", 1000000000, 1000000100, "1\n")
    commit(e1, "two", 1000000200, 1000000200, "2\n")
    print("E1a before amend        :", fmt(e1, "-n", "1"))
    print("E1b amend, no date env  :", g(e1, "commit", "-q", "--amend", "-m", "two amended"), fmt(e1, "-n", "1"))
    print("E1c amend --reset-author:", g(e1, "commit", "-q", "--amend", "--reset-author", "-m", "two reset"), fmt(e1, "-n", "1"))
    print("E1d amend, committer pinned @1000000500:", g(e1, "commit", "-q", "--amend", "-m", "two pinned", c=1000000500), fmt(e1, "-n", "1"))

    e2 = new_repo("e2")
    commit(e2, "base", 1000000000, 1000000000, "b\n", "base.txt")
    g(e2, "checkout", "-q", "-b", "feat")
    commit(e2, "feat1", 1000000200, 1000000200, "f1\n", "feat.txt")
    g(e2, "checkout", "-q", "main")
    commit(e2, "main1", 1000000300, 1000000300, "m\n", "main.txt")
    g(e2, "checkout", "-q", "feat")
    print("E2a feat before rebase  :", fmt(e2, "-n", "1"), cutoff(e2, "feat.txt"))
    print("E2b rebase main         :", g(e2, "rebase", "-q", "main"), fmt(e2, "-n", "1"), cutoff(e2, "feat.txt"))
    print("E2c rebase main again   :", g(e2, "rebase", "main"), fmt(e2, "-n", "1"))
    print("E2d rebase --force-rebase:", g(e2, "rebase", "-q", "--force-rebase", "main"), fmt(e2, "-n", "1"), cutoff(e2, "feat.txt"))
    print("E2e --committer-date-is-author-date:", g(e2, "rebase", "-q", "--committer-date-is-author-date", "main"), fmt(e2, "-n", "1"), cutoff(e2, "feat.txt"))

    e3 = SCRATCH / "exp" / "e3"
    e3.mkdir(parents=True)
    g(e3, "init", "-q", "-b", "x")
    g(e3, "commit", "-q", "--allow-empty", "-m", "X", a=1000000900, c=1000000100)
    g(e3, "checkout", "-q", "--orphan", "y")
    g(e3, "commit", "-q", "--allow-empty", "-m", "Y", a=1000000100, c=1000000900)
    for args in (["--all"], ["--all", "--date-order"], ["--all", "--topo-order"]):
        print("E3", " ".join(args), "->", g(e3, "log", *args, "--format=%h|%at|%ct|%s"))

    for name, readd_ct in (("e4", 1000000400), ("e5", 1000000050)):
        r = new_repo(name)
        commit(r, "add1", 1000000100, 1000000100, "1\n")
        commit(r, "mod2", 1000000200, 1000000200, "2\n")
        g(r, "rm", "-q", "f.txt")
        g(r, "commit", "-q", "-m", "del3", a=1000000300, c=1000000300)
        commit(r, "readd4", 1000000400, readd_ct, "4\n")
        print(f"{name.upper()} --diff-filter=A (readd committer {readd_ct}):", fmt(r, "--diff-filter=A", "--", "f.txt"))
        print(f"{name.upper()} --diff-filter=A --reverse:", fmt(r, "--reverse", "--diff-filter=A", "--", "f.txt"))
        print(f"{name.upper()} cutoff:", cutoff(r, "f.txt"))

    e6 = new_repo("e6")
    commit(e6, "report landed", 1000000100, 1000000100, "# report\n", "report.md")
    print("E6a cutoff before amend :", cutoff(e6, "report.md"))
    print("E6b amend, no date env  :", g(e6, "commit", "-q", "--amend", "-m", "report landed (amended)"), cutoff(e6, "report.md"))


def part_synthetic():
    spec = importlib.util.spec_from_file_location("rla", str(LANE / "tools" / "report-landing-audit.py"))
    rla = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rla)
    root = SCRATCH / "synth"
    root.mkdir(parents=True, exist_ok=True)

    def sh(repo, *args, when=None):
        env = env_base({"GIT_AUTHOR_NAME": "kama-shokunin", "GIT_COMMITTER_NAME": "kama-shokunin"})
        if when is not None:
            env["GIT_AUTHOR_DATE"] = f"@{when} +0000"
            env["GIT_COMMITTER_DATE"] = f"@{when} +0000"
        r = subprocess.run(["git", "-C", str(repo), "-c", "commit.gpgsign=false", *args],
                           env=env, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"git {args}: rc={r.returncode} {r.stderr}")
        return r.stdout.strip()

    def make(name):
        t = root / name
        lane, fleet = t / "lane", t / "fleet"
        lane.mkdir(parents=True)
        fleet.mkdir()
        for repo in (lane, fleet):
            sh(repo, "init", "-q", "-b", "master")
        return lane, fleet

    def lane_commit(lane, msg, when=None):
        p = lane / "f"
        p.write_text((p.read_text() if p.exists() else "") + msg + "\n")
        sh(lane, "add", "f")
        sh(lane, "commit", "-q", "-m", msg, when=when)
        return sh(lane, "rev-parse", "HEAD")

    def report(fleet, text, when=None):
        rel = ".ufo/reports/round-1/kama.md"
        p = fleet / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        sh(fleet, "add", rel)
        sh(fleet, "commit", "-q", "-m", "round-1: kama report", when=when)
        return sh(fleet, "rev-parse", "HEAD")

    def audit(lane, fleet):
        res = rla.audit_round(str(lane), str(fleet), "master", "kama", 1, None)
        def short(tok):
            return tok[:9] if len(tok) == 40 else tok
        return {"cutoff": res["cutoff"], "committed": res["report_committed"],
                "required(pre)": res["required"],
                "post_report": [short(s) for s in res["post_report"]],
                "defects": [(d["kind"], short(d["token"])) for d in res["defects"]]}

    lane, fleet = make("s1")
    a = lane_commit(lane, "round-1: work", 1000)
    b = lane_commit(lane, "round-1: measure", 1100)
    report(fleet, f"# r1\n## Work performed\nwork\n## Landed changes\n- `{a[:9]}` work\n", 1200)
    print("S1 before rewrite :", audit(lane, fleet), "b=", b[:9])
    sh(lane, "commit", "--amend", "-q", "-m", "round-1: measure")
    b2 = sh(lane, "rev-parse", "HEAD")
    print("S1 after amend    :", audit(lane, fleet), "b2=", b2[:9])
    print("S1 ctimes         :", sh(lane, "log", "--format=%h %at %ct %s", "-n", "2"))

    lane, fleet = make("s2")
    a = lane_commit(lane, "round-1: work", 1000)
    b = lane_commit(lane, "round-1: measure", 1100)
    report(fleet, f"# r1\n## Work performed\nwork\n## Landed changes\n- `{a[:9]}` work\n- `{b[:9]}` measure\n", 1200)
    c = lane_commit(lane, "round-1: late advice", 1250)
    print("S2 before amend   :", audit(lane, fleet), "c=", c[:9])
    sh(fleet, "commit", "--amend", "-q", "-m", "round-1: kama report")
    print("S2 after amend    :", audit(lane, fleet))
    print("S2 fleet ctime    :", sh(fleet, "log", "--format=%h %at %ct %s", "-n", "1"))


def part_census_and_draft():
    def census(tag):
        for cmd in CMDS:
            r = subprocess.run(["bash", "-c", cmd], cwd=LANE, capture_output=True, text=True)
            print(f"[{tag}] rc={r.returncode} out={r.stdout.strip()!r} err={r.stderr.strip()!r}")

    census("before")
    base_text = run(["git", "-C", str(LANE), "show", f"{BASE}:corpus/SOURCES.md"]).stdout
    print("draft row cell count =", len(ROW.strip().strip("|").split("|")), "(contract: 11)")
    print("git-scm git-log URL already in base file:", "git-scm.com/docs/git-log" in base_text)
    lines = base_text.split("\n")
    idx = max(i for i, line in enumerate(lines) if re.match(r"^\|\s*S\d{3,}\s*\|", line))
    lines.insert(idx + 1, ROW)
    (LANE / "corpus" / "SOURCES.md").write_text("\n".join(lines), encoding="utf-8")
    census("after")
    r = run(["git", "-C", str(LANE), "-c", "commit.gpgsign=false", "-c", "user.name=scratch",
             "-c", "user.email=scratch@x", "commit", "-q", "-am", "scratch: draft S066 row (not the lane)"])
    print("scratch commit rc =", r.returncode)
    r = subprocess.run(["python3", "tools/sources-append-only.py", "--from", BASE, "--to", "HEAD",
                        "--repo", str(LANE), "--path", "corpus/SOURCES.md"],
                       cwd=LANE, capture_output=True, text=True)
    print("append-only rc =", r.returncode, r.stdout.strip(), r.stderr.strip())


def part_history():
    def git2(repo, *a):
        r = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)
        return r.returncode, r.stdout

    rc, out = git2(str(LANE), "log", BASE, "--format=%H|%an|%at|%ct|%s")
    print("lane log rc =", rc)
    rows = [line.split("|", 4) for line in out.splitlines()]
    pat = re.compile(r"^(?:round-\d+:|checkpoint\(r\d+\))")
    lane_round = [r for r in rows if r[1] == "kama-shokunin" and pat.match(r[4])]
    print(f"lane kama round/checkpoint commits = {len(lane_round)}; "
          f"at!=ct = {sum(1 for r in lane_round if r[2] != r[3])}; "
          f"all lane commits at!=ct = {sum(1 for r in rows if r[2] != r[3])} of {len(rows)}; "
          f"ct<at = {sum(1 for r in rows if int(r[3]) < int(r[2]))}")
    for n in range(10, 22):
        rc, o = git2(FLEET, "log", "--diff-filter=A", "--format=%h|%at|%ct", "--", f".ufo/reports/round-{n}/kama.md")
        joined = o.strip().replace("\n", " ; ") or "(none)"
        print(f"fleet round-{n} kama.md add commit(s) rc={rc}: {joined}")
    for n in range(10, 21):
        rc, o = git2(FLEET, "log", "--diff-filter=A", "--format=%ct", "--", f".ufo/reports/round-{n}/kama.md")
        vals = o.split()
        if not vals:
            print(f"r{n}: no fleet add commit")
            continue
        cut = int(vals[-1])
        p = re.compile(rf"^(?:round-{n}:|checkpoint\(r{n}\))")
        mine = [r for r in rows if r[1] == "kama-shokunin" and p.match(r[4])]
        fwd = [(r[0][:9], int(r[2]), int(r[3])) for r in mine if int(r[2]) <= cut < int(r[3])]
        rev = [(r[0][:9], int(r[2]), int(r[3])) for r in mine if int(r[3]) <= cut < int(r[2])]
        print(f"r{n} cutoff={cut} lane_commits={len(mine)} at!=ct={sum(1 for r in mine if r[2] != r[3])} "
              f"at<=cutoff<ct={fwd} ct<=cutoff<at={rev}")


def main():
    shutil.rmtree(SCRATCH, ignore_errors=True)
    (SCRATCH / "home").mkdir(parents=True)
    r = run(["git", "clone", "-q", LANE_SRC, str(LANE)])
    print("clone rc =", r.returncode, r.stderr.strip())
    r = run(["git", "-C", str(LANE), "checkout", "-q", BASE])
    print("checkout rc =", r.returncode, r.stderr.strip())
    part_experiments()
    part_synthetic()
    part_census_and_draft()
    part_history()
    return 0


if __name__ == "__main__":
    sys.exit(main())
