#!/usr/bin/env python3
"""Fake live tool: records argv and echoes the original receipt as the rerun."""
import json
import os
import sys

argv = sys.argv[1:]
dump = os.environ["FAKE_ARGV"]
with open(dump, "w") as fh:
    json.dump(argv, fh, indent=1)
rec = json.load(open(os.environ["FAKE_ORIG"]))
rec["schema"] = ("kama-llamacpp-live/v5" if "--server-archive" in argv
                 else "kama-llamacpp-live/v4")
out = argv[argv.index("--out") + 1]
with open(out, "w") as fh:
    json.dump(rec, fh)
sys.exit(0)
