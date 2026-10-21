import sys,json
# baseline (file named baseline.json) -> VALID exit 0; mutants -> mode from env
import os
if sys.argv[1].endswith("baseline.json"): print("VALID"); sys.exit(0)
mode=os.environ["MODE"]
if mode=="crash": raise RuntimeError("mutant crash")
if mode=="ne": print("NOT-EVALUATED"); sys.exit(3)
if mode=="silent1": sys.exit(1)
if mode=="invalid": print("INVALID fake: 1 problem(s)"); sys.exit(1)
if mode=="err2": print("usage"); sys.exit(2)
