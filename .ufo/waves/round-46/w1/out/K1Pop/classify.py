import re, sys, json, importlib.util
spec = importlib.util.spec_from_file_location("c1", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round46-release-recheck-audit.py")
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)
text = open("/fast/scratch/hyaku/kama-r46/K1Pop/SOURCES.base.md").read()
pop = c1.population(text)
print("population size", len(pop))
# Any line with an S id and at least 2 pipes
ROWL = re.compile(r"^(\s*)\|\s*(S\d+)\s*\|")
URLANY = re.compile(r"https://(?:github\.com/ggml-org/llama\.cpp/(?:blob|tree)/([\w.\-]+)/([^\s`;,)|]+)|raw\.githubusercontent\.com/ggml-org/llama\.cpp/([\w.\-]+)/([^\s`;,)|]+))")
out=[]
for ln,line in enumerate(text.splitlines(),1):
    m = ROWL.match(line)
    if not m: 
        # maybe llama.cpp url but no S row start
        if "llama.cpp/blob" in line or "llama.cpp/tree" in line or "llama.cpp/pull" in line or "llama.cpp/commit" in line or "llama.cpp/releases" in line:
            print("NON-S-ROW", ln, line[:160])
        continue
    c = c1.cells(line)
    sid = m.group(2)
    m2 = URLANY.search(line)
    if not m2: continue
    ref, path = (m2.group(1), m2.group(2)) if m2.group(1) else (m2.group(3), m2.group(4))
    path = path.split("#")[0]
    reasons=[]
    if len(c)!=11: reasons.append(f"cells={len(c)}")
    if len(c)>=11:
        recheck=c[9]; status=c[7]
        if recheck!="on-release": reasons.append(f"recheck={recheck}")
        if status not in ("mined","queued"): reasons.append(f"status={status}")
    if not c1.HEX40.fullmatch(ref):
        if len(c)>5 and c1.HEX40.search(c[5]): pass
        else: reasons.append(f"ref={ref[:20]} no-40hex-anchor")
    if len(m.group(1))>3: reasons.append(f"indent={len(m.group(1))}")
    if not m.group(0).startswith(m.group(1)+"|"): pass
    if not re.fullmatch(r"S\d{3,}", sid): reasons.append("id-shape")
    inseg = sid in pop
    out.append({"line":ln,"id":sid,"ref":ref,"path":path,"reasons":reasons,"in_pop":inseg,
                "cells":c if len(c)<=14 else c[:8]})
print("== rows citing llama.cpp subtree but OUTSIDE population ==")
n=0
for r in out:
    if r["in_pop"]: continue
    n+=1
    print(json.dumps({k:r[k] for k in ("line","id","ref","path","reasons","id" in [] and 0 or "cells")}, ensure_ascii=False))
print("outside:",n,"total-citing:",len(out))
