import subprocess, sys, collections, json
REPO="/fast/scratch/hyaku/kama-r48/X1Banner/lane"
FILE="SCORECARD.md"
EVENT="0718b6ab"
TIPS={"base":"33e005827742b29772b153cda036ec9f27f653be","build":"380bcdff9c8af06997c482f6eb03db926a794a2b"}
EXEMPT=["## Axes","## Planned","## Retired","## Saturation","## Capabilities"]

def git(*a):
    return subprocess.run(["git","-C",REPO,*a],capture_output=True,check=True).stdout

def blob(rev, path):
    try: b=git("show",f"{rev}:{path}")
    except subprocess.CalledProcessError: return None
    parts=b.split(b"\n")
    if parts and parts[-1]==b"": parts=parts[:-1]
    return parts

def sections(lines):
    out=[]; cur=None
    for ln in lines:
        if ln.startswith(b"## "): cur=ln[3:].rstrip(b"\r").rstrip(b" ").decode()
        out.append(cur)
    return out

def count(lines,sec): 
    return sum(1 for s in sections(lines) if s==sec)

parent=git("rev-parse",f"{EVENT}^").decode().strip()
print("parent",parent[:8])
P=blob(parent,FILE); C=blob(EVENT,FILE)
print("parent lines",len(P),"commit lines",len(C) if C else None)
# -U0 diff hunks -> deleted lines with parent positions
diff=subprocess.run(["git","-C",REPO,"diff","-U0",parent,EVENT,"--",FILE],capture_output=True,check=True).stdout.decode("utf-8","surrogateescape")
deleted=[]  # (parent_index0, text)
i=0; lines=diff.split("\n")
while i<len(lines):
    l=lines[i]
    if l.startswith("@@"):
        # @@ -a,b +c,d @@
        head=l.split("@@")[1].strip()
        minus=head.split(" ")[0]; a,b=minus[1:].split(",") if "," in minus else (minus[1:],"1")
        a=int(a); b=int(b) if b else 1
        i+=1; idx=a-1
        while i<len(lines) and not lines[i].startswith("@@"):
            if lines[i].startswith("-"):
                deleted.append((idx, lines[i][1:])); idx+=1
            elif lines[i].startswith("+"):
                pass
            elif lines[i].startswith(" "):
                idx+=1
            i+=1
        continue
    i+=1
print("deleted lines parsed",len(deleted))
D=collections.Counter(t for _,t in deleted)
numstat=git("diff","--numstat",parent,EVENT,"--",FILE).decode().strip()
print("numstat:",numstat)
ps=sections(P)
# eligibility per exempt title over window
win=git("rev-list","--topo-order","--reverse",f"{EVENT}..{TIPS['build']}").decode().split()
win=[EVENT]+win
cnt_parent={t:count(P,t[3:]) for t in EXEMPT}
elig={}
for t in EXEMPT:
    mx=max((count(blob(c,FILE) or [],t[3:]) for c in win),default=0)
    elig[t]= mx>=cnt_parent[t]
    print(f"exempt {t!r}: parent={cnt_parent[t]} window_max={mx} eligible={elig[t]}")
graded=[(idx,t) for idx,t in deleted if ps[idx] is None or f"## {ps[idx]}" not in EXEMPT or not elig[f"## {ps[idx]}"]]
print("graded",len(graded),"ungraded",len(deleted)-len(graded))
# K = parent lines minus D (multiset)
K=collections.Counter(P)-D
for name,tip in TIPS.items():
    M=blob(tip,FILE); Mc=collections.Counter(M)
    held=0; deficit=collections.Counter()
    for l,n in D.items():
        h=min(n,max(0,Mc[l]-K[l])); held+=h
        if n-h>0: deficit[l]=n-h
    print(f"--- {name} {tip[:8]}: total D={sum(D.values())} held(all)={held}")
    # graded-only held
    Dh=collections.Counter(t for _,t in graded)
    gh=0; gdef=collections.Counter()
    for l,n in Dh.items():
        h=min(n,max(0,Mc[l]-K[l])); gh+=h
        if n-h>0: gdef[l]=n-h
    print(f"    graded D={sum(Dh.values())} graded_held={gh} missing={sum(gdef.values())}")
    for l,n in gdef.items():
        idxs=[i for i,t in graded if t==l]
        print(f"    MISSING x{n} parent_lines={[i+1 for i in idxs]} section={[ps[i] for i in idxs]}")
        print("    TEXT:",repr(l.decode("utf-8","surrogateescape")))
