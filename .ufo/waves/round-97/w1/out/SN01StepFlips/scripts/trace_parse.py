#!/usr/bin/env python3
"""SN01StepFlips standalone parser tracer.

Extracts ROUTER_PY from the tracked probe (read-only, via `git show`), patches a COPY in
scratch to name the guard that decided, and runs gguf_parse directly on each fixture.

This answers: for each (T, nd) fixture, WHICH guard produced the verdict?
  steps          -> the step budget (MAX_STEPS) tripped: the claim's "-"
  meta           -> the header-position ceiling (MAX_META) tripped
  size           -> the `pos + n > size` guard tripped (Bad -> invalid)
  guard-size     -> the `n_kv*13 + n_tensors*24 > size` early return
  guard-max_tensors -> the MAX_TENSORS early return
  offset-ok      -> the parse completed and the offset chain decided invalid
  ok             -> the parse completed and the file is well-formed (state "ok")
"""
import ast
import json
import re
import struct
import subprocess
import sys
import time
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
FIX = Path("/fast/scratch/hyaku/kama-r97/SN01StepFlips/fix")
OUT = Path("/fast/scratch/hyaku/kama-r97/SN01StepFlips/trace")

CASES = [(833332, 1), (833333, 1), (900000, 1), (700000, 4), (555555, 4), (555556, 4)]


def extract_router_py() -> str:
    src = subprocess.run(["git", "-C", str(LANE), "show", "HEAD:tools/kama-probe.sh"],
                         capture_output=True, text=True).stdout
    m = re.search(r"^ROUTER_PY=\$\(cat <<'PY'\n(.*?)^PY$", src, re.S | re.M)
    assert m, "ROUTER_PY not found"
    return m.group(1)


def patch(py: str) -> str:
    out = []
    for line in py.splitlines():
        if line.strip() == "raise Unknown()":
            indent = line[:len(line) - len(line.lstrip())]
            out.append(f'{indent}raise Unknown("steps:" + str(steps[0]))')
            continue
        if line.strip() == "raise Bad()":
            indent = line[:len(line) - len(line.lstrip())]
            out.append(f'{indent}raise Bad("size:" + str(f.tell()) + "+" + str(n) + ">" + str(size))')
            continue
        out.append(line)
    py = "\n".join(out) + "\n"
    # name the early returns
    py = py.replace('            if n_kv * 13 + n_tensors * 24 > size:\n                return "invalid"',
                    '            if n_kv * 13 + n_tensors * 24 > size:\n                return "invalid-guard-size"')
    py = py.replace('            if n_kv > MAX_KV or n_tensors > MAX_TENSORS:\n                return "-"',
                    '            if n_kv > MAX_KV or n_tensors > MAX_TENSORS:\n                return "-guard-max_tensors"')
    # report the step count and the reason
    py = py.replace('        except Bad:\n            return "invalid"\n        except Unknown:\n            return "-"',
                    '        except Bad as e:\n            return "invalid:" + str(e)\n'
                    '        except Unknown as e:\n            return "-:" + str(e)')
    # report the final step count on a completed parse
    py = py.replace('            return "ok"\n', '            return "ok:steps=" + str(steps[0])\n')
    assert "invalid-guard-size" in py and "steps:" in py and "ok:steps=" in py, "patch failed"
    return py


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    py = patch(extract_router_py())
    mod = OUT / "router_traced.py"
    mod.write_text(py)
    # strip the CLI driver (the module runs its own argv logic at import); keep only the defs
    # by executing only the top part up to `try:\n    doc = json.load`
    src = py.split("\ntry:\n    doc = json.load")[0]
    ns = {"__name__": "traced"}
    exec(compile(src, str(mod), "exec"), ns)
    gguf_parse = ns["gguf_parse"]
    MAX_STEPS = ns["MAX_STEPS"]
    MAX_TENSORS = ns["MAX_TENSORS"]
    MAX_META = ns["MAX_META"]

    rows = []
    for T, nd in CASES:
        for fam in ("A", "B"):
            p = FIX / f"t{T}_nd{nd}_{fam}.gguf"
            t0 = time.monotonic()
            state = gguf_parse(str(p))
            dt = time.monotonic() - t0
            steps_claim = 4 + T * (5 + nd)
            rec = {"T": T, "nd": nd, "fam": fam, "path": str(p), "bytes": p.stat().st_size,
                   "state": state, "parse_seconds": round(dt, 3),
                   "steps_claim": steps_claim, "max_steps": MAX_STEPS,
                   "max_tensors": MAX_TENSORS, "max_meta": MAX_META,
                   "over_budget": steps_claim > MAX_STEPS}
            rows.append(rec)
            print(f"T={T} nd={nd} fam={fam} bytes={rec['bytes']} state={state} "
                  f"parse={dt:.3f}s steps_claim={steps_claim} over={rec['over_budget']}")
    (OUT / "trace_results.json").write_text(json.dumps(rows, indent=1))
    print(f"WROTE {OUT / 'trace_results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
