#!/usr/bin/env python3
"""Audit kama round reports for unresolvable commit citations and landed-commit omissions.

Usage: report-landing-audit.py [--rounds 10-20 | --rounds 10-] [--report N=PATH ...]
                               [--errata PATH | --no-errata] [--json]
       report-landing-audit.py --selftest

Population: the fleet reports `.ufo/reports/round-N/kama.md` for the selected
rounds (`A-B` inclusive, `A-` = every round >= A with a fleet report).
Defect kinds (finite, mechanical; no prose judgment):

  unresolved-full-hash  a 40-hex token in the report that is no git object in
                        the lane or fleet repo, except an occurrence inside
                        an exact Registry source URL from the committed
                        `corpus/SOURCES.md` blob, outside `## Landed changes`;
                        URL classification is not source-validity proof
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
unusable git or non-UTF-8 git output, shallow/grafted/non-sha1 repository,
malformed ledger, empty round selection, output failure).
Errors are never verdicts.

Repository trust (round 23, tests/report-audit/repo-state-grid.py):
refs/replace, lazy fetch, signature display, log re-encoding,
log.follow/log.showRoot and .mailmap are neutralized; a plain --branch name
means refs/heads/<name>; shallow, grafted, partial-clone, non-sha1 and
non-top-level repositories and ref-named citations are refused. Objects
borrowed through objects/info/alternates or a .git gitfile still resolve as
local, and other repository-local channels are not claimed. Audit trusted
repositories only; git >= 2.45 is required.
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
SOURCES = "corpus/SOURCES.md"
SOURCE_URL = re.compile(r"https?://[^ \t\n\r\f\v|]+")
SOURCE_URL_END = r"(?=[\s`'\"<>()\[\]|,;*]|\Z)"
SOURCE_ROW = re.compile(r"S[0-9]{3,}")
FULL = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{40}(?![0-9A-Za-z])")
ABBREV = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")
KINDS = ("unresolved-full-hash", "landed-unresolved", "landed-ambiguous",
         "landed-omitted", "landed-section-missing")
RESOLVABLE = ("unresolved-full-hash", "landed-unresolved", "landed-ambiguous",
              "landed-omitted")


class EvalError(Exception):
    """Could not evaluate: never converted into a verdict."""


# Repository-local state that changed, crashed or hijacked verdicts in the
# round-23 fault grid: refs/replace substitutions, promisor lazy fetches and
# signature verification (both may run repo-configured programs), re-encoded
# log output, log.follow/log.showRoot cutoffs and an eagerly read worktree
# .mailmap. Old git (< 2.45) rejects --no-lazy-fetch, which is an EvalError.
GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch",
                 "-c", "i18n.logOutputEncoding=UTF-8",
                 "-c", "log.follow=false", "-c", "log.showRoot=true",
                 "-c", "log.showSignature=false", "-c", "log.mailmap=false")


def git_env(**extra):
    """No inherited GIT_* variables and no user/system config. This alone
    does not isolate repository-local config or refs; git() adds
    GIT_ISOLATION for the channels the fault grid covers."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", **extra)
    return env


def git(repo, *args, stdin=None, env=None, errors="strict"):
    """stdout as UTF-8 text with universal newlines (as text mode did).
    Strict by default: undecodable output is an EvalError, never a
    traceback verdict. Callers that only match ASCII fields and never emit
    the text (lane log records, report path listing) pass surrogateescape."""
    try:
        proc = subprocess.run(["git", *GIT_ISOLATION, "-C", str(repo), *args],
                              input=None if stdin is None else stdin.encode(),
                              capture_output=True, env=env or git_env())
    except OSError as exc:
        raise EvalError(f"cannot run git: {exc}") from exc
    if proc.returncode != 0:
        raise EvalError(f"git {' '.join(args)} in {repo}: rc={proc.returncode} "
                        f"{proc.stderr.decode(errors='replace').strip()}")
    try:
        out = proc.stdout.decode("utf-8", errors)
    except UnicodeDecodeError as exc:
        raise EvalError(f"git {' '.join(args)} in {repo}: output is not "
                        f"UTF-8: {exc}") from exc
    return out.replace("\r\n", "\n").replace("\r", "\n")


