import sys, shutil
from pathlib import Path
sys.path.insert(0,"/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
from harness import Stub, Runner, ids_doc, jbody, uptime_str
S=Path("/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
def reg(runner, port, nrows, label, kill=240):
    d=S/"rows"
    if d.exists(): shutil.rmtree(d)
    d.mkdir(parents=True)
    pin=d/"pin.txt"; pin.write_text(f"http://127.0.0.1:{port}/v1\n")
    regf=d/"registry.tsv"
    L=["id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes"]
    for i in range(nrows): L.append(f"row{i}\t{pin}\tgrep:http://[^ ]+\thttp://127.0.0.1:{port}/v1\ta\tr")
    regf.write_text("\n".join(L)+"\n")
    hist=d/"history"
    rc,so,se,dt=runner.run(["check","--json","--registry",str(regf),"--history",str(hist),
                             "--timeout","5","--connect-timeout","2"],kill=kill)
    print(f"{label:<46} rc={rc} t={dt:7.2f}s out={len(so)}B {uptime_str()}", flush=True)
    return dt
R={k:Runner(S,(S/f).read_bytes(),k) for k,f in
   {"M2":"probe-M2.sh","cand-json_array":"cand-json_array.sh"}.items()}
print("=== rows FIXED at 8, per-row listener bytes double ===", flush=True)
for pay in (100000,200000,400000):
    for tag in ("M2","cand-json_array"):
        with Stub({"/v1/models": jbody(ids_doc(["a"*pay]))}) as s:
            reg(R[tag], s.port, 8, f"BYTES-{tag}-rows8-payload-{pay}")
