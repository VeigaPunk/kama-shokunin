#!/usr/bin/env python3
"""Audit kama round reports for unresolvable commit citations and landed-commit omissions.

Usage: report-landing-audit.py [--rounds 10-20 | --rounds 10-] [--report N=PATH ...]
                               [--errata PATH | --no-errata] [--json]
       report-landing-audit.py --selftest

Population: the fleet reports `.ufo/reports/round-N/kama.md` for the selected
rounds (`A-B` inclusive, `A-` = every round >= A with a fleet report).
Defect kinds (finite, mechanical; no prose judgment):

  unresolved-full-hash  a 40-hex token anywhere in the report that is no git
                        object in the lane repo or the fleet repo
  landed-unresolved     a 7..40-hex token inside `## Landed changes` that
                        contains a digit and a letter (40-hex always) and is
                        no commit in either repo
  landed-ambiguous      such a token that is an ambiguous abbreviation
  landed-omitted        a lane commit by `<lane>-shokunin` whose subject starts
                        `round-N:` or `checkpoint(rN)` and whose AUTHOR time is
                        no later than the author time of the fleet commit that
                        first added the report, not cited in `## Landed
                        changes` by a >=7-hex prefix
  landed-section-missing  the report has no `## Landed changes` section

Author time is used because rebases (jj-lane.sh recovery) rewrite committer
time but keep author time. Cross-repository clock skew is not detectable.
Lane commits authored after the report are `post_report` and not required.
`--report N=PATH` audits a draft; when the fleet already holds round N's
report, its first-add time is still the cutoff, otherwise "now" is.

Errata (`registry/report-landing-errata.tsv`, read from the committed
`--branch` blob unless `--errata PATH`): one row per corrected defect,
`round<TAB>kind<TAB>token<TAB>correction<TAB>evidence`. A defect is corrected
only by a row with equal round, kind and token. Rows for selected rounds
that match no defect are `errata-unmatched`. A row is `errata-invalid` when
its correction is not a lane/fleet commit (resolvable kinds) or, for
`landed-omitted`, differs from the omitted commit itself.

Exit: 0 clean (no uncorrected defect, no unmatched/invalid errata row);
1 failed (at least one); 2 could-not-evaluate (missing/irregular report,
unusable git, malformed ledger, empty round selection, output failure).
Errors are never verdicts.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import time

LANE = "kama"
ERRATA = "registry/report-landing-errata.tsv"
FULL = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{40}(?![0-9A-Za-z])")
ABBREV = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")
KINDS = ("unresolved-full-hash", "landed-unresolved", "landed-ambiguous",
         "landed-omitted", "landed-section-missing")
RESOLVABLE = ("unresolved-full-hash", "landed-unresolved", "landed-ambiguous",
              "landed-omitted")
SEP, END = "\x1f", "\x1e"


class EvalError(Exception):
    """Could not evaluate: never converted into a verdict."""


def git_env(**extra):
    """No inherited GIT_* variables and no user/system config, so neither
    the audited repos nor the selftest fixtures can be redirected."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", **extra)
    return env


def git(repo, *args, stdin=None, env=None):
    try:
        proc = subprocess.run(["git", "-C", str(repo), *args], input=stdin,
                              capture_output=True, text=True,
                              env=env or git_env())
    except OSError as exc:
        raise EvalError(f"cannot run git: {exc}") from exc
    if proc.returncode != 0:
        raise EvalError(f"git {' '.join(args)} in {repo}: rc={proc.returncode} "
                        f"{proc.stderr.strip()}")
    return proc.stdout


def lookup(repos, tokens, peel=""):
    """{token: 'found'|'ambiguous'|'missing'} across repos, via one
    `cat-file --batch-check` per repo; a git failure is EvalError."""
    tokens = sorted(set(tokens))
    status = {t: "missing" for t in tokens}
    if not tokens:
        return status
    for repo in repos:
        out = git(repo, "cat-file", "--batch-check",
                  stdin="".join(f"{t}{peel}\n" for t in tokens))
        lines = out.split("\n")[:len(tokens)]
        if len(lines) != len(tokens):
            raise EvalError(f"cat-file --batch-check in {repo}: short output")
        for token, line in zip(tokens, lines):
            if line.endswith(" missing"):
                continue
            if line.endswith(" ambiguous"):
                if status[token] != "found":
                    status[token] = "ambiguous"
                continue
            parts = line.split(" ")
            if len(parts) != 3 or not re.fullmatch(r"[0-9a-f]{40}", parts[0]):
                raise EvalError(f"cat-file in {repo}: unexpected {line!r}")
            status[token] = "found"
    return status


