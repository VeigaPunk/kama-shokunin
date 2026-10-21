import sys
# crash: uncaught exception -> exit 1, empty stdout (no INVALID verdict)
raise RuntimeError("simulated gate crash")
