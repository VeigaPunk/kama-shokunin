import csv, re, subprocess, collections
LANE="/home/vgpnk/Projects/shokunin/kama-shokunin"
D="/fast/scratch/hyaku/kama-r44/K2Cheat/lane"
FLEET="/home/vgpnk/Projects/shokunin"
FLEET_REV="b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025"
BASE="9d9cc93ec50783cd114829a91757b90d57c78dc6"
TOK=re.compile(r"(expansion|quality|discernment)|(unprovable[- ]but[- ]better)|(unprovable)|(improved|harmed|unchanged)",re.I)
def read_line(line):
    out,cur={},None
    for m in TOK.finditer(line):
        if m.group(1): cur=m.group(1).lower(); continue
        if cur is None: continue
        v="unprovable-but-better" if m.group(2) else "unprovable" if m.group(3) else m.group(4).lower()
        out.setdefault(cur,set()).add(v)
    return out
def show(repo,rev,path):
    p=subprocess.run(["git","-C",repo,"show",f"{rev}:{path}"],capture_output=True,text=True)
    return p.stdout.splitlines() if p.returncode==0 else None
rows=list(csv.DictReader(open(f"{LANE}/.ufo/waves/round-44/c2/draft-ledger.tsv"),delimiter="\t"))
def side(rnd,side):
    return ("fleet",FLEET_REV,f".ufo/reports/round-{rnd}/kama.md") if side=="self" else ("lane",BASE,f"corpus/lessons/round-{rnd}-verifier-spotcheck.md")
NEG=re.compile(r"\bnot\b|\bn't\b|\bno\b|\bnever\b|\bwithout\b|\brather than\b|\bunproven\b|\bcannot\b|\bnot yet\b|\bnot a\b",re.I)
cand_dist=[]; neg=[]; multi=collections.Counter(); absent=0; misses=[]
for r in rows:
    rnd,tr,sd,v=r["round"],r["trend"],r["side"],r["verdict"]
    repo,rev,path=side(rnd,sd)
    text=show(FLEET if repo=="fleet" else D,rev,path)
    if text is None: print("MISSING FILE",path); continue
    cands=[(i+1,x) for i,x in enumerate(text) if tr in read_line(x)]
    dist=collections.Counter(tuple(sorted(read_line(x)[tr])) for _,x in cands)
    if len(cands)>1: multi[len(cands)]+=1
    if v=="absent":
        absent+=1
        print(f"ABSENT {rnd} {tr} {sd} filelines={len(text)} trend_lines={len(cands)}")
        continue
    ln=int(r["line"]); line=text[ln-1]
    others={tuple(sorted(set(read_line(x)[tr]))) for i,x in cands if i!=ln}
    if NEG.search(line): neg.append((rnd,tr,sd,ln,v,line))
    if others and {tuple(sorted(read_line(line)[tr]))} not in others:
        cand_dist.append((rnd,tr,sd,v,ln,line,[(i,sorted(read_line(x)[tr])) for i,x in cands]))
print("multi-candidate files (n candidates -> count):",dict(multi))
print("absent rows:",absent)
print("\nNEGATION-LIKE cited lines:",len(neg))
for x in neg: print("  ",x[0],x[1],x[2],"L"+str(x[3]),x[4],"|",x[5].strip()[:220])
print("\nROWS WHERE THE CITED LINE IS THE ONLY ONE WITH THAT VERDICT (verdict could not be re-read from another line):",len(cand_dist))
for x in cand_dist[:20]: print("  ",x[0],x[1],x[2],"L"+str(x[4]),x[3],"|",x[5].strip()[:160])
