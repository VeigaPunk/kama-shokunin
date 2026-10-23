import json, shutil, subprocess, sys, re, hashlib
from pathlib import Path
S = Path(sys.argv[1]); base = S/"tip"
R = ".ufo/waves/round-25/final/context-capacity-receipt.json"
def run(name, mut_receipt=None, mut_tree=None):
    t = S/"c2m"/name
    if t.exists(): shutil.rmtree(t)
    shutil.copytree(base, t)
    d = json.load(open(t/R))
    if mut_receipt: mut_receipt(d)
    json.dump(d, open(t/R,"w"), indent=1)
    if mut_tree: mut_tree(t)
    p = subprocess.run([sys.executable, ".ufo/waves/round-25/count-c2.py"], cwd=t, capture_output=True, text=True)
    print(f"{name:28s} exit={p.returncode} :: {p.stdout.strip()} {p.stderr.strip()[:120]}")
def cell(d, i): return [c for c in d["cells"] if c["id"]==i][0]
raw = lambda t: t/".ufo/waves/round-25/final/raw"
# registered five (MutationC2Receipts)
run("control-unmutated")
run("raw-bytes", mut_tree=lambda t: (raw(t)/"K1.health.body").write_text((raw(t)/"K1.health.body").read_text().replace("ok","no")))
def rs(d): c=cell(d,"K1"); v=c["raw"]["raw_health"]; c["raw"]["raw_health"]=("b" if v[0]!="b" else "c")+v[1:]
run("raw-sha", rs)
run("raw-deleted", mut_tree=lambda t: (raw(t)/"K1.health.body").unlink())
def re_(d): cell(d,"K1")["raw"]=[]
run("raw-empty", re_)
def rc(d): cell(d,"K1")["raw"]=dict(cell(d,"K2")["raw"])
run("raw-cross-cell", rc)
# new mutants
def drop(d):
    for c in d["cells"]:
        c["raw"]={"raw_health": c["raw"]["raw_health"]}
run("N1-drop-4-of-5-raw-keys", drop)
def alias(d):
    c=cell(d,"K1"); c["raw"]={"anything": cell(d,"K2")["raw"]["server_log"]}
run("N2-K1-unregistered-key-K2hash", alias)
def pool(d):
    c=cell(d,"K5"); old=c["kv_pool_n_ctx"]; new=old*2
    c["kv_pool_n_ctx"]=new
    c["log_lines"]=[re.sub(r"(llama_context: n_ctx +=  ?)%d\s*$"%old, lambda m: m.group(1)+str(new), x) for x in c["log_lines"]]
    c["props_n_ctx"]=c["props_n_ctx"]*2
run("N3-K5-pool-x2-fields-only", pool)
def l2(d):
    c=cell(d,"L2"); 
    for q in c["requests"]: q["status"]=200
run("N4-L2-status-200-fields", l2)
def unify(d):
    c=cell(d,"K2"); c["log_lines"]=[x.replace("kv_unified = 'false'","kv_unified = 'true'") for x in c["log_lines"]]
run("N5-K2-kv_unified-flipped", unify)
