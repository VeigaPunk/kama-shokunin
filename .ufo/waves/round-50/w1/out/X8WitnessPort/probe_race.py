#!/usr/bin/env python3
"""X8WitnessPort deterministic probe of the witness-dir handshake logic.

Loads the frozen lane tool as a module (read-only; nothing is edited) and drives
prepare_witness_dir / hold_for_witness with stub server children, so the
interleavings that need two runs in one directory can be made deterministic
without the network or a real server.

case1  another run's prepare removes this run's announcement, and this run's
       hold end removes the other run's announcement (cross-run deletion)
case2  an interleaved prepare between the temp-file create and its os.replace
       turns the announce into an uncaught FileNotFoundError (simulated
       interleaving of exactly the frozen code paths)
case3  one release file ends every hold in the directory
"""
import importlib.util
import json
import os
import re
import shutil
import sys
import threading
import time

TOOL = "/fast/scratch/hyaku/kama-r50/X8WitnessPort/lane/tools/kama-llamacpp-live.py"
S = "/fast/scratch/hyaku/kama-r50/X8WitnessPort"
OUT = ("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/"
       "w1/out/X8WitnessPort")

spec = importlib.util.spec_from_file_location("klive", TOOL)
klive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(klive)


class Stub:
    """A live child that never exits: poll() None, a chosen pid for the tmp name."""

    def __init__(self, pid):
        self.pid = pid

    def poll(self):
        return None


def fresh(name):
    w = os.path.join(S, "race", name)
    shutil.rmtree(w, ignore_errors=True)
    os.makedirs(w)
    return w


def listing(w):
    return sorted(os.listdir(w))


def ready_pid(w):
    try:
        with open(os.path.join(w, "ready.json")) as fh:
            return json.load(fh).get("pid")
    except (OSError, ValueError):
        return None


def wait_for(pred, timeout=5.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        v = pred()
        if v:
            return v
        time.sleep(0.002)
    return None


def code_lines():
    src = open(TOOL).read().splitlines()
    out = {}
    for pat, key in ((r"^def prepare_witness_dir", "prepare"),
                     (r"^def hold_for_witness", "hold"),
                     (r"os\.replace\(tmp, ready_path\)", "replace"),
                     (r"for path in \(ready_path, tmp\)", "finally_unlink"),
                     (r"not os\.path\.exists\(release\)", "release_test")):
        for i, ln in enumerate(src, 1):
            if re.search(pat, ln):
                out[key] = i
    return out


def case1(results):
    w = fresh("case1")
    p1, p2 = 999001, 999002
    rec = {"dir": w, "pids": [p1, p2]}
    a = {}
    ta = threading.Thread(target=lambda: a.update(r=klive.hold_for_witness(
        w, Stub(p1), 41001, 2.0)), daemon=True)
    ta.start()
    rec["a_announced_pid"] = wait_for(lambda: ready_pid(w))
    rec["a_ready_listing"] = listing(w)
    # a second run's parse-time prepare (kama-llamacpp-live.py main, before any server)
    klive.prepare_witness_dir(w)
    rec["listing_after_other_prepare"] = listing(w)
    rec["other_prepare_removed_first_announcement"] = (
        rec["a_announced_pid"] == p1 and listing(w) == [])
    b = {}
    tb = threading.Thread(target=lambda: b.update(r=klive.hold_for_witness(
        w, Stub(p2), 41002, 8.0)), daemon=True)
    tb.start()
    rec["b_announced_pid"] = wait_for(lambda: ready_pid(w) == p2)
    rec["b_ready_listing"] = listing(w)
    ta.join(timeout=10)
    rec["a_returned"] = a.get("r")
    # A's hold end must not remove B's announcement
    rec["listing_at_a_end"] = listing(w)
    rec["b_still_held_at_a_end"] = tb.is_alive()
    rec["a_end_removed_b_announcement"] = (tb.is_alive()
                                           and "ready.json" not in listing(w))
    open(os.path.join(w, "release"), "w").close()
    tb.join(timeout=15)
    rec["b_returned"] = b.get("r")
    rec["listing_after_b_end"] = listing(w)
    results["case1"] = rec


def case2(results):
    w = fresh("case2")
    p3 = 999003
    rec = {"dir": w, "pid": p3}
    real_replace = os.replace
    injected = []

    def wrapper(src, dst):
        rec.setdefault("os_replace", []).append(
            {"src": os.path.basename(src), "dst": os.path.basename(dst)})
        if os.path.basename(dst) == "ready.json" and not injected:
            injected.append(True)
            # exactly what a second run does at parse time, in this microsecond
            klive.prepare_witness_dir(w)
        return real_replace(src, dst)

    os.replace = wrapper
    try:
        try:
            r = klive.hold_for_witness(w, Stub(p3), 41003, 5.0)
            rec["returned"] = r
            rec["raised"] = None
        except BaseException as exc:  # noqa: BLE001
            rec["raised"] = {"type": type(exc).__name__, "str": str(exc)[:200]}
            rec["raised"] = rec["raised"]
    finally:
        os.replace = real_replace
    rec["injected"] = bool(injected)
    rec["listing_after"] = listing(w)
    results["case2"] = rec


def case3(results):
    w = fresh("case3")
    p5, p6 = 999005, 999006
    klive.prepare_witness_dir(w)
    rec = {"dir": w, "pids": [p5, p6]}
    a, b = {}, {}
    ta = threading.Thread(target=lambda: a.update(r=klive.hold_for_witness(
        w, Stub(p5), 41005, 6.0)), daemon=True)
    tb = threading.Thread(target=lambda: b.update(r=klive.hold_for_witness(
        w, Stub(p6), 41006, 6.0)), daemon=True)
    ta.start()
    wait_for(lambda: ready_pid(w) is not None)
    time.sleep(0.2)
    tb.start()
    time.sleep(0.5)
    rec["announce_at_release"] = ready_pid(w)
    rec["listing_at_release"] = listing(w)
    open(os.path.join(w, "release"), "w").close()
    ta.join(timeout=15)
    tb.join(timeout=15)
    rec["a"] = a.get("r")
    rec["b"] = b.get("r")
    rec["one_release_ended_both"] = bool(
        a.get("r") and b.get("r") and a["r"].get("released")
        and b["r"].get("released"))
    rec["listing_after"] = listing(w)
    results["case3"] = rec


def main():
    results = {"tool": TOOL, "lines": code_lines()}
    case1(results)
    case2(results)
    case3(results)
    dest = os.path.join(OUT, "results", "race.json")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as fh:
        json.dump(results, fh, indent=1)
    print(json.dumps(results, indent=1))
    print("wrote", dest)


if __name__ == "__main__":
    main()
