#!/usr/bin/env python3
"""round74-selfdesc-canon.py - round-74 C1 (calibration): the self-description
canon resolves the newest capability repertoire whatever heading form it wears.

Round 73's record disclosed R73-D1: the byte-frozen r42 reconciler's ``canon()``
matches only a BOLD ``**Capabilities - canonical list as of round <M>**`` heading
(a literal closing ``**``), so from round 72 on the record's unbolded
``## Capabilities - canonical list as of round 72`` canonical lists and
``### Capabilities demonstrated in round <M>`` demonstrated tables are invisible
to it.  This counter closes that hole by resolving the capability repertoire
from the newest capability table by round number regardless of heading markup,
while still reusing the byte-frozen r42 module's ``canon()`` and table parser
via import - never copied.

Predicate (frozen: plans/round-74-claims.md section C1; the same sentence is the
module's PREDICATE constant and the receipt label; the constant below carries it
verbatim on one line, byte-equal to the plan's blockquote minus its quote marks
and line breaks):

    `python3 tools/round74-selfdesc-canon.py --repo <lane>` prints one
    `SELFDESC_CANON_V2 canon_round=<N> canon_rows=<c> demonstrated=<d> total=<t> invisible=<i>`
    line and exits 0 only when `<lane>/SCORECARD.md` resolves its capability
    repertoire from the newest capability table by round number regardless of
    heading markup — bold `**Capabilities — canonical list as of round <M>**`,
    unbolded `## Capabilities — canonical list as of round <M>` and `###
    Capabilities demonstrated in round <M>` forms all count — and `invisible`
    names every capability a demonstrated-capabilities table newer than the
    newest bold canonical heading carries while the bold canon does not,
    requiring `invisible=0` so the record never relies on a form its own
    reconciler cannot see; it exits 1 naming each
    `SELFDESC_CANON_V2_FINDING invisible <round> <name>` and 2 when
    SCORECARD.md is unreadable or no capability table can be parsed.

Resolution rules (all three count as capability tables):

  * bold canonical headings  - a line carrying ``canonical list as of round N``
    where the heading text is bold (a surrounding ``**`` pair, or an ``## ``
    heading whose line carries the ``**`` pair).  This is the byte-frozen r42
    ``canon()`` population, reused via import.
  * unbolded canonical lists - an ``## Capabilities — canonical list as of round
    N`` heading without the ``**`` pair (the round-72 record form).
  * demonstrated tables      - a ``### Capabilities demonstrated in round N``
    heading.

`canon_round`/`canon_rows` are always the byte-frozen r42 ``canon()``'s bold
resolution - the form the lane's own reconciler can see - so the receipt shows
both what the record is and what the record's own reconciler sees.
`demonstrated` counts the distinct names carried only by capability tables whose
round is newer than `canon_round` (the names the bold canon cannot see).
`total` counts the distinct names the newest-by-round resolution reaches -
everything the bold canon names plus everything only newer tables carry, the
full repertoire the frozen r42 reconciler would see if its heading match were
markup-agnostic.  `invisible` is the subset of `demonstrated` the bold canon
does not name; `invisible=0` is the clean state.

Exit map: 0 clean (invisible=0); 1 findings (one SELFDESC_CANON_V2_FINDING line
per invisible capability, newest round first, names sorted within a round);
2 could-not-evaluate (CLI misuse, --repo is not a git repository, SCORECARD.md
missing/unreadable, no capability table parses).  A scored run never exits 2
for a finding: it names the findings and exits 1.  Non-goals: heading
visibility only - the reconciler's other arms (banner, planned, closure
pointer) are not re-graded here, and SCORECARD.md is never edited.

Selftest: `--selftest --repo R --work W` (W absent or empty, never inherited
TMPDIR) builds fixture arms under W and grades each: the frozen predicate arm
compares the PREDICATE constant against the plan's C1 blockquote read from
plans/round-74-claims.md in --repo; the kill fixture (newest additions only
under demonstrated round 73/74 tables, newest bold canon at round 71) must
exit 1 with invisible=4; the clean fixture (plus a bold round-74 canonical list
covering all seven names) must exit 0 with total=7; a bold-only record parses;
a demonstrated-table record with a stale demonstrated round beyond the bold
canon resolves that round; exit codes 2 (missing SCORECARD, no table) and CLI
misuse are each checked.  Prints `SELFDESC_CANON_V2_SELFTEST pass=<n> fail=0`;
exit 0 iff fail=0.

The r42 module's bytes stay unchanged and its own 5/5 selftest stays green; the
import is guarded so it never writes a __pycache__ next to the frozen file.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = Path(__file__).resolve()
LANE = TOOL.parent.parent
PLAN_NAME = "plans/round-74-claims.md"
SCORECARD_NAME = "SCORECARD.md"
MODULE_NAME = "round74-selfdesc-canon.py"

PREDICATE = "`python3 tools/round74-selfdesc-canon.py --repo <lane>` prints one `SELFDESC_CANON_V2 canon_round=<N> canon_rows=<c> demonstrated=<d> total=<t> invisible=<i>` line and exits 0 only when `<lane>/SCORECARD.md` resolves its capability repertoire from the newest capability table by round number regardless of heading markup — bold `**Capabilities — canonical list as of round <M>**`, unbolded `## Capabilities — canonical list as of round <M>` and `### Capabilities demonstrated in round <M>` forms all count — and `invisible` names every capability a demonstrated-capabilities table newer than the newest bold canonical heading carries while the bold canon does not, requiring `invisible=0` so the record never relies on a form its own reconciler cannot see; it exits 1 naming each `SELFDESC_CANON_V2_FINDING invisible <round> <name>` and 2 when SCORECARD.md is unreadable or no capability table can be parsed."

SUMMARY_LABEL = "SELFDESC_CANON_V2"
FINDING_LABEL = "SELFDESC_CANON_V2_FINDING"
SELFTEST_LABEL = "SELFDESC_CANON_V2_SELFTEST"

# The r42 reconciler's bold-canonical heading match (a literal closing "**").
BOLD_CANON_RE = re.compile(r"canonical list as of round\s+(\d+)\*\*", re.I)
# Any canonical-list heading, bold or not.
CANON_HEADING_RE = re.compile(r"canonical list as of round\s+(\d+)", re.I)
# A demonstrated-capabilities heading.
DEMO_HEADING_RE = re.compile(r"Capabilities demonstrated in round\s+(\d+)", re.I)
# A line is a heading (markdown) when it starts with '#' or carries the bold pair.
_HEADING_RE = re.compile(r"^\s*#|\*\*")

_R42 = None


class CanonError(RuntimeError):
    """A could-not-evaluate condition (exit 2), never a finding."""


def _load_r42() -> object:
    """Load tools/round42-selfdesc-reconcile.py once (imported, never copied)."""
    global _R42
    if _R42 is not None:
        return _R42
    path = Path(__file__).resolve().parent / "round42-selfdesc-reconcile.py"
    if not path.is_file():
        raise CanonError("byte-frozen r42 module {} is absent".format(path))
    spec = importlib.util.spec_from_file_location("round74_inherited_r42_selfdesc_reconcile",
                                                  str(path))
    if spec is None or spec.loader is None:
        raise CanonError("cannot build an import spec for {}".format(path))
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    except OSError as exc:
        raise CanonError("cannot import r42 module {}: {}".format(path, exc)) from exc
    finally:
        sys.dont_write_bytecode = previous
    for name in ("canon", "table_rows"):
        if not callable(getattr(module, name, None)):
            raise CanonError("inherited r42 module {} lacks {}".format(path, name))
    _R42 = module
    return module


def _git(repo, *args):
    argv = ["git", "-C", str(repo), *args]
    try:
        return subprocess.run(argv, capture_output=True, text=True)
    except OSError as exc:
        raise CanonError("git {}: {}".format(" ".join(args), exc)) from exc


def resolve_repo(repo: str) -> Path:
    """The graded surface is <repo>/SCORECARD.md; --repo itself only has to be
    a readable directory (a git toplevel when it is a git repository)."""
    path = Path(repo).expanduser()
    if not path.is_dir():
        raise CanonError("--repo {!r} is not a directory".format(repo))
    proc = _git(path, "rev-parse", "--show-toplevel")
    if proc.returncode != 0 and "not a git repository" not in proc.stderr:
        raise CanonError("--repo {!r} git probe failed: {}".format(
            repo, proc.stderr.strip()))
    return path


def read_scorecard(repo: Path) -> str:
    scorecard = repo / SCORECARD_NAME
    if not scorecard.is_file():
        raise CanonError("{} missing".format(scorecard))
    try:
        return scorecard.read_bytes().decode("utf-8").replace("\r\n", "\n")
    except OSError as exc:
        raise CanonError("cannot read {}: {}".format(scorecard, exc)) from exc
    except UnicodeDecodeError as exc:
        raise CanonError("{} is not UTF-8: {}".format(scorecard, exc)) from exc


def _names_below(lines, index, mod):
    return [row[0] for row in mod.table_rows(lines[index + 1:])]


def capability_tables(text: str, mod) -> list:
    """Every capability table as (round, line_index, kind) with kind in
    {'bold-canon', 'canon', 'demo'}; a demonstrated table wins over a
    canonical table at the same round, so the demonstrated additions are
    never hidden by a same-round canonical list."""
    tables = []
    lines = text.split("\n")
    per_round: dict = {}
    for i, line in enumerate(lines):
        bold = BOLD_CANON_RE.search(line)
        canon = CANON_HEADING_RE.search(line)
        demo = DEMO_HEADING_RE.search(line)
        if bold:
            kind = "bold-canon"
            round_no = int(bold.group(1))
        elif canon and _HEADING_RE.search(line):
            kind = "canon"
            round_no = int(canon.group(1))
        elif demo and line.lstrip().startswith("#"):
            kind = "demo"
            round_no = int(demo.group(1))
        else:
            continue
        entry = (round_no, i, kind)
        previous = per_round.get(round_no)
        if previous is None:
            per_round[round_no] = entry
        elif previous[2] == "demo":
            continue
        elif kind == "demo":
            per_round[round_no] = entry
        elif previous[2] == "canon":
            continue
        elif kind == "canon":
            per_round[round_no] = entry
    tables = sorted(per_round.values(), key=lambda t: t[0])
    return tables


def resolve(text: str, mod) -> dict:
    """The v2 resolution over one SCORECARD text (never raises CanonError)."""
    lines = text.split("\n")
    canon_round, canon_rows = mod.canon(text)
    canon_names = [row[0] for row in canon_rows]
    tables = capability_tables(text, mod)
    if not tables:
        raise CanonError("no capability table can be parsed from SCORECARD.md")
    newest_round = tables[-1][0]
    newest_names: set = set()
    for round_no, index, _kind in tables:
        if round_no == newest_round:
            newest_names.update(_names_below(lines, index, mod))
    demonstrated: set = set()
    for round_no, index, _kind in tables:
        if round_no > canon_round:
            demonstrated.update(_names_below(lines, index, mod))
    invisible = sorted(demonstrated - set(canon_names))
    # The repertoire the newest-by-round resolution reaches: everything the
    # record's own reconciler can see (the bold canon) plus everything only
    # newer tables carry.
    total = set(canon_names) | demonstrated
    return {
        "canon_round": canon_round,
        "canon_rows": len(canon_rows),
        "demonstrated": len(demonstrated),
        "total": len(total),
        "invisible": invisible,
        "newest_round": newest_round,
        "demonstrated_names": demonstrated,
        "canon_names": canon_names,
    }


def grade(repo: Path) -> dict:
    mod = _load_r42()
    text = read_scorecard(repo)
    return resolve(text, mod)


def emit(document: dict) -> None:
    print("{} canon_round={} canon_rows={} demonstrated={} total={} invisible={}".format(
        SUMMARY_LABEL, document["canon_round"], document["canon_rows"],
        document["demonstrated"], document["total"], len(document["invisible"])))
    for round_no, index, _kind in document["findings"]:
        print("{} invisible {} {}".format(FINDING_LABEL, round_no, index))


def run(repo_path: str) -> dict:
    repo = resolve_repo(repo_path)
    mod = _load_r42()
    text = read_scorecard(repo)
    document = resolve(text, mod)
    lines = text.split("\n")
    # Name each invisible capability with the round of the newest table that
    # carries it (a demonstrated table, by construction).
    carried: dict = {}
    for round_no, index, _kind in capability_tables(text, mod):
        if round_no <= document["canon_round"]:
            continue
        for name in _names_below(lines, index, mod):
            if name in document["invisible"] and name not in carried:
                carried[name] = round_no
    findings = [(carried.get(name, document["newest_round"]), name)
                for name in sorted(document["invisible"])]
    document["findings"] = findings
    for round_no, name in findings:
        print("{} invisible {} {}".format(FINDING_LABEL, round_no, name))
    print("{} canon_round={} canon_rows={} demonstrated={} total={} invisible={}".format(
        SUMMARY_LABEL, document["canon_round"], document["canon_rows"],
        document["demonstrated"], document["total"], len(document["invisible"])))
    return document


def _plan_c1_predicate(text: str) -> str:
    """The plan's C1 blockquote, joined onto one line; '' when no blockquote
    names this module."""
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        stripped = line.lstrip()
        if (stripped.startswith(">")
                and "`python3 tools/round74-selfdesc-canon.py" in stripped):
            start = index
            break
    if start is None:
        return ""
    body = []
    index = start
    while index < len(lines) and lines[index].lstrip().startswith(">"):
        stripped = lines[index].lstrip()[1:]
        if stripped.startswith(" "):
            stripped = stripped[1:]
        body.append(stripped)
        index += 1
    return " ".join(body)


def _plan_predicate_at_tip(repo: Path, tip: str) -> str:
    proc = _git(repo, "cat-file", "-p", "{}:{}".format(tip, PLAN_NAME))
    if proc.returncode != 0:
        raise CanonError("{} unreadable at {}: {}".format(PLAN_NAME, tip, proc.stderr.strip()))
    return _plan_c1_predicate(proc.stdout)


def _fixture(root: Path, name: str) -> Path:
    fixture = root / name
    fixture.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(["git", "-C", str(fixture), "init", "-q"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise CanonError("git init {}: {}".format(fixture, proc.stderr.strip()))
    proc = subprocess.run(["git", "-C", str(fixture), "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True)
    if proc.returncode != 0 or os.path.realpath(proc.stdout.strip()) != os.path.realpath(fixture):
        raise CanonError("fixture {} is not its own toplevel".format(fixture))
    return fixture


def _commit(fixture: Path, message: str) -> None:
    ident = ["-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
             "-c", "commit.gpgsign=false"]
    for args in (["add", "-A"], ["commit", "-q", "-m", message]):
        proc = subprocess.run(["git", "-C", str(fixture), *ident, *args],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            raise CanonError("git {} in {}: {}".format(" ".join(args), fixture,
                                                       proc.stderr.strip()))


BOLD71 = """**Capabilities — canonical list as of round 71**

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curates where kama learns | `corpus/SOURCES.md` | 10 |
| pin-watch | Lists upstream release tags per pinned engine | `tools/pin-watch.py` | 41 |
| digest-ledger | Classifies every cited full SHA-256 | `tools/digest-ledger.py` | 42 |
"""

DEMO73 = """### Capabilities demonstrated in round 73

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| round-scope-cases | Grades linked-worktree and submodule scope cases | `tools/round73-round-scope-cases.py` | 73 |
| receipt-claim-binding | Rejects a three-token tip claim naming another revision | `tools/round73-receipt-claim-binding.py` | 73 |
"""

DEMO74 = """### Capabilities demonstrated in round 74

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| province-host-drift | Compares the recorded host triple with the live triple | `tools/round73-province-host-drift.py` | 73 |
| live-ollama-lifecycle | Starts the pinned Ollama binary on a loopback port | `tools/kama-ollama-live.py` | 61 |
"""

BOLD74 = """**Capabilities — canonical list as of round 74**

