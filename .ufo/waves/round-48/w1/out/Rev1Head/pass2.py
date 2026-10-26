#!/usr/bin/env python3
"""Pass 2: per-class kept/dropped + banner text forensics."""
import json, re, subprocess, sys, collections
REPO=sys.argv[1]; START=sys.argv[2]; TIP=sys.argv[3]
def git(*a): return subprocess.run(["git","-C",REPO,*a],check=True,capture_output=True).stdout
def show(rev):
    try: return git("show",f"{rev}:SCORECARD.md").decode("utf-8","replace")
    except subprocess.CalledProcessError: return ""
def secs(lines):
    out,cur=[],None
    for ln in lines:
        if ln.startswith("## "): cur=ln.rstrip()
        out.append(cur)
    return out
def bnd(lines):
    for i,l in enumerate(lines):
        if l.startswith("## Round 6"): return i
    return len(lines)
def hunks(d):
    cur=None
    for ln in d.splitlines():
        m=re.match(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@",ln)
        if m:
            if cur: yield cur
            cur=[int(m.group(1)),int(m.group(2) or 1),[],[],[]]
            continue
        if cur is None: continue
        if ln.startswith("-") and not ln.startswith("---"): cur[2].append(ln[1:])
        elif ln.startswith("+") and not ln.startswith("+++"): cur[3].append(ln[1:])
        else: cur[4].append(ln)
    if cur: yield cur
def cls(sec,t):
    t=t.strip()
    if sec is None: return "banner"
    b=sec[3:].strip().split(" — ")[0].split(" (")[0].strip()
    if b=="Axes": return "Axes:row" if t.startswith("|") else "Axes:prose"
    if b=="Planned": return "Planned:pointer"
    if b=="Saturation": return "Saturation"
    if b=="Capabilities": return "Capabilities:mirror"
    return "other:"+b[:24]
commits=git("rev-list","--first-parent","--reverse",f"{START}..HEAD","--","SCORECARD.md").decode().split()
base_new=show(TIP)
newset=collections.Counter(x.strip() for x in base_new.split("\n"))
events=[]
for c in commits:
    p=git("rev-parse",f"{c}^").decode().strip()
    old=show(p); new=show(c)
    ol=old.split("\n"); b=bnd(ol); S=secs(ol)
    nset_here=set(x.strip() for x in new.split("\n"))
    d=git("diff","-U0","--no-color",p,c,"--","SCORECARD.md").decode("utf-8","replace")
    per=collections.defaultdict(lambda:{"del":0,"kept_file":0,"dropped":[],"added":0})
    for os_,oc,ds,ads,_ in hunks(d):
        si=os_ if oc==0 else os_-1
        if si>=b:
            continue
        if oc==0:
            k=cls(S[si-1] if si-1>=0 else None, ads[0] if ads else "")
            per[k]["added"]+=len(ads); continue
        n=min(oc,b-si)
        for j in range(n):
            i=si+j; k=cls(S[i], ol[i]); s=ol[i].strip()
            per[k]["added"]+=0
            per[k]["del"]+=1
            if s and s in nset_here: per[k]["kept_file"]+=1
            elif s: per[k]["dropped"].append(ol[i])
        per[k if False else cls(S[si], ol[si])]["added"]+=len(ads)
    events.append(dict(commit=c[:8],parent=p[:8],
        subject=git("log","-1","--format=%s",c).decode().strip()[:100],
        per={k:{"del":v["del"],"kept_in_commit_file":v["kept_file"],
                "added":v["added"],"dropped":len(v["dropped"]),
                "dropped_at_tip":sum(1 for x in v["dropped"] if x.strip() not in newset),
                "samples":[x[:150] for x in v["dropped"][:3]]} for k,v in per.items()}))
print(json.dumps(events,indent=1))
