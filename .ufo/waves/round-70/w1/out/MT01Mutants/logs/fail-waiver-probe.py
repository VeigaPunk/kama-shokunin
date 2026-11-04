#!/usr/bin/env python3
"""fail-waiver-probe.py - MT01Mutants detector D2e.

Loads a round65-host-census.py candidate, replaces MEMBERS with one member that RAN
and failed, passes `--waive <that member>` on the module's own argv, and reports the
exit code. A waiver must never cover a fail: expect exit 1.
"""
import contextlib
import importlib.util
import io
import sys

FAIL_FIXTURE = [("A", "synthetic-fail", ["bash", "-c", "echo boom; exit 1"], "NEVER-PRINTED", [])]


def load(path):
    spec = importlib.util.spec_from_file_location("census_failprobe", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    if len(sys.argv) < 2:
        print("usage: fail-waiver-probe.py <census.py>", file=sys.stderr)
        return 2
    path = sys.argv[1]
    mod = load(path)
    mod.MEMBERS = FAIL_FIXTURE
    sys.argv = [path, "--waive", "synthetic-fail"]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = mod.main()
    for line in buf.getvalue().strip().splitlines():
        print(f"  {line}")
    print(f"FAIL_WAIVER_PROBE fail_member_waived_exit={code}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
