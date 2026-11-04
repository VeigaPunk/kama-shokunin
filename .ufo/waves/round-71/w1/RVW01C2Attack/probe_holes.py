#!/usr/bin/env python3
"""Probe each H-variant's hole observable with round-70 control mechanics
(module import + MEMBERS injection + argv/env waiver channels).

Prints, per variant and fixture, the exit code and the HOST_CENSUS verdict line.
"""
import contextlib
import importlib.util
import io
import os
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r71/RVW01C2Attack")

PASS_MARKER = "RESULT pass=30 fail=0"
REFUSAL_MARKER = "invalid path"
REFUSAL_REASON = "fail-closed refusal: synthetic NTFS stand-in (control)"

REFUSED = [
    ("A", "synthetic-pass", ["bash", "-c", f"echo {PASS_MARKER!r}"], PASS_MARKER, []),
    ("A", "synthetic-refused",
     ["bash", "-c", f"echo {REFUSAL_MARKER!r}: the lane holds a tracked path NTFS cannot check out"],
     "NEVER-PRINTED", [(REFUSAL_MARKER, REFUSAL_REASON)]),
]
ALLPASS = [
    ("A", "synthetic-pass", ["bash", "-c", f"echo {PASS_MARKER!r}"], PASS_MARKER, []),
    ("A", "synthetic-pass-2", ["bash", "-c", f"echo {PASS_MARKER!r}"], PASS_MARKER, []),
]
FAILING = [
    ("A", "synthetic-pass", ["bash", "-c", f"echo {PASS_MARKER!r}"], PASS_MARKER, []),
    ("A", "synthetic-broken", ["bash", "-c", "echo boom; exit 3"], "NEVER-PRINTED", []),
]


def load(path):
    spec = importlib.util.spec_from_file_location("census_probe", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def call(mod, members, argv=None):
    mod.MEMBERS = members
    buf, err = io.StringIO(), io.StringIO()
    saved = sys.argv
    if argv is not None:
        sys.argv = argv
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            code = mod.main()
    finally:
        sys.argv = saved
    lines = buf.getvalue().strip().splitlines()
    verdict = [l for l in lines if l.startswith("HOST_CENSUS ")]
    return code, (verdict[-1] if verdict else "<no verdict line>")


def show(tag, code, v):
    print(f"{tag:58} exit={code} {v}")


def main():
    for name in ["H1-waiver-covers-pass", "H2-forged-waived-token",
                 "H3-second-call-silent", "H4-phantom-not-evaluated"]:
        path = S / "shims" / f"{name}.py"
        print(f"--- {name} ---")
        # the hole observables
        m = load(path)
        c, v = call(load(path), ALLPASS, argv=["census", "--waive", "synthetic-pass"])
        show(f"ALLPASS + waive synthetic-pass (passing member)", c, v)
        c, v = call(load(path), REFUSED, argv=["census", "--waive", "no-such-member"])
        show("REFUSED + waive no-such-member (unknown)", c, v)
        # invariants the boundary cares about
        c, v = call(load(path), REFUSED)
        show("REFUSED no waiver", c, v)
        c, v = call(load(path), ALLPASS)
        show("ALLPASS no waiver", c, v)
        c, v = call(load(path), FAILING)
        show("FAILING no waiver", c, v)
        c, v = call(load(path), FAILING, argv=["census", "--waive", "synthetic-broken"])
        show("FAILING + waive synthetic-broken", c, v)
        c, v = call(load(path), REFUSED, argv=["census", "--waive", "synthetic-refused"])
        show("REFUSED + waive synthetic-refused", c, v)
        c, v = call(load(path), REFUSED, argv=["census", "--waive", "synthetic"])
        show("REFUSED + waive prefix 'synthetic'", c, v)
        if name == "H3-second-call-silent":
            m = load(path)  # ONE module object, two calls
            c1, v1 = call(m, FAILING, argv=["census", "--waive", "synthetic-broken"])
            c2, v2 = call(m, FAILING, argv=["census", "--waive", "synthetic-broken"])
            show("FAILING+waive call#1 (same module obj)", c1, v1)
            show("FAILING+waive call#2 (same module obj)", c2, v2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
