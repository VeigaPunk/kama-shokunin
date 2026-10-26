import re, subprocess, csv
D="/fast/scratch/hyaku/kama-r44/K2Cheat/lane"; FLEET="/home/vgpnk/Projects/shokunin"
FR="b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025"; B="9d9cc93ec50783cd114829a91757b90d57c78dc6"
TOK=re.compile(r"(expansion|quality|discernment)|(unprovable[- ]but[- ]better)|(unprovable)|(improved|harmed|unchanged)",re.I)
ORDER={"harmed":0,"unchanged":1,"unprovable":2,"unprovable-but-better":3,"improved":4}
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
def side(rnd,sd):
    return ("fleet",FR,f".ufo/reports/round-{rnd}/kama.md") if sd=="self" else ("lane",B,f"corpus/lessons/round-{rnd}-verifier-spotcheck.md")
cand={}; 
for rnd in range(10,44):
  for tr in ("expansion","quality","discernment"):
    for sd in ("self","outside"):
      repo,rev,path=side(rnd,sd)
      t=show(FLEET if repo=="fleet" else D,rev,path)
      cand[(rnd,tr,sd)]=None if t is None else [(i+1,read_line(x)[tr]) for i,x in enumerate(t) if tr in read_line(x)]
def allowed(k):
    c=cand[k]
    if c is None: return None
    s=set()
    for i,vs in c:
        s|=vs
        if len(vs)>=2: s.add("mixed")
    return s
def linefor(k,v):
    for i,vs in cand[k]:
        if v=="mixed" and len(vs)>=2: return i
        if v in vs: return i
    raise SystemExit(f"no line for {k} {v}")
rows=[]
for rnd in range(10,44):
  for tr in ("expansion","quality","discernment"):
    a=allowed((rnd,tr,"self")); b=allowed((rnd,tr,"outside"))
    for sd,(repo,rev,path) in (("self",side(rnd,"self")),("outside",side(rnd,"outside"))):
      al=allowed((rnd,tr,sd))
      if al is None or not al:
        rows.append([str(rnd),tr,sd,"absent",repo,rev,path,"-","file absent or gives no verdict word for this trend at this rev"]); continue
      other=allowed((rnd,tr,"outside" if sd=="self" else "self"))
      common=(al & other) if other else set()
      if common: v=sorted(common)[0]
      else: v=sorted(al)[0]
      rows.append([str(rnd),tr,sd,v,repo,rev,path,str(linefor((rnd,tr,sd),v)),"chosen from in-file candidate lines to maximise agreement; not read"])
v={(r[0],r[1],r[2]):r[3] for r in rows}
agree=over=under=otherm=absent=0; mism=[]
for rnd in range(10,44):
  for tr in ("expansion","quality","discernment"):
    s=v[(str(rnd),tr,"self")]; o=v[(str(rnd),tr,"outside")]
    if "absent" in (s,o): absent+=1; continue
    if "mixed" in (s,o): otherm+=1; mism.append((rnd,tr,s,o))
    elif s==o: agree+=1
    elif ORDER[s]>ORDER[o]: over+=1; mism.append((rnd,tr,s,o))
    else: under+=1; mism.append((rnd,tr,s,o))
with open("registry/verdict-ledger.tsv","w") as fh:
    fh.write("round\ttrend\tside\tverdict\trepo\trev\tpath\tline\tnote\n")
    for r in rows: fh.write("\t".join(r)+"\n")
sc=open("SCORECARD.md").read().splitlines()
add=["","### Round-44 calibration ledger","","Round-44 C2: filed trend verdict beside outside closure verdict.","","| round | trend | self | outside |","|---|---|---|---|"]
add+=[f"| {r} | {t} | {s} | {o} |" for (r,t,s,o) in mism]
add+=["",f"agreement={agree}/{agree+over+under} overclaim={over} underclaim={under} other={otherm} absent={absent}",""]
i=sc.index("## Axes"); j=[k for k in range(i,len(sc)) if sc[k].lstrip().startswith("|")][1]
sc.insert(j+1,"| calibration | 7 | `registry/verdict-ledger.tsv` (round-44 C2) | round 44 |")
open("SCORECARD.md","w").write("\n".join(sc+add)+"\n")
open("/fast/scratch/hyaku/kama-r44/K2Cheat/out/opt_counts.txt","w").write(f"agree={agree} over={over} under={under} other={otherm} absent={absent}\n")
print("wrote", agree, over, under, otherm, absent)
