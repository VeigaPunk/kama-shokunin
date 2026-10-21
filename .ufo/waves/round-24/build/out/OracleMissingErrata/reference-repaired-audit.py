#!/usr/bin/env python3
"""Reference repaired auditor: proof that the pinned oracle is satisfiable.

This is NOT the candidate under review. It is a minimal repair of the r23
base that satisfies every arm of the pinned oracle, written only to prove
the oracle is consistent and achievable. It lives in scratch; the candidate
under review is whatever L1 ships.

Three changes against the base (tools/report-landing-audit.py at
0df800e896f6bce285a81e794ad4ae1d1e6c3a71):

1. check_history_repo() no longer refuses a repository for promisor
   METADATA alone. Promisor metadata is a declaration, not evidence of
   incompleteness: a promisor-marked repository whose required objects are
   all present locally must be audited normally. What is still refused is
   the promisor PACK (a repository that really is missing objects).

2. The errata ledger read distinguishes the two absence classes. The
   ledger path is first looked up in the tree:
     - the path is not in the tree at all -> the ledger was never committed:
       that is a repository without a ledger, which the base already
       refuses, and it stays refused;
     - the path IS in the tree but its blob is not available locally ->
       required evidence is unavailable: exit 2, never an empty ledger.

3. A ledger row whose correction commit cannot be resolved is unknown, not
   invalid, when the repository is promisor-backed (the object is promised
   by the origin and may simply not be local); in an ordinary repository
   the absence is evidence and the row is invalid, as before.
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

GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch",
                 "-c", "i18n.logOutputEncoding=UTF-8",
                 "-c", "log.follow=false", "-c", "log.showRoot=true",
                 "-c", "log.showSignature=false", "-c", "log.mailmap=false")
GIT_TIMEOUT = 20


class EvalError(Exception):
    """Could not evaluate: never converted into a verdict."""


def git_env(**extra):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", **extra)
    return env


def git(repo, *args, stdin=None, env=None, errors="strict"):
    try:
        proc = subprocess.run(["git", *GIT_ISOLATION, "-C", str(repo), *args],
                              input=None if stdin is None else stdin.encode(),
                              capture_output=True, env=env or git_env(),
                              timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired as exc:
        raise EvalError(f"git {' '.join(args)} in {repo}: timed out after "
                        f"{GIT_TIMEOUT}s") from exc
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
    """{token: 'found'|'ambiguous'|'missing'} across repos.

    Local-object resolution only. Promisor metadata alone never changes
    the result: a token that is not present locally is missing, whether or
    not the repository is promisor-backed, and the verdict is decided on
    the local evidence (oracle-amendment-1.json prospective_expected[0]).
    """
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
                raise EvalError(f"{repo}: citation {token} names a ref")
            status[token] = "found"
    return status


def landed_match(text):
    return re.search(r"^## Landed changes[^\n]*\n(.*?)(?=^## |\Z)", text,
                     re.S | re.M)


def checkable_abbrev(token):
    return len(token) == 40 or (re.search(r"[0-9]", token) is not None
                                and re.search(r"[a-f]", token) is not None)


def round_commits(lane_repo, branch, lane, rnd):
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
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise EvalError(f"unexpected git log record {sha[:80]!r}")
        if author == f"{lane}-shokunin" and pat.match(subject):
            if not re.fullmatch(r"[0-9]{1,18}", atime):
                raise EvalError(f"unexpected git log record {sha} "
                                f"author time {atime[:40]!r}")
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
    """The ledger is required evidence.

    Two absence classes, kept apart:
      * the path is not in the tree: this repository has no ledger. The
        base refused this and it stays refused.
      * the path IS in the tree but its blob is not available locally:
        required evidence is unavailable -> exit 2. Never an empty ledger.
    """
    if args.no_errata:
        return []
    if args.errata:
        try:
            return parse_errata(Path(args.errata).read_text(encoding="utf-8"),
                                args.errata)
        except (OSError, UnicodeDecodeError) as exc:
            raise EvalError(f"cannot read errata {args.errata}: {exc}") from exc
    entry = git(lane_repo, "ls-tree", tip, "--", ERRATA).rstrip("\n")
    if not entry:
        raise EvalError(f"{tip}:{ERRATA}: no ledger in this repository")
    metadata, sep, path = entry.partition("\t")
    fields = metadata.split()
    if (not sep or "\n" in entry or path != ERRATA or len(fields) != 3
            or fields[1] != "blob" or fields[0] not in ("100644", "100755")):
        raise EvalError(f"{tip}:{ERRATA}: not a regular blob")
    try:
        text = git(lane_repo, "cat-file", "blob", fields[2])
    except EvalError as exc:
        raise EvalError(f"{tip}:{ERRATA}: ledger committed but its blob is "
                        f"not available locally: {exc}") from exc
    return parse_errata(text, f"{args.branch}:{ERRATA}")


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
    hexed = {e["line"]: e["correction"].lower() for e in errata
             if e["kind"] in RESOLVABLE
             and re.fullmatch(r"[0-9a-fA-F]{7,40}", e["correction"])}
    status = lookup(repos, list(hexed.values()), "^{commit}")
    invalid = [e for e in errata if e["kind"] in RESOLVABLE and (
        status.get(hexed.get(e["line"])) != "found"
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
            listed = git(fleet_repo, "ls-tree", "-r", "--name-only", "HEAD",
                         "--", ".ufo/reports", errors="surrogateescape")
            pat = re.compile(rf"\.ufo/reports/round-([0-9]+)/{re.escape(lane)}\.md")
            present = [int(m.group(1)) for m in map(pat.fullmatch,
                                                    listed.split("\n")) if m]
            rounds.update(n for n in present if n >= lo)
    return rounds


def check_history_repo(repo):
    """Refuse a repository whose visible history is not its object history.

    Promisor METADATA and a promisor PACK are declarations, not evidence of
    incompleteness: they say an object may live at the origin, not that any
    object the audit reads is missing here. Neither is a refusal by itself.
    What is refused is a genuine defect of the visible history: a shallow
    boundary, a graft file, or a non-sha1 object format.

    Whether the objects the audit actually reads are present is decided
    where they are read: the ledger read refuses an unavailable committed
    blob, and an unavailable required object is a content-derived
    could-not-evaluate.
    """
    fmt = git(repo, "rev-parse", "--show-object-format").strip()
    if fmt != "sha1":
        raise EvalError(f"{repo}: object format {fmt!r}, not sha1")
    if git(repo, "rev-parse", "--show-prefix").strip():
        raise EvalError(f"{repo}: not a repository top level")
    if git(repo, "rev-parse", "--is-shallow-repository").strip() != "false":
        raise EvalError(f"{repo}: shallow repository")
    path = Path(repo, git(repo, "rev-parse", "--git-path",
                          "info/grafts").strip())
    if grafts_effective(path):
        raise EvalError(f"{repo}: {path} rewrites history")


def grafts_effective(path):
    try:
        mode = os.lstat(path).st_mode
    except FileNotFoundError:
        return False
    if not stat.S_ISREG(mode):
        return True
    return any(line.strip() and not line.startswith(b"#")
               for line in Path(path).read_bytes().splitlines())


def promisor_metadata(repo):
    """True when the repository is promisor-backed. A declaration only: it
    says an object may live at the origin, not that any object is missing
    here. A promisor pack counts too: the repository really does hold
    objects it does not have."""
    listing = git(repo, "config", "--null", "--list",
                  errors="surrogateescape")
    for entry in filter(None, listing.split("\0")):
        key, _, value = entry.partition("\n")
        if key == "extensions.partialclone":
            return True
        if re.fullmatch(r"remote\..+\.promisor", key) and git_bool(value):
            return True
        if re.fullmatch(r"remote\..+\.partialclonefilter", key):
            return True
    pack = Path(repo, git(repo, "rev-parse", "--git-path",
                          "objects/pack").strip())
    if pack.is_dir() and any(p.suffix == ".promisor"
                             and p.with_suffix(".pack").exists()
                             for p in pack.iterdir()):
        return True
    return False


def git_bool(value):
    v = value.strip().lower()
    return v in ("", "true", "yes", "on") or (
        re.fullmatch(r"-?[0-9]+", v) is not None and int(v) != 0)


def resolve_branch(lane_repo, branch):
    head = f"refs/heads/{branch}"
    if git(lane_repo, "for-each-ref", "--format=%(refname)", head).strip():
        return git(lane_repo, "rev-parse", "--verify",
                   f"{head}^{{commit}}").strip()
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


def main(argv=None):
    ap = argparse.ArgumentParser(description="reference repaired auditor")
    ap.add_argument("--lane-repo", required=True)
    ap.add_argument("--fleet-repo", required=True)
    ap.add_argument("--branch", default="master")
    ap.add_argument("--lane", default=LANE)
    ap.add_argument("--rounds", default="10-")
    ap.add_argument("--report", action="append")
    ap.add_argument("--errata")
    ap.add_argument("--no-errata", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        status, doc = run(args)
        print(json.dumps(doc, indent=1, sort_keys=True) if args.json
              else render(doc), flush=True)
        return status
    except EvalError as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"could-not-evaluate: internal: {type(exc).__name__}: "
              f"{exc!r}"[:2000], file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
