"""The SKILL.md prose asserts: 'a 700,000-tensor nd=1 file decides invalid'
   and 'That file now decides invalid at nd <= 2 and stays - at nd >= 3'.
   Measure the 700,000 family at nd=1,2,3,4 directly against the real probe."""
import re, subprocess, time, struct
from pathlib import Path
LANE="/home/vgpnk/Projects/shokunin/kama-shokunin"
S=Path("/fast/scratch/hyaku/kama-r97/SN01StepFlips")
src=subprocess.run(["git","-C",LANE,"show","HEAD:tools/kama-probe.sh"],capture_output=True,text=True).stdout
py=re.search(r"^ROUTER_PY=\$\(cat <<'PY'\n(.*?)^PY$",src,re.S|re.M).group(1)
py=py.replace('        except Unknown:\n            return "-"','        except Unknown as e:\n            return "-:"+str(e)\n')
ns={"__name__":"t"}; exec(compile(py.split("\ntry:\n    doc = json.load")[0],"m","exec"),ns)
gp=ns["gguf_parse"]

def famA(T,nd):
    out=[b"GGUF",struct.pack("<I",3),struct.pack("<QQ",T,0)]; off=0
    for i in range(T):
        name=b"t%07d"%i
        dims=struct.pack("<"+"Q"*nd,1,*([1]*(nd-1)))
        out.append(struct.pack("<Q",len(name))+name+struct.pack("<I",nd)+dims+struct.pack("<IQ",0,off))
        off+=32
    head=b"".join(out); pad=(len(head)+31)//32*32-len(head)
    return head+b"\0"*pad+b"\0"*16

D=S/"contrast"; D.mkdir(exist_ok=True)
print(f"{'T':>8} {'nd':>3} {'steps=4+T*(5+nd)':>17} {'<=5M':>6} {'probe state':>22} {'secs':>6}")
for nd in (1,2,3,4):
    T=700_000
    p=D/f"c700k_nd{nd}.gguf"; p.write_bytes(famA(T,nd))
    steps=4+T*(5+nd)
    t0=time.monotonic(); st=gp(str(p)); dt=time.monotonic()-t0
    print(f"{T:>8} {nd:>3} {steps:>17} {str(steps<=5_000_000):>6} {st:>22} {dt:>6.2f}")
