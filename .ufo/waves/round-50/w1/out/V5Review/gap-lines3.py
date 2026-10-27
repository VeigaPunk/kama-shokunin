import importlib.util, collections
spec = importlib.util.spec_from_file_location("tool", "/fast/scratch/hyaku/kama-r50/V5Review/tool-v5.py")
tool = importlib.util.module_from_spec(spec); spec.loader.exec_module(tool)
repo = "/fast/scratch/hyaku/kama-r50/V5Review/lane"
tip = "97c864bead3ee4a2f629574e77263d33834ec98a"
event = "dd9f5dc6c0e6"
f = "SCORECARD.md"
# replicate tool's commits/parents
commits, parents = [], {}
for line in tool._text(repo, "rev-list", "--topo-order", "--reverse", "--parents", tip).split("\n"):
    parts = line.split()
    if parts:
        commits.append(parts[0]); parents[parts[0]] = parts[1] if len(parts) > 1 else None
c = [x for x in commits if x.startswith(event)][0]
p = parents[c]
i = commits.index(c)
window = commits[i:]
contract = tool._text(repo, "show", f"{tip}:registry/append-only-contract.tsv")
rows = tool.parse_contract(contract)
r = tool.Repo(repo)
dl = tool.deleted_lines(repo, p, c, f)
titles, prefixes = tool.file_regions(rows, f)
pb = r.blobs([f"{p}:{f}"])[f"{p}:{f}"]
psec = tool.sections(r.list_lines(pb))
pcount = r.section_counts(pb)
wb = r.blobs([f"{x}:{f}" for x in window])
eligible = {t for t in titles
            if max(r.section_counts(wb[f"{x}:{f}"])[t] if wb[f"{x}:{f}"] else 0 for x in window)
            >= pcount[t]}
print("titles", titles, "eligible", eligible)
origin_cache, keyset_cache = {}, {}
def body_of(b):
    if b not in keyset_cache:
        body = r.list_lines(b) if b else []
        keyset_cache[b] = (body, {tool.key(x) for x in body})
    return keyset_cache[b]
def origins(ff):
    bl = r.blobs([f"{x}:{f}" for x in commits])
    orig = collections.defaultdict(set)
    for x in commits:
        b = bl[f"{x}:{f}"]
        if b is None: continue
        body, keys = body_of(b)
        pkeys = set()
        for q in (parents[x] or "").split():
            if bl.get(f"{q}:{f}") == b:
                pkeys = keys; break
            qb = bl.get(f"{q}:{f}")
            if qb is not None:
                pkeys |= body_of(qb)[1]
        if pkeys is keys: continue
        for ln, t in zip(body, tool.sections(body)):
            k = tool.key(ln)
            if k not in pkeys:
                orig[k].add(t)
    return orig
org = origins(f)
ng = 0
for pos, text in dl:
    s = psec[pos-1]
    un = (s in eligible) and bool(org.get(tool.key(text), frozenset()) & titles)
    if s in eligible:
        print(f"{pos:>4} sec={s:<16} {'UNGRADED' if un else 'graded'} org={sorted(org.get(tool.key(text), frozenset()), key=lambda x:(x is None,x))} {text[:50]!r}")
    if not un: ng += 1
print("tool-graded total", ng, "of", len(dl))
