import re,subprocess,csv,sys
D="/fast/scratch/hyaku/kama-r44/K2Cheat/lane"; F="/home/vgpnk/Projects/shokunin"
FR="b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025"; B="9d9cc93ec50783cd114829a91757b90d57c78dc6"
ORDER={"harmed":0,"unchanged":1,"unprovable":2,"unprovable-but-better":3,"improved":4}
TOK=re.compile(r"(expansion|quality|discernment)|(unprovable[- ]but[- ]better)|(unprovable)|(improved|harmed|unchanged)",re.I)
def seq(line,tr):
    out=[];cur=None
    for m in TOK.finditer(line):
        if m.group(1): cur=m.group(1).lower(); continue
        if cur!=tr: continue
        out.append("unprovable-but-better" if m.group(2) else "unprovable" if m.group(3) else m.group(4).lower())
    return out
def show(repo,rev,path):
    p=subprocess.run(["git","-C",repo,"show",f"{rev}:{path}"],capture_output=True,text=True)
    return p.stdout.splitlines() if p.returncode==0 else None
rows=list(csv.reader(open("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/c2/draft-ledger.tsv"),delimiter="\t"))
changed=0
for r in rows[1:]:
    if r[3]=="absent": continue
    repo,rev,path=(("fleet",FR,f".ufo/reports/round-{r[0]}/kama.md") if r[2]=="self" else ("lane",B,f"corpus/lessons/round-{r[0]}-verifier-spotcheck.md"))
    t=show(F if repo=="fleet" else D,rev,path); s=seq(t[int(r[7])-1],r[1])
    if s and s[0]!=r[3]: changed+=1; r[3]=s[0]; r[8]="headline reading (first verdict word on the cited line)"
open(D+"/registry/verdict-ledger.tsv","w").write("\n".join("\t".join(r) for r in rows)+"\n")
d={(r[0],r[1],r[2]):r[3] for r in rows[1:]}
agree=over=under=other=absent=0; mism=[]
for q in range(10,44):
  for t in ("expansion","quality","discernment"):
    s=d[(str(q),t,"self")]; o=d[(str(q),t,"outside")]
    if "absent" in (s,o): absent+=1; continue
    if "mixed" in (s,o): other+=1; mism.append((q,t,s,o))
    elif s==o: agree+=1
    elif ORDER[s]>ORDER[o]: over+=1; mism.append((q,t,s,o))
    else: under+=1; mism.append((q,t,s,o))
sc=open("/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md").read().splitlines()
i=sc.index("## Axes"); j=[k for k in range(i,len(sc)) if sc[k].lstrip().startswith("|")][1]
sc.insert(j+1,"| calibration | 7 | `registry/verdict-ledger.tsv` (round-44 C2) | round 44 |")
add=["","### Round-44 calibration ledger","","| round | trend | self | outside |","|---|---|---|---|"]
add+=[f"| {r} | {t} | {s} | {o} |" for (r,t,s,o) in mism]
add+=["",f"agreement={agree}/{agree+over+under} overclaim={over} underclaim={under} other={other} absent={absent}",""]
open(D+"/SCORECARD.md","w").write("\n".join(sc+add)+"\n")
subprocess.run(["git","-C",D,"add","-A"],check=True)
subprocess.run(["git","-C",D,"-c","user.name=r44-k2","-c","user.email=r44-k2@fixture.invalid","commit","-qm","K2Cheat: headline reading of the draft"],check=True)
tip=subprocess.run(["git","-C",D,"rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
p=subprocess.run([sys.executable,"tools/round44-verdict-ledger-audit.py","--repo",D,"--tip",tip,"--fleet",F,"--out","/fast/scratch/hyaku/kama-r44/K2Cheat/out/headline.out"],capture_output=True,text=True,cwd=D)
print("changed rows:",changed,"exit",p.returncode); print(p.stdout.splitlines()[1])
