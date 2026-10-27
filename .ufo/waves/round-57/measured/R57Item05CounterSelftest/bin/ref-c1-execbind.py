#!/usr/bin/env python3
"""Reference C1 instrument for the round-57 E03 selftest.

Shape-compatible with `tools/round56-prereg-check.py` (same CLI, same summary
fields) plus two additions the selftest's --require-witness mode demands:
`battery_sha256=` and `prereg_sha256=` of the committed blobs it read.

The binding is *reachability*, not a bare `ast.walk`: a label counts as executed
only if its `run(...)`/`assert_mutant_breaks_detection(...)` call site is live
from the module's `if __name__ == "__main__"` block (or, absent that guard, from
the module body), in source order, with constant-false branches skipped and
nothing after an unconditional `return`/`raise` counted.
"""
import argparse
import ast
import hashlib
import json
import subprocess
import sys

PREREG = ".ufo/waves/round-56/preregistration.json"
BATTERY = "tools/round56-env-leg-battery.py"
LABEL_CALLS = ("run", "assert_mutant_breaks_detection")


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                          env={"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
                               "PATH": "/usr/bin:/bin"})


def const_bool(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.Constant) and node.value in (0, 1):
        return bool(node.value)
    return None


class Reach:
    def __init__(self, tree):
        self.defined = {n.name: n for n in ast.walk(tree)
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        self.labels, self.seen = set(), set()

    def calls(self, node):
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Call) or not isinstance(sub.func, ast.Name):
                continue
            name = sub.func.id
            if name in LABEL_CALLS and sub.args:
                a0 = sub.args[0]
                if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                    self.labels.add(a0.value)
            elif name in self.defined and name not in self.seen:
                self.seen.add(name)
                self.stmts(self.defined[name].body)

    def stmts(self, body):
        for st in body:
            if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(st, (ast.Return, ast.Raise)):
                self.calls(st)
                return
            if isinstance(st, ast.If):
                b = const_bool(st.test)
                if b is not False:
                    self.stmts(st.body)
                if b is not True:
                    self.stmts(st.orelse)
                continue
            if isinstance(st, (ast.For, ast.AsyncFor, ast.While)):
                self.calls(st.target if hasattr(st, "target") else st.iter)
                self.stmts(st.body)
                self.stmts(st.orelse)
                continue
            if isinstance(st, (ast.With, ast.AsyncWith)):
                self.calls(st)
                self.stmts(st.body)
                continue
            if isinstance(st, ast.Try):
                self.stmts(st.body)
                for h in st.handlers:
                    self.stmts(h.body)
                self.stmts(st.orelse)
                self.stmts(st.finalbody)
                continue
            self.calls(st)


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
    expected = {name for name, spec in roster.items()
                if spec.get("designation") in ("control", "positive-control", "kill")}
    match = assignment == roster and isinstance(roster, dict) and bool(roster)
    kills = sum(1 for v in roster.values() if v.get("designation") == "kill")
    controls = sum(1 for v in roster.values() if v.get("designation") in ("control", "positive-control"))

    r = Reach(tree)
    entry = False
    for st in tree.body:
        if isinstance(st, ast.If) and isinstance(st.test, ast.Compare):
            src = ast.unparse(st.test)
            if "__name__" in src and "__main__" in src:
                entry = True
                r.stmts(st.body)
    if not entry:
        r.stmts(tree.body)
    executed = expected <= r.labels
    met = match and executed and kills == 1 and controls == 2
    text = (f"tip={tip}\npresent=1 roster_match={int(match)} kills={kills} controls={controls} "
            f"met={met}\n"
            f"battery_sha256={hashlib.sha256(bat.stdout).hexdigest()}\n"
            f"prereg_sha256={hashlib.sha256(preg.stdout).hexdigest()}\n"
            f"executed={len(r.labels & expected)}/{len(expected)}\n")
    print(text, end="")
    if a.out:
        open(a.out, "w").write(text)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
