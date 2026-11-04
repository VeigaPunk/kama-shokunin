#!/usr/bin/env python3
"""round72-round-scope.py - round-72 C1 (calibration): the pre-report cleanliness arm cannot be satisfied vacuously.

Predicate (frozen: plans/round-72-claims.md section C1; the same sentence is the pre-report
gate's arm-6 docstring and the receipt label; the PREDICATE constant below carries it verbatim
on one line, byte-equal to the plan's blockquote minus its quote marks and line breaks):

    `python3 tools/round72-round-scope.py --repo <lane> --round <N> --tip <rev>` prints one
    `ROUND_SCOPE round=<N> cases=3 findings=<f>` line and exits 0 only when the round's frozen
    claims plan `plans/round-<N>-claims.md` exists at `<rev>` with a first heading naming round
    `<N>`, no path outside the declared record allow-list is uncommitted, and no path under
    `.ufo/waves/round-<N>/` is git-ignored; it exits 1 naming every finding as
    `ROUND_SCOPE_FINDING <case> <detail>`.

Cases (`cases=3` is the fixed case population; findings are printed in this order):

  A `label`    the round's frozen claims plan `plans/round-<N>-claims.md` exists as a blob at
               `--tip` and its first markdown heading names round `<N>`. This anchor is the
               lane-owned freeze plan, not the fleet prompt `.ufo/prompts/kama-round-<N>.md`:
               the prompt lives in the fleet repo and cannot be read at a lane tip (the plan's
               pre-score freeze amendment, 2026-11-03T22:45 -03).
  B `stray`    `git -C <repo> status --porcelain -uall` over the WHOLE repository; every path a
               record names is one finding unless the path is in the `--allow` list. A rename
               record names two paths (the source and the destination) and yields one finding per
               unallowed path.
  C `ignored`  `git -C <repo> status --porcelain -uall --ignored -- .ufo/waves/round-<N>`; every
               `!!` record is one finding. No allow-list escape exists here by design: an ignored
               path the round ships under its wave dir is a finding, and a round that needs one
               declares it in its claims plan first.

Output (default mode):

    ROUND_SCOPE_FINDING <case> <detail>      one line per finding
    ROUND_SCOPE round=<N> cases=3 findings=<f>

Exit map: `0` clean, `1` findings, `2` could-not-evaluate (CLI misuse, `--repo` is not a git
repository, `--tip` does not resolve to a commit, a git command fails, an unbuildable selftest
fixture). A scored run never exits 2 for a finding: it names the findings and exits 1.

Repository resolution: `--repo` is resolved through `git rev-parse --show-toplevel` and every
git call names `-C <toplevel>`, so every path in a finding is repository-root-relative (porcelain
v1 guarantees root-relative paths even when invoked from a subdirectory).

Allow list: `--allow PATH` (repeatable) declares a record path that may be uncommitted. An entry
is either exact repository-relative path match, or - when it ends with `/` - a directory prefix.
Entries are validated (relative, no `..`, no empty segment); a bad entry is CLI misuse, exit 2.

Wiring: the pre-report gate enters this module as arm 6 `round-scope` with
`python3 tools/round72-round-scope.py --repo <repo> --round <N> --tip <tip>` and passes when it
exits 0. The gate's own `PRE_REPORT round=<N> arms=6 failed=<f> uncommitted=<u>` verdict is
owned by tools/pre-report-gate.py; this module only prints ROUND_SCOPE lines.

Selftest fixtures mirror the pre-score control harness
(.ufo/waves/round-72/controls/round-scope-control.py): the same committed tree, the same three
defect mutations (missing freeze plan, uncommitted path outside the wave dir, git-ignored path
inside the wave dir), plus a wrong-round heading, a heading-less plan, an allow-listed stray,
an allow-listed directory, a not-a-git-repository probe, CLI misuse, and `--json` round-trip.
Every fixture is a throwaway git repository under `--work`; its toplevel is asserted before the
first commit, and every git mutation names `-C <fixture>` with a throwaway identity passed as
`-c user.name=fixture -c user.email=fixture@invalid` (never `git config`).

Receipts for this tool live under .ufo/waves/round-72/w1/EX01RoundScope/.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PREDICATE = "`python3 tools/round72-round-scope.py --repo <lane> --round <N> --tip <rev>` prints one `ROUND_SCOPE round=<N> cases=3 findings=<f>` line and exits 0 only when the round's frozen claims plan `plans/round-<N>-claims.md` exists at `<rev>` with a first heading naming round `<N>`, no path outside the declared record allow-list is uncommitted, and no path under `.ufo/waves/round-<N>/` is git-ignored; it exits 1 naming every finding as `ROUND_SCOPE_FINDING <case> <detail>`."

CASE_ORDER = ("label", "stray", "ignored")
GIT_TIMEOUT = 120

_HEADING_RE = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
_ROUND_RE = re.compile(r"(?i)\bround[\s_.\-]*0*(\d+)\b")
_C_ESCAPES = {
    "a": "\a", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v",
    "\\": "\\", '"': '"',
}


class ScopeError(RuntimeError):
    """A could-not-evaluate condition (exit 2), never a finding."""


def _one_line(text: str, limit: int = 160) -> str:
    flat = " ".join(str(text).split())
    return flat if len(flat) <= limit else flat[:limit] + "..."


def _git(repo: Path | str, *args: str) -> subprocess.CompletedProcess:
    argv = ["git", "-C", str(repo), *args]
    try:
        return subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="surrogateescape",
            timeout=GIT_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ScopeError("{} failed: {}".format(" ".join(argv), _one_line(exc))) from exc


def resolve_repo(repo: str) -> Path:
    path = Path(repo).expanduser()
    if not path.is_dir():
        raise ScopeError("--repo {!r} is not a directory".format(repo))
    proc = _git(path, "rev-parse", "--show-toplevel")
    if proc.returncode != 0 or not proc.stdout.strip():
        detail = _one_line(proc.stderr) or "rev-parse --show-toplevel failed"
        raise ScopeError("--repo {!r} is not a git repository ({})".format(repo, detail))
    return Path(os.path.realpath(proc.stdout.strip()))


def _cunquote(text: str) -> str:
    """Decode one git porcelain path token (C-quoted when it holds special bytes)."""
    if not (len(text) >= 2 and text[0] == '"' and text[-1] == '"'):
        return text
    body = text[1:-1]
    out = bytearray()
    i = 0
    while i < len(body):
        ch = body[i]
        if ch != "\\":
            out.extend(ch.encode("utf-8", "surrogateescape"))
            i += 1
            continue
        i += 1
        if i >= len(body):
            out.extend(b"\\")
            break
        esc = body[i]
        if esc in _C_ESCAPES:
            out.extend(_C_ESCAPES[esc].encode("utf-8"))
            i += 1
        elif esc in "01234567":
            digits = body[i:i + 3]
            if len(digits) == 3 and all(c in "01234567" for c in digits):
                out.append(int(digits, 8) & 0xFF)
                i += 3
            else:
                out.extend(esc.encode("utf-8", "surrogateescape"))
                i += 1
        else:
            out.extend(esc.encode("utf-8", "surrogateescape"))
            i += 1
    return out.decode("utf-8", "surrogateescape")


def _record_paths(record: str) -> list[str]:
    """Repository-relative paths named by one porcelain v1 record (rename -> two paths)."""
    if len(record) < 4:
        return []
    body = record[3:]
    if body.startswith('"'):
        i = 1
        while i < len(body):
            if body[i] == "\\":
                i += 2
                continue
            if body[i] == '"':
                break
            i += 1
        first = body[:i + 1]
        rest = body[i + 1:]
        paths = [_cunquote(first)]
        if rest.startswith(" -> "):
            paths.append(_cunquote(rest[4:]))
        return paths
    if " -> " in body:
        old, new = body.rsplit(" -> ", 1)
        return [_cunquote(old), _cunquote(new)]
    return [_cunquote(body)]


def _first_heading(text: str) -> str | None:
    for raw in text.splitlines():
        match = _HEADING_RE.match(raw)
        if match:
            return match.group(2).strip()
    return None


def _round_numbers(text: str) -> set[int]:
    return {int(number) for number in _ROUND_RE.findall(text)}


def _normalize_allow(entries: list[str] | None) -> list[str]:
    out: list[str] = []
    for raw in entries or []:
        entry = raw.strip()
        if not entry:
            raise ScopeError("--allow entry is empty")
        if entry.startswith("/"):
            raise ScopeError("--allow {!r} is absolute; use a repository-relative path".format(raw))
        if entry.startswith("./"):
            entry = entry[2:]
        segments = entry[:-1].split("/") if entry.endswith("/") else entry.split("/")
        if not segments or any(seg in ("", ".", "..") for seg in segments):
            raise ScopeError("--allow {!r} is not a repository-relative path".format(raw))
        out.append(entry)
    return out


def _allowed(path: str, allow: list[str]) -> bool:
    for entry in allow:
        if entry.endswith("/"):
            if path.startswith(entry):
                return True
        elif path == entry:
            return True
    return False


def _finding(case: str, detail: str) -> dict:
    return {"case": case, "detail": _one_line(detail)}


def _label_findings(root: Path, round_no: int, tip: str) -> list[dict]:
    plan_rel = "plans/round-{}-claims.md".format(round_no)
    spec = "{}:{}".format(tip, plan_rel)
    probe = _git(root, "cat-file", "-e", spec)
    if probe.returncode != 0:
        return [_finding("label", "{} rev={} status=absent".format(plan_rel, tip))]
    kind = _git(root, "cat-file", "-t", spec)
    objtype = kind.stdout.strip()
    if kind.returncode != 0 or objtype != "blob":
        return [_finding("label", "{} rev={} status=not-a-blob type={}".format(
            plan_rel, tip, _one_line(objtype) or "unknown"))]
    blob = _git(root, "cat-file", "-p", spec)
    if blob.returncode != 0:
        raise ScopeError("git cat-file -p {} failed: {}".format(spec, _one_line(blob.stderr)))
    heading = _first_heading(blob.stdout)
    if heading is None:
        return [_finding("label", "{} rev={} status=no-heading".format(plan_rel, tip))]
    if round_no not in _round_numbers(heading):
        return [_finding("label", "{} rev={} status=heading-mismatch heading={}".format(
            plan_rel, tip, heading))]
    return []


def _stray_findings(root: Path, allow: list[str]) -> list[dict]:
    proc = _git(root, "status", "--porcelain", "-uall")
    if proc.returncode != 0:
        raise ScopeError("git status --porcelain -uall failed: {}".format(_one_line(proc.stderr)))
    findings = []
    for record in proc.stdout.splitlines():
        if not record.strip():
            continue
        status = record[:2]
        for path in _record_paths(record):
            if not _allowed(path, allow):
                findings.append(_finding("stray", "{} status={}".format(path, status)))
    return findings


def _ignored_findings(root: Path, round_no: int) -> list[dict]:
    wave_rel = ".ufo/waves/round-{}".format(round_no)
    proc = _git(root, "status", "--porcelain", "-uall", "--ignored", "--", wave_rel)
    if proc.returncode != 0:
        raise ScopeError("git status --ignored -- {} failed: {}".format(
            wave_rel, _one_line(proc.stderr)))
    findings = []
    for record in proc.stdout.splitlines():
        if not record.strip() or record[:2] != "!!":
            continue
        for path in _record_paths(record):
            findings.append(_finding("ignored", path))
    return findings


def evaluate(repo: str, round_no: int, tip: str = "master", allow: list[str] | None = None) -> dict:
    """Run the three cases and derive the pinned verdict; the only scoring entry point."""
    allow = list(allow or [])
    root = resolve_repo(repo)
    rev = _git(root, "rev-parse", "--verify", "--quiet", "{}^{{commit}}".format(tip))
    if rev.returncode != 0 or not rev.stdout.strip():
        raise ScopeError("--tip {!r} does not resolve to a commit".format(tip))

    findings: list[dict] = []
    findings.extend(_label_findings(root, round_no, tip))
    findings.extend(_stray_findings(root, allow))
    findings.extend(_ignored_findings(root, round_no))
    findings.sort(key=lambda item: (CASE_ORDER.index(item["case"]), item["detail"]))

    line = "ROUND_SCOPE round={} cases={} findings={}".format(round_no, len(CASE_ORDER), len(findings))
    return {
        "repo": str(root),
        "round": round_no,
        "tip": tip,
        "rev": rev.stdout.strip(),
        "allow": allow,
        "cases": len(CASE_ORDER),
        "findings": findings,
        "count": len(findings),
        "line": line,
        "exit": 0 if not findings else 1,
    }


def render(result: dict) -> list[str]:
    lines = [
        "ROUND_SCOPE_FINDING {} {}".format(item["case"], item["detail"])
        for item in result["findings"]
    ]
    lines.append(result["line"])
    return lines


# ---------------------------------------------------------------------------
# Selftest fixtures. Nothing below touches the graded repository: every fixture
# is a throwaway git repository under --work, its toplevel is asserted before
# the first commit, and every git call names -C <fixture>.
# ---------------------------------------------------------------------------

_FIXTURE_FILES = {
    "SCORECARD.md": "# scorecard\n\n## Axes\n\n| axis | score |\n|---|---|\n| calibration | 7 |\n",
    "LOG.md": "# log\n",
    "SKILL.md": "# skill\n",
    "PROVINCE.md": "# province\n",
    "corpus/SOURCES.md": "# sources\n",
    ".gitignore": ".ufo/waves/round-72/*.log\n",
    "plans/round-72-claims.md": "# kama round 72 \u2014 frozen claims\n\nbody\n",
    ".ufo/waves/round-72/evidence.txt": "committed evidence\n",
}
_ROUND_NO = 72


def build_fixture(work: Path, case: str) -> Path:
    """Build one throwaway git repository mirroring the pre-score control fixture set."""
    root = Path(work) / case
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    for rel, body in _FIXTURE_FILES.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    if case == "label-missing":
        (root / "plans/round-72-claims.md").unlink()
    if case == "label-wrong-round":
        (root / "plans/round-72-claims.md").write_text(
            "# kama round 71 \u2014 frozen claims\n\nbody\n", encoding="utf-8")
    if case == "label-no-heading":
        (root / "plans/round-72-claims.md").write_text("body only\n", encoding="utf-8")

    init = _git(root, "init", "-q", "-b", "master")
    if init.returncode != 0:
        raise ScopeError("fixture git init failed at {}: {}".format(root, _one_line(init.stderr)))
    top = _git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or os.path.realpath(top.stdout.strip()) != os.path.realpath(str(root)):
        raise ScopeError("fixture toplevel {!r} is not {!r}".format(
            top.stdout.strip(), str(root)))
    add = _git(root, "add", "-A")
    if add.returncode != 0:
        raise ScopeError("fixture git add failed at {}: {}".format(root, _one_line(add.stderr)))
    commit = _git(root, "-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
                  "-c", "commit.gpgsign=false", "commit", "-q", "-m", "fixture")
    if commit.returncode != 0:
        raise ScopeError("fixture git commit failed at {}: {}".format(root, _one_line(commit.stderr)))

    if case == "stray-root":
        (root / "stray-note.md").write_text(
            "uncommitted round work outside the wave dir\n", encoding="utf-8")
    if case == "stray-renamed":
        moved = _git(root, "mv", "LOG.md", "moved name.md")
        if moved.returncode != 0:
            raise ScopeError("fixture git mv failed at {}: {}".format(
                root, _one_line(moved.stderr)))
    if case == "ignored-in-wave":
        (root / ".ufo/waves/round-72/scratch.log").write_text(
            "ignored evidence\n", encoding="utf-8")
    return root


def _plan_predicate(repo: str, round_no: int = _ROUND_NO) -> str | None:
    """The plan's C1 blockquote, joined onto one line; None when the plan is absent."""
    path = Path(repo) / "plans/round-{}-claims.md".format(round_no)
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = None
    for index, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith(">") and "`python3 tools/round72-round-scope.py" in stripped:
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


