#!/usr/bin/env python3
"""R04DecoyArgv: smallest argv-routing no-op vs round-59 C1 checker/counter.

Constructs a one-change mutant of the committed genuine battery whose every leg
routes argv to `python3 other-script --counter ... --expect ...` (never the
committed counter runner), builds counter-identical fixtures in scratch, and
scores them with the committed checker bytes. Control: frozen C1 counter run.
"""
import difflib
import os
import pathlib
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
TIP = "aca8d0067ea25627c5015c2193c843965148bc8e"
ROOT = pathlib.Path("/fast/scratch/hyaku/kama-r59/R04DecoyArgv")
TMP = ROOT / "tmp"
WORK = ROOT / "work"
OUTDIR = ROOT / "out"
os.environ["TMPDIR"] = str(TMP)
for d in (TMP, WORK, OUTDIR):
    d.mkdir(parents=True, exist_ok=True)

PREREG = ".ufo/waves/round-56/preregistration.json"
BATTERY = "tools/round56-env-leg-battery.py"
SIDE = ("tools/round56-env-leg-test.py", "tools/round54-replay-code-audit.py",
        "tools/round56-replay-code-audit.py")
CHECKER = "tools/round59-battery-outcome-check.py"
GENUINE = "tests/round58-battery-variants/genuine.py"
OLD = '["python3", str(TEST), "--counter"'
NEW = '["python3", "other-script", "--counter"'


def git(repo, *args, ident=False):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    cmd = ["git", "-C", str(repo)]
    if ident:
        cmd += ["-c", "user.name=kama-r59-counter", "-c", "user.email=kama-r59@invalid"]
    return subprocess.run(cmd + list(args), capture_output=True, text=True, env=env)


def blob(rel):
    p = git(LANE, "show", f"{TIP}:{rel}")
    assert p.returncode == 0, f"missing blob {rel}: {p.stderr.strip()}"
    return p.stdout


def build_fixture(name, battery_bytes):
    fx = WORK / name
    if fx.exists():
        import shutil
        shutil.rmtree(fx)
    fx.mkdir()
    assert git(fx, "init", "-q").returncode == 0
    files = {PREREG: blob(PREREG), BATTERY: battery_bytes}
    for rel in SIDE:
        files[rel] = blob(rel)
    for rel, data in files.items():
        dst = fx / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(data)
    assert git(fx, "add", "-A").returncode == 0
    top = git(fx, "rev-parse", "--show-toplevel").stdout.strip()
    assert top == str(fx), f"toplevel mismatch {top} != {fx}"
    p = git(fx, "commit", "-qm", "fixture", ident=True)
    assert p.returncode == 0, p.stderr.strip()
    assert git(fx, "rev-parse", "--show-toplevel").stdout.strip() == str(fx)
    return fx


def score(fx, label):
    checker = WORK / "outcome-checker.py"
    checker.write_text(blob(CHECKER))
    p = subprocess.run([sys.executable, str(checker), "--repo", str(fx), "--tip", "HEAD"],
                       capture_output=True, text=True, timeout=400,
                       env={**os.environ, "TMPDIR": str(TMP)})
    (OUTDIR / f"{label}.stdout.txt").write_text(p.stdout)
    (OUTDIR / f"{label}.stderr.txt").write_text(p.stderr)
    print(f"### {label} exit={p.returncode}")
    print(p.stdout, end="")
    if p.stderr.strip():
        print("[stderr] " + p.stderr.strip()[:500])
    return p.returncode


def main():
    resolved = git(LANE, "rev-parse", "--verify", TIP + "^{commit}").stdout.strip()
    print(f"tip-resolved={resolved} matches={resolved == TIP}")

    genuine = blob(GENUINE)
    n_old = genuine.count(OLD)
    assert n_old == 2, f"argv anchor count {n_old} != 2"
    d1 = genuine.replace(OLD, NEW)
    assert "str(TEST)" not in d1 and d1.count('"other-script"') == 2
    (OUTDIR / "decoy-argv-battery.py").write_text(d1)
    print(f"decoy D1 bytes={len(d1)} genuine bytes={len(genuine)} delta=2 argv[1] sites")

    d3 = d1.replace('"--counter", str(counter)', '"--counter", "other-counter.py"')
    assert d3.count('"other-counter.py"') == 2
    (OUTDIR / "decoy-uncommitted-counter-value.py").write_text(d3)

    n16 = blob("tests/round59-battery-variants/N16-decoy-counter-call.py")
    diff = "".join(difflib.unified_diff(genuine.splitlines(True),
                                        n16.splitlines(True),
                                        "genuine", "N16-decoy-counter-call"))
    (OUTDIR / "n16-vs-genuine.diff").write_text(diff)

    # Control: frozen C1 counter command, committed bytes (worktree counter == tip blob).
    p = subprocess.run([sys.executable, "tools/round59-c1-counter.py", "--repo", LANE,
                        "--tip", TIP, "--work", str(WORK)],
                       capture_output=True, text=True, cwd=LANE,
                       env={**os.environ}, timeout=1200)
    (OUTDIR / "c1-counter-control.stdout.txt").write_text(p.stdout)
    (OUTDIR / "c1-counter-control.stderr.txt").write_text(p.stderr)
    print(f"### c1-counter-control exit={p.returncode}")
    print(p.stdout, end="")
    if p.stderr.strip():
        print("[stderr] " + p.stderr.strip()[:500])

    score(build_fixture("D1-decoy-argv", d1), "D1-decoy-argv")
    score(build_fixture("D3-decoy-uncommitted-value", d3), "D3-decoy-uncommitted-value")


main()
