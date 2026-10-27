#!/usr/bin/env python3
"""Exercise a selected replay counter's env_leg against a live child carrying LD_AUDIT.
The child uses the non-audit DSO already observed refused by this glibc; the variable
name remains present in /proc/<pid>/environ and must be rejected by the new BAD_ENV."""
import argparse
import importlib.util
import os
import subprocess
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True)
    ap.add_argument("--expect", choices=("detected", "missed"), required=True)
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("round_counter", a.counter)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    env = dict(os.environ, LD_AUDIT="/usr/lib/libexpat.so.1")
    p = subprocess.Popen(["sleep", "5"], env=env)
    try:
        time.sleep(0.05)
        probs = []
        keys = mod.env_leg(p.pid, probs)
        detected = keys is not None and "env: server environment carries LD_AUDIT" in probs
        result = "detected" if detected else "missed"
        print(f"ld_audit={result} pid={p.pid} problems={probs}")
        return 0 if result == a.expect else 1
    finally:
        p.terminate()
        p.wait()


if __name__ == "__main__":
    raise SystemExit(main())
