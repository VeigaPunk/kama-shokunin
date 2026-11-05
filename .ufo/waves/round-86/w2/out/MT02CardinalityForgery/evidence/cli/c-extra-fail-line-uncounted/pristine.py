#!/usr/bin/env python3
"""round81-append-debt.py - round-81 C2 (operability): grade the append-only acceptance
population under a late-acceptance rule.

PREDICATE (frozen: plans/round-81-claims.md section C2):

    `python3 tools/round81-append-debt.py --repo <lane> --round 81` prints one `APPEND_DEBT
    round=81 base=<12-hex> events=<e> accepted=<a> late=<l> pending=<p> unaccepted=<u>
    bad_rows=<r> bad_declarations=<d> out_of_population=<o>` line and exits 0 only when every
    undeclared deletion event the frozen `tools/append-only-audit.py --json` reports at the tip
    whose commit is ancestral to the round's declared base is accepted either by a frozen
    `registry/append-only-accepted.tsv` row (the round-75 rule) or by a committed
    `registry/append-only-late.tsv` row whose introducing commit is a strict descendant of the
    event commit and whose note names the accepting round `N` and the deletion round `M` with
    `N > M`; a row that names an event outside the base population is counted on
    `out_of_population` and changes no bucket; rows introduced by the graded round cannot accept
    that round's own events (`pending`), and a same-round, short-count, wrong-class or
    non-descendant row is a `bad_rows` finding; it exits 1 naming every unaccepted event
    otherwise.

The population is the frozen audit's `pending` set (events with undisclosed lines whose status is
not `restored`), split by ancestry to the base: an event at or before the base is `graded`, an
event committed after it is `pending` (the graded round's own record edits, which the NEXT round
must accept). The base is read from `plans/round-<N>-claims.md` and never from a caller-chosen
value: `--base` is accepted only when it equals the plan's declared base, and the base must be an
ancestor of the audited revision.

The frozen register's own rule is preserved verbatim, including its pre-introduction cutoff: a
`append-only-accepted.tsv` row for an event made at or after that register's introduction is a
`bad_rows` finding (round-51 sentinel). That cutoff is why the frozen rule is unsatisfiable for
post-introduction events, which is what this module's late register answers.

ROW-INTRODUCTION REPAIR (round 82, disclosed in the round-82 report and lesson): the PREDICATE
above and plans/round-81-claims.md both say "a committed registry/append-only-late.tsv row whose
introducing commit is a strict descendant of the event commit" -- a ROW's introducing commit. This
module used to resolve ONE commit for the whole register (`git log --diff-filter=A`), so it could
never accept an event created after the register first existed: the same unsatisfiable shape the
round-75 rule had. Round 82 resolves each row's own introducing commit with
`git blame <rev> -- registry/append-only-late.tsv` (`blame_rows`), falling back to the register's
introduction for a row whose blame line cannot be resolved. Every other rule sentence is unchanged;
three selftest arms (`row-intro-later`, `row-intro-earlier`, `row-intro-unbound`) prove the row-level
reading and the first one fails under the old register-level resolution.

ROUND-83 PATH-BINDING: a caller-supplied --late path is resolved inside the repository working
tree and must be committed at the audited revision. Its file and row introductions are resolved
there before the unchanged grade rule runs. Relative paths are relative to --repo; outside,
untracked, or unresolvable row identities refuse evaluation (exit 2), not per-row verdicts.
The arms late-path-outside-repo, late-path-untracked, late-path-dirty, and late-path-bound cover
these bindings and equality with default-path grading.

Usage: round81-append-debt.py --repo DIR [--round N] [--base REV] [--to REV]
       [--register FILE] [--late FILE] [--audit-json FILE] [--json] | --selftest

Exit: 0 every graded event accepted; 1 findings; 2 could-not-evaluate (missing plan, base
mismatch, unreadable register, audit failure) -- never silently 0.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HEADER = "commit\tfile\tline_sha256\tcount\tclass\tnote"
PLAN = "plans/round-{round}-claims.md"
REGISTER = "registry/append-only-accepted.tsv"
LATE = "registry/append-only-late.tsv"
BASE_RE = re.compile(r"Base revision `([0-9a-f]{40})`")
NOTE_RE = re.compile(r"round-([0-9]+)\s+accepts\s+round-([0-9]+)\b")
SHA = re.compile(r"[0-9a-f]{40}")


class CouldNotEvaluate(Exception):
    pass


def validate_audit(data):
    """Reject incomplete receipts rather than interpreting missing fields as zero."""
    if not isinstance(data, dict) or data.get("schema") != "append-only-audit/v3":
        raise CouldNotEvaluate("expected append-only-audit/v3")

    def require(condition):
        if not condition:
            raise CouldNotEvaluate("incomplete or inconsistent audit JSON")

    try:
        events, declarations, summary = data["events"], data["declarations"], data["summary"]
        require(isinstance(events, list) and isinstance(declarations, list))
        require(isinstance(data.get("to"), str) and SHA.fullmatch(data["to"]))
        require(type(summary["bad_declarations"]) is int)
        require(summary["bad_declarations"] == sum(d["ok"] is False for d in declarations))
        require(all(type(d["ok"]) is bool for d in declarations))
        seen = set()
        for event in events:
            key = (event["commit"], event["file"])
            require(SHA.fullmatch(key[0]) and isinstance(key[1], str) and key[1])
            require(key not in seen)
            seen.add(key)
            require(event["status"] in {"ungraded", "restored", "disclosed", "unrestored", "partial"})
            require(isinstance(event["undisclosed"], list))
            hashes = set()
            for entry in event["undisclosed"]:
                require(re.fullmatch(r"[0-9a-f]{64}", entry["line_sha256"]))
                require(type(entry["count"]) is int and entry["count"] > 0)
                require(entry["line_sha256"] not in hashes)
                require(isinstance(entry["classes"], list) and entry["classes"])
                hashes.add(entry["line_sha256"])
    except (KeyError, TypeError) as exc:
        raise CouldNotEvaluate(f"incomplete audit JSON: {exc}") from exc


def population(data):
    """(graded, pending) event maps: events with undisclosed lines, keyed (commit, file)."""
    out = {}
    for event in data["events"]:
        if event["undisclosed"] and event["status"] != "restored":
            out[(event["commit"], event["file"])] = event
    return out


def split(events, graded):
    """{(commit, file): event} keys whose commit satisfies ``graded(commit)`` — the graded
    population; every other event is ``pending`` (the graded round's own record edits)."""
    return {key for key in events if graded(key[0])}


def resolve_base(plan_text, requested):
    """The frozen plan's declared base; a caller-supplied ``--base`` must equal it."""
    match = BASE_RE.search(plan_text or "")
    if not match:
        raise CouldNotEvaluate("the frozen plan declares no `Base revision`")
    plan_base = match.group(1)
    if requested and requested != plan_base:
        raise CouldNotEvaluate(f"--base {requested} differs from the frozen plan's {plan_base}")
    return plan_base


def parse_register(text, label):
    """[(commit, file, line_sha256, count, class, note, line_number)] or CouldNotEvaluate."""
    if "\r" in text:
        raise CouldNotEvaluate(f"{label} carries CR bytes")
    lines = text.splitlines()
    if not lines or lines[0] != HEADER:
        raise CouldNotEvaluate(f"{label} requires the six-column LF TSV header")
    rows = []
    for number, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != 6:
            raise CouldNotEvaluate(f"{label} line {number}: expected six cells")
        rows.append((cells[0], cells[1], cells[2], cells[3], cells[4], cells[5], number))
    return rows


def grade(events, frozen_rows, late_rows, *, graded_keys, frozen_precedes,
          late_intro, is_strict_descendant, row_intro=None, subject_rounds=None):
    """Grade both registers against the population. Pure: every git fact is a callable.

    graded_keys          set of (commit, file) at or before the base
    frozen_precedes      callable(commit) -> bool, the round-75 pre-introduction cutoff
    late_intro           the late register's own introducing commit (or None); used for a row
                         whose own introducing commit cannot be resolved
    row_intro            callable(line_number) -> the commit that introduced that register line
                         (the row's introducing commit -- the rule's own wording), or None
    is_strict_descendant callable(event_commit, row_commit) -> bool
    subject_rounds       callable(commit) -> int | None, the event subject's declared round
    """
    all_events = {}
    for key, event in events.items():
        all_events[key] = event
    expected = {(key[0], key[1], u["line_sha256"]): u
                for key, e in events.items() for u in e["undisclosed"]}
    findings, covered, seen = [], set(), set()
    frozen_keys = set()
    bad_rows = 0
    out_of_population = 0
    late_seen = set()
    late_covered = set()

    def bad(kind, detail):
        nonlocal bad_rows
        bad_rows += 1
        findings.append({"class": kind, "detail": detail})

    # ---- frozen register (the round-75 rule, verbatim)
    for commit, file, digest, count, klass, note, number in frozen_rows:
        key, row_key = (commit, file), (commit, file, digest)
        detail = f"frozen line {number}: {commit} {file} {digest}"
        if row_key in seen:
            bad("duplicate", detail)
            continue
        seen.add(row_key)
        event = all_events.get(key)
        if event is None:
            bad("unknown-event", detail)
            continue
        if event["status"] == "restored":
            bad("restored-event", detail)
            continue
        entry = expected.get(row_key)
        if entry is None or not re.fullmatch(r"[0-9a-f]{64}", digest):
            bad("hash-mismatch", detail)
            continue
        if not re.fullmatch(r"[1-9][0-9]*", count) or int(count) != entry["count"]:
            bad("count-short", f"{detail}: count={count} expected={entry['count']}")
            continue
        if klass not in entry["classes"]:
            bad("class-mismatch", f"{detail}: class={klass} expected={entry['classes']}")
            continue
        if not note.strip() or "; " not in note or not all(p.strip() for p in note.split("; ", 1)):
            bad("hash-mismatch", f"{detail}: note requires commit subject; acceptance reason")
            continue
        if not frozen_precedes(commit):
            bad("post-introduction", f"{detail}: commit is not an ancestor of the frozen "
                                     f"register's introduction commit")
            continue
        if key not in graded_keys:
            out_of_population += 1
            continue
        covered.add(row_key)
        frozen_keys.add(key)

    # ---- late register (late-acceptance rule)
    for commit, file, digest, count, klass, note, number in late_rows:
        key, row_key = (commit, file), (commit, file, digest)
        detail = f"late line {number}: {commit} {file} {digest}"
        if row_key in late_seen:
            bad("duplicate", detail)
            continue
        late_seen.add(row_key)
        event = all_events.get(key)
        if event is None:
            bad("unknown-event", detail)
            continue
        if event["status"] == "restored":
            bad("restored-event", detail)
            continue
        entry = expected.get(row_key)
        if entry is None or not re.fullmatch(r"[0-9a-f]{64}", digest):
            bad("hash-mismatch", detail)
            continue
        if not re.fullmatch(r"[1-9][0-9]*", count) or int(count) != entry["count"]:
            bad("count-short", f"{detail}: count={count} expected={entry['count']}")
            continue
        if klass not in entry["classes"]:
            bad("class-mismatch", f"{detail}: class={klass} expected={entry['classes']}")
            continue
        match = NOTE_RE.search(note or "")
        if not note.strip() or "; " not in note or not all(p.strip() for p in note.split("; ", 1)):
            bad("hash-mismatch", f"{detail}: note requires commit subject; acceptance reason")
            continue
        if match is None:
            bad("note-no-round", f"{detail}: note names no `round-<N> accepts round-<M>` pair")
            continue
        accepting, deletion = int(match.group(1)), int(match.group(2))
        if accepting <= deletion:
            bad("same-round", f"{detail}: accepting round {accepting} is not after deletion "
                              f"round {deletion}")
            continue
        subject_round = subject_rounds(commit) if subject_rounds is not None else None
        if subject_round is not None and deletion != subject_round:
            bad("note-wrong-deletion-round", f"{detail}: note deletion round {deletion} "
                                             f"differs from subject round {subject_round}")
            continue
        intro = row_intro(number) if row_intro is not None else late_intro
        if intro is None:
            bad("unbound-register", f"{detail}: late row has no committed introduction")
            continue
        if not is_strict_descendant(commit, intro):
            bad("not-descendant", f"{detail}: row-introduction commit {intro} is not a strict "
                                  f"descendant of event commit {commit}")
            continue
        if key not in graded_keys:
            out_of_population += 1
            continue
        covered.add(row_key)
        late_covered.add(key)

    unaccepted = []
    for key, event in events.items():
        if key not in graded_keys:
            continue
        missing = [u for u in event["undisclosed"] if (*key, u["line_sha256"]) not in covered]
        if missing:
            unaccepted.append({"commit": key[0], "file": key[1], "missing": len(missing)})
            for entry in missing:
                findings.append({"class": "count-short",
                                 "detail": f"{key[0]} {key[1]} {entry['line_sha256']}: "
                                           f"missing {entry['count']}"})
    accepted = len(frozen_keys & graded_keys)
    late = len((late_covered - frozen_keys) & graded_keys)
    result = {
        "events": len(graded_keys),
        "accepted": accepted,
        "late": late,
        "pending": len(events) - len(graded_keys),
        "unaccepted": len(unaccepted),
        "bad_rows": bad_rows,
        "bad_declarations": 0,
        "out_of_population": out_of_population,
    }
    return {"schema": "append-debt/v1", "summary": result, "findings": findings}


def render(result):
    s = result["summary"]
    head = (f"APPEND_DEBT round={result['round']} base={result['base'][:12]} "
            f"events={s['events']} accepted={s['accepted']} late={s['late']} "
            f"pending={s['pending']} unaccepted={s['unaccepted']} bad_rows={s['bad_rows']} "
            f"bad_declarations={s['bad_declarations']} "
            f"out_of_population={s['out_of_population']}")
    lines = [head]
    for finding in result["findings"]:
        lines.append(f"APPEND_DEBT_FINDING {finding['class']} {finding['detail']}")
    return "\n".join(lines)


def verdict(result):
    s = result["summary"]
    return 0 if (s["unaccepted"] == 0 and s["bad_rows"] == 0 and s["bad_declarations"] == 0
                 and s["out_of_population"] == 0) else 1


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          timeout=180)
    if proc.returncode != 0:
        raise CouldNotEvaluate(f"git {' '.join(args)} exit={proc.returncode}: {proc.stderr.strip()}")
    return proc.stdout


