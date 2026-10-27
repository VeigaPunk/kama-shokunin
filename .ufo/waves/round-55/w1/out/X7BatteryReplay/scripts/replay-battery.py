#!/usr/bin/env python3
"""X7BatteryReplay: independent replay of the round-55 C1 kill battery.

Reproduces the four named mutants (m-ldpreload/envnames, m-text-flip/code,
m-member-flip/rehash, m-ldaudit-foreign/hostlibs-vector) plus the unmutated
positive control in MY OWN clone, runs the FROZEN counter (tools/round54-replay-code-audit.py
from the lane, unmodified) per mutant, and writes receipts into my out dir.

The L1 harness (.ufo/waves/round-55/c1/battery/run-battery.py) is NOT run: it
would write the L1's receipts. Its MUTANTS table (patch text only, module import
is side-effect free: main() is guarded) is reused verbatim so the mutants are
byte-identical; all clone/commit/run/compare logic here is mine.
"""
import os
import re
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FREEZE = "9c60eae6f7ed84f7da93d219a406aadc30958c6c"
COUNTER = os.path.join(LANE, "tools/round54-replay-code-audit.py")
BATTERY_DIR = os.path.join(LANE, ".ufo/waves/round-55/c1/battery")
LIVE = "tools/kama-llamacpp-live.py"
S = os.environ.get("X7SCRATCH", "/fast/scratch/hyaku/kama-r55/w1/X7BatteryReplay")
OUT = os.environ.get("X7OUT", os.path.join(LANE, ".ufo/waves/round-55/w1/out/X7BatteryReplay"))
CLONE = os.path.join(S, "lane")

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("run_battery_mod", os.path.join(BATTERY_DIR, "run-battery.py"))
run_battery = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run_battery)  # patch table only; main() is __main__-guarded

MUTANTS = run_battery.MUTANTS
ORDER = ["control", "m-ldpreload", "m-text-flip", "m-member-flip", "m-ldaudit-foreign"]
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def git(*args, cwd=None):
    r = run(["git", "-C", cwd or CLONE, *args], env=ENV)
    if r.returncode:
        raise SystemExit(f"git {args}: {r.stderr[:400]}")
    return r.stdout.strip()


def counter(tip, name):
    """Run the frozen counter on my clone; returns (rc, met, text)."""
    outp = os.path.join(OUT, f"{name}.out")
    scratch = os.path.join(S, f"run-{name}")
    shutil.rmtree(scratch, ignore_errors=True)
    os.makedirs(scratch, exist_ok=True)
    p = run([sys.executable, COUNTER, "--repo", CLONE, "--tip", tip,
             "--scratch", scratch, "--out", outp], env=ENV)
    text = open(outp).read() if os.path.isfile(outp) else p.stdout
    lines = text.splitlines()
    met = "met=True" in lines[1] if len(lines) > 1 else False
    return p.returncode, met, text


def main():
    os.makedirs(OUT, exist_ok=True)
    if not os.path.isdir(os.path.join(CLONE, ".git")):
        r = run(["git", "clone", "--shared", LANE, CLONE], env=ENV)
        if r.returncode:
            print(f"clone failed: {r.stderr[:300]}")
            return 2
    top = git("rev-parse", "--show-toplevel")
    assert top == CLONE, f"toplevel {top} != {CLONE}"
    print(f"clone toplevel verified: {top}")

    # record the exact mutant patch text used (independence record)
    with open(os.path.join(OUT, "mutant-patches.txt"), "w") as fh:
        for name, (leg, kind, old, new) in MUTANTS.items():
            fh.write(f"=== {name} leg={leg} kind={kind}\n--- old ---\n{old!r}\n--- new ---\n{new!r}\n")
        fh.write(f"ENV_ANCHOR={run_battery.ENV_ANCHOR!r}\n")
        fh.write(f"FLIP_ANCHOR={run_battery.FLIP_ANCHOR!r}\n")

    live_path = os.path.join(CLONE, LIVE)
    original = git("show", f"{FREEZE}:{LIVE}") + "\n"
    summary = []
    for name in ORDER:
        git("reset", "--hard", FREEZE)
        src = open(live_path).read()
        if src != original:
            print(f"{name}: clone not clean at freeze")
            return 2
        if name != "control":
            leg, kind, old, new = MUTANTS[name]
            if src.count(old) != 1:
                print(f"{name}: anchor not unique ({src.count(old)})")
                return 2
            open(live_path, "w").write(src.replace(old, new))
            git("add", LIVE)
            r = run(["git", "-C", CLONE, "-c", "user.name=fx", "-c", "user.email=fx@invalid",
                     "commit", "-q", "-m", f"X7 battery mutant {name}"], env=ENV)
            if r.returncode:
                print(f"{name}: fixture commit failed: {r.stderr[:300]}")
                return 2
        tip = git("rev-parse", "HEAD")
        rc, met, text = counter(tip, name)
        if name == "control":
            ok = rc == 0 and met
            leg, kind = "all legs", "kill"
        else:
            leg, kind, _old, _new = MUTANTS[name]
            if kind == "vector":
                ok = rc == 0 and met
            else:
                leg_failed = f"{leg} " in "\n".join(
                    ln for ln in text.splitlines() if ln.startswith("detail: "))
                ok = rc == 1 and not met and leg_failed
        summary.append((name, leg, kind, rc, met, ok, tip))
        print(f"replay {name}: leg={leg} kind={kind} exit={rc} met={met} tip={tip[:12]} "
              f"-> {'ok' if ok else 'REPLAY-DIVERGENT'}", flush=True)

    with open(os.path.join(OUT, "replay-summary.txt"), "w") as fh:
        for row in summary:
            fh.write(" ".join(str(x) for x in row) + "\n")
    return 0 if all(s[5] for s in summary) else 1


if __name__ == "__main__":
    sys.exit(main())
