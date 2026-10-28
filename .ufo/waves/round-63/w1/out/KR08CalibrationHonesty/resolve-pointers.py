import re, subprocess, sys, fnmatch
REPO="/home/vgpnk/Projects/shokunin/kama-shokunin"; T="03a6a1d850902a66a13dfad33f89cf3a8b759a09"
files=sys.argv[1:]
tree=subprocess.run(["git","-C",REPO,"ls-tree","-r","--name-only",T],capture_output=True,text=True).stdout.split("\n")
treeset=set(x for x in tree if x)
dirs=set()
for p in treeset:
    parts=p.split("/")
    for i in range(1,len(parts)): dirs.add("/".join(parts[:i]))
def exists(tok):
    t=tok.rstrip("/")
    if any(c in t for c in "*{}<>$ "): return None  # pattern/placeholder
    if t in treeset or t in dirs: return True
    return False
for f in files:
    text=subprocess.run(["git","-C",REPO,"show",f"{T}:{f}"],capture_output=True,text=True).stdout
    for n,line in enumerate(text.split("\n"),1):
        for m in re.finditer(r"`([^`]+)`", line):
            tok=m.group(1).strip()
            if "/" not in tok and not re.search(r"\.(md|py|sh|tsv|json|txt|c|toml|gguf)$",tok): continue
            if tok.startswith("http"): continue
            cand=re.sub(r":\d+(-\d+)?$","",tok)
            cand=cand.split("#")[0]
            r=exists(cand)
            if r is False:
                print(f"{f}:{n}: UNRESOLVED `{tok}`")
            elif r is None:
                pass
