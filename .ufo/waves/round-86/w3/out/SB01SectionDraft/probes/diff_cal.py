import importlib.util, re, subprocess, pathlib, tempfile
S="/fast/scratch/hyaku/kama-r86/SB01SectionDraft"
COPY=f"{S}/copy"
def load(n,f):
    s=importlib.util.spec_from_file_location(n,f"{COPY}/tools/{f}"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
P=load("r86po","round86-pin-origin.py"); R=load("r86rc","round86-rendered-cells.py")
root=pathlib.Path(tempfile.mkdtemp(prefix="sb01-ph-", dir=f"{S}/tmp"))
body="FABRICATED line\n"
P.write_anchor(root,"corpus/anchors/a.txt","https://example.invalid/fabricated/README.md","v1",1,1,["FABRICATED line"],body_override=body)
P.write_anchor(root,"corpus/anchors/b.txt","https://example.invalid/fabricated/README.md","v2",1,1,["FABRICATED line"],body_override=body)
P.write_rows(root,"corpus/anchors/a.txt","corpus/anchors/b.txt")
res=P.grade(root,"worktree",P.ROWS,fetch=lambda u: body.encode())
print("P-H verdict:",res["results"][0]["verdict"], res["results"][0]["detail"][:150])
text=open(f"{S}/SCORECARD.tip.md").read(); lines=text.splitlines()
x=subprocess.check_output(["cmark","--sourcepos","-t","xml",f"{S}/SCORECARD.tip.md"],text=True)
blocks=[(int(a),int(b)) for a,b in re.findall(r'<(?:code_block|html_block)[^>]*sourcepos="(\d+):\d+-(\d+):\d+"',x)]
cal=[i+1 for i,l in enumerate(lines) if re.match(r"^\|\s*calibration\s*\|",l)]
cm=[n for n in cal if not any(a<=n<=b for a,b in blocks)]
rend=R.rendered(text)
ins=[l for l in rend.splitlines() if re.match(r"^\|\s*calibration\s*\|",l)]
print("column-0 calibration rows in file:",cal)
print("cmark non-code calibration rows:",cm)
print("instrument rendered calibration rows:",len(ins))
au=[i+1 for i,l in enumerate(lines) if l.startswith("**Current authority")]
print("cmark non-code authority lines:",[n for n in au if not any(a<=n<=b for a,b in blocks)], "of", au)
