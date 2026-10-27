#!/usr/bin/env python3
"""R10C2Counter fixture driver: one clone, six C2 predicate mutants, measured receipts.
Lane stays read-only; all mutations happen inside the scratch clone after a
toplevel guard assertion."""
import os
import pathlib
import shutil
import subprocess

SCRATCH = pathlib.Path("/fast/scratch/hyaku/kama-r56/R10C2Counter")
OUT = SCRATCH / "out"
RECEIPTS = OUT / "receipts"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
CLONE = SCRATCH / "clone"
CHECKER = f"{LANE}/tools/round56-prereg-check.py"
PREREG_PATH = ".ufo/waves/round-56/preregistration.json"
BATTERY_PATH = "tools/round56-env-leg-battery.py"
BASE = "e10b6d39af450e8d652be9ac2986768b531fe13f"
FREEZE = "efc6b3ec6fb6ea308c15855e9b8b62856f4255b7"

env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
           GIT_AUTHOR_NAME="r10c2", GIT_AUTHOR_EMAIL="r10c2@scratch.invalid",
           GIT_COMMITTER_NAME="r10c2", GIT_COMMITTER_EMAIL="r10c2@scratch.invalid",
           TMPDIR=str(OUT / "tmp"))
pathlib.Path(env["TMPDIR"]).mkdir(parents=True, exist_ok=True)
RECEIPTS.mkdir(parents=True, exist_ok=True)


def git(*args, cwd=CLONE):
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=env)
    if p.returncode:
        raise SystemExit(f"git {' '.join(args)}: rc={p.returncode} {p.stderr.strip()}")
    return p.stdout.strip()


def blob(rev, path):
    p = subprocess.run(["git", "-C", LANE, "show", f"{rev}:{path}"],
                       capture_output=True, env=env)
    if p.returncode:
        raise SystemExit(f"blob {rev}:{path}: {p.stderr.decode().strip()}")
    return p.stdout


def check(tag, repo, tip):
    p = subprocess.run(["python3", CHECKER, "--repo", repo, "--tip", tip],
                       capture_output=True, text=True, env=env, cwd=SCRATCH)
    body = p.stdout + p.stderr + f"exit={p.returncode}\n"
    (RECEIPTS / f"{tag}.out").write_text(body)
    stdout_flat = " / ".join(p.stdout.split())
    last_err = p.stderr.strip().splitlines()[-1][:110] if p.stderr.strip() else "-"
    print(f"{tag:22s} tip={tip[:12]} exit={p.returncode} {stdout_flat} | stderr: {last_err}")
    return p.returncode


def build_tip(tag, message, prereg_bytes, battery_bytes):
    (CLONE / PREREG_PATH).unlink(missing_ok=True) if prereg_bytes is None \
        else (CLONE / PREREG_PATH).write_bytes(prereg_bytes)
    (CLONE / BATTERY_PATH).unlink(missing_ok=True) if battery_bytes is None \
        else (CLONE / BATTERY_PATH).write_bytes(battery_bytes)
    git("add", "-A")
    git("commit", "-q", "-m", f"r10c2 fixture: {tag} - {message}")
    return git("rev-parse", "HEAD")


def main():
    if CLONE.exists():
        shutil.rmtree(CLONE)
    git("clone", "--quiet", "--no-hardlinks", f"file://{LANE}", str(CLONE), cwd=SCRATCH)
    toplevel = git("rev-parse", "--show-toplevel")
    if pathlib.Path(toplevel).resolve() != CLONE.resolve():
        raise SystemExit(f"guard: toplevel {toplevel} != {CLONE}")
    print(f"guard-ok toplevel={toplevel}")
    git("checkout", "--quiet", FREEZE)
    lane_tree = git("rev-parse", f"{FREEZE}^{{tree}}", cwd=LANE)
    clone_tree = git("rev-parse", "HEAD^{tree}")
    print(f"tree-equality lane={lane_tree[:12]} clone={clone_tree[:12]} equal={lane_tree == clone_tree}")

    canon_prereg = blob(FREEZE, PREREG_PATH)
    canon_battery = blob(FREEZE, BATTERY_PATH)
    kill_line = b'"m-drop-ldaudit": {"designation": "kill", "expected": "missed"}'
    ctrl_line = b'"m-drop-ldaudit": {"designation": "control", "expected": "missed"}'
    if canon_battery.count(kill_line) != 1:
        raise SystemExit("mutant anchor not unique")

    tips = {}
    tips["t1-designation-swap"] = build_tip(
        "t1-designation-swap", "battery kill->control, prereg frozen",
        canon_prereg, canon_battery.replace(kill_line, ctrl_line))
    tips["t2-missing-battery"] = build_tip(
        "t2-missing-battery", "battery deleted, prereg frozen", canon_prereg, None)
    tips["t3-missing-prereg"] = build_tip(
        "t3-missing-prereg", "prereg deleted, battery frozen", None, canon_battery)
    bad = (b'{\n  "battery": {"roster": {"base-old-counter": "control",'
           b' "round56-counter": "positive-control", "m-drop-ldaudit": "kill"}},\n'
           b'  "controls": {}\n}\n')
    tips["t4-malformed-values"] = build_tip(
        "t4-malformed-values", "prereg roster values are strings", bad, canon_battery)
    tips["t5-root-array"] = build_tip(
        "t5-root-array", "prereg is a JSON array", b"[]\n", canon_battery)
    tips["t6-duplicate-roster"] = build_tip(
        "t6-duplicate-roster", "battery appends unparsable ROSTER binding",
        canon_prereg, canon_battery + b"\n\nROSTER = UNBOUND_NAME\n")

    print("== frozen claims (lane repo) ==")
    check("lane-base", LANE, BASE)
    check("lane-freeze", LANE, FREEZE)
    print("== clone fixtures ==")
    check("clone-freeze", str(CLONE), FREEZE)
    for tag, tip in tips.items():
        check(tag, str(CLONE), tip)
    print("done")


if __name__ == "__main__":
    main()
