import os, subprocess, time
def bench(script, loc="en_US.UTF-8"):
    env=dict(os.environ); env["LC_ALL"]=loc
    t=time.monotonic(); p=subprocess.run(["bash","-c",script],capture_output=True,env=env)
    return time.monotonic()-t, p.returncode, len(p.stdout)
# isolated: R rows of 200000 bytes each; string-append vs array-append
setup = 'row=$(head -c 200000 /dev/zero | tr "\\0" "a"); set --; for ((i=0;i<%d;i++)); do set -- "$@" "$row"; done;'
old = 'local out="" first=1 r; for r in "$@"; do if [ "$first" -eq 1 ]; then out=$r; first=0; else out="$out,"$'"'"'\\n'"'"'"$r"; fi; done; printf "%s" "$out"'
new = 'local -a __ja=(); local r __i; for r in "$@"; do __ja+=("$r"); done; printf "%s" "${__ja[0]}"; for ((__i=1; __i<${#__ja[@]}; __i++)); do printf ",%s" "${__ja[__i]}"; done'
print("R     string-append(s)   array-append(s)   ratio")
for R in (16,32,64,128):
    s = setup % R
    d1,_,o1 = bench(s+old)
    d2,_,o2 = bench(s+new)
    print(f"{R:<5} {d1:8.3f}          {d2:8.3f}        {d1/max(d2,1e-9):5.2f}   out1={o1} out2={o2}", flush=True)
