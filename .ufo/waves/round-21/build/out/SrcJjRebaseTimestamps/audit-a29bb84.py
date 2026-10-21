#!/usr/bin/env python3
"""Audit kama round reports for unresolvable commit citations and landed-commit omissions.

Usage: report-landing-audit.py [--rounds 10-20] [--report N=PATH ...]
                               [--errata PATH | --no-errata] [--json]
       report-landing-audit.py --selftest

Population: the fleet reports `.ufo/reports/round-N/kama.md` for the selected
rounds. Defect kinds (finite, mechanical; no prose judgment):

  unresolved-full-hash  a 40-hex token anywhere in the report that is no git
                        object in the lane repo or the fleet repo
  landed-unresolved     a 7..40-hex token inside `## Landed changes` that does
                        not resolve to a commit in either repo
  landed-omitted        a lane commit whose subject starts `round-N:` or
                        `checkpoint(rN)` (author `<lane>-shokunin`, committed no
                        later than the commit that first added the report)
                        that `## Landed changes` does not cite by a >=7-hex
                        prefix
  landed-section-missing  the report has no `## Landed changes` section

Commits made after the report was first committed are counted as
`post_report` and are not required in that report. A report passed with
`--report N=PATH` that is not yet committed uses the current time as cutoff.

Errata (`registry/report-landing-errata.tsv`, append-only): one row per
corrected defect, `round<TAB>kind<TAB>token<TAB>correction<TAB>evidence`.
A defect is corrected only by a row with the same round and kind whose token
equals the defect token. A row that matches no defect is `errata-unmatched`;
a row whose correction is not a resolvable lane/fleet commit (for the two
resolvable kinds) is `errata-invalid`. Both fail the run.

Exit: 0 clean (no uncorrected defect, no unmatched/invalid errata row);
1 failed (at least one); 2 could-not-evaluate (missing report, unusable git,
unreadable errata). Errors are never verdicts.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

LANE = "kama"
FULL = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{40}(?![0-9A-Za-z])")
ABBREV = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")
KINDS = ("unresolved-full-hash", "landed-unresolved", "landed-omitted",
         "landed-section-missing")
RESOLVABLE = ("unresolved-full-hash", "landed-unresolved", "landed-omitted")


class EvalError(Exception):
    """Could not evaluate: never converted into a verdict."""


def git(repo, *args, check=True):
    proc = subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise EvalError(f"git {' '.join(args)} in {repo}: rc={proc.returncode} "
                        f"{proc.stderr.strip()}")
    return proc


def is_object(repos, token, kind=""):
    spec = f"{token}^{{{kind}}}" if kind else token
    for repo in repos:
        proc = git(repo, "cat-file", "-e", spec, check=False)
        if proc.returncode == 0:
            return True
    return False


def landed_section(text):
    match = re.search(r"^## Landed changes[^\n]*\n(.*?)(?=^## |\Z)", text,
                      re.S | re.M)
    return None if match is None else match.group(1)


def round_commits(lane_repo, branch, lane, rnd):
    out = git(lane_repo, "log", "--format=%H%x09%an%x09%ct%x09%s",
              branch).stdout
    pat = re.compile(rf"^(?:round-{rnd}:|checkpoint\(r{rnd}\))")
    rows = []
    for line in out.splitlines():
        sha, author, ctime, subject = line.split("\t", 3)
        if author == f"{lane}-shokunin" and pat.match(subject):
            rows.append({"sha": sha, "ctime": int(ctime), "subject": subject})
    return rows


def report_cutoff(fleet_repo, rel):
    out = git(fleet_repo, "log", "--diff-filter=A", "--format=%ct", "--",
              rel).stdout.split()
    return int(out[-1]) if out else None


def audit_round(lane_repo, fleet_repo, branch, lane, rnd, path):
    rel = f".ufo/reports/round-{rnd}/{lane}.md"
    report = Path(path) if path else Path(fleet_repo) / rel
    try:
        text = report.read_text(encoding="utf-8")
    except OSError as exc:
        raise EvalError(f"round {rnd}: cannot read {report}: {exc}") from exc
    cutoff = report_cutoff(fleet_repo, rel) if path is None else None
    committed = cutoff is not None
    if cutoff is None:
        cutoff = int(time.time())
    repos = (lane_repo, fleet_repo)
    defects = []
    for token in sorted(set(FULL.findall(text))):
        if not is_object(repos, token):
            defects.append({"kind": "unresolved-full-hash", "token": token})
    section = landed_section(text)
    commits = round_commits(lane_repo, branch, lane, rnd)
    pre = [c for c in commits if c["ctime"] <= cutoff]
    post = [c for c in commits if c["ctime"] > cutoff]
    if section is None:
        defects.append({"kind": "landed-section-missing", "token": "-"})
        section = ""
    else:
        for token in sorted(set(ABBREV.findall(section))):
            if not is_object(repos, token, "commit"):
                defects.append({"kind": "landed-unresolved", "token": token})
    cited = set(ABBREV.findall(section))
    cited_anywhere = set(ABBREV.findall(text))
    for commit in pre:
        if not any(commit["sha"].startswith(t) for t in cited):
            defects.append({"kind": "landed-omitted", "token": commit["sha"],
                            "cited_elsewhere": any(
                                commit["sha"].startswith(t)
                                for t in cited_anywhere)})
    return {
        "round": rnd, "report": str(report), "report_committed": committed,
        "cutoff": cutoff, "round_commits": len(commits),
        "required": len(pre), "post_report": [c["sha"] for c in post],
        "defects": defects,
    }


def load_errata(path):
    if path is None:
        return []
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise EvalError(f"cannot read errata {path}: {exc}") from exc
    rows = []
    for num, line in enumerate(lines, 1):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 5 or not parts[0].isdigit() or parts[1] not in KINDS:
            raise EvalError(f"errata {path}:{num}: malformed row")
        rows.append({"line": num, "round": int(parts[0]), "kind": parts[1],
                     "token": parts[2], "correction": parts[3],
                     "evidence": parts[4]})
    return rows


def apply_errata(results, errata, repos):
    used = set()
    for res in results:
        for defect in res["defects"]:
            match = [e for e in errata if e["round"] == res["round"]
                     and e["kind"] == defect["kind"]
                     and e["token"] == defect["token"]]
            defect["corrected_by"] = [e["line"] for e in match]
            used.update(e["line"] for e in match)
    unmatched = [e for e in errata if e["line"] not in used]
    invalid = []
    for row in errata:
        if row["kind"] in RESOLVABLE and not is_object(
                repos, row["correction"], "commit"):
            invalid.append(row)
    return unmatched, invalid


def parse_rounds(spec):
    rounds = []
    for part in spec.split(","):
        if "-" in part:
            lo, hi = part.split("-", 1)
            rounds.extend(range(int(lo), int(hi) + 1))
        else:
            rounds.append(int(part))
    return rounds


def run(args):
    lane_repo = Path(args.lane_repo).resolve()
    fleet_repo = Path(args.fleet_repo).resolve()
    overrides = {}
    for item in args.report or []:
        key, _, value = item.partition("=")
        overrides[int(key)] = value
    rounds = sorted(set(parse_rounds(args.rounds)) | set(overrides))
    git(lane_repo, "rev-parse", "--verify", f"{args.branch}^{{commit}}")
    git(fleet_repo, "rev-parse", "--verify", "HEAD^{commit}")
    results = [audit_round(lane_repo, fleet_repo, args.branch, args.lane, r,
                           overrides.get(r)) for r in rounds]
    errata = [] if args.no_errata else load_errata(
        args.errata or lane_repo / "registry/report-landing-errata.tsv")
    unmatched, invalid = apply_errata(results, errata, (lane_repo, fleet_repo))
    by_kind = {k: 0 for k in KINDS}
    total = corrected = 0
    for res in results:
        for d in res["defects"]:
            total += 1
            by_kind[d["kind"]] += 1
            corrected += bool(d["corrected_by"])
    summary = {
        "rounds": rounds, "reports": len(results), "defects": total,
        "corrected": corrected, "uncorrected": total - corrected,
        "by_kind": by_kind, "errata_rows": len(errata),
        "errata_unmatched": len(unmatched), "errata_invalid": len(invalid),
        "required_commits": sum(r["required"] for r in results),
        "post_report_commits": sum(len(r["post_report"]) for r in results),
    }
    status = 0 if (summary["uncorrected"] == 0 and not unmatched
                   and not invalid) else 1
    summary["status"] = "clean" if status == 0 else "failed"
    return status, {"summary": summary, "results": results,
                    "errata_unmatched": unmatched, "errata_invalid": invalid}


def render(doc):
    s = doc["summary"]
    lines = []
    for res in doc["results"]:
        lines.append(f"round={res['round']} required={res['required']} "
                     f"post_report={len(res['post_report'])} "
                     f"defects={len(res['defects'])}")
        for d in res["defects"]:
            mark = "corrected" if d["corrected_by"] else "UNCORRECTED"
            lines.append(f"  {mark} {d['kind']} {d['token']}")
    for e in doc["errata_unmatched"]:
        lines.append(f"errata-unmatched line={e['line']} {e['kind']} {e['token']}")
    for e in doc["errata_invalid"]:
        lines.append(f"errata-invalid line={e['line']} correction={e['correction']}")
    lines.append(
        f"summary reports={s['reports']} defects={s['defects']} "
        f"corrected={s['corrected']} uncorrected={s['uncorrected']} "
        f"errata_unmatched={s['errata_unmatched']} "
        f"errata_invalid={s['errata_invalid']} status={s['status']}")
    return "\n".join(lines)


# --------------------------------------------------------------------- selftest

def _sh(repo, *args, env=None):
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   capture_output=True, text=True, env=env)


def _commit(repo, msg, author, when, path="f"):
    env = dict(os.environ, GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
               GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
               GIT_AUTHOR_DATE=f"@{when} +0000",
               GIT_COMMITTER_DATE=f"@{when} +0000")
    target = Path(repo) / path
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "a", encoding="utf-8") as fh:
        fh.write(msg + "\n")
    _sh(repo, "add", path, env=env)
    _sh(repo, "commit", "-q", "-m", msg, env=env)
    return git(repo, "rev-parse", "HEAD").stdout.strip()


def selftest():
    cases = []

    def check(name, cond):
        cases.append((name, bool(cond)))

    with tempfile.TemporaryDirectory(prefix="report-landing-selftest-") as tmp:
        lane, fleet = Path(tmp, "lane"), Path(tmp, "fleet")
        for repo in (lane, fleet):
            repo.mkdir()
            _sh(repo, "init", "-q", "-b", "master")
        a = _commit(lane, "round-1: work", "kama-shokunin", 1000)
        b = _commit(lane, "round-1: measure", "kama-shokunin", 1100)
        c = _commit(lane, "checkpoint(r1): save", "kama-shokunin", 1150)
        _commit(lane, "round-1: foreign author", "someone", 1160)
        _commit(lane, "round-10: other round", "kama-shokunin", 1170)
        mash = a[:20] + b[20:]
        rep = fleet / ".ufo/reports/round-1/kama.md"
        rep.parent.mkdir(parents=True)
        rep.write_text(
            "# r1\n## Work performed\nmeasured at " + mash + "\n"
            "## Landed changes\n- `" + a[:9] + "` work\n- `" + b + "` measure\n"
            "- `deadbee1` typo\n## Before\n" + c[:9] + " cited outside\n",
            encoding="utf-8")
        _commit(fleet, "round-1: kama report", "kama-shokunin", 1200,
                ".ufo/reports/round-1/kama.md")
        late = _commit(lane, "round-1: late advice", "kama-shokunin", 1300)
        base = argparse.Namespace(lane_repo=str(lane), fleet_repo=str(fleet),
                                  branch="master", lane="kama", rounds="1",
                                  report=None, errata=None, no_errata=True)
        rc, doc = run(base)
        kinds = sorted((d["kind"], d["token"]) for d in doc["results"][0]["defects"])
        check("raw-fails", rc == 1)
        check("mashup-detected", ("unresolved-full-hash", mash) in kinds)
        check("checkpoint-omission-detected", ("landed-omitted", c) in kinds)
        check("bad-abbrev-detected", ("landed-unresolved", "deadbee1") in kinds)
        check("exact-defect-count", len(kinds) == 3)
        check("foreign-author-and-other-round-ignored",
              doc["results"][0]["round_commits"] == 4)
        check("post-report-excluded", doc["results"][0]["post_report"] == [late])
        errata = Path(tmp, "errata.tsv")
        errata.write_text(
            f"1\tunresolved-full-hash\t{mash}\t{a}\tselftest\n"
            f"1\tlanded-omitted\t{c}\t{c}\tselftest\n"
            f"1\tlanded-unresolved\tdeadbee1\t{b}\tselftest\n",
            encoding="utf-8")
        rc, doc = run(argparse.Namespace(**{**vars(base), "no_errata": False,
                                            "errata": str(errata)}))
        check("errata-clean", rc == 0 and doc["summary"]["uncorrected"] == 0)
        with open(errata, "a", encoding="utf-8") as fh:
            fh.write(f"1\tlanded-omitted\t{'0' * 40}\t{a}\tpadding\n")
        rc, doc = run(argparse.Namespace(**{**vars(base), "no_errata": False,
                                            "errata": str(errata)}))
        check("unmatched-errata-fails", rc == 1
              and doc["summary"]["errata_unmatched"] == 1)
        errata.write_text(
            f"1\tunresolved-full-hash\t{mash}\t{'f' * 40}\tbad\n"
            f"1\tlanded-omitted\t{c}\t{c}\tselftest\n"
            f"1\tlanded-unresolved\tdeadbee1\t{b}\tselftest\n",
            encoding="utf-8")
        rc, doc = run(argparse.Namespace(**{**vars(base), "no_errata": False,
                                            "errata": str(errata)}))
        check("invalid-correction-fails", rc == 1
              and doc["summary"]["errata_invalid"] == 1)
        errata.write_text("1\tnot-a-kind\tx\ty\tz\n", encoding="utf-8")
        try:
            run(argparse.Namespace(**{**vars(base), "no_errata": False,
                                      "errata": str(errata)}))
            check("malformed-errata-is-error", False)
        except EvalError:
            check("malformed-errata-is-error", True)
        draft = Path(tmp, "draft.md")
        draft.write_text("## Landed changes\n" + "\n".join(
            x[:12] for x in (a, b, c, late)) + "\n## End\n", encoding="utf-8")
        rc, doc = run(argparse.Namespace(**{**vars(base), "rounds": "1",
                                            "report": [f"1={draft}"]}))
        check("uncommitted-draft-requires-all", rc == 0
              and doc["results"][0]["required"] == 4)
        draft.write_text("## Work performed\n" + a + "\n", encoding="utf-8")
        rc, doc = run(argparse.Namespace(**{**vars(base),
                                            "report": [f"1={draft}"]}))
        check("missing-section-fails", rc == 1 and any(
            d["kind"] == "landed-section-missing"
            for d in doc["results"][0]["defects"]))
        try:
            run(argparse.Namespace(**{**vars(base), "rounds": "2"}))
            check("missing-report-is-error", False)
        except EvalError:
            check("missing-report-is-error", True)
        try:
            run(argparse.Namespace(**{**vars(base),
                                      "lane_repo": str(Path(tmp, "nope"))}))
            check("unusable-git-is-error", False)
        except EvalError:
            check("unusable-git-is-error", True)
    failed = [n for n, ok in cases if not ok]
    for name, ok in cases:
        print(f"{'ok' if ok else 'FAIL'} {name}")
    print(f"selftest cases={len(cases)} failed={len(failed)}")
    return 0 if not failed else 1


def main(argv=None):
    here = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lane-repo", default=str(here))
    ap.add_argument("--fleet-repo", default=str(here.parent))
    ap.add_argument("--branch", default="master")
    ap.add_argument("--lane", default=LANE)
    ap.add_argument("--rounds", default="10-20")
    ap.add_argument("--report", action="append",
                    help="N=PATH: audit an uncommitted report for round N")
    ap.add_argument("--errata")
    ap.add_argument("--no-errata", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    try:
        status, doc = run(args)
    except (EvalError, ValueError) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(doc, indent=1, sort_keys=True) if args.json else render(doc))
    return status


if __name__ == "__main__":
    sys.exit(main())
