#!/usr/bin/env python3
"""gate-registry-check.py -- registry-row completeness gate for the kama lane.

Proposed replacement for the occurrence-only v1 of this tool (round-28 routed
defect 4: `corpus/lessons/round-28-verifier-spotcheck.md:233-236`).

v1 asked only "does this path occur anywhere in SKILL.md" and reported
`unregistered <path>` (occurrence only, lines 129-131 of v1). It had no
fixture self-test and never printed the revision it measured. This version
asks the question PROTOCOL §Gate standard, Registry asks: does the lane's
registry home carry a FULL row for every instrument the lane tracks? The row
fields there are `name`, `gate|probe`, entry command, verdict map (code ->
class), self-test command and spelling, pinned-value path, write scope,
owner.

Contract:

  * Registry home is this lane's `SKILL.md` (PROTOCOL §Gate standard,
    Registry: "a child lane's *registry home* is its own `SKILL.md`"). Every
    `## ` section of that file is read, so every `## Round-NN ... instrument
    registry` section and the `## Local gate/probe registry` home table are
    parsed. Only registry-shaped tables are used: a table whose header has a
    `Name` column, a `Kind / entry command` column, a `Verdict map` or
    `Exit map` column and a `Self-test` column. Other SKILL.md tables
    (decision tables, error-signature tables, dated prose tables) are not
    registry tables and are ignored.
  * Population of instruments: every tracked path matching
    `^\\.ufo/waves/round-[^/]+/count-[^/]+\\.py$` (round counters) plus every
    tracked `tools/*.py` and `tools/*.sh` (lane tools).
  * Coverage rule: an instrument is covered iff some registry row names its
    repo-relative path in the row's `Kind / entry command` cell, in the
    row's `Name` cell, or in the row's `Self-test` cell (a fixture named by
    another row's self-test is registered by that row). A prose mention in
    SKILL.md is NOT coverage -- that is exactly the v1 defect, and it is why
    `.ufo/waves/round-17/count-verdicts.py` (named in a prose paragraph) is
    a finding while a real row is not. An instrument with no registry row
    prints `finding no-registry-row:<path>`.
  * Row rules (the new part). A row that names an instrument is checked for:
      - path        : the row names the instrument's repo-relative path
                      (satisfied by the match that made the row visible)
      - kind        : the kind phrase is `gate` or `probe` (PROTOCOL:
                      "Row fields: name, `gate|probe`, ..."). `measurement:`,
                      `capability:` and a missing kind are findings. A
                      qualifier after the kind word is allowed ("gate on a
                      gate:", "gate + persistence:").
      - entry       : the kind cell carries an interpreter-invoked command
                      (`python3 ...`, `bash ...`, `/usr/bin/python3 ...`).
      - verdict map : the `Verdict map`/`Exit map` cell is non-empty and
                      names at least one exit code (`0`, `1`, `2`, ...), or
                      explicitly defers to another row of the same table.
      - self-test   : the `Self-test` cell names a self-test spelling
                      (`--selftest`, `--self-test`, `run_selftest`,
                      `self-test`), or a fixture spelling (the word
                      `fixture`, `expected.json`, `SHA256SUMS`,
                      `test-snapshot.sh`, or a quoted artifact path), or
                      states the absence explicitly (`none`, `non-runnable`,
                      "no ... self-test").
    A row whose kind cell reads `retired` or `non-runnable` is exempt from
    the kind, entry and self-test rules -- that is the lane's own retirement
    spelling (round-28 spot-check item 5: "Give the retired round-27 row a
    kind and an entry command, or mark it explicitly as non-runnable") --
    but it still owes a verdict map. The marker must sit in the kind cell:
    a `none (retired)` write-scope cell does not retire a row, and a prose
    word "retired" in a name cell does not either.

Output:

    rev <full 40-hex hash>      the revision the verdict was measured at
    finding <finding-id>        one line per finding, in document order
    sections S rows R findings F

Finding ids are stable and machine-readable:

    <class>:<subject>              for an instrument-wide finding
    <class>:<subject>#<row-label>  for a row-specific finding (the row's
                                   `Name` cell, so two rows naming the same
                                   instrument get distinct ids)

Classes: `no-registry-row`, `kind-not-conforming`, `entry-command-missing`,
`verdict-map-missing`, `selftest-missing`.

Exit codes:

    0  clean: no finding
    1  failed: at least one finding
    2  could-not-evaluate (not a git repository, unreadable revision,
       missing SKILL.md, git failure/timeout, or a tampered self-test
       snapshot)

Self-test:

    `--selftest` runs the committed fixtures under `fixtures/` (next to this
    file) and compares the finding ids of every fixture case with the
    expected ids in `fixtures/expected.json`. The expected ids are a
    committed baseline, not a recomputation: `expected.json` pins the
    sha256 of every fixture input file and the tool verifies those digests
    before comparing, so an edited fixture is reported `snapshot_tampered`
    (could-not-evaluate, exit 2) instead of a compared verdict. Any
    difference in the finding-id set is a self-test failure (exit 1).

Read-only: the tool issues only `git rev-parse`, `git ls-tree`, `git ls-files`
and `git show`. It never writes to the repository, never stages and never
checks out. The self-test reads committed fixtures only -- no temporary
tree, no network, no live-tree write.

Usage:

    gate-registry-check.py [--repo DIR] [--rev REV | --worktree]
                            [--selftest] [--fixtures DIR]

    --repo DIR     repository to evaluate (default: current directory)
    --rev REV      revision to evaluate (default: HEAD)
    --worktree     evaluate the index plus the SKILL.md on disk instead of a
                   committed tree
    --selftest     run the committed fixtures and exit
    --fixtures DIR fixture directory. Resolution order when omitted:
                   $GATE_REGISTRY_FIXTURES, `<script dir>/fixtures`,
                   `<repo root>/tests/gate-registry-check/fixtures`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

COUNTER_RE = re.compile(r"^\.ufo/waves/round-[^/]+/count-[^/]+\.py$")
TOOL_RE = re.compile(r"^tools/[^/]+\.(py|sh)$")
SKILL_PATH = "SKILL.md"

EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_ERROR = 2

GIT_TIMEOUT = 30

# ---------------------------------------------------------------------------
# Markdown table parsing
# ---------------------------------------------------------------------------

H2_RE = re.compile(r"^##\s+(.*\S)\s*$")
TABLE_ROW_RE = re.compile(r"^\s*\|")
SEPARATOR_CELL_RE = re.compile(r"^:?-{2,}:?$")

# A repo-relative path that can name an instrument.
PATH_RE = re.compile(
    r"(?<![\w./-])((?:\.ufo|tools|tests|registry|corpus)/[A-Za-z0-9_.\-/]*"
    r"[A-Za-z0-9_-]\.(?:py|sh|json|tsv))"
)


def split_row(line: str) -> list[str]:
    """Split a markdown table row on unescaped pipes."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    cells = re.split(r"(?<!\\)\|", body)
    return [c.replace("\\|", "|").strip() for c in cells]


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(SEPARATOR_CELL_RE.match(c) for c in cells if c != "")


