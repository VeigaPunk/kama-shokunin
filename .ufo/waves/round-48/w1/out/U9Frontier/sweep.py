import re,sys,importlib.util
spec=importlib.util.spec_from_file_location("c","/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round46-release-recheck-audit.py")
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
base=open("/fast/scratch/hyaku/kama-r48/U9Frontier/SOURCES.380.md").read()
import subprocess
b0=subprocess.run(["git","-C","/home/vgpnk/Projects/shokunin/kama-shokunin","show","0163fea2:corpus/SOURCES.md"],capture_output=True,text=True).stdout
pop0=c.population(b0); pop1=c.population(base)
print(type(pop0), len(pop0), len(pop1))
ids=lambda p:[ (x[0] if isinstance(x,(tuple,list)) else (x['id'] if isinstance(x,dict) else x)) for x in (p.values() if isinstance(p,dict) else p)]
try:
    s0=set(p if isinstance(p,str) else p for p in (pop0.keys() if isinstance(pop0,dict) else map(lambda x:x[0],pop0)))
    s1=set(pop1.keys() if isinstance(pop1,dict) else map(lambda x:x[0],pop1))
except Exception as e: print(e); sys.exit()
print("in pop at 380 not at base:",sorted(s1-s0)); print("in base not 380:",sorted(s0-s1))
# rows citing llama.cpp elsewhere
LL=re.compile(r"ggml-org/llama\.cpp|llama\.cpp|b119\d\d|b11755|b11889")
for ln,l in enumerate(base.splitlines(),1):
    m=c.ROW.match(l)
    if not m: continue
    sid=m.group(1)
    if sid in s1: continue
    cs=c.cells(l)
    if len(cs)<11: continue
    src=cs[1]+" "+cs[5]
    if re.search(r"ggml-org/llama\.cpp|raw\.githubusercontent\.com/ggml-org/llama|llama\.cpp b1|llama-b1|b11\d{3}",l):
        print(sid,ln,cs[2],cs[3],cs[7],cs[9],"|",cs[1][:110])
