#!/usr/bin/env python3
"""Stub auditor: exits 2 with an UNRELATED refusal reason (no traceback)."""
import sys
print("could-not-evaluate: git: rc=1 fatal: something totally unrelated",
      file=sys.stderr)
sys.exit(2)