def lookup(repos, tokens, peel=""):
    """{token: 'found'|'ambiguous'|'missing'} across repos, via
    `cat-file --batch-check` per repo; a git failure is EvalError. With a
    peel, git answers `missing` for an ambiguous short name, so the bare
    name is asked first to keep ambiguity visible."""
    tokens = sorted(set(tokens))
    status = {t: "missing" for t in tokens}
    if not tokens:
        return status
    if peel:
        bare = lookup(repos, tokens)
        status.update({t: "ambiguous" for t, s in bare.items()
                       if s == "ambiguous"})
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
            if line.endswith(" excluded") or line.endswith(" dangling"):
                continue
            parts = line.split(" ")
            if len(parts) != 3 or not re.fullmatch(r"[0-9a-f]{40}", parts[0]):
                raise EvalError(f"cat-file in {repo}: unexpected {line!r}")
            if not peel and not parts[0].startswith(token):
                # git resolved a same-named ref before the object prefix
                raise EvalError(f"{repo}: citation {token} names a ref")
            status[token] = "found"
    return status


def landed_match(text):
    return re.search(r"^## Landed changes[^\n]*\n(.*?)(?=^## |\Z)", text,
                     re.S | re.M)


def checkable_abbrev(token):
    """A Landed token is checked as a citation only if it cannot be an
    ordinary word or number: 40 hex, or both a digit and a letter."""
    return len(token) == 40 or (re.search(r"[0-9]", token) is not None
                                and re.search(r"[a-f]", token) is not None)


def round_commits(lane_repo, branch, lane, rnd):
    """NUL-delimited records: git truncates names and subjects at NUL, so
    no commit text can inject or shift a field (\\x1f/\\x1e can)."""
    out = git(lane_repo, "log", "-z", "--format=%H%x00%an%x00%at%x00%s",
              branch, errors="surrogateescape")
    fields = out.split("\0")
    if fields and fields[-1] == "":
        fields.pop()
    if len(fields) % 4:
        raise EvalError(f"unexpected git log output ({len(fields)} fields)")
    pat = re.compile(rf"^(?:round-{rnd}:|checkpoint\(r{rnd}\))")
    rows = []
    for i in range(0, len(fields), 4):
        sha, author, atime, subject = fields[i:i + 4]
        if (not re.fullmatch(r"[0-9a-f]{40}", sha)
                or not re.fullmatch(r"[0-9]{1,12}", atime)):
            raise EvalError(f"unexpected git log record {sha[:80]!r} "
                            f"{atime[:40]!r}")
        if author == f"{lane}-shokunin" and pat.match(subject):
            rows.append({"sha": sha, "atime": int(atime), "subject": subject})
    return rows


def report_cutoff(fleet_repo, rel):
    out = git(fleet_repo, "log", "--diff-filter=A", "--format=%at", "--",
              rel).split()
    return int(out[-1]) if out else None


def read_report(path):
    try:
        if not stat.S_ISREG(os.stat(path).st_mode):
            raise EvalError(f"{path}: not a regular file")
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise EvalError(f"cannot read {path}: {exc}") from exc


def census_source_urls(text):
    """Return the source URL and census-normalized form for each valid S-row."""
    urls = set()
    in_registry = False
    for line in text.split("\n"):
        if re.match(r" {0,3}##[ \t]", line):
            in_registry = line.lstrip(" ")[2:].strip(" \t") == "Registry"
            continue
        if re.match(r" {0,3}#[ \t]", line):
            in_registry = False
            continue
        if not in_registry or not re.match(r" {0,3}\|", line):
            continue
        cells = line.lstrip(" ").split("|")
        if len(cells) != 13 or not SOURCE_ROW.fullmatch(cells[1].strip(" \t")):
            continue
        match = SOURCE_URL.search(cells[2])
        if match is None or not match.group(0).startswith("https://"):
            continue
        full = match.group(0)
        census = re.sub(r"#[^ ]*$", "", full)
        census = re.sub(r"/$", "", census)
        census = re.sub(r"^[A-Za-z]+://", "", census)
        host, slash, rest = census.partition("/")
        urls.add((full, host.lower() + slash + rest))
    return urls


