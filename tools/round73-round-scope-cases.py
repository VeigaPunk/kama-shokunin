#!/usr/bin/env python3
"""round73-round-scope-cases.py - round-73 C1 (calibration): the round-scope counter kills
the three survivors its own claim recorded.

Predicate (frozen: plans/round-73-claims.md section C1; the same sentence is the module's
PREDICATE constant and the receipt label; the constant below carries it verbatim on one line,
byte-equal to the plan's blockquote minus its quote marks and line breaks):

    `python3 tools/round73-round-scope-cases.py --repo <lane> --round <N> --tip <rev>` prints
    one `ROUND_SCOPE_V2 round=<N> cases=6 findings=<f>` line and exits 0 only when the round's
    frozen claims plan `plans/round-<N>-claims.md` exists at `<rev>` with a first heading naming
    round `<N>`, no path outside the declared record allow-list is uncommitted in the primary
    worktree or in any linked worktree of the repository, no path under a
    `.ufo/waves/round-<M>/` directory with `M >= <N>` is git-ignored, and every initialized
    submodule worktree has no uncommitted or untracked content; it exits 1 naming every finding
    as `ROUND_SCOPE_V2_FINDING <case> <detail>`.

Cases (`cases=6` is the fixed case population; findings are printed in this order):

  A `label`    the round's frozen claims plan `plans/round-<N>-claims.md` exists as a blob at
               `--tip` and its first markdown heading names round `<N>` (inherited from
               tools/round72-round-scope.py, imported, not copied).
  B `stray`    `git -C <repo> status --porcelain -uall` over the whole primary worktree; every
               path a record names is one finding unless the path is in `--allow` (inherited).
  C `ignored`  `git -C <repo> status --porcelain -uall --ignored -- .ufo/waves/round-<N>`;
               every `!!` record is one finding (inherited).
  D `worktree` A5: `git -C <repo> worktree list --porcelain`; for every worktree path other
               than the resolved primary, `git -C <path> status --porcelain -uall` is graded
               like `stray` (paths checked against `--allow`). A linked worktree that cannot be
               read is a finding naming the path, never a pass.
  E `ignored-older-label`
               A6: every `.ufo/waves/round-<M>` directory present in the primary worktree with
               `M >= <N>` (parsed from the directory name; unparseable names skipped) is probed
               with `git status --porcelain -uall --ignored -- <dir>`; every `!!` record is a
               finding. Older rounds (`M < N`) are outside the population by design: the lane's
               committed-then-ignored `__pycache__` leftovers live there.
  F `submodule` A7: for every path in `git config -f .gitmodules --get-regexp path` whose
               worktree directory exists, `git -C <path> status --porcelain -uall` is graded
               (every record is a finding); the parent is also probed with
               `git status --porcelain -uall --ignore-submodules=none` and every record naming
               a configured submodule path is a finding naming the submodule path and the
               parent record. An uninitialised submodule (no worktree directory) is not graded
               and is named in the output as skipped.

Output (default mode):

    ROUND_SCOPE_V2_FINDING <case> <detail>     one line per finding, case order then detail
    ROUND_SCOPE_V2_SKIP submodule <path> reason=<no-worktree|not-initialised>
    ROUND_SCOPE_V2 round=<N> cases=6 findings=<f>

Exit map: `0` clean, `1` findings, `2` could-not-evaluate (CLI misuse, `--repo` is not a git
repository, `--tip` does not resolve to a commit, a git command fails, an unbuildable selftest
fixture). A scored run never exits 2 for a finding: it names the findings and exits 1.

The three inherited graders (`_label_findings`, `_stray_findings`, `_ignored_findings`) and
their helpers are imported from `tools/round72-round-scope.py` with
`importlib.util.spec_from_file_location`; that file's bytes stay unchanged, so its own 16 selftest
arms stay green. The import is guarded so it never writes a `__pycache__` next to it.

`--allow PATH` is repeatable and validated exactly like the round-72 counter: repository-
relative path, a trailing `/` declares a directory prefix, absolute/`..`/empty-segment entries
are CLI misuse (exit 2). The allow-list applies to `stray` and `worktree` records only; the
`ignored`, `ignored-older-label` and `submodule` cases have no allow-list escape by design.

Selftest: `--selftest` builds throwaway git repositories under `--work` (default a fresh
TMPDIR directory), prints PASS/FAIL per arm, and ends with
`ROUND_SCOPE_V2_SELFTEST pass=<n> fail=<m>`. Every fixture toplevel is asserted before its
first commit, every git mutation names `-C <fixture>` with a throwaway identity passed as
`-c user.name=fixture -c user.email=fixture@invalid`, and the work dir is removed on success.
The arms cover the inherited cases red and the clean tree green, worktree red/green, the
older-label case red and an older-round ignored file that must stay green, submodule red
(modified tracked + untracked content), submodule green, an `ignore=all` variant killed, the
uninitialised-submodule skip line, CLI misuse / not-a-repo / bad-allow / unresolvable-tip exit
2, a `--json` round-trip, the predicate-equals-plan arm (the plan is read from the tip), and a
do-nothing shim (a counter that only greps the plan heading) that the three survivor fixtures
must score red.

Receipts for this tool live under .ufo/waves/round-73/w1/EX01ScopeV2/.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PREDICATE = "`python3 tools/round73-round-scope-cases.py --repo <lane> --round <N> --tip <rev>` prints one `ROUND_SCOPE_V2 round=<N> cases=6 findings=<f>` line and exits 0 only when the round's frozen claims plan `plans/round-<N>-claims.md` exists at `<rev>` with a first heading naming round `<N>`, no path outside the declared record allow-list is uncommitted in the primary worktree or in any linked worktree of the repository, no path under a `.ufo/waves/round-<M>/` directory with `M >= <N>` is git-ignored, and every initialized submodule worktree has no uncommitted or untracked content; it exits 1 naming every finding as `ROUND_SCOPE_V2_FINDING <case> <detail>`."

CASE_ORDER = ("label", "stray", "ignored", "worktree", "ignored-older-label", "submodule")
_SUMMARY_LABEL = "ROUND_SCOPE_V2"
_ROUND_DIR_RE = re.compile(r"^round-(\d+)$")
_GITMODULE_PATH_KEY_RE = re.compile(r"^submodule\.(.+)\.path$")

_INHERITED = None


class ScopeError(RuntimeError):
    """A could-not-evaluate condition (exit 2), never a finding."""


def _inherited():
    """Load tools/round72-round-scope.py once and return the module (imported, not copied)."""
    global _INHERITED
    if _INHERITED is not None:
        return _INHERITED
    path = Path(__file__).resolve().parent / "round72-round-scope.py"
    if not path.is_file():
        raise ScopeError("inherited counter {} is absent".format(path))
    spec = importlib.util.spec_from_file_location("round73_inherited_round72_round_scope",
                                                  str(path))
    if spec is None or spec.loader is None:
        raise ScopeError("cannot build an import spec for {}".format(path))
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    except OSError as exc:
        raise ScopeError("cannot import inherited counter {}: {}".format(path, exc)) from exc
    finally:
        sys.dont_write_bytecode = previous
    for name in ("_label_findings", "_stray_findings", "_ignored_findings"):
        if not callable(getattr(module, name, None)):
            raise ScopeError("inherited counter {} lacks {}".format(path, name))
    _INHERITED = module
    return module


# ---------------------------------------------------------------------------
# The three round-73 cases. Every git call names -C <path>; a git failure is a
# could-not-evaluate (ScopeError), never a pass.
# ---------------------------------------------------------------------------


def _worktree_roots(mod, root: Path) -> list[Path]:
    """Every worktree root of the repository, primary first (round 73 F3 repair)."""
    proc = mod._git(root, "worktree", "list", "--porcelain")
    if proc.returncode != 0:
        raise mod.ScopeError("git worktree list --porcelain failed: {}".format(
            mod._one_line(proc.stderr)))
    entries = [line[len("worktree "):] for line in proc.stdout.splitlines()
               if line.startswith("worktree ")]
    if not entries:
        raise mod.ScopeError("git worktree list --porcelain reported no worktrees")
    return [Path(raw) for raw in entries if raw.strip()]


def _worktree_findings(mod, root: Path, allow: list[str]) -> list[dict]:
    """A5: grade every linked worktree of the repository like the primary `stray` case."""
    entries = [str(p) for p in _worktree_roots(mod, root)]
    primary = os.path.realpath(str(root))
    findings = []
    for raw in entries:
        if not raw.strip():
            continue
        if os.path.realpath(raw) == primary:
            continue
        status = mod._git(raw, "status", "--porcelain", "-uall")
        if status.returncode != 0:
            findings.append(mod._finding(
                "worktree", "{} status=unreadable {}".format(raw, mod._one_line(status.stderr))))
            continue
        for record in status.stdout.splitlines():
            if not record.strip():
                continue
            state = record[:2]
            for path in mod._record_paths(record):
                if not mod._allowed(path, allow):
                    findings.append(mod._finding(
                        "worktree", "{} {} status={}".format(raw, path, state)))
    return findings


def _ignored_older_findings(mod, root: Path, round_no: int) -> list[dict]:
    """A6: every git-ignored record under present round-<M> wave dirs with M >= N.

    Round 73 F3 repair: the population is enumerated in EVERY worktree of the repository,
    not only the primary one, so an ignored file under a later round's wave dir in a linked
    worktree is graded too (the frozen sentence names no worktree exception).
    """
    findings: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for wt in _worktree_roots(mod, root):
        waves = wt / ".ufo" / "waves"
        if not waves.is_dir():
            continue
        try:
            entries = list(waves.iterdir())
        except OSError as exc:
            raise mod.ScopeError("cannot list {}: {}".format(waves, mod._one_line(exc))) from exc
        names = []
        for entry in entries:
            match = _ROUND_DIR_RE.match(entry.name)
            if match is None:
                continue
            if int(match.group(1)) < round_no:
                continue
            if not entry.is_dir():
                continue
            names.append(entry.name)
        for name in sorted(names):
            rel = ".ufo/waves/{}".format(name)
            proc = mod._git(wt, "status", "--porcelain", "-uall", "--ignored", "--", rel)
            if proc.returncode != 0:
                raise mod.ScopeError("git status --ignored -- {} failed in {}: {}".format(
                    rel, wt, mod._one_line(proc.stderr)))
            for record in proc.stdout.splitlines():
                if not record.strip() or record[:2] != "!!":
                    continue
                for path in mod._record_paths(record):
                    key = (str(wt), path)
                    if key in seen:
                        continue
                    seen.add(key)
                    detail = path if os.path.realpath(str(wt)) == os.path.realpath(str(root)) \
                        else "{} where={}".format(path, wt)
                    findings.append(mod._finding("ignored-older-label", detail))
    return findings


def _submodule_paths(mod, root: Path) -> list[str]:
    """Configured submodule paths from .gitmodules (a missing file declares none)."""
    proc = mod._git(root, "config", "-f", ".gitmodules", "--get-regexp", "path")
    if proc.returncode == 1:
        return []
    if proc.returncode != 0:
        raise mod.ScopeError("git config -f .gitmodules --get-regexp path failed: {}".format(
            mod._one_line(proc.stderr)))
    paths: list[str] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        key, _, value = line.partition(" ")
        if _GITMODULE_PATH_KEY_RE.match(key) is None:
            continue
        value = value.strip()
        if value and value not in paths:
            paths.append(value)
    return paths


def _submodule_findings(mod, root: Path) -> tuple[list[dict], list[dict]]:
    """A7: grade every initialized submodule worktree, recursively, plus the parent records.

    Round 73 F3 repair: a nested initialized submodule is graded too (the frozen sentence
    names "every initialized submodule worktree", not only the top level).
    """
    findings: list[dict] = []
    skipped: list[dict] = []
    subs = _submodule_paths(mod, root)
    visited = {os.path.realpath(str(root))}

    def walk(repo: Path, prefix: str, depth: int) -> None:
        canonical = os.path.realpath(str(repo))
        if canonical in visited:
            raise mod.ScopeError("cyclic submodule worktree: {}".format(prefix))
        visited.add(canonical)
        for sub in _submodule_paths(mod, repo):
            full = "{}/{}".format(prefix, sub) if prefix else sub
            target = repo / sub
            if not target.is_dir():
                skipped.append({"case": "submodule", "path": full, "reason": "no-worktree"})
                continue
            probe = mod._git(target, "rev-parse", "--show-toplevel")
            if probe.returncode != 0 or not probe.stdout.strip():
                skipped.append({"case": "submodule", "path": full,
                                "reason": "not-initialised"})
                continue
            status = mod._git(target, "status", "--porcelain", "-uall")
            if status.returncode != 0:
                raise mod.ScopeError("git status in submodule {} failed: {}".format(
                    full, mod._one_line(status.stderr)))
            for record in status.stdout.splitlines():
                if not record.strip():
                    continue
                state = record[:2]
                for path in mod._record_paths(record):
                    findings.append(mod._finding(
                        "submodule", "{} {} status={}".format(full, path, state)))
            walk(target, full, depth + 1)

    for sub in subs:
        target = root / sub
        if not target.is_dir():
            skipped.append({"case": "submodule", "path": sub, "reason": "no-worktree"})
            continue
        probe = mod._git(target, "rev-parse", "--show-toplevel")
        if probe.returncode != 0 or not probe.stdout.strip():
            skipped.append({"case": "submodule", "path": sub, "reason": "not-initialised"})
            continue
        status = mod._git(target, "status", "--porcelain", "-uall")
        if status.returncode != 0:
            raise mod.ScopeError("git status in submodule {} failed: {}".format(
                sub, mod._one_line(status.stderr)))
        for record in status.stdout.splitlines():
            if not record.strip():
                continue
            state = record[:2]
            for path in mod._record_paths(record):
                findings.append(mod._finding(
                    "submodule", "{} {} status={}".format(sub, path, state)))
        walk(target, sub, 1)
    if subs:
        parent = mod._git(root, "status", "--porcelain", "-uall", "--ignore-submodules=none")
        if parent.returncode != 0:
            raise mod.ScopeError("git status --ignore-submodules=none failed: {}".format(
                mod._one_line(parent.stderr)))
        configured = set(subs)
        for record in parent.stdout.splitlines():
            if not record.strip():
                continue
            hit = None
            for path in mod._record_paths(record):
                if path in configured:
                    hit = path
                    break
            if hit is None:
                continue
            findings.append(mod._finding(
                "submodule", "{} parent-record={} status={}".format(
                    hit, record.strip(), record[:2])))
    skipped.sort(key=lambda item: item["path"])
    return findings, skipped


def evaluate(repo: str, round_no: int, tip: str = "master",
             allow: list[str] | None = None) -> dict:
    """Run the six cases and derive the pinned verdict; the only scoring entry point."""
    mod = _inherited()
    try:
        allow = mod._normalize_allow(allow)
        return _evaluate(mod, repo, round_no, tip, allow)
    except mod.ScopeError as exc:
        raise ScopeError(str(exc)) from exc


def _evaluate(mod, repo: str, round_no: int, tip: str, allow: list[str]) -> dict:
    root = mod.resolve_repo(repo)
    rev = mod._git(root, "rev-parse", "--verify", "--quiet", "{}^{{commit}}".format(tip))
    if rev.returncode != 0 or not rev.stdout.strip():
        raise mod.ScopeError("--tip {!r} does not resolve to a commit".format(tip))

    findings: list[dict] = []
    findings.extend(mod._label_findings(root, round_no, tip))
    findings.extend(mod._stray_findings(root, allow))
    findings.extend(mod._ignored_findings(root, round_no))
    findings.extend(_worktree_findings(mod, root, allow))
    findings.extend(_ignored_older_findings(mod, root, round_no))
    submodule_findings, skipped = _submodule_findings(mod, root)
    findings.extend(submodule_findings)
    findings.sort(key=lambda item: (CASE_ORDER.index(item["case"]), item["detail"]))

    line = "{} round={} cases={} findings={}".format(
        _SUMMARY_LABEL, round_no, len(CASE_ORDER), len(findings))
    return {
        "repo": str(root),
        "round": round_no,
        "tip": tip,
        "rev": rev.stdout.strip(),
        "allow": allow,
        "cases": len(CASE_ORDER),
        "case_order": list(CASE_ORDER),
        "findings": findings,
        "count": len(findings),
        "skipped": skipped,
        "line": line,
        "exit": 0 if not findings else 1,
    }


def render(result: dict) -> list[str]:
    lines = [
        "ROUND_SCOPE_V2_FINDING {} {}".format(item["case"], item["detail"])
        for item in result["findings"]
    ]
    for item in result["skipped"]:
        lines.append("ROUND_SCOPE_V2_SKIP {} {} reason={}".format(
            item["case"], item["path"], item["reason"]))
    lines.append(result["line"])
    return lines


# ---------------------------------------------------------------------------
# Selftest fixtures. Nothing below touches the graded repository: every fixture
# is a throwaway git repository under --work, its toplevel is asserted before
# the first commit, and every git call names -C <fixture>.
# ---------------------------------------------------------------------------

_FIXTURE_ID = ["-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
               "-c", "commit.gpgsign=false"]
_ROUND_NO = 73

_SEED_FILES = {
    ".gitignore": ".ufo/waves/round-*/*.log\n",
    "SCORECARD.md": "# scorecard\n\n## Axes\n\n| axis | score |\n|---|---|\n| calibration | 7 |\n",
    "LOG.md": "# log\n",
    "SKILL.md": "# skill\n",
    "PROVINCE.md": "# province\n",
    "corpus/SOURCES.md": "# sources\n",
    "plans/round-71-claims.md": "# kama round 71 \u2014 frozen claims\n\nbody\n",
    "plans/round-73-claims.md": "# kama round 73 \u2014 frozen claims\n\nbody\n",
    ".ufo/waves/round-73/evidence.txt": "committed evidence\n",
}

_SHIM_SOURCE = r'''
import re, subprocess, sys

repo, round_no = sys.argv[1], sys.argv[2]
proc = subprocess.run(["git", "-C", repo, "cat-file", "-p",
                       "master:plans/round-{}-claims.md".format(round_no)],
                      capture_output=True, text=True)
heading = ""
if proc.returncode == 0:
    for line in proc.stdout.splitlines():
        if line.lstrip().startswith("#"):
            heading = line
            break
if re.search(r"(?i)\bround[\s_.\-]*0*{}\b".format(round_no), heading):
    print("ROUND_SCOPE_V2 round={} cases=6 findings=0".format(round_no))
    sys.exit(0)
print("ROUND_SCOPE_V2 round={} cases=6 findings=1".format(round_no))
sys.exit(1)
'''


def _fixture_git(mod, repo: Path | str, *args: str, check: bool = True):
    proc = mod._git(repo, *args)
    if check and proc.returncode != 0:
        raise ScopeError("fixture git {} failed at {}: {}".format(
            " ".join(args), repo, mod._one_line(proc.stderr)))
    return proc


def _assert_toplevel(mod, root: Path) -> None:
    proc = mod._git(root, "rev-parse", "--show-toplevel")
    if (proc.returncode != 0
            or os.path.realpath(proc.stdout.strip()) != os.path.realpath(str(root))):
        raise ScopeError("fixture toplevel {!r} is not {!r}".format(
            proc.stdout.strip(), str(root)))


def _put(root: Path, rel: str, text: str) -> None:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _build_seed(mod, work: Path) -> Path:
    seed = work / "fixtures" / "seed"
    seed.mkdir(parents=True)
    for rel, body in _SEED_FILES.items():
        _put(seed, rel, body)
    _fixture_git(mod, seed, "init", "-q", "-b", "master")
    _assert_toplevel(mod, seed)
    _fixture_git(mod, seed, "add", "-A")
    _fixture_git(mod, seed, *_FIXTURE_ID, "commit", "-q", "-m", "seed")
    return seed


def _clone(mod, seed: Path, dest: Path) -> Path:
    if dest.exists():
        shutil.rmtree(dest)
    _fixture_git(mod, dest.parent, "clone", "-q", "--shared", str(seed), str(dest))
    _assert_toplevel(mod, dest)
    return dest


def _commit(mod, root: Path, message: str) -> None:
    _fixture_git(mod, root, "add", "-A")
    _fixture_git(mod, root, *_FIXTURE_ID, "commit", "-q", "-m", message)


def _make_submodule_repo(mod, work: Path) -> Path:
    subrepo = work / "fixtures" / "subrepo"
    if subrepo.exists():
        shutil.rmtree(subrepo)
    subrepo.mkdir(parents=True)
    _put(subrepo, "child.txt", "base\n")
    _fixture_git(mod, subrepo, "init", "-q", "-b", "master")
    _assert_toplevel(mod, subrepo)
    _fixture_git(mod, subrepo, "add", "-A")
    _fixture_git(mod, subrepo, *_FIXTURE_ID, "commit", "-q", "-m", "subrepo base")
    return subrepo


def _add_submodule(mod, root: Path, subrepo: Path, ignore_all: bool = False) -> None:
    proc = mod._git(root, "-c", "protocol.file.allow=always", "submodule", "add", "-q",
                    str(subrepo), "sub")
    if proc.returncode != 0:
        raise ScopeError("fixture git submodule add failed at {}: {}".format(
            root, mod._one_line(proc.stderr)))
    if ignore_all:
        _fixture_git(mod, root, "config", "-f", ".gitmodules", "submodule.sub.ignore", "all")
    _commit(mod, root, "add submodule{}".format(" with ignore=all" if ignore_all else ""))


def _plan_predicate_at_tip(mod, repo: str, round_no: int, tip: str) -> str | None:
    """The plan's C1 blockquote at <tip>, joined onto one line; None when the plan is absent."""
    root = mod.resolve_repo(repo)
    spec = "{}:plans/round-{}-claims.md".format(tip, round_no)
    proc = mod._git(root, "cat-file", "-p", spec)
    if proc.returncode != 0:
        return None
    lines = proc.stdout.splitlines()
    start = None
    for index, line in enumerate(lines):
        stripped = line.lstrip()
        if (stripped.startswith(">")
                and "`python3 tools/round73-round-scope-cases.py" in stripped):
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


