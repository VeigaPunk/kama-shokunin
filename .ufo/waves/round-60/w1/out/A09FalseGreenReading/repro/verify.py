"""Run the lane's round60-c1-counter verify() against a receipt (read-only use of lane source)."""
import importlib.util
import json
import sys

spec = importlib.util.spec_from_file_location(
    'c1counter', '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round60-c1-counter.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

receipt = json.load(open(sys.argv[1]))
run_dir = sys.argv[2]
nonce = sys.argv[3]
bad = mod.verify(receipt, run_dir, nonce)
print('verify_bad=' + json.dumps(bad))
print('accepted=' + str(not bad).lower())
