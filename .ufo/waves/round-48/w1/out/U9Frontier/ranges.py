import csv,subprocess,re
def show(rev,p): return subprocess.run(["git","-C","up","show",f"{rev}:{p}"],capture_output=True,text=True).stdout.split("\n")
rows=list(csv.DictReader(open("/home/vgpnk/Projects/shokunin/kama-shokunin/registry/release-recheck-b11906.tsv"),delimiter="\t"))
print(len(rows),"rows; released",set(r['release'] for r in rows))
cache={}
for r in rows:
    if r['path'] not in ("src/llama-context.cpp","src/llama-kv-cache.cpp"): continue
    p=r['path']; old=cache.setdefault((p,'o'),show("b11906",p)); new=cache.setdefault((p,'n'),show("b11912",p))
    out=[]
    for rg in r['release_lines'].split(","):
        m=re.match(r"(\d+)(?:-(\d+))?$",rg.strip())
        if not m: out.append(rg+":?"); continue
        a=int(m.group(1)); b=int(m.group(2) or a)
        blk=old[a-1:b]
        pos=[i+1 for i in range(len(new)-len(blk)+1) if new[i:i+len(blk)]==blk]
        out.append(f"{rg}->{pos[0] if pos else 'NO-EXACT-MATCH'}{'' if len(pos)<=1 else '(x%d)'%len(pos)}")
    print(r['id'],p,r['verdict'],"|"," ".join(out))