def _child_env() -> dict:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_selftest(args) -> int:
    mod = _inherited()
    if args.work:
        work = Path(args.work).resolve()
        if work.exists() and (not work.is_dir() or any(work.iterdir())):
            print("ROUND_SCOPE_V2_SELFTEST could-not-evaluate: --work {} is not an empty directory"
                  .format(work))
            return 2
    else:
        work = Path(tempfile.mkdtemp(prefix="round73-scope-selftest-"))
    work.mkdir(parents=True, exist_ok=True)
    print("ROUND_SCOPE_V2_SELFTEST_WORK {}".format(work))

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

    def check(label: str, result: dict, want_exit: int, want_count: int | None = None,
              want_cases: list[str] | None = None, detail_has=None,
              want_line: str | None = None) -> None:
        for line in render(result):
            print("  " + line)
        problems = []
        if result["exit"] != want_exit:
            problems.append("exit={} want {}".format(result["exit"], want_exit))
        if want_count is not None and result["count"] != want_count:
            problems.append("findings={} want {}".format(result["count"], want_count))
        if want_cases is not None:
            cases = sorted({item["case"] for item in result["findings"]})
            if cases != sorted(want_cases):
                problems.append("cases={} want {}".format(cases, sorted(want_cases)))
        if detail_has is not None:
            needles = [detail_has] if isinstance(detail_has, str) else list(detail_has)
            details = " | ".join(item["detail"] for item in result["findings"])
            for needle in needles:
                if needle not in details:
                    problems.append("detail lacks {!r} (got {!r})".format(needle, details))
        if want_line is not None and result["line"] != want_line:
            problems.append("line={!r} want {!r}".format(result["line"], want_line))
        mark(label, problems)

    def run(repo: Path | str, round_no: int = _ROUND_NO, allow: list[str] | None = None,
            tip: str = "master") -> dict:
        return evaluate(str(repo), round_no, tip, allow or [])

    clean_line = "ROUND_SCOPE_V2 round=73 cases=6 findings=0"

    try:
        seed = _build_seed(mod, work)

        # --- inherited cases: green reference and their r72 red fixtures ---------------
        clean = _clone(mod, seed, work / "fixtures/clean")
        check("clean", run(clean), 0, 0, want_line=clean_line)

        label_missing = _clone(mod, seed, work / "fixtures/label-missing")
        (label_missing / "plans/round-73-claims.md").unlink()
        _commit(mod, label_missing, "drop the round-73 plan")
        check("label-missing", run(label_missing), 1, 1, ["label"],
              detail_has="status=absent")

        label_wrong = _clone(mod, seed, work / "fixtures/label-wrong-round")
        _put(label_wrong, "plans/round-73-claims.md",
             "# kama round 71 \u2014 mislabelled\n\nbody\n")
        _commit(mod, label_wrong, "mislabelled heading")
        check("label-wrong-round", run(label_wrong), 1, 1, ["label"],
              detail_has="status=heading-mismatch")

        label_no_heading = _clone(mod, seed, work / "fixtures/label-no-heading")
        _put(label_no_heading, "plans/round-73-claims.md", "body only\n")
        _commit(mod, label_no_heading, "heading-less plan")
        check("label-no-heading", run(label_no_heading), 1, 1, ["label"],
              detail_has="status=no-heading")

        stray_root = _clone(mod, seed, work / "fixtures/stray-root")
        _put(stray_root, "stray-note.md", "uncommitted round work outside the wave dir\n")
        check("stray-root", run(stray_root), 1, 1, ["stray"],
              detail_has="stray-note.md")

        stray_renamed = _clone(mod, seed, work / "fixtures/stray-renamed")
        _fixture_git(mod, stray_renamed, "mv", "LOG.md", "moved name.md")
        check("stray-renamed", run(stray_renamed), 1, 2, ["stray"],
              detail_has="moved name.md")

        ignored_in_wave = _clone(mod, seed, work / "fixtures/ignored-in-wave")
        _put(ignored_in_wave, ".ufo/waves/round-73/scratch.log", "ignored evidence\n")
        check("ignored-in-wave", run(ignored_in_wave), 1, 2,
              ["ignored", "ignored-older-label"], detail_has="scratch.log")

        check("allow-exact", run(stray_root, allow=["stray-note.md"]), 0, 0,
              want_line=clean_line)

        allow_dir = _clone(mod, seed, work / "fixtures/allow-dir")
        _put(allow_dir, ".ufo/waves/round-73/records/new.out", "uncommitted record\n")
        check("allow-dir", run(allow_dir, allow=[".ufo/waves/round-73/records/"]), 0, 0,
              want_line=clean_line)

        subdir = _clone(mod, seed, work / "fixtures/subdir-repo")
        _put(subdir, "stray-note.md", "root-relative probe\n")
        check("subdir-repo", run(subdir / "corpus"), 1, 1, ["stray"],
              detail_has="stray-note.md status=??")

        # --- A5: worktree -------------------------------------------------------------
        worktree_dirty = _clone(mod, seed, work / "fixtures/worktree-dirty")
        worktree_wt = work / "fixtures/worktree-dirty-wt"
        if worktree_wt.exists():
            shutil.rmtree(worktree_wt)
        _fixture_git(mod, worktree_dirty, "worktree", "add", "-q", "--detach", str(worktree_wt))
        _put(worktree_wt, "LOG.md", "# log\ndirty in linked worktree\n")
        _put(worktree_wt, "stray-in-wt.txt", "untracked in linked worktree\n")
        check("worktree-red", run(worktree_dirty), 1, 2, ["worktree"],
              detail_has=[str(worktree_wt), "LOG.md", "stray-in-wt.txt"])
        check("worktree-allow", run(worktree_dirty, allow=["LOG.md"]), 1, 1, ["worktree"],
              detail_has="stray-in-wt.txt")

        worktree_clean = _clone(mod, seed, work / "fixtures/worktree-clean")
        worktree_clean_wt = work / "fixtures/worktree-clean-wt"
        if worktree_clean_wt.exists():
            shutil.rmtree(worktree_clean_wt)
        _fixture_git(mod, worktree_clean, "worktree", "add", "-q", "--detach",
                     str(worktree_clean_wt))
        check("worktree-green", run(worktree_clean), 0, 0, want_line=clean_line)

        # --- A6: ignored older/newer label -------------------------------------------
        older_label_red = _clone(mod, seed, work / "fixtures/older-label-red")
        _put(older_label_red, ".ufo/waves/round-72/hidden.log", "ignored work in round 72\n")
        check("older-label-red", run(older_label_red, round_no=71), 1, 1,
              ["ignored-older-label"], detail_has=".ufo/waves/round-72/hidden.log")

        older_label_green = _clone(mod, seed, work / "fixtures/older-label-green")
        _put(older_label_green, ".ufo/waves/round-71/old.log", "older ignored leftover\n")
        check("older-label-green", run(older_label_green), 0, 0, want_line=clean_line)

        # --- A7: submodule ------------------------------------------------------------
        subrepo = _make_submodule_repo(mod, work)

        submodule_red = _clone(mod, seed, work / "fixtures/submodule-red")
        _add_submodule(mod, submodule_red, subrepo)
        _put(submodule_red, "sub/child.txt", "modified inside the submodule\n")
        _put(submodule_red, "sub/leak.txt", "untracked inside the submodule\n")
        check("submodule-red", run(submodule_red), 1, 4, ["stray", "submodule"],
              detail_has=["sub child.txt", "sub leak.txt", "parent-record="])

        submodule_green = _clone(mod, seed, work / "fixtures/submodule-green")
        _add_submodule(mod, submodule_green, subrepo)
        check("submodule-green", run(submodule_green), 0, 0, want_line=clean_line)

        submodule_ignore_all = _clone(mod, seed, work / "fixtures/submodule-ignore-all")
        _add_submodule(mod, submodule_ignore_all, subrepo, ignore_all=True)
        _put(submodule_ignore_all, "sub/child.txt", "modified inside the submodule\n")
        _put(submodule_ignore_all, "sub/leak.txt", "untracked inside the submodule\n")
        check("submodule-ignore-all", run(submodule_ignore_all), 1, 3, ["submodule"],
              detail_has=["sub child.txt", "sub leak.txt", "parent-record="])

        submodule_uninit = _clone(mod, seed, work / "fixtures/submodule-uninitialised")
        _put(submodule_uninit, ".gitmodules",
             "[submodule \"ghost\"]\n\tpath = ghost\n\turl = https://example.invalid/ghost.git\n")
        _commit(mod, submodule_uninit, "declare an uninitialised submodule")
        uninit_result = run(submodule_uninit)
        problems = []
        if uninit_result["exit"] != 0:
            problems.append("exit={} want 0".format(uninit_result["exit"]))
        if uninit_result["skipped"] != [
                {"case": "submodule", "path": "ghost", "reason": "no-worktree"}]:
            problems.append("skipped={!r} want the ghost entry".format(
                uninit_result["skipped"]))
        rendered = "\n".join(render(uninit_result))
        if "ROUND_SCOPE_V2_SKIP submodule ghost reason=no-worktree" not in rendered:
            problems.append("skip line absent (got {!r})".format(rendered))
        mark("submodule-uninitialised-skip", problems)

        # --- exit-2 paths -------------------------------------------------------------
        try:
            evaluate(str(clean), _ROUND_NO, "deadbeefdeadbeef")
        except ScopeError as exc:
            mark("tip-unresolvable", [] if "does not resolve" in str(exc) else [str(exc)])
        else:
            mark("tip-unresolvable", ["evaluate accepted an unresolvable --tip"])

        bad_allow = subprocess.run(
            [sys.executable, os.path.abspath(__file__), "--repo", str(clean),
             "--round", str(_ROUND_NO), "--allow", "/etc/passwd"],
            capture_output=True, text=True, env=_child_env())
        mark("bad-allow", [] if bad_allow.returncode == 2 else
             ["exit={} want 2".format(bad_allow.returncode)])

        plain = work / "plain-dir"
        plain.mkdir(exist_ok=True)
        try:
            evaluate(str(plain), _ROUND_NO, "master")
        except ScopeError as exc:
            mark("not-a-git-repo", [] if "not a git repository" in str(exc) else [str(exc)])
        else:
            mark("not-a-git-repo", ["evaluate accepted a non-git directory"])

        misuse = subprocess.run(
            [sys.executable, os.path.abspath(__file__), "--repo", str(clean), "--tip", "master"],
            capture_output=True, text=True, env=_child_env())
        mark("cli-misuse", [] if misuse.returncode == 2 else
             ["exit={} want 2".format(misuse.returncode)])

        # --- json round-trip ----------------------------------------------------------
        json_run = subprocess.run(
            [sys.executable, os.path.abspath(__file__), "--repo", str(clean),
             "--round", str(_ROUND_NO), "--tip", "master", "--json"],
            capture_output=True, text=True, env=_child_env())
        problems = []
        if json_run.returncode != 0:
            problems.append("exit={} want 0".format(json_run.returncode))
        try:
            document = json.loads(json_run.stdout)
        except json.JSONDecodeError as exc:
            problems.append("unparseable json: {}".format(exc))
        else:
            if document.get("line") != clean_line:
                problems.append("line={!r} want {!r}".format(
                    document.get("line"), clean_line))
            if document.get("count") != 0 or document.get("exit") != 0:
                problems.append("count={!r} exit={!r}".format(
                    document.get("count"), document.get("exit")))
            if document.get("cases") != 6:
                problems.append("cases={!r} want 6".format(document.get("cases")))
        mark("json-roundtrip", problems)

        # --- predicate equals the plan at the tip -------------------------------------
        try:
            frozen = _plan_predicate_at_tip(mod, args.repo, _ROUND_NO, "master")
        except ScopeError as exc:
            frozen = None
            predicate_error = str(exc)
        else:
            predicate_error = ""
        if frozen is None:
            mark("predicate", ["plans/round-73-claims.md unreadable at master in --repo {}: {}"
                               .format(args.repo, predicate_error)])
        elif frozen == "":
            mark("predicate", ["plan has no round-scope blockquote"])
        else:
            problems = []
            if PREDICATE != frozen:
                problems.append("PREDICATE differs from the plan blockquote (len {} vs {})"
                                .format(len(PREDICATE), len(frozen)))
            if "\n" in PREDICATE:
                problems.append("PREDICATE is not one line")
            mark("predicate", problems)

        # --- do-nothing shim: the three survivors must score it red -------------------
        shim = work / "do-nothing-shim.py"
        shim.write_text(_SHIM_SOURCE, encoding="utf-8")
        print("SHIM a counter that only greps the plan heading; the three survivor "
              "fixtures must score it red")
        problems = []
        survivors = (
            ("worktree", worktree_dirty, 73),
            ("ignored-older-label", older_label_red, 71),
            ("submodule", submodule_ignore_all, 73),
        )
        for name, fixture, round_no in survivors:
            real = run(fixture, round_no=round_no)
            shim_run = subprocess.run([sys.executable, str(shim), str(fixture), str(round_no)],
                                      capture_output=True, text=True, env=_child_env())
            if real["exit"] != 1:
                problems.append("real counter exit={} on {} (want 1)".format(
                    real["exit"], name))
            if shim_run.returncode != 0:
                problems.append("shim exit={} on {} (want 0: it cannot see the work)".format(
                    shim_run.returncode, name))
        mark("shim-does-nothing", problems)
    except ScopeError as exc:
        print("ROUND_SCOPE_V2_SELFTEST could-not-evaluate: {}".format(exc))
        print("ROUND_SCOPE_V2_SELFTEST_WORK_KEPT {}".format(work))
        return 2
    except OSError as exc:
        print("ROUND_SCOPE_V2_SELFTEST could-not-evaluate: {}".format(
            mod._one_line(exc)))
        print("ROUND_SCOPE_V2_SELFTEST_WORK_KEPT {}".format(work))
        return 2

    print("ROUND_SCOPE_V2_SELFTEST pass={} fail={}".format(passed, len(failed)))
    if failed:
        print("ROUND_SCOPE_V2_SELFTEST_FAILED " + ",".join(failed))
        print("ROUND_SCOPE_V2_SELFTEST_WORK_KEPT {}".format(work))
        return 1
    shutil.rmtree(work, ignore_errors=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Round-73 C1 round scope v2: the frozen claims plan at the tip, whole-repo "
                    "uncommitted records in the primary and every linked worktree, git-ignored "
                    "records under present round-<M> wave dirs with M >= N, and initialized "
                    "submodule worktrees."
    )
    ap.add_argument("--repo", default=".",
                    help="lane repository to grade (default: current directory)")
    ap.add_argument("--round", dest="round_no", type=int, default=None,
                    help="round number whose claims plan and wave dirs are graded (required)")
    ap.add_argument("--tip", default="master",
                    help="revision whose committed claims plan is read (default: master)")
    ap.add_argument("--allow", action="append", default=None, metavar="PATH",
                    help="repository-relative record path allowed to be uncommitted; "
                         "repeatable; a trailing / declares a directory prefix")
    ap.add_argument("--work", default=None,
                    help="selftest scratch dir (must be absent or empty; "
                         "default: fresh TMPDIR directory)")
    ap.add_argument("--selftest", action="store_true", help="run the fixture selftest")
    ap.add_argument("--json", action="store_true",
                    help="emit one JSON document instead of the human lines")
    args = ap.parse_args(argv)

    if args.selftest:
        return run_selftest(args)
    if args.round_no is None:
        ap.error("--round is required (or use --selftest)")
    if args.round_no < 1:
        print("ROUND_SCOPE_V2 could-not-evaluate round={} (round must be >= 1)".format(
            args.round_no))
        return 2

    try:
        result = evaluate(args.repo, args.round_no, args.tip, args.allow)
    except ScopeError as exc:
        print("ROUND_SCOPE_V2 could-not-evaluate round={}: {}".format(args.round_no, exc))
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for line in render(result):
            print(line)
    return result["exit"]


if __name__ == "__main__":
    sys.exit(main())
