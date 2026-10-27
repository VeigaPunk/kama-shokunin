#!/usr/bin/env python3
"""X09NewNoopFixtures driver: score seat-authored no-op variants with the round-58 C1
checker at the measured tip. Mirrors tools/round58-c1-counter.py fixture construction
exactly (prereg + three side files from the tip, the candidate at the battery path,
one throwaway git fixture per candidate), but takes an arbitrary variant directory so
files outside the 11 enumerated variants can be measured. Exit 0 iff every candidate was
evaluated (accept/reject is data, not failure)."""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

PREREG = ".ufo/waves/round-56/preregistration.json"
BATTERY = "tools/round56-env-leg-battery.py"
SIDE_FILES = ["tools/round56-env-leg-test.py", "tools/round54-replay-code-audit.py",
              "tools/round56-replay-code-audit.py"]


def clean_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=clean_env())


def blob(repo, tip, path):
    p = git(repo, "show", f"{tip}:{path}")
    if p.returncode:
        raise SystemExit(f"missing blob {tip}:{path}")
    return p.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--checker", required=True)
    ap.add_argument("--variants", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rev = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}").stdout.decode().strip()
    os.makedirs(a.work, exist_ok=True)
    work = tempfile.mkdtemp(prefix="x09-", dir=a.work)
    rows = []
    try:
        common = {PREREG: blob(a.repo, rev, PREREG)}
        for f in SIDE_FILES:
            common[f] = blob(a.repo, rev, f)
        for cand in sorted(pathlib.Path(a.variants).glob("*.py")):
            fx = pathlib.Path(work) / cand.stem
            fx.mkdir()
            if git(fx, "init", "-q").returncode:
                raise SystemExit("git init failed")
            top = git(fx, "rev-parse", "--show-toplevel").stdout.decode().strip()
            if os.path.realpath(top) != os.path.realpath(fx):
                raise SystemExit(f"fixture toplevel mismatch: {top} != {fx}")
            files = dict(common)
            files[BATTERY] = cand.read_bytes()
            for rel, data in files.items():
                dst = fx / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(data)
            git(fx, "add", "-A")
            c = git(fx, "-c", "user.name=x09", "-c", "user.email=x09@invalid",
                    "commit", "-q", "-m", "fixture")
            if c.returncode:
                raise SystemExit(f"fixture commit failed: {c.stderr.decode()}")
            p = subprocess.run([sys.executable, a.checker, "--repo", str(fx), "--tip", "HEAD"],
                               capture_output=True, text=True, timeout=180, cwd=str(fx),
                               env=clean_env())
            verdict = {0: "accept", 1: "reject"}.get(p.returncode, "error")
            rows.append({"variant": cand.name, "verdict": verdict, "exit": p.returncode,
                         "stdout": p.stdout.strip(), "stderr": p.stderr.strip()[-400:]})
    finally:
        shutil.rmtree(work, ignore_errors=True)
    text = json.dumps({"tip": rev, "checker": a.checker, "rows": rows}, indent=1)
    pathlib.Path(a.out).write_text(text + "\n")
    for r in rows:
        print(f"{r['variant']}: {r['verdict']} exit={r['exit']}")
        for ln in r["stdout"].splitlines():
            print(f"  {ln}")
    return 0 if all(r["verdict"] != "error" for r in rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
