#!/usr/bin/env python3
"""round87-gate-arm-faults.py - round-87 C2 (operability): fault-seeding harness for the
gate arm `round86-instruments` in tools/pre-report-gate.py.

Predicate (frozen: plans/round-87-claims.md section C2, predicate 2): this harness prints
`ARM14_FAULTS faults=3 killed=3 escaped=0` and exits 0 on the lane tree.

Method:
  1. Load tools/pre-report-gate.py from --repo by path (importlib); the gate is not copied.
  2. Copy the repo's tools/ into a scratch tools tree under --work.
  3. Control: run gate.evaluate(repo, 87, tip='master', tools_dir=<unmodified copy>) and
     look up the arm named `round86-instruments`. The control must show that arm ok True;
     otherwise the line `CONTROL_RED` is printed and the exit is 1.
  4. Faults: for each round-86 instrument (round86-rendered-cells.py, round86-mutant-owners.py,
     round86-pin-origin.py) replace THAT instrument in a fresh scratch copy of tools/ with a
     stub whose `--selftest` prints `FAULT_STUB pass=0 fail=1` and exits 0 (one fault per run).
     Run gate.evaluate(...) on that copy. A fault is killed iff the arm exists and its ok is
     False. A missing arm counts as escaped.
  5. Print `ARM14_FAULTS faults=3 killed=<k> escaped=<e>` as the final line. Exit 0 iff
     killed == 3 and the control is green.

Scratch: --work is a parent directory (default: a fresh directory under $TMPDIR; the harness
never uses /tmp). A private directory is created inside --work for the scratch tools trees and
removed at the end, together with the default --work directory when the harness created it.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import sys
import tempfile
from pathlib import Path

ARM_NAME = "round86-instruments"
ROUND = 87
TIP = "master"
FAULT_TARGETS = (
    "round86-rendered-cells.py",
    "round86-mutant-owners.py",
    "round86-pin-origin.py",
)
STUB_SOURCE = (
    "#!/usr/bin/env python3\n"
    "# FAULT_STUB: seeded fault for round87-gate-arm-faults.py; always fails its own summary.\n"
    "print(\"FAULT_STUB pass=0 fail=1\")\n"
    "raise SystemExit(0)\n"
)


def _load_gate(repo: Path):
    gate_path = repo / "tools" / "pre-report-gate.py"
    if not gate_path.is_file():
        raise SystemExit(f"gate not found: {gate_path}")
    spec = importlib.util.spec_from_file_location("pre_report_gate_r87", gate_path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load gate: {gate_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "evaluate"):
        raise SystemExit(f"gate has no evaluate(): {gate_path}")
    return module


def _arm(result: dict, name: str):
    for arm in result.get("arms", []):
        if arm.get("name") == name:
            return arm
    return None


def _evaluate_with_tools(gate, repo: Path, tools_dir: Path):
    """Run the gate against a tools dir; any exception is reported, not swallowed silently."""
    try:
        return gate.evaluate(str(repo), ROUND, tip=TIP, tools_dir=str(tools_dir)), None
    except Exception as exc:  # noqa: BLE001 - a crash is recorded as an escape, with its reason
        return None, f"{type(exc).__name__}: {exc}"


def _copy_tools(repo_tools: Path, dest: Path) -> Path:
    shutil.copytree(repo_tools, dest, ignore=shutil.ignore_patterns("__pycache__"))
    return dest


def _default_work() -> Path:
    base = os.environ.get("TMPDIR")
    if not base:
        raise SystemExit("TMPDIR is unset; pass --work <dir> (the harness never uses /tmp)")
    base_path = Path(base)
    base_path.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="round87-arm14-faults-", dir=str(base_path)))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--repo", default=".", help="lane tree containing tools/ (default: .)")
    ap.add_argument("--work", default=None,
                    help="scratch parent directory (default: a fresh dir under $TMPDIR)")
    args = ap.parse_args(argv)

    repo = Path(args.repo).resolve()
    repo_tools = repo / "tools"
    if not repo_tools.is_dir():
        raise SystemExit(f"tools dir not found: {repo_tools}")

    gate = _load_gate(repo)

    created_work = args.work is None
    work = _default_work() if created_work else Path(args.work).resolve()
    work.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="arm-", dir=str(work)))

    killed = 0
    escaped = 0
    try:
        # Control: the unmodified tools copy must show the arm green.
        control_tools = _copy_tools(repo_tools, scratch / "control" / "tools")
        result, crash = _evaluate_with_tools(gate, repo, control_tools)
        arm = _arm(result, ARM_NAME) if result is not None else None
        control_ok = arm is not None and arm.get("ok") is True
        if crash:
            print(f"CONTROL crashed: {crash}")
        elif arm is None:
            print(f"CONTROL arm={ARM_NAME} missing")
        else:
            print(f"CONTROL arm={ARM_NAME} ok={arm.get('ok')} exit={arm.get('exit')} "
                  f"detail={arm.get('detail')}")

        # Faults: one stubbed instrument per run.
        for index, target in enumerate(FAULT_TARGETS, start=1):
            tools = _copy_tools(repo_tools, scratch / f"fault{index}" / "tools")
            (tools / target).write_text(STUB_SOURCE, encoding="utf-8")
            result, crash = _evaluate_with_tools(gate, repo, tools)
            arm = _arm(result, ARM_NAME) if result is not None else None
            if crash:
                status = f"escaped (gate crashed: {crash})"
                escaped += 1
            elif arm is None:
                status = "escaped (arm missing)"
                escaped += 1
            elif arm.get("ok") is False:
                status = f"killed (arm ok=False exit={arm.get('exit')}) detail={arm.get('detail')}"
                killed += 1
            else:
                status = f"escaped (arm ok={arm.get('ok')}) detail={arm.get('detail')}"
                escaped += 1
            print(f"FAULT {index} target={target} {status}")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
        if created_work:
            shutil.rmtree(work, ignore_errors=True)

    if not control_ok:
        print("CONTROL_RED")
    print(f"ARM14_FAULTS faults={len(FAULT_TARGETS)} killed={killed} escaped={escaped}")
    return 0 if (killed == len(FAULT_TARGETS) and control_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