def parse_tables(text: str) -> list[dict]:
    """Return every markdown table in `text` as {"header": [...], "rows": [...]}."""
    lines = text.split("\n")
    tables: list[dict] = []
    i = 0
    while i < len(lines):
        if TABLE_ROW_RE.match(lines[i]):
            j = i
            block: list[list[str]] = []
            while j < len(lines) and TABLE_ROW_RE.match(lines[j]):
                block.append(split_row(lines[j]))
                j += 1
            if len(block) >= 2 and is_separator(block[1]):
                tables.append({"header": block[0], "rows": block[2:]})
            i = j
        else:
            i += 1
    return tables


def column_index(header: list[str], *needles: str) -> int:
    for n in needles:
        for idx, cell in enumerate(header):
            if n.lower() in cell.lower():
                return idx
    return -1


def is_registry_table(header: list[str]) -> bool:
    return (
        column_index(header, "name") >= 0
        and column_index(header, "kind") >= 0
        and column_index(header, "verdict map", "exit map") >= 0
        and column_index(header, "self-test") >= 0
    )


# ---------------------------------------------------------------------------
# Row rules
# ---------------------------------------------------------------------------

KIND_RE = re.compile(r"^\s*\**\s*([A-Za-z][A-Za-z0-9 +_-]*?)\s*:")
INTERPRETER_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:python3(?:\.[0-9]+)?|python|bash|sh|zsh)(?![A-Za-z0-9_-])"
)
EXIT_CODE_RE = re.compile(r"(?<![0-9A-Za-z_])[0-9](?![0-9A-Za-z_])")
DEFER_RE = re.compile(r"\bas (?:the|above|previous)\b[^.]{0,60}\brow\b", re.IGNORECASE)
SELF_TEST_SPELLING_RE = re.compile(
    r"--self-?test|\brun_selftest\b|\bself-?test\b",
    re.IGNORECASE,
)
FIXTURE_SPELLING_RE = re.compile(
    r"\bfixtures?\b|\bexpected\.json\b|\bSHA256SUMS\b|\btest-snapshot\.sh\b"
    r"|`[^`]*\.(?:json|sh|tsv)`",
    re.IGNORECASE,
)
SELF_TEST_ABSENT_RE = re.compile(
    r"\bnone\b|non-?runnable|\bno\b[^.|]{0,40}\bself-?test\b"
    r"|\bno\b[^.|]{0,30}\bfixture\b",
    re.IGNORECASE,
)
RETIRED_KIND_RE = re.compile(r"^(?:retired|non-?runnable)\b", re.IGNORECASE)
RETIRED_ROW_RE = re.compile(r"\bretired\b|non-?runnable|\bdo not use\b", re.IGNORECASE)