def landed_section(text):
    match = re.search(r"^## Landed changes[^\n]*\n(.*?)(?=^## |\Z)", text,
                      re.S | re.M)
    return None if match is None else match.group(1)


def checkable_abbrev(token):
    """A Landed token is checked as a citation only if it cannot be an
    ordinary word or number: 40 hex, or both a digit and a letter."""
    return len(token) == 40 or (re.search(r"[0-9]", token) is not None
                                and re.search(r"[a-f]", token) is not None)


def round_commits(lane_repo, branch, lane, rnd):
    out = git(lane_repo, "log", f"--format=%H{SEP}%an{SEP}%ct{SEP}%s{END}",
              branch)
    pat = re.compile(rf"^(?:round-{rnd}:|checkpoint\(r{rnd}\))")
    rows = []
    for record in out.split(END):
        record = record.lstrip("\n")
        if not record:
            continue
        fields = record.split(SEP, 3)
        if len(fields) != 4 or not fields[2].isdigit():
            raise EvalError(f"unexpected git log record {record[:80]!r}")
        sha, author, atime, subject = fields
        if author == f"{lane}-shokunin" and pat.match(subject):
            rows.append({"sha": sha, "atime": int(atime), "subject": subject})
    return rows


def report_cutoff(fleet_repo, rel):
    out = git(fleet_repo, "log", "--diff-filter=A", "--format=%ct", "--",
              rel).split()
    return int(out[-1]) if out else None


def read_report(path):
    try:
        if not stat.S_ISREG(os.stat(path).st_mode):
            raise EvalError(f"{path}: not a regular file")
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise EvalError(f"cannot read {path}: {exc}") from exc


def audit_round(lane_repo, fleet_repo, branch, lane, rnd, path):
    rel = f".ufo/reports/round-{rnd}/{lane}.md"
    report = Path(path) if path else Path(fleet_repo) / rel
    text = read_report(report)
    cutoff = report_cutoff(fleet_repo, rel)
    committed = cutoff is not None
    if cutoff is None:
        if path is None:
            raise EvalError(f"round {rnd}: {rel} has no fleet commit")
        cutoff = int(time.time())
    repos = (lane_repo, fleet_repo)
    defects = []
    full = lookup(repos, FULL.findall(text))
    defects += [{"kind": "unresolved-full-hash", "token": t}
                for t, s in full.items() if s != "found"]
    section = landed_section(text)
    commits = round_commits(lane_repo, branch, lane, rnd)
    pre = [c for c in commits if c["atime"] <= cutoff]
    post = [c for c in commits if c["atime"] > cutoff]
    if section is None:
        defects.append({"kind": "landed-section-missing", "token": "-"})
        section = ""
    cited = set(ABBREV.findall(section))
    status = lookup(repos, [t for t in cited if checkable_abbrev(t)],
                    "^{commit}")
    for token, state in status.items():
        if state == "missing":
            defects.append({"kind": "landed-unresolved", "token": token})
        elif state == "ambiguous":
            defects.append({"kind": "landed-ambiguous", "token": token})
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


def parse_errata(text, origin):
    rows = []
    for num, line in enumerate(text.split("\n"), 1):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 5 or not parts[0].isdigit() or parts[1] not in KINDS:
            raise EvalError(f"errata {origin}:{num}: malformed row")
        rows.append({"line": num, "round": int(parts[0]), "kind": parts[1],
                     "token": parts[2], "correction": parts[3],
                     "evidence": parts[4]})
    return rows


def load_errata(args, lane_repo):
    if args.no_errata:
        return []
    if args.errata:
        try:
            return parse_errata(Path(args.errata).read_text(encoding="utf-8"),
                                args.errata)
        except (OSError, UnicodeDecodeError) as exc:
            raise EvalError(f"cannot read errata {args.errata}: {exc}") from exc
    return parse_errata(git(lane_repo, "show", f"{args.branch}:{ERRATA}"),
                        f"{args.branch}:{ERRATA}")