Same four columns; supersedes the round-71 list.

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curates where kama learns | `corpus/SOURCES.md` | 10 |
| pin-watch | Lists upstream release tags per pinned engine | `tools/pin-watch.py` | 41 |
| digest-ledger | Classifies every cited full SHA-256 | `tools/digest-ledger.py` | 42 |
| round-scope-cases | Grades linked-worktree and submodule scope cases | `tools/round73-round-scope-cases.py` | 73 |
| receipt-claim-binding | Rejects a three-token tip claim naming another revision | `tools/round73-receipt-claim-binding.py` | 73 |
| province-host-drift | Compares the recorded host triple with the live triple | `tools/round73-province-host-drift.py` | 73 |
| live-ollama-lifecycle | Starts the pinned Ollama binary on a loopback port | `tools/kama-ollama-live.py` | 61 |
"""

# The kill fixture: identical record to .ufo/waves/round-74/controls/build-survivors.py
C1_HEAD = "# kama-shokunin — SCORECARD\n\nfixture record\n\n## Capabilities\n\nmirror\n\n"
KILL_RECORD = C1_HEAD + BOLD71 + "\n" + DEMO73 + "\n" + DEMO74
CLEAN_RECORD = KILL_RECORD + "\n" + BOLD74
DEMO_ONLY_RECORD = C1_HEAD + DEMO73
DEMO_STALE_RECORD = C1_HEAD + BOLD71 + "\n" + DEMO73.replace("round 73", "round 98")


def _run_cli(argv):
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run([sys.executable, str(TOOL), *argv],
                          capture_output=True, text=True, env=env)


def _record(outcomes, name: str, ok: bool, detail: str = "") -> None:
    print("SELFDESC_CANON_V2_ARM {} {}".format(name, "ok" if ok else "FAIL {}".format(detail)))
    outcomes.append((name, ok))


def run_selftest(repo: Path, work: Path) -> int:
    outcomes: list = []
    fixtures = work / "fixtures"
    fixtures.mkdir(parents=True, exist_ok=True)

    def build(name: str, record: str) -> Path:
        fixture = _fixture(fixtures, name)
        (fixture / SCORECARD_NAME).write_text(record, encoding="utf-8")
        _commit(fixture, "record")
        return fixture

    def arm(name: str, fixture: Path, want_exit: int, must_out=(), must_not=()):
        proc = _run_cli(["--repo", str(fixture)])
        out = proc.stdout + proc.stderr
        problems = []
        if proc.returncode != want_exit:
            problems.append("exit={} want {}".format(proc.returncode, want_exit))
        for token in must_out:
            if token not in out:
                problems.append("missing {!r}".format(token))
        for token in must_not:
            if token in out:
                problems.append("unexpected {!r}".format(token))
        _record(outcomes, name, not problems, "; ".join(problems))
        if problems:
            for line in out.splitlines()[:20]:
                print("    out: {}".format(line))
        return proc

    # arm: the predicate sentence is one line, byte-equal to the plan's C1
    # blockquote read from plans/round-74-claims.md in --repo.
    plan_text = (repo / PLAN_NAME).read_text(encoding="utf-8")
    frozen = _plan_c1_predicate(plan_text)
    problems = []
    if "\n" in PREDICATE:
        problems.append("PREDICATE is not one line")
    if frozen != PREDICATE:
        problems.append("PREDICATE differs from the plan blockquote (len {} vs {})".format(
            len(PREDICATE), len(frozen)))
    _record(outcomes, "predicate", not problems, "; ".join(problems))

    # arm: the plan's blockquote at master in --repo parses and matches.
    try:
        tip_frozen = _plan_predicate_at_tip(repo, "master")
    except CanonError as exc:
        _record(outcomes, "predicate-at-tip", False, str(exc))
    else:
        _record(outcomes, "predicate-at-tip", tip_frozen == PREDICATE,
                "master copy len {}".format(len(tip_frozen)))

    # arm: the kill fixture — demonstrated 73/74 additions under unbolded
    # headings only; the v2 counter must see all four and exit 1.  Each
    # invisible capability is named at the round of the newest table that
    # carries it.
    kill = build("kill", KILL_RECORD)
    proc = arm(
        "kill-invisible", kill, 1,
        must_out=[
            "SELFDESC_CANON_V2 canon_round=71 canon_rows=3 demonstrated=4 total=7 invisible=4",
            "SELFDESC_CANON_V2_FINDING invisible 74 live-ollama-lifecycle",
            "SELFDESC_CANON_V2_FINDING invisible 74 province-host-drift",
            "SELFDESC_CANON_V2_FINDING invisible 73 receipt-claim-binding",
            "SELFDESC_CANON_V2_FINDING invisible 73 round-scope-cases",
        ],
    )

    # arm: the clean fixture — a bold round-74 canonical list covering all
    # seven names; exit 0 with total=7 invisible=0.
    clean = build("clean", CLEAN_RECORD)
    arm("clean-bold-covers", clean, 0,
        must_out=["SELFDESC_CANON_V2 canon_round=74 canon_rows=7 demonstrated=0 total=7 invisible=0"])

    # arm: a bold-only record resolves exactly the r42 canon() resolution.
    bold_only = build("boldonly", C1_HEAD + BOLD71)
    arm("bold-only", bold_only, 0,
        must_out=["SELFDESC_CANON_V2 canon_round=71 canon_rows=3 demonstrated=0 total=3 invisible=0"])

    # arm: a demonstrated table round newer than the bold canon (stale round
    # number in a demonstrated heading) resolves that round and its names.
    stale = build("demostale", DEMO_STALE_RECORD)
    arm("demo-newer-round", stale, 1,
        must_out=["SELFDESC_CANON_V2 canon_round=71 canon_rows=3 demonstrated=2 total=5 invisible=2"])

    # arm: could-not-evaluate — SCORECARD.md missing.
    empty = _fixture(fixtures, "empty")
    proc = _run_cli(["--repo", str(empty)])
    ok = proc.returncode == 2 and "could-not-evaluate" in (proc.stdout + proc.stderr)
    _record(outcomes, "scorecard-missing", ok,
            "exit={}".format(proc.returncode))
    if not ok:
        print("    out: " + (proc.stdout + proc.stderr).strip()[:300])

    # arm: could-not-evaluate — SCORECARD.md carries no capability table.
    notables = _fixture(fixtures, "notables")
    (notables / SCORECARD_NAME).write_text("# nothing here\n", encoding="utf-8")
    _commit(notables, "record")
    proc = _run_cli(["--repo", str(notables)])
    out = proc.stdout + proc.stderr
    ok = proc.returncode == 2 and "could-not-evaluate" in out and "no capability table" in out
    _record(outcomes, "no-capability-table", ok, "exit={}".format(proc.returncode))
    if not ok:
        print("    out: " + out.strip()[:300])

    # arm: CLI misuse — no --repo, and --repo naming a non-directory path.
    proc = _run_cli([])
    ok = proc.returncode == 2
    _record(outcomes, "cli-misuse", ok, "exit={}".format(proc.returncode))
    notdir = work / "notdir"
    notdir.write_text("x", encoding="utf-8")
    proc = _run_cli(["--repo", str(notdir)])
    out = proc.stdout + proc.stderr
    ok = proc.returncode == 2 and "not a directory" in out
    _record(outcomes, "repo-not-directory", ok, "exit={}".format(proc.returncode))
    if not ok:
        print("    out: " + out.strip()[:300])

    # arm: --work must be absent or empty (never inherited TMPDIR state).
    dirty = work / "dirtywork"
    dirty.mkdir(parents=True, exist_ok=True)
    (dirty / "leftover").write_text("x", encoding="utf-8")
    proc = _run_cli(["--selftest", "--repo", str(repo), "--work", str(dirty)])
    out = proc.stdout + proc.stderr
    ok = proc.returncode == 2
    _record(outcomes, "work-not-empty", ok, "exit={}".format(proc.returncode))
    if not ok:
        print("    out: " + out.strip()[:300])

    passed = sum(1 for _, ok in outcomes if ok)
    failed = len(outcomes) - passed
    print("{} pass={} fail={}".format(SELFTEST_LABEL, passed, failed))
    if failed:
        return 1
    shutil.rmtree(fixtures, ignore_errors=True)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Round-74 C1 self-description canon v2: resolve the capability "
                    "repertoire from the newest capability table by round number "
                    "regardless of heading markup (bold canonical, unbolded "
                    "canonical, demonstrated), reusing the byte-frozen r42 "
                    "reconciler's canon()/table parser via import.")
    ap.add_argument("--repo", default=".",
                    help="lane repository to grade (default: current directory)")
    ap.add_argument("--selftest", action="store_true",
                    help="run the fixture selftest (needs --repo and --work)")
    ap.add_argument("--work", default=None,
                    help="selftest work root (absent or empty; never inherited TMPDIR)")
    args = ap.parse_args(argv)

    if args.selftest:
        repo = Path(args.repo).expanduser().resolve()
        if not repo.is_dir():
            print("{} could-not-evaluate: --repo {!r} is not a directory".format(
                SELFTEST_LABEL, args.repo))
            return 2
        if not args.work:
            work = Path(tempfile.mkdtemp(prefix="selfdesc-canon-v2-selftest-"))
        else:
            work = Path(args.work).expanduser().resolve()
            if work.exists() and any(work.iterdir()):
                print("{} could-not-evaluate: --work {} is not empty".format(
                    SELFTEST_LABEL, work))
                return 2
            work.mkdir(parents=True, exist_ok=True)
        try:
            return run_selftest(repo, work)
        except CanonError as exc:
            print("{} could-not-evaluate: {}".format(SELFTEST_LABEL, exc))
            return 2
        finally:
            shutil.rmtree(work, ignore_errors=True)

    try:
        document = run(args.repo)
    except CanonError as exc:
        print("{} could-not-evaluate: {}".format(SUMMARY_LABEL, exc))
        return 2
    return 0 if not document["invisible"] else 1


if __name__ == "__main__":
    sys.exit(main())
