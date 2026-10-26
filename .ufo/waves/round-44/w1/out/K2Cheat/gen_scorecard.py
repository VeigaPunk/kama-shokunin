# lazy integrator: derive SCORECARD disagreement table from the ledger rows themselves
import csv, sys
ORDER = {"harmed":0,"unchanged":1,"unprovable":2,"unprovable-but-better":3,"improved":4}
rows = list(csv.DictReader(open("registry/verdict-ledger.tsv"), delimiter="\t"))
v = {(r["round"], r["trend"], r["side"]): r["verdict"] for r in rows}
agree=over=under=other=absent=0; mism=[]
for rnd in range(10,44):
    for tr in ("expansion","quality","discernment"):
        s=v.get((str(rnd),tr,"self")); o=v.get((str(rnd),tr,"outside"))
        if s is None or o is None: continue
        if "absent" in (s,o): absent+=1; continue
        if "mixed" in (s,o): other+=1; mism.append((rnd,tr,s,o))
        elif s==o: agree+=1
        elif ORDER[s]>ORDER[o]: over+=1; mism.append((rnd,tr,s,o))
        else: under+=1; mism.append((rnd,tr,s,o))
out=["","### Round-44 calibration ledger","","Round-44 C2: the lane's filed trend verdict beside the outside closure's verdict.","","| round | trend | self | outside |","|---|---|---|---|"]
out += [f"| {r} | {t} | {s} | {o} |" for (r,t,s,o) in mism]
out += ["", f"agreement={agree}/{agree+over+under} overclaim={over} underclaim={under} other={other} absent={absent}", ""]
open("SCORECARD.md","a").write("\n".join(out))
sc=open("SCORECARD.md").read().splitlines()
i=sc.index("## Axes")
# insert a row naming the ledger into the Axes table, immediately after the header separator
j=[k for k in range(i,len(sc)) if sc[k].lstrip().startswith("|")][1]
sc.insert(j+1,"| calibration | 7 | `registry/verdict-ledger.tsv` (round-44 C2) | round 44 |")
open("SCORECARD.md","w").write("\n".join(sc)+"\n")
