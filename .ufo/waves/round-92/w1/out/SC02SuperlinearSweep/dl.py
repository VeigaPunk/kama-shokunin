import sys, json, time
from pathlib import Path
sys.path.insert(0,"/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
from harness import Stub, Runner, jbody, uptime_str
S=Path("/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
R=Runner(S,(S/"probe-M2.sh").read_bytes(),"M2")
SLOW="/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep/slow.gguf"
def entry(i):
    return {"id": f"g{i:05d}", "status": {"value": "unloaded",
            "args": [SLOW, "--model", SLOW]}}
for N in (50, 500, 5000, 20000):
    body={"object":"list","data":[entry(i) for i in range(N)]}
    b=jbody(body)
    with Stub({"/v1/models": b, "/props": b'{"role":"router","models_autoload":true}'}) as s:
        rc,so,se,dt=R.check(s.port, "*")
        try:
            row=json.loads(so)["rows"][0]; v=row["verdict"]; rsn=row["reason"]
        except Exception as e:
            v=rsn=f"unparsed {e}"
        print(f"N={N:<6} body={len(b)}B rc={rc} t={dt:6.2f}s verdict={v:<16} reason={rsn:<26} {uptime_str()}", flush=True)
