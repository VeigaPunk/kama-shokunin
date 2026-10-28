import re,sys
sc=open("SCORECARD.md",encoding="utf-8").read().split("\n")
pv=open("PROVINCE.md",encoding="utf-8").read()
i=max(i for i,l in enumerate(sc) if re.search(r"canonical list as of round\s+63\*\*",l))
rows=[]
for l in sc[i+1:]:
    if l.startswith("|"):
        rows.append([c.strip() for c in l.strip().strip("|").split("|")])
    elif rows: break
rows=rows[2:]
print("canon rows:",len(rows))
for r in rows:
    toks=re.findall(r"`([^`]+)`",r[2])
    for t in toks:
        if t.startswith(("tools/","registry/")):
            print(f"{r[0]:34s} {t:44s} in_PROVINCE={t in pv}")
