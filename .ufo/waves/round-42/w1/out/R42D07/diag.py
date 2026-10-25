import hashlib, importlib.util, os, random, shutil, sys
SEAT="/fast/scratch/kama-r42/seats/R42D07"
spec=importlib.util.spec_from_file_location("c2ctr", f"{SEAT}/clone/tools/round42-digest-audit.py")
c2=importlib.util.module_from_spec(spec); spec.loader.exec_module(c2)
rng=random.Random(42)
for i in range(c2.CASES):
    d=f"{SEAT}/tmp/diag-{i}"; shutil.rmtree(d,ignore_errors=True); os.makedirs(d)
    c2.make_case(rng,d,i)
    want=c2.ref_dir(d)
    payloads=[f for f in sorted(os.listdir(d)) if f.startswith("data")]
    led={}
    lp=os.path.join(d,c2.LEDGER)
    if os.path.isfile(lp): led=c2.parse_ledger(open(lp).read())
    comp=[(k[:8],v["cls"],bool(v["path"]),v["note"][:6],v["correct"][:8]) for k,v in sorted(led.items())]
    print(f"case{i}: payloads={payloads} want={c2.summary(want)} exit={c2.exit_of(want)} ledger={comp}")
