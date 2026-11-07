import os, subprocess, time
def bench(script, loc="en_US.UTF-8"):
    env=dict(os.environ); env["LC_ALL"]=loc
    t=time.monotonic(); p=subprocess.run(["bash","-c",script],capture_output=True,env=env)
    return time.monotonic()-t, p.returncode, len(p.stdout)
old = 'local out="" first=1 r; for r in "$@"; do if [ "$first" -eq 1 ]; then out=$r; first=0; else out="$out,"$'"'"'\\n'"'"'"$r"; fi; done; printf "%s" "$out"'
new = 'local -a __ja=(); local r __i; for r in "$@"; do __ja+=("$r"); done; printf "%s" "${__ja[0]}"; for ((__i=1; __i<${#__ja[@]}; __i++)); do printf ",%s" "${__ja[__i]}"; done'
print("== per-row size S fixed = 200000, R rows ==")
for R in (16,32,64,128):
    s = 'row=$(head -c 200000 /dev/zero | tr "\\0" "a"); set --; for ((i=0;i<%d;i++)); do set -- "$@" "$row"; done;' % R
    d1,_,o1 = bench(s+old); d2,_,o2 = bench(s+new)
    print(f"R={R:<4} string={d1:8.3f}s array={d2:8.3f}s  ratio={d1/max(d2,1e-9):5.2f}  bytes={o1}", flush=True)
print("== TOTAL output fixed at 3.2 MB, R rows (S=3200000/R) ==")
for R in (16,32,64,128):
    s = 'row=$(head -c %d /dev/zero | tr "\\0" "a"); set --; for ((i=0;i<%d;i++)); do set -- "$@" "$row"; done;' % (3200000//R, R)
    d1,_,o1 = bench(s+old); d2,_,o2 = bench(s+new)
    print(f"R={R:<4} string={d1:8.3f}s array={d2:8.3f}s  ratio={d1/max(d2,1e-9):5.2f}  bytes={o1}", flush=True)
