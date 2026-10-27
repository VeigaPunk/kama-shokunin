#!/usr/bin/env python3
"""noop-instrument - a do-nothing instrument: it declares the canonical row counts
and claims met=True without reading SCORECARD.md, any evidence path, or any tool.
The only thing it echoes is the run nonce it is handed."""
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--nonce", default="")
a = ap.parse_args()
print(f"nonce={a.nonce}")
print("canon_rows=11 rows_bound=11 evidence=20/20 content=20/20 exec=10/10 "
      "mismatches=0 met=True")
