#!/usr/bin/env python3
import sys
sys.path.insert(0, "/fast/scratch/hyaku/kama-r100/RV02WordingC2")
import harness
from harness import Stub, run_probe, make_shim, send_http, ROUTER_ON
def main():
    results = []
    for rc, name in [(7, "rc7-refused"), (28, "rc28-timeout"), (52, "rc52-empty"), (56, "rc56-reset"), (63, "rc63-maxfilesize")]:
        shim = make_shim(rc, dirn="shim%d" % rc)
        st = Stub(lambda c: send_http(c, 200, ROUTER_ON)); st.start()
        try:
            got = run_probe(st.port, shim=shim)
        finally:
            st.close()
        line = "CASE X-shim-%s verdict=%s reason=%s exit=%s (probe line ||return2)" % (name, got[0], got[1], got[2])
        print(line, flush=True); results.append(line)
    shim28 = make_shim(28, dirn="shim-plain")
    for mode in ["listeners", "consumers"]:
        st = Stub(lambda c: send_http(c, 200, ROUTER_ON)); st.start()
        try:
            got = run_probe(st.port, mode=mode, shim=shim28)
        finally:
            st.close()
        line = "CASE X-plain-%s-rc28 verdict=%s reason=%s exit=%s (set-e plain path)" % (mode, got[0], got[1], got[2])
        print(line, flush=True); results.append(line)
    harness.WORK.__class__  # keep ref
    (harness.WORK / "results2.txt").write_text("\n".join(results) + "\n")
    print("DONE2 %d" % len(results))
main()
