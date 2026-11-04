#!/usr/bin/env python3
"""pre-report-gate.py - round-71 C1 (calibration), round-72 C1 (six arms), round-73 C1
(six-case round-scope arm), round-74 C1-C3 wiring (arm 7 `round74-v2`): the round's
pre-report verdict in one gate.

Predicate (frozen: plans/round-71-claims.md section C1, amended by
plans/round-72-claims.md section C1 and the plans/round-74-claims.md sections C1-C3
wiring note; the same sentence is this gate's PREDICATE and the receipt label. Round 73
section C1 re-points arm 5 at the six-case counter without amending that sentence;
round 74 adds arm 7 and moves the arm count 6 -> 7):

    `python3 tools/pre-report-gate.py --repo <lane> --round <N> --tip <rev>` prints one
    `PRE_REPORT round=<N> arms=8 failed=<f> uncommitted=<u>` line and exits 0 only when
    the five reconciled instruments (selfdesc reconciler, newest-closure counter,
    receipt-pointer audit, worktree-landing check, round-scope counter) plus the three
    round-74 v2 counters arm 7 composes (selfdesc canon, receipt-claim binding,
    province host drift) are all green AND no path under `.ufo/waves/round-<N>/` is
    uncommitted; it exits 1 naming every failed arm otherwise.

The round-71 receipt -- `PRE_REPORT round=71 arms=5 failed=0 uncommitted=0` -- is that
round's five-arm measurement and stays readable as one: five arms is the population round
71 had. From round 72 on the gate printed `arms=6`; from round 74 on it printed `arms=7`
and from round 75 on it prints `arms=8`. A five-arm line can only be a round-71 record, a
six-arm line a round-72/73 record, a seven-arm line a round-74 record.

Arms, in fixed order, every one run with cwd = --repo:
  1 selfdesc          tools/round42-selfdesc-reconcile.py      --repo <repo> --tip <tip>
  2 newest-closure    tools/round69-newest-closure-counter.py  --repo <repo> --rev <tip> --since-round 63
  3 receipt-audit     tools/round68-receipt-pointer-audit.py   --repo <repo> --rev <tip>
  4 worktree-landing  tools/round67-worktree-landing-check.py  --repo <repo>
  5 round-scope       tools/round73-round-scope-cases.py       --repo <repo> --round <N> --tip <tip>
  6 round-clean       git -C <repo> status --porcelain -uall -- .ufo/waves/round-<N>
  7 round74-v2        tools/round74-selfdesc-canon.py          --repo <repo>
                      tools/round74-receipt-claim-binding.py   --repo <repo> --round <N> --tip <tip>
                      tools/round74-province-host-drift.py     --repo <repo>
  8 round75-instruments tools/round75-interpretation-pins.py   --repo <repo>
                      tools/round75-survivor-probe.py          --repo <repo>
                      tools/round75-append-accepted.py         --repo <repo>

`round-scope` is the round-72 C1 addition -- the sixth arm the gate has ever had, executed
fifth because `ARM_ORDER` derives every instrument arm from `ARM_SPECS` and keeps the
built-in cleanliness check last. Round 73 re-points it at
`tools/round73-round-scope-cases.py`, which grades six cases: the three inherited ones
(`label`, `stray`, `ignored`) plus one per survivor class the round-72 closure recorded --
`worktree` (A5, dirt in a linked worktree), `ignored-older-label` (A6, a valid older-round
label hiding another round's ignored work) and `submodule` (A7,
`submodule.<name>.ignore=all`). It grades the round's own scope rather than only its wave
dir: `plans/round-<N>-claims.md` exists at `<tip>` with a first heading naming round `<N>`,
no uncommitted path outside the declared record allow-list in the primary worktree or in
any linked worktree, no git-ignored path under any `.ufo/waves/round-<M>/` with
`M >= <N>`, and no uncommitted or untracked content in an initialized submodule worktree;
it prints `ROUND_SCOPE_V2 round=<N> cases=6 findings=<f>` and names each
`ROUND_SCOPE_V2_FINDING <case> <detail>`. The wave-dir porcelain check alone is vacuously
green for a wrong `--round` label, for round work outside the wave dir, for a git-ignored
file inside it, and for all three survivor classes (measured at the round-72 base:
`.ufo/waves/round-72/measured/before/round-scope-control-old.out`,
`SCOPE_CONTROL cases=3 base_green=3 killed=0`, exit 1 -- the round-72 counter's own
three-case measurement is `ROUND_SCOPE round=<N> cases=3 findings=<f>`; that counter stays
byte-frozen at `tools/round72-round-scope.py` and its line is never re-issued here).

`round74-v2` is the round-74 C1-C3 addition -- the seventh arm, executed last, after the
built-in wave-dir cleanliness check. It composes the three round-74 v2 counters, each run
with cwd = --repo and resolved from <repo>/tools (or --tools-dir) exactly like the other
instrument scripts: `round74-selfdesc-canon.py --repo <repo>` (the C1 heading-visibility
counter printing `SELFDESC_CANON_V2 ...`), `round74-receipt-claim-binding.py --repo <repo>
--round <N> --tip <tip>` (the C2 explicit-revision claim-binding counter printing
`RECEIPT_CLAIM_V2 ...`) and `round74-province-host-drift.py --repo <repo>` (the C3
base-revision host-block preservation counter printing `PROVINCE_HOST_DRIFT_V2 ...`). The
arm is green only when all three exit 0. A module absent from the tools dir fails the arm
closed naming the absent script, never vacuously green; a module that exits non-zero fails
the arm, its detail carrying all three counters' verdict lines, the failing counter's
first `*_V2_FINDING` line and a `missing <script>` record per absent module.

`round75-instruments` is the round-75 addition -- the eighth arm, executed last. It composes
`tools/round75-interpretation-pins.py --repo <repo>` (C1, printing `INTERPRETATION_PINS
pins=<n> declared=<d> killed=<k> escaped=<e>`), `tools/round75-survivor-probe.py --repo
<repo>` (C2, printing `SURVIVORS2 mutants=<m> killed=<k> escaped=<e>`) and
`tools/round75-append-accepted.py --repo <repo>` (C3, printing `APPEND_ACCEPTED events=<e>
accepted=<a> unaccepted=<u> bad_rows=<r> bad_declarations=<d>`), resolved exactly like the
other instruments. The arm is green only when all three exit 0 and fails closed on an absent
module, naming `missing <script>`; a failing counter contributes its verdict line and first
`*_FINDING` line to the arm's detail.

`failed` counts the arms that did not pass (arm 6 fails when its porcelain output is
non-empty; arm 5 fails when the counter exits non-zero, which it does whenever it has a
finding; arm 7 fails when any of its three counters is absent or exits non-zero);
`uncommitted` is the number of non-empty porcelain records from arm 6 only.
Because `-uall` expands untracked directories into individual files, one record is one
file -- `.ufo/waves/round-70` at the round-71 start carries 26 files (the freeze's
count), which the plain-status form collapses into 14 entries. Exit: 0 iff
`failed == 0 and uncommitted == 0` across all seven arms, else 1. Exit 2 is reserved for CLI
misuse (missing --round, --repo not a directory) and for an unevaluable selftest fixture; a
scored run never exits 2, it names the failing arms and exits 1. Exit 3 is reserved for
re-entry: a gate whose environment already carries PRE_REPORT_GATE_DEPTH >= 1 refuses to
evaluate and prints `PRE_REPORT_RECURSION depth=<d> ...`. That chain is real -- a SCORECARD
`run` fact that executes the scored gate recurses gate -> selfdesc reconciler ->
round-41 run-fact harness -> gate (the harness runs the fact command with a 300 s
timeout in a clone of the tip) -- so a run fact must cite
`python3 tools/pre-report-gate.py --selftest` (which touches no lane instrument) rather
than the scored gate. The guard bounds the recursion to one refused re-entry instead of
an unbounded process chain; it never fires for a normal scored run.



Output (default mode; one line per arm in the order above, then the verdict):
    PRE_REPORT_ARM <name> exit=<e> ok|FAIL <detail>
    PRE_REPORT round=<N> arms=8 failed=<f> uncommitted=<u>

`--json` replaces the human lines with one JSON document whose "line" field carries the
same PRE_REPORT verdict string. Child processes get stdout+stderr captured, a 600 s
timeout each, cwd = --repo, the caller's environment (so TMPDIR is honoured) and
PYTHONDONTWRITEBYTECODE=1 (the gate must not grow a __pycache__ in the repo it grades).

Instrument wiring
  By default the instrument scripts are resolved as <repo>/tools/<name>. `--tools-dir
  DIR` overrides the directory (default None); the selftest uses it to inject four stub
  instruments next to a copy of the real round67-worktree-landing-check.py, so the
  fixture arms exercise this gate's wiring (arm names, counts, exit map) while the
  landing arm keeps the real byte-comparison instrument -- fixture arms (d), (e) and (f)
  below are therefore real DIRTY/MISSING detections, not stub exits. The last three
  fixture arms copy the real `tools/round73-round-scope-cases.py` (and the byte-frozen
  `tools/round72-round-scope.py` it imports) into the same tools dir, so arm 5 is also
  exercised as the module this gate ships with, on a clean fixture and on the A5/A6
  survivor shapes; a missing module is a could-not-evaluate, never a pass. Arm 7
  resolves its three counters the same way and the selftest injects one stub per
  counter, so the arm's composition, its fail-closed absence handling and its
  per-counter detail are all exercised without the real round-74 modules being present.

Selftest (--selftest; fixtures under --work, or a fresh TMPDIR tempdir)
  (a) green fixture                              -> exit 0, failed=0 uncommitted=0
  (b) one uncommitted file under the wave dir    -> exit 1, round-clean FAIL, uncommitted=1
  (c) red newest-closure stub (stale pointer)    -> exit 1, newest-closure FAIL
  (d) missing declared path (PROVINCE.md)        -> exit 1, worktree-landing FAIL (MISSING)
  (e) byte-changed declared path (SCORECARD.md)  -> exit 1, worktree-landing FAIL (DIRTY)
  (f) CRLF-translated declared path (SKILL.md)   -> exit 1, worktree-landing FAIL (DIRTY)
  (g) red round-scope stub (findings=1)          -> exit 1, round-scope FAIL, finding named
  (h) green round-scope stub                     -> exit 0, verdict `arms=6`
  (i) real round-scope counter, clean fixture    -> exit 0, `ROUND_SCOPE_V2 ... findings=0`
  (j) real counter, dirty linked worktree (A5)   -> exit 1, round-scope FAIL naming `worktree`
  (k) real counter, ignored file under round-71  -> exit 1, round-scope FAIL naming
                                                    `ignored-older-label` (A6; M=71 >= N=70)
  (l) arm-5 verdict selector                     -> picks `ROUND_SCOPE_V2 ` over a later line
  (m) red canon stub inside arm 7                -> exit 1, round74-v2 FAIL naming
                                                    SELFDESC_CANON_V2_FINDING
  (n) green arm-7 stubs                          -> exit 0, verdict `arms=8`
  (o) drift-v2 stub deleted                      -> exit 1, round74-v2 FAIL naming the
                                                    absent round74-province-host-drift.py
  (p) red pins stub inside arm 8                 -> exit 1, round75-instruments FAIL naming
                                                    INTERPRETATION_PINS_FINDING
  (q) green arm-8 stubs                          -> exit 0, verdict `arms=8`
  (r) append-accepted stub deleted               -> exit 1, round75-instruments FAIL naming
                                                    the absent round75-append-accepted.py
  Prints PASS/FAIL per arm and `PRE_REPORT_SELFTEST pass=<n> fail=0`; exit 0 iff every
  arm passed. A fixture tree that cannot be built or verified is a could-not-evaluate
  (exit 2), never a pass. The fixture commits into its own throwaway repository only,
  after asserting `git rev-parse --show-toplevel` equals the fixture directory.

Receipts for this tool live under .ufo/waves/round-71/w1/EX01PreReportGate/ (five-arm
build), .ufo/waves/round-72/w1/EX03GateArm6/ (six-arm amendment),
.ufo/waves/round-73/w1/EX04GateArm/ (six-case round-scope re-point) and
.ufo/waves/round-74/w1/EX04GateArm7/ (arm-7 `round74-v2` amendment, applied from
arm7.patch).
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
    "`PRE_REPORT round=<N> arms=8 failed=<f> uncommitted=<u>` line and exits 0 only when "
    "the five reconciled instruments (selfdesc reconciler, newest-closure counter, "
    "receipt-pointer audit, worktree-landing check, round-scope counter), the three "
    "round-74 v2 counters arm 7 composes (selfdesc canon, receipt-claim binding, "
    "province host drift) and the three round-75 counters arm 8 composes (interpretation "
    "pins, survivor probe, append-accepted accounting) are all green AND no path under "
    "`.ufo/waves/round-<N>/` is uncommitted; it exits 1 naming every failed arm otherwise."
)

ARM_TIMEOUT = 600
ARM_SPECS = [
    ("selfdesc", ("round42-selfdesc-reconcile.py", "--repo", "{repo}", "--tip", "{tip}")),
    ("newest-closure", ("round69-newest-closure-counter.py", "--repo", "{repo}",
                        "--rev", "{tip}", "--since-round", "63")),
    ("receipt-audit", ("round68-receipt-pointer-audit.py", "--repo", "{repo}", "--rev", "{tip}")),
    ("worktree-landing", ("round67-worktree-landing-check.py", "--repo", "{repo}")),
    ("round-scope", ("round73-round-scope-cases.py", "--repo", "{repo}", "--round", "{round}",
                     "--tip", "{tip}")),
]
ARM_ORDER = [name for name, _ in ARM_SPECS] + ["round-clean", "round74-v2",
              "round75-instruments"]
VERDICT_RE = {
    "selfdesc": r"mismatches=\d+ met=(?:True|False)",
    "newest-closure": r"(?:NEWEST_CLOSURE|STALE_CALIBRATION) ",
    "receipt-audit": r"RECEIPT_POINTER_AUDIT ",
    "worktree-landing": r"WORKTREE_LANDING_CHECK ",
    "round-scope": r"ROUND_SCOPE_V2 ",
    "round74-v2-canon": r"SELFDESC_CANON_V2 ",
    "round74-v2-claim-v2": r"RECEIPT_CLAIM_V2 ",
    "round74-v2-drift-v2": r"PROVINCE_HOST_DRIFT_V2 ",
    "round75-instruments-pins": r"INTERPRETATION_PINS ",
    "round75-instruments-survivors2": r"SURVIVORS2 ",
    "round75-instruments-append-accepted": r"APPEND_ACCEPTED ",
}
DEFECT_RE = re.compile(r"(?:DIRTY|MISSING|UNTRACKED|UNREADABLE) ")
SCOPE_FINDING_RE = re.compile(r"ROUND_SCOPE_V2_FINDING ")
V2_FINDING_RE = re.compile(
    r"(?:SELFDESC_CANON_V2|RECEIPT_CLAIM_V2|PROVINCE_HOST_DRIFT_V2)_FINDING ")
R75_FINDING_RE = re.compile(
    r"(?:INTERPRETATION_PINS|SURVIVORS2|APPEND_ACCEPTED)_FINDING ")
_DEFECT_ARMS = ("worktree-landing", "round-scope",
                "round74-v2-canon", "round74-v2-claim-v2", "round74-v2-drift-v2",
                "round75-instruments-pins", "round75-instruments-survivors2",
                "round75-instruments-append-accepted")

# Arm 7 `round74-v2`: the three round-74 v2 counters composed into one arm.
# (module key, script name, argument template with the usual {repo}/{tip}/{round}
# substitution); each absent module fails the arm closed, never a vacuous green.
ROUND74_V2_MODULES = (
    ("canon", "round74-selfdesc-canon.py", ("--repo", "{repo}")),
    ("claim-v2", "round74-receipt-claim-binding.py",
     ("--repo", "{repo}", "--round", "{round}", "--tip", "{tip}")),
    ("drift-v2", "round74-province-host-drift.py", ("--repo", "{repo}")),
)

# Arm 8 `round75-instruments`: the three round-75 counters composed into one arm.
ROUND75_MODULES = (
    ("pins", "round75-interpretation-pins.py", ("--repo", "{repo}")),
    ("survivors2", "round75-survivor-probe.py", ("--repo", "{repo}")),
    ("append-accepted", "round75-append-accepted.py", ("--repo", "{repo}")),
)


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

    For arms 4, 5 and arm 7's three counters the first concrete defect record is
    appended -- DIRTY/MISSING/UNTRACKED/UNREADABLE for the landing check,
    ROUND_SCOPE_V2_FINDING for the six-case round-scope counter, and the round-74 v2
    finding families (SELFDESC_CANON_V2_FINDING, RECEIPT_CLAIM_V2_FINDING,
    PROVINCE_HOST_DRIFT_V2_FINDING) for the round74-v2 counters -- so a failed arm
    names the path, case or counter that broke it.
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
    defects = [ln for ln in lines
               if DEFECT_RE.match(ln) or SCOPE_FINDING_RE.match(ln)
               or V2_FINDING_RE.match(ln) or R75_FINDING_RE.match(ln)]
    if name in _DEFECT_ARMS and defects:
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
    """Run the seven arms and derive the pinned verdict; the only scoring entry point."""
    repo_path = os.path.realpath(repo)
    tools_path = os.path.realpath(tools_dir) if tools_dir else os.path.join(repo_path, "tools")
    arms: list[dict] = []
    for name, template in ARM_SPECS:
        script = os.path.join(tools_path, template[0])
        argv = [sys.executable, script] + [
            token.replace("{repo}", repo_path).replace("{tip}", tip)
                 .replace("{round}", str(round_no))
            for token in template[1:]
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

    # Arm 7 round74-v2: compose the three round-74 v2 counters. Each module is
    # resolved from the tools dir exactly like the ARM_SPECS instruments; an absent
    # module fails the arm closed naming the script, and any non-zero exit fails the
    # arm with the failing counter's verdict and first *_V2_FINDING in the detail.
    v2_details: list[str] = []
    v2_codes: list[int] = []
    for mod_name, script_name, template in ROUND74_V2_MODULES:
        script = os.path.join(tools_path, script_name)
        if not os.path.isfile(script):
            v2_details.append(f"missing {script_name}")
            v2_codes.append(1)
            continue
        argv_v2 = [sys.executable, script] + [
            token.replace("{repo}", repo_path).replace("{tip}", tip)
                 .replace("{round}", str(round_no))
            for token in template
        ]
        code_v2, text_v2, spawn_error_v2 = _run(argv_v2, repo_path, depth)
        if code_v2 != 0:
            v2_codes.append(code_v2)
        v2_details.append(_detail(f"round74-v2-{mod_name}", text_v2, spawn_error_v2))
    arms.append({
        "name": "round74-v2",
        "argv": [os.path.join(tools_path, script_name)
                 for _, script_name, _ in ROUND74_V2_MODULES],
        "exit": 0 if not v2_codes else max(v2_codes),
        "ok": not v2_codes,
        "detail": " | ".join(v2_details),
    })

    # Arm 8 round75-instruments: the three round-75 counters composed the same way.
    r75_details: list[str] = []
    r75_codes: list[int] = []
    for mod_name, script_name, template in ROUND75_MODULES:
        script = os.path.join(tools_path, script_name)
        if not os.path.isfile(script):
            r75_details.append(f"missing {script_name}")
            r75_codes.append(1)
            continue
        argv_r75 = [sys.executable, script] + [
            token.replace("{repo}", repo_path).replace("{tip}", tip)
                 .replace("{round}", str(round_no))
            for token in template
        ]
        code_r75, text_r75, spawn_error_r75 = _run(argv_r75, repo_path, depth)
        if code_r75 != 0:
            r75_codes.append(code_r75)
        r75_details.append(_detail(f"round75-instruments-{mod_name}", text_r75, spawn_error_r75))
    arms.append({
        "name": "round75-instruments",
        "argv": [os.path.join(tools_path, script_name)
                 for _, script_name, _ in ROUND75_MODULES],
        "exit": 0 if not r75_codes else max(r75_codes),
        "ok": not r75_codes,
        "detail": " | ".join(r75_details),
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
# a throwaway git repository under --work, its tools dir holds four stubs plus a
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

_STUB_ROUND_SCOPE = _STUB_COMMON + '''
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default=".")
ap.add_argument("--round", type=int, default=0)
ap.add_argument("--tip", default="HEAD")
a = ap.parse_args()
try:
    with open(os.path.join(HERE, "scope-expect.txt"), "r", encoding="utf-8") as fh:
        want_round, want_tip = fh.read().split()
except (OSError, ValueError):
    want_round, want_tip = "0", "HEAD"
if str(a.round) != want_round or a.tip != want_tip:
    print("ROUND_SCOPE_V2_FINDING argv round={} tip={}".format(a.round, a.tip))
    print("ROUND_SCOPE_V2 round={} cases=6 findings=1".format(a.round))
    raise SystemExit(1)
if red("round-scope"):
    print("ROUND_SCOPE_V2_FINDING worktree /fixture/linked status=?? dirty.txt")
    print("ROUND_SCOPE_V2 round={} cases=6 findings=1".format(a.round))
    raise SystemExit(1)
print("ROUND_SCOPE_V2 round={} cases=6 findings=0".format(a.round))
raise SystemExit(0)
'''

_STUB_CANON = _STUB_COMMON + '''
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default=".")
a = ap.parse_args()
if red("round74-canon"):
    print("SELFDESC_CANON_V2_FINDING invisible 73 stub-capability")
    print("SELFDESC_CANON_V2 canon_round=70 canon_rows=2 demonstrated=1 total=3 "
          "invisible=1")
    raise SystemExit(1)
print("SELFDESC_CANON_V2 canon_round=70 canon_rows=2 demonstrated=0 total=2 invisible=0")
raise SystemExit(0)
'''

_STUB_CLAIM_V2 = _STUB_COMMON + '''
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default=".")
ap.add_argument("--round", type=int, default=0)
ap.add_argument("--tip", default="HEAD")
a = ap.parse_args()
if red("round74-claim-v2"):
    print("RECEIPT_CLAIM_V2_FINDING wrapped-claim corpus/lessons/round-70.md :: 3")
    print("RECEIPT_CLAIM_V2 round={} cited=1 bound=0 unbound=1 shifted=0 stale=0 "
          "claims=1 unbound_claims=1 bound_revisions=0".format(a.round))
    raise SystemExit(1)
print("RECEIPT_CLAIM_V2 round={} cited=0 bound=0 unbound=0 shifted=0 stale=0 "
      "claims=0 unbound_claims=0 bound_revisions=0".format(a.round))
raise SystemExit(0)
'''

_STUB_DRIFT_V2 = _STUB_COMMON + '''
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default=".")
a = ap.parse_args()
if red("round74-drift-v2"):
    print("PROVINCE_HOST_DRIFT_V2_FINDING edited-block stub block")
    print("PROVINCE_HOST_DRIFT_V2 blocks=1 recorded=Linux/x86_64/arch "
          "live=Linux/x86_64/arch stale=0 edited=1")
    raise SystemExit(1)
print("PROVINCE_HOST_DRIFT_V2 blocks=1 recorded=Linux/x86_64/arch "
      "live=Linux/x86_64/arch stale=0 edited=0")
raise SystemExit(0)
'''

_STUB_PINS = _STUB_COMMON + '''
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default=".")
a = ap.parse_args()
if red("round75-pins"):
    print("INTERPRETATION_PINS_FINDING P1 declared=3 mutant=5")
    print("INTERPRETATION_PINS pins=2 declared=1 killed=1 escaped=1")
    raise SystemExit(1)
print("INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0")
raise SystemExit(0)
'''

_STUB_SURVIVORS2 = _STUB_COMMON + '''
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default=".")
a = ap.parse_args()
if red("round75-survivors2"):
    print("SURVIVORS2_FINDING c2_conflict_off mutant_exit=0 arm=none")
    print("SURVIVORS2 mutants=5 killed=4 escaped=1")
    raise SystemExit(1)
print("SURVIVORS2 mutants=5 killed=5 escaped=0")
raise SystemExit(0)
'''

_STUB_APPEND_ACCEPTED = _STUB_COMMON + '''
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default=".")
a = ap.parse_args()
if red("round75-append-accepted"):
    print("APPEND_ACCEPTED_FINDING hash-mismatch stub row")
    print("APPEND_ACCEPTED events=53 accepted=52 unaccepted=1 bad_rows=1 bad_declarations=0")
    raise SystemExit(1)
print("APPEND_ACCEPTED events=53 accepted=53 unaccepted=0 bad_rows=0 bad_declarations=0")
raise SystemExit(0)
'''

_FIXTURE_FILES = {
    "SCORECARD.md": b"# Scorecard (pre-report-gate selftest fixture)\n\n## Axes\n\n"
                    b"| axis | score |\n|---|---|\n| calibration | 7 |\n",
    "LOG.md": b"# Log (fixture)\n\n- fixture round\n",
    "PROVINCE.md": b"# Province (fixture)\n",
    "SKILL.md": b"# Skill (fixture)\n\none\ntwo\n",
    "corpus/SOURCES.md": b"# Sources (fixture)\n",
    "plans/round-70-claims.md": b"# kama round 70 \xe2\x80\x94 frozen claims\n\nfixture body\n",
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
    real_scope = Path(__file__).resolve().parent / "round73-round-scope-cases.py"
    real_scope_r72 = Path(__file__).resolve().parent / "round72-round-scope.py"
    if not real_scope.is_file():
        print("PRE_REPORT_SELFTEST could-not-evaluate: round-73 scope counter missing at "
              f"{real_scope}")
        return 2

    tools = work / "tools"
    tools.mkdir()
    shutil.copy2(real_wlc, tools / "round67-worktree-landing-check.py")
    (tools / "round42-selfdesc-reconcile.py").write_text(_STUB_SELFDESC, encoding="utf-8")
    (tools / "round69-newest-closure-counter.py").write_text(_STUB_NEWEST, encoding="utf-8")
    (tools / "round68-receipt-pointer-audit.py").write_text(_STUB_RECEIPT, encoding="utf-8")
    (tools / "round73-round-scope-cases.py").write_text(_STUB_ROUND_SCOPE, encoding="utf-8")
    (tools / "round74-selfdesc-canon.py").write_text(_STUB_CANON, encoding="utf-8")
    (tools / "round74-receipt-claim-binding.py").write_text(_STUB_CLAIM_V2, encoding="utf-8")
    (tools / "round74-province-host-drift.py").write_text(_STUB_DRIFT_V2, encoding="utf-8")
    (tools / "round75-interpretation-pins.py").write_text(_STUB_PINS, encoding="utf-8")
    (tools / "round75-survivor-probe.py").write_text(_STUB_SURVIVORS2, encoding="utf-8")
    (tools / "round75-append-accepted.py").write_text(_STUB_APPEND_ACCEPTED, encoding="utf-8")
    (tools / "scope-expect.txt").write_text("70 master\n", encoding="utf-8")
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
              detail_has: str | None = None, want_line: str | None = None,
              render_has: str | None = None) -> None:
        nonlocal passed
        lines = render(result)
        for line in lines:
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
        if render_has is not None and not any(render_has in line for line in lines):
            problems.append(f"render lacks {render_has!r}")
        if problems:
            failed_arms.append(label)
            print(f"FAIL {label} :: " + "; ".join(problems))
        else:
            passed += 1
            print(f"PASS {label}")

    # (a) green fixture: the target shape, exit 0.
    check("green", evaluate(repo, round_no, "master", str(tools)), 0, 0, 0, "round-clean", True,
          detail_has="files=0",
          want_line="PRE_REPORT round=70 arms=8 failed=0 uncommitted=0")

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

    # (g) red round-scope stub: the sixth arm is a named failure on its own evidence.
    red_file.write_text("round-scope\n", encoding="utf-8")
    check("round-scope-red", evaluate(repo, round_no, "master", str(tools)), 1, 1, 0,
          "round-scope", False,
          detail_has="ROUND_SCOPE_V2 round=70 cases=6 findings=1 | ROUND_SCOPE_V2_FINDING worktree",
          render_has="round-scope exit=1 FAIL")
    red_file.write_text("", encoding="utf-8")

    # (h) green round-scope stub: arm passes, the verdict carries seven arms.
    check("round-scope-green", evaluate(repo, round_no, "master", str(tools)), 0, 0, 0,
          "round-scope", True, detail_has="findings=0",
          render_has="round-scope exit=0 ok",
          want_line="PRE_REPORT round=70 arms=8 failed=0 uncommitted=0")

    # (i)-(k) the real round-73 counter through the same arm-5 wiring: the clean fixture,
    # then the A5 linked-worktree survivor and the A6 ignored-older-round survivor.
    shutil.copy2(real_scope, tools / real_scope.name)
    if real_scope_r72.is_file():
        shutil.copy2(real_scope_r72, tools / real_scope_r72.name)

    check("round-scope-v2-clean", evaluate(repo, round_no, "master", str(tools)), 0, 0, 0,
          "round-scope", True,
          detail_has="ROUND_SCOPE_V2 round=70 cases=6 findings=0",
          want_line="PRE_REPORT round=70 arms=8 failed=0 uncommitted=0")

    linked = work / "linked-worktree"
    added = _git(repo, "worktree", "add", "--detach", str(linked), "master", check=False)
    if added.returncode != 0:
        print("PRE_REPORT_SELFTEST could-not-evaluate: fixture git worktree add failed: "
              f"{added.stderr.strip()}")
        return 2
    (linked / "dirty.txt").write_text("uncommitted linked-worktree work\n", encoding="utf-8")
    check("round-scope-v2-a5-red", evaluate(repo, round_no, "master", str(tools)), 1, 1, 0,
          "round-scope", False,
          detail_has="ROUND_SCOPE_V2 round=70 cases=6 findings=1 | ROUND_SCOPE_V2_FINDING worktree")
    _git(repo, "worktree", "remove", "--force", str(linked), check=False)

    exclude_rel = _git(repo, "rev-parse", "--git-path", "info/exclude").stdout.strip()
    exclude = Path(exclude_rel)
    if not exclude.is_absolute():
        exclude = repo / exclude
    exclude.parent.mkdir(parents=True, exist_ok=True)
    prior_exclude = exclude.read_bytes() if exclude.exists() else b""
    exclude.write_bytes(prior_exclude + b".ufo/waves/round-71/\n")
    wave71 = repo / ".ufo/waves/round-71"
    wave71.mkdir(parents=True)
    (wave71 / "scratch.log").write_text("ignored round-71 evidence\n", encoding="utf-8")
    check("round-scope-v2-a6-red", evaluate(repo, round_no, "master", str(tools)), 1, 1, 0,
          "round-scope", False, detail_has="ROUND_SCOPE_V2_FINDING ignored-older-label")
    shutil.rmtree(wave71)
    exclude.write_bytes(prior_exclude)

    # (l) the arm-5 verdict selector picks the V2 line, not a later diagnostic line.
    probe = ("ROUND_SCOPE_V2_FINDING worktree /fixture/linked status=?? dirty.txt\n"
             "ROUND_SCOPE_V2 round=70 cases=6 findings=1\n"
             "later diagnostic line\n")
    want_detail = ("ROUND_SCOPE_V2 round=70 cases=6 findings=1 | "
                   "ROUND_SCOPE_V2_FINDING worktree /fixture/linked status=?? dirty.txt")
    got_detail = _detail("round-scope", probe)
    if got_detail == want_detail:
        passed += 1
        print("PASS verdict-selector")
    else:
        failed_arms.append("verdict-selector")
        print(f"FAIL verdict-selector :: detail={got_detail!r} want {want_detail!r}")

    # (m) red canon stub inside arm 7: one failing counter fails the whole arm and
    # the detail names the failing counter's verdict and finding.
    red_file.write_text("round74-canon\n", encoding="utf-8")
    check("round74-v2-red", evaluate(repo, round_no, "master", str(tools)), 1, 1, 0,
          "round74-v2", False,
          detail_has="SELFDESC_CANON_V2_FINDING invisible 73 stub-capability",
          render_has="round74-v2 exit=1 FAIL")
    red_file.write_text("", encoding="utf-8")

    # (n) green arm-7 stubs: the arm passes and the verdict carries seven arms.
    check("round74-v2-green", evaluate(repo, round_no, "master", str(tools)), 0, 0, 0,
          "round74-v2", True,
          detail_has="SELFDESC_CANON_V2 canon_round=70 canon_rows=2 demonstrated=0 "
                     "total=2 invisible=0",
          render_has="round74-v2 exit=0 ok",
          want_line="PRE_REPORT round=70 arms=8 failed=0 uncommitted=0")

    # (o) a deleted counter stub fails arm 7 closed, naming the absent module.
    drift_stub = tools / "round74-province-host-drift.py"
    drift_stub.unlink()
    check("round74-v2-missing", evaluate(repo, round_no, "master", str(tools)), 1, 1, 0,
          "round74-v2", False,
          detail_has="missing round74-province-host-drift.py",
          render_has="round74-v2 exit=1 FAIL")
    drift_stub.write_text(_STUB_DRIFT_V2, encoding="utf-8")

    # (p) red pins stub inside arm 8: one failing counter fails the whole arm and the
    # detail names the counter's verdict and its first *_FINDING line.
    red_file.write_text("round75-pins\n", encoding="utf-8")
    check("round75-instruments-red", evaluate(repo, round_no, "master", str(tools)), 1, 1, 0,
          "round75-instruments", False,
          detail_has="INTERPRETATION_PINS_FINDING P1 declared=3 mutant=5",
          render_has="round75-instruments exit=1 FAIL")
    red_file.write_text("", encoding="utf-8")

    # (q) green arm-8 stubs: the arm passes and the verdict carries eight arms.
    check("round75-instruments-green", evaluate(repo, round_no, "master", str(tools)), 0, 0, 0,
          "round75-instruments", True,
          detail_has="SURVIVORS2 mutants=5 killed=5 escaped=0",
          render_has="round75-instruments exit=0 ok",
          want_line="PRE_REPORT round=70 arms=8 failed=0 uncommitted=0")

    # (r) a deleted round-75 counter fails arm 8 closed, naming the absent module.
    aa_stub = tools / "round75-append-accepted.py"
    aa_stub.unlink()
    check("round75-instruments-missing", evaluate(repo, round_no, "master", str(tools)), 1, 1, 0,
          "round75-instruments", False,
          detail_has="missing round75-append-accepted.py",
          render_has="round75-instruments exit=1 FAIL")
    aa_stub.write_text(_STUB_APPEND_ACCEPTED, encoding="utf-8")

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
        description="One pre-report gate: five reconciled instruments, round-worktree "
                    "cleanliness, the round-74 v2 counter trio and the round-75 instrument trio "
                    "(arms=8 from round 75)."
    )
    ap.add_argument("--repo", default=".", help="repository to grade (default: current directory)")
    ap.add_argument("--round", dest="round_no", type=int, default=None,
                    help="round number whose .ufo/waves/round-<N> dir is graded (required)")
    ap.add_argument("--tip", default="master", help="revision the instruments evaluate (default: master)")
    ap.add_argument("--selftest", action="store_true", help="run the fixture selftest")
    ap.add_argument("--json", action="store_true", help="emit one JSON document instead of the human lines")
    ap.add_argument("--tools-dir", default=None,
                    help="directory holding the instrument scripts (default: <repo>/tools)")
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
