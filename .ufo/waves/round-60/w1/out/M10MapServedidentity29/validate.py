import importlib.util, json, subprocess, sys, os
LANE="/home/vgpnk/Projects/shokunin/kama-shokunin"
spec=importlib.util.spec_from_file_location("m", LANE+"/tools/round60-c2-counter.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
receipt=open(LANE+"/.ufo/waves/round-60/live/receipt.json").read()
caps,ok=m.receipt_caps(receipt)
print("receipt_caps ok=",ok, "keys=",sorted(caps))
base=subprocess.run(["git","-C",LANE,"show",m.BASE+":corpus/knowledge/served-identity-crosswalk.md"],capture_output=True,text=True).stdout
lines=base.split("\n")
line29=lines[28]
print("line29 len=",len(line29),"starts=",line29[:60])
rows=[l for l in open(LANE+"/.ufo/waves/round-60/w1/out/M10MapServedidentity29/rows.tsv").read().split("\n") if l.strip()]
pop=m.population(LANE, m.BASE)
print("pop line29 present:", ("corpus/knowledge/served-identity-crosswalk.md",29) in pop, "pop size=",len(pop))
for r in rows:
    cols=r.split("\t")
    assert len(cols)==8, cols
    rid,path,ln,quote,pred,verdict,obs,reason=cols
    key=(path,int(ln))
    assert key==("corpus/knowledge/served-identity-crosswalk.md",29), key
    q=quote.strip(); nq=len(q.split())
    print(rid,"words=",nq,"substr=",q in pop[key], "verdict=",verdict)
    assert 3<=nq<=25 and q in pop[key]
    if verdict=="not-observable":
        assert pred.strip()=="" and len(reason.strip())>=20
        print("   not-observable reason ok")
        continue
    tree=m.safe_compile(pred)
    ev=m.evaluate(tree,caps); fa=m.falsifiable(tree,caps)
    print("   evaluate=",ev,"falsifiable=",fa)
    assert fa is True, rid
    assert ev == (verdict=="confirmed"), (rid,ev,verdict)
reg=open(LANE+"/.ufo/waves/round-60/w1/out/M10MapServedidentity29/rows.tsv").read()
sc=m.score(pop, reg, receipt, "")
print("score:", {k:sc[k] for k in ("covered","evaluated","eval_lines","sensitive","bound","contradicted","amended","receipt_ok","good_rows","errors","met")})
