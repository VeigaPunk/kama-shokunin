import importlib.util, sys
spec = importlib.util.spec_from_file_location("cwb", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
cand = sys.argv[2]
for name in ["case_refused", "case_allpass", "case_waiver_ne", "case_waiver_fail", "case_unknown"]:
    checks, facts = getattr(m, name)(cand)
    state = "FAILED " + ";".join(checks.failed()) if checks.failed() else "held"
    print(f"{name}: {state} | {facts}")
