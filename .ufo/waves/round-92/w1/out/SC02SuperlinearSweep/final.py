import sys, time, shutil
from pathlib import Path
sys.path.insert(0,"/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
from harness import Stub, Runner, ids_doc, jbody, uptime_str
S=Path("/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
def reg(runner, port, nrows, json_out, label, kill=120):
    d=S/"rows"
    if d.exists(): shutil.rmtree(d)
    d.mkdir(parents=True)
    pin=d/"pin.txt"; pin.write_text(f"http://127.0.0.1:{port}/v1\n")
    regf=d/"registry.tsv"
    L=["id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes"]
    for i in range(nrows): L.append(f"row{i}\t{pin}\tgrep:http://[^ ]+\thttp://127.0.0.1:{port}/v1\ta\tr")
    regf.write_text("\n".join(L)+"\n")
    hist=d/"history"
    args=["check","--registry",str(regf),"--history",str(hist),"--timeout","5","--connect-timeout","2"]
    if json_out: args.insert(1,"--json")
    rc,so,se,dt=runner.run(args,kill=kill)
    print(f"{label:<50} rc={rc} t={dt:7.2f}s out={len(so)}B {uptime_str()}", flush=True)
    return dt
R={k:Runner(S,(S/f).read_bytes(),k) for k,f in
   {"M2":"probe-M2.sh","cand-json_array":"cand-json_array.sh","cand-print_table":"cand-print_table.sh"}.items()}
print("=== print_table (NON-json check path) ===", flush=True)
for tag in ("M2","cand-print_table"):
    for n in (16,32,64):
        with Stub({"/v1/models": jbody(ids_doc(["a"*200000]))}) as s:
            reg(R[tag], s.port, n, False, f"PT-{tag}-nonjson-rows-{n}")
print("=== json_array repeat x2 (json path) ===", flush=True)
for rep in (1,2):
    for tag in ("M2","cand-json_array"):
        for n in (32,64):
            with Stub({"/v1/models": jbody(ids_doc(["a"*200000]))}) as s:
                reg(R[tag], s.port, n, True, f"JA{rep}-{tag}-json-rows-{n}")
