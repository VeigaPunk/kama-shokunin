#!/usr/bin/env python3
"""Build a synthetic EX02-style candidate: master gate + wired round86-instruments arm
plus three green instrument stubs, mirroring the frozen C2 claim."""
import os
import re
import shutil
import subprocess
import sys

CLONE = "/fast/scratch/hyaku/kama-r87/MT02GateArmBattery/wt"
ROOT = "/fast/scratch/hyaku/kama-r87/MT02GateArmBattery"
SYNTH = os.path.join(ROOT, "synth")

src = open(os.path.join(CLONE, "tools", "pre-report-gate.py"), encoding="utf-8").read()

# 1. ARM_ORDER: append the arm after round83-instruments (frozen claim).
src = src.replace('"round81-instruments", "round82-instruments", "round83-instruments"]',
                  '"round81-instruments", "round82-instruments", "round83-instruments",\n'
                  '              "round86-instruments"]')

# 2. Module tuple + arm function, mirroring the round83 pattern (frozen claim:
#    three --selftests, each summary must be `<prefix> pass=<n> fail=0`).
arm_fn = '''
# Arm 14 `round86-instruments` (round 87): the round-86 counter trio's own selftests,
# each required to end with its OWN summary prefix.
ROUND86_MODULES = (
    ("round86-rendered-cells.py", "RENDERED_CELLS_SELFTEST"),
    ("round86-mutant-owners.py", "MUTANT_OWNERS_SELFTEST"),
    ("round86-pin-origin.py", "PIN_ORIGIN_SELFTEST"),
)


def _round86_instruments(tools_path: str, repo_path: str, depth: int = 0) -> dict:
    details: list[str] = []
    commands: list[list[str]] = []
    failed = False
    for script_name, prefix in ROUND86_MODULES:
        script = os.path.join(tools_path, script_name)
        argv = [sys.executable, script, "--selftest"]
        commands.append(argv)
        if not os.path.isfile(script):
            failed = True
            details.append(f"missing {script_name}")
            continue
        code, text, error = _run(argv, repo_path, depth)
        summary = _last_line(text)
        ok = code == 0 and error is None and re.fullmatch(
            rf"{prefix} pass=[0-9]+ fail=0", summary) is not None
        failed = failed or not ok
        reason = error or summary or "(no output)"
        if code == 0 and not ok and error is None:
            reason = f"missing valid final selftest summary: {reason}"
        details.append(f"{script_name} exit={code} {'ok' if ok else 'FAIL'} {_one_line(reason)}")
    return {
        "name": "round86-instruments",
        "argv": commands,
        "exit": 1 if failed else 0,
        "ok": not failed,
        "detail": " | ".join(details),
    }


def evaluate('''
assert "\n\ndef evaluate(" in src
src = src.replace("\n\ndef evaluate(", arm_fn, 1)

# 3. evaluate dispatch: append after the round83 arm.
marker = "    arms.append(_round83_instruments(tools_path, repo_path, depth))"
assert marker in src
src = src.replace(marker, marker + "\n    arms.append(_round86_instruments(tools_path, repo_path, depth))", 1)

# Tools: full copy + three green instruments.
if os.path.exists(SYNTH):
    shutil.rmtree(SYNTH)
os.makedirs(SYNTH)
shutil.copytree(os.path.join(CLONE, "tools"), os.path.join(SYNTH, "tools"), symlinks=True)
GREEN = {
    "round86-rendered-cells.py": "RENDERED_CELLS_SELFTEST pass=2 fail=0",
    "round86-mutant-owners.py": "MUTANT_OWNERS_SELFTEST pass=2 fail=0",
    "round86-pin-origin.py": "PIN_ORIGIN_SELFTEST pass=2 fail=0",
}
for name, line in GREEN.items():
    with open(os.path.join(SYNTH, "tools", name), "w", encoding="utf-8") as fh:
        fh.write("#!/usr/bin/env python3\n" + f'print("{line}")\n')

with open(os.path.join(SYNTH, "pre-report-gate.py"), "w", encoding="utf-8") as fh:
    fh.write(src)

print("synth built:", SYNTH)
