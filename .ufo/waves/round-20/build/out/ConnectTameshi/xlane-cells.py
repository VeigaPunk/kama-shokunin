#!/usr/bin/env python3
"""xlane-cells.py - ConnectTameshi (kama round 20): error-vs-verdict cells.

Read-only on both repos. Materializes instrument bytes from git (GIT_* scrubbed)
into a scratch dir under /tmp/kama-r20-ConnectTameshi, injects one error or one
real verdict per cell, and records how each instrument classifies it next to
the class tameshi's written method assigns (tameshi SKILL.md:189-212, :1664-1671
@ 6acaf4dd): kill/reject needs an observed verdict; a crash, signal, timeout,
not-runnable suite, undeclared code or a run that never enumerated its count is
could-not-evaluate.

Arms: kama frozen 37bd4c5 tests/llamacpp-live/install-tree-grid.py (grid-*),
kama frozen 37bd4c5 .ufo/waves/round-18/c2/survivors.py selftest_arm (arm-*),
tameshi 6acaf4dd tools/mutate-and-run.sh (runner-*).

Usage: xlane-cells.py --out RECEIPT.json [--only CELL_PREFIX]
  grid-hang waits for the grid's hard-coded 300 s gate timeout; it runs only
  when selected with --only grid-hang.
Exit: 0 every selected cell ran (rows are observations, not a gate);
      2 setup failure (git show, scratch, existing --out).
"""
import argparse
import hashlib
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

KAMA = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
TAMESHI = Path("/home/vgpnk/Projects/shokunin/tameshi-shokunin")
KAMA_REV = "37bd4c5bd456a2f8a54d3312c28495c321715856"
TAMESHI_REV = "6acaf4dd2f2a8c9de4312e89a05c0f5155c9f055"
SCRATCH_PARENT = Path("/tmp/kama-r20-ConnectTameshi")
MEMBER = "libllama.so.0.7.0"

FAKE_GATE = r'''
import os, signal, sys, time
receipt = sys.argv[1]
if os.path.basename(receipt) == "baseline.json":
    print(f"VALID {receipt}")
    sys.exit(0)
cell = os.environ["XLANE_CELL"]
if cell == "grid-invalid-verdict":
    print(f"INVALID {receipt}: 1 problem(s)")
    print("  - install_tree member digest mismatch")
    sys.exit(1)
if cell == "grid-uncaught-exception":
    raise RuntimeError("injected crash before any verdict")
if cell == "grid-silent-exit-1":
    sys.exit(1)
if cell == "grid-not-evaluated-3":
    print(f"NOT-EVALUATED {receipt}")
    sys.exit(3)
if cell == "grid-sigkill":
    os.kill(os.getpid(), signal.SIGKILL)
if cell == "grid-sigterm":
    os.kill(os.getpid(), signal.SIGTERM)
if cell == "grid-undeclared-exit-4":
    sys.exit(4)
if cell == "grid-valid-verdict":
    print(f"VALID {receipt}")
    sys.exit(0)
if cell == "grid-hang":
    time.sleep(3600)
sys.exit(97)
'''

# cell -> (injection, class tameshi's method assigns)
GRID_CELLS = {
    "grid-invalid-verdict": ("stdout INVALID + exit 1", "verdict:reject"),
    "grid-uncaught-exception": ("RuntimeError traceback, exit 1, empty stdout", "could-not-evaluate"),
    "grid-silent-exit-1": ("exit 1, empty stdout", "could-not-evaluate"),
    "grid-not-evaluated-3": ("stdout NOT-EVALUATED + exit 3", "could-not-evaluate"),
    "grid-sigkill": ("SIGKILL (returncode -9)", "could-not-evaluate"),
    "grid-sigterm": ("SIGTERM (returncode -15)", "could-not-evaluate"),
    "grid-undeclared-exit-4": ("undeclared exit 4", "could-not-evaluate"),
    "grid-valid-verdict": ("stdout VALID + exit 0", "verdict:accept"),
    "grid-hang": ("sleep past the grid's 300 s gate timeout", "could-not-evaluate"),
}
GRID_STATUS_CLASS = {"rejected": "verdict:reject", "accepted": "verdict:accept",
                     "error": "could-not-evaluate", "absent": "could-not-evaluate"}
# install-tree-grid.py:17-18 exit map
GRID_EXIT_MEANING = {0: "verdict: every mutant rejected",
                     1: "verdict: a mutant survived",
                     2: "baseline invalid / bad input"}

RUNNER_TARGET = "#!/usr/bin/env bash\necho pristine-marker\n"
RUNNER_SPEC = ("@defect D1 | swap the marker\n"
               "@old echo pristine-marker\n"
               "@new echo mutant-marker\n")
