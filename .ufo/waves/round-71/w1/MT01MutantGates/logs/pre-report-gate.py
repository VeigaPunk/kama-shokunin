#!/usr/bin/env python3
"""pre-report-gate.py - round-71 C1 (calibration): the round's pre-report verdict in one gate.

Predicate (frozen: plans/round-71-claims.md section C1; the same sentence is the
counter's code comment and the receipt label):

    `python3 tools/pre-report-gate.py --repo <lane> --round <N> --tip <rev>` prints one
    `PRE_REPORT round=<N> arms=5 failed=<f> uncommitted=<u>` line and exits 0 only when
    the four reconciled instruments (selfdesc reconciler, newest-closure counter,
    receipt-pointer audit, worktree-landing check) are all green AND no path under
    `.ufo/waves/round-<N>/` is uncommitted; it exits 1 naming every failed arm otherwise.

Arms, in fixed order, every one run with cwd = --repo:
  1 selfdesc          tools/round42-selfdesc-reconcile.py     --repo <repo> --tip <tip>
  2 newest-closure    tools/round69-newest-closure-counter.py --repo <repo> --rev <tip> --since-round 63
  3 receipt-audit     tools/round68-receipt-pointer-audit.py  --repo <repo> --rev <tip>
  4 worktree-landing  tools/round67-worktree-landing-check.py --repo <repo>
  5 round-clean       git -C <repo> status --porcelain -uall -- .ufo/waves/round-<N>

`failed` counts the arms that did not pass (arm 5 fails when its porcelain output is
non-empty); `uncommitted` is the number of non-empty porcelain records from arm 5.
Because `-uall` expands untracked directories into individual files, one record is one
file -- `.ufo/waves/round-70` at the round-71 start carries 26 files (the freeze's
count), which the plain-status form collapses into 14 entries. Exit: 0 iff
`failed == 0 and uncommitted == 0`, else 1. Exit 2 is reserved for CLI misuse (missing
--round, --repo not a directory) and for an unevaluable selftest fixture; a scored run
never exits 2, it names the failing arms and exits 1. Exit 3 is reserved for re-entry:
a gate whose environment already carries PRE_REPORT_GATE_DEPTH >= 1 refuses to evaluate
and prints `PRE_REPORT_RECURSION depth=<d> ...`. That chain is real -- a SCORECARD
`run` fact that executes the scored gate recurses gate -> selfdesc reconciler ->
round-41 run-fact harness -> gate (the harness runs the fact command with a 300 s
timeout in a clone of the tip) -- so a run fact must cite
`python3 tools/pre-report-gate.py --selftest` (which touches no lane instrument) rather
than the scored gate. The guard bounds the recursion to one refused re-entry instead of
an unbounded process chain; it never fires for a normal scored run.



Output (default mode; one line per arm in the order above, then the verdict):
    PRE_REPORT_ARM <name> exit=<e> ok|FAIL <detail>
    PRE_REPORT round=<N> arms=5 failed=<f> uncommitted=<u>

`--json` replaces the human lines with one JSON document whose "line" field carries the
same PRE_REPORT verdict string. Child processes get stdout+stderr captured, a 600 s
timeout each, cwd = --repo, the caller's environment (so TMPDIR is honoured) and
PYTHONDONTWRITEBYTECODE=1 (the gate must not grow a __pycache__ in the repo it grades).

Instrument wiring
  By default the four scripts are resolved as <repo>/tools/<name>. `--tools-dir DIR`
  overrides the directory (default None); the selftest uses it to inject three stub
  instruments next to a copy of the real round67-worktree-landing-check.py, so the
  fixture arms exercise this gate's wiring (arm names, counts, exit map) while the
  landing arm keeps the real byte-comparison instrument -- fixture arms (d), (e) and (f)
  below are therefore real DIRTY/MISSING detections, not stub exits.

Selftest (--selftest; fixtures under --work, or a fresh TMPDIR tempdir)
  (a) green fixture                              -> exit 0, failed=0 uncommitted=0
  (b) one uncommitted file under the wave dir    -> exit 1, round-clean FAIL, uncommitted=1
  (c) red newest-closure stub (stale pointer)    -> exit 1, newest-closure FAIL
  (d) missing declared path (PROVINCE.md)        -> exit 1, worktree-landing FAIL (MISSING)
  (e) byte-changed declared path (SCORECARD.md)  -> exit 1, worktree-landing FAIL (DIRTY)
  (f) CRLF-translated declared path (SKILL.md)   -> exit 1, worktree-landing FAIL (DIRTY)
  Prints PASS/FAIL per arm and `PRE_REPORT_SELFTEST pass=<n> fail=0`; exit 0 iff every
  arm passed. A fixture tree that cannot be built or verified is a could-not-evaluate
  (exit 2), never a pass. The fixture commits into its own throwaway repository only,
  after asserting `git rev-parse --show-toplevel` equals the fixture directory.

Receipts for this tool live under .ufo/waves/round-71/w1/EX01PreReportGate/.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

PREDICATE = (
    "`python3 tools/pre-report-gate.py --repo <lane> --round <N> --tip <rev>` prints one "
    "`PRE_REPORT round=<N> arms=5 failed=<f> uncommitted=<u>` line and exits 0 only when "
    "the four reconciled instruments (selfdesc reconciler, newest-closure counter, "
    "receipt-pointer audit, worktree-landing check) are all green AND no path under "
    "`.ufo/waves/round-<N>/` is uncommitted; it exits 1 naming every failed arm otherwise."
)

ARM_TIMEOUT = 600
ARM_SPECS = [
    ("selfdesc", ("round42-selfdesc-reconcile.py", "--repo", "{repo}", "--tip", "{tip}")),
    ("newest-closure", ("round69-newest-closure-counter.py", "--repo", "{repo}",
                        "--rev", "{tip}", "--since-round", "63")),
    ("receipt-audit", ("round68-receipt-pointer-audit.py", "--repo", "{repo}", "--rev", "{tip}")),
    ("worktree-landing", ("round67-worktree-landing-check.py", "--repo", "{repo}")),
]
ARM_ORDER = [name for name, _ in ARM_SPECS] + ["round-clean"]
VERDICT_RE = {
    "selfdesc": r"mismatches=\d+ met=(?:True|False)",
    "newest-closure": r"(?:NEWEST_CLOSURE|STALE_CALIBRATION) ",
    "receipt-audit": r"RECEIPT_POINTER_AUDIT ",
    "worktree-landing": r"WORKTREE_LANDING_CHECK ",
}
DEFECT_RE = re.compile(r"(?:DIRTY|MISSING|UNTRACKED|UNREADABLE) ")


def _decode(data) -> str:
    if not data:
        return ""
    if isinstance(data, str):
        return data
    return data.decode("utf-8", "replace")


def _one_line(text: str, limit: int = 240) -> str:
    flat = re.sub(r"\s+", " ", text).strip()
    return flat[:limit] if len(flat) > limit else flat


def _last_line(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines[-1] if lines else ""


def _detail(name: str, text: str, fallback: str | None = None) -> str:
    """One-line arm detail: the arm's own verdict line (last match), else its last line.

    For arm 4 the first concrete defect record (DIRTY/MISSING/UNTRACKED/UNREADABLE) is
    appended, so a failed landing names the path that broke it.
    """
    if fallback:
        return _one_line(fallback)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    chosen = ""
    pattern = VERDICT_RE.get(name)
    if pattern:
        matches = [ln for ln in lines if re.search(pattern, ln)]
        if matches:
            chosen = matches[-1]
    if not chosen and lines:
        chosen = lines[-1]
    if not chosen:
        chosen = "(no output)"
    defects = [ln for ln in lines if DEFECT_RE.match(ln)]
    if name == "worktree-landing" and defects:
        chosen = chosen + " | " + defects[0]
    return _one_line(chosen)


DEPTH_ENV = "PRE_REPORT_GATE_DEPTH"


def _gate_depth() -> int:
    """The gate's own nesting level (0 for any normal invocation)."""
    try:
        return max(0, int(os.environ.get(DEPTH_ENV, "0")))
    except (TypeError, ValueError):
        return 0


