#!/usr/bin/env python3
"""Round-58 C1 checker: bind the declared battery roster to *executed* battery legs.

Replaces the round-57 syntactic call-site walk of tools/round56-prereg-check.py (which
dead code, an unused function, an early return or a rebound `run` all satisfy).  The
committed battery blob at --tip is executed as `__main__` in a child interpreter under
a hermetic harness:
  * subprocess.run/call/check_call/check_output are replaced by a recorder that returns a
    canned CompletedProcess; Popen and os.system are blocked;
  * pathlib.Path.read_text serves committed blobs of the --repo tip (by longest repo-
    relative path suffix), write_text/mkdir/write_bytes are swallowed, and
    tempfile.TemporaryDirectory yields a virtual name - nothing is written, nothing is run;
  * sys.setprofile (call/return events, https://docs.python.org/3/library/sys.html#sys.setprofile)
    records every call of a function named `run` or `assert_mutant_breaks_detection`
    defined in the battery file, with the first argument as its label and the subprocess
    invocations made while that frame is on the stack.
Verdict (met): the preregistered ROSTER matches the battery literal, kills == 1 and
controls == 2, every control/positive-control/kill roster label was passed to a `run`
frame that issued at least one subprocess invocation carrying `--counter`, and, if the
battery defines assert_mutant_breaks_detection, that function was invoked at least once
and every invocation issued at least one subprocess invocation.  Exit 0 met, 1 not met,
2 could not evaluate (child failure or timeout).  Scratch: --work, $TMPDIR, else
$HYAKU_SCRATCH/kama-r58; removed on exit."""
import argparse
import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile

PREREG = ".ufo/waves/round-56/preregistration.json"
BATTERY = "tools/round56-env-leg-battery.py"
WATCHED = ("run", "assert_mutant_breaks_detection")
TIMEOUT = 60


def clean_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, env=clean_env())


