#!/usr/bin/env python3
"""SN01StepFlips: does the SKILL.md table's VERDICT column generalise?

The SKILL.md round-97 table pairs a step count with a verdict:
    833,332 | nd=1 | 4,999,996 | <= budget | invalid
and the prose says "MAX_STEPS = 5,000,000 decides it (invalid) when that sum fits".

That pairing is only true for a file that is ALSO malformed. This builds WELL-FORMED files
of the same (T, nd) - correct offsets, real data section, consistent sizes - so the probe can
reach a verdict, and reads what the probe actually returns.

If the probe returns `ok` for a well-formed 833,332-tensor nd=1 file, then "invalid" is a
property of the fixture, not of the step budget, and the table's verdict column (plus the
prose) over-generalises.
"""
import json
import struct
import subprocess
import sys
import time
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
OUT = Path("/fast/scratch/hyaku/kama-r97/SN01StepFlips/wellformed")
CASES = [(833332, 1), (555555, 4), (833333, 1), (555556, 4)]


def wellformed(T: int, nd: int) -> bytes:
    """A GGUF the loader would accept: sequential aligned offsets + a real data section."""
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", T, 0)]
    off = 0
    for i in range(T):
        name = b"t%07d" % i
        dims = struct.pack("<" + "Q" * nd, 1, *([1] * (nd - 1)))
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<I", nd) + dims
                   + struct.pack("<IQ", 0, off))   # type 0 = F32
        off += 32                                          # 4 bytes of data, 32-aligned
    head = b"".join(out)
    pad = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * pad + b"\0" * off


def traced_module():
    import re
    src = subprocess.run(["git", "-C", str(LANE), "show", "HEAD:tools/kama-probe.sh"],
                         capture_output=True, text=True).stdout
    m = re.search(r"^ROUTER_PY=\$\(cat <<'PY'\n(.*?)^PY$", src, re.S | re.M)
    py = m.group(1)
    py = py.replace('            return "ok"\n', '            return "ok:steps=" + str(steps[0])\n')
    py = py.replace('        except Unknown:\n            return "-"',
                    '        except Unknown as e:\n            return "-:" + str(e)\n')
    py = py.replace('        except Bad:\n            return "invalid"',
                    '        except Bad as e:\n            return "invalid:" + str(e)\n')
    src = py.split("\ntry:\n    doc = json.load")[0]
    ns = {"__name__": "traced"}
    exec(compile(src, "router_traced.py", "exec"), ns)
    return ns


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ns = traced_module()
    gguf_parse = ns["gguf_parse"]
    rows = []
    for T, nd in CASES:
        blob = wellformed(T, nd)
        p = OUT / f"wf_t{T}_nd{nd}.gguf"
        p.write_bytes(blob)
        t0 = time.monotonic()
        state = gguf_parse(str(p))
        dt = time.monotonic() - t0
        steps = 4 + T * (5 + nd)
        rec = {"T": T, "nd": nd, "bytes": len(blob), "state": state, "seconds": round(dt, 3),
               "steps_claim": steps, "fits_budget": steps <= 5_000_000,
               "table_verdict": "invalid" if steps <= 5_000_000 else "-"}
        rows.append(rec)
        print(f"wellformed T={T} nd={nd} bytes={len(blob)} steps_claim={steps} "
              f"fits_budget={rec['fits_budget']} table_says={rec['table_verdict']} "
              f"probe_says={state} ({dt:.2f}s)")
    (OUT / "wellformed_results.json").write_text(json.dumps(rows, indent=1))
    print(f"WROTE {OUT / 'wellformed_results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
