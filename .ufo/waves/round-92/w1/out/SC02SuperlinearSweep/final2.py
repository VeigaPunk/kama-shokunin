import sys, shutil
from pathlib import Path
sys.path.insert(0,"/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
from harness import Stub, Runner, ids_doc, jbody, uptime_str
S=Path("/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
def reg(runner, port, nrows, label, kill=180):
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
    print(f"{label:<44} rc={rc} t={dt:7.2f}s out={len(so)}B {uptime_str()}", flush=True)
    return dt
R={k:Runner(S,(S/f).read_bytes(),k) for k,f in
   {"M2":"probe-M2.sh","cand-json_array":"cand-json_array.sh"}.items()}
print("=== json_array attribution, interleaved, payload 200000 B/row ===", flush=True)
for rep in (1,2):
    for n in (16,32,64):
        for tag in ("M2","cand-json_array"):
            with Stub({"/v1/models": jbody(ids_doc(["a"*200000]))}) as s:
                reg(R[tag], s.port, n, f"JA-r{rep}-{tag}-rows-{n}")
