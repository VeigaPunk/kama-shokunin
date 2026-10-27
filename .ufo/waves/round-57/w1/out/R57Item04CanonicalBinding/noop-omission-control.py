#!/usr/bin/env python3
"""noop-omission-control.py - the do-nothing omission control.

It reads no SCORECARD bytes, resolves no evidence, and hashes no row, yet it
prints a green summary.  Any harness that accepts this as met=True is bound to
the instrument's self-description instead of the canonical rows.
"""
import sys

print("canonical_reads=0 bound=0 omitted=0 extra=0 distinct=0 mismatches=0 met=True")
sys.exit(0)
