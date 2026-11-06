import importlib.util, os, pathlib, sys

RC = "/fast/scratch/hyaku/kama-r88/SN01FixtureSafety/counter.py"
spec = importlib.util.spec_from_file_location("rc", RC)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

work = pathlib.Path(sys.argv[1])
work.mkdir(parents=True, exist_ok=True)
probe = work / "kama-probe.sh"
probe.write_text("#!/bin/bash\nsleep 60\nexit 1\n")
env = dict(os.environ, TMPDIR=str(work))
print("HARNESS work=%s ready" % work, flush=True)
m.live_cells(probe, work, env)
print("HARNESS live_cells returned (unexpected)", flush=True)
