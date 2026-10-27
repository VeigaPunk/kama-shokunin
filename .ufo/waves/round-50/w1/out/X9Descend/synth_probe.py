#!/usr/bin/env python3
"""Synthetic probes of the frozen C1 counter's descendant walk: descendants(),
replay_pid(), descends_from(), pid_alive(), and the teardown snapshot/check model.
The counter copy is byte-identical to the lane file; only its functions are called.
No network, no llama-server: the replay/live tool/server are stand-ins with the same
process shape and the same PR_SET_PDEATHSIG cascade."""
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time

S = sys.argv[1]
spec = importlib.util.spec_from_file_location("c1", os.path.join(S, "counter_copy.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
HERE = os.path.dirname(os.path.abspath(__file__))
SHIM, TOOL, DEEP = (os.path.join(HERE, n) for n in ("shim.py", "spawn_child.py", "deep.py"))
NOISY = ("import subprocess, sys\n"
         "bg = subprocess.Popen(['sleep', '300'])\n"
         "sys.exit(subprocess.call(sys.argv[1:]))\n")
RUN = os.path.join(S, f"run-{os.getpid()}")
os.makedirs(RUN, exist_ok=True)
results, jury = [], []


def check(case, name, cond, detail):
    results.append({"case": case, "check": name, "pass": bool(cond), "detail": detail})
    print(f"{'PASS' if cond else 'FAIL'} {case} {name}: {detail}")


def st(pid):
    return mod.stat_fields(pid)


def direct(pid):
    return sorted(p for p in mod.descendants(pid) if (st(p) or (None, None))[1] == pid)


def start(child_argv, tag, noisy=False, code=None):
    inv = code if code is not None else (NOISY if noisy else mod.INVOKER)
    argv = [sys.executable, "-I", "-c", inv] + child_argv
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": S, "TMPDIR": S}
    log = open(os.path.join(RUN, f"{tag}.log"), "wb")
    p = subprocess.Popen(argv, env=env, cwd=S, stdout=log, stderr=log, start_new_session=True)
    return p, log


def pgid_kill(p):
    for pid, _s in mod.descendants(p.pid).items():
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except OSError:
        pass
    if p.poll() is None:
        p.wait()


def wait_file(path, timeout=20):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        try:
            with open(path) as fh:
                txt = fh.read().split()
            if txt:
                return int(txt[0])
        except OSError:
            pass
        time.sleep(0.05)
    raise SystemExit(f"timeout waiting for {path}")


def chain(tag, noisy=False):
    d = os.path.join(RUN, tag)
    os.makedirs(d, exist_ok=True)
    p, log = start([sys.executable, "-I", SHIM, "chain", d], tag, noisy=noisy)
    srv = wait_file(os.path.join(d, "server.pid"))
    return p, log, d, srv


def dead(pid, start_t=None, timeout=10.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        if not mod.pid_alive(pid, start_t):
            return True
        time.sleep(0.05)
    return False


# ---------------------------------------------------------------- decoy: unrelated
decoy = subprocess.Popen(["sleep", "600"])
print(f"probe pid {os.getpid()} decoy (unrelated counter-side child) pid {decoy.pid}")

# ---------------------------------------------------------------- A control tree
p, log, d, srv = chain("A")
inv = p.pid
kids = direct(inv)
shim = kids[0] if kids else None
tool = wait_file(os.path.join(d, "tool.pid"))
snap = mod.descendants(inv)
check("A", "descendants-covers-3-levels", set(snap) == {shim, tool, srv},
      f"root invoker {inv}: snapshot {sorted(snap)} shim {shim} tool {tool} server {srv}")
check("A", "replay_pid-single-child", mod.replay_pid(p) == shim,
      f"direct children {kids} -> replay_pid {mod.replay_pid(p)}")
check("A", "descends_from-grandchild", mod.descends_from(tool, shim) is True,
      f"tool {tool} ppid {st(tool)[1]} == replay {shim}")
check("A", "descends_from-great-grandchild-to-invoker", mod.descends_from(srv, inv) is True,
      f"server {srv} -> {st(srv)[1]} -> {shim} -> {inv}")
check("A", "snapshot-excludes-root-and-counter-side", inv not in snap and os.getpid() not in snap
      and decoy.pid not in snap,
      f"root {inv} in snap {inv in snap}; probe {os.getpid()} in snap {os.getpid() in snap}; "
      f"decoy {decoy.pid} in snap {decoy.pid in snap}")
check("A", "snapshot-excludes-probes-own-descendants",
      not (set(snap) & ({decoy.pid} | {os.getpid()})),
      f"snapshot ∩ {{probe, decoy}} = {sorted(set(snap) & {os.getpid(), decoy.pid})}")
snap_starts = dict(snap)
os.kill(inv, signal.SIGKILL)
p.wait()
t0 = time.monotonic()
while time.monotonic() - t0 < 10 and any(mod.pid_alive(pid, s) for pid, s in snap_starts.items()):
    time.sleep(0.05)
alive = [pid for pid, s in snap_starts.items() if mod.pid_alive(pid, s)]
check("A", "teardown-cascade-empties-snapshot", alive == [],
      f"alive {alive} after SIGKILL of invoker, settled in {time.monotonic() - t0:.2f} s")
mod.reap(p, snap_starts.items())
log.close()

# ---------------------------------------------------------------- B noisy invoker
p, log, d, srv = chain("B", noisy=True)
inv = p.pid
kids = direct(inv)
rp = mod.replay_pid(p)
server = srv
prob = f"server pid {server} does not descend from the replay process {rp}"
check("B", "extra-invoker-child-breaks-replay_pid", rp is None and len(kids) == 2,
      f"invoker {inv} direct children {kids} -> replay_pid {rp}; bind leg would append {prob!r}")
check("B", "noisy-invoker-bind-leg-false-negative",
      bool(rp is None or not mod.descends_from(server, rp)) and (server in mod.descendants(inv)),
      f"counter expression (replay_pid {rp}) -> problem; the server {server} is in the invoker subtree")
pgid_kill(p)
log.close()

# ---------------------------------------------------------------- C ppid gap (reparent)
d = os.path.join(RUN, "C")
os.makedirs(d, exist_ok=True)
p, log = start([sys.executable, "-I", SHIM, "detach", d], "C")
inv = p.pid
esc = wait_file(os.path.join(d, "escaped.pid"))
time.sleep(0.4)
esc_ppid = st(esc)[1]
snap = mod.descendants(inv)
check("C", "escaped-reparented-out-of-subtree", esc not in snap and esc_ppid != inv,
      f"escaped {esc} ppid {esc_ppid}; snapshot of invoker {inv} = {sorted(snap)}")
check("C", "descends_from-false-across-gap", mod.descends_from(esc, inv) is False,
      f"descends_from({esc}, {inv}) = {mod.descends_from(esc, inv)} (the intermediate that "
      f"setsid'd and exited is gone from the chain)")
snap_starts = dict(snap)
os.kill(inv, signal.SIGKILL)
p.wait()
dead_all = all(dead(pid, s, 5.0) for pid, s in snap_starts.items())
alive = [pid for pid, s in snap_starts.items() if mod.pid_alive(pid, s)]
check("C", "teardown-check-passes-while-escaped-descendant-lives",
      dead_all and alive == [] and mod.pid_alive(esc),
      f"snapshot alive {alive}; escaped descendant {esc} alive {mod.pid_alive(esc)} -> "
      f"ok = not alive and refused would be True")
mod.reap(p, snap_starts.items())
try:
    os.kill(esc, signal.SIGKILL)
except OSError:
    pass
time.sleep(0.2)
check("C", "cleanup-escaped", not mod.pid_alive(esc), f"escaped {esc} alive {mod.pid_alive(esc)}")
log.close()

# ---------------------------------------------------------------- D post-snapshot child
p, log, d, srv = chain("D")
inv = p.pid
shim = direct(inv)[0]
snap = mod.descendants(inv)
os.kill(shim, signal.SIGUSR1)
late = wait_file(os.path.join(d, "late.pid"))
check("D", "late-child-absent-from-snapshot", late not in snap and st(late)[1] == shim,
      f"late child {late} ppid {shim}; snapshot taken before it existed {sorted(snap)}")
snap_starts = dict(snap)
os.kill(inv, signal.SIGKILL)
p.wait()
t0 = time.monotonic()
while time.monotonic() - t0 < 10 and any(mod.pid_alive(pid, s) for pid, s in snap_starts.items()):
    time.sleep(0.05)
alive = [pid for pid, s in snap_starts.items() if mod.pid_alive(pid, s)]
check("D", "late-child-survives-snapshot-only-check", alive == [] and mod.pid_alive(late),
      f"snapshot alive {alive} after {time.monotonic() - t0:.2f} s; late descendant {late} "
      f"alive {mod.pid_alive(late)}")
mod.reap(p, snap_starts.items())
try:
    os.kill(late, signal.SIGKILL)
except OSError:
    pass
log.close()

# ---------------------------------------------------------------- E zombies
zcode = ("import os, time\n"
         "z = os.fork()\n"
         "if z == 0:\n    os._exit(0)\n"
         "live = os.fork()\n"
         "if live == 0:\n    time.sleep(30)\n"
         "time.sleep(30)\n")
p, log = start([], "E", code=zcode)
time.sleep(0.6)
zs = [pid for pid in os.listdir("/proc") if pid.isdigit()
      and (st(int(pid)) or (None, None, 0))[1] == p.pid
      and (st(int(pid)) or (None,))[0] == "Z"]
kids = direct(p.pid)
check("E", "zombie-child-not-counted", zs and len(kids) == 1,
      f"zombie children of {p.pid}: {zs}; descendants/direct live children {kids} "
      f"-> replay_pid {mod.replay_pid(p)}")
check("E", "pid_alive-zombie-false", all(mod.pid_alive(z) is False for z in zs),
      f"pid_alive({zs}) = {[mod.pid_alive(z) for z in zs]}")
pgid_kill(p)
log.close()
z2 = ("import os, time\nz = os.fork()\nif z == 0:\n    os._exit(0)\ntime.sleep(20)\n")
p, log = start([], "E2", code=z2)
time.sleep(0.6)
check("E2", "only-zombie-child-means-no-replay-pid", mod.replay_pid(p) is None,
      f"invoker {p.pid} direct live children {direct(p.pid)} -> replay_pid None")
pgid_kill(p)
log.close()

# ---------------------------------------------------------------- F depth cap
p, log = start([sys.executable, "-I", DEEP, "70"], "F")
time.sleep(1.5)
snap = mod.descendants(p.pid)
depth = {}
for pid in snap:
    d_, seen = 0, pid
    while st(seen) and st(seen)[1] in snap:
        seen, d_ = st(seen)[1], d_ + 1
    depth[pid] = d_
leaf = max(depth, key=lambda k: depth[k]) if depth else None
check("F", "descendants-finds-70-hop-chain", len(snap) == 71,
      f"invoker {p.pid}: descendants {len(snap)} processes, deepest {leaf} at {depth.get(leaf)} hops")
check("F", "descends_from-caps-at-64-hops", leaf is not None and mod.descends_from(leaf, p.pid) is False,
      f"descends_from(leaf {leaf}, invoker {p.pid}) = {mod.descends_from(leaf, p.pid)} while the "
      f"leaf is in descendants() -> the 64-hop cap disagrees with the BFS")
pgid_kill(p)
log.close()

decoy.kill()
decoy.wait()
bad = [r for r in results if not r["pass"]]
print(f"summary: {len(results) - len(bad)}/{len(results)} checks as predicted")
with open(os.path.join(S, "synth-results.json"), "w") as fh:
    json.dump(results, fh, indent=1)
sys.exit(0 if not bad else 1)
