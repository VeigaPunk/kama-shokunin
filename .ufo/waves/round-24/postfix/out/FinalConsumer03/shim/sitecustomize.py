"""Non-mutating argv logger for the pristine replay-v3 driver run.

sitecustomize is injected via PYTHONPATH; the driver file itself is NOT
modified. Every subprocess.run argv is appended to $ARGV_LOG as JSON.
"""
import json
import os
import subprocess

_log = os.environ.get("ARGV_LOG")
if _log:
    _orig = subprocess.run

    def run(*a, **kw):
        try:
            cmd = a[0] if a else kw.get("args")
            with open(_log, "a", encoding="utf-8") as fh:
                fh.write(json.dumps([str(c) for c in cmd]) + "\n")
        except Exception:
            pass
        return _orig(*a, **kw)

    subprocess.run = run
