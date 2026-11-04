#!/usr/bin/env python3
"""refused-member-control.py - round-70 C2's cheapest do-nothing control.

Loads a given `round65-host-census.py` as a module, replaces its MEMBERS with two
synthetic members, and runs its `main()` twice:

  refused fixture   one member emits a registered refusal marker (`invalid path`),
                    the other passes
  all-pass fixture  both members pass

Prints `REFUSED_MEMBER_CONTROL refused_fixture_exit=<n> allpass_fixture_exit=<n>` and exits 1
unless the refused fixture exits nonzero and the all-pass fixture exits 0. That pair is the
frozen counter: a census whose exit is derived from `failed` alone scores (0, 0) — a member
that never ran reads as a pass.

Usage: python3 refused-member-control.py <path-to-round65-host-census.py>

Read-only on the given file; the module's own scratch dirs are created and removed by its
`main()`. Never imports git state, never writes outside the module's temp dirs.
"""
import contextlib
import importlib.util
import io
import json
import os
import sys

PASS_MARKER = "RESULT pass=30 fail=0"
REFUSAL_MARKER = "invalid path"
REFUSAL_REASON = "fail-closed refusal: synthetic NTFS stand-in (control)"

REFUSED_FIXTURE = [
    ("A", "synthetic-pass", ["bash", "-c", f"echo {PASS_MARKER!r}"], PASS_MARKER, []),
    ("A", "synthetic-refused",
     ["bash", "-c", f"echo {REFUSAL_MARKER!r}: the lane holds a tracked path NTFS cannot check out"],
     "NEVER-PRINTED",  [(REFUSAL_MARKER, REFUSAL_REASON)]),
]
ALLPASS_FIXTURE = [
    ("A", "synthetic-pass", ["bash", "-c", f"echo {PASS_MARKER!r}"], PASS_MARKER, []),
    ("A", "synthetic-pass-2", ["bash", "-c", f"echo {PASS_MARKER!r}"], PASS_MARKER, []),
]


def load(path):
    spec = importlib.util.spec_from_file_location("census_under_control", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(mod, members):
    mod.MEMBERS = members
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = mod.main()
    return code, buf.getvalue().strip().splitlines()


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        print("usage: refused-member-control.py <path-to-round65-host-census.py>", file=sys.stderr)
        return 2
    path = os.path.abspath(sys.argv[1])
    if not os.path.isfile(path):
        print(f"could-not-evaluate: not a file: {path}", file=sys.stderr)
        return 2
    try:
        refused_exit, refused_lines = run(load(path), REFUSED_FIXTURE)
        allpass_exit, allpass_lines = run(load(path), ALLPASS_FIXTURE)
    except Exception as exc:  # a control that cannot run proves nothing
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"refused_fixture": refused_lines, "allpass_fixture": allpass_lines}))
    print(f"REFUSED_MEMBER_CONTROL refused_fixture_exit={refused_exit} "
          f"allpass_fixture_exit={allpass_exit}")
    return 0 if (refused_exit != 0 and allpass_exit == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
