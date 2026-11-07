import os, subprocess, time, statistics, shutil, json
from pathlib import Path
sys_path="/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep"
import sys; sys.path.insert(0, sys_path)
from harness import Stub, Runner, ids_doc, jbody, uptime_str
S=Path(sys_path)
def bench(script):
    env=dict(os.environ); env["LC_ALL"]="en_US.UTF-8"
    t=time.monotonic(); p=subprocess.run(["bash","-c",script],capture_output=True,env=env)
    return time.monotonic()-t, p.returncode, len(p.stdout)
OLD='local out="" first=1 r; for r in "$@"; do if [ "$first" -eq 1 ]; then out=$r; first=0; else out="$out,"$'"'"'\\n'"'"'"$r"; fi; done; printf "%s" "$out"'
NEW='local -a __ja=(); local r __i; for r in "$@"; do __ja+=("$r"); done; printf "%s" "${__ja[0]}"; for ((__i=1; __i<${#__ja[@]}; __i++)); do printf ",%s" "${__ja[__i]}"; done'
print("=== ISOLATED json_array construct: TOTAL output fixed at 3.2 MB, R rows (min of 3, interleaved) ===", flush=True)
for R in (16,32,64,128):
    s='row=$(head -c %d /dev/zero | tr "\\0" "a"); set --; for ((i=0;i<%d;i++)); do set -- "$@" "$row"; done;' % (3200000//R, R)
    o=[]; n=[]
    for rep in range(3):
        d,_,bo=bench(s+OLD); o.append(d)
        d,_,bn=bench(s+NEW); n.append(d)
    print(f"R={R:<4} string-append min={min(o):7.3f}s  array-append min={min(n):7.3f}s  ratio={min(o)/max(min(n),1e-9):5.2f}  bytes_old={bo} bytes_new={bn}", flush=True)
