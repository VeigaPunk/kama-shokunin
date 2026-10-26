import subprocess, json, sys, re
LANE="lane"
def git(*a):
    return subprocess.run(["git","-C",LANE]+list(a),capture_output=True,text=True,check=True).stdout
tips=["74558c71c38ceaeace15fd4cf8aa9d84977584b1","82b5e9d33a19"]  # 82b5e9d3 short
tips[1]=git("rev-parse","82b5e9d3").strip()
def blob(rev):
    return git("show",f"{rev}:SCORECARD.md")
def section_of(text, blobtext):
    sec=None
    for line in blobtext.split("\n"):
        if line.startswith("## "): sec=line[3:].strip()
        if line==text: return sec
    return "ABSENT"
rows=[]
for line in open("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X2Lane/regraded-7.tsv").read().split("\n"):
    if not line or line.startswith("parent_line"): continue
    parts=line.split("\t")
    rows.append({"parent_line":parts[0],"section":parts[1],"origin_claim":parts[2],"text":parts[3]})
revs=git("rev-list","--topo-order","--reverse","HEAD","--","SCORECARD.md").split()
blobs={r:blob(r) for r in [tips[0], revs[-1], tips[1]]}
# first commit whose blob holds the text
first={}
for r in revs:
    b=blob(r)
    for i,row in enumerate(rows):
        if i in first: continue
        if row["text"] in b.split("\n"):
            first[i]=r
out={"tips":tips,"rows":[]}
parent=git("rev-parse","0718b6abbda6^").strip()
pb=blob(parent)
for i,row in enumerate(rows):
    r=first.get(i)
    out["rows"].append({
        "parent_line":row["parent_line"],
        "section_at_parent":section_of(row["text"],pb),
        "origin_claim":row["origin_claim"],
        "first_commit":r,
        "section_at_first":section_of(row["text"],blob(r)) if r else None,
        "held_at_82b5e9d3":row["text"] in blobs[tips[1]].split("\n"),
        "held_at_build":row["text"] in blobs[tips[0]].split("\n"),
        "text":row["text"][:120]})
print(json.dumps(out,indent=1))
