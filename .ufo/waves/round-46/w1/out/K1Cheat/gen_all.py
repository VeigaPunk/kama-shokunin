import importlib.util, re
spec=importlib.util.spec_from_file_location("c","/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round46-release-recheck-audit.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
L="/home/vgpnk/Projects/shokunin/kama-shokunin"; UP="/fast/scratch/hyaku/kama-r46/L1/llama.git"
pop=m.population(m.show(L,m.BASE,m.SOURCES))

def groups(nums):
    ns=sorted(nums); out=[]
    for n in ns:
        if out and n==out[-1][1]+1: out[-1]=(out[-1][0],n)
        else: out.append((n,n))
    fin=[]
    for a,b in out:
        while b-a+1>80: fin.append((a,a+79)); a+=80
        fin.append((a,b))
    return fin

def pad(pt,g):
    a,b=g
    while len(re.sub(r"\s","","".join(pt[a-1:b])))<20 and b<len(pt): b+=1
    return (a,b)

def relocate(pt,rt,g):
    t=m.excerpt(pt,g); n=g[1]-g[0]+1
    for j in range(len(rt)-n+1):
        if m.excerpt(rt,(j+1,j+n))==t: return (j+1,j+n)
    return None

rows=[]; stats={"unchanged-file":0,"holds":0,"holds-reworded":0,"removed":0,"drifted":0}; bad=[]
for sid,e in sorted(pop.items()):
    p=e["path"]; pin=e["pin"]
    pb=m.blob(UP,pin,p); rb=m.blob(UP,m.RELEASE_COMMIT,p)
    pt=(m.show(UP,pin,p) or "").splitlines(); rt=(m.show(UP,m.RELEASE_COMMIT,p) or "").splitlines()
    st,wk=m.cited(e["cells"])
    st={n for n in st if n<=len(pt)}; wk={n for n in wk if n<=len(pt)}
    gr=[pad(pt,g) for g in groups(st)] if st else []
    if not gr:
        gr=[(1,min(5,len(pt)))] if pt else []
    changed="0" if pb==rb else "1"
    PF=m.ws(" ".join(pt)); RF=m.ws(" ".join(rt))
    if changed=="0":
        v="unchanged-file"; rf=",".join(f"{a}-{b}" for a,b in gr); rr=rf; wp=wn="-"; note="-"
    else:
        rel=[relocate(pt,rt,g) for g in gr]
        if all(x is not None for x in rel):
            v="holds"; rf=",".join(f"{a}-{b}" for a,b in gr); rr=",".join(f"{a}-{b}" for a,b in rel); wp=wn="-"; note="-"
        else:
            rrg=[(min(g[0],len(rt)),min(g[1],len(rt))) for g in gr] if rt else []
            if not rt:
                # path absent at release
                v="removed"; rf=",".join(f"{a}-{b}" for a,b in gr); rr=",".join("-" for _ in gr); wp=wn="-"; note="-"
            else:
                P=m.ws(" ".join(" ".join(pt[a-1:b]) for a,b in gr)); R=m.ws(" ".join(" ".join(rt[a-1:b]) for a,b in rrg))
                wp=next((m.ws(x) for a,b in gr for x in pt[a-1:b] if len(m.ws(x))>=12 and m.ws(x) in P and m.ws(x) not in RF),None)
                wn=next((m.ws(x) for a,b in rrg for x in rt[a-1:b] if len(m.ws(x))>=12 and m.ws(x) in R and m.ws(x) not in PF),None)
                if not (wp and wn):
                    bad.append(sid); continue
                v="holds-reworded"; rf=",".join(f"{a}-{b}" for a,b in gr); rr=",".join(f"{a}-{b}" for a,b in rrg)
                note="auto-filled from the diff: witness lines are picked, no reader classified the hunk."
    stats[v]+=1
    rows.append("\t".join([sid,p,pin,m.RELEASE,pb,rb,changed,rf,rr,wp,wn,v,note]))
hdr="\t".join(m.HEADER)
open("ledger-all.tsv","w").write(hdr+"\n"+"\n".join(rows)+"\n")
print(stats, "rows",len(rows),"bad",bad)
