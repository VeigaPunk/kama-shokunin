#!/usr/bin/env python3
"""Force the live-tool window: child passes _child_running, exits before exe open/hold."""
import importlib.util, os, subprocess, tempfile, time
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
spec = importlib.util.spec_from_file_location("kama_live", LANE + "/tools/kama-llamacpp-live.py")
live = importlib.util.module_from_spec(spec); spec.loader.exec_module(live)
p = subprocess.Popen(["/bin/sleep", "30"])
try:
    print("initial _child_running:", live._child_running(p))
    p.terminate()
    time.sleep(0.1)  # leave the dead child unreaped, as between live-tool calls
    print("server_exe after child exit:", live.server_exe(p.pid))
    with tempfile.TemporaryDirectory(prefix="sen2race-witness-") as wd:
        try:
            live.hold_for_witness(wd, p, 18196, 1.0)
            print("witness hold unexpectedly returned")
        except live.SetupError as e:
            print("witness hold rejected:", str(e))
finally:
    p.wait()
