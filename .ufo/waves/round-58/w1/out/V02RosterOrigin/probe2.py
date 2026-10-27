#!/usr/bin/env python3
"""V02RosterOrigin probe 2: the two counts vs roster identity.
P6 adds a fourth roster entry whose designation is outside the counted class on both
surfaces; P7 reproduces round-56 R11C2Mutation mutant B (kill->control, both surfaces
synced) against the round-58 checker."""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
TIP = "e4891d8a4c9c70e97124980c2ec9aee5762a7f0a"
S = "/fast/scratch/hyaku/kama-r58/V02RosterOrigin"
BATTERY = "tools/round56-env-leg-battery.py"
PREREG = ".ufo/waves/round-56/preregistration.json"
SIDE = ["tools/round56-env-leg-test.py", "tools/round54-replay-code-audit.py",
        "tools/round56-replay-code-audit.py"]
CHECKER = os.path.join(S, "checker-r58.py")


def env():
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e["GIT_CONFIG_GLOBAL"] = os.devnull
    e["GIT_CONFIG_NOSYSTEM"] = "1"
    e["TMPDIR"] = S
    return e


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, env=env())


def blob(p, rev=TIP):
    r = git(LANE, "show", f"{rev}:{p}")
    assert r.returncode == 0, p
    return r.stdout


def once(t, old, new):
    assert t.count(old) == 1, (t.count(old), old)
    return t.replace(old, new)


BAT = blob(BATTERY).decode()
PREG = json.loads(blob(PREREG))
CHECKER = os.path.join(S, "checker-r58.py")
if not os.path.exists(CHECKER):
    pathlib.Path(CHECKER).write_bytes(blob("tools/round58-battery-exec-check.py"))


def synced(roster):
    p = json.loads(json.dumps(PREG))
    p["battery"]["roster"] = roster
    return json.dumps(p, indent=2).encode() + b"\n"


r = {k: dict(v) for k, v in PREG["battery"]["roster"].items()}
r["extra-annotation"] = {"designation": "note", "expected": "n/a"}
b = once(BAT, '    "m-drop-ldaudit": {"designation": "kill", "expected": "missed"},\n',
         '    "m-drop-ldaudit": {"designation": "kill", "expected": "missed"},\n'
         '    "extra-annotation": {"designation": "note", "expected": "n/a"},\n')
P6 = ("P6-fourth-entry", b.encode(), synced(r), "4 roster entries, 1 kill 2 controls + uncounted note")

r7 = {k: dict(v) for k, v in PREG["battery"]["roster"].items()}
r7["m-drop-ldaudit"] = {"designation": "control", "expected": "missed"}
b7 = once(BAT, '"m-drop-ldaudit": {"designation": "kill", "expected": "missed"}',
          '"m-drop-ldaudit": {"designation": "control", "expected": "missed"}')
P7 = ("P7-kill-to-control-both-surfaces", b7.encode(), synced(r7),
      "round-56 R11 mutant B reproduced: equality holds, counts must bite")

for name, bat, preg, note in [P6, P7]:
    fx = pathlib.Path(tempfile.mkdtemp(prefix=name + "-", dir=S))
    assert git(fx, "init", "-q").returncode == 0
    top = git(fx, "rev-parse", "--show-toplevel").stdout.decode().strip()
    assert os.path.realpath(top) == os.path.realpath(fx), (top, fx)
    files = {BATTERY: bat, PREREG: preg}
    for f in SIDE:
        files[f] = blob(f)
    for rel, data in files.items():
        d = fx / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_bytes(data)
    git(fx, "add", "-A")
    assert git(fx, "-c", "user.name=v02", "-c", "user.email=v02@invalid",
               "commit", "-q", "-m", name).returncode == 0
    p = subprocess.run([sys.executable, CHECKER, "--repo", str(fx), "--tip", "HEAD"],
                       capture_output=True, text=True, env=env(), cwd=S, timeout=300)
    print(f"### {name}\nnote: {note}\nexit={p.returncode}\n{p.stdout}{p.stderr}")
    shutil.rmtree(fx, ignore_errors=True)
