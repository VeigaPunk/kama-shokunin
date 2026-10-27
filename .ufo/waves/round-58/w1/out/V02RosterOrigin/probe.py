#!/usr/bin/env python3
"""V02RosterOrigin probe: is `kills == 1 and controls == 2` a derived invariant or a
carried literal?  Build throwaway repos (git -C <fixture>) holding the round-56 prereg +
battery, apply single-anchor roster/call-site transforms, and score each with the
build-tip round-58 checker (tools/round58-battery-exec-check.py)."""
import json
import os
import pathlib
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


def blob(path, rev=TIP):
    p = git(LANE, "show", f"{rev}:{path}")
    assert p.returncode == 0, path
    return p.stdout


def once(text, old, new):
    assert text.count(old) == 1, (text.count(old), old)
    return text.replace(old, new)


BAT = blob(BATTERY).decode()
PREG = json.loads(blob(PREREG))


def synced(roster):
    p = json.loads(json.dumps(PREG))
    p["battery"]["roster"] = roster
    return json.dumps(p, indent=2).encode() + b"\n"


def roster(**kw):
    return {k: dict(v) for k, v in PREG["battery"]["roster"].items()}


SCEN = []


def add(name, bat, preg, note):
    SCEN.append((name, bat.encode(), preg, note))


# P0 genuine battery + genuine prereg: harness sanity.
add("P0-genuine", BAT, blob(PREREG), "control: unchanged committed pair")

# P1 two-sidedness erased: positive control given the same expected outcome as the red
# control (both expect `missed`); battery literal, call site and prereg all synced.
r = roster()
r["round56-counter"] = {"designation": "control", "expected": "missed"}
b = once(BAT, 'results.append(run("round56-counter", NEW, "detected"',
         'results.append(run("round56-counter", NEW, "missed"')
b = once(b, '"round56-counter": {"designation": "positive-control", "expected": "detected"}',
         '"round56-counter": {"designation": "control", "expected": "missed"}')
add("P1-both-controls-miss", b, synced(r), "controls=2 both expected missed (no must-detect side)")

# P2 positive-control role erased, expected outcomes keep their bracket.
r2 = roster()
r2["round56-counter"] = {"designation": "control", "expected": "detected"}
b2 = once(BAT, '"round56-counter": {"designation": "positive-control", "expected": "detected"}',
          '"round56-counter": {"designation": "control", "expected": "detected"}')
add("P2-role-erased", b2, synced(r2), "two plain controls, still one missed + one detected")

# P3 call-site expected arguments swapped, ROSTER literal and prereg untouched: a
# behaviour-changing battery (both legs assert the opposite of the declared expectation).
b3 = once(BAT, 'results.append(run("base-old-counter", OLD, "missed"',
          'results.append(run("base-old-counter", OLD, "detected"')
b3 = once(b3, 'results.append(run("round56-counter", NEW, "detected"',
          'results.append(run("round56-counter", NEW, "missed"')
add("P3-callsite-expect-swapped", b3, blob(PREREG),
    "roster literal intact, run() expected args inverted")

# P4 one control only (positive control removed from roster and from the calls).
r4 = roster()
del r4["round56-counter"]
b4 = once(BAT, '    results.append(run("round56-counter", NEW, "detected", OUT / "build-c1.out"))\n', "")
b4 = once(b4, '    "round56-counter": {"designation": "positive-control", "expected": "detected"},\n', "")
add("P4-one-control", b4, synced(r4), "controls=1 (constant should bite)")

# P5 no kill: the kill entry re-designated positive-control, prereg synced.
r5 = roster()
r5["m-drop-ldaudit"] = {"designation": "positive-control", "expected": "missed"}
b5 = once(BAT, '"m-drop-ldaudit": {"designation": "kill", "expected": "missed"}',
          '"m-drop-ldaudit": {"designation": "positive-control", "expected": "missed"}')
add("P5-no-kill", b5, synced(r5), "kills=0 controls=3 (constant should bite)")


def build(name, bat, preg):
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
    return fx


pathlib.Path(CHECKER).write_bytes(blob("tools/round58-battery-exec-check.py"))
out = []
for name, bat, preg, note in SCEN:
    fx = build(name, bat, preg)
    p = subprocess.run([sys.executable, CHECKER, "--repo", str(fx), "--tip", "HEAD"],
                       capture_output=True, text=True, env=env(), cwd=S, timeout=300)
    row = f"### {name}\nnote: {note}\nexit={p.returncode}\n{p.stdout}{p.stderr}"
    print(row)
    out.append((name, p.returncode, p.stdout))
    import shutil
    shutil.rmtree(fx, ignore_errors=True)
pathlib.Path(os.path.join(S, "probe.out")).write_text("\n".join(
    f"{n}\texit={rc}\t{q.strip().replace(chr(10), ' | ')}" for n, rc, q in out) + "\n")