def _kill_tree(proc: subprocess.Popen) -> None:
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (AttributeError, OSError):
        proc.kill()


def _run(argv: list[str], cwd: str, depth: int = 0) -> tuple[int, str, str | None]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env[DEPTH_ENV] = str(depth + 1)
    try:
        proc = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env=env, start_new_session=True)
    except OSError as exc:
        return 127, "", f"spawn failed: {exc}"
    try:
        out, err = proc.communicate(timeout=ARM_TIMEOUT)
    except subprocess.TimeoutExpired:
        _kill_tree(proc)
        out, err = proc.communicate()
        return 124, _decode(out) + _decode(err), f"timeout after {ARM_TIMEOUT}s"
    return proc.returncode, _decode(out) + _decode(err), None


def evaluate(repo: str, round_no: int, tip: str = "master", tools_dir: str | None = None,
             depth: int = 0) -> dict:
    """Run the five arms and derive the pinned verdict; the only scoring entry point."""
    repo_path = os.path.realpath(repo)
    tools_path = os.path.realpath(tools_dir) if tools_dir else os.path.join(repo_path, "tools")
    arms: list[dict] = []
    for name, template in ARM_SPECS:
        script = os.path.join(tools_path, template[0])
        argv = [sys.executable, script] + [
            token.replace("{repo}", repo_path).replace("{tip}", tip) for token in template[1:]
        ]
        code, text, spawn_error = _run(argv, repo_path, depth)
        arms.append({
            "name": name,
            "argv": argv,
            "exit": code,
            "ok": code == 0,
            "detail": _detail(name, text, spawn_error),
        })

    wave_rel = f".ufo/waves/round-{round_no}"
    argv_clean = ["git", "-C", repo_path, "status", "--porcelain", "-uall", "--", wave_rel]
    code_clean, text_clean, spawn_error = _run(argv_clean, repo_path, depth)
    records = [ln for ln in text_clean.splitlines() if ln.strip()]
    uncommitted = len(records) if code_clean == 0 else 0
    if spawn_error:
        detail_clean = _one_line(spawn_error)
    elif code_clean != 0:
        detail_clean = _one_line(f"git status exit={code_clean} {_last_line(text_clean)}")
    elif uncommitted:
        detail_clean = _one_line(f"files={uncommitted} first={records[0]}")
    else:
        detail_clean = "files=0"
    arms.append({
        "name": "round-clean",
        "argv": argv_clean,
        "exit": code_clean,
        "ok": code_clean == 0 and uncommitted == 0,
        "detail": detail_clean,
    })

    failed = sum(1 for arm in arms if not arm["ok"])
    verdict = f"PRE_REPORT round={round_no} arms={len(arms)} failed={failed} uncommitted={uncommitted}"
    return {
        "repo": repo_path,
        "round": round_no,
        "tip": tip,
        "arms": arms,
        "failed": failed,
        "uncommitted": uncommitted,
        "exit": 0 if failed == 0 and uncommitted == 0 else 1,
        "line": verdict,
    }