def is_instrument(path: str) -> bool:
    return bool(COUNTER_RE.match(path) or TOOL_RE.match(path))


def find_path(text: str) -> str | None:
    m = PATH_RE.search(text)
    return m.group(1) if m else None


def kind_phrase(cell: str) -> str | None:
    m = KIND_RE.match(cell)
    return m.group(1).strip() if m else None


def kind_is_gate_or_probe(phrase: str | None) -> bool:
    if not phrase:
        return False
    return bool(re.match(r"^(gate|probe)\b", phrase.lower()))


def selftest_ok(cell: str) -> bool:
    return bool(
        SELF_TEST_SPELLING_RE.search(cell)
        or FIXTURE_SPELLING_RE.search(cell)
        or SELF_TEST_ABSENT_RE.search(cell)
    )


def row_label(name_cell: str, index: int) -> str:
    label = re.sub(r"\s+", " ", name_cell).strip()
    label = label.replace("|", "/")
    return label[:60] if label else f"row{index}"


def check_row(
    cells: list[str], header: list[str], index: int
) -> tuple[str | None, list[tuple[str, str]]]:
    """Return (subject, findings) for one registry row.

    `subject` is the instrument path the row names, or None when the row
    names no path at all. A row that names no path carries no finding:
    there is no instrument to be wrong about.
    """
    kind_idx = column_index(header, "kind")
    verdict_idx = column_index(header, "verdict map", "exit map")
    selftest_idx = column_index(header, "self-test")
    name_idx = column_index(header, "name")

    kind_cell = cells[kind_idx] if 0 <= kind_idx < len(cells) else ""
    verdict_cell = cells[verdict_idx] if 0 <= verdict_idx < len(cells) else ""
    selftest_cell = cells[selftest_idx] if 0 <= selftest_idx < len(cells) else ""
    name_cell = cells[name_idx] if 0 <= name_idx < len(cells) else ""

    named = [p for p in (find_path(kind_cell), find_path(name_cell)) if p]
    subject = named[0] if named else None
    if subject is None:
        return None, []
    label = row_label(name_cell, index)
    subject_key = subject

    findings: list[tuple[str, str]] = []
    phrase = kind_phrase(kind_cell)
    retired_in_kind = bool(phrase and RETIRED_KIND_RE.match(phrase))
    # A retirement statement anywhere in the row (name, self-test or write
    # scope cell) marks the row as retired. It waives the self-test rule
    # only; the kind and entry-command rules are waived only when the
    # retirement marker sits in the kind cell, because that is where a kind
    # would otherwise sit.
    row_text = " ".join(cells)
    retired_anywhere = bool(RETIRED_ROW_RE.search(row_text))

    if not retired_in_kind:
        if not kind_is_gate_or_probe(phrase):
            findings.append(("kind-not-conforming", f"{subject_key}#{label}"))
        if not INTERPRETER_RE.search(kind_cell):
            findings.append(("entry-command-missing", f"{subject_key}#{label}"))
        if not selftest_ok(selftest_cell) and not retired_anywhere:
            findings.append(("selftest-missing", f"{subject_key}#{label}"))
        if not verdict_cell.strip() or (
            not EXIT_CODE_RE.search(verdict_cell) and not DEFER_RE.search(verdict_cell)
        ):
            findings.append(("verdict-map-missing", f"{subject_key}#{label}"))

    return subject, findings


# ---------------------------------------------------------------------------
# Evaluation over a SKILL.md text
# ---------------------------------------------------------------------------


