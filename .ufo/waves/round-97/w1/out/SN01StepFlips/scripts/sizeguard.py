"""Does the size guard (n_kv*13 + n_tensors*24 > size) decide the `-` rows instead of the step budget?
Truncate the SAME declared tensor count to a body too small for the header count."""
import re, subprocess, sys, time
from pathlib import Path
LANE="/home/vgpnk/Projects/shokunin/kama-shokunin"
src=subprocess.run(["git","-C",LANE,"show","HEAD:tools/kama-probe.sh"],capture_output=True,text=True).stdout
py=re.search(r"^ROUTER_PY=\$\(cat <<'PY'\n(.*?)^PY$",src,re.S|re.M).group(1)
py=py.replace('        except Unknown:\n            return "-"','        except Unknown as e:\n            return "-:"+str(e)\n')
py=py.replace('            if n_kv * 13 + n_tensors * 24 > size:\n                return "invalid"',
              '            if n_kv * 13 + n_tensors * 24 > size:\n                return "invalid-SIZE-GUARD"')
py=py.replace('            if n_kv > MAX_KV or n_tensors > MAX_TENSORS:\n                return "-"',
              '            if n_kv > MAX_KV or n_tensors > MAX_TENSORS:\n                return "-MAX_TENSORS"')
ns={"__name__":"t"}; exec(compile(py.split("\ntry:\n    doc = json.load")[0],"m","exec"),ns)
gp=ns["gguf_parse"]
FIX=Path("/fast/scratch/hyaku/kama-r97/SN01StepFlips/fix")
for T,nd in [(833333,1),(555556,4),(900000,1),(700000,4)]:
    src_f=FIX/f"t{T}_nd{nd}_A.gguf"
    b=src_f.read_bytes()
    need=T*24
    # (1) full file (as built)
    t0=time.monotonic(); s1=gp(str(src_f)); d1=time.monotonic()-t0
    # (2) same declared count, body truncated below the size guard's threshold
    trunc=Path(f"/fast/scratch/hyaku/kama-r97/SN01StepFlips/fix/trunc_{T}_{nd}.gguf")
    trunc.write_bytes(b[:need-1])
    s2=gp(str(trunc))
    # (3) exactly at threshold (not > size)
    trunc2=Path(f"/fast/scratch/hyaku/kama-r97/SN01StepFlips/SN01StepFlips_thresh_{T}_{nd}.gguf")
    trunc2=Path(f"/fast/scratch/hyaku/kama-r97/SN01StepFlips/thresh_{T}_{nd}.gguf")
    trunc2.write_bytes(b[:need])
    s3=gp(str(trunc2))
    print(f"T={T} nd={nd} size_guard_threshold={need} full_file_state={s1} ({d1:.2f}s) "
          f"truncated_to_{need-1}={s2} truncated_to_{need}={s3}")
