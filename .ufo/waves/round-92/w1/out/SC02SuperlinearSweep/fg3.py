import sys, json
from pathlib import Path
sys.path.insert(0,"/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
from harness import Stub, Runner, jbody, uptime_str
S=Path("/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
R={k:Runner(S,(S/f).read_bytes(),k) for k,f in {"M2":"probe-M2.sh","BASE":"probe-BASE.sh"}.items()}
D=str(S)
def body_for(N, target):
    return {"object":"list","data":[{"id":"good","status":{"value":"unloaded",
            "args":["/etc/hostname","--model",target]}} for i in range(N)]}
for target,label in ((f"{D}/slow.gguf","slow-invalid"), (f"{D}/no-such.gguf","missing")):
    for N in (1,6):
        for tag in ("M2","BASE"):
            with Stub({"/v1/models": jbody(body_for(N,target)),
                       "/props": b'{"role":"router","models_autoload":true}'}) as s:
                rc,so,se,dt=R[tag].check(s.port,"good")
                try:
                    row=json.loads(so)["rows"][0]; v=row["verdict"]; rsn=row["reason"]
                except Exception: v=rsn="unparsed"
                print(f"FG3-{tag:<5} {label:<14} N={N:<3} rc={rc} t={dt:6.2f}s verdict={v:<16} reason={rsn:<26} {uptime_str()}", flush=True)