_GREEN = 'echo "SELFTEST: PASS (1/1 cases)"'
_HIT = 'grep -q mutant-marker "$MUTANT"'
RUNNER_CELLS = {
    "runner-true-kill": (
        f'if {_HIT}; then echo "FAIL case-1 marker"; '
        f'echo "SELFTEST: FAIL (1/1 cases)"; exit 1; fi; {_GREEN}',
        "FAIL label + summary, exit 1", "verdict:kill", 30),
    "runner-uncaught-exception": (
        f"if {_HIT}; then exec python3 -c "
        "'raise RuntimeError(\"injected crash before any verdict\")'; fi; "
        f"{_GREEN}",
        "python traceback, exit 1, no summary", "could-not-evaluate", 30),
    "runner-sigterm": (
        f"if {_HIT}; then kill -TERM $$; fi; {_GREEN}",
        "suite shell SIGTERM (exit 143)", "could-not-evaluate", 30),
    "runner-sigkill": (
        f"if {_HIT}; then kill -KILL $$; fi; {_GREEN}",
        "suite shell SIGKILL (exit 137)", "could-not-evaluate", 30),
    "runner-hang": (
        f"if {_HIT}; then sleep 30; fi; {_GREEN}",
        "sleep past --timeout 2 (exit 124)", "could-not-evaluate", 2),
    "runner-not-runnable": (
        f"if {_HIT}; then exec /nonexistent/xlane-suite; fi; {_GREEN}",
        "exec of a missing suite (exit 127)", "could-not-evaluate", 30),
}
RUNNER_CLASS = {"KILLED": "verdict:kill", "SURVIVED": "verdict:survive",
                "INCONCLUSIVE": "could-not-evaluate"}

ARM_TARGET = "target-conjunct attribution"
ARM_CELLS = {
    "arm-complete-kill": (1, f"FAIL {ARM_TARGET}\n4/5 selftest cases passed\n",
                          "FAIL target line + full count 4/5, exit 1", "verdict:kill"),
    "arm-early-abort": (1, f"FAIL {ARM_TARGET}\n",
                        "FAIL target line, then abort: no count, exit 1",
                        "could-not-evaluate"),
    "arm-signal": (-9, f"FAIL {ARM_TARGET}\n", "FAIL target line, SIGKILL",
                   "could-not-evaluate"),
}
ARM_CLASS = {"killed": "verdict:kill", "survived": "verdict:survive",
             "inconclusive": "could-not-evaluate"}


def child_env(scratch, extra=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
                "PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": str(scratch)})
    env.update(extra or {})
    return env


def git_show(repo, rev, path, dest, scratch):
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"],
                          capture_output=True, env=child_env(scratch))
    if proc.returncode != 0:
        raise RuntimeError(f"git show {rev}:{path} exit {proc.returncode}")
    dest.write_bytes(proc.stdout)
    return {"repo": str(repo), "rev": rev, "path": path,
            "sha256": hashlib.sha256(proc.stdout).hexdigest()}


def grid_cell(cell, grid, gate, receipt, scratch):
    cmd = [sys.executable, str(grid), "--gate", str(gate), "--receipt",
           str(receipt), "--model-sha", "m", "--server-sha", "s",
           "--impl-sha", "i", "--probe-sha", "p", "--tool-sha", "t",
           "--members", MEMBER, "--json"]
    proc = subprocess.run(cmd, capture_output=True, timeout=900,
                          env=child_env(scratch, {"XLANE_CELL": cell}))
    row, traceback = None, b"Traceback (most recent call last)" in proc.stderr
    try:
        doc = json.loads(proc.stdout.decode("utf-8"))
        row = doc["rows"][0]
    except (ValueError, KeyError, IndexError):
        doc = None
    status = row.get("status") if row else None
    if status is not None:
        observed = GRID_STATUS_CLASS.get(status, status)
    else:
        observed = "instrument-crash" if traceback else "no-row"
    return {"instrument_exit": proc.returncode,
            "instrument_exit_meaning": GRID_EXIT_MEANING.get(
                proc.returncode, "undeclared"),
            "row_status": status,
            "gate_exit": row.get("gate_exit") if row else None,
            "instrument_traceback": traceback,
            "stderr_last": proc.stderr.decode("utf-8", "replace")
                               .strip().splitlines()[-1:],
            "observed_class": observed}


