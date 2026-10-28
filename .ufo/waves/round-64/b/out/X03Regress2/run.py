import subprocess, sys, os, shutil
S=sys.argv[1]
rows = {
 "gguf-declared-identity-replay": ("python3 %T/tools/gguf-identity.py --selftest", '"status": "passed"'),
 "context-capacity-receipt": ("python3 %T/tools/kama-context-capacity.py --only K1 --host-idle-timeout 20 --scratch %S/context-capacity --out %S/cc.json", '"all_ports_closed": true'),
 "instrument-agreement": ("python3 %T/tools/instrument-agreement.py --selftest", "IA_SELFTEST pass="),
}
for tag in ("T0","T1"):
    for cap,(tpl,pat) in rows.items():
        sc=f"{S}/work/{tag}-{cap}"; shutil.rmtree(sc, ignore_errors=True); os.makedirs(sc)
        cmd=tpl.replace("%T",f"{S}/{tag}").replace("%S",sc).replace("%R","/nonexistent")
        p=subprocess.run(cmd,shell=True,capture_output=True,text=True,cwd=sc)
        out=p.stdout+p.stderr
        last=[l for l in out.splitlines() if l.strip()]
        print(f"{tag} {cap}: exit={p.returncode} pattern={'PRESENT' if pat in out else 'ABSENT'} tail={last[-2:]}")
        if cap.startswith("context") and os.path.exists(sc+"/cc.json"):
            import json; j=json.load(open(sc+"/cc.json")); print("   cc.json error=",j.get("error"),"host_idle=",j.get("host_idle"),"summary=",j.get("summary"),"exit_code=",j.get("exit_code"))