def render(result: dict) -> list[str]:
    lines = []
    for arm in result["arms"]:
        status = "ok" if arm["ok"] else "FAIL"
        lines.append(f"PRE_REPORT_ARM {arm['name']} exit={arm['exit']} {status} {arm['detail']}")
    lines.append(result["line"])
    return lines


# ---------------------------------------------------------------------------
# Selftest fixtures. Nothing below touches the graded repository: the fixture is
# a throwaway git repository under --work, its tools dir holds three stubs plus a
# copy of the real landing check, and every git mutation is scoped with -C and
# guarded by a toplevel assertion.
# ---------------------------------------------------------------------------

_STUB_COMMON = '''\
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def red(arm):
    path = os.path.join(HERE, "red-arms.txt")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return arm in fh.read().split()
    except FileNotFoundError:
        return False
'''

_STUB_SELFDESC = _STUB_COMMON + '''
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default=".")
ap.add_argument("--tip", default="HEAD")
a = ap.parse_args()
print("tip={}".format(a.tip))
if red("selfdesc"):
    print("r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 "
          "province=0 rel=0 closure_ptr=0 mismatches=1 met=False")
    print("detail: stub-red selfdesc")
    raise SystemExit(1)
print("r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 "
      "province=0 rel=0 closure_ptr=1 mismatches=0 met=True")
raise SystemExit(0)
'''