def runner_cell(cell, runner, scratch, suite, timeout_s):
    work = scratch / cell
    work.mkdir()
    target, spec = work / "target.sh", work / "d.spec"
    target.write_text(RUNNER_TARGET)
    spec.write_text(RUNNER_SPEC)
    proc = subprocess.run(
        ["bash", str(runner), "--target", str(target), "--defects", str(spec),
         "--suite", suite, "--workdir", str(work / "run"), "--label", cell,
         "--timeout", str(timeout_s), "--tail", "2"],
        capture_output=True, timeout=300, env=child_env(scratch), cwd=work)
    out = proc.stdout.decode("utf-8", "replace")
    m = re.search(r"(?m)^DEFECT D1: (\w+) \(([^)]*)\)", out)
    head = re.search(r"(?m)^MUTATE: (\w+) \(.*\)$", out)
    tool = re.search(r"(?m)^MUTATE_TOOL: \S+ sha256=([0-9a-f]{64})", out)
    verdict = m.group(1) if m else None
    return {"instrument_exit": proc.returncode,
            "defect_line": m.group(0) if m else None,
            "headline": head.group(0) if head else None,
            "tool_sha256": tool.group(1) if tool else None,
            "observed_class": RUNNER_CLASS.get(verdict, f"none:{verdict}")}


def arm_cells(survivors_path):
    mod = runpy.run_path(str(survivors_path), run_name="xlane_survivors")
    arm = mod["selftest_arm"]

    def fake(code, stdout):
        return {"record": {"exit": code, "timed_out": False,
                           "spawn_error": None}, "stdout": stdout.encode()}
    base = fake(0, "5/5 selftest cases passed\n")
    rows = {}
    for cell, (code, stdout, injection, expected) in ARM_CELLS.items():
        status, why = arm(base, fake(code, stdout), ARM_TARGET)
        rows[cell] = {"injection": injection, "expected_by_tameshi": expected,
                      "instrument_exit": None, "arm_result": [status, why],
                      "observed_class": ARM_CLASS.get(status, status)}
    return rows


def run_cells(args, scratch):
    # survivors.py resolves LANE = SELF.parents[4] at import: keep its depth.
    surv = scratch / "lane" / ".ufo" / "waves" / "round-18" / "c2" / "survivors.py"
    surv.parent.mkdir(parents=True)
    pins = {
        "grid": git_show(KAMA, KAMA_REV,
                         "tests/llamacpp-live/install-tree-grid.py",
                         scratch / "install-tree-grid.py", scratch),
        "survivors": git_show(KAMA, KAMA_REV,
                              ".ufo/waves/round-18/c2/survivors.py",
                              surv, scratch),
        "runner": git_show(TAMESHI, TAMESHI_REV, "tools/mutate-and-run.sh",
                           scratch / "mutate-and-run.sh", scratch),
    }

    def selected(cell):
        if args.only:
            return cell.startswith(args.only)
        return cell != "grid-hang"

    rows = {}
    gate, receipt = scratch / "fake-gate.py", scratch / "receipt.json"
    gate.write_text(FAKE_GATE)
    receipt.write_text(json.dumps({"server": {"install_tree": {
        MEMBER: "0" * 64, "libggml-base.so.0.27.0": "1" * 64}}}))
    for cell, (injection, expected) in GRID_CELLS.items():
        if selected(cell):
            rows[cell] = {"injection": injection, "expected_by_tameshi": expected,
                          **grid_cell(cell, scratch / "install-tree-grid.py",
                                      gate, receipt, scratch)}
    for cell, (suite, injection, expected, tmo) in RUNNER_CELLS.items():
        if selected(cell):
            rows[cell] = {"injection": injection, "expected_by_tameshi": expected,
                          **runner_cell(cell, scratch / "mutate-and-run.sh",
                                        scratch, suite, tmo)}
    if any(selected(c) for c in ARM_CELLS):
        rows.update({c: r for c, r in arm_cells(surv).items() if selected(c)})
    for row in rows.values():
        row["agrees_with_tameshi_method"] = (
            row["observed_class"] == row["expected_by_tameshi"])
    return rows, pins


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default=None)
    args = ap.parse_args(argv)
    out = Path(args.out)
    if out.exists():
        print(f"xlane-cells: refusing to overwrite {out}", file=sys.stderr)
        return 2
    SCRATCH_PARENT.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="run-", dir=SCRATCH_PARENT))
    try:
        rows, pins = run_cells(args, scratch)
    except Exception as exc:  # own fault is could-not-evaluate, never a row
        print(f"xlane-cells: own fault: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 2
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    receipt_doc = {"schema": "kama-r20-xlane-cells/v1", "pins": pins,
                   "python": sys.version.split()[0],
                   "scratch_removed": not scratch.exists(), "cells": rows}
    with open(out, "x", encoding="utf-8") as fh:
        json.dump(receipt_doc, fh, indent=1)
        fh.write("\n")
    for cell, row in rows.items():
        print("\t".join([cell, str(row["instrument_exit"]),
                         row["observed_class"], row["expected_by_tameshi"],
                         "agree" if row["agrees_with_tameshi_method"]
                         else "DISAGREE"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
