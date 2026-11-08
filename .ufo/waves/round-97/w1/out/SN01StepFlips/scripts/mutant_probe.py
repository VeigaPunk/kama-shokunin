#!/usr/bin/env python3
"""SN01StepFlips: mutant probes against the real parser.

Q1 (contrast row): T=700,000 nd=1 -> the SKILL.md prose asserts it "decides invalid".
Q2 (forgery coverage): a probe that charges ONE EXTRA STEP PER TENSOR HEADER (5+nd -> 6+nd)
    still satisfies every C2 cell's expectation, but it makes SKILL.md's C3 table stale:
    the within-budget rows (833,332 @ nd=1, 555,555 @ nd=4) would become `-`, not `invalid`.
    Does any counter catch that?
"""
import json
import re
import struct
import subprocess
import sys
import time
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SCRATCH = Path("/fast/scratch/hyaku/kama-r97/SN01StepFlips")
FIX = SCRATCH / "fix"

# (T, nd, malformed?) -> expected probe state
CASES = [
    (700000, 1, True),    # SKILL prose: "a 700,000-tensor nd=1 file decides invalid"
    (833332, 1, True),
    (555555, 4, True),
    (900000, 1, True),
    (833333, 1, True),
    (700000, 4, True),
    (555556, 4, True),
]


def router_py() -> str:
    src = subprocess.run(["git", "-C", str(LANE), "show", "HEAD:tools/kama-probe.sh"],
                         capture_output=True, text=True).stdout
    m = re.search(r"^ROUTER_PY=\$\(cat <<'PY'\n(.*?)^PY$", src, re.S | re.M)
    return m.group(1)


def load(mod_src: str):
    src = mod_src.split("\ntry:\n    doc = json.load")[0]
    ns = {"__name__": "m"}
    exec(compile(src, "m.py", "exec"), ns)
    return ns


def instrument(py: str) -> str:
    py = py.replace('            return "ok"\n', '            return "ok:steps=" + str(steps[0])\n')
    py = py.replace('        except Unknown:\n            return "-"',
                    '        except Unknown as e:\n            return "-:" + str(e)\n')
    py = py.replace('        except Bad:\n            return "invalid"',
                    '        except Bad as e:\n            return "invalid:" + str(e)\n')
    return py


def mutant_plus1(py: str) -> str:
    """One extra step charged per tensor header."""
    anchor = "                skip(u64())  # name\n"
    assert py.count(anchor) == 1, py.count(anchor)
    return py.replace(anchor, anchor + "                need(1)  # MUTANT: +1 step per header\n")


def main() -> int:
    base_py = router_py()
    variants = {
        "honest": load(instrument(base_py)),
        "plus1_per_header": load(instrument(mutant_plus1(base_py))),
    }
    rows = []
    for name, ns in variants.items():
        gguf_parse = ns["gguf_parse"]
        for T, nd, _ in CASES:
            p = FIX / f"t{T}_nd{nd}_A.gguf"
            t0 = time.monotonic()
            state = gguf_parse(str(p))
            dt = time.monotonic() - t0
            honest_steps = 4 + T * (5 + nd)
            mutant_steps = 4 + T * (6 + nd)
            rows.append({"variant": name, "T": T, "nd": nd, "state": state,
                         "seconds": round(dt, 3), "honest_steps": honest_steps,
                         "variant_steps": mutant_steps,
                         "honest_verdict_src": "invalid" if honest_steps <= 5_000_000 else "-",
                         "honest_verdict": "invalid" if honest_steps <= 5_000_000 else "-",
                         "variant_verdict": "invalid" if mutant_steps <= 5_000_000 else "-"})
            print(f"{name:18s} T={T:7d} nd={nd} state={state:22s} "
                  f"steps_claim={'4999999' if name=='honest' else ''}"
                  f" honest_verdict={rows[-1]['honest_verdict']:8s} "
                  f"variant_verdict={rows[-1]['variant_verdict']:8s} ({dt:.2f}s)")
    (SCRATCH / "mutant_results.json").write_text(json.dumps(rows, indent=1))
    print(f"WROTE {SCRATCH / 'mutant_results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
