#!/usr/bin/env python3
"""Breakdown of zero-deleted, non-prefix first-parent edges by file. Needs aoa.py = tools/append-only-audit.py @3a09a1d in cwd and ./lane clone.
Output captured in mid_breakdown.out. Read-only on the clone."""
import subprocess, json, collections, re
repo="lane"; tip="3a09a1d93dcc16799cf6c4b48786e6440af134c4"
g=lambda *a: subprocess.run(["git","-C",repo,*a],capture_output=True,check=True).stdout
d=json.loads(subprocess.run(["python3","aoa.py","--repo",repo,"--to",tip,"--json"],capture_output=True).stdout)
rows=[r.split() for r in g("rev-list","--parents","--topo-order","--reverse",tip).decode().split("\n") if r]
byfile=collections.Counter(); pos=collections.Counter()
for c,*ps in rows:
    if not ps: continue
    p=ps[0]
    for f in d["files"]:
        a=subprocess.run(["git","-C",repo,"cat-file","blob",f"{p}:{f}"],capture_output=True)
        b=subprocess.run(["git","-C",repo,"cat-file","blob",f"{c}:{f}"],capture_output=True)
        if a.returncode or b.returncode or a.stdout==b.stdout or b.stdout.startswith(a.stdout): continue
        ns=g("diff","--numstat","--no-renames",p,c,"--",f).decode().split("\t")
        if ns[1]!="0": continue
        byfile[f if not f.startswith("corpus/lessons/") else "corpus/lessons/*.md"]+=1
        m=re.search(r"^@@ -(\d+)(?:,(\d+))? ",g("diff","-U0","--no-renames",p,c,"--",f).decode(),re.M)
        pos["top(start=0)" if int(m.group(1))==0 else "middle"]+=1
print(dict(byfile)); print(dict(pos))
