import importlib.util, re, sys, os
R = "/home/vgpnk/Projects/shokunin/kama-shokunin"
spec = importlib.util.spec_from_file_location("c", os.path.join(R, "tools/round42-selfdesc-reconcile.py"))
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
text = open(os.environ["S"] + "/SCORECARD.head.md").read()
lines = text.split("\n")
# fence-aware state
fence = None; infence = []
for i, l in enumerate(lines, 1):
    m = re.match(r"^(\s*)(`{3,}|~{3,})", l)
    if fence is None:
        if m: fence = m.group(2)[0] * len(m.group(2)); infence.append(i); 
        else: infence.append(None)
    else:
        infence.append(i if True else None)
        if m and m.group(2)[0]==fence[0] and len(m.group(2))>=len(fence) and l.strip()==m.group(2):
            fence = None
print("total lines", len(lines))
rounds_all = [(i, int(m.group(1))) for i, l in enumerate(lines, 1) for m in [re.match(r"^## Round (\d+)", l)] if m]
def in_fence(i):
    # fence opened at line i' <= i and not closed
    f = None
    for j in range(1, i):
        l = lines[j-1]
        m = re.match(r"^\s*(`{3,}|~{3,})", l)
        if f is None:
            if m: f = m.group(1)
        else:
            if m and m.group(1)[0]==f[0] and len(m.group(1))>=len(f) and l.strip()==m.group(1): f=None
    return f is not None
print("round headings:", len(rounds_all), "max", max(n for _, n in rounds_all))
fenced = [(i, n) for i, n in rounds_all if in_fence(i)]
print("fenced round headings:", fenced)
print("max fence-aware:", max(n for i, n in rounds_all if not in_fence(i)))
print("distinct round numbers:", sorted(set(n for _, n in rounds_all)))
for name in ["Axes","Planned","Retired","Capabilities","Saturation","Historical head sections (superseded in round 42)"]:
    hits=[i+1 for i,l in enumerate(lines) if l.strip()=="## "+name]
    print("section", name, hits, "fenced:", [in_fence(h) for h in hits])
for name in ["Planned","Retired","Capabilities","Saturation"]:
    print(name, "sections() count", len(c.sections(text, name)))
bn, rows = c.canon(text)
print("canon round", bn, "rows", len(rows))
for r in rows: print("  ", r[0][:60], "|", r[-1][:20] if r else r)
