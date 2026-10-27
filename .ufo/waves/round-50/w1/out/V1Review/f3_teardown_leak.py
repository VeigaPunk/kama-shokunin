#!/usr/bin/env python3
"""V1Review fixture F3: teardown_leg with a replay that announces a pid it does NOT
own (R1-style decoy). Shows the leg fails closed (correct) but the counter leaves the
announced process alive - only snapshotted descendants are reaped (lines 505-526).
The fake replay sets its own PR_SET_PDEATHSIG like the real replay, so the loop ends
fast. The fixture kills the decoy itself afterwards."""
import importlib.util, os, sys, json, socket, subprocess, time

S = "/fast/scratch/hyaku/kama-r50/V1Review/f3"
os.makedirs(S, exist_ok=True)
os.environ["TMPDIR"] = S
spec = importlib.util.spec_from_file_location(
    "c1", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-replay-bind-audit.py")
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)

tree = os.path.join(S, "faketree")
os.makedirs(os.path.join(tree, "tools"), exist_ok=True)
open(os.path.join(tree, "tools", "kama-live-replay.py"), "w").write(
    "import json, sys, time, os, ctypes, signal\n"
    "libc = ctypes.CDLL(None)\n"
    "libc.prctl(1, signal.SIGTERM)  # PR_SET_PDEATHSIG, faithful to the real replay\n"
    "wd = sys.argv[sys.argv.index('--witness-dir') + 1]\n"
    "cfg = json.load(open(os.path.join(os.path.dirname(wd), 'decoy.json')))\n"
    "json.dump({'pid': cfg['pid'], 'port': cfg['port']}, open(os.path.join(wd, 'ready.json'), 'w'))\n"
    "time.sleep(120)\n")
Sfake = os.path.join(S, "fakeS"); os.makedirs(Sfake, exist_ok=True)
decoy = subprocess.Popen(["sleep", "300"])  # announced-but-unowned process
sk = socket.socket(); sk.bind(("127.0.0.1", 0)); port = sk.getsockname()[1]; sk.close()
json.dump({"pid": decoy.pid, "port": port}, open(os.path.join(Sfake, "decoy.json"), "w"))
try:
    detail = []
    t0 = time.time()
    ok = c1.teardown_leg(tree, "unused-receipt", Sfake, detail)
    print("teardown_leg returned %s in %.1f s" % (ok, time.time() - t0))
    for d in detail:
        print("  detail:", d)
    time.sleep(0.5)
    print("decoy pid %d alive AFTER counter finished: %s  <- LEAK if True"
          % (decoy.pid, decoy.poll() is None))
    rp = subprocess.run(["pgrep", "-f", "faketree/tools/kama-live-replay.py"], capture_output=True)
    print("fake replay leftovers (snapshotted, reaped by counter):", rp.stdout.decode().split())
finally:
    decoy.kill(); decoy.wait()
    print("decoy killed by fixture cleanup, rc:", decoy.poll())
print("F3 DONE")
