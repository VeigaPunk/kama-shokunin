#!/usr/bin/env python3
"""CR01RepeatCounter - fixture audit for the frozen round-93 C1 counter.

Answers three questions with the counter's own bytes:
 1. is slow.gguf parsed to the END of its tensor-info list before `invalid`?
 2. is ok.gguf `ok` for the M1 parser (and what does the counter's sanity loop compare)?
 3. does P02 need a DECIDED valid candidate (raw `ok`) or only a candidate that is not bad?

Method: import the frozen counter module (read-only), build its exact fixtures with its own
gguf(), extract ROUTER_PY from the M1 probe bytes, and append a driver that prints the raw
gguf_state(path).  A second copy carries stderr diagnostics at the two exits so the return
point is visible (not graded; diagnostic only).
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
OUT = LANE / ".ufo/waves/round-93/w1/out/CR01RepeatCounter"
SCR = Path("/fast/scratch/hyaku/kama-r93/CR01RepeatCounter")
M1 = "fe5f031cb1b9d33e1160360d892149b8ac3c7771"

spec = importlib.util.spec_from_file_location("rr", LANE / "tools/round93-router-repeat.py")
rr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rr)

probe = subprocess.run(["git", "-C", str(LANE), "show", f"{M1}:tools/kama-probe.sh"],
                       capture_output=True, check=True).stdout
rp = rr.probe_router_py(probe)

DRIVER = '''

if len(sys.argv) > 2 and sys.argv[2] == "diag":
    for p in sys.argv[3:]:
        t0 = time.monotonic()
        st = gguf_state(p)
        print("%s\\t%s\\t%.3fs" % (p, st, time.monotonic() - t0))
    sys.exit(0)
'''

DIAG_INVALID_OLD = '''            for off, nbytes in infos:
                if off != expect or start + off + nbytes > size:
                    return "invalid"
'''
DIAG_INVALID_NEW = '''            for off, nbytes in infos:
                if off != expect or start + off + nbytes > size:
                    sys.stderr.write("DIAG_INVALID_AT tell=%d size=%d steps=%d ninfos=%d off=%d nbytes=%d\\n"
                                     % (f.tell(), size, steps[0], len(infos), off, nbytes))
                    return "invalid"
'''
DIAG_OK_OLD = '''            return "ok"
'''
DIAG_OK_NEW = '''            sys.stderr.write("DIAG_OK_AT tell=%d size=%d steps=%d ninfos=%d\\n"
                             % (f.tell(), size, steps[0], len(infos)))
            return "ok"
'''

fx = SCR / "fixture-audit"
fx.mkdir(parents=True, exist_ok=True)
slow, ok, ok2 = fx / "slow.gguf", fx / "ok.gguf", fx / "ok2.gguf"
slow_bytes, ok_bytes, ok2_bytes = rr.gguf(rr.TENSORS, 1, False), rr.gguf(1, 32, True), rr.gguf(2, 32, True)
slow.write_bytes(slow_bytes)
ok.write_bytes(ok_bytes)
ok2.write_bytes(ok2_bytes)
missing = fx / "absent" / "missing.gguf"

# a plausible distinct valid file: same byte size as slow.gguf (trailing slack is legal)
padded = fx / "okpad.gguf"
padded.write_bytes(ok_bytes + b"\0" * (len(slow_bytes) - len(ok_bytes)))
assert len(padded.read_bytes()) == len(slow_bytes)

body = json.dumps({"object": "list", "data": [
    {"id": "good", "status": {"value": "unloaded", "args": ["/bin/true", "-m", str(p)]}} for p in
    (slow, ok, ok2, padded, missing)]}).encode()
bpath = fx / "body.json"
bpath.write_bytes(body)

print(f"FIXTURE sizes slow={len(slow.read_bytes())} ok={len(ok.read_bytes())} "
      f"ok2={len(ok2.read_bytes())} padded={len(padded.read_bytes())}")

r = subprocess.run([sys.executable, "-c", rp + DRIVER, str(bpath), "diag",
                    str(slow), str(ok), str(ok2), str(padded), str(missing)],
                   capture_output=True, text=True)
print("FIXTURE_RAW_STATE " + r.stdout.strip().replace("\n", " | "))

drp = rp
assert drp.count(DIAG_INVALID_OLD) == 1 and drp.count(DIAG_OK_OLD) == 1
drp = drp.replace(DIAG_INVALID_OLD, DIAG_INVALID_NEW).replace(DIAG_OK_OLD, DIAG_OK_NEW)
rd = subprocess.run([sys.executable, "-c", drp + DRIVER, str(bpath), "diag",
                     str(slow), str(ok)], capture_output=True, text=True)
print("FIXTURE_DIAG_STATE " + rd.stdout.strip().replace("\n", " | "))
for line in rd.stderr.splitlines():
    print("FIXTURE_DIAG " + line)

# what the counter's own sanity loop asserts (file_state, not gguf_state)
rs = subprocess.run([sys.executable, "-c", rp, str(bpath), "files", "0", "1", "2", "3", "4"],
                    capture_output=True, text=True)
print("FIXTURE_FILE_STATE " + rs.stdout.strip().replace("\n", " | "))
print("FIXTURE_SANITY_EXPECT src=tools/round93-router-repeat.py:208 "
      "slow=invalid ok=- ok2=- missing=missing (raw ok is never asserted)")
