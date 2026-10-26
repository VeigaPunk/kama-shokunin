import re, json, importlib.util
spec = importlib.util.spec_from_file_location("c1", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round46-release-recheck-audit.py")
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)
text = open("/fast/scratch/hyaku/kama-r46/K1Pop/SOURCES.base.md").read()
pop = c1.population(text)
ROWL = re.compile(r"^(\s*)\|\s*(S\d+)\s*\|")
rows=[]
for ln,line in enumerate(text.splitlines(),1):
    m = ROWL.match(line)
    if not m: continue
    c = c1.cells(line)
    rows.append({"ln":ln,"id":m.group(2),"indent":len(m.group(1)),"ncells":len(c),"line":line,"c":c})
print("total S-rows", len(rows), "pop", len(pop))
# Which rows mention llama.cpp at all
def cells_of(r):
    return r["c"]
sel=[]
for r in rows:
    L=r["line"]
    mentions_llama = "llama.cpp" in L or "llama-server" in L or "llamacpp" in L.lower()
    if not mentions_llama: continue
    # does it cite a FILE (blob/tree/raw) at a ref?
    m2 = c1.URL.search(L)
    rel = re.findall(r"llama\.cpp/releases/tag/([\w.\-]+)", L)
    pr = re.findall(r"llama\.cpp/(?:pull|commit|issues)/(\d+|[0-9a-f]{7,40})", L)
    sel.append((r["id"], r["ln"], r["indent"], r["ncells"], r["c"][7] if len(r["c"])>7 else "?", r["c"][9] if len(r["c"])>9 else "?", r["c"][3] if len(r["c"])>3 else "?",
                (m2.group(1) or m2.group(3)) if m2 else None, (m2.group(2) or m2.group(4)) if m2 else None, rel, pr, r["id"] in pop))
print()
for s in sel:
    print("\t".join(str(x) for x in s))
