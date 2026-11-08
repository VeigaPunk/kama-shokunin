import json, subprocess, sys, time, http.server, socket, threading, os
from pathlib import Path
sys.path.insert(0, "/fast/scratch/hyaku/kama-r97/SN01StepFlips")
from driver import Stub, router_body, PROPS, run_check, PROBE_DIR
SCRATCH = Path("/fast/scratch/hyaku/kama-r97/SN01StepFlips")
WF = SCRATCH / "wellformed"
pristine = PROBE_DIR / "pristine" / "kama-probe.sh"
cwd = SCRATCH / "cwd"; cwd.mkdir(exist_ok=True)
exe = str(WF / "ok.gguf")
# ok.gguf for the exe slot
import struct
head = (b"GGUF" + struct.pack("<I",3) + struct.pack("<QQ",1,0) + struct.pack("<Q",2) + b"t0"
        + struct.pack("<I",1) + struct.pack("<Q",32) + struct.pack("<IQ",0,0))
pad = (len(head)+31)//32*32 - len(head)
(Path(WF)/"ok.gguf").write_bytes(head + b"\0"*pad + b"\0"*128)
for T, nd in [(833332,1),(555555,4),(833333,1),(555556,4)]:
    f = WF / f"wf_t{T}_nd{nd}.gguf"
    body = router_body([[str(WF/"ok.gguf"), "-m", str(f)]])
    with Stub({"/v1/models": body, "/props": PROPS}) as st:
        r = run_check(pristine, st.port, cwd)
    print(f"WELLFORMED T={T} nd={nd} router_verdict={r['verdict']}/{r['reason']} wall={r['wall']:.2f}s")