def run_selftest(args) -> int:
    if args.work:
        work = Path(args.work).resolve()
        if work.exists() and (not work.is_dir() or any(work.iterdir())):
            print("ROUND_SCOPE_SELFTEST could-not-evaluate: --work {} is not an empty directory"
                  .format(work))
            return 2
    else:
        work = Path(tempfile.mkdtemp(prefix="round-scope-selftest-"))
    work.mkdir(parents=True, exist_ok=True)
    print("ROUND_SCOPE_SELFTEST_WORK {}".format(work))

    passed = 0
    failed: list[str] = []

    def mark(label: str, problems: list[str]) -> None:
        nonlocal passed
        if problems:
            failed.append(label)
            print("FAIL {} :: {}".format(label, "; ".join(problems)))
        else:
            passed += 1
            print("PASS {}".format(label))

    def check(label: str, result: dict, want_exit: int, want_count: int,
              want_case: str | None = None, detail_has: str | None = None,
              want_line: str | None = None) -> None:
        for line in render(result):
            print("  " + line)
        problems = []
        if result["exit"] != want_exit:
            problems.append("exit={} want {}".format(result["exit"], want_exit))
        if result["count"] != want_count:
            problems.append("findings={} want {}".format(result["count"], want_count))
        if want_case is not None:
            cases = sorted({item["case"] for item in result["findings"]})
            if cases != [want_case]:
                problems.append("cases={} want [{}]".format(cases, want_case))
        if detail_has is not None:
            details = " | ".join(item["detail"] for item in result["findings"])
            if detail_has not in details:
                problems.append("detail lacks {!r} (got {!r})".format(detail_has, details))
        if want_line is not None and result["line"] != want_line:
            problems.append("line={!r} want {!r}".format(result["line"], want_line))
        mark(label, problems)

    def run(case: str, allow: list[str] | None = None, tip: str = "master") -> dict:
        return evaluate(str(build_fixture(work, case)), _ROUND_NO, tip, allow or [])

    try:
        clean_line = "ROUND_SCOPE round=72 cases=3 findings=0"
        check("clean", run("clean"), 0, 0, want_line=clean_line)

        check("label-missing", run("label-missing"), 1, 1, want_case="label",
              detail_has="status=absent")
        check("label-wrong-round", run("label-wrong-round"), 1, 1, want_case="label",
              detail_has="status=heading-mismatch")
        check("label-no-heading", run("label-no-heading"), 1, 1, want_case="label",
              detail_has="status=no-heading")

        check("stray-root", run("stray-root"), 1, 1, want_case="stray",
              detail_has="stray-note.md")
        check("ignored-in-wave", run("ignored-in-wave"), 1, 1, want_case="ignored",
              detail_has="scratch.log")

        check("allow-exact", run("stray-root", allow=["stray-note.md"]), 0, 0,
              want_line=clean_line)

        dirfixture = build_fixture(work, "clean")
        record = dirfixture / ".ufo/waves/round-72/records/new.out"
        record.parent.mkdir(parents=True)
        record.write_text("uncommitted record\n", encoding="utf-8")
        check("allow-dir", evaluate(str(dirfixture), _ROUND_NO, "master",
                                    [".ufo/waves/round-72/records/"]), 0, 0,
              want_line=clean_line)

        check("stray-renamed", run("stray-renamed"), 1, 2, want_case="stray",
              detail_has="moved name.md")

        subdir = build_fixture(work, "subdir-clean")
        (subdir / "stray-note.md").write_text("root-relative probe\n", encoding="utf-8")
        check("subdir-repo", evaluate(str(subdir / "corpus"), _ROUND_NO, "master"), 1, 1,
              want_case="stray", detail_has="stray-note.md status=??")

        try:
            evaluate(str(build_fixture(work, "clean")), _ROUND_NO, "deadbeefdeadbeef")
        except ScopeError as exc:
            mark("tip-unresolvable", [] if "does not resolve" in str(exc) else [str(exc)])
        else:
            mark("tip-unresolvable", ["evaluate accepted an unresolvable --tip"])

        bad_allow = subprocess.run(
            [sys.executable, os.path.abspath(__file__), "--repo", str(work / "clean"),
             "--round", str(_ROUND_NO), "--allow", "/etc/passwd"],
            capture_output=True, text=True)
        mark("bad-allow", [] if bad_allow.returncode == 2 else
             ["exit={} want 2".format(bad_allow.returncode)])

        plain = work / "plain-dir"
        plain.mkdir(exist_ok=True)
        try:
            evaluate(str(plain), _ROUND_NO, "master")
        except ScopeError as exc:
            mark("not-a-git-repo",
                 [] if "not a git repository" in str(exc) else [str(exc)])
        else:
            mark("not-a-git-repo", ["evaluate accepted a non-git directory"])

        misuse = subprocess.run(
            [sys.executable, os.path.abspath(__file__), "--repo", str(work), "--tip", "master"],
            capture_output=True, text=True)
        mark("cli-misuse", [] if misuse.returncode == 2 else
             ["exit={} want 2".format(misuse.returncode)])

        json_root = build_fixture(work, "json-clean")
        json_run = subprocess.run(
            [sys.executable, os.path.abspath(__file__), "--repo", str(json_root),
             "--round", str(_ROUND_NO), "--tip", "master", "--json"],
            capture_output=True, text=True)
        problems = []
        if json_run.returncode != 0:
            problems.append("exit={} want 0".format(json_run.returncode))
        try:
            document = json.loads(json_run.stdout)
        except json.JSONDecodeError as exc:
            problems.append("unparseable json: {}".format(exc))
        else:
            if document.get("line") != clean_line:
                problems.append("line={!r} want {!r}".format(document.get("line"), clean_line))
            if document.get("count") != 0 or document.get("exit") != 0:
                problems.append("count={!r} exit={!r}".format(
                    document.get("count"), document.get("exit")))
        mark("json-roundtrip", problems)

        frozen = _plan_predicate(args.repo, _ROUND_NO)
        if frozen is None:
            print("SKIP predicate (no plans/round-72-claims.md at --repo {})".format(args.repo))
        elif frozen == "":
            mark("predicate", ["plan has no round-scope blockquote"])
        else:
            problems = []
            if PREDICATE != frozen:
                problems.append("PREDICATE differs from the plan blockquote "
                                "(len {} vs {})".format(len(PREDICATE), len(frozen)))
            if "\n" in PREDICATE:
                problems.append("PREDICATE is not one line")
            mark("predicate", problems)
    except ScopeError as exc:
        print("ROUND_SCOPE_SELFTEST could-not-evaluate: {}".format(exc))
        print("ROUND_SCOPE_SELFTEST_WORK_KEPT {}".format(work))
        return 2
    except OSError as exc:
        print("ROUND_SCOPE_SELFTEST could-not-evaluate: {}".format(_one_line(exc)))
        print("ROUND_SCOPE_SELFTEST_WORK_KEPT {}".format(work))
        return 2

    print("ROUND_SCOPE_SELFTEST pass={} fail={}".format(passed, len(failed)))
    if failed:
        print("ROUND_SCOPE_SELFTEST_FAILED " + ",".join(failed))
        print("ROUND_SCOPE_SELFTEST_WORK_KEPT {}".format(work))
        return 1
    shutil.rmtree(work, ignore_errors=True)
    return 0


