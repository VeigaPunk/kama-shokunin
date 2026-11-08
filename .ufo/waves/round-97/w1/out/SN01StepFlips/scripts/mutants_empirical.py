"""Empirical verdicts of the REAL probe under three probe variants, on the six C3 shapes.

  honest   : HEAD bytes
  plus1    : +1 step charged per tensor header (header cost 6+nd instead of 5+nd)
  pre1     : +1 preamble step (preamble 5 instead of 4)
Each shape is graded on famA (malformed: no data section) AND famC (well-formed: real data).
"""
import re, subprocess, time, struct, json
from pathlib import Path
LANE="/home/vgpnk/Projects/shokunin/kama-shokunin"
S=Path("/fast/scratch/hyaku/kama-r97/SN01StepFlips")
src=subprocess.run(["git","-C",LANE,"show","HEAD:tools/kama-probe.sh"],capture_output=True,text=True).stdout

def build(base):
    py=re.search(r"^ROUTER_PY=\$\(cat <<'PY'\n(.*?)^PY$",base,re.S|re.M).group(1)
    a="                skip(u64())  # name\n"
    assert py.count(a)==1
    py=py.replace(a,a+"                need(1)  # MUTANT +1 per header\n")
    py=py.replace('        except Unknown:\n            return "-"','        except Unknown as e:\n            return "-:"+str(e)\n')
    py=py.replace('            return "ok"\n','            return "ok:steps="+str(steps[0])\n')
    return py

def build_pre(base):
    py=re.search(r"^ROUTER_PY=\$\(cat <<'PY'\n(.*?)^PY$",base,re.S|re.M).group(1)
    a='        try:\n            if rd(4) != b"GGUF":\n'
    assert py.count(a)==1
    py=py.replace(a,'        try:\n            need(1)  # MUTANT preamble+1\n            if rd(4) != b"GGUF":\n')
    py=py.replace('        except Unknown:\n            return "-"','        except Unknown as e:\n            return "-:"+str(e)\n')
    py=py.replace('            return "ok"\n','            return "ok:steps="+str(steps[0])\n')
    return py

def load(py):
    ns={"__name__":"t"}; exec(compile(py.split("\ntry:\n    doc = json.load")[0],"m","exec"),ns); return ns

def mkfam(T,nd,data):
    out=[b"GGUF",struct.pack("<I",3),struct.pack("<QQ",T,0)]; off=0
    for i in range(T):
        name=b"t%07d"%i
        dims=struct.pack("<"+"Q"*nd,1,*([1]*(nd-1)))
        out.append(struct.pack("<Q",len(name))+name+struct.pack("<I",nd)+dims+struct.pack("<IQ",0,off))
        off+=32
    head=b"".join(out); pad=(len(head)+31)//32*32-len(head)
    return head+b"\0"*pad+(b"\0"*off if data else b"\0"*16)

SHAPES=[(833332,1),(833333,1),(900000,1),(700000,4),(555555,4),(555556,4)]
D=S/"mutfix"; D.mkdir(exist_ok=True)
variants={"honest":load(build(src)),"plus1":load(build(src)),"pre1":load(build_pre(src))}
# honest and pre1 from src; plus1 needs its own module (build() mutates) -> rebuild clean
variants["honest"]=load(build(src).replace("                need(1)  # MUTANT +1 per header\n",""))
variants["pre1"]=load(build_pre(src))
print(f"{'shape':>16} {'fam':>5} {'table verdict':>13} | " + " | ".join(f"{k:>22}" for k in variants))
out=[]
for T,nd in SHAPES:
    for data,fam in ((False,"famA"),(True,"famC")):
        p=D/f"{fam}_t{T}_nd{nd}.gguf"; p.write_bytes(mkfam(T,nd,data))
        cells=[]
        for k,ns in variants.items():
            t0=time.monotonic(); st=ns["gguf_parse"](str(p)); dt=time.monotonic()-t0
            cells.append(f"{st} ({dt:.1f}s)"); out.append({"variant":k,"T":T,"nd":nd,"fam":fam,"state":st})
        tv = "invalid" if 4+T*(5+nd)<=5_000_000 else "-"
        print(f"{f'T={T} nd={nd}':>16} {fam:>5} {tv:>13} | " + " | ".join(f"{c:>22}" for c in cells))
Path(S/"mutants_empirical.json").write_text(json.dumps(out,indent=1))
