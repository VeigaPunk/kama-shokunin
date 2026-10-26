#!/usr/bin/env python3
"""Per first-parent edge, per contracted file: numstat deletions vs strict byte-prefix (new startswith old).
Read-only on --repo. Usage: prefix_scan.py REPO TIP"""
import subprocess, sys, json, collections
repo, tip = sys.argv[1], sys.argv[2]
def g(*a): return subprocess.run(["git","-C",repo,*a],capture_output=True,check=True).stdout
d = json.loads(subprocess.run([sys.executable,"aoa.py","--repo",repo,"--to",tip,"--json"],capture_output=True).stdout)
files = d["files"]
revs = g("rev-list","--parents","--topo-order","--reverse",tip).decode().split("\n")
rows = [r.split() for r in revs if r]
blob = {}
def getb(c,f):
    k=(c,f)
    if k not in blob:
        p=subprocess.run(["git","-C",repo,"cat-file","blob",f"{c}:{f}"],capture_output=True)
        blob[k]=p.stdout if p.returncode==0 else None
    return blob[k]
cnt = collections.Counter(); ex = collections.defaultdict(list)
for c,*ps in rows:
    if not ps: continue
    p=ps[0]
    for f in files:
        a,b = getb(p,f), getb(c,f)
        if a is None or a==b: continue
        if b is None: cnt["file_deleted"]+=1; ex["file_deleted"].append((c[:8],f)); continue
        ns = g("diff","--numstat","--no-renames",p,c,"--",f).decode().split("\t")
        dele = int(ns[1]) if ns[1].isdigit() else -1
        prefix = b.startswith(a)
        if prefix: cnt["pure_append"]+=1
        elif dele==0: cnt["noprefix_zero_deleted(mid-file insert)"]+=1; ex["mid"].append((c[:8],f,ns[0]))
        else:
            k = "noprefix_deleted>=20" if dele>=20 else "noprefix_deleted<20"
            cnt[k]+=1
            if dele>=20: ex["ge20"].append((c[:8],f,dele))
print(json.dumps({"files":len(files),"commits":len(rows),"counts":cnt,"examples":{k:v[:12] for k,v in ex.items()}},indent=1,default=dict))
