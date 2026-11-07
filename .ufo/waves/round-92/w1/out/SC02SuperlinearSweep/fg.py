import sys, json
from pathlib import Path
sys.path.insert(0,"/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
from harness import Stub, Runner, jbody, uptime_str
S=Path("/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
R=Runner(S,(S/"probe-M2.sh").read_bytes(),"M2")
D=str(S)
for N in (1,2,5,10,20,50):
    body={"object":"list","data":[{"id":f"g{i:05d}","status":{"value":"unloaded",
            "args":["/etc/hostname","--model",f"{D}/slow.gguf"]}} for i in range(N)]}
    with Stub({"/v1/models": jbody(body),
               "/props": b'{"role":"router","models_autoload":true}'}) as s:
        rc,so,se,dt=R.check(s.port,"good")
        try:
            row=json.loads(so)["rows"][0]; v=row["verdict"]; rsn=row["reason"]
        except Exception: v=rsn="unparsed"
        print(f"FG-M2 N={N:<4} rc={rc} t={dt:6.2f}s verdict={v:<16} reason={rsn:<26} {uptime_str()}", flush=True)