def apply_errata(results, errata, repos):
    selected = {r["round"] for r in results}
    used = set()
    for res in results:
        for defect in res["defects"]:
            match = [e for e in errata if e["round"] == res["round"]
                     and e["kind"] == defect["kind"]
                     and e["token"] == defect["token"]]
            defect["corrected_by"] = [e["line"] for e in match]
            used.update(e["line"] for e in match)
    unmatched = [e for e in errata
                 if e["round"] in selected and e["line"] not in used]
    status = lookup(repos, [e["correction"] for e in errata
                            if e["kind"] in RESOLVABLE], "^{commit}")
    invalid = [e for e in errata if e["kind"] in RESOLVABLE and (
        status.get(e["correction"]) != "found"
        or (e["kind"] == "landed-omitted" and e["correction"] != e["token"]))]
    return unmatched, invalid


def parse_rounds(spec, fleet_repo, lane):
    rounds = set()
    for part in spec.split(","):
        part = part.strip()
        if re.fullmatch(r"\d+", part):
            rounds.add(int(part))
            continue
        m = re.fullmatch(r"(\d+)-(\d*)", part)
        if not m:
            raise EvalError(f"--rounds: bad item {part!r}")
        lo = int(m.group(1))
        if m.group(2):
            hi = int(m.group(2))
            if hi < lo:
                raise EvalError(f"--rounds: empty range {part!r}")
            rounds.update(range(lo, hi + 1))
        else:
            present = [int(p.name.split("-", 1)[1])
                       for p in (Path(fleet_repo) / ".ufo/reports").glob("round-*")
                       if p.name.split("-", 1)[1].isdigit()
                       and (p / f"{lane}.md").is_file()]
            rounds.update(n for n in present if n >= lo)
    return rounds


def run(args):
    lane_repo = Path(args.lane_repo).resolve()
    fleet_repo = Path(args.fleet_repo).resolve()
    overrides = {}
    for item in args.report or []:
        key, sep, value = item.partition("=")
        if not sep or not key.isdigit() or not value:
            raise EvalError(f"--report wants N=PATH, got {item!r}")
        overrides[int(key)] = value
    rounds = sorted(parse_rounds(args.rounds, fleet_repo, args.lane)
                    | set(overrides))
    if not rounds:
        raise EvalError("no rounds selected")
    git(lane_repo, "rev-parse", "--verify", f"{args.branch}^{{commit}}")
    git(fleet_repo, "rev-parse", "--verify", "HEAD^{commit}")
    results = [audit_round(lane_repo, fleet_repo, args.branch, args.lane, r,
                           overrides.get(r)) for r in rounds]
    errata = load_errata(args, lane_repo)
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

def _commit(repo, msg, author, when, path="f", committed=None):
    env = git_env(GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
                  GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
                  GIT_AUTHOR_DATE=f"@{when} +0000",
                  GIT_COMMITTER_DATE=f"@{committed or when} +0000")
    target = Path(repo) / path
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "a", encoding="utf-8") as fh:
        fh.write(msg + "\n")
    git(repo, "add", path, env=env)
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg, env=env)
    return git(repo, "rev-parse", "HEAD").strip()


def _ns(base, **kw):
    return argparse.Namespace(**{**vars(base), **kw})


