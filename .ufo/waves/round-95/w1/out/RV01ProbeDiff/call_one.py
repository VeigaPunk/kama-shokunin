import sys, time, traceback
src = open("/fast/scratch/hyaku/kama-r95/RV01ProbeDiff/new-router-inst.py").read()
g = {"__name__": "routerinst"}
exec(compile(src, "routerinst", "exec"), g)
path = sys.argv[1]
t0 = time.monotonic()
try:
    st = g["gguf_parse"](path)
except Exception:
    st = "EXC"; traceback.print_exc()
dt = time.monotonic() - t0
steps = g["STEPS_LAST"][-1][0] if g["STEPS_LAST"] else -1
print(f"{path}\tstate={st}\tsteps={steps}\twall={dt:.3f}s")
