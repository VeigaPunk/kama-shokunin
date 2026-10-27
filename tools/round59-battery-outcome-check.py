#!/usr/bin/env python3
"""Round-59 checker: verify each named battery leg's returned outcome is consequential."""
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

BATTERY = "tools/round56-env-leg-battery.py"
PREREG = ".ufo/waves/round-56/preregistration.json"
SIDE = ("tools/round56-env-leg-test.py", "tools/round54-replay-code-audit.py",
        "tools/round56-replay-code-audit.py")
LABELS = ("base-old-counter", "round56-counter", "m-drop-ldaudit", "mutant-assert")


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=env)


def scratch_root():
    root = os.environ.get("TMPDIR") or os.path.join(os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku"), "kama-r59")
    os.makedirs(root, exist_ok=True)
    return root


def result_for(counter_path):
    """Read the runner's BAD_ENV declaration and return its synthetic observed state."""
    text = pathlib.Path(counter_path).read_text(errors="replace")
    match = re.search(r"BAD_ENV\s*=\s*\(([^)]*)\)", text)
    return "detected" if match and "LD_AUDIT" in match.group(1) else "missed"


def child(src_path, repo, tip, out_path, fault_label):
    real_run, real_popen = subprocess.run, subprocess.Popen
    tree = set(real_run(["git", "-C", repo, "ls-tree", "-r", "--name-only", tip], capture_output=True,
                        text=True).stdout.splitlines())
    frames, stack, allow, virtual = [], [], [], {}

    def blob_for(path):
        parts = pathlib.PurePath(str(path)).parts
        for i in range(len(parts)):
            rel = "/".join(parts[i:]).lstrip("/")
            if rel in tree:
                allow.append(True)
                try:
                    p = real_run(["git", "-C", repo, "show", f"{tip}:{rel}"], capture_output=True,
                                 text=True)
                    if p.returncode:
                        raise FileNotFoundError(rel)
                    return p.stdout
                finally:
                    allow.pop()
        raise FileNotFoundError(str(path))

    def fake_run(cmd, *args, **kwargs):
        argv = [str(c) for c in cmd] if isinstance(cmd, (list, tuple)) else [str(cmd)]
        if not stack:
            return subprocess.CompletedProcess(argv, 2, "", "unbound subprocess")
        rec = stack[-1]
        rec["calls"].append(argv)
        counter = None
        if "--counter" in argv and argv.index("--counter") + 1 < len(argv):
            counter = argv[argv.index("--counter") + 1]
        observed = result_for(counter) if counter else ""
        expected = None
        if "--expect" in argv and argv.index("--expect") + 1 < len(argv):
            expected = argv[argv.index("--expect") + 1]
        if rec["label"] == fault_label:
            observed = "missed" if observed == "detected" else "detected"
        stdout = f"ld_audit={observed} pid=1 problems=[]\n"
        rc = 0 if expected == observed else 1
        return subprocess.CompletedProcess(argv, rc, stdout, "")

    def blocked(*args, **kwargs):
        raise RuntimeError("process spawning blocked by round-59 harness")

    class FakeTD:
        def __init__(self, *args, **kwargs):
            self.name = "/virtual/round59"
        def __enter__(self): return self.name
        def __exit__(self, *args): return False
        def cleanup(self): return None

    subprocess.run = subprocess.call = subprocess.check_call = fake_run
    subprocess.check_output = lambda cmd, *a, **k: fake_run(cmd).stdout
    subprocess.Popen = lambda *a, **k: real_popen(*a, **k) if allow else blocked()
    os.system = blocked
    def read_text(self, *args, **kwargs):
        if str(self) in virtual:
            return virtual[str(self)]
        return blob_for(self)
    pathlib.Path.read_text = read_text
    pathlib.Path.write_text = lambda self, data, *a, **k: virtual.__setitem__(str(self), data) or len(data)
    pathlib.Path.write_bytes = lambda self, data: len(data)
    pathlib.Path.mkdir = lambda self, *a, **k: None
    tempfile.TemporaryDirectory = FakeTD
    sys.argv = [src_path]
    with open(src_path, encoding="utf-8") as source:
        code = compile(source.read(), src_path, "exec")
    exit_code = 0

    def profile(frame, event, arg):
        if frame.f_code.co_filename != src_path or frame.f_code.co_name not in ("run", "assert_mutant_breaks_detection"):
            return
        if event == "call":
            label = frame.f_locals.get(frame.f_code.co_varnames[0]) if frame.f_code.co_name == "run" else "mutant-assert"
            rec = {"label": label, "calls": [], "returned": None}
            stack.append(rec)
            frames.append(rec)
        elif event == "return" and stack and stack[-1]["label"] == ("mutant-assert" if frame.f_code.co_name == "assert_mutant_breaks_detection" else frame.f_locals.get("label")):
            stack[-1]["returned"] = arg
            stack.pop()


    sys.setprofile(profile)
    try:
        try:
            exec(code, {"__name__": "__main__", "__file__": src_path})
        except SystemExit as exc:
            exit_code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    except BaseException as exc:
        return {"error": f"{type(exc).__name__}: {exc}", "exit": 2, "frames": frames}
    finally:
        sys.setprofile(None)
    with open(out_path, "w", encoding="utf-8") as out:
        json.dump({"exit": exit_code, "frames": frames}, out)
    return {"exit": exit_code, "frames": frames}


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
    checker = pathlib.Path(__file__).resolve()
    work = tempfile.mkdtemp(prefix="r59-c1-", dir=scratch_root())
    try:
        fx = pathlib.Path(work) / "battery"
        fx.mkdir()
        if git(fx, "init", "-q").returncode:
            print("could-not-evaluate: git init failed")
            return 2
        files = [PREREG, BATTERY, *SIDE]
        for rel in files:
            p = git(a.repo, "show", f"{tip}:{rel}")
            if p.returncode:
                print(f"could-not-evaluate: missing {rel}")
                return 2
            dst = fx / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(p.stdout)
        p = git(fx, "add", "-A")
        if p.returncode:
            print("could-not-evaluate: fixture git add failed")
            return 2
        p = git(fx, "-c", "user.name=kama-r59-counter", "-c", "user.email=kama-r59@invalid", "commit", "-qm", "fixture")
        if p.returncode:
            print("could-not-evaluate: fixture commit failed")
            return 2
        base = fx / BATTERY
        results = []
        for fault in ("", *LABELS):
            outcome_path = pathlib.Path(work) / (("normal" if not fault else "fault-" + fault) + ".json")
            child_run = subprocess.run(
                [sys.executable, str(checker), "--child", "--repo", str(fx), "--tip", "HEAD",
                 "--source", str(base), "--out", str(outcome_path), "--fault", fault],
                capture_output=True, text=True, timeout=60, env={**os.environ, "TMPDIR": scratch_root()})
            if child_run.returncode or not outcome_path.is_file():
                results.append({"fault": fault or "baseline", "passed": False, "exit": 2,
                                "error": child_run.stderr or "child failed"})
                continue
            outcome = json.loads(outcome_path.read_text())
            frames = outcome.get("frames", [])
            by_label = {f.get("label"): f for f in frames}
            expected_labels = set(LABELS)
            names_ok = set(by_label) == expected_labels and len(frames) == len(expected_labels)
            per_leg = {}
            for label in LABELS:
                frame = by_label.get(label, {})
                calls = frame.get("calls", [])
                per_leg[label] = (len(calls) == 1 and "--counter" in calls[0]
                                  and "--expect" in calls[0] and frame.get("returned") is True)
            if not fault:
                passed = names_ok and all(per_leg.values()) and outcome.get("exit") == 0
            else:
                passed = names_ok and per_leg.get(fault, False) and outcome.get("exit") == 1
            results.append({"fault": fault or "baseline", "passed": passed, "exit": outcome.get("exit"),
                            "labels": names_ok, "per_leg": per_leg, "error": outcome.get("error")})
        met = all(r["passed"] for r in results)
        text = f"tip={tip}\npredicate=C1-r59 each named leg returns a bound expected outcome; one-leg faults propagate\n"
        text += f"runs={len(results)} passed={sum(r['passed'] for r in results)}/{len(results)} errors={sum(bool(r.get('error')) for r in results)} met={met}\n"
        text += "\n".join(json.dumps(r, sort_keys=True) for r in results) + "\n"
        print(text, end="")
        if a.out:
            pathlib.Path(a.out).write_text(text)
        return 0 if met else 1
    finally:
        import shutil
        shutil.rmtree(work, ignore_errors=True)


def child_main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--child", action="store_true")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fault", default="")
    a = ap.parse_args()
    result = child(a.source, a.repo, a.tip, a.out, a.fault)
    return 2 if result.get("error") else 0


def entry():
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        return child_main()
    return main()


if __name__ == "__main__":
    raise SystemExit(entry())