def evaluate_text(
    text: str, population: list[str]
) -> tuple[list[tuple[str, str]], int, int]:
    """Return (findings, tables_parsed, rows_parsed) for a SKILL.md text."""
    findings: list[tuple[str, str]] = []
    tables = 0
    rows = 0
    covered: set[str] = set()

    lines = text.split("\n")
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if H2_RE.match(line):
            if current:
                blocks.append(current)
            current = []
            continue
        current.append(line)
    if current:
        blocks.append(current)

    for body in blocks:
        for table in parse_tables("\n".join(body)):
            header = table["header"]
            if not is_registry_table(header):
                continue
            tables += 1
            kind_idx = column_index(header, "kind")
            name_idx = column_index(header, "name")
            selftest_idx = column_index(header, "self-test")
            for index, cells in enumerate(table["rows"], 1):
                if not any(c.strip() for c in cells):
                    continue
                rows += 1
                subject, row_findings = check_row(cells, header, index)
                if subject is not None:
                    covered.add(subject)
                for cell_idx in (kind_idx, name_idx, selftest_idx):
                    if 0 <= cell_idx < len(cells):
                        named = find_path(cells[cell_idx])
                        if named is not None:
                            covered.add(named)
                findings.extend(row_findings)

    for path in population:
        if path not in covered:
            findings.append(("no-registry-row", path))

    return findings, tables, rows


# ---------------------------------------------------------------------------
# Git surface
# ---------------------------------------------------------------------------