def _default_lane(repo: Path) -> str:
    name = repo.name
    return name[:-len("-shokunin")] if name.endswith("-shokunin") else name


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Round-72 C1 round scope: the frozen claims plan at the tip, whole-repo "
                    "uncommitted records, and git-ignored paths under the wave dir (round 72)."
    )
    ap.add_argument("--repo", default=".", help="lane repository to grade (default: current directory)")
    ap.add_argument("--round", dest="round_no", type=int, default=None,
                    help="round number whose claims plan and wave dir are graded (required)")
    ap.add_argument("--tip", default="master",
                    help="revision whose committed claims plan is read (default: master)")
    ap.add_argument("--lane", default=None,
                    help="lane name recorded in --json (default: repo dir name minus a trailing -shokunin)")
    ap.add_argument("--allow", action="append", default=None, metavar="PATH",
                    help="repository-relative record path allowed to be uncommitted; repeatable; "
                         "a trailing / declares a directory prefix")
    ap.add_argument("--work", default=None,
                    help="selftest scratch dir (must be absent or empty; default: fresh TMPDIR dir)")
    ap.add_argument("--selftest", action="store_true", help="run the fixture selftest")
    ap.add_argument("--json", action="store_true",
                    help="emit one JSON document instead of the human lines")
    args = ap.parse_args(argv)

    if args.selftest:
        return run_selftest(args)
    if args.round_no is None:
        ap.error("--round is required (or use --selftest)")
    if args.round_no < 1:
        print("ROUND_SCOPE could-not-evaluate round={} (round must be >= 1)".format(args.round_no))
        return 2

    try:
        allow = _normalize_allow(args.allow)
        result = evaluate(args.repo, args.round_no, args.tip, allow)
    except ScopeError as exc:
        print("ROUND_SCOPE could-not-evaluate round={}: {}".format(args.round_no, exc))
        return 2

    result["lane"] = args.lane or _default_lane(Path(result["repo"]))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for line in render(result):
            print(line)
    return result["exit"]


if __name__ == "__main__":
    sys.exit(main())
