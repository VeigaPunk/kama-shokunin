#!/usr/bin/env python3
"""Blind-spot probe for tools/report-landing-audit.py, scoped to round 15.

Read-only with respect to the lane and fleet repositories. It writes only to a
fresh temp directory (removed at exit) and to blindspot-probe.json in the
AuditReport15 out directory. Each case states the expected result before the
tool is run, so a mismatch is visible in the output.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
FLEET = Path("/home/vgpnk/Projects/shokunin")
TOOL = LANE / "tools" / "report-landing-audit.py"
REPORT = FLEET / ".ufo" / "reports" / "round-15" / "kama.md"
OUT = LANE / ".ufo" / "waves" / "round-21" / "build" / "out" / "AuditReport15"
TMP = Path(tempfile.mkdtemp(prefix="kama-r21-AR15-"))


def run_tool(*args):
    proc = subprocess.run([sys.executable, str(TOOL), *args],
                          capture_output=True, text=True, cwd=str(LANE))
    doc = None
    try:
        doc = json.loads(proc.stdout)
    except ValueError:
        pass
    return proc.returncode, doc, proc.stderr.strip()


def summarise(doc):
    res = doc["results"][0]
    return {
        "defects": [[d["kind"], d["token"]] for d in res["defects"]],
        "required": res["required"],
        "round_commits": res["round_commits"],
        "post_report": res["post_report"],
        "report_committed": res["report_committed"],
        "cutoff": res["cutoff"],
    }


def git(repo, *args, env=None):
    return subprocess.run(["git", "-C", str(repo), "-c", "commit.gpgsign=false",
                           "-c", "core.hooksPath=/dev/null", *args],
                          capture_output=True, text=True, env=env)


def commit(repo, author, subject, ctime, rel, content):
    path = Path(repo) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    env = dict(os.environ, GIT_AUTHOR_NAME=author, GIT_AUTHOR_EMAIL="t@x",
               GIT_COMMITTER_NAME=author, GIT_COMMITTER_EMAIL="t@x",
               GIT_AUTHOR_DATE="@%d +0000" % ctime,
               GIT_COMMITTER_DATE="@%d +0000" % ctime)
    git(repo, "add", "-A")
    proc = git(repo, "commit", "-q", "-m", subject, env=env)
    if proc.returncode != 0:
        raise SystemExit("commit failed: " + proc.stderr)
    return git(repo, "rev-parse", "HEAD").stdout.strip()


BASE = REPORT.read_text(encoding="utf-8")
LINES = BASE.split("\n")
TITLE = LINES[0]
ROW_B8 = "| `b8bdc56efc43fe6baad9415d0ca75b7b81ffa952` |"
ROW_70 = "| `70af36c2b15b46d3b4b3c15ef20459cff640dfaf` |"
H70 = "70af36c2b15b46d3b4b3c15ef20459cff640dfaf"


def add_row(row):
    out = list(LINES)
    idx = [i for i, line in enumerate(out) if line.startswith(ROW_B8)]
    assert len(idx) == 1, idx
    out.insert(idx[0] + 1, row)
    return "\n".join(out)


def drop_row(prefix):
    out = [line for line in LINES if not line.startswith(prefix)]
    assert len(out) == len(LINES) - 1
    return "\n".join(out)


def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


CASES = [
    ("M0 unmodified committed report", "0 defects", BASE),
    ("M1 Landed row cites round-14 commit e545ed99 (40-hex)",
     "0 defects: real commit of another round accepted",
     add_row("| `e545ed99aaa519196a2a7779b0a293b2ce4c765c` | probe |")),
    ("M2 Landed row cites round-14 commit by 7-hex e545ed9",
     "0 defects: real commit of another round accepted",
     add_row("| `e545ed9` | probe |")),
    ("M3 Landed row cites blob 783004569 (40-hex)",
     "landed-unresolved: blob rejected by ^{commit}",
     add_row("| `783004569af9072afdeb32c6eeacc462868eb76b` | probe |")),
    ("M4 Landed row cites fleet report commit 402b93b5",
     "0 defects: fleet object accepted (either-repo rule)",
     add_row("| `402b93b58868976096a3c58e3ed8f32ea8dd8f0c` | probe |")),
    ("M5 Landed row 7-hex nonexistent 0123abc",
     "landed-unresolved", add_row("| `0123abc` | probe |")),
    ("M6 Landed row for 70af36c2 removed",
     "landed-omitted 70af36c2", drop_row(ROW_70)),
    ("M7 Landed row for 70af36c2 written uppercase",
     "landed-omitted (FP: commit is cited, uppercase ignored)",
     once(BASE, ROW_70, ROW_70.replace(H70, H70.upper()))),
    ("M8 body uppercase nonexistent 40-hex",
     "0 defects (FN: uppercase never checked)",
     once(BASE, TITLE, TITLE + " `0123456789ABCDEF0123456789ABCDEF01234567`")),
    ("M9 body lowercase nonexistent 40-hex",
     "unresolved-full-hash",
     once(BASE, TITLE, TITLE + " `0123456789abcdef0123456789abcdef01234567`")),
    ("M10 body nonexistent 10-hex",
     "0 defects (FN: 7..39-hex outside Landed unchecked)",
     once(BASE, TITLE, TITLE + " `0badc0de42`")),
    ("M11 body hash e545ed99 replaced by fleet commit 215ba746",
     "0 defects (FN: wrong hash resolving to unrelated object)",
     once(BASE, "e545ed99aaa519196a2a7779b0a293b2ce4c765c",
          "215ba74670a518f07c94efc4738a00f0bf6c6ba7")),
    ("M12 Landed row nonexistent 40-hex",
     "unresolved-full-hash + landed-unresolved",
     add_row("| `0123456789abcdef0123456789abcdef01234567` | probe |")),
    ("M13 prose word 'effaced' (all a-f letters) in Landed intro",
     "landed-unresolved (FP: prose word read as hash)",
     once(BASE, "All groups are tied to", "All groups, effaced in prose, are tied to")),
]


def run_mutants():
    mdir = TMP / "mutants"
    mdir.mkdir()
    rows = []
    for idx, (name, expected, text) in enumerate(CASES):
        path = mdir / ("m%02d.md" % idx)
        path.write_text(text, encoding="utf-8")
        code, doc, err = run_tool("--rounds", "15", "--report", "15=" + str(path),
                                  "--no-errata", "--json")
        rec = {"case": name, "expected": expected, "exit": code}
        if doc is None:
            rec["error"] = err[-300:]
        else:
            rec.update(summarise(doc))
        rows.append(rec)
    return rows


def run_synthetic():
    root = TMP / "synthetic"
    lane_t = root / "lane"
    fleet_t = root / "fleet"
    for d in (lane_t, fleet_t):
        d.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", "-b", "master", str(d)], check=True)
    c1 = commit(lane_t, "kama-shokunin", "round-15: guard (pre, cited)", 1000, "a.txt", "c1\n")
    c2 = commit(lane_t, "kama-shokunin", "Round-15 - capitalised variant (pre, uncited)", 1001, "a.txt", "c2\n")
    c3 = commit(lane_t, "protocol-shokunin", "round-15: other author (pre)", 1002, "a.txt", "c3\n")
    c4 = commit(lane_t, "kama-shokunin", "checkpoint(r15): partial (pre, cited)", 1003, "a.txt", "c4\n")
    c5 = commit(lane_t, "kama-shokunin", "round-15: late (post)", 2000, "a.txt", "c5\n")

    def report(hashes):
        body = "# Kama - round 15 (synthetic)\n\n## Landed changes\n\n| Commit | Landed work |\n|---|---|\n"
        body += "".join("| `%s` | row |\n" % h for h in hashes)
        return body + "\n## Sources\n\nnone\n"

    rel = ".ufo/reports/round-15/kama.md"
    commit(fleet_t, "kama-shokunin", "round-15: kama report", 1500, rel, report([c1, c4]))
    s_a = run_tool("--lane-repo", str(lane_t), "--fleet-repo", str(fleet_t),
                   "--rounds", "15", "--no-errata", "--json")
    (fleet_t / rel).write_text(report([c1]), encoding="utf-8")
    s_b = run_tool("--lane-repo", str(lane_t), "--fleet-repo", str(fleet_t),
                   "--rounds", "15", "--no-errata", "--json")
    rows = []
    for name, expected, (code, doc, err) in (
        ("S1 committed report cites c1,c4; c2 'Round-15 - ' uncited",
         "0 defects (FN: c2 invisible to subject regex; c3 other author ignored; c5 post)", (s_a)),
        ("S2 same committed report, working-tree edit cites only c1",
         "landed-omitted c4 only; c2 still invisible", (s_b)),
    ):
        rec = {"case": name, "expected": expected, "exit": code}
        if doc is None:
            rec["error"] = err[-300:]
        else:
            rec.update(summarise(doc))
        rows.append(rec)
    return rows, {"c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        mutants = run_mutants()
        synthetic, hashes = run_synthetic()
        result = {"mutants": mutants, "synthetic": synthetic, "synthetic_commits": hashes}
        (OUT / "blindspot-probe.json").write_text(
            json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
        for rec in mutants + synthetic:
            print(rec["case"])
            print("    expected:", rec["expected"])
            print("    exit:", rec["exit"], "| defects:", rec.get("defects", rec.get("error")),
                  "| required:", rec.get("required"), "| round_commits:", rec.get("round_commits"),
                  "| post:", rec.get("post_report"), "| committed:", rec.get("report_committed"))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
