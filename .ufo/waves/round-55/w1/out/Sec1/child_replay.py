import importlib.util, os, time
spec = importlib.util.spec_from_file_location(
    "replay", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-live-replay.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.set_own_pdeathsig()          # what the replay does on startup (replay:945)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "CHILD.PID"), "w").write(str(os.getpid()))
time.sleep(120)                # stands in for llama-server observation
