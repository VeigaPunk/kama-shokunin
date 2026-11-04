#!/usr/bin/env python3
"""C2 mutants against the LATEST landed census bytes (af6eb6c2:tools/round65-host-census.py)."""
import importlib.util, json, os, re, subprocess, sys
S="/fast/scratch/hyaku/kama-r70/MT01Mutants"
LANE="/home/vgpnk/Projects/shokunin/kama-shokunin"
CTL=os.path.join(LANE,".ufo/waves/round-70/controls/refused-member-control.py")
PROBE=os.path.join(S,"fail-waiver-probe.py")
SRC=os.path.join(S,"v/c2ex02-latest.py")

HIT='''            if hit:
                suffix = record_ne(name)
                lines.append(f"refused [{tier}] {name}: {hit[1]} (marker {hit[0]!r}){suffix}")
'''
EXIT="    return 0 if (failed == 0 and not unwaived_ne) else 1\n"
VERDICT='''    print(f"HOST_CENSUS pass={passed} fail={failed} not_evaluated={not_evaluated}"
          f"{waived_cell} total={len(MEMBERS)} tierA_fail={fails_a} tierB_fail={fails_b}")
'''
MEMBER='''    ("A", "round42-selfdesc-reconcile selftest",
     ["tools/round42-selfdesc-reconcile.py", "--selftest", "--work", "__WORK__"],
     "",
     [("invalid path", "fail-closed refusal: the lane holds a tracked path NTFS cannot check out, so the fixture clone cannot be created on this host (L0 question, kama round-65)")]),
'''
NE_TAIL="    if unwaived_ne:\n"

MUT={
 "c2a":(HIT,'''            if hit:
                passed += 1  # MUTANT c2a: a refusal counts as a pass
                lines.append(f"pass [{tier}] {name}")
'''),
 "c2b":(EXIT,"    return 1  # MUTANT c2b: always exit 1\n"),
 "c2c":(VERDICT,'''    print(f"HOST_CENSUS pass={passed} fail={failed}"
          f"{waived_cell} total={len(MEMBERS)} tierA_fail={fails_a} tierB_fail={fails_b}")
'''),
 "c2d":(MEMBER,"    # MUTANT c2d: the reconciler member was dropped\n"),
 "c2e":(NE_TAIL,'''    failed -= sum(1 for n, v in evaluated.items()
                  if v == "fail" and n in waive_set)  # MUTANT c2e: a failing member can be waived
'''+NE_TAIL),
}

def load(p):
    spec=importlib.util.spec_from_file_location("c_"+re.sub(r"\W","_",p),p)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def probe(p):
    r=subprocess.run([sys.executable,PROBE,p],capture_output=True,text=True)
    m=re.search(r"fail_member_waived_exit=(\d+)",r.stdout)
    return int(m.group(1)) if m else None, r.stdout.strip()

def main():
    src=open(SRC).read()
    cases=[("latest",SRC)]
    for name,(old,new) in MUT.items():
        d=os.path.join(S,"v","L-"+name); os.makedirs(d,exist_ok=True)
        t=src
        assert t.count(old)==1,(name,t.count(old))
        p=os.path.join(d,"round65-host-census.py"); open(p,"w").write(t.replace(old,new))
        subprocess.run([sys.executable,"-c",f"import ast;ast.parse(open({p!r}).read())"],check=True)
        cases.append(("L-"+name,p))
    for name,p in cases:
        pr=subprocess.run([sys.executable,CTL,p],capture_output=True,text=True)
        lines=pr.stdout.strip().splitlines()
        fx=json.loads(lines[0]) if lines and lines[0].startswith("{") else {}
        ref=next((l for l in fx.get("refused_fixture",[]) if l.startswith("HOST_CENSUS pass=")),"")
        alp=next((l for l in fx.get("allpass_fixture",[]) if l.startswith("HOST_CENSUS pass=")),"")
        pe,pout=probe(p)
        row={"candidate":name,"path":p,"control_exit":pr.returncode,
             "control_line":lines[-1] if lines else "","refused_verdict":ref,"allpass_verdict":alp,
             "refused_has_ne1":"not_evaluated=1" in ref,"allpass_has_ne0":"not_evaluated=0" in alp,
             "members":len(load(p).MEMBERS),"probe_exit":pe,
             "ctl_stderr":pr.stderr.strip()[:200]}
        print(json.dumps(row),flush=True)
if __name__=="__main__":
    main()
