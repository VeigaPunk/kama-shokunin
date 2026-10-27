#!/usr/bin/env python3
"""Round-56 C2 calibration counter: compare the frozen battery roster to preregistration.
The gate reads only committed blobs at --tip and binds names, designations and expected
LD_AUDIT outcomes; absent files are the red do-nothing control."""
import argparse
import ast
import json
import os
import subprocess
import sys

BASE = "e10b6d39af450e8d652be9ac2986768b531fe13f"
PREREG = ".ufo/waves/round-56/preregistration.json"
BATTERY = "tools/round56-env-leg-battery.py"


def clean_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    return env


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, env=clean_env())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    rev = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}")
    if rev.returncode:
        print("could-not-evaluate: invalid tip")
        return 2
    tip = rev.stdout.decode().strip()
    preg = git(a.repo, "show", f"{tip}:{PREREG}")
    bat = git(a.repo, "show", f"{tip}:{BATTERY}")
    if preg.returncode or bat.returncode:
        text = f"tip={tip}\npresent=0 roster_match=0 kills=0 controls=0 met=False\n"
        print(text, end="")
        if a.out:
            open(a.out, "w").write(text)
        return 1
    try:
        obj = json.loads(preg.stdout)
        tree = ast.parse(bat.stdout.decode("utf-8", "replace"))
    except (ValueError, SyntaxError) as exc:
        print(f"could-not-evaluate: {exc}")
        return 2
    roster = obj.get("battery", {}).get("roster", {})
    assignment = None
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ROSTER" for t in n.targets):
            try:
                assignment = ast.literal_eval(n.value)
            except (ValueError, SyntaxError):
                pass
    invoked = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        if node.func.id in ("run", "assert_mutant_breaks_detection") and node.args:
            label = node.args[0]
            if isinstance(label, ast.Constant) and isinstance(label.value, str):
                invoked.add(label.value)
    expected = {name for name, spec in roster.items()
                if spec.get("designation") in ("control", "positive-control", "kill")}
    executed = expected <= invoked
    match = assignment == roster and isinstance(roster, dict) and bool(roster)
    kills = sum(1 for v in (roster.values() if isinstance(roster, dict) else []) if v.get("designation") == "kill")
    controls = sum(1 for v in (roster.values() if isinstance(roster, dict) else [])
                   if v.get("designation") in ("control", "positive-control"))
    met = match and executed and kills == 1 and controls == 2
    text = (f"tip={tip}\npresent=1 roster_match={int(match)} kills={kills} controls={controls} "
            f"met={met}\n")
    print(text, end="")
    if a.out:
        open(a.out, "w").write(text)
    return 0 if met else 1


if __name__ == "__main__":
    raise SystemExit(main())
