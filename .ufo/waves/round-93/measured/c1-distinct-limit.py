#!/usr/bin/env python3
"""Round-93 L1 receipt for the C1 disclosed limit (round-94 planned item 2): N DISTINCT slow invalid copies, one
entry each, probe at the repaired C1 revision, 2 runs per N; prints the verdict per N and the load. Usage: <scratch>"""
import importlib.util, sys, tempfile
from pathlib import Path
spec = importlib.util.spec_from_file_location("rr", "tools/round93-router-repeat.py")
rr = importlib.util.module_from_spec(spec); spec.loader.exec_module(rr)
import subprocess
REV = "b37657998858b6300fc8fbbbebb7e256239bf0f8"
work = Path(tempfile.mkdtemp(dir=sys.argv[1])); R = rr.Runner(work)
R.install(subprocess.run(["git", "show", f"{REV}:tools/kama-probe.sh"], capture_output=True, check=True).stdout)
ok = work / "ok.gguf"; ok.write_bytes(rr.gguf(1, 32, True))
blob = rr.gguf(rr.TENSORS, 1, False)
files = []
for i in range(32):
    p = work / f"slow{i:02d}.gguf"; p.write_bytes(blob); files.append(str(p))
print(f"# rev={REV} load1={open('/proc/loadavg').read().split()[0]}")
for n in (1, 2, 4, 6, 8, 12, 16, 32):
    body = rr.router_body([[str(ok), "-m", files[i]] for i in range(n)])
    with rr.Stub({"/v1/models": body, "/props": rr.PROPS}) as st:
        res = [R.check(st.port) for _ in range(2)]
    print(f"C1_DISTINCT n={n} " + " ".join(f"{v}/{r}/{dt:.2f}s" for _, v, r, dt in res), flush=True)
