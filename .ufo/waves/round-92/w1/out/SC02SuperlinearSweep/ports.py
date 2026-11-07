import sys, time, json
from pathlib import Path
sys.path.insert(0,"/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
from harness import Stub, Runner, ids_doc, jbody, uptime_str
S=Path("/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep")
R=Runner(S,(S/"probe-M2.sh").read_bytes(),"M2")
RB=Runner(S,(S/"probe-BASE.sh").read_bytes(),"BASE")
def run(nports, payload, tag, runner):
    stubs=[Stub({"/v1/models": jbody(ids_doc(["a"*payload]))}) for _ in range(nports)]
    try:
        # probe lists real listeners only; instead drive cmd_listeners with --port? no:
        # use `check` per port is O(n) but json_array is only used in listeners/consumers/check-json.
        # Here: run `listeners --json` is host-driven; emulate with `consumers`? Use check --json on a
        # registry with nports rows -> each row a different port.
        d=S/"ports"; d.mkdir(exist_ok=True)
        pin=d/"pin.txt"
        regf=d/"registry.tsv"
        L=["id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes"]
        for i,s in enumerate(stubs):
            pin.write_text(f"http://127.0.0.1:{s.port}/v1\n")
            L.append(f"row{i}\t{pin}\tgrep:http://[^ ]+\thttp://127.0.0.1:{s.port}/v1\ta\tr")
        regf.write_text("\n".join(L)+"\n")
        hist=d/"history"
        rc,so,se,dt=runner.run(["check","--json","--registry",str(regf),"--history",str(hist),
                                 "--timeout","5","--connect-timeout","2"],kill=300)
        nrows=so.count(b'"id": "row')
        print(f"{tag} ports={nports} payload={payload} rc={rc} t={dt:7.2f}s out={len(so)}B rows={nrows} {uptime_str()}", flush=True)
    finally:
        for s in stubs: s.__exit__()
for nports in (16,32,64):
    run(nports, 200000, "PORTS-M2", R)
