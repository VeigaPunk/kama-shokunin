#!/usr/bin/env python3
"""Round-59 C1 counter: outcome-bound leg checker versus fixed battery fixtures."""
import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

BENIGN = ["B1-rename-comment", "B2-helper-leg", "B3-concat-labels"]
OLD_NOOPS = ["N01-calls-removed", "N02-if-false", "N03-unused-function", "N04-early-return",
             "N05-env-guard", "N06-run-body-noop", "N07-mutant-assert-noop", "N08-main-not-invoked",
             "N09-empty-loop", "N10-run-rebound", "N11-try-else"]
NEW_NOOPS = ["N12-ignore-leg-result", "N13-wrong-leg-expected", "N14-ignore-mutant-result",
             "N15-duplicate-leg-label", "N16-decoy-counter-call"]
VARIANT_DIR = "tests/round58-battery-variants"
NEW_VARIANT_DIR = "tests/round59-battery-variants"
BATTERY = "tools/round56-env-leg-battery.py"
FILES = [".ufo/waves/round-56/preregistration.json", BATTERY,
         "tools/round56-env-leg-test.py", "tools/round54-replay-code-audit.py",
         "tools/round56-replay-code-audit.py"]
CHECKER = "tools/round59-battery-outcome-check.py"
PREDICATE = "C1-r59 outcome-binding checker accepts genuine+3/3 benign and rejects 16/16 no-ops, errors=0"


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=env)


def blob(repo, tip, path):
    p = git(repo, "show", f"{tip}:{path}")
    if p.returncode:
        raise ValueError(f"missing committed blob {path}")
    return p.stdout


def root_for(arg):
    root = arg or os.environ.get("TMPDIR") or os.path.join(os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku"), "kama-r59")
    os.makedirs(root, exist_ok=True)
    return root


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--checker", help="external checker path for pre-data shortcut controls")
    ap.add_argument("--work")
    ap.add_argument("--out")
    a = ap.parse_args()
    resolved = git(a.repo, "rev-parse", "--verify", f"{a.tip}^{{commit}}")
    if resolved.returncode:
        print("could-not-evaluate: invalid tip")
        return 2
    tip = resolved.stdout.decode().strip()
    work = pathlib.Path(tempfile.mkdtemp(prefix="r59-c1-", dir=root_for(a.work)))
    try:
        if a.checker:
            checker = pathlib.Path(a.checker).resolve()
            if not checker.is_file():
                print("could-not-evaluate: checker file absent")
                return 2
        else:
            checker = work / "outcome-checker.py"
            checker.write_bytes(blob(a.repo, tip, CHECKER))
        outcomes = []
        names = ["genuine"] + BENIGN + OLD_NOOPS + NEW_NOOPS
        for name in names:
            fx = work / name
            fx.mkdir()
            if git(fx, "init", "-q").returncode:
                print("could-not-evaluate: fixture git init failed")
                return 2
            files = {rel: blob(a.repo, tip, rel) for rel in FILES}
            if name in OLD_NOOPS:
                battery_path = f"{VARIANT_DIR}/{name}.py"
            elif name in NEW_NOOPS:
                battery_path = f"{NEW_VARIANT_DIR}/{name}.py"
            elif name in BENIGN:
                battery_path = f"{VARIANT_DIR}/{name}.py"
            else:
                battery_path = f"{VARIANT_DIR}/genuine.py"
            files[BATTERY] = blob(a.repo, tip, battery_path)
            for rel, data in files.items():
                dst = fx / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(data)
            if git(fx, "add", "-A").returncode:
                print("could-not-evaluate: fixture add failed")
                return 2
            commit = git(fx, "-c", "user.name=kama-r59-counter", "-c", "user.email=kama-r59@invalid",
                         "commit", "-qm", "fixture")
            if commit.returncode:
                print("could-not-evaluate: fixture commit failed")
                return 2
            top = git(fx, "rev-parse", "--show-toplevel").stdout.decode().strip()
            if os.path.realpath(top) != os.path.realpath(fx):
                print("could-not-evaluate: fixture toplevel mismatch")
                return 2
            try:
                p = subprocess.run([sys.executable, str(checker), "--repo", str(fx), "--tip", "HEAD"],
                                   capture_output=True, text=True, timeout=90,
                                   env={**os.environ, "TMPDIR": str(work)})
            except subprocess.TimeoutExpired:
                outcomes.append((name, "error", 124, "timeout"))
                continue
            verdict = {0: "accept", 1: "reject"}.get(p.returncode, "error")
            outcomes.append((name, verdict, p.returncode, p.stdout.strip() or p.stderr.strip()))
        accepted = {name: result for name, result, _, _ in outcomes}
        genuine = int(accepted.get("genuine") == "accept")
        benign = sum(accepted.get(n) == "accept" for n in BENIGN)
        rejected = sum(accepted.get(n) == "reject" for n in OLD_NOOPS + NEW_NOOPS)
        errors = sum(v == "error" for _, v, _, _ in outcomes)
        complete = len(outcomes) == 1 + len(BENIGN) + len(OLD_NOOPS) + len(NEW_NOOPS)
        met = complete and genuine == 1 and benign == len(BENIGN) and rejected == len(OLD_NOOPS) + len(NEW_NOOPS) and errors == 0
        lines = [f"tip={tip}", f"predicate={PREDICATE}",
                 f"genuine={genuine}/1 benign={benign}/{len(BENIGN)} noop_rejected={rejected}/{len(OLD_NOOPS)+len(NEW_NOOPS)} errors={errors} met={met}"]
        lines.extend(f"detail: {n} {v} exit={rc}" for n, v, rc, _ in outcomes)
        text = "\n".join(lines) + "\n"
        print(text, end="")
        if a.out:
            pathlib.Path(a.out).write_text(text)
        return 0 if met else 1
    except ValueError as exc:
        print(f"could-not-evaluate: {exc}")
        return 2
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
