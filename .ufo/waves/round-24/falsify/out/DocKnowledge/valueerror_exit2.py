#!/usr/bin/env python3
"""Stub auditor: exits 2 with the catch-all's generic internal ValueError text."""
import sys
print("could-not-evaluate: internal: ValueError: totally unrelated bug",
      file=sys.stderr)
sys.exit(2)