def selftest():
    cases = []

    def check(name, cond):
        cases.append((name, bool(cond)))

    def is_error(fn):
        try:
            fn()
        except EvalError:
            return True
        return False

    with tempfile.TemporaryDirectory(prefix="report-landing-selftest-") as tmp:
        decoy = Path(tmp, "decoy.git")
        git(tmp, "init", "-q", "--bare", str(decoy))
        decoy_before = sorted(p.name for p in (decoy / "objects").iterdir())
        saved = os.environ.get("GIT_DIR")
        os.environ["GIT_DIR"] = str(decoy)
        try:
            lane, fleet = Path(tmp, "lane"), Path(tmp, "fleet")
            for repo in (lane, fleet):
                repo.mkdir()
                git(repo, "init", "-q", "-b", "master")
            a = _commit(lane, "round-1: work", "kama-shokunin", 1000)
            b = _commit(lane, "round-1:measure", "kama-shokunin", 1100)
            c = _commit(lane, "checkpoint(r1) save", "kama-shokunin", 1150)
            # rebased after the report: committer time later, author earlier
            d = _commit(lane, "round-1: rebased", "kama-shokunin", 1155,
                        committed=5000)
            _commit(lane, "round-1: foreign author", "someone", 1160)
            _commit(lane, "round-1: lookalike", "kama-shokunin-extra", 1161)
            _commit(lane, "round-10: other round", "kama-shokunin", 1170)
            _commit(lane, "xround-1: prefixed", "kama-shokunin", 1171)
            mash = a[:20] + b[20:]
            rep = fleet / ".ufo/reports/round-1/kama.md"
            rep.parent.mkdir(parents=True)
            rep.write_text(
                "# r1\n## Work performed\nmeasured at " + mash + "\n"
                "prefix ## Landed changes is not a heading\n"
                "## Landed changes (commits)\n- `" + a[:9] + "` work\n- `" + b
                + "` measure\n- `" + d[:7] + "` rebased\n- `deadbee1` typo\n"
                "- words: defaced acceded 1234567 20261021 " + "f" * 39 + "\n"
                "- short " + "e" * 6 + " and " + a[:7] + "g\n"
                "## Before\n" + c[:9] + " cited outside\n",
                encoding="utf-8")
            _commit(fleet, "round-1: kama report", "kama-shokunin", 1200,
                    ".ufo/reports/round-1/kama.md")
            late = _commit(lane, "round-1: late advice", "kama-shokunin", 1300)
            base = argparse.Namespace(
                lane_repo=str(lane), fleet_repo=str(fleet), branch="master",
                lane="kama", rounds="1", report=None, errata=None,
                no_errata=True)
            rc, doc = run(base)
            res = doc["results"][0]
            kinds = sorted((x["kind"], x["token"]) for x in res["defects"])
            check("raw-fails", rc == 1)
            check("mashup-detected", ("unresolved-full-hash", mash) in kinds)
            check("checkpoint-without-colon-omission-detected",
                  ("landed-omitted", c) in kinds)
            check("bad-abbrev-detected", ("landed-unresolved", "deadbee1") in kinds)
            check("exact-defect-set", kinds == sorted([
                ("unresolved-full-hash", mash), ("landed-omitted", c),
                ("landed-unresolved", "deadbee1")]))
            check("subject-without-space-required",
                  not any(t == b for _, t in kinds) and res["required"] == 4)
            check("author-exact-other-round-and-prefix-ignored",
                  res["round_commits"] == 5)
            check("author-time-cutoff-survives-rebase",
                  d not in res["post_report"])
            check("post-report-excluded", res["post_report"] == [late])
            check("token-bounds", FULL.findall("f" * 39) == []
                  and ABBREV.findall("e" * 6) == []
                  and ABBREV.findall("a" * 7 + "g") == [])
            check("heading-anchor", landed_section(
                "prefix ## Landed changes\nx\n") is None
                and landed_section("## Landed changes (c)\nx\n") == "x\n")
            check("hex-words-not-citations", not checkable_abbrev("defaced")
                  and not checkable_abbrev("1234567")
                  and checkable_abbrev("deadbee1"))
            errata = Path(tmp, "errata.tsv")

            def with_rows(*rows):
                errata.write_text("".join("\t".join(map(str, r)) + "\n"
                                          for r in rows), encoding="utf-8")
                return run(_ns(base, no_errata=False, errata=str(errata)))

            good = [(1, "unresolved-full-hash", mash, a, "t"),
                    (1, "landed-omitted", c, c, "t"),
                    (1, "landed-unresolved", "deadbee1", b, "t")]
            rc, doc = with_rows(*good)
            check("errata-clean", rc == 0 and doc["summary"]["uncorrected"] == 0)
            rc, doc = with_rows(*good, (1, "landed-omitted", "0" * 40, a, "pad"))
            check("unmatched-errata-fails", rc == 1
                  and doc["summary"]["errata_unmatched"] == 1)
            rc, doc = with_rows(*good, (2, "landed-omitted", c, c, "x"))
            check("unselected-round-row-ignored", rc == 0)
            for label, row in (
                    ("round-must-equal", (2, "landed-omitted", c, c, "t")),
                    ("kind-must-equal", (1, "landed-unresolved", c, c, "t")),
                    ("token-must-equal", (1, "landed-omitted", c[:12], c, "t"))):
                rc, doc = with_rows(good[0], row, good[2])
                check(label, rc == 1 and doc["summary"]["uncorrected"] == 1)
            rc, doc = with_rows((1, "unresolved-full-hash", mash, "f" * 40, "x"),
                                *good[1:])
            check("invalid-correction-fails", rc == 1
                  and doc["summary"]["errata_invalid"] == 1)
            blob = git(lane, "rev-parse", "HEAD:f").strip()
            rc, doc = with_rows((1, "unresolved-full-hash", mash, blob, "x"),
                                *good[1:])
            check("blob-is-not-a-correction", rc == 1
                  and doc["summary"]["errata_invalid"] == 1)
            rc, doc = with_rows(good[0], (1, "landed-omitted", c, a, "other"),
                                good[2])
            check("omitted-correction-must-be-the-commit", rc == 1
                  and doc["summary"]["errata_invalid"] == 1)
            errata.write_text("1\tnot-a-kind\tx\ty\tz\n", encoding="utf-8")
            check("malformed-errata-is-error", is_error(
                lambda: run(_ns(base, no_errata=False, errata=str(errata)))))
            draft = Path(tmp, "draft.md")
            draft.write_text("## Landed changes\n" + "\n".join(
                x[:12] for x in (a, b, c, d)) + "\n## End\n", encoding="utf-8")
            rc, doc = run(_ns(base, report=[f"1={draft}"]))
            check("draft-uses-fleet-cutoff", rc == 0
                  and doc["results"][0]["required"] == 4
                  and doc["results"][0]["report_committed"])
            draft.write_text("## Work performed\n" + a + "\n", encoding="utf-8")
            rc, doc = run(_ns(base, report=[f"1={draft}"]))
            check("missing-section-fails", rc == 1 and any(
                x["kind"] == "landed-section-missing"
                for x in doc["results"][0]["defects"]))
            new_draft = Path(tmp, "draft2.md")
            new_draft.write_text("## Landed changes\nnone\n", encoding="utf-8")
            rc, doc = run(_ns(base, rounds="2", report=[f"2={new_draft}"]))
            check("uncommitted-draft-uses-now", rc == 0
                  and not doc["results"][0]["report_committed"])
            check("missing-report-is-error",
                  is_error(lambda: run(_ns(base, rounds="2"))))
            check("reversed-range-is-error",
                  is_error(lambda: run(_ns(base, rounds="3-2"))))
            check("empty-report-path-is-error",
                  is_error(lambda: run(_ns(base, report=["1="]))))
            check("irregular-report-is-error",
                  is_error(lambda: run(_ns(base, report=[f"1={tmp}"]))))
            check("unusable-git-is-error", is_error(
                lambda: run(_ns(base, lane_repo=str(Path(tmp, "nope"))))))
            check("open-range-finds-reports",
                  parse_rounds("1-", fleet, "kama") == {1})
        finally:
            if saved is None:
                os.environ.pop("GIT_DIR", None)
            else:
                os.environ["GIT_DIR"] = saved
        check("inherited-GIT_DIR-untouched", sorted(
            p.name for p in (decoy / "objects").iterdir()) == decoy_before)
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
    ap.add_argument("--rounds", default="10-")
    ap.add_argument("--report", action="append",
                    help="N=PATH: audit a draft report for round N")
    ap.add_argument("--errata")
    ap.add_argument("--no-errata", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.selftest:
            return selftest()
        status, doc = run(args)
        print(json.dumps(doc, indent=1, sort_keys=True) if args.json
              else render(doc), flush=True)
        return status
    except EvalError as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        try:
            print(f"could-not-evaluate: output: {exc}", file=sys.stderr)
        except OSError:
            pass
        return 2


if __name__ == "__main__":
    sys.exit(main())