def load_source_urls(lane_repo, branch):
    """Read only the committed regular SOURCES.md blob; absent is legacy."""
    entry = git(lane_repo, "ls-tree", branch, "--", SOURCES).rstrip("\n")
    if not entry:
        return None
    metadata, sep, path = entry.partition("\t")
    fields = metadata.split()
    if (not sep or "\n" in entry or path != SOURCES or len(fields) != 3
            or fields[1] != "blob" or fields[0] not in ("100644", "100755")):
        raise EvalError(f"{branch}:{SOURCES}: not a regular blob")
    text = git(lane_repo, "cat-file", "blob", fields[2])
    forms = census_source_urls(text)
    if not forms:
        return None

    def alternatives(values):
        return "|".join(re.escape(value) for value in
                        sorted(values, key=len, reverse=True))

    full = alternatives({url for url, _ in forms})
    census = alternatives({url for _, url in forms})
    return re.compile(
        rf"(?<![A-Za-z0-9._~%+@:/-])(?:{full}|{census}){SOURCE_URL_END}")


def classify_full_hashes(text, source_urls, landed):
    """Keep FULL scanning unchanged except for exact URL occurrences."""
    if source_urls is None:
        return FULL.findall(text), []
    url_spans = [match.span() for match in source_urls.finditer(text)]
    lo, hi = landed.span() if landed else (-1, -1)
    tokens, classified, unclassified = [], set(), set()
    for match in FULL.finditer(text):
        start, end = match.span()
        token = match.group(0)
        if (lo <= start < hi or not any(
                left <= start and end <= right for left, right in url_spans)):
            tokens.append(token)
            unclassified.add(token)
        else:
            classified.add(token)
    return tokens, sorted(classified - unclassified)


def audit_round(lane_repo, fleet_repo, branch, lane, rnd, path, source_urls):
    rel = f".ufo/reports/round-{rnd}/{lane}.md"
    report = Path(path) if path else Path(fleet_repo) / rel
    if path:
        text = read_report(report)
    else:
        # committed fleet bytes, not a possibly edited working-tree copy
        try:
            text = git(fleet_repo, "show", f"HEAD:{rel}")
        except EvalError as exc:
            raise EvalError(f"round {rnd}: cannot read {rel} at fleet "
                            f"HEAD: {exc}") from exc
    cutoff = report_cutoff(fleet_repo, rel)
    committed = cutoff is not None
    if cutoff is None:
        if path is None:
            raise EvalError(f"round {rnd}: {rel} has no fleet commit")
        cutoff = int(time.time())
    repos = (lane_repo, fleet_repo)
    defects = []
    landed = landed_match(text)
    full_tokens, classified_hashes = classify_full_hashes(
        text, source_urls, landed)
    full = lookup(repos, full_tokens)
    defects += [{"kind": "unresolved-full-hash", "token": t}
                for t, s in full.items() if s != "found"]
    section = None if landed is None else landed.group(1)
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
        "source_url_hashes": classified_hashes,
        "defects": defects,
    }


def parse_errata(text, origin):
    rows = []
    for num, line in enumerate(text.split("\n"), 1):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 5 or not re.fullmatch(r"[0-9]+", parts[0]) \
                or parts[1] not in KINDS:
            raise EvalError(f"errata {origin}:{num}: malformed row")
        rows.append({"line": num, "round": int(parts[0]), "kind": parts[1],
                     "token": parts[2], "correction": parts[3],
                     "evidence": parts[4]})
    return rows


