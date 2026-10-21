import os, sys
# Fake gate for error-injection: baseline VALID; every mutant crashes with an
# uncaught exception (exit 1, traceback, no INVALID line, empty stdout).
if os.path.basename(sys.argv[1]) == "baseline.json":
    print("VALID")
    sys.exit(0)
raise RuntimeError("simulated crash: no verdict emitted")
