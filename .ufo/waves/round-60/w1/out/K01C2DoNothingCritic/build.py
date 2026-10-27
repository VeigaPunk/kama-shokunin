import importlib.util, json, sys
R="/home/vgpnk/Projects/shokunin/kama-shokunin"
sp=importlib.util.spec_from_file_location("c2",R+"/tools/round60-c2-counter.py"); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
pop=m.population(R,m.BASE)
receipt=m.blob(R,"HEAD",m.RECEIPT)
for k,v in sorted(pop.items()): print(k, len(v.split()), repr(v[:110]))
# predicates: each reads one capture field vs a literal copied from receipt
PREDS=["c['version']['version'] == '0.40.11'","c['ps-before']['models'] == []","c['tags-empty']['models'] == []","c['v1-model-single']['object'] == 'model'","c['generate']['done'] == True"]
keys=sorted(pop)
rows=[]
def quote(line):
    w=line.split()
    for n in range(8,2,-1):
        for s in range(0,max(1,len(w)-n+1)):
            q=" ".join(w[s:s+n])
            if q in line: return q
    return None
for i,k in enumerate(keys):
    q=quote(pop[k]); assert q and 3<=len(q.split())<=25
    if i<5: row=[f"D{i}",k[0],str(k[1]),q,PREDS[i],"confirmed","",""]
    else: row=[f"D{i}",k[0],str(k[1]),q,"","not-observable","","not observable in this capture set"]
    rows.append(row)
text="id\tpath\tline\tquote\tpredicate\tverdict\tobserved\treason\n"+"".join("\t".join(r)+"\n" for r in rows)
open("registry.tsv","w").write(text)
s=m.score(pop,text,receipt,"")
print(s)
print(m.controls(pop,text,receipt,""))
