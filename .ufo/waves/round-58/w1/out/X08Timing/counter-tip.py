#!/usr/bin/env python3
"""Round-58 C1 (operability) frozen counter: score a battery-roster checker against the
committed variant set `tests/round58-battery-variants/` (1 genuine, 3 behaviour-preserving
rewrites, 11 no-op variants whose roster literal stays intact).

Predicate (same sentence as .ufo/waves/round-58/controls/freeze.txt):
  C1-r58: the checker accepts the genuine round-56 battery and 3/3 behaviour-preserving
  rewrites, and rejects 11/11 enumerated no-op variants, with 0 evaluation errors.

Reads only committed blobs at --tip (variants, preregistration, the files the battery
reads) plus the checker under test, taken from --checker FILE or --checker-blob REV:PATH.
Each variant is committed into a throwaway fixture repo under the scratch root (git is
always called with -C <fixture>); the checker is run as
`python3 CHECKER --repo <fixture> --tip HEAD` and exit 0 = accepted, 1 = rejected,
anything else = evaluation error.  Exit 0 here = predicate met, 1 = not met, 2 = could
not evaluate.  Scratch root: --work, else $TMPDIR, else $HYAKU_SCRATCH/kama-r58 (never /tmp
unless the operator sets it); the fixture tree is removed on exit."""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

VARIANTS = "tests/round58-battery-variants"
BENIGN = ["B1-rename-comment", "B2-helper-leg", "B3-concat-labels"]
NOOPS = ["N01-calls-removed", "N02-if-false", "N03-unused-function", "N04-early-return",
         "N05-env-guard", "N06-run-body-noop", "N07-mutant-assert-noop", "N08-main-not-invoked",
         "N09-empty-loop", "N10-run-rebound", "N11-try-else"]
PREREG = ".ufo/waves/round-56/preregistration.json"
BATTERY = "tools/round56-env-leg-battery.py"
SIDE_FILES = ["tools/round56-env-leg-test.py", "tools/round54-replay-code-audit.py",
              "tools/round56-replay-code-audit.py"]
PREDICATE = "C1-r58 accept genuine+3/3 benign, reject 11/11 no-op, errors=0"


def genv():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    return env


def git(repo, *args, inp=None):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=genv(), input=inp)


def blob(repo, tip, path):
    p = git(repo, "show", f"{tip}:{path}")
    if p.returncode:
        raise SystemExit(f"could-not-evaluate: missing blob {tip}:{path}")
    return p.stdout


def scratch_root(arg):
    root = arg or os.environ.get("TMPDIR") or os.path.join(
        os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku"), "kama-r58")
    os.makedirs(root, exist_ok=True)
    return root


def verdict(checker, fixture):
    p = subprocess.run([sys.executable, str(checker), "--repo", str(fixture), "--tip", "HEAD"],
                       capture_output=True, text=True, timeout=120, cwd=str(fixture),
                       env={**genv(), "PYTHONDONTWRITEBYTECODE": "1"})
    return {0: "accept", 1: "reject"}.get(p.returncode, "error"), p.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--checker")
    ap.add_argument("--checker-blob", help="REV:PATH read from --repo")
    ap.add_argument("--work")
    ap.add_argument("--out")
    a = ap.parse_args()
    rev = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}")
    if rev.returncode:
        print("could-not-evaluate: invalid tip")
        return 2
    tip = rev.stdout.decode().strip()
    work = tempfile.mkdtemp(prefix="c1-", dir=scratch_root(a.work))
    try:
        if a.checker_blob:
            r, _, pth = a.checker_blob.partition(":")
            checker = pathlib.Path(work) / "checker-under-test.py"
            checker.write_bytes(blob(a.repo, r, pth))
        elif a.checker:
            checker = pathlib.Path(a.checker).resolve()
        else:
            print("could-not-evaluate: --checker or --checker-blob required")
            return 2
        if not checker.is_file():
            print("could-not-evaluate: checker file absent")
            return 2
        common = {PREREG: blob(a.repo, tip, PREREG)}
        for f in SIDE_FILES:
            common[f] = blob(a.repo, tip, f)
        rows = []
        for name in ["genuine"] + BENIGN + NOOPS:
            fx = pathlib.Path(work) / name
            fx.mkdir()
            if git(fx, "init", "-q").returncode:
                print("could-not-evaluate: git init failed")
                return 2
            top = git(fx, "rev-parse", "--show-toplevel").stdout.decode().strip()
            if os.path.realpath(top) != os.path.realpath(fx):
                print("could-not-evaluate: fixture toplevel mismatch")
                return 2
            files = dict(common)
            files[BATTERY] = blob(a.repo, tip, f"{VARIANTS}/{name}.py")
            for rel, data in files.items():
                dst = fx / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(data)
            git(fx, "add", "-A")
            c = git(fx, "-c", "user.name=c1-counter", "-c", "user.email=c1-counter@invalid",
                    "commit", "-q", "-m", "fixture")
            if c.returncode:
                print("could-not-evaluate: fixture commit failed")
                return 2
            try:
                v, rc = verdict(checker, fx)
            except subprocess.TimeoutExpired:
                v, rc = "error", 124
            rows.append((name, v, rc))
        got = {n: v for n, v, _ in rows}
        gen = int(got["genuine"] == "accept")
        ben = sum(got[n] == "accept" for n in BENIGN)
        noo = sum(got[n] == "reject" for n in NOOPS)
        err = sum(v == "error" for _, v, _ in rows)
        met = gen == 1 and ben == len(BENIGN) and noo == len(NOOPS) and err == 0
        lines = [f"tip={tip}", f"predicate={PREDICATE}",
                 f"genuine={gen}/1 benign={ben}/{len(BENIGN)} noop_rejected={noo}/{len(NOOPS)} "
                 f"errors={err} met={met}"]
        lines += [f"detail: {n} {v} exit={rc}" for n, v, rc in rows]
        text = "\n".join(lines) + "\n"
        print(text, end="")
        if a.out:
            pathlib.Path(a.out).write_text(text)
        return 0 if met else 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
