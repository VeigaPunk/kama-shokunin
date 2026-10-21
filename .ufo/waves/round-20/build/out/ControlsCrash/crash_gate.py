#!/usr/bin/env python3
"""ControlsCrash (kama round 20) crash-gate stub.

Raises at import: every invocation exits 1 with a Python traceback on stderr
and nothing on stdout. It never opens its receipt argument, so it can never
observe a verdict; any rejection credited to it is an error counted as a
verdict (honest class: could-not-evaluate).
"""
raise RuntimeError('crash-gate stub: raised at import; no receipt was read')
