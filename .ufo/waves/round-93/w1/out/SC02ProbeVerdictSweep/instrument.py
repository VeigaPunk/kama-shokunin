#!/usr/bin/env python3
"""SC02: instrument the M1 ROUTER_PY copy in scratch (candidate file, lane untouched).

Adds counters for steps consumed, wall time and the reason a parse ended, then
reports steps/parse for GGUF shapes so the DEADLINE (4.0 s wall) vs MAX_STEPS
(4M) crossover can be located.
"""
import json, os, re, struct, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep")
from extract import gguf

SRC = Path("/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep/router-m1.py").read_text()
# report the final step count and wall time of each parse
SRC = SRC.replace(
    "        except Bad:\n            return \"invalid\"\n        except Unknown:\n            return \"-\"\n",
    "        except Bad:\n            REPORT.append(('bad', steps[0], time.monotonic() - T0)); return \"invalid\"\n"
    "        except Unknown:\n            REPORT.append(('unknown', steps[0], time.monotonic() - T0)); return \"-\"\n",
)
assert "REPORT.append" in SRC, "instrumentation anchor not found"
SRC = SRC.replace("MAX_STEPS, DEADLINE = 4_000_000, time.monotonic() + 4.0",
                  "MAX_STEPS, DEADLINE = 4_000_000, time.monotonic() + 4.0\nREPORT = []\nT0 = time.monotonic()")
# also report the "ok" and early-return outcomes
SRC = SRC.replace('            return "invalid"\n        except Bad:', '            return "invalid"\n        except Bad:')
W = Path(sys.argv[1]); W.mkdir(parents=True, exist_ok=True)
exe = W / "ok.gguf"; exe.write_bytes(gguf(1, 32, True))

for tens in (150000, 300000, 600000, 700000, 900000):
    f = W / f"t{tens}.gguf"
    if not f.exists():
        f.write_bytes(gguf(tens, 1, False))
    body = W / f"body{tens}.json"
    body.write_bytes(json.dumps({"object": "list", "data": [
        {"id": "good", "status": {"value": "unloaded", "args": [str(exe), "-m", str(f)]}}]}).encode())
    src = SRC + "\n"
    # append a report printer at the end of the 'files' branch
    src = src.replace('    sys.exit(0)\nfor n, e in enumerate(seq):',
                       '    sys.stderr.write(repr(REPORT)+"\\n")\n    sys.exit(0)\nfor n, e in enumerate(seq):')
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, "-c", src, str(body), "files", "0"], capture_output=True)
    dt = time.monotonic() - t0
    print(f"tensors={tens} wall={dt:.2f}s out={p.stdout.decode().strip()!r} report={p.stderr.decode().strip()}", flush=True)