_STUB_NEWEST = _STUB_COMMON + '''
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default=".")
ap.add_argument("--rev", default="HEAD")
ap.add_argument("--since-round", type=int, default=1)
a = ap.parse_args()
if red("newest-closure"):
    print("NEWEST_CLOSURE newest=corpus/lessons/round-70-verifier-spotcheck.md "
          "date=2026-11-03 round=70 row_names=corpus/lessons/round-69-verifier-spotcheck.md "
          "row_current=false")
    print("STALE_CALIBRATION row_names=corpus/lessons/round-69-verifier-spotcheck.md "
          "newest=corpus/lessons/round-70-verifier-spotcheck.md newest_date=2026-11-03")
    raise SystemExit(1)
print("NEWEST_CLOSURE newest=corpus/lessons/round-69-verifier-spotcheck.md "
      "date=2026-11-01 round=69 row_names=corpus/lessons/round-69-verifier-spotcheck.md "
      "row_current=true")
raise SystemExit(0)
'''

_STUB_RECEIPT = _STUB_COMMON + '''
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default=".")
ap.add_argument("--rev", default="HEAD")
a = ap.parse_args()
if red("receipt-audit"):
    print("RECEIPT_POINTER_AUDIT files=2 cited=0 resolved=0 expanded=0 corrected=0 unresolved=1")
    raise SystemExit(1)
print("RECEIPT_POINTER_AUDIT files=2 cited=0 resolved=0 expanded=0 corrected=0 unresolved=0")
raise SystemExit(0)
'''

_FIXTURE_FILES = {
    "SCORECARD.md": b"# Scorecard (pre-report-gate selftest fixture)\n\n## Axes\n\n"
                    b"| axis | score |\n|---|---|\n| calibration | 7 |\n",
    "LOG.md": b"# Log (fixture)\n\n- fixture round\n",
    "PROVINCE.md": b"# Province (fixture)\n",
    "SKILL.md": b"# Skill (fixture)\n\none\ntwo\n",
    "corpus/SOURCES.md": b"# Sources (fixture)\n",
    ".ufo/waves/round-70/evidence.txt": b"committed fixture evidence\n",
}


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise RuntimeError(
            "git {} failed rc={}: {}".format(" ".join(args), proc.returncode, proc.stderr.strip())
        )
    return proc


def _fixture_repo(work: Path) -> Path:
    repo = work / "repo"
    repo.mkdir(parents=True)
    _git(repo, "init", "-q", "-b", "master")
    top = _git(repo, "rev-parse", "--show-toplevel").stdout.strip()
    if os.path.realpath(top) != os.path.realpath(str(repo)):
        raise RuntimeError(f"fixture toplevel {top!r} is not the fixture dir {str(repo)!r}")
    _git(repo, "config", "core.autocrlf", "false")
    for rel, body in _FIXTURE_FILES.items():
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=pre-report-selftest", "-c", "user.email=kama@invalid",
         "-c", "commit.gpgsign=false", "commit", "-q", "-m", "fixture")
    return repo


