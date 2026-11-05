import subprocess,sys,re,collections,json
LANE="/home/vgpnk/Projects/shokunin/kama-shokunin"
def rows(rev):
    txt=subprocess.check_output(["git","-C",LANE,"show",f"{rev}:corpus/SOURCES.md"],text=True)
    out={}
    in_reg=False
    for line in txt.splitlines():
        if line.startswith("## "):
            in_reg = line.strip()=="## Registry"
            continue
        if in_reg and re.match(r"^\| S[0-9]{3} \|",line):
            cells=[c.strip() for c in line.strip().strip("|").split(" | ")]
            # split on ' | ' may break cells containing ' | '; check counts
            out[cells[0]]=cells
    return out
B=rows("3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d"); T=rows("bafae7afb41843564ac2468d28beb8e0bb98e8e6")
def summ(d):
    tiers=collections.Counter(c[3] for c in d.values())
    st=collections.Counter(c[7] for c in d.values())
    lens=collections.Counter(len(c) for c in d.values())
    return dict(rows=len(d),tiers=dict(sorted(tiers.items())),status=dict(sorted(st.items())),cellcounts=dict(lens))
print("BASE",json.dumps(summ(B)))
print("TIP ",json.dumps(summ(T)))
added=[k for k in T if k not in B]; removed=[k for k in B if k not in T]
print("added",added,[T[k][3]+"/"+T[k][7] for k in added]); print("removed",removed)
changed=[]
for k in B:
    if k in T and B[k]!=T[k]:
        diffs=[(i,B[k][i],T[k][i]) for i in range(min(len(B[k]),len(T[k]))) if B[k][i]!=T[k][i]]
        changed.append((k,len(B[k]),len(T[k]),[(i, x[:80], y[:80]) for i,x,y in diffs]))
print("changed",len(changed)); [print(c) for c in changed]
# S-id gaps / duplicates
import itertools
print("dup ids base", len(B)!=len(list(B)))
