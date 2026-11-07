import sys
from pathlib import Path
sys.path.insert(0,"/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
from harness import Stub, Runner, ids_doc, jbody, uptime_str
S=Path("/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
R={k:Runner(S,(S/f).read_bytes(),k) for k,f in
   {"M2":"probe-M2.sh","cand-print_table":"cand-print_table.sh"}.items()}
def run(runner, nwide, nnarrow, payload, label):
    w=Stub({"/v1/models": jbody(ids_doc(["a"*payload]))})
    n=Stub({"/v1/models": jbody(ids_doc(["tiny"]))})
    try:
        d=S/"mixed2"
        if d.exists():
            for p in d.rglob("*"): p.unlink()
        d.mkdir(parents=True, exist_ok=True)
        regf=d/"registry.tsv"
        L=["id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes"]
        for i in range(nwide):
            f=d/f"w{i}.txt"; f.write_text(f"http://127.0.0.1:{w.port}/v1\n")
            L.append(f"wide{i}\t{f}\tgrep:http://[^ ]+\thttp://127.0.0.1:{w.port}/v1\ta\tr")
        for i in range(nnarrow):
            f=d/f"n{i}.txt"; f.write_text(f"http://127.0.0.1:{n.port}/v1\n")
            L.append(f"nar{i}\t{f}\tgrep:http://[^ ]+\thttp://127.0.0.1:{n.port}/v1\ta\tr")
        regf.write_text("\n".join(L)+"\n")
        hist=d/"history"
        rc,so,se,dt=runner.run(["check","--registry",str(regf),"--history",str(hist),
                                 "--timeout","5","--connect-timeout","2"],kill=300)
        print(f"{label:<44} rc={rc} t={dt:7.2f}s out={len(so)}B {uptime_str()}", flush=True)
    finally:
        w.__exit__(); n.__exit__()
for tag in ("M2","cand-print_table"):
    run(R[tag], 1, 7, 200000, f"MIX2-{tag}-1wide-7narrow")