def harness(src_path, repo, tip, out_path):
    """Child mode: execute src_path as __main__ under the hermetic harness."""
    import pathlib
    import tempfile as tf
    real_run, real_popen, allow = subprocess.run, subprocess.Popen, []
    tree = set(real_run(["git", "-C", repo, "ls-tree", "-r", "--name-only", tip],
                        capture_output=True, text=True, env=clean_env()).stdout.split("\n"))
    frames, stack = [], []

    def blob_for(path):
        parts = pathlib.PurePath(str(path)).parts
        for i in range(len(parts)):
            rel = "/".join(parts[i:]).lstrip("/")
            if rel in tree:
                allow.append(1)
                try:
                    return real_run(["git", "-C", repo, "show", f"{tip}:{rel}"], capture_output=True,
                                    text=True, env=clean_env()).stdout
                finally:
                    allow.pop()
        raise FileNotFoundError(str(path))

    def fake_run(cmd, *a, **k):
        argv = [str(c) for c in cmd] if isinstance(cmd, (list, tuple)) else [str(cmd)]
        if stack:
            stack[-1]["sub"].append(argv)
        return subprocess.CompletedProcess(argv, 0, "ld_audit=detected\n", "")

    def blocked(*a, **k):
        raise RuntimeError("blocked by harness")

    class FakeTD:
        def __init__(self, *a, **k):
            self.name = "/virtual/" + str(k.get("prefix", "tmp")) + "x"

        def __enter__(self):
            return self.name

        def __exit__(self, *e):
            return False

        def cleanup(self):
            return None

    subprocess.run = subprocess.call = subprocess.check_call = fake_run
    subprocess.check_output = lambda cmd, *a, **k: fake_run(cmd).stdout
    subprocess.Popen = lambda *a, **k: real_popen(*a, **k) if allow else blocked()
    os.system = blocked
    pathlib.Path.read_text = lambda self, *a, **k: blob_for(self)
    pathlib.Path.write_text = lambda self, data, *a, **k: len(data)
    pathlib.Path.write_bytes = lambda self, data: len(data)
    pathlib.Path.mkdir = lambda self, *a, **k: None
    tf.TemporaryDirectory = FakeTD
    src = open(src_path).read()
    code = compile(src, src_path, "exec")

    def prof(frame, event, arg):
        if frame.f_code.co_filename != src_path or frame.f_code.co_name not in WATCHED:
            return
        if event == "call":
            first = frame.f_code.co_varnames[0] if frame.f_code.co_argcount else None
            label = frame.f_locals.get(first) if first else None
            rec = {"fn": frame.f_code.co_name, "label": label if isinstance(label, str) else None,
                   "sub": [], "frame": id(frame)}
            stack.append(rec)
            frames.append(rec)
        elif event == "return" and stack and stack[-1]["frame"] == id(frame):
            stack.pop()

    err = None
    sys.setprofile(prof)
    try:
        exec(code, {"__name__": "__main__", "__file__": src_path})
    except SystemExit:
        pass
    except BaseException as exc:  # noqa: BLE001 - a crashing battery is evidence, not a harness fault
        err = f"{type(exc).__name__}: {exc}"
    finally:
        sys.setprofile(None)
    rows = [{"fn": f["fn"], "label": f["label"], "sub": len(f["sub"]),
             "counter": sum(1 for s in f["sub"] if "--counter" in s)} for f in frames]
    with open(out_path, "w") as fh:
        json.dump({"frames": rows, "error": err}, fh)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--out")
    ap.add_argument("--work")
    ap.add_argument("--harness", help=argparse.SUPPRESS)
    ap.add_argument("--harness-out", help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.harness:
        return harness(a.harness, a.repo, a.tip, a.harness_out)
    rev = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}")
    if rev.returncode:
        print("could-not-evaluate: invalid tip")
        return 2
    tip = rev.stdout.decode().strip()
    preg = git(a.repo, "show", f"{tip}:{PREREG}")
    bat = git(a.repo, "show", f"{tip}:{BATTERY}")
    if preg.returncode or bat.returncode:
        text = f"tip={tip}\npresent=0 roster_match=0 kills=0 controls=0 executed=0 met=False\n"
        print(text, end="")
        if a.out:
            open(a.out, "w").write(text)
        return 1
    try:
        roster = json.loads(preg.stdout).get("battery", {}).get("roster", {})
        tree = ast.parse(bat.stdout.decode("utf-8", "replace"))
    except (ValueError, SyntaxError) as exc:
        print(f"could-not-evaluate: {exc}")
        return 2
    assignment = None
    defines_assert = False
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ROSTER" for t in n.targets):
            try:
                assignment = ast.literal_eval(n.value)
            except (ValueError, SyntaxError):
                pass
        if isinstance(n, ast.FunctionDef) and n.name == "assert_mutant_breaks_detection":
            defines_assert = True
    match = isinstance(roster, dict) and bool(roster) and assignment == roster
    vals = list(roster.values()) if isinstance(roster, dict) else []
    kills = sum(1 for v in vals if v.get("designation") == "kill")
    controls = sum(1 for v in vals if v.get("designation") in ("control", "positive-control"))
    expected = {k for k, v in (roster.items() if isinstance(roster, dict) else [])
                if v.get("designation") in ("control", "positive-control", "kill")}
    root = a.work or os.environ.get("TMPDIR") or os.path.join(
        os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku"), "kama-r58")
    os.makedirs(root, exist_ok=True)
    work = tempfile.mkdtemp(prefix="exec-", dir=root)
    try:
        src = os.path.join(work, "battery.py")
        res = os.path.join(work, "result.json")
        open(src, "wb").write(bat.stdout)
        try:
            p = subprocess.run([sys.executable, os.path.abspath(__file__), "--repo", a.repo, "--tip", tip,
                                "--harness", src, "--harness-out", res],
                               capture_output=True, text=True, timeout=TIMEOUT, cwd=work, env=clean_env())
        except subprocess.TimeoutExpired:
            print("could-not-evaluate: harness timeout")
            return 2
        if p.returncode or not os.path.exists(res):
            print(f"could-not-evaluate: harness failed rc={p.returncode}")
            return 2
        frames = json.load(open(res))["frames"]
    finally:
        shutil.rmtree(work, ignore_errors=True)
    ran = {f["label"] for f in frames if f["fn"] == "run" and f["counter"] >= 1}
    asserts = [f for f in frames if f["fn"] == "assert_mutant_breaks_detection"]
    assert_ok = (not defines_assert) or (bool(asserts) and all(f["sub"] >= 1 for f in asserts))
    executed = bool(expected) and expected <= ran and assert_ok
    met = match and executed and kills == 1 and controls == 2
    text = (f"tip={tip}\npresent=1 roster_match={int(match)} kills={kills} controls={controls} "
            f"executed={int(executed)} legs={len(ran & expected)}/{len(expected)} "
            f"mutant_assert={'n/a' if not defines_assert else len(asserts)} met={met}\n")
    print(text, end="")
    if a.out:
        open(a.out, "w").write(text)
    return 0 if met else 1


if __name__ == "__main__":
    raise SystemExit(main())
