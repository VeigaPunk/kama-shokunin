#!/usr/bin/env python3
"""SN01StepFlips - measure the REAL step boundary by sweeping MAX_STEPS on a SCRATCH COPY.

The tracked lane probe is never modified: the bytes are copied into the scratch dir and the
MAX_STEPS constant is rewritten there. For each fixture the sweep finds the smallest
MAX_STEPS at which the parser still DECIDES (`invalid`) - i.e. the number of steps the real
parser actually charges for that file.

The sweep also tells WHICH guard decided:
  * threshold == 4                       -> the size guard (n_kv*13 + n_tensors*24 > size) fired
  * threshold == 4 + T*(5+nd)           -> the header parse completed; the offset check decided
  * state is `-` at every MAX_STEPS     -> MAX_TENSORS / MAX_META decided
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drive import router_body, extract_router_py, direct_parse  # noqa: E402


def patched_probe(src: Path, dst: Path, max_steps: int) -> bool:
    text = src.read_text()
    new, n = re.subn(r"(?m)^MAX_STEPS = [0-9_]+", f"MAX_STEPS = {max_steps}", text)
    if n != 1:
        return False
    dst.write_text(new)
    return True


def main() -> int:
    scratch = Path(sys.argv[1]).resolve()
    src = Path(sys.argv[2]).resolve()
    fdir = Path(sys.argv[3]).resolve()
    work = scratch / "sweep"
    work.mkdir(parents=True, exist_ok=True)
    cwd = scratch / "cwd"
    cwd.mkdir(parents=True, exist_ok=True)
    exe = str(fdir / "ok.gguf")
    fixtures = [("t800k_nd1", 800_000, 1), ("t520k_nd4", 520_000, 4),
                ("t714286_nd1", 714_286, 1), ("t555554_nd4", 555_554, 4)]
    out = {}
    for name, T, nd in fixtures:
        path = fdir / f"{name}.gguf"
        body = work / f"{name}.body.json"
        body.write_bytes(router_body([[exe, "-m", str(path)]]))
        probe_path = work / f"probe-{name}.sh"
        lo, hi = 4, 6_000_000
        best = None
        while lo <= hi:
            mid = (lo + hi) // 2
            if not patched_probe(src, probe_path, mid):
                raise SystemExit("MAX_STEPS anchor not unique")
            rp = extract_router_py(probe_path.read_text())
            state, _ = direct_parse(rp, body, 0, cwd)
            if state == "invalid":
                best = mid
                hi = mid - 1
            else:
                lo = mid + 1
        # the mutant (+1 per header) threshold
        mlo, mhi = 4, 8_000_000
        mbest = None
        while mlo <= mhi:
            mid = (mlo + mhi) // 2
            text = src.read_text()
            anchor = "            for _ in range(n_tensors):"
            if text.count(anchor) != 1:
                raise SystemExit("overcharge anchor not unique")
            text = text.replace(anchor, anchor + "\n                steps[0] += 1", 1)
            text, n = re.subn(r"(?m)^MAX_STEPS = [0-9_]+", f"MAX_STEPS = {mid}", text)
            assert n == 1
            probe_path.write_text(text)
            rp = extract_router_py(text)
            state, _ = direct_parse(rp, body, 0, cwd)
            if state == "invalid":
                mbest = mid
                mhi = mid - 1
            else:
                mlo = mid + 1
        plan = 4 + T * (5 + nd)
        mut = 4 + T * (6 + nd)
        out[name] = dict(T=T, nd=nd, measured_threshold=best, plan_steps=plan,
                         mutant_threshold=mbest, mutant_plan=mut,
                         match=best == plan, mutant_match=mbest == mut)
        print(f"SWEEP {name} T={T} nd={nd} measured_deciding_threshold={best} "
              f"plan_steps={plan} match={int(best == plan)} | "
              f"mutant(+1/header)_threshold={mbest} mutant_plan={mut} "
              f"mutant_match={int(mbest == mut)}", flush=True)
    (work / "sweep.json").write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
