#!/usr/bin/env python3
"""SN01StepFlips - end-to-end behavioural comparison: real probe vs +1/header overcharge probe.

Both run through the SAME stub router and the SAME fixtures; only the probe bytes differ
(the mutant is applied to a SCRATCH COPY - the tracked lane file is never touched).

The verdict that matters: a fixture that grades `invalid` (MODEL_UNLOADED / router-model-invalid)
under the real probe and MODEL_OK / router-unloaded-autoload under the mutant is DECIDED by
the step budget, so a cell on it is a real discriminator against the +1/header forgery.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drive import Stub, router_body, PROPS, run_probe, extract_router_py, direct_parse  # noqa: E402

ANCHOR = "            for _ in range(n_tensors):"


def main() -> int:
    scratch = Path(sys.argv[1]).resolve()
    src = Path(sys.argv[2]).resolve()
    fdir = Path(sys.argv[3]).resolve()
    work = scratch / "mutant"
    work.mkdir(parents=True, exist_ok=True)
    cwd = scratch / "cwd"
    cwd.mkdir(parents=True, exist_ok=True)
    exe = str(fdir / "ok.gguf")

    text = src.read_text()
    if text.count(ANCHOR) != 1:
        raise SystemExit(f"overcharge anchor appears {text.count(ANCHOR)} times, not 1")
    mtext = text.replace(ANCHOR, ANCHOR + "\n                steps[0] += 1", 1)
    mprobe = work / "probe-overcharge.sh"
    mprobe.write_text(mtext)

    # confirm the patch really is a +1/header charge and nothing else
    m2 = re.search(r"MAX_STEPS = [0-9_]+", mtext)
    print(f"MUTANT bytes_delta={len(mtext) - len(text)} max_steps_line={m2.group(0)} "
          f"anchor_count={mtext.count(ANCHOR)}")

    edir = fdir.parent / "edge"
    fixtures = [("t800k_nd1", 800_000, 1), ("t520k_nd4", 520_000, 4),
                ("t714286_nd1", 714_286, 1), ("t555554_nd4", 555_554, 4)]
    if edir.is_dir():
        fixtures += [("edge714285_nd1", 714_285, 1), ("edge714286_nd1", 714_286, 1),
                     ("edge714287_nd1", 714_287, 1), ("edge499999_nd4", 499_999, 4),
                     ("edge500000_nd4", 500_000, 4), ("edge500001_nd4", 500_001, 4)]
    rows = []
    for name, T, nd in fixtures:
        path = (edir if name.startswith("edge") else fdir) / f"{name}.gguf"
        body = work / f"{name}.body.json"
        body.write_bytes(router_body([[exe, "-m", str(path)]]))
        r_state, r_dt = direct_parse(extract_router_py(text), body, 0, cwd)
        m_state, m_dt = direct_parse(extract_router_py(mtext), body, 0, cwd)
        real = []
        mut = []
        for _ in range(2):
            routes = {"/v1/models": router_body([[exe, "-m", str(path)]]), "/props": PROPS}
            with Stub(routes) as st:
                real.append(run_probe(src, cwd, st.port))
            with Stub(routes) as st:
                mut.append(run_probe(mprobe, cwd, st.port))
        print(f"E2E {name} T={T} nd={nd} real_state={r_state} ({r_dt:.2f}s) "
              f"mutant_state={m_state} ({m_dt:.2f}s)")
        for i, (rr, mm) in enumerate(zip(real, mut), 1):
            print(f"E2E {name} run{i} real={rr[1]}/{rr[2]} {rr[3]:.2f}s | "
                  f"mutant={mm[1]}/{mm[2]} {mm[3]:.2f}s")
        rows.append(dict(name=name, T=T, nd=nd, real_state=r_state, mutant_state=m_state,
                         real_verdict=real[0][1], real_reason=real[0][2],
                         mutant_verdict=mut[0][1], mutant_reason=mut[0][2],
                         real_seconds=real[0][3], mutant_seconds=mut[0][3]))
    (work / "e2e.json").write_text(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
