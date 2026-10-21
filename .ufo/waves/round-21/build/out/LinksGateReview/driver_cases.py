import importlib.util
import os
import subprocess
import sys

# Scratch-only driver: loads a snapshot of check-receipt.py unchanged and
# records every selftest subprocess verdict (exit code + gate stdout).
rev = sys.argv[1]
path = f"/tmp/kama-r21-LinksGateReview/{rev}/tests/llamacpp-live/check-receipt.py"
spec = importlib.util.spec_from_file_location("cr_" + rev, path)
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)

orig_run = subprocess.run
log = []


def wrap(args, *a, **kw):
    res = orig_run(args, *a, **kw)
    if isinstance(args, list) and len(args) > 2 \
            and "case-" in os.path.basename(str(args[2])):
        log.append((os.path.basename(args[2]), res.returncode,
                    res.stdout, res.stderr, args[3:]))
    return res


subprocess.run = wrap
rc = cr._selftest()
print(f"# rev={rev} selftest_return={rc} recorded_cases={len(log)}")
for name, code, out, err, extra in log:
    lines = out.strip().splitlines()
    head = lines[0] if lines else "<no stdout>"
    print(f"{name}\texit={code}\t{head}")
    for line in lines[1:]:
        print(f"      {line}")
    if err.strip():
        print(f"      STDERR: {err.strip()[:300]}")