def load_errata(args, lane_repo, tip):
    if args.no_errata:
        return []
    if args.errata:
        try:
            return parse_errata(Path(args.errata).read_text(encoding="utf-8"),
                                args.errata)
        except (OSError, UnicodeDecodeError) as exc:
            raise EvalError(f"cannot read errata {args.errata}: {exc}") from exc
    return parse_errata(git(lane_repo, "show", f"{tip}:{ERRATA}"),
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
    # only hex corrections are looked up: a revision expression such as
    # HEAD or :/text is never a correction
    status = lookup(repos, [e["correction"] for e in errata
                            if e["kind"] in RESOLVABLE and re.fullmatch(
                                r"[0-9a-f]{7,40}", e["correction"])],
                    "^{commit}")
    invalid = [e for e in errata if e["kind"] in RESOLVABLE and (
        status.get(e["correction"]) != "found"
        or (e["kind"] == "landed-omitted" and e["correction"] != e["token"]))]
    return unmatched, invalid


def parse_rounds(spec, fleet_repo, lane):
    rounds = set()
    for part in spec.split(","):
        part = part.strip()
        if re.fullmatch(r"[0-9]+", part):
            rounds.add(int(part))
            continue
        m = re.fullmatch(r"([0-9]+)-([0-9]*)", part)
        if not m:
            raise EvalError(f"--rounds: bad item {part!r}")
        lo = int(m.group(1))
        if m.group(2):
            hi = int(m.group(2))
            if hi < lo:
                raise EvalError(f"--rounds: empty range {part!r}")
            rounds.update(range(lo, hi + 1))
        else:
            # committed fleet reports only, never working-tree drafts
            listed = git(fleet_repo, "ls-tree", "-r", "--name-only", "HEAD",
                         "--", ".ufo/reports", errors="surrogateescape")
            pat = re.compile(rf"\.ufo/reports/round-([0-9]+)/{re.escape(lane)}\.md")
            present = [int(m.group(1)) for m in map(pat.fullmatch,
                                                    listed.split("\n")) if m]
            rounds.update(n for n in present if n >= lo)
    return rounds


def check_history_repo(repo):
    """Refuse a repository whose visible history is not its object history
    (shallow boundary, info/grafts), whose missing objects belong to a
    promisor remote (absence is not evidence there), or whose object names
    the 40-hex scanners cannot read (non-sha1 object format)."""
    fmt = git(repo, "rev-parse", "--show-object-format").strip()
    if fmt != "sha1":
        raise EvalError(f"{repo}: object format {fmt!r}, not sha1")
    if git(repo, "rev-parse", "--show-prefix").strip():
        raise EvalError(f"{repo}: not a repository top level")
    if git(repo, "rev-parse", "--is-shallow-repository").strip() != "false":
        raise EvalError(f"{repo}: shallow repository")
    for rel in ("info/grafts", "objects/pack"):
        path = Path(repo, git(repo, "rev-parse", "--git-path", rel).strip())
        if rel == "info/grafts" and os.path.lexists(path):
            raise EvalError(f"{repo}: {path} rewrites history")
        if rel == "objects/pack" and path.is_dir() and any(
                p.suffix == ".promisor" for p in path.iterdir()):
            raise EvalError(f"{repo}: partial clone (promisor pack)")
    for line in git(repo, "config", "--list", "--name-only").split("\n"):
        if line == "extensions.partialclone" or re.fullmatch(
                r"remote\..+\.promisor", line):
            pass


def resolve_branch(lane_repo, branch):
    """Pin the lane tip once. A plain name is refs/heads/<name> first, so a
    same-named tag cannot shadow the branch; other revisions as given."""
    try:
        return git(lane_repo, "rev-parse", "--verify",
                   f"refs/heads/{branch}^{{commit}}").strip()
    except EvalError:
        return git(lane_repo, "rev-parse", "--verify",
                   f"{branch}^{{commit}}").strip()


def run(args):
    lane_repo = Path(args.lane_repo).resolve()
    fleet_repo = Path(args.fleet_repo).resolve()
    overrides = {}
    for item in args.report or []:
        key, sep, value = item.partition("=")
        if not sep or not re.fullmatch(r"[0-9]+", key) or not value:
            raise EvalError(f"--report wants N=PATH, got {item!r}")
        overrides[int(key)] = value
    rounds = sorted(parse_rounds(args.rounds, fleet_repo, args.lane)
                    | set(overrides))
    if not rounds:
        raise EvalError("no rounds selected")
    for repo in (lane_repo, fleet_repo):
        check_history_repo(repo)
    tip = resolve_branch(lane_repo, args.branch)
    git(fleet_repo, "rev-parse", "--verify", "HEAD^{commit}")
    source_urls = load_source_urls(lane_repo, tip)
    results = [audit_round(lane_repo, fleet_repo, tip, args.lane, r,
                           overrides.get(r), source_urls) for r in rounds]
    errata = load_errata(args, lane_repo, tip)
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
            edge = _commit(lane, "round-1: at cutoff", "kama-shokunin", 1200)
            mash = a[:20] + b[20:]
            rep = fleet / ".ufo/reports/round-1/kama.md"
            rep.parent.mkdir(parents=True)
            rep.write_text(
                "# r1\n## Work performed\nmeasured at " + mash + "\n"
                "prefix ## Landed changes is not a heading\n"
                "## Landed changes (commits)\n- `" + a[:9] + "` work\n- `" + b
                + "` measure\n- `" + d[:7] + "` rebased\n- `deadbee1` typo\n"
                "- `" + edge[:10] + "` boundary\n"
                "- words: defaced acceded 1234567 20261021 " + "f" * 39 + "\n"
                "- short " + "e" * 6 + " and " + a[:7] + "g\n"
                "## Before\n" + c[:9] + " cited outside\n",
                encoding="utf-8")
            # author time is the cutoff: committer time 6000 must not move it
            _commit(fleet, "round-1: kama report", "kama-shokunin", 1200,
                    ".ufo/reports/round-1/kama.md", committed=6000)
            body = rep.read_text(encoding="utf-8")
            for when, action in ((1400, "rm"), (1500, "add")):
                env = git_env(GIT_AUTHOR_NAME="x", GIT_COMMITTER_NAME="x",
                              GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
                              GIT_AUTHOR_DATE=f"@{when} +0000",
                              GIT_COMMITTER_DATE=f"@{when} +0000")
                if action == "rm":
                    git(fleet, "rm", "-q", ".ufo/reports/round-1/kama.md",
                        env=env)
                else:
                    rep.parent.mkdir(parents=True, exist_ok=True)
                    rep.write_text(body, encoding="utf-8")
                    git(fleet, "add", ".ufo/reports/round-1/kama.md", env=env)
                git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
                    f"report {action}", env=env)
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
                  not any(t == b for _, t in kinds) and res["required"] == 5)
            check("boundary-commit-required-not-post", edge not in
                  res["post_report"] and not any(t == edge for _, t in kinds))
            check("first-add-cutoff-not-readd", res["cutoff"] == 1200)
            check("author-exact-other-round-and-prefix-ignored",
                  res["round_commits"] == 6)
            check("author-time-cutoff-survives-rebase",
                  d not in res["post_report"])
            check("post-report-excluded", res["post_report"] == [late])
            check("token-bounds", FULL.findall("f" * 39) == []
                  and ABBREV.findall("e" * 6) == []
                  and ABBREV.findall("a" * 7 + "g") == [])
            check("heading-anchor", landed_match(
                "prefix ## Landed changes\nx\n") is None
                and landed_match("## Landed changes (c)\nx\n").group(1) == "x\n")
            check("hex-words-not-citations", not checkable_abbrev("defaced")
                  and not checkable_abbrev("1234567")
                  and checkable_abbrev("deadbee1")
                  and checkable_abbrev("1" * 40) and checkable_abbrev("f" * 40))
            foreign = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"
            source_url = (
                "https://GitHub.com/ggml-org/llama.cpp/blob/" + foreign
                + "/tools/server/README.md/#readme")
            census_url = (
                "github.com/ggml-org/llama.cpp/blob/" + foreign
                + "/tools/server/README.md")
            malformed_url = (
                "https://other.example/project/blob/" + foreign + "/source.cc")
            lead_url = (
                "https://other.example/project/blob/" + foreign + "/lead.cc")
            source_fixture = (
                "## Registry\n"
                "| id | source | kind | tier | scope | anchor | teaches | "
                "status | opened | recheck | used-by |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| S001 | upstream — " + source_url
                + " | code | A | fixture scope | fixture anchor | fixture "
                "teaches | mined | 2026-10-21 | on-release | — |\n"
                "| S002 | malformed — " + malformed_url
                + " | code | A | fixture scope | fixture anchor | fixture "
                "teaches | mined | 2026-10-21 | on-release |\n"
                "## Leads\n"
                "| S003 | lead — " + lead_url
                + " | code | A | fixture scope | fixture anchor | fixture "
                "teaches | mined | 2026-10-21 | on-release | — |\n")
            all_landed = "\n".join(
                f"- `{oid}`" for oid in (a, b, c, d, edge))
            source_draft = Path(tmp, "source-url-draft.md")

            def source_case(body, landed_lines=None):
                landed_lines = all_landed if landed_lines is None else landed_lines
                source_draft.write_text(
                    "## Work performed\n" + body + "\n"
                    "## Landed changes\n" + landed_lines + "\n",
                    encoding="utf-8")
                result, report = run(_ns(
                    base, report=[f"1={source_draft}"]))
                kinds = sorted((item["kind"], item["token"])
                               for item in report["results"][0]["defects"])
                return result, report, kinds

            rc, doc, kinds = source_case(source_url)
            check("absent-source-registry-is-no-exemption",
                  rc == 1 and kinds == [("unresolved-full-hash", foreign)]
                  and doc["results"][0]["source_url_hashes"] == [])
            _commit(lane, source_fixture, "source-fixture", 1250,
                    "corpus/SOURCES.md")
            rc, doc, kinds = source_case(source_url)
            check("curated-full-source-url-accepted",
                  rc == 0 and kinds == []
                  and doc["results"][0]["source_url_hashes"] == [foreign])
            rc, doc, kinds = source_case(census_url)
            check("census-normalized-source-url-accepted",
                  rc == 0 and kinds == []
                  and doc["results"][0]["source_url_hashes"] == [foreign])
            rc, doc, kinds = source_case(source_url + "\n" + foreign)
            check("bare-copy-of-curated-hash-remains-unresolved",
                  rc == 1 and kinds == [("unresolved-full-hash", foreign)]
                  and doc["results"][0]["source_url_hashes"] == [])
            unregistered_url = (
                "https://github.com/ggml-org/llama.cpp/blob/" + foreign
                + "/tools/server/other.cc")
            rc, doc, kinds = source_case(unregistered_url)
            check("unregistered-source-url-remains-unresolved",
                  rc == 1 and kinds == [("unresolved-full-hash", foreign)]
                  and doc["results"][0]["source_url_hashes"] == [])
            rc, doc, kinds = source_case(malformed_url)
            check("malformed-source-row-is-not-an-exemption",
                  rc == 1 and kinds == [("unresolved-full-hash", foreign)]
                  and doc["results"][0]["source_url_hashes"] == [])
            rc, doc, kinds = source_case(lead_url)
            check("leads-url-is-not-a-registry-exemption",
                  rc == 1 and kinds == [("unresolved-full-hash", foreign)]
                  and doc["results"][0]["source_url_hashes"] == [])
            rc, doc, kinds = source_case("not" + census_url)
            check("census-url-left-boundary",
                  rc == 1 and kinds == [("unresolved-full-hash", foreign)]
                  and doc["results"][0]["source_url_hashes"] == [])
            rc, doc, kinds = source_case(census_url + ".bak")
            check("census-url-right-boundary",
                  rc == 1 and kinds == [("unresolved-full-hash", foreign)]
                  and doc["results"][0]["source_url_hashes"] == [])
            rc, doc, kinds = source_case("http://" + census_url)
            check("scheme-stripped-url-not-matched-inside-http",
                  rc == 1 and kinds == [("unresolved-full-hash", foreign)]
                  and doc["results"][0]["source_url_hashes"] == [])
            rc, doc, kinds = source_case("https://outer.example/" + source_url)
            check("full-source-url-not-matched-inside-another-url",
                  rc == 1 and kinds == [("unresolved-full-hash", foreign)]
                  and doc["results"][0]["source_url_hashes"] == [])
            uncommitted_hash = "9" * 40
            uncommitted_url = (
                "https://worktree.example/project/blob/" + uncommitted_hash
                + "/source.cc")
            (lane / SOURCES).write_text(
                source_fixture.replace(
                    "## Leads\n",
                    "| S004 | worktree — " + uncommitted_url
                    + " | code | A | fixture scope | fixture anchor | fixture "
                    "teaches | mined | 2026-10-21 | on-release | — |\n"
                    "## Leads\n", 1),
                encoding="utf-8")
            rc, doc, kinds = source_case(uncommitted_url)
            check("worktree-source-row-does-not-authorize",
                  rc == 1 and kinds == [
                      ("unresolved-full-hash", uncommitted_hash)]
                  and doc["results"][0]["source_url_hashes"] == [])
            landed_without_checkpoint = "\n".join(
                f"- `{oid}`" for oid in (a, b, d, edge))
            landed_without_checkpoint += "\n- " + source_url
            rc, doc, kinds = source_case(
                "no source URL in body", landed_without_checkpoint)
            check("landed-source-url-keeps-both-hash-checks",
                  rc == 1 and kinds == sorted([
                      ("unresolved-full-hash", foreign),
                      ("landed-unresolved", foreign),
                      ("landed-omitted", c)])
                  and doc["results"][0]["source_url_hashes"] == [])
            source_draft.write_text(
                "## Work performed\nfixture\n## Landed changes " + source_url
                + "\n" + all_landed + "\n", encoding="utf-8")
            rc, doc = run(_ns(base, report=[f"1={source_draft}"]))
            kinds = sorted((item["kind"], item["token"])
                           for item in doc["results"][0]["defects"])
            check("landed-heading-source-url-keeps-full-hash-check",
                  rc == 1 and kinds == [("unresolved-full-hash", foreign)]
                  and doc["results"][0]["source_url_hashes"] == [])
            blobs = Path(tmp, "blobs")
            blobs.mkdir()
            names = []
            for i in range(1500):
                (blobs / str(i)).write_text(f"blob {i}\n", encoding="utf-8")
                names.append(str(blobs / str(i)))
            oids = git(lane, "hash-object", "-w", "--stdin-paths",
                       stdin="\n".join(names) + "\n").split()
            seen, short = {}, None
            for oid in oids:
                if oid[:4] in seen and seen[oid[:4]] != oid:
                    short = oid[:4]
                    break
                seen[oid[:4]] = oid
            check("ambiguous-prefix-is-ambiguous", short is not None
                  and lookup((lane,), [short]) == {short: "ambiguous"}
                  and lookup((lane,), [short], "^{commit}")
                  == {short: "ambiguous"}
                  and lookup((lane,), [oids[0]]) == {oids[0]: "found"}
                  and lookup((lane,), ["0" * 40]) == {"0" * 40: "missing"})
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
                x[:12] for x in (a, b, c, d, edge)) + "\n## End\n",
                encoding="utf-8")
            rc, doc = run(_ns(base, report=[f"1={draft}"]))
            check("draft-uses-fleet-cutoff", rc == 0
                  and doc["results"][0]["required"] == 5
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
            pristine = rep.read_text(encoding="utf-8")
            rep.write_text("edited, uncommitted\n", encoding="utf-8")
            rc, doc = run(base)
            check("committed-report-bytes-not-worktree", rc == 1 and len(
                doc["results"][0]["defects"]) == 3)
            rep.write_text(pristine, encoding="utf-8")
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
    except Exception as exc:  # an unanticipated error is never a verdict
        try:
            print(f"could-not-evaluate: internal: {type(exc).__name__}: "
                  f"{exc!r}"[:2000], file=sys.stderr)
        except Exception:
            pass
        return 2


if __name__ == "__main__":
    sys.exit(main())
