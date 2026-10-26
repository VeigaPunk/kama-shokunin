# usage: variant.py <round> <trend> <side> <verdict> <line> <tag> [--summary-disclaim] [--table-extra-col]
import csv, sys, subprocess, os
D="/fast/scratch/hyaku/kama-r44/K2Cheat/lane"
ORDER={"harmed":0,"unchanged":1,"unprovable":2,"unprovable-but-better":3,"improved":4}
rnd,tr,sd,v,ln,tag=sys.argv[1:7]
flags=sys.argv[7:]
base=list(csv.reader(open("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/c2/draft-ledger.tsv"),delimiter="\t"))
hdr,body=base[0],base[1:]
for r in body:
    if r[0]==rnd and r[1]==tr and r[2]==sd:
        r[3]=v; r[7]=ln; r[8]="variant: one line, verdict chosen; not read"
open("/fast/scratch/hyaku/kama-r44/K2Cheat/lane/registry/verdict-ledger.tsv","w").write("\n".join("\t".join(r) for r in [hdr]+body)+"\n")
d={(r[0],r[1],r[2]):r[3] for r in body}
agree=over=under=other=absent=0; mism=[]
for q in range(10,44):
  for t in ("expansion","quality","discernment"):
    s=d.get((str(q),t,"self")); o=d.get((str(q),t,"outside"))
    if s is None or o is None: continue
    if "absent" in (s,o): absent+=1; continue
    if "mixed" in (s,o): other+=1; mism.append((q,t,s,o))
    elif s==o: agree+=1
    elif ORDER[s]>ORDER[o]: over+=1; mism.append((q,t,s,o))
    else: under+=1; mism.append((q,t,s,o))
sc=open("/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md").read().splitlines()
i=sc.index("## Axes"); j=[k for k in range(i,len(sc)) if sc[k].lstrip().startswith("|")][1]
sc.insert(j+1,"| calibration | 7 | `registry/verdict-ledger.tsv` (round-44 C2) | round 44 |")
add=["","### Round-44 calibration ledger",""]
if "--summary-disclaim" in flags:
    add+=["scope note: this table is generated from the ledger by script; no file was read and these figures prove only token consistency.",""]
add+=["| round | trend | self | outside |","|---|---|---|---|"]
add+=[f"| {r} | {t} | {s} | {o} |" + (" fabricated-extra-cell |" if "--table-extra-col" in flags else "") for (r,t,s,o) in mism]
add+=["",f"agreement={agree}/{agree+over+under} overclaim={over} underclaim={under} other={other} absent={absent}",""]
open("/fast/scratch/hyaku/kama-r44/K2Cheat/lane/SCORECARD.md","w").write("\n".join(sc+add)+"\n")
subprocess.run(["git","-C",D,"add","-A"],check=True)
subprocess.run(["git","-C",D,"-c","user.name=r44-k2","-c","user.email=r44-k2@fixture.invalid","commit","-qm",tag],check=True)
tip=subprocess.run(["git","-C",D,"rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
p=subprocess.run([sys.executable,"tools/round44-verdict-ledger-audit.py","--repo",D,"--tip",tip,"--fleet","/home/vgpnk/Projects/shokunin","--out",f"/fast/scratch/hyaku/kama-r44/K2Cheat/out/{tag}.out"],capture_output=True,text=True,cwd=D)
print(f"{tag}: tip={tip} exit={p.returncode}")
print(p.stdout.splitlines()[1])
