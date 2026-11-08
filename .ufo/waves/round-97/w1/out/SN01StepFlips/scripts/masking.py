"""Which guard decides a `-` file? Test the MAX_TENSORS masking effect at 1,000,001 tensors."""
import re, subprocess, struct, time
from pathlib import Path
LANE="/home/vgpnk/Projects/shokunin/kama-shokunin"
src=subprocess.run(["git","-C",LANE,"show","HEAD:tools/kama-probe.sh"],capture_output=True,text=True).stdout
py=re.search(r"^ROUTER_PY=\$\(cat <<'PY'\n(.*?)^PY$",src,re.S|re.M).group(1)
py=py.replace('        except Unknown:\n            return "-"','        except Unknown as e:\n            return "-:steps:"+str(e)\n')
py=py.replace('            if n_kv > MAX_KV or n_tensors > MAX_TENSORS:\n                return "-"',
              '            if n_kv > MAX_KV or n_tensors > MAX_TENSORS:\n                return "-MAX_TENSORS(n="+str(n_tensors)+")"')
py=py.replace('            if n_kv * 13 + n_tensors * 24 > size:\n                return "invalid"',
              '            if n_kv * 13 + n_tensors * 24 > size:\n                return "invalid-SIZE-GUARD"')
ns={"__name__":"t"}; exec(compile(py.split("\ntry:\n    doc = json.load")[0],"m","exec"),ns)
gp=ns["gguf_parse"]
D=Path("/fast/scratch/hyaku/kama-r97/SN01StepFlips/maskfix"); D.mkdir(exist_ok=True)
def mk(T,nd):
    out=[b"GGUF",struct.pack("<I",3),struct.pack("<QQ",T,0)]; off=0
    for i in range(T):
        name=b"t%07d"%i
        dims=struct.pack("<"+"Q"*nd,1,*([1]*(nd-1)))
        out.append(struct.pack("<Q",len(name))+name+struct.pack("<I",nd)+dims+struct.pack("<IQ",0,off))
        off+=32
    head=b"".join(out); pad=(len(head)+31)//32*32-len(head)
    return head+b"\0"*pad+b"\0"*16
for T,nd,label in [(900000,1,"W14 target: 900,000 < MAX_TENSORS 1,000,000"),
                    (1000001,1,"1,000,001 > MAX_TENSORS 1,000,000")]:
    p=D/f"m{T}.gguf"; p.write_bytes(mk(T,nd))
    t0=time.monotonic(); st=gp(str(p)); dt=time.monotonic()-t0
    print(f"T={T:>9} nd={nd} steps_claim={4+T*(5+nd):>9} state={st:<32} ({dt:.2f}s)  [{label}]")
