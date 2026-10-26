import re, importlib.util
spec = importlib.util.spec_from_file_location("c1", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round46-release-recheck-audit.py")
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)
text = open("/fast/scratch/hyaku/kama-r46/K1Pop/SOURCES.base.md").read()
pop = c1.population(text)
ROWL = re.compile(r"^(\s*)\|\s*(S\d+)\s*\|")
rows=[]
for ln,line in enumerate(text.splitlines(),1):
    m=ROWL.match(line)
    if m: rows.append((ln,line,c1.cells(line)))
print("rows",len(rows),"pop",len(pop))
print("cells!=11:",[ (ln,c[0]) for ln,_,c in rows if len(c)!=11][:20])
# URL in cell1 vs cell5
for ln,line,c in rows:
    if len(c)<11: continue
    u1=c1.URL.search(c[1]); u5=c1.URL.search(c[5]) if len(c)>5 else None
    if u5 and not u1:
        print("URL-IN-ANCHOR-ONLY", c[0], "inpop" if c[0] in pop else "OUT", u5.group(1) or u5.group(3), u5.group(2) or u5.group(4))
# llama.cpp mentions anywhere in the line (broad), with classification
print("--- broad llama.cpp mentions outside pop ---")
for ln,line,c in rows:
    if c[0] in pop: continue
    L=line
    if re.search(r"llama\.cpp|llama-server|llama_build|build_info", L):
        u=c1.URL.search(L)
        print(c[0], "cells=%d"%len(c), "tier=%s"%c[3], "status=%s"%c[7], "recheck=%s"%c[9],
              "url=%s"%((u.group(1) or u.group(3)) if u else "-"), "| teaches:", c[6][:90])
