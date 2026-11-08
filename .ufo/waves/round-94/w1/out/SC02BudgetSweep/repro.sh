#!/usr/bin/env bash
# SC02BudgetSweep repro harness — round-94 C1 defect-class sweep.
# Rebuilds every reproduction cited in .ufo/waves/round-94/w1/SC02BudgetSweep.md
#
# Usage:  bash repro.sh <scratchdir>
# Requires: git (lane readable), python3, bash, coreutils. Writes only under <scratchdir>.
set -uo pipefail
S=${1:?scratch dir}
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
M1=a27656a454b1a2364f8b6e55f42fbca8c2e86ee4
BASE=e6f1dccecbad6dea44a129dabc928822c458e824
mkdir -p "$S/harness" "$S/fx" "$S/wt"
cd "$S"

# --- fixtures / probes -------------------------------------------------------
git clone --shared -q "$LANE" wt
git -C wt checkout --detach "$M1"
git -C "$LANE" show "$BASE:tools/kama-probe.sh" > harness/probe_base.sh
cp wt/tools/kama-probe.sh harness/probe_m1.sh
sed 's/timeout 60 python3 -c "\$ROUTER_PY"/timeout 600 python3 -c "$ROUTER_PY"/' \
    harness/probe_m1.sh > harness/probe_m1_wrapper600.sh
python3 - <<'PY'
import subprocess, sys
for rev, out in (("a27656a454b1a2364f8b6e55f42fbca8c2e86ee4","harness/router_m1.py"),
                 ("5af794958b0fc08f574aa2e67650282269549b02","harness/router_counterbase.py")):
    b = subprocess.run(["git","-C","/home/vgpnk/Projects/shokunin/kama-shokunin","show",rev+":tools/kama-probe.sh"],capture_output=True).stdout.decode()
    s = b.index("ROUTER_PY=$(cat <<'PY'\n")+len("ROUTER_PY=$(cat <<'PY'\n"); e = b.index("\nPY\n)", s)
    open(out,"w").write(b[s:e])
print("fixtures ready")
PY
cat > harness/mkfixtures.py <<'PY'
import json, os, struct, sys, time
from pathlib import Path
def gguf(n, elems=1, with_data=False):
    out=[b"GGUF",struct.pack("<I",3),struct.pack("<QQ",n,0)]; off=0; chunk=[]
    for i in range(n):
        nm=b"t%07d"%i; chunk.append(struct.pack("<Q",len(nm))+nm+struct.pack("<IQIQ",1,elems,0,off))
        off+=(elems*4+31)//32*32
        if len(chunk)>=20000: out.append(b"".join(chunk)); chunk=[]
    out.append(b"".join(chunk)); head=b"".join(out)
    pad=(len(head)+31)//32*32-len(head)
    return head+b"\0"*pad+(b"\0"*off if with_data else b"\0"*16)
w=Path(sys.argv[1]).resolve(); w.mkdir(parents=True,exist_ok=True)
k=int(sys.argv[2]); t=int(sys.argv[3]); blob=gguf(t); paths=[]
for i in range(k):
    p=w/f"slow-{i}.gguf"; p.write_bytes(blob); os.utime(p,ns=(time.time_ns(),time.time_ns()+i*1_000_000_000)); paths.append(str(p))
ok=w/"ok.gguf"; ok.write_bytes(gguf(1,32,True)); cor=w/"corrupt.gguf"; cor.write_bytes(b"NOTAGGUF"+b"\0"*184)
def L(a): return json.dumps({"object":"list","data":[{"id":"good","status":{"value":"unloaded","args":x}} for x in a]},separators=(",",":"))
(w/"body.json").write_text(L([[str(ok),"-m",p] for p in paths]))
(w/"body_ok.json").write_text(L([[str(ok),"-m",str(ok)]]*4))
print(json.dumps({"dir":str(w),"n_distinct":k,"tensors":t,"bytes":len(blob)}))
PY
python3 harness/mkfixtures.py "$S/fx/d40"  40 150000
python3 harness/mkfixtures.py "$S/fx/n400k" 1 400000
python3 harness/mkfixtures.py "$S/fx/d20"  20 150000
echo "SETUP DONE in $S"
echo "--- F5 (per-file band flip): the SAME 400k file, same probe, alternating runs:"
for i in 1 2 3 4; do
  printf '  try%s: ' $i
  python3 - "$S" <<'PY'
import subprocess,sys,time
S=sys.argv[1]
t=time.monotonic()
r=subprocess.run([sys.executable,"-c",open(f"{S}/harness/router_m1.py").read(),f"{S}/fx/n400k/body.json","files","0"],capture_output=True)
print(f"state={r.stdout.decode().strip()!r} wall={time.monotonic()-t:.2f}s load1={open('/proc/loadavg').read().split()[0]}")
PY
done