def run_git(root: str, args: list[str]) -> tuple[int, bytes, str]:
    try:
        p = subprocess.run(
            ["git", "-C", root, *args],
            capture_output=True,
            timeout=GIT_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, b"", str(e)
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace").strip()


def git_root(repo: str) -> tuple[str | None, str]:
    rc, out, err = run_git(repo, ["rev-parse", "--show-toplevel"])
    if rc != 0:
        return None, f"not a git working tree at {repo!r}: {err or f'rc={rc}'}"
    root = out.decode("utf-8", "surrogateescape").strip()
    if not root:
        return None, f"empty repository root for {repo!r}"
    return root, ""


def resolve_rev(root: str, rev: str) -> tuple[str | None, str]:
    rc, out, err = run_git(root, ["rev-parse", "--verify", f"{rev}^{{commit}}"])
    if rc != 0:
        return None, f"cannot resolve revision {rev!r}: {err or f'rc={rc}'}"
    full = out.decode("ascii", "replace").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", full):
        return None, f"revision {rev!r} did not resolve to a full hash: {full!r}"
    return full, ""


def tracked_paths(root: str, rev: str | None) -> tuple[list[str] | None, str]:
    if rev is None:
        rc, out, err = run_git(root, ["ls-files", "-z"])
    else:
        rc, out, err = run_git(root, ["ls-tree", "-r", "-z", "--name-only", "--full-tree", rev])
    if rc != 0:
        what = "git ls-files" if rev is None else f"git ls-tree {rev}"
        return None, f"{what} failed: {err or f'rc={rc}'}"
    paths = [p.decode("utf-8", "surrogateescape") for p in out.split(b"\0") if p]
    return sorted(p for p in paths if is_instrument(p)), ""


def skill_text(root: str, rev: str | None) -> tuple[str | None, str]:
    if rev is None:
        path = Path(root) / SKILL_PATH
        try:
            return path.read_text(encoding="utf-8", errors="surrogateescape"), ""
        except OSError as e:
            return None, f"cannot read {path}: {e}"
    rc, out, err = run_git(root, ["show", f"{rev}:{SKILL_PATH}"])
    if rc != 0:
        return None, f"git show {rev}:{SKILL_PATH} failed: {err or f'rc={rc}'}"
    return out.decode("utf-8", "surrogateescape"), ""


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_fixtures(explicit: str | None, repo: str) -> Path:
    """Resolve the fixture directory (see the usage note above)."""
    if explicit:
        return Path(explicit)
    env = os.environ.get("GATE_REGISTRY_FIXTURES")
    if env:
        return Path(env)
    script_dir = Path(__file__).resolve().parent
    candidates = [script_dir / "fixtures"]
    root, _err = git_root(repo)
    if root is not None:
        candidates.append(Path(root) / "tests" / "gate-registry-check" / "fixtures")
    for cand in candidates:
        if (cand / "expected.json").is_file():
            return cand
    return candidates[0]


def selftest(fixtures: Path) -> int:
    manifest = fixtures / "expected.json"
    if not manifest.is_file():
        print(f"selftest: FAIL missing fixture manifest {manifest}", file=sys.stderr)
        return EXIT_ERROR
    try:
        spec = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"selftest: FAIL cannot read {manifest}: {e}", file=sys.stderr)
        return EXIT_ERROR
    cases = spec.get("cases")
    if not isinstance(cases, list) or not cases:
        print(f"selftest: FAIL {manifest} carries no cases", file=sys.stderr)
        return EXIT_ERROR

    failures: list[str] = []
    for case in cases:
        cid = case.get("id", "<unnamed>")
        skill_rel = case.get("skill")
        tracked_rel = case.get("tracked")
        expected = list(case.get("expected_findings", []))
        digests = case.get("sha256", {}) or {}
        if not skill_rel or not tracked_rel:
            failures.append(f"{cid}: case is incomplete")
            continue

        # Digest gate first: an edited snapshot is could-not-evaluate, not a
        # compared verdict (PROTOCOL §Gate standard, Two evidences).
        tampered: list[str] = []
        for rel in (skill_rel, tracked_rel):
            f = fixtures / rel
            want = digests.get(rel)
            if want is None:
                failures.append(f"{cid}: expected.json pins no digest for {rel}")
                continue
            if not f.is_file():
                failures.append(f"{cid}: missing fixture input {rel}")
                continue
            got = sha256_file(f)
            if got != want:
                tampered.append(f"{rel} (want {want}, got {got})")
        if tampered:
            print(
                f"selftest: FAIL snapshot_tampered {cid}: {'; '.join(tampered)}",
                file=sys.stderr,
            )
            return EXIT_ERROR

        skill = (fixtures / skill_rel).read_text(encoding="utf-8", errors="surrogateescape")
        tracked = [
            line.strip()
            for line in (fixtures / tracked_rel).read_text(encoding="utf-8").split("\n")
            if line.strip()
        ]
        found, _tables, _rows = evaluate_text(skill, tracked)
        got_ids = sorted(f"{cls}:{subject}" for cls, subject in found)
        want_ids = sorted(expected)
        if got_ids != want_ids:
            failures.append(
                f"{cid}: finding ids differ; missing={sorted(set(want_ids) - set(got_ids))} "
                f"unexpected={sorted(set(got_ids) - set(want_ids))}"
            )

    if failures:
        for f in failures:
            print(f"selftest: FAIL {f}", file=sys.stderr)
        print(f"selftest: FAIL ({len(failures)} of {len(cases)} cases)", file=sys.stderr)
        return EXIT_FINDINGS
    print(f"selftest: ok ({len(cases)} committed fixture cases; digests verified)")
    return EXIT_CLEAN


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Check that every instrument the lane tracks has a FULL registry row "
            "in SKILL.md, and print the revision the verdict was measured at."
        ),
    )
    ap.add_argument("--repo", default=".", help="repository to evaluate (default: .)")
    ap.add_argument(
        "--rev",
        default=None,
        help="revision to evaluate (default: HEAD; use --worktree for the index)",
    )
    ap.add_argument(
        "--worktree",
        action="store_true",
        help="evaluate the index plus the SKILL.md on disk instead of a committed tree",
    )
    ap.add_argument("--selftest", action="store_true", help="run the committed fixtures and exit")
    ap.add_argument(
        "--fixtures",
        default=None,
        help="fixture directory (default: <script dir>/fixtures)",
    )
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest(resolve_fixtures(args.fixtures, args.repo))

    if args.worktree and args.rev:
        print("ERROR could not evaluate: --worktree and --rev are mutually exclusive", file=sys.stderr)
        return EXIT_ERROR

    root, err = git_root(args.repo)
    if root is None:
        print(f"ERROR could not evaluate: {err}", file=sys.stderr)
        return EXIT_ERROR

    rev: str | None
    if args.worktree:
        rev = None
        rc, out, err = run_git(root, ["rev-parse", "--verify", "HEAD^{commit}"])
        if rc != 0:
            print(
                f"ERROR could not evaluate: cannot resolve HEAD: {err or f'rc={rc}'}",
                file=sys.stderr,
            )
            return EXIT_ERROR
        measured = out.decode("ascii", "replace").strip()
    else:
        full, err = resolve_rev(root, args.rev or "HEAD")
        if full is None:
            print(f"ERROR could not evaluate: {err}", file=sys.stderr)
            return EXIT_ERROR
        rev = full
        measured = full

    population, err = tracked_paths(root, rev)
    if population is None:
        print(f"ERROR could not evaluate: {err}", file=sys.stderr)
        return EXIT_ERROR

    text, err = skill_text(root, rev)
    if text is None:
        print(f"ERROR could not evaluate: {err}", file=sys.stderr)
        return EXIT_ERROR

    findings, tables, rows = evaluate_text(text, population)

    print(f"rev {measured}")
    if args.worktree:
        print("tree worktree")
    for cls, subject in findings:
        print(f"finding {cls}:{subject}")
    print(f"tables {tables} rows {rows} findings {len(findings)}")
    return EXIT_CLEAN if not findings else EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
