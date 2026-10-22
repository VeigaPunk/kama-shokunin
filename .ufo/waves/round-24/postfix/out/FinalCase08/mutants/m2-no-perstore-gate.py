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
means refs/heads/<name>; shallow, grafted, non-sha1 and non-top-level
repositories and ref-named citations are refused. Objects borrowed through
objects/info/alternates or a .git gitfile still resolve as local, and other
repository-local channels are not claimed. Audit trusted repositories only;
git >= 2.45 is required.

Partial clones (round 24): a citation that neither audited repository
holds is still a proved absence, whatever the repository declares: promisor
metadata alone never changes a verdict, and the promisor remote is never
contacted (the --no-lazy-fetch isolation covers every git call). The one
case that is not a verdict is a citation whose content cannot be read: for
a token that no audited repository resolves, the objects the store
references but cannot serve are listed with `rev-list --objects
--missing=print` over the store's present objects (the commit graph is
switched off for that walk), and a token that names one of them, or that a
missing tree or commit could hide, is unknown, not absent, so the audit
refuses (exit 2, `unknown: unavailable required object`, naming the object).
Missing objects the citation does not name are unrelated and block nothing;
the diagnosis is never a precondition on the audit.
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
# how a local answer ranks: a resolved object wins, an ambiguous prefix is a
# proved fact, an object whose content cannot be read is unknown, a known
# object of the wrong type is a proved mismatch, and an object nobody holds
# is the weakest answer.
RANK = {"absent": 0, "wrongtype": 1, "unknown": 2, "ambiguous": 3, "found": 4}


class EvalError(Exception):
    """Could not evaluate: never converted into a verdict."""


class RepoStore:
    """One audited repository and the commit root the audit reads.

    The root is the audit's context (the pinned lane branch tip, the fleet
    tip). The store also remembers the objects the repository references
    but cannot serve -- over all its present objects, reachable or not, not
    only over the root: a citation to one of them cannot be proved absent,
    so the audit refuses instead of reporting a verdict about it. The set
    is computed once per store, in this run only."""

    __slots__ = ("path", "root", "_missing")

    def __init__(self, path, root):
        self.path = path
        self.root = root
        self._missing = None

    def missing(self):
        """(missing, opaque): the known unavailable object ids that
        present local objects reference, and the subset of them that hides
        names behind the audited root (computed at most once per store)."""
        if self._missing is None:
            self._missing = missing_reachable(self.path, self.root)
        return self._missing


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

# Seconds per git call; real audits take milliseconds per call.
GIT_TIMEOUT = 20