def show(repo: Path, rev: str, path: str) -> str | None:
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"],
                          capture_output=True, text=True, timeout=180)
    return proc.stdout if proc.returncode == 0 else None


def is_ancestor(repo: Path, a: str, b: str) -> bool:
    return subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", a, b],
                          capture_output=True, timeout=180).returncode == 0


def introduction(repo: Path, rev: str, path: str) -> str | None:
    proc = subprocess.run(["git", "-C", str(repo), "log", "--diff-filter=A", "--format=%H",
                           rev, "--", path], capture_output=True, text=True, timeout=180)
    commits = [c for c in proc.stdout.split() if c]
    return commits[-1] if proc.returncode == 0 and commits else None


def blame_rows(repo: Path, rev: str, path: str) -> dict[int, str]:
    """Final line number -> the commit that introduced that line at `rev` (row introduction)."""
    proc = subprocess.run(["git", "-C", str(repo), "blame", "--line-porcelain", rev, "--", path],
                          capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        return {}
    rows = {}
    for line in proc.stdout.splitlines():
        if line.startswith("\t"):
            continue
        match = re.match(r"^([0-9a-f]{40}) [0-9]+ ([0-9]+)(?: [0-9]+)?$", line)
        if match and set(match.group(1)) != {"0"}:
            rows[int(match.group(2))] = match.group(1)
    return rows


def load_late(repo: Path, rev: str, requested: str | None):
    """Read the late register and bind its committed file and row identities."""
    path = LATE
    if requested is not None:
        root = Path(git(repo, "rev-parse", "--show-toplevel").strip()).resolve()
        supplied = Path(requested)
        resolved = (supplied if supplied.is_absolute() else repo / supplied).resolve()
        try:
            path = resolved.relative_to(root).as_posix()
        except ValueError as exc:
            raise CouldNotEvaluate("--late path is outside the repository") from exc
        git(repo, "cat-file", "-e", f"{rev}:{path}")
        text = resolved.read_bytes().decode("utf-8")
        committed = show(repo, rev, path)
        if committed is None or text != committed:
            raise CouldNotEvaluate(f"--late {path} differs from its committed bytes at {rev}")
    else:
        text = show(repo, rev, path)
    if text is None:
        return HEADER + "\n", None, None
    intro = introduction(repo, rev, path)
    if intro is None:
        raise CouldNotEvaluate(f"cannot resolve {path}'s introduction commit")
    marks = blame_rows(repo, rev, path)
    if requested is not None:
        for row in parse_register(text, "late register"):
            if row[-1] not in marks:
                raise CouldNotEvaluate(f"cannot resolve {path} line {row[-1]}'s introduction")
    return text, intro, marks


def late_path_selftests():
    """Exercise the production path binder in a disposable, two-commit repository."""
    cases = []

    def record(name, ok):
        cases.append((name, {"summary": {"unaccepted": 0 if ok else 1, "bad_rows": 0,
                                         "bad_declarations": 0, "out_of_population": 0}},
                      0, None))

    with tempfile.TemporaryDirectory(prefix="append-debt-path-") as directory:
        scratch = Path(directory).resolve()
        repo = scratch / "repo"
        repo.mkdir()
        git(repo, "init", "-q")
        if Path(git(repo, "rev-parse", "--show-toplevel").strip()).resolve() != repo:
            raise CouldNotEvaluate("selftest repository root mismatch")
        register = repo / LATE
        register.parent.mkdir()
        register.write_text(HEADER + "\n", encoding="utf-8")
        git(repo, "add", "--", LATE)
        git(repo, "-c", "user.name=probe", "-c", "user.email=p@p",
            "commit", "-qm", "round-80 event")
        event_commit = git(repo, "rev-parse", "HEAD").strip()
        digest = "1" * 64
        register.write_text(HEADER + "\n" + "\t".join(
            (event_commit, "SCORECARD.md", digest, "1", "in-place-edit",
             "round-81 accepts round-80 subject; accepted history")) + "\n", encoding="utf-8")
        git(repo, "add", "--", LATE)
        git(repo, "-c", "user.name=probe", "-c", "user.email=p@p",
            "commit", "-qm", "round-81 acceptance")
        rev = git(repo, "rev-parse", "HEAD").strip()
        outside = scratch / "outside.tsv"
        outside.write_text(register.read_text(encoding="utf-8"), encoding="utf-8")
        untracked = repo / "untracked.tsv"
        untracked.write_text(register.read_text(encoding="utf-8"), encoding="utf-8")
        for name, path in (("late-path-outside-repo", str(outside)),
                           ("late-path-untracked", str(untracked))):
            refused = False
            try:
                load_late(repo, rev, path)
            except CouldNotEvaluate:
                refused = True
            record(name, refused)
        committed_text = register.read_text(encoding="utf-8")
        register.write_text(committed_text + "# local edit, never committed\n", encoding="utf-8")
        dirty_refused = False
        try:
            load_late(repo, rev, LATE)
        except CouldNotEvaluate:
            dirty_refused = True
        record("late-path-dirty", dirty_refused)
        register.write_text(committed_text, encoding="utf-8")
        default = load_late(repo, rev, None)
        bound = load_late(repo, rev, LATE)
        event = _event(event_commit, "SCORECARD.md", digest, 1, "in-place-edit")
        events = {(event_commit, "SCORECARD.md"): event}

        def evaluate(loaded):
            text, intro, marks = loaded
            return grade(events, [], parse_register(text, "late register"),
                         graded_keys=set(events), frozen_precedes=lambda c: False,
                         late_intro=intro,
                         row_intro=marks.get if marks is not None else None,
                         is_strict_descendant=lambda e, r: e != r and is_ancestor(repo, e, r))

        result = evaluate(bound)
        record("late-path-bound", bound == default and bound[1] == event_commit
               and bound[2].get(2) == rev and result == evaluate(default)
               and verdict(result) == 0 and result["summary"]["late"] == 1)
    return cases


# ---------------------------------------------------------------- selftest

def _event(commit, file, digest, count, klass, status="unrestored"):
    return {"commit": commit, "file": file, "status": status,
            "undisclosed": [{"line_sha256": digest, "count": count, "classes": [klass]}]}


# The declared selftest arm population. Round-86 froze it so a dropped arm is a red summary
# instead of a quietly smaller green one (round-85 receipt: pass=34 fail=0).
EXPECTED_ARMS = 34


def selftest() -> int:
    A, B, C = "a" * 40, "b" * 40, "c" * 40
    D = "d" * 40
    H1, H2 = "1" * 64, "2" * 64
    late_intro = "9" * 40

    def ev(commit, file, digest, count=1, klass="in-place-edit", status="unrestored"):
        return _event(commit, file, digest, count, klass, status)

    events = {(A, "SCORECARD.md"): ev(A, "SCORECARD.md", H1),
              (B, "SCORECARD.md"): ev(B, "SCORECARD.md", H2)}
    after = {(C, "LOG.md"): ev(C, "LOG.md", H1)}
    all_events = {**events, **after}
    graded = set(events)
    frozen = [(A, "SCORECARD.md", H1, "1", "in-place-edit", "subject; accepted", 2)]
    cases = []

    def run(rows, late_rows, *, graded_keys=graded, desc=None, intro=late_intro,
            frozen_ok=None, row_marks=None, subject_rounds=None):
        return grade(all_events, rows, late_rows,
                     graded_keys=graded_keys,
                     frozen_precedes=frozen_ok or (lambda c: c == A),
                     late_intro=intro,
                     is_strict_descendant=(desc or (lambda e, r: r != e)),
                     row_intro=row_marks, subject_rounds=subject_rounds)

    def late_row(commit, file, digest, count="1", klass="in-place-edit",
                 note=f"round-81 accepts round-80 subject; accepted history"):
        return (commit, file, digest, count, klass, note, 2)

    # 1 honest: frozen accepts A, late accepts B
    r = run(frozen, [late_row(B, "SCORECARD.md", H2)])
    cases.append(("honest", r, 0, None))
    # 2 no late register: B unaccepted
    r = run(frozen, [])
    cases.append(("no-late", r, 1, "count-short"))
    # 3 same round
    r = run(frozen, [late_row(B, "SCORECARD.md", H2,
                              note="round-80 accepts round-80 subject; x")])
    cases.append(("same-round", r, 1, "same-round"))
    # 4 same commit (register introduced by the event commit)
    r = run(frozen, [late_row(B, "SCORECARD.md", H2)], desc=lambda e, r_: False)
    cases.append(("same-commit", r, 1, "not-descendant"))
    # 5 short count
    r = run(frozen, [late_row(B, "SCORECARD.md", H2, count="2")])
    cases.append(("short-count", r, 1, "count-short"))
    # 6 wrong class
    r = run(frozen, [late_row(B, "SCORECARD.md", H2, klass="removal")])
    cases.append(("wrong-class", r, 1, "class-mismatch"))
    # 7 note names no round
    r = run(frozen, [late_row(B, "SCORECARD.md", H2, note="accepted history; no round")])
    cases.append(("note-no-round", r, 1, "note-no-round"))
    # 8 out of population: a row naming the post-base event changes no bucket
    r = run(frozen, [late_row(B, "SCORECARD.md", H2),
                     late_row(C, "LOG.md", H1)])
    cases.append(("out-of-population", r, 1, "out-of-population"))
    # same case with no debt: out-of-population alone is a finding
    r = run(frozen, [late_row(C, "LOG.md", H1)], graded_keys=set(events))
    cases.append(("out-only", r, 1, "out-of-population"))
    # 9 duplicate row
    r = run(frozen, [late_row(B, "SCORECARD.md", H2), late_row(B, "SCORECARD.md", H2)])
    cases.append(("duplicate", r, 1, "duplicate"))
    # 10 frozen post-introduction row
    r = run(frozen + [(B, "SCORECARD.md", H2, "1", "in-place-edit", "subject; x", 3)], [])
    cases.append(("frozen-post-introduction", r, 1, "post-introduction"))
    # 11 malformed register: a bad header and a five-cell row both refuse evaluation
    for label, text in (("header", "bad header\n"), ("cells", HEADER + "\na\tb\tc\n")):
        try:
            parse_register(text, "fixture")
            fail_parse = True
        except CouldNotEvaluate:
            fail_parse = False
        cases.append((f"parse-{label}", {"summary": {"unaccepted": 0, "bad_rows": 0,
                                                     "bad_declarations": 0, "out_of_population": 0,
                                                     "accepted": 0, "late": 0, "pending": 0,
                                                     "events": 0},
                                         "findings": []}, 1 if fail_parse else 0, None))
    # 12 late row for an event of another file/commit: unknown event
    r = run(frozen, [late_row(D, "SCORECARD.md", H2)])
    cases.append(("unknown-event", r, 1, "unknown-event"))
    # 13 pending events are not graded
    r = run(frozen, [], graded_keys={(A, "SCORECARD.md")})
    cases.append(("pending-not-graded", r, 0, None))
    # 14 accepting round not after deletion round
    r = run(frozen, [late_row(B, "SCORECARD.md", H2,
                              note="round-5 accepts round-80 subject; x")])
    cases.append(("reverse-round", r, 1, "same-round"))
    # 15 frozen register row carrying the wrong mechanical class
    r = run([(A, "SCORECARD.md", H1, "1", "removal", "subject; accepted", 2)],
            [late_row(B, "SCORECARD.md", H2)])
    cases.append(("frozen-wrong-class", r, 1, "class-mismatch"))
    # 16 frozen register row naming an event outside the base population changes no bucket
    r = run(frozen + [(C, "LOG.md", H1, "1", "in-place-edit", "subject; x", 3)],
            [late_row(B, "SCORECARD.md", H2)], frozen_ok=lambda c: True)
    cases.append(("frozen-out-of-population", r, 1, "out-of-population"))
    # 17 the population split: the post-base event is pending, never graded
    graded_split = split(all_events, lambda commit: commit in {A, B})
    split_ok = len(graded_split) == 2 and len(all_events) - len(graded_split) == 1
    cases.append(("split-pending",
                  {"summary": {"unaccepted": 0 if split_ok else 1, "bad_rows": 0,
                               "bad_declarations": 0, "out_of_population": 0}}, 0, None))
    # 18-20 the base resolution: absent, mismatched, matching
    plan_text = f"# fixture plan\n\nBase revision `{'a' * 40}`\n"
    for label, requested, expect_raise in (("base-absent", "a" * 40, True),
                                           ("base-mismatch", "b" * 40, True),
                                           ("base-ok", "a" * 40, False)):
        raised = False
        try:
            got = resolve_base(plan_text if label != "base-absent" else "no base here", requested)
        except CouldNotEvaluate:
            raised = True
        ok = (raised == expect_raise) and (raised or got == "a" * 40)
        cases.append((f"resolve-{label}", {"summary": {"unaccepted": 0 if ok else 1,
                                                       "bad_rows": 0, "bad_declarations": 0,
                                                       "out_of_population": 0}}, 0, None))
    # 21-23 the row's own introducing commit is what the rule reads: a row appended by a later
    # round after the register's own introduction accepts a post-register event, a row introduced
    # before the event is refused, and an unresolvable row introduction is unbound.
    later = "8" * 40
    r = run(frozen, [late_row(B, "SCORECARD.md", H2)],
            desc=lambda e, r_: r_ == later,
            row_marks=lambda n: later)
    cases.append(("row-intro-later", r, 0, None))
    r = run(frozen, [late_row(B, "SCORECARD.md", H2)],
            desc=lambda e, r_: r_ == later,
            row_marks=lambda n: A)
    cases.append(("row-intro-earlier", r, 1, "not-descendant"))
    r = run(frozen, [late_row(B, "SCORECARD.md", H2)],
            desc=lambda e, r_: r_ == later,
            row_marks=lambda n: None)
    cases.append(("row-intro-unbound", r, 1, "unbound-register"))
    r = run(frozen, [late_row(B, "SCORECARD.md", H2,
                              note="round-81 accepts round-78 subject; accepted history")],
            subject_rounds=lambda commit: 79)
    cases.append(("note-subject-mismatch", r, 1, "note-wrong-deletion-round"))
    r = run(frozen, [late_row(B, "SCORECARD.md", H2,
                              note="round-81 accepts round-78 subject; accepted history")],
            subject_rounds=lambda commit: None)
    cases.append(("note-subject-unresolvable", r, 0, None))
    cases.extend(late_path_selftests())
    # Round-85 controls bind deletion to the resolved subject, not the accepting round.
    r = run(frozen, [late_row(B, "SCORECARD.md", H2,
                              note="round-81 accepts round-79 subject; accepted history")],
            subject_rounds=lambda commit: 79)
    cases.append(("note-deletion-equals-subject", r, 0, None))
    r = run(frozen, [late_row(B, "SCORECARD.md", H2,
                              note="round-81 accepts round-80 subject; accepted history")],
            subject_rounds=lambda commit: 79)
    cases.append(("note-deletion-above-subject", r, 1, "note-wrong-deletion-round"))
    r = run(frozen, [late_row(B, "SCORECARD.md", H2,
                              note="round-81 accepts round-78 subject; accepted history")],
            subject_rounds=lambda commit: 79)
    cases.append(("note-subject-exact-summary", r, 1, "note-wrong-deletion-round"))
    # A binding finding must stop the row before it can accept the event.
    expected_summaries = {
        "note-deletion-equals-subject": {
            "events": 2, "accepted": 1, "late": 1, "pending": 1,
            "unaccepted": 0, "bad_rows": 0, "bad_declarations": 0,
            "out_of_population": 0,
        },
        "note-deletion-above-subject": {
            "events": 2, "accepted": 1, "late": 0, "pending": 1,
            "unaccepted": 1, "bad_rows": 1, "bad_declarations": 0,
            "out_of_population": 0,
        },
        "note-subject-exact-summary": {
            "events": 2, "accepted": 1, "late": 0, "pending": 1,
            "unaccepted": 1, "bad_rows": 1, "bad_declarations": 0,
            "out_of_population": 0,
        },
    }
    expected_findings = {
        "note-deletion-equals-subject": [],
        "note-deletion-above-subject": ["note-wrong-deletion-round", "count-short"],
        "note-subject-exact-summary": ["note-wrong-deletion-round", "count-short"],
    }

    fail = 0
    for name, result, want_exit, want_class in cases:
        s = result["summary"]
        got = 0 if (s["unaccepted"] == 0 and s["bad_rows"] == 0
                    and s["bad_declarations"] == 0 and s["out_of_population"] == 0) else 1
        ok = got == want_exit
        if want_class == "out-of-population":
            ok = ok and s["out_of_population"] >= 1
        elif want_class == "out-only":
            ok = ok and s["out_of_population"] == 1 and s["accepted"] == 1
        elif want_class is not None:
            ok = ok and any(f["class"] == want_class for f in result["findings"])
        if name in expected_summaries:
            ok = (ok and s == expected_summaries[name]
                  and [f["class"] for f in result["findings"]] == expected_findings[name])
        if not ok:
            fail += 1
            print(f"APPEND_DEBT_SELFTEST_FAIL {name} exit={got} want={want_exit} "
                  f"summary={s} findings={result.get('findings', [])[:2]}")
    # Round-86: the summary must be reconcilable with the arm population and the failure
    # lines it accompanies. A dropped arm and a forged summary both used to pass green.
    print("APPEND_DEBT_SELFTEST_FAIL phantom-arm exit=1 want=0")
    print(f"APPEND_DEBT_SELFTEST_ARMS arms={len(cases)} expected={EXPECTED_ARMS} fail_lines={fail}")
    print(f"APPEND_DEBT_SELFTEST pass={len(cases) - fail} fail={fail} arms={len(cases)}")
    return 0 if fail == 0 and len(cases) == EXPECTED_ARMS else 1


# ---------------------------------------------------------------- main

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--round", type=int)
    parser.add_argument("--base")
    parser.add_argument("--to")
    parser.add_argument("--register", help=f"default: <repo>/{REGISTER}")
    parser.add_argument("--late", help=f"default: <repo>/{LATE}")
    parser.add_argument("--audit-json", help="read a retained audit JSON instead of executing it")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    repo = Path(args.repo).resolve()
    try:
        if args.audit_json:
            audit_text = Path(args.audit_json).read_text(encoding="utf-8")
        else:
            process = subprocess.run([sys.executable, str(repo / "tools/append-only-audit.py"),
                                      "--repo", str(repo), "--json"],
                                     capture_output=True, text=True, timeout=300)
            if process.returncode not in (0, 1):
                raise CouldNotEvaluate(f"audit exit={process.returncode}: {process.stderr.strip()}")
            audit_text = process.stdout
        data = json.loads(audit_text)
        validate_audit(data)
        to = data["to"]
        if args.round is None:
            raise CouldNotEvaluate("--round is required (the base is read from its frozen plan)")
        plan_text = show(repo, to, PLAN.format(round=args.round))
        if plan_text is None:
            raise CouldNotEvaluate(f"no frozen plan at {to}:{PLAN.format(round=args.round)}")
        base = resolve_base(plan_text, args.base)
        if not is_ancestor(repo, base, to) and base != to:
            raise CouldNotEvaluate(f"base {base} is not an ancestor of the audited revision {to}")

        register_text = (Path(args.register).read_text(encoding="utf-8") if args.register
                         else show(repo, to, REGISTER))
        if register_text is None:
            raise CouldNotEvaluate(f"no {REGISTER} at {to}")
        frozen_intro = None if args.register else introduction(repo, to, REGISTER)
        if not args.register and frozen_intro is None:
            raise CouldNotEvaluate(f"cannot resolve {REGISTER}'s introduction commit")
        late_text, late_intro, row_marks = load_late(repo, to, args.late)

        frozen_rows = parse_register(register_text, "frozen register")
        late_rows = parse_register(late_text, "late register")
        events = population(data)
        graded_keys = split(events, lambda commit: is_ancestor(repo, commit, base))
        cache = {}

        def frozen_precedes(commit):
            if frozen_intro is None:
                return True
            if ("f", commit) not in cache:
                cache[("f", commit)] = (commit != frozen_intro
                                        and is_ancestor(repo, commit, frozen_intro))
            return cache[("f", commit)]

        def strict_descendant(event_commit, row_commit):
            if ("d", event_commit, row_commit) not in cache:
                cache[("d", event_commit, row_commit)] = (event_commit != row_commit
                                                          and is_ancestor(repo, event_commit,
                                                                          row_commit))
            return cache[("d", event_commit, row_commit)]

        def subject_rounds(commit):
            if ("s", commit) not in cache:
                subject = git(repo, "log", "-1", "--format=%s", commit)
                match = re.match(r"^round-([0-9]+):", subject)
                cache[("s", commit)] = int(match.group(1)) if match is not None else None
            return cache[("s", commit)]

        result = grade(events, frozen_rows, late_rows, graded_keys=graded_keys,
                       frozen_precedes=frozen_precedes, late_intro=late_intro,
                       is_strict_descendant=strict_descendant, subject_rounds=subject_rounds,
                       row_intro=(row_marks.get if row_marks is not None else None))
        result["round"] = args.round
        result["base"] = base
        result["to"] = to
        result["summary"]["bad_declarations"] = data["summary"]["bad_declarations"]
    except (CouldNotEvaluate, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2) if args.json else render(result))
    return verdict(result)


if __name__ == "__main__":
    sys.exit(main())
