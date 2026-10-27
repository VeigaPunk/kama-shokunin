#!/usr/bin/env python3
"""Seat X01 scratch probe: run the round-58 exec checker against battery variants that
are OUTSIDE the 11 enumerated no-ops, to record checker limits (not C1 credit)."""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

S = pathlib.Path(os.environ["S"])
CLONE = S / "clone"
TIP = "e4891d8a4c9c70e97124980c2ec9aee5762a7f0a"
PREREG = ".ufo/waves/round-56/preregistration.json"
BATTERY = "tools/round56-env-leg-battery.py"


def genv():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, env=genv())


def blob(path):
    return git(CLONE, "show", f"{TIP}:{path}").stdout


GEN = blob(f"tests/round58-battery-variants/genuine.py").decode()

P1 = GEN.replace(
    '    p = subprocess.run(["python3", str(TEST), "--counter", str(counter), "--expect", expected],\n'
    '                       capture_output=True, text=True)\n',
    '    p = subprocess.run(["true", "--counter", "decoy"], capture_output=True, text=True)\n', 1)
P1 = P1.replace(
    '    p = subprocess.run(["python3", str(TEST), "--counter", str(counter), "--expect", "detected"],\n'
    '                       capture_output=True, text=True)\n',
    '    p = subprocess.run(["true", "--counter", "decoy"], capture_output=True, text=True)\n', 1)

P2 = GEN.replace(
    '    """Exact receipt-field predicate; never substring membership."""\n'
    '    return fields.get(key) == expected',
    '    """Exact receipt-field predicate; never substring membership."""\n'
    '    return True', 1)

P3 = GEN.replace('results.append(run("round56-counter", NEW, "detected", OUT / "build-c1.out"))',
                 'results.append(run("round56-counter", NEW, "missed", OUT / "build-c1.out"))', 1)

P4 = GEN.replace('    return 0 if all(results) else 1', '    return 0', 1)

CASES = {"P0-genuine-as-fixture": GEN, "P1-decoy-counter-not-invoked": P1,
         "P2-assertion-always-true": P2, "P3-positive-control-expectation-flipped": P3,
         "P4-exit-zero-unconditional": P4, "P5-empty-battery": ""}

checker = CLONE / "tools/round58-battery-exec-check.py"
rows = []
for name, src in CASES.items():
    fx = pathlib.Path(tempfile.mkdtemp(prefix="probe-", dir=S))
    try:
        if git(fx, "init", "-q").returncode:
            raise SystemExit("git init failed")
        top = git(fx, "rev-parse", "--show-toplevel").stdout.decode().strip()
        assert os.path.realpath(top) == os.path.realpath(fx), (top, fx)
        (fx / PREREG).parent.mkdir(parents=True, exist_ok=True)
        (fx / PREREG).write_bytes(blob(PREREG))
        (fx / BATTERY).parent.mkdir(parents=True, exist_ok=True)
        (fx / BATTERY).write_text(src)
        for extra in ("tools/round56-env-leg-test.py", "tools/round54-replay-code-audit.py",
                      "tools/round56-replay-code-audit.py"):
            (fx / extra).write_bytes(blob(extra))
        git(fx, "add", "-A")
        c = git(fx, "-c", "user.name=x01-probe", "-c", "user.email=x01-probe@invalid",
                "commit", "-q", "-m", "probe")
        assert c.returncode == 0, c.stderr
        p = subprocess.run([sys.executable, str(checker), "--repo", str(fx), "--tip", "HEAD"],
                           capture_output=True, text=True, cwd=str(fx), timeout=180, env=genv())
        rows.append((name, p.returncode, p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "",
                     p.stderr.strip()[-300:]))
    finally:
        shutil.rmtree(fx, ignore_errors=True)

for name, rc, last, err in rows:
    print(f"{name}: exit={rc} | {last}" + (f" | stderr={err}" if err else ""))