def git(repo, *args, stdin=None, env=None, errors="strict"):
    """stdout as UTF-8 text with universal newlines (as text mode did).
    Strict by default: undecodable output is an EvalError, never a
    traceback verdict. Callers that only match ASCII fields and never emit
    the text (lane log records, report path listing) pass surrogateescape."""
    try:
        proc = subprocess.run(["git", *GIT_ISOLATION, "-C", str(repo), *args],
                              input=None if stdin is None else stdin.encode(),
                              capture_output=True, env=env or git_env(),
                              timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired as exc:
        # e.g. a FIFO at .git/config, an include target, .git/shallow or a
        # ref file blocks git's read: a hang is never a verdict
        error = EvalError(f"git {' '.join(args)} in {repo}: timed out after "
                          f"{GIT_TIMEOUT}s")
        # a timeout (or a broken git) is not a missing object: a follow-up
        # diagnostic call would only risk a second timeout
        error.fatal = True
        raise error from exc
    except OSError as exc:
        error = EvalError(f"cannot run git: {exc}")
        error.fatal = True
        raise error from exc
    if proc.returncode != 0:
        raise EvalError(f"git {' '.join(args)} in {repo}: rc={proc.returncode} "
                        f"{proc.stderr.decode(errors='replace').strip()}")
    try:
        out = proc.stdout.decode("utf-8", errors)
    except UnicodeDecodeError as exc:
        raise EvalError(f"git {' '.join(args)} in {repo}: output is not "
                        f"UTF-8: {exc}") from exc
    return out.replace("\r\n", "\n").replace("\r", "\n")


def bare_objects(store, tokens):
    """{token: (state, object id)} for one store: what the bare name
    resolves to there. The id is the canonical object the name stands for,
    so the same object in two stores is recognised as the same object."""
    out = git(store.path, "cat-file", "--batch-check",
              stdin="".join(f"{t}\n" for t in tokens))
    lines = out.split("\n")[:len(tokens)]
    if len(lines) != len(tokens):
        raise EvalError(f"cat-file --batch-check in {store.path}: "
                        f"short output")
    result = {}
    for token, line in zip(tokens, lines):
        if line.endswith(" missing"):
            result[token] = ("absent", None)
        elif line.endswith(" ambiguous"):
            result[token] = ("ambiguous", None)
        elif line.endswith(" excluded") or line.endswith(" dangling"):
            result[token] = ("excluded", None)
        else:
            parts = line.split(" ")
            if len(parts) != 3 or not re.fullmatch(r"[0-9a-f]{40}", parts[0]):
                raise EvalError(f"cat-file in {store.path}: unexpected {line!r}")
            if not parts[0].startswith(token):
                # git resolved a same-named ref before the object prefix
                raise EvalError(f"{store.path}: citation {token} names a ref")
            result[token] = ("found", parts[0])
    return result


def lookup(stores, tokens, peel=""):
    """{token: 'found'|'ambiguous'|'unknown'|'wrongtype'|'absent'} across
    stores, via `cat-file --batch-check` per store; a git failure is
    EvalError. With a peel, git answers `missing' for an ambiguous short
    name, so the bare name is asked first to keep ambiguity visible.

    'wrongtype' names an object that exists locally but is not a commit:
    a proved local mismatch. 'unknown' names an object that exists but
    whose peeled target the repository cannot serve (a tag whose target
    is unavailable): its content cannot be read, so it is no verdict.
    With no peel, any object type is a found token."""
    tokens = sorted(set(tokens))
    status = {t: "absent" for t in tokens}
    if not tokens:
        return status

    def offer(token, state):
        if RANK[state] > RANK[status[token]]:
            status[token] = state

    # token -> {canonical object id: {what the stores proved about it}}
    proved = {}
    for store in stores:
        # what THIS store holds under the bare name: the presence must be
        # the store's own, never the merge of every store, or an object
        # that lives in one repository would make it look present (and
        # unreadable) in the other
        here = bare_objects(store, tokens) if peel else None
        if here is not None:
            for token, (state, _) in here.items():
                if state == "ambiguous":
                    # git answers 'missing' for an ambiguous short name
                    # under a peel, so the bare answer keeps the
                    # ambiguity visible
                    offer(token, "ambiguous")
        out = git(store.path, "cat-file", "--batch-check",
                  stdin="".join(f"{t}{peel}\n" for t in tokens))
        lines = out.split("\n")[:len(tokens)]
        if len(lines) != len(tokens):
            raise EvalError(f"cat-file --batch-check in {store.path}: "
                            f"short output")
        unresolved = []
        for token, line in zip(tokens, lines):
            if line.endswith(" missing"):
                if here is not None:
                    unresolved.append(token)
                continue
            if line.endswith(" ambiguous"):
                offer(token, "ambiguous")
                continue
            if line.endswith(" excluded") or line.endswith(" dangling"):
                continue
            parts = line.split(" ")
            if len(parts) != 3 or not re.fullmatch(r"[0-9a-f]{40}", parts[0]):
                raise EvalError(f"cat-file in {store.path}: unexpected {line!r}")
            if not peel and not parts[0].startswith(token):
                # git resolved a same-named ref before the object prefix
                raise EvalError(f"{store.path}: citation {token} names a ref")
            offer(token, "found")
        if unresolved:
            # the object is here; ask whether what it dereferences to is
            # here too: a tag whose target is unavailable is unknown, a
            # tag or blob that dereferences to a known object is a proved
            # mismatch
            out = git(store.path, "cat-file", "--batch-check",
                      stdin="".join(f"{t}^{{}}\n" for t in unresolved))
            lines = out.split("\n")[:len(unresolved)]
            if len(lines) != len(unresolved):
                raise EvalError(f"cat-file --batch-check in {store.path}: "
                                f"short output")
            for token, line in zip(unresolved, lines):
                state = "unknown" if line.endswith(" missing") else "wrongtype"
                oid = here[token][1]
                proved.setdefault(token, {}).setdefault(oid, set()).add(state)
    # Reconcile per canonical object: a store that proves the object is a
    # known non-commit has proved the mismatch, so another store's
    # inability to serve that object does not make the citation unknown.
    # Different objects behind one abbreviated name are not reconciled:
    # there the uncertainty stands.
    for token, per_object in proved.items():
        conclusive = False
        unsure = False
        for states in per_object.values():
            if "wrongtype" in states:
                conclusive = True
            else:
                unsure = True
        if conclusive and not unsure:
            offer(token, "wrongtype")
        elif unsure:
            offer(token, "unknown")
    return status


def landed_match(text):
    return re.search(r"^## Landed changes[^\n]*\n(.*?)(?=^## |\Z)", text,
                     re.S | re.M)


def checkable_abbrev(token):
    """A Landed token is checked as a citation only if it cannot be an
    ordinary word or number: 40 hex, or both a digit and a letter."""
    return len(token) == 40 or (re.search(r"[0-9]", token) is not None
                                and re.search(r"[a-f]", token) is not None)


def root_tree(repo, root, cause=None):
    """The tree id the root commit names, or None.

    The id is in the commit header, so it is readable even when the tree
    object itself is absent: a refusal about a missing tree can then name
    that tree. When the commit cannot be read either, None is returned and
    the caller keeps its own reason. A fatal cause (a timeout or a broken
    git) skips the call: another 20 s would only be spent again."""
    if cause is not None and getattr(cause, "fatal", False):
        return None
    try:
        tree = git(repo, "log", "-1", "--format=%T", root).strip()
    except EvalError:
        return None
    return tree if re.fullmatch(r"[0-9a-f]{40}", tree) else None


def required_read(what, exc):
    """A read of evidence the audit needs failed: the object is not
    available, so the audit refuses with a content-derived reason that
    names what was wanted."""
    return EvalError(f"unavailable required object: {what}: {exc}")


def round_commits(lane_repo, branch, lane, rnd):
    """NUL-delimited records: git truncates names and subjects at NUL, so
    no commit text can inject or shift a field (\\x1f/\\x1e can)."""
    try:
        out = git(lane_repo, "log", "-z", "--format=%H%x00%an%x00%at%x00%s",
                  branch, errors="surrogateescape")
    except EvalError as exc:
        raise required_read(f"the {lane} history of {branch}", exc) from exc
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
            # only required candidates need a usable time; an unrelated
            # commit with a malformed date must not block the audit
            if not re.fullmatch(r"[0-9]{1,18}", atime):
                raise EvalError(f"unexpected git log record {sha} "
                                f"author time {atime[:40]!r}")
            rows.append({"sha": sha, "atime": int(atime), "subject": subject})
    return rows


def report_cutoff(fleet_repo, rel):
    try:
        out = git(fleet_repo, "log", "--diff-filter=A", "--format=%at", "--",
                  rel).split()
    except EvalError as exc:
        tree = root_tree(fleet_repo, "HEAD", exc)
        what = (f"the first add of {rel} in {fleet_repo} (tip tree {tree})"
                if tree else f"the first add of {rel} in {fleet_repo}")
        raise required_read(what, exc) from exc
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
    try:
        entry = git(lane_repo, "ls-tree", branch, "--", SOURCES).rstrip("\n")
    except EvalError as exc:
        tree = root_tree(lane_repo, branch, exc)
        what = (f"{branch}:{SOURCES} (tip tree {tree}) in {lane_repo}" if tree
                else f"{branch}:{SOURCES} in {lane_repo}")
        raise required_read(what, exc) from exc
    if not entry:
        return None
    metadata, sep, path = entry.partition("\t")
    fields = metadata.split()
    if (not sep or "\n" in entry or path != SOURCES or len(fields) != 3
            or fields[1] != "blob" or fields[0] not in ("100644", "100755")):
        raise EvalError(f"{branch}:{SOURCES}: not a regular blob")
    try:
        text = git(lane_repo, "cat-file", "blob", fields[2])
    except EvalError as exc:
        raise required_read(f"{branch}:{SOURCES} ({fields[2]}) in {lane_repo}",
                            exc) from exc
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


def refuse_unknown(rnd, status, stores):
    """Refuse a citation that names content which cannot be read.

    A resolved, ambiguous or wrong-type token is a finding; a token that
    nobody holds is a proved absence unless the history references it (or
    hides it behind a missing tree or commit), in which case its absence
    is not proved and the audit must refuse instead of reporting a
    verdict about it. Every refusal names the object that is not
    available: the cited token itself, the object the store references
    under that name, or the missing tree or commit that could hide it."""
    for token, state in status.items():
        if state in ("found", "ambiguous", "wrongtype"):
            continue
        if state == "unknown":
            raise EvalError(
                f"round {rnd}: unknown: unavailable required object: {token} "
                f"is present but its content cannot be served")
        store = unknown_citation(stores, token)
        if store is not None:
            raise EvalError(
                f"round {rnd}: unknown: unavailable required object: {token} "
                f"is referenced by local objects in {store.path} but the "
                f"repository cannot serve it")
        hole, hole_oid = opaque_hole(stores)
        if hole is not None:
            raise EvalError(
                f"round {rnd}: unknown: unavailable required object: {token} "
                f"could be hidden behind the missing tree or commit "
                f"{hole_oid} in {hole.path}")


def audit_round(lane_repo, fleet_repo, branch, lane, rnd, path, source_urls,
                stores):
    rel = f".ufo/reports/round-{rnd}/{lane}.md"
    report = Path(path) if path else Path(fleet_repo) / rel
    if path:
        text = read_report(report)
    else:
        # committed fleet bytes, not a possibly edited working-tree copy
        try:
            text = git(fleet_repo, "show", f"HEAD:{rel}")
        except EvalError as exc:
            tree = root_tree(fleet_repo, "HEAD", exc)
            what = (f"{rel} at fleet HEAD (tip tree {tree}, {fleet_repo})"
                    if tree else f"{rel} at fleet HEAD ({fleet_repo})")
            raise required_read(what, exc) from exc
    cutoff = report_cutoff(fleet_repo, rel)
    committed = cutoff is not None
    if cutoff is None:
        if path is None:
            raise EvalError(f"round {rnd}: {rel} has no fleet commit")
        cutoff = int(time.time())
    defects = []
    landed = landed_match(text)
    full_tokens, classified_hashes = classify_full_hashes(
        text, source_urls, landed)
    full = lookup(stores, full_tokens)
    refuse_unknown(rnd, full, stores)
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
    status = lookup(stores, [t for t in cited if checkable_abbrev(t)],
                    "^{commit}")
    refuse_unknown(rnd, status, stores)
    for token, state in status.items():
        if state == "found":
            continue
        if state == "ambiguous":
            defects.append({"kind": "landed-ambiguous", "token": token})
            continue
        # 'absent' (proved absent) and 'wrongtype' (locally known, not a
        # commit) are both failed findings
        defects.append({"kind": "landed-unresolved", "token": token})
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
    try:
        text = git(lane_repo, "show", f"{tip}:{ERRATA}")
    except EvalError as exc:
        # the committed ledger is evidence the audit needs
        raise required_read(f"{tip}:{ERRATA} in {lane_repo}", exc) from exc
    return parse_errata(text, f"{args.branch}:{ERRATA}")


def apply_errata(results, errata, stores):
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
    # only hex corrections of the SELECTED rounds are looked up (case-
    # folded, as git does): a revision expression such as HEAD or :/text is
    # never a correction, and a row of a round that was not audited is not
    # this audit's business -- reading its object would be a guess
    hexed = {e["line"]: e["correction"].lower() for e in errata
             if e["kind"] in RESOLVABLE
             and e["round"] in selected
             and re.fullmatch(r"[0-9a-fA-F]{7,40}", e["correction"])}
    status = lookup(stores, list(hexed.values()), "^{commit}")
    for e in errata:
        token = hexed.get(e["line"])
        if token is None or e["round"] not in selected:
            continue
        state = status.get(token)
        if state == "unknown":
            raise EvalError(
                f"errata line {e['line']}: unknown: unavailable required "
                f"object: {token} is present but its content cannot be served")
        if state == "absent":
            store = unknown_citation(stores, token)
            if store is not None:
                raise EvalError(
                    f"errata line {e['line']}: unknown: unavailable required "
                    f"object: {token} is referenced by local objects in "
                    f"{store.path} but the repository cannot serve it")
            hole, hole_oid = opaque_hole(stores)
            if hole is not None:
                raise EvalError(
                    f"errata line {e['line']}: unknown: unavailable required "
                    f"object: {token} could be hidden behind the missing tree "
                    f"or commit {hole_oid} in {hole.path}")
    # a row of a round that was not audited cannot make this audit fail
    invalid = [e for e in errata if e["round"] in selected
               and e["kind"] in RESOLVABLE and (
                   status.get(hexed.get(e["line"])) != "found"
                   or (e["kind"] == "landed-omitted"
                       and e["correction"] != e["token"]))]
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
            try:
                listed = git(fleet_repo, "ls-tree", "-r", "--name-only",
                             "HEAD", "--", ".ufo/reports",
                             errors="surrogateescape")
            except EvalError as exc:
                # the listing is evidence the audit needs
                tree = root_tree(fleet_repo, "HEAD", exc)
                what = (f".ufo/reports at fleet HEAD (tip tree {tree}, "
                        f"{fleet_repo})" if tree else
                        f".ufo/reports at fleet HEAD ({fleet_repo})")
                raise required_read(what, exc) from exc
            pat = re.compile(rf"\.ufo/reports/round-([0-9]+)/{re.escape(lane)}\.md")
            present = [int(m.group(1)) for m in map(pat.fullmatch,
                                                    listed.split("\n")) if m]
            rounds.update(n for n in present if n >= lo)
    return rounds


def check_history_repo(repo):
    """Refuse a repository whose visible history is not its object history
    (shallow boundary, info/grafts) or whose object names the 40-hex
    scanners cannot read (non-sha1 object format). A partial clone is not
    a refusal: what it declares changes no verdict, only the availability
    of the objects it can serve decides."""
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


def present_roots(repo):
    """Every present object that can root a traversal: the commits, trees
    and tags the local object database holds, reachable or not. A dangling
    commit, tree or tag can reference an object the repository cannot
    serve, and no ref reaches it."""
    out = git(repo, "cat-file", "--batch-all-objects",
              "--batch-check=%(objectname) %(objecttype)")
    roots = []
    for line in out.split("\n"):
        name, _, kind = line.partition(" ")
        if kind in ("commit", "tree", "tag") and \
                re.fullmatch(r"[0-9a-f]{40}", name):
            roots.append(name)
    return roots


def missing_reachable(repo, root):
    """(missing, opaque): the known unavailable object ids that present
    local objects reference, and the subset of them that hides names
    behind the audited root.

    Two walks, two root sets. The first walks from every present object
    of the store, so a dangling commit, tree or tag that references a
    missing object is seen too, and a citation of such an object is still
    unknown. It names the unavailable ids it ENCOUNTERS: the descendants
    hidden behind a missing tree cannot be enumerated, which is exactly
    why the second walk exists. That one identifies the opaque
    boundaries of the pinned root - the missing trees and commits behind
    the audit's own root, whose names are hidden - and its roots are the
    pinned root ONLY, so unreachable garbage in the store is not a
    dependency of the audit. `rev-list --missing=print` names the missing
    ids with a `?` prefix instead of failing; the --no-lazy-fetch
    isolation keeps a promisor remote untouched. The commit graph is
    switched off for the walks so that it cannot hide an unavailable
    object."""
    roots = present_roots(repo)
    if root not in roots:
        roots.append(root)

    def walk(extra, walk_roots):
        out = git(repo, "-c", "core.commitGraph=false", "rev-list",
                  "--objects", "--missing=print", "--no-object-names", *extra,
                  "--stdin", stdin="".join(f"{r}\n" for r in walk_roots))
        return {line[1:] for line in out.split("\n") if line.startswith("?")}

    missing = walk((), roots)
    opaque = walk(("--filter=blob:none",), [root])
    return missing, opaque


def build_store(repo, root):
    """The audited repository and the commit root the audit reads: the
    pinned lane branch tip or the fleet tip. The root is the audit's
    context, not a completeness gate; the store-wide diagnosis of what
    the repository cannot serve runs only for a citation that no audited
    repository resolves."""
    return RepoStore(repo, root)


def unknown_citation(stores, token):
    """The store whose present local objects reference the cited token but
    cannot serve it, or None.

    Such a token is not a proved absence: the repository references it and
    cannot hand it over, so the audit must refuse rather than report a
    verdict about it. A missing object the citation does not name is
    unrelated and does not block anything."""
    for store in stores:
        missing, _ = store.missing()
        for oid in missing:
            if oid == token or oid.startswith(token):
                return store
    return None


def opaque_hole(stores):
    """The store with a missing tree or commit and one such object id, or
    (None, None).

    Behind such a hole the names of the objects below it are not known, so
    an unresolved token could be hiding there. The id is the lowest one the
    store reports, so a refusal names the same unavailable object every
    time."""
    for store in stores:
        _, opaque = store.missing()
        if opaque:
            return store, sorted(opaque)[0]
    return None, None


def grafts_effective(path):
    """True unless the grafts file is absent or holds only blank and `#`
    comment lines (which git skips); anything not a regular file, or any
    other line, may rewrite history and is refused unread."""
    try:
        mode = os.lstat(path).st_mode
    except FileNotFoundError:
        return False
    if not stat.S_ISREG(mode):
        return True
    return any(line.strip() and not line.startswith(b"#")
               for line in Path(path).read_bytes().splitlines())


def resolve_branch(lane_repo, branch):
    """Pin the lane tip once. A plain name that exists as refs/heads/<name>
    must peel to a commit there (a same-named tag never substitutes for a
    broken branch); other revisions resolve as given."""
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
    fleet_tip = git(fleet_repo, "rev-parse", "--verify",
                    "HEAD^{commit}").strip()
    # the roots the audit reads: the pinned lane tip and the fleet tip
    stores = (build_store(lane_repo, tip),
              build_store(fleet_repo, fleet_tip))
    source_urls = load_source_urls(lane_repo, tip)
    results = [audit_round(lane_repo, fleet_repo, tip, args.lane, r,
                           overrides.get(r), source_urls, stores)
               for r in rounds]
    errata = load_errata(args, lane_repo, tip)
    unmatched, invalid = apply_errata(results, errata, stores)
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
            store = RepoStore(lane, "HEAD")
            check("ambiguous-prefix-is-ambiguous", short is not None
                  and lookup((store,), [short]) == {short: "ambiguous"}
                  and lookup((store,), [short], "^{commit}")
                  == {short: "ambiguous"}
                  and lookup((store,), [oids[0]]) == {oids[0]: "found"}
                  and lookup((store,), ["0" * 40]) == {"0" * 40: "absent"})
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
            rc, doc = with_rows(*good, (2, "unresolved-full-hash", "0" * 40,
                                        "0" * 40, "x"))
            check("unselected-invalid-correction-is-ignored",
                  rc == 0 and doc["summary"]["errata_invalid"] == 0
                  and doc["summary"]["errata_unmatched"] == 0)
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

            # round 24: metadata alone changes nothing, availability does
            blob_draft = Path(tmp, "blob-draft.md")
            blob_draft.write_text(
                "## Landed changes\n- `" + blob + "` blob\n", encoding="utf-8")
            rc, doc = run(_ns(base, report=[f"1={blob_draft}"]))
            kinds = sorted((x["kind"], x["token"])
                           for x in doc["results"][0]["defects"])
            check("wrongtype-citation-is-a-failed-finding",
                  rc == 1 and ("landed-unresolved", blob) in kinds)
            # a blob that lives in one audited repository only: its absence
            # from the other is not an unreadable object
            fleet_blob = git(fleet, "hash-object", "-w", "--stdin",
                             stdin="fleet only blob\n").strip()
            fleet_draft = Path(tmp, "fleet-blob-draft.md")
            fleet_draft.write_text(
                "## Landed changes\n- `" + fleet_blob + "` fleet blob\n",
                encoding="utf-8")
            rc, doc = run(_ns(base, report=[f"1={fleet_draft}"]))
            kinds = sorted((x["kind"], x["token"])
                           for x in doc["results"][0]["defects"])
            check("fleet-only-blob-citation-is-a-failed-finding",
                  rc == 1 and ("landed-unresolved", fleet_blob) in kinds)
            lane_blob = git(lane, "hash-object", "-w", "--stdin",
                            stdin="lane only blob\n").strip()
            lane_draft = Path(tmp, "lane-blob-draft.md")
            lane_draft.write_text(
                "## Landed changes\n- `" + lane_blob + "` lane blob\n",
                encoding="utf-8")
            rc, doc = run(_ns(base, report=[f"1={lane_draft}"]))
            kinds = sorted((x["kind"], x["token"])
                           for x in doc["results"][0]["defects"])
            check("lane-only-blob-citation-is-a-failed-finding",
                  rc == 1 and ("landed-unresolved", lane_blob) in kinds)
            fleet_tree = git(fleet, "mktree",
                             stdin=f"100644 blob {fleet_blob}\tf\n").strip()
            tree_draft = Path(tmp, "fleet-tree-draft.md")
            tree_draft.write_text(
                "## Landed changes\n- `" + fleet_tree + "` fleet tree\n",
                encoding="utf-8")
            rc, doc = run(_ns(base, report=[f"1={tree_draft}"]))
            kinds = sorted((x["kind"], x["token"])
                           for x in doc["results"][0]["defects"])
            check("fleet-only-tree-citation-is-a-failed-finding",
                  rc == 1 and ("landed-unresolved", fleet_tree) in kinds)
            tag_target = git(fleet, "hash-object", "-w", "--stdin",
                             stdin="fleet tag target\n").strip()
            fleet_tag = git(fleet, "mktag",
                            stdin=f"object {tag_target}\ntype blob\ntag t\n"
                                  f"tagger k <a@x> 1000 +0000\n\ntag\n",
                            env=git_env(GIT_AUTHOR_NAME="k",
                                        GIT_COMMITTER_NAME="k",
                                        GIT_AUTHOR_EMAIL="a@x",
                                        GIT_COMMITTER_EMAIL="a@x")).strip()
            tag_only_draft = Path(tmp, "fleet-tag-draft.md")
            tag_only_draft.write_text(
                "## Landed changes\n- `" + fleet_tag + "` fleet tag\n",
                encoding="utf-8")
            rc, doc = run(_ns(base, report=[f"1={tag_only_draft}"]))
            kinds = sorted((x["kind"], x["token"])
                           for x in doc["results"][0]["defects"])
            check("fleet-only-tag-citation-is-a-failed-finding",
                  rc == 1 and ("landed-unresolved", fleet_tag) in kinds)
            errata_blob = Path(tmp, "errata-fleet-blob.tsv")
            errata_blob.write_text(
                "1\tlanded-unresolved\t" + fleet_blob + "\t" + fleet_blob
                + "\tevidence\n", encoding="utf-8")
            rc, doc = run(_ns(base, report=[f"1={fleet_draft}"],
                               no_errata=False, errata=str(errata_blob)))
            check("errata-correction-naming-the-cited-fleet-only-blob-is-invalid",
                  rc == 1 and doc["summary"]["errata_invalid"] == 1
                  and doc["summary"]["errata_unmatched"] == 0)
            # the errata correction consumer, ISOLATED: the report cites a
            # known lane blob (an ordinary finding on its own) and the
            # ledger corrects that token with a fleet-only blob
            lane_blob_a = git(lane, "hash-object", "-w", "--stdin",
                              stdin="known lane blob\n").strip()
            fleet_blob_b = git(fleet, "hash-object", "-w", "--stdin",
                               stdin="other fleet blob\n").strip()
            isolated_draft = Path(tmp, "isolated-errata-draft.md")
            isolated_draft.write_text(
                "## Landed changes\n- `" + lane_blob_a + "` lane blob\n",
                encoding="utf-8")
            rc, doc = run(_ns(base, report=[f"1={isolated_draft}"]))
            kinds = sorted((x["kind"], x["token"])
                           for x in doc["results"][0]["defects"])
            check("known-lane-blob-citation-is-an-ordinary-finding",
                  rc == 1 and ("landed-unresolved", lane_blob_a) in kinds)
            isolated_errata = Path(tmp, "isolated-errata.tsv")
            isolated_errata.write_text(
                "1\tlanded-unresolved\t" + lane_blob_a + "\t" + fleet_blob_b
                + "\tevidence\n", encoding="utf-8")
            rc, doc = run(_ns(base, report=[f"1={isolated_draft}"],
                              no_errata=False, errata=str(isolated_errata)))
            check("errata-correction-naming-a-fleet-only-blob-is-invalid",
                  rc == 1 and doc["summary"]["errata_invalid"] == 1
                  and doc["summary"]["errata_unmatched"] == 0)
            git(lane, "repack", "-ad")
            pack_dir = Path(lane, git(lane, "rev-parse", "--git-path",
                                      "objects/pack").strip())
            marker = sorted(pack_dir.glob("*.pack"))[0].with_suffix(".promisor")
            marker.write_text("", encoding="utf-8")
            trap = Path(tmp, "lazy-fetch-ran")
            for key, value in (("extensions.partialClone", "origin"),
                               ("remote.origin.url",
                                "ssh://example.invalid/x.git"),
                               ("remote.origin.promisor", "true"),
                               ("remote.origin.partialclonefilter",
                                "blob:none"),
                               ("core.sshCommand",
                                f"touch {trap}; false")):
                git(lane, "config", key, value)
            rc, doc = run(base)
            kinds = sorted((x["kind"], x["token"])
                           for x in doc["results"][0]["defects"])
            check("promisor-metadata-keeps-the-local-verdict",
                  rc == 1 and kinds == sorted([
                      ("unresolved-full-hash", mash), ("landed-omitted", c),
                      ("landed-unresolved", "deadbee1")]))
            check("promisor-remote-is-never-contacted", not trap.exists())
            hole_commit = _commit(lane, "round-1: hole", "kama-shokunin",
                                  1300, "hole.txt")
            mid = _commit(lane, "round-1: mid", "kama-shokunin", 1400,
                          "mid.txt")
            _commit(lane, "round-1: top", "kama-shokunin", 1500, "top.txt")
            hole = git(lane, "rev-parse", f"{hole_commit}:hole.txt").strip()
            Path(lane, git(lane, "rev-parse", "--git-path",
                           "objects").strip(),
                 hole[:2], hole[2:]).unlink()
            rc, doc = run(base)
            kinds = sorted((x["kind"], x["token"])
                           for x in doc["results"][0]["defects"])
            check("unrelated-missing-object-does-not-block",
                  rc == 1 and kinds == sorted([
                      ("unresolved-full-hash", mash), ("landed-omitted", c),
                      ("landed-unresolved", "deadbee1")]))
            hole_draft = Path(tmp, "hole-draft.md")
            hole_draft.write_text(
                "## Work performed\n" + hole + "\n"
                "## Landed changes\n- `" + a[:9] + "` work\n", encoding="utf-8")
            check("citation-of-a-missing-object-is-unknown",
                  is_error(lambda: run(_ns(base, report=[f"1={hole_draft}"]))))
            errata_hole = Path(tmp, "errata-hole.tsv")
            errata_hole.write_text(
                "1\tunresolved-full-hash\t" + hole + "\t" + a + "\tevidence\n",
                encoding="utf-8")
            check("errata-cannot-rescue-unavailable-content",
                  is_error(lambda: run(_ns(base, report=[f"1={hole_draft}"],
                                          no_errata=False,
                                          errata=str(errata_hole)))))
            errata_fake = Path(tmp, "errata-fake.tsv")
            errata_fake.write_text(
                "1\tunresolved-full-hash\t" + mash + "\t" + a + "\tevidence\n",
                encoding="utf-8")
            rc, doc = run(_ns(base, no_errata=False, errata=str(errata_fake)))
            defects = doc["results"][0]["defects"]
            check("errata-corrects-an-ordinary-absent-citation",
                  rc == 1 and doc["summary"]["errata_invalid"] == 0
                  and any(d["token"] == mash and d["corrected_by"]
                          for d in defects)
                  and doc["summary"]["uncorrected"] == 2)
            identity = git_env(GIT_AUTHOR_NAME="kama-shokunin",
                               GIT_COMMITTER_NAME="kama-shokunin",
                               GIT_AUTHOR_EMAIL="a@x",
                               GIT_COMMITTER_EMAIL="a@x")
            tree = git(lane, "rev-parse", "HEAD^{tree}").strip()
            target = git(lane, "commit-tree", tree, "-m", "tag target",
                         env=identity).strip()
            git(lane, "tag", "-a", "-m", "hole", "v-hole", target,
                env=identity)
            tag_oid = git(lane, "rev-parse", "v-hole").strip()
            Path(lane, git(lane, "rev-parse", "--git-path",
                           "objects").strip(),
                 target[:2], target[2:]).unlink()
            tag_draft = Path(tmp, "tag-draft.md")
            tag_draft.write_text(
                "## Landed changes\n- `" + tag_oid + "` tag\n",
                encoding="utf-8")
            check("known-tag-with-unavailable-target-is-unknown",
                  is_error(lambda: run(_ns(base, report=[f"1={tag_draft}"]))))
            # the same tag in both audited repositories: one of them can
            # serve what the tag points at, so the citation is a known
            # mismatch, not an unknown
            target = git(fleet, "hash-object", "-w", "--stdin",
                         stdin="tag target\n").strip()
            identity = git_env(GIT_AUTHOR_NAME="k", GIT_COMMITTER_NAME="k",
                               GIT_AUTHOR_EMAIL="a@x",
                               GIT_COMMITTER_EMAIL="a@x")
            tag = git(fleet, "mktag",
                      stdin=f"object {target}\ntype blob\ntag t\n"
                            f"tagger k <a@x> 1000 +0000\n\ntag\n",
                      env=identity).strip()

            def _obj(repo, oid):
                path = Path(repo, git(repo, "rev-parse", "--git-path",
                                      "objects").strip(), oid[:2], oid[2:])
                path.parent.mkdir(parents=True, exist_ok=True)
                return path

            _obj(lane, tag).write_bytes(_obj(fleet, tag).read_bytes())
            _obj(lane, target).write_bytes(_obj(fleet, target).read_bytes())
            shared_draft = Path(tmp, "shared-tag-draft.md")
            shared_draft.write_text(
                "## Landed changes\n- `" + tag + "` tag\n", encoding="utf-8")
            rc, doc = run(_ns(base, report=[f"1={shared_draft}"]))
            kinds = sorted((x["kind"], x["token"])
                           for x in doc["results"][0]["defects"])
            check("same-tag-in-both-stores-known-mismatch-is-a-control",
                  rc == 1 and ("landed-unresolved", tag) in kinds)
            # the target is observable in the fleet only: the fleet proves
            # the mismatch, the lane cannot serve the target
            _obj(lane, target).unlink()
            rc, doc = run(_ns(base, report=[f"1={shared_draft}"]))
            kinds = sorted((x["kind"], x["token"])
                           for x in doc["results"][0]["defects"])
            check("same-tag-with-the-target-only-in-the-fleet-is-a-mismatch",
                  rc == 1 and ("landed-unresolved", tag) in kinds)
            # the mirror: the target is observable in the lane only
            _obj(lane, target).write_bytes(_obj(fleet, target).read_bytes())
            _obj(fleet, target).unlink()
            rc, doc = run(_ns(base, report=[f"1={shared_draft}"]))
            kinds = sorted((x["kind"], x["token"])
                           for x in doc["results"][0]["defects"])
            check("same-tag-with-the-target-only-in-the-lane-is-a-mismatch",
                  rc == 1 and ("landed-unresolved", tag) in kinds)
            # the target is observable nowhere: the content cannot be read
            _obj(lane, target).unlink()
            check("tag-target-missing-everywhere-is-unknown",
                  is_error(lambda: run(_ns(base, report=[f"1={shared_draft}"]))))
            missing, opaque = missing_reachable(
                lane, git(lane, "rev-parse", "HEAD").strip())
            check("blob-hole-is-not-an-opaque-hole",
                  hole in missing and hole not in opaque)
            # an unreachable MISSING BLOB is not an opaque hole: the
            # fabricated citation here is UNRELATED and absent, so the
            # ordinary finding stands (the dangling blob itself is cited in
            # the next control, which is unknown)
            dangling_blob = git(lane, "hash-object", "-w", "--stdin",
                                stdin="dangling blob\n").strip()
            blob_tree = git(lane, "mktree", stdin=f"100644 blob "
                           f"{dangling_blob}\td\n").strip()
            Path(lane, git(lane, "rev-parse", "--git-path",
                           "objects").strip(),
                 dangling_blob[:2], dangling_blob[2:]).unlink()
            fake = "1234567890abcdef1234567890abcdef12345678"
            garbage_draft = Path(tmp, "garbage-draft.md")
            garbage_draft.write_text(
                "## Work performed\n" + fake + "\n"
                "## Landed changes\n- `" + a[:9] + "` work\n",
                encoding="utf-8")
            rc, doc = run(_ns(base, report=[f"1={garbage_draft}"]))
            kinds = sorted((x["kind"], x["token"])
                           for x in doc["results"][0]["defects"])
            check("unreachable-missing-blob-does-not-block",
                  rc == 1 and ("unresolved-full-hash", fake) in kinds)
            cited_draft = Path(tmp, "cited-dangling-draft.md")
            cited_draft.write_text(
                "## Work performed\n" + dangling_blob + "\n"
                "## Landed changes\n- `" + a[:9] + "` work\n",
                encoding="utf-8")
            check("cited-missing-behind-a-dangling-tree-is-unknown",
                  is_error(lambda: run(_ns(base, report=[f"1={cited_draft}"]))))
            # an unreachable MISSING TREE is an opaque hole for the store
            # but not for the audited root: a dangling commit names a tree
            # the store cannot serve, and no ref reaches either of them
            kept_blob = git(lane, "hash-object", "-w", "--stdin",
                            stdin="kept blob\n").strip()
            opaque_tree = git(lane, "mktree", stdin=f"100644 blob "
                              f"{kept_blob}\tkeep\n").strip()
            dangling_commit = git(lane, "commit-tree", opaque_tree, "-m",
                                  "dangling", env=git_env(
                                      GIT_AUTHOR_NAME="kama-shokunin",
                                      GIT_COMMITTER_NAME="kama-shokunin",
                                      GIT_AUTHOR_EMAIL="a@x",
                                      GIT_COMMITTER_EMAIL="a@x")).strip()
            Path(lane, git(lane, "rev-parse", "--git-path",
                           "objects").strip(),
                 opaque_tree[:2], opaque_tree[2:]).unlink()
            missing_all, opaque_relevant = missing_reachable(
                lane, git(lane, "rev-parse", "HEAD").strip())
            all_roots = present_roots(lane)
            opaque_everywhere = {
                line[1:] for line in git(
                    lane, "-c", "core.commitGraph=false", "rev-list",
                    "--objects", "--missing=print", "--no-object-names",
                    "--filter=blob:none", "--stdin",
                    stdin="".join(f"{r}\n" for r in all_roots)
                ).split("\n") if line.startswith("?")}
            check("store-wide-walk-sees-the-unreachable-missing-tree",
                  opaque_tree in missing_all
                  and opaque_tree in opaque_everywhere
                  and opaque_tree not in opaque_relevant
                  and dangling_commit in all_roots)
            rc, doc = run(_ns(base, report=[f"1={garbage_draft}"]))
            kinds = sorted((x["kind"], x["token"])
                           for x in doc["results"][0]["defects"])
            check("unreachable-opaque-garbage-does-not-block",
                  rc == 1 and ("unresolved-full-hash", fake) in kinds)
            tree = git(lane, "rev-parse", f"{mid}^{{tree}}").strip()
            Path(lane, git(lane, "rev-parse", "--git-path",
                           "objects").strip(),
                 tree[:2], tree[2:]).unlink()
            missing, opaque = missing_reachable(
                lane, git(lane, "rev-parse", "HEAD").strip())
            check("missing-tree-is-an-opaque-hole", tree in opaque)
            clean_draft = Path(tmp, "clean-draft.md")
            clean_draft.write_text(
                "## Landed changes\n" + "".join(
                    f"- `{oid}` cited\n" for oid in (a, b, c, d, edge)),
                encoding="utf-8")
            rc, doc = run(_ns(base, report=[f"1={clean_draft}"]))
            check("unused-tree-hole-does-not-block-resolved-citations",
                  rc == 0 and doc["results"][0]["defects"] == [])
            check("opaque-hole-makes-an-unresolved-token-unknown",
                  is_error(lambda: run(base)))
            # the open range lists the fleet reports: a missing fleet tip
            # tree must be refused with the tree named
            fleet_tree = git(fleet, "rev-parse", "HEAD^{tree}").strip()
            Path(fleet, git(fleet, "rev-parse", "--git-path",
                            "objects").strip(),
                 fleet_tree[:2], fleet_tree[2:]).unlink()
            message = ""
            try:
                run(_ns(base, rounds="10-"))
            except EvalError as exc:
                message = str(exc)
            check("open-range-listing-names-the-missing-fleet-tree",
                  fleet_tree in message
                  and "unavailable required object" in message)
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
