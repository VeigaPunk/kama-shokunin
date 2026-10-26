"""Sen1Witness: unit-level host-safety probes of hold_for_witness + parser bounds.

Imports the frozen lane tool by path (no server, no network). Each case prints
one line: CASE<TAB>result.
"""
import importlib.util
import json
import os
import subprocess
import sys
import time
import signal

TOOL = "/fast/scratch/hyaku/kama-r49/Sen1Witness/lane/tools/kama-llamacpp-live.py"
spec = importlib.util.spec_from_file_location("klive", TOOL)
klive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(klive)

S = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(S, "unit")


def fresh(name):
    d = os.path.join(BASE, name)
    subprocess.run(["rm", "-rf", d], check=True)
    os.makedirs(d)
    return d


def child():
    # stand-in for the llama-server child: hold_for_witness only polls it
    return subprocess.Popen(["sleep", "120"])


def case(name, wdir, timeout, setup=None):
    c = child()
    try:
        if setup:
            setup(wdir)
        t0 = time.monotonic()
        r = klive.hold_for_witness(wdir, c, 12345, timeout)
        dt = round((time.monotonic() - t0) * 1000)
        extra = ""
        rp = os.path.join(wdir, "ready.json")
        if os.path.islink(rp):
            extra += f" ready_is_symlink->{os.readlink(rp)}"
        if os.path.exists(rp):
            try:
                st = os.stat(rp)
                extra += f" ready_mode={oct(st.st_mode & 0o777)}"
            except OSError as e:
                extra += f" stat_err={e}"
        print(f"{name}\treleased={r['released']} waited_ms={r['waited_ms']} actual_ms={dt}{extra}")
        return r
    finally:
        c.kill()
        c.wait()


os.makedirs(BASE, exist_ok=True)

# 1. plain hold, timeout reached with no release
r = case("t1-no-release-timeout", fresh("t1"), 0.5)

# 2. pre-existing release file (stale from an earlier run / attacker)
case("t2-preexisting-release", fresh("t2"), 30,
     setup=lambda d: open(os.path.join(d, "release"), "w").write("stale\n"))

# 3. release is a *directory*: exists() is True, no observer action
case("t3-release-is-dir", fresh("t3"), 30,
     setup=lambda d: os.makedirs(os.path.join(d, "release")))

# 4. release is a dangling symlink: exists() False -> held to the timeout
case("t4-release-dangling-symlink", fresh("t4"), 0.5,
     setup=lambda d: os.symlink("/nonexistent/x", os.path.join(d, "release")))

# 5. stale ready.json from an earlier run is overwritten (freshness check)
def stale_ready(d):
    json.dump({"schema": "kama-live-witness/v1", "port": 1, "pid": 1},
              open(os.path.join(d, "ready.json"), "w"))
case("t5-stale-ready-overwritten", fresh("t5"), 0.3, setup=stale_ready)

# 6. ready.json.tmp pre-created as a symlink to an outside file
victim = os.path.join(BASE, "victim.txt")
open(victim, "w").write("OPERATOR DATA THAT MUST SURVIVE\n")
d6 = fresh("t6")


def symlink_tmp(d):
    os.symlink(victim, os.path.join(d, "ready.json.tmp"))


case("t6-tmp-symlink", d6, 0.3, setup=symlink_tmp)
print(f"t6-victim-file\tcontent={open(victim, 'rb').read()[:60]!r}")

# 7. ready.json pre-created as a symlink to an outside file
victim2 = os.path.join(BASE, "victim2.txt")
open(victim2, "w").write("SECOND OPERATOR FILE\n")
d7 = fresh("t7")
case("t7-ready-symlink", d7, 0.3,
     setup=lambda d: os.symlink(victim2, os.path.join(d, "ready.json")))
print(f"t7-victim2-file\tcontent={open(victim2, 'rb').read()[:60]!r}")

# 8. witness dir is not writable
d8 = fresh("t8")
os.chmod(d8, 0o500)
try:
    c = child()
    try:
        r = klive.hold_for_witness(d8, c, 12345, 0.3)
        print(f"t8-unwritable-dir\tno raise, released={r['released']}")
    except Exception as e:
        print(f"t8-unwritable-dir\traised {type(e).__name__}: {e}")
    finally:
        c.kill(); c.wait()
finally:
    os.chmod(d8, 0o700)

# 9. witness dir replaced by a file / removed between check and hold
d9 = fresh("t9")
c = child()
try:
    subprocess.run(["rm", "-rf", d9])
    r = klive.hold_for_witness(d9, c, 12345, 0.3)
    print(f"t9-dir-vanished\tcreated_dir={os.path.isdir(d9)} ready={os.path.exists(os.path.join(d9, 'ready.json'))}")
except Exception as e:
    print(f"t9-dir-vanished\traised {type(e).__name__}: {e}")
finally:
    c.kill(); c.wait()

# 10. child dies during the hold
d10 = fresh("t10")
c = subprocess.Popen(["sleep", "0.10"])
t0 = time.monotonic()
r = klive.hold_for_witness(d10, c, 12345, 30)
print(f"t10-child-dies\treleased={r['released']} waited_ms={r['waited_ms']} "
      f"actual_ms={round((time.monotonic()-t0)*1000)}")
c.wait()

# 11. parser bounds: inf / nan / huge / negative
p = klive.build_parser()
for val in ("inf", "nan", "1e12", "-1", "0"):
    try:
        a = p.parse_args(["--model", "m", "--model-sha256", "0" * 64,
                          "--witness-dir", BASE, "--witness-timeout", val])
        ok = a.witness_timeout > 0
        print(f"t11-parser-{val}\tparsed witness_timeout={a.witness_timeout!r} gt0={ok}")
    except SystemExit as e:
        print(f"t11-parser-{val}\trejected SystemExit({e.code})")

# 12. hold loop with an infinite timeout must not be reachable from the parser above;
#     demonstrate the loop itself ignores the deadline when timeout is inf
d12 = fresh("t12")
c = child()
t0 = time.monotonic()
def stop_later():
    time.sleep(0.4)
    open(os.path.join(d12, "release"), "w").write("x")
import threading
threading.Thread(target=stop_later, daemon=True).start()
r = klive.hold_for_witness(d12, c, 12345, float("inf"))
print(f"t12-inf-timeout\treleased={r['released']} waited_ms={r['waited_ms']} (released only by the external thread)")
c.kill(); c.wait()