def run_selftest(args) -> int:
    if args.work:
        work = Path(args.work).resolve()
        if work.exists() and (not work.is_dir() or any(work.iterdir())):
            print(f"PRE_REPORT_SELFTEST could-not-evaluate: --work {work} is not an empty directory")
            return 2
    else:
        work = Path(tempfile.mkdtemp(prefix="pre-report-gate-selftest-"))
    work.mkdir(parents=True, exist_ok=True)
    print(f"PRE_REPORT_SELFTEST_WORK {work}")

    real_wlc = Path(__file__).resolve().parent / "round67-worktree-landing-check.py"
    if not real_wlc.is_file():
        print(f"PRE_REPORT_SELFTEST could-not-evaluate: real instrument missing at {real_wlc}")
        return 2

    tools = work / "tools"
    tools.mkdir()
    shutil.copy2(real_wlc, tools / "round67-worktree-landing-check.py")
    (tools / "round42-selfdesc-reconcile.py").write_text(_STUB_SELFDESC, encoding="utf-8")
    (tools / "round69-newest-closure-counter.py").write_text(_STUB_NEWEST, encoding="utf-8")
    (tools / "round68-receipt-pointer-audit.py").write_text(_STUB_RECEIPT, encoding="utf-8")
    red_file = tools / "red-arms.txt"
    red_file.write_text("", encoding="utf-8")

    try:
        repo = _fixture_repo(work)
    except (RuntimeError, OSError) as exc:
        print(f"PRE_REPORT_SELFTEST could-not-evaluate: {exc}")
        return 2

    originals = {rel: (repo / rel).read_bytes() for rel in _FIXTURE_FILES}
    round_no = 70
    passed = 0
    failed_arms: list[str] = []

    def check(label: str, result: dict, want_exit: int, want_failed: int,
              want_uncommitted: int, arm: str, want_ok: bool,
              detail_has: str | None = None, want_line: str | None = None) -> None:
        nonlocal passed
        for line in render(result):
            print(f"  {line}")
        problems = []
        if result["exit"] != want_exit:
            problems.append(f"exit={result['exit']} want {want_exit}")
        if result["failed"] != want_failed:
            problems.append(f"failed={result['failed']} want {want_failed}")
        if result["uncommitted"] != want_uncommitted:
            problems.append(f"uncommitted={result['uncommitted']} want {want_uncommitted}")
        if [a["name"] for a in result["arms"]] != ARM_ORDER:
            problems.append(f"arm order {[a['name'] for a in result['arms']]}")
        target = next((a for a in result["arms"] if a["name"] == arm), None)
        if target is None:
            problems.append(f"arm {arm} missing")
        else:
            if target["ok"] != want_ok:
                problems.append(f"{arm} ok={target['ok']} want {want_ok}")
            if detail_has is not None and detail_has not in target["detail"]:
                problems.append(f"{arm} detail lacks {detail_has!r} (got {target['detail']!r})")
        if want_line is not None and result["line"] != want_line:
            problems.append(f"line={result['line']!r} want {want_line!r}")
        if problems:
            failed_arms.append(label)
            print(f"FAIL {label} :: " + "; ".join(problems))
        else:
            passed += 1
            print(f"PASS {label}")

    # (a) green fixture: the target shape, exit 0.
    check("green", evaluate(repo, round_no, "master", str(tools)), 0, 0, 0, "round-clean", True,
          want_line="PRE_REPORT round=70 arms=5 failed=0 uncommitted=0")

    # (b) one uncommitted file under the round's wave dir.
    extra = repo / ".ufo/waves/round-70/extra.out"
    extra.write_bytes(b"uncommitted fixture file\n")
    check("wave-uncommitted", evaluate(repo, round_no, "master", str(tools)), 1, 1, 1,
          "round-clean", False, detail_has="files=1")
    extra.unlink()

    # (c) red newest-closure stub: a stale pointer is a named arm failure.
    red_file.write_text("newest-closure\n", encoding="utf-8")
    check("stale-newest-closure", evaluate(repo, round_no, "master", str(tools)), 1, 1, 0,
          "newest-closure", False, detail_has="STALE_CALIBRATION")
    red_file.write_text("", encoding="utf-8")

    # (d) a declared self-record path missing from the worktree (real landing check).
    (repo / "PROVINCE.md").unlink()
    check("missing-declared-path", evaluate(repo, round_no, "master", str(tools)), 1, 1, 0,
          "worktree-landing", False, detail_has="MISSING PROVINCE.md")
    (repo / "PROVINCE.md").write_bytes(originals["PROVINCE.md"])

    # (e) a byte-changed declared path.
    with open(repo / "SCORECARD.md", "ab") as fh:
        fh.write(b"dirty trailing line\n")
    check("dirty-declared-path", evaluate(repo, round_no, "master", str(tools)), 1, 1, 0,
          "worktree-landing", False, detail_has="DIRTY SCORECARD.md")
    (repo / "SCORECARD.md").write_bytes(originals["SCORECARD.md"])

    # (f) a CRLF-translated declared path (same lines, different bytes).
    (repo / "SKILL.md").write_bytes(originals["SKILL.md"].replace(b"\n", b"\r\n"))
    check("crlf-declared-path", evaluate(repo, round_no, "master", str(tools)), 1, 1, 0,
          "worktree-landing", False, detail_has="DIRTY SKILL.md")
    (repo / "SKILL.md").write_bytes(originals["SKILL.md"])

    total = passed + len(failed_arms)
    print(f"PRE_REPORT_SELFTEST pass={passed} fail={len(failed_arms)}")
    if failed_arms:
        print("PRE_REPORT_SELFTEST_FAILED " + ",".join(failed_arms))
        print(f"PRE_REPORT_SELFTEST_WORK_KEPT {work}")
        return 1
    if not args.keep:
        shutil.rmtree(work, ignore_errors=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="One pre-report gate: four reconciled instruments plus round-worktree cleanliness (round 71)."
    )
    ap.add_argument("--repo", default=".", help="repository to grade (default: current directory)")
    ap.add_argument("--round", dest="round_no", type=int, default=None,
                    help="round number whose .ufo/waves/round-<N> dir is graded (required)")
    ap.add_argument("--tip", default="master", help="revision the instruments evaluate (default: master)")
    ap.add_argument("--selftest", action="store_true", help="run the fixture selftest")
    ap.add_argument("--json", action="store_true", help="emit one JSON document instead of the human lines")
    ap.add_argument("--tools-dir", default=None,
                    help="directory holding the four instrument scripts (default: <repo>/tools)")
    ap.add_argument("--work", default=None,
                    help="selftest scratch dir (must be absent or empty; default: fresh TMPDIR dir)")
    ap.add_argument("--keep", action="store_true", help="keep the selftest scratch dir")
    args = ap.parse_args(argv)

    if args.selftest:
        return run_selftest(args)
    depth = _gate_depth()
    if depth:
        print(f"PRE_REPORT_RECURSION depth={depth} refused: the scored gate is being re-entered "
              f"through an executed SCORECARD run fact (gate -> selfdesc reconciler -> round-41 "
              f"run-fact harness -> gate); cite `python3 tools/pre-report-gate.py --selftest` "
              f"there instead")
        return 3
    if args.round_no is None:
        ap.error("--round is required (or use --selftest)")
    if not os.path.isdir(args.repo):
        print(f"PRE_REPORT could-not-evaluate round={args.round_no} repo={args.repo!r} (not a directory)")
        return 2

    result = evaluate(args.repo, args.round_no, args.tip, args.tools_dir)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for line in render(result):
            print(line)
    return result["exit"]


if __name__ == "__main__":
    sys.exit(main())
