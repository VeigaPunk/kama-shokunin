#!/usr/bin/env python3
"""FollowFixture: repo-local ``log.follow`` flips ``report_cutoff()`` in report-landing-audit.py.

Round-23 grid fixture (seat CloseKama22.FollowFixture, leaf). Each case builds fresh lane and
fleet repositories under a mkdtemp directory in /tmp (never the real lane or fleet checkouts),
commits a kama round-1 report history that contains a rename, and runs an auditor file with
--json. The knob that varies is repo-local ``log.follow`` in the FLEET fixture only. The
auditor's git_env() strips GIT_* variables and disables global and system config, but not the
repository's own .git/config, so a fleet-local ``log.follow`` reaches report_cutoff().

Cutoff contracts, both computed from the same fixture:
  path     git log --diff-filter=A -- <rel>            frozen base at 4fe9339f
  lineage  git log --follow --diff-filter=A -- <rel>   first add of the report file across renames

Entry points for the grid:
  run_case(auditor, case, log_follow)   one fixture, one auditor, one config -> dict
  run_matrix(auditors)                  every case x {log.follow unset, true} x auditors

Usage:
  follow_case.py                          frozen oracle (blob at --oracle-rev of --lane-repo)
  follow_case.py --auditor NAME=PATH      add an auditor file; repeatable
  follow_case.py --contract path --json   judge against the path contract; JSON output

Exit: 0 every row matches --contract; 1 some row does not; 2 harness error.
Standalone: stdlib only; does not import the auditor.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

BASE_REV = "4fe9339f8fc3a4a4a479d9c938a850da12f1124d"
DEFAULT_LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
ORACLE = "tools/report-landing-audit.py"
LANE = "kama"
ROUND = 1
REL = f".ufo/reports/round-{ROUND}/{LANE}.md"
DRAFT = "drafts/kama-r1.md"
DRAFT_SECOND = "drafts/kama-r1-second.md"
LANE_AUTHOR = f"{LANE}-shokunin"
FLEET_AUTHOR = "fixture-fleet"
CONTRACTS = ("lineage", "path")

T_A = "# Round 1 report\n## Work performed\nfixture\n## Landed changes\n- `{A}` start\n"
T_AB = T_A + "- `{B}` finish\n"
T_LATE = T_A + "Late note without a citation.\n"
T_SECOND = ("# Round 1 report, second draft\n## Work performed\nfixture two\n"
            "## Landed changes\n- `{A}` start\n")


@dataclasses.dataclass(frozen=True)
class Step:
    op: str                   # "write" | "move" | "remove"
    when: int                 # fleet commit author and committer time (unix seconds)
    message: str
    path: str                 # write/remove target, or move source
    dst: str | None = None    # move destination
    text: str | None = None   # content for write, or for an edited move; {A}/{B} = lane SHAs


@dataclasses.dataclass(frozen=True)
class Expect:
    cutoff: int
    verdict: str                    # "clean" | "failed"
    omitted: tuple[str, ...] = ()   # lane labels reported as landed-omitted


@dataclasses.dataclass(frozen=True)
class Case:
    name: str
    about: str
    lane: tuple[tuple[str, int, str], ...]   # (label, author time, subject)
    fleet: tuple[Step, ...]
    lineage: Expect
    path: Expect


LANE_AB = (("A", 1000, "round-1: start"), ("B", 2000, "round-1: finish"))

CASES = (
    Case("C0-no-rename",
         "control: canonical add at 1500; round commit B (2000) never cited",
         LANE_AB,
         (Step("write", 1500, "report: add at canonical path", REL, text=T_A),),
         lineage=Expect(1500, "clean"), path=Expect(1500, "clean")),
    Case("C1-late-edit",
         "control: canonical add at 1500; uncited edit at 2500; no rename",
         LANE_AB,
         (Step("write", 1500, "report: add", REL, text=T_A),
          Step("write", 2500, "report: late edit", REL, text=T_LATE)),
         lineage=Expect(1500, "clean"), path=Expect(1500, "clean")),
    Case("G1-move-uncited",
         "draft at 1500 moved unchanged to canonical at 2500; B (2000) uncited",
         LANE_AB,
         (Step("write", 1500, "report: draft", DRAFT, text=T_A),
          Step("move", 2500, "report: move to canonical path", DRAFT, dst=REL)),
         lineage=Expect(1500, "clean"), path=Expect(2500, "failed", ("B",))),
    Case("G2-move-cites-B",
         "as G1, but the move at 2500 also cites B",
         LANE_AB,
         (Step("write", 1500, "report: draft", DRAFT, text=T_A),
          Step("move", 2500, "report: move and cite B", DRAFT, dst=REL, text=T_AB)),
         lineage=Expect(1500, "clean"), path=Expect(2500, "clean")),
    Case("G3-move-pre-content",
         "B (1200) precedes the draft at 1500; move at 2500 unchanged; B uncited",
         (("A", 1000, "round-1: start"), ("B", 1200, "round-1: finish")),
         (Step("write", 1500, "report: draft", DRAFT, text=T_A),
          Step("move", 2500, "report: move to canonical path", DRAFT, dst=REL)),
         lineage=Expect(1500, "failed", ("B",)), path=Expect(2500, "failed", ("B",))),
    Case("G5-remove-then-move",
         "canonical report removed at 1100; second draft written at 1300 after B (1200, "
         "uncited) and moved to canonical at 1500",
         (("A", 900, "round-1: start"), ("B", 1200, "round-1: finish")),
         (Step("write", 1000, "report: first add", REL, text=T_A),
          Step("remove", 1100, "report: remove first", REL),
          Step("write", 1300, "report: second draft", DRAFT_SECOND, text=T_SECOND),
          Step("move", 1500, "report: move second to canonical", DRAFT_SECOND, dst=REL)),
         lineage=Expect(1300, "failed", ("B",)), path=Expect(1000, "clean")),
)


def hermetic_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    env.update(extra or {})
    return env


def git(repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, env=hermetic_env(env))
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} in {repo}: rc={proc.returncode}: "
                           f"{proc.stderr.strip()}")
    return proc.stdout


def commit(repo: Path, author: str, when: int, message: str) -> str:
    stamp = f"@{when} +0000"
    git(repo, "add", "-A")
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty",
        "-m", message,
        env={"GIT_AUTHOR_NAME": author, "GIT_COMMITTER_NAME": author,
             "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
             "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
             "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp})
    return git(repo, "rev-parse", "HEAD").strip()


def fill_placeholders(text: str, shas: dict[str, str]) -> str:
    for label, sha in shas.items():
        text = text.replace("{" + label + "}", sha[:9])
    return text


def apply(fleet: Path, step: Step, shas: dict[str, str]) -> None:
    source = fleet / step.path
    if step.op == "write":
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(fill_placeholders(step.text or "", shas), encoding="utf-8")
    elif step.op == "move":
        dest = fleet / step.dst
        dest.parent.mkdir(parents=True, exist_ok=True)
        os.replace(source, dest)
        if step.text is not None:
            dest.write_text(fill_placeholders(step.text, shas), encoding="utf-8")
    elif step.op == "remove":
        source.unlink()
    else:
        raise ValueError(f"unknown step op {step.op!r}")


def build(root: Path, case: Case, log_follow: bool) -> tuple[Path, Path, dict[str, str]]:
    lane, fleet = root / "lane", root / "fleet"
    for repo in (lane, fleet):
        repo.mkdir()
        git(repo, "init", "-q", "-b", "master")
    shas = {label: commit(lane, LANE_AUTHOR, when, subject)
            for label, when, subject in case.lane}
    for step in case.fleet:
        apply(fleet, step, shas)
        commit(fleet, FLEET_AUTHOR, step.when, step.message)
    if log_follow:
        git(fleet, "config", "--local", "log.follow", "true")
    return lane, fleet, shas


def audit(auditor: Path, lane: Path, fleet: Path) -> tuple[int, dict | None, str]:
    proc = subprocess.run(
        [sys.executable, str(auditor), "--lane-repo", str(lane),
         "--fleet-repo", str(fleet), "--branch", "master", "--lane", LANE,
         "--rounds", str(ROUND), "--no-errata", "--json"],
        capture_output=True, text=True, env=hermetic_env())
    try:
        doc = json.loads(proc.stdout) if proc.stdout.strip() else None
    except json.JSONDecodeError:
        doc = None
    return proc.returncode, doc, proc.stderr.strip()


def observe(case: Case, rc: int, doc: dict | None, err: str,
            shas: dict[str, str]) -> dict:
    if doc is None:
        return {"rc": rc, "verdict": "could-not-evaluate", "error": err}
    res = doc["results"][0]
    cutoff = res["cutoff"]
    names = {sha: label for label, sha in shas.items()}
    when = {label: t for label, t, _ in case.lane}
    omitted = sorted(names.get(d["token"], d["token"]) for d in res["defects"]
                     if d["kind"] == "landed-omitted")
    other = sorted(f"{d['kind']}:{d['token']}" for d in res["defects"]
                   if d["kind"] != "landed-omitted")
    required = sorted(k for k, t in when.items() if t <= cutoff)
    return {"rc": rc, "verdict": doc["summary"]["status"], "cutoff": cutoff,
            "required": res["required"], "required_labels": required,
            "post_report": sorted(names.get(s, s) for s in res["post_report"]),
            "omitted": omitted, "other_defects": other,
            "count_ok": res["required"] == len(required)}


def judge(case: Case, observed: dict) -> dict[str, bool]:
    verdicts = {}
    for contract in CONTRACTS:
        exp: Expect = getattr(case, contract)
        verdicts[contract] = (
            observed.get("verdict") == exp.verdict
            and observed.get("cutoff") == exp.cutoff
            and observed.get("omitted") == sorted(exp.omitted)
            and observed.get("other_defects") == []
            and observed.get("count_ok") is True)
    return verdicts


def run_case(auditor: Path, case: Case, log_follow: bool, oracle: str = "auditor") -> dict:
    """One fresh fixture, one auditor run, one repo-local log.follow setting."""
    with tempfile.TemporaryDirectory(prefix=f"follow-{case.name}-", dir="/tmp") as tmp:
        lane, fleet, shas = build(Path(tmp), case, log_follow)
        rc, doc, err = audit(auditor, lane, fleet)
        observed = observe(case, rc, doc, err, shas)
    return {"oracle": oracle, "case": case.name, "log_follow": log_follow,
            **observed, "match": judge(case, observed)}


def run_matrix(auditors: list[tuple[str, Path]]) -> list[dict]:
    return [run_case(auditor, case, log_follow, oracle)
            for oracle, auditor in auditors
            for case in CASES
            for log_follow in (False, True)]


def summarize(rows: list[dict]) -> dict:
    summary: dict[str, dict] = {}
    for oracle in dict.fromkeys(r["oracle"] for r in rows):
        mine = [r for r in rows if r["oracle"] == oracle]
        flips = []
        for case in CASES:
            off = next(r for r in mine if r["case"] == case.name and not r["log_follow"])
            on = next(r for r in mine if r["case"] == case.name and r["log_follow"])
            flips.append({"case": case.name,
                          "verdict_flip": off["verdict"] != on["verdict"],
                          "cutoff_flip": off.get("cutoff") != on.get("cutoff")})
        summary[oracle] = {"rows": len(mine),
                           "match_lineage": sum(r["match"]["lineage"] for r in mine),
                           "match_path": sum(r["match"]["path"] for r in mine),
                           "flips": flips}
    return summary


def render(rows: list[dict], summary: dict, contract: str) -> str:
    out = [f"{'oracle':<12}{'case':<20}{'log.follow':<11}{'cutoff':>7}  {'verdict':<19}"
           f"{'req':>4}  {'post_report':<12}{'omitted':<9}{'ok':<4}"]
    for r in rows:
        out.append(
            f"{r['oracle']:<12}{r['case']:<20}{('true' if r['log_follow'] else 'unset'):<11}"
            f"{str(r.get('cutoff', '-')):>7}  {r['verdict']:<19}"
            f"{str(r.get('required', '-')):>4}  {','.join(r.get('post_report', [])) or '-':<12}"
            f"{','.join(r.get('omitted', [])) or '-':<9}"
            f"{'yes' if r['match'][contract] else 'NO':<4}")
    out.append("")
    for oracle, info in summary.items():
        verdict = [f["case"] for f in info["flips"] if f["verdict_flip"]]
        cutoff = [f["case"] for f in info["flips"]
                  if f["cutoff_flip"] and not f["verdict_flip"]]
        out.append(f"{oracle}: matches lineage {info['match_lineage']}/{info['rows']}, "
                   f"path {info['match_path']}/{info['rows']}; "
                   f"verdict flips by log.follow: {', '.join(verdict) or 'none'}; "
                   f"cutoff-only flips: {', '.join(cutoff) or 'none'}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lane-repo", default=DEFAULT_LANE)
    ap.add_argument("--oracle-rev", default=BASE_REV)
    ap.add_argument("--auditor", action="append", default=[], metavar="NAME=PATH")
    ap.add_argument("--contract", choices=CONTRACTS, default="lineage")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        with tempfile.TemporaryDirectory(prefix="follow-oracle-", dir="/tmp") as tmp:
            frozen = Path(tmp, "report-landing-audit.frozen.py")
            frozen.write_text(git(Path(args.lane_repo), "show",
                                  f"{args.oracle_rev}:{ORACLE}"), encoding="utf-8")
            auditors = [("frozen", frozen)]
            for item in args.auditor:
                name, sep, path = item.partition("=")
                if not sep or not name or not path:
                    raise ValueError(f"--auditor wants NAME=PATH, got {item!r}")
                auditors.append((name, Path(path)))
            rows = run_matrix(auditors)
    except (RuntimeError, ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"harness error: {exc}", file=sys.stderr)
        return 2
    summary = summarize(rows)
    ok = all(r["match"][args.contract] for r in rows)
    if args.json:
        print(json.dumps({"contract": args.contract, "rows": rows, "summary": summary},
                         indent=1, sort_keys=True))
    else:
        print(render(rows, summary, args.contract))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
