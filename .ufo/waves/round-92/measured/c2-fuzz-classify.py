import random, subprocess, sys, os
seed=int(os.environ["SEED"]); random.seed(seed)
alpha = ["\udcff","\udc85","\udcc3",'a','b','/','.gguf','\\','"','\t','\n','\r','\x01','\x1b','\x1f','\x7f',',',' ','é','ж','\u0085','-','*','%s','%','$','`']
cases=["".join(random.choice(alpha) for _ in range(random.randint(0,25))) for _ in range(3000)]
def run(lib, fn, cs):
    script = f'source {lib}; set +e; while IFS= read -r -d "" x; do {fn} "$x"; printf "\\0"; done'
    data = b"".join(c.encode('utf-8','surrogateescape') + b"\0" for c in cs)
    return subprocess.run(["bash","-c",script], input=data, capture_output=True).stdout.split(b"\0")
tot={"jstr":[0,0],"served_persist":[0,0]}
for fn in tot:
    a=run("lib-base.sh",fn,cases); b=run("lib-new.sh",fn,cases)
    d=[i for i in range(len(cases)) if a[i]!=b[i]]
    if d:
        sub=[cases[i] for i in d]
        a2=run("lib-base.sh",fn,sub); a3=run("lib-base.sh",fn,sub)
        for k,i in enumerate(d):
            if a2[k]!=a3[k] or a2[k]!=a[i]: tot[fn][0]+=1   # base nondeterministic
            else:
                tot[fn][1]+=1; print("STABLE-DIFF",fn,repr(cases[i]),a[i],b[i])
    print(f"SEED={seed} {fn} cases={len(cases)} diffs={len(d)} base_nondeterministic={tot[fn][0]} stable_diffs={tot[fn][1]}")
