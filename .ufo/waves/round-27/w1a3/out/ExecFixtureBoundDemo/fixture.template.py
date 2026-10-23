#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# MARKER-A3-FIXTURE-BOUND-DEMO  (line 2 of the two-line marker snippet)
#
# Deliberately runaway fixture, reproducing the round-27 mined mistake:
# a file whose MARKER points back at itself, appended to itself without bound.
# The real incident (attempt-2 seat ReviewA3Diff) grew sitecustomize.py to
# 262699483136 bytes of a repeated two-line MARKER snippet and filled /fast;
# copies are kept in .ufo/waves/round-27/a3/mistake-runaway/.
#
# This file only *appends its own bytes to itself* in a loop and records MiB
# crossings into a SEPARATE progress log named by $PROGRESS_LOG (the fix
# shape: MARKER/log never points at a file Python imports or at its own
# input).  Nothing here is imported by Python, so the fixture cannot be
# re-entered through sitecustomize.
#
# Env switches, both read before the loop and changing nothing inside it:
#   A3_SIG_DFL=1   restore the SIGXFSZ default action (terminate); used only
#                  because CPython/the launching shell may leave SIGXFSZ
#                  ignored, in which case the kernel turns the cap into
#                  OSError(EFBIG) instead of killing the writer.
#   A3_SWALLOW=1   catch OSError around the self-append and keep looping, to
#                  show whether the *file* stays bounded when the writer
#                  survives the cap.
# There is no handler around the write unless A3_SWALLOW=1 is set.
#
# Padding below is inert text, kept only so each loop iteration appends a few
# KiB and the run reaches a given cap in a bounded number of iterations.
# ---------------------------------------------------------------------------
PADDING = """
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
a3 fixture bound demo padding a3 fixture bound demo padding a3 fixture bound demo
"""
import os
import signal

_P = os.path.abspath(__file__)
_BLOB = open(_P, "rb").read()          # the file's own content
_LOG = os.environ["PROGRESS_LOG"]      # separate file: never imported, never the fixture
_SWALLOW = os.environ.get("A3_SWALLOW") == "1"

if os.environ.get("A3_SIG_DFL") == "1":
    signal.signal(signal.SIGXFSZ, signal.SIG_DFL)

with open(_LOG, "a") as lg:
    lg.write("start blob=%d pid=%d sigxfsz=%s swallow=%s\n"
             % (len(_BLOB), os.getpid(), signal.getsignal(signal.SIGXFSZ), _SWALLOW))

_LAST_MIB = 0
_ERRS = 0
while True:
    if _SWALLOW:
        try:
            with open(_P, "ab") as f:
                f.write(_BLOB)
        except OSError as e:
            _ERRS += 1
            if _ERRS <= 3 or _ERRS % 1000 == 0:
                with open(_LOG, "a") as lg:
                    lg.write("swallowed errno=%s count=%d size=%d\n"
                             % (e.errno, _ERRS, os.path.getsize(_P)))
    else:
        with open(_P, "ab") as f:      # self-append: the runaway
            f.write(_BLOB)
    n = os.path.getsize(_P)
    mib = n >> 20
    if mib > _LAST_MIB:
        _LAST_MIB = mib
        with open(_LOG, "a") as lg:
            lg.write("crossed mib=%d size=%d\n" % (mib, n))
