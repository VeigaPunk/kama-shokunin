#!/usr/bin/env python3
"""Build three minimal isolated fixtures (prereg + battery only) and run the
frozen base checker, the live round-57 checker, and the execution probe."""
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import batteries  # noqa: E402

SEAT = "/fast/scratch/hyaku/kama-r57/R57Item30AxisFit"
FIX = os.path.join(SEAT, "fixtures", "variants")
EVID = os.path.join(SEAT, "evidence")
PREREG = os.path.join(SEAT, "instruments", "preregistration.json")


def sh(args, cwd=None, env=None):
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)


def build(name: str, source: str):
    d = os.path.join(FIX, name)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, ".ufo", "waves", "round-56"))
    os.makedirs(os.path.join(d, "tools"))
    shutil.copy(PREREG, os.path.join(d, ".ufo", "waves", "round-56", "preregistration.json"))
    with open(os.path.join(d, "tools", "round56-env-leg-battery.py"), "w") as f:
        f.write(source)
    for step in (["git", "init", "-q"], ["git", "add", "-A"],
                 ["git", "-c", "user.name=fixture", "-c", "user.email=f@x", "commit", "-qm", "fixture"]):
        r = sh(step, cwd=d)
        if r.returncode:
            raise SystemExit(f"{name}: {step} failed: {r.stderr}")
    top = sh(["git", "rev-parse", "--show-toplevel"], cwd=d).stdout.strip()
    assert os.path.realpath(top) == os.path.realpath(d), (top, d)
    return d


def main():
    os.makedirs(FIX, exist_ok=True)
    os.makedirs(EVID, exist_ok=True)
    env = dict(os.environ, KAMA57_SCRATCH=EVID)
    lines = []
    for name, source in batteries.VARIANTS.items():
        d = build(name, source)
        tip = sh(["git", "rev-parse", "HEAD"], cwd=d).stdout.strip()
        for label, instrument in (("checker-base", "precheck-at-base.py"),
                                  ("checker-head", "precheck-at-head.py")):
            r = sh(["python3", os.path.join(SEAT, "instruments", instrument),
                    "--repo", d, "--tip", tip])
            out = " ".join(r.stdout.split())
            lines.append(f"variant={name} {label} exit={r.returncode} :: {out}")
        r = sh(["python3", os.path.join(SEAT, "exec_bind.py"), d, tip], env=env)
        lines.append(f"variant={name} exec-probe exit={r.returncode} :: {' '.join(r.stdout.split())}")
    text = "\n".join(lines) + "\n"
    open(os.path.join(EVID, "variant-matrix.out"), "w").write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
