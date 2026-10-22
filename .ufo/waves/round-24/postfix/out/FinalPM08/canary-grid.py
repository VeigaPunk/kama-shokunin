#!/usr/bin/env python3
"""FinalPM08 private canary grid: records every invocation, then refuses."""
import os
import sys

log = os.environ["PM08_CANARY_LOG"]
with open(log, "a", encoding="utf-8") as fh:
    fh.write("CALLED " + " ".join(sys.argv) + "\n")
print("canary grid was invoked", file=sys.stderr)
sys.exit(2)
