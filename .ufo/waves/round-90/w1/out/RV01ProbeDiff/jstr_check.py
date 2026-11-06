import json,subprocess,sys,os,time
S="/fast/scratch/hyaku/kama-r90/RV01ProbeDiff"
res={}
for loc in ["C","C.utf8","en_US.utf8"]:
  for name in ["base","M"]:
    env=dict(os.environ,LC_ALL=loc)
    o=subprocess.run(["bash",f"{S}/jstr_run.sh",f"{S}/jstr_{name}.sh"],capture_output=True,env=env)
    lines=o.stdout.decode("latin1").splitlines()
    bad=[];ok=0
    for ln in lines:
        p=ln.split("\t")
        if p[0]=="U":
            raw=bytes.fromhex(p[1]); outb=bytes.fromhex(p[2])
            try:
                parsed=json.loads(outb.decode("utf-8"))
                exp=("q"+raw.decode("utf-8",errors="strict")+"q") if raw!=b"\xff" else None
                if exp is not None and parsed!=exp: bad.append(("U",raw.hex(),outb.hex(),parsed))
                else: ok+=1
            except Exception as e:
                bad.append(("U",raw.hex(),outb.hex(),type(e).__name__))
            continue
        i=int(p[0]); outb=bytes.fromhex(p[1])
        try:
            parsed=json.loads(outb.decode("utf-8"))
            if parsed!=f"a{chr(i)}z": bad.append((i,outb.decode("utf-8","replace"),parsed))
            else: ok+=1
        except Exception as e:
            bad.append((i,outb.decode("utf-8","replace"),type(e).__name__))
    print(f"{loc:12} {name:5} rc={o.returncode} lines={len(lines)} ok={ok} bad={len(bad)}")
    for b in bad[:12]: print("    ",b)
