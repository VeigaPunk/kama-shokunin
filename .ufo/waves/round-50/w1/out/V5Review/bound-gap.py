# Reproduce the counter's native bound vs the v5-spec (eligibility-aware) count
# for the dd9f5dc6 SCORECARD.md event on the lane clone.
import importlib.util, collections, fnmatch
spec = importlib.util.spec_from_file_location("ctr", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-append-audit-v5-check.py")
ctr = importlib.util.module_from_spec(spec); spec.loader.exec_module(ctr)
spec2 = importlib.util.spec_from_file_location("tool", "/fast/scratch/hyaku/kama-r50/V5Review/tool-v5.py")
tool = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(tool)
repo = "/fast/scratch/hyaku/kama-r50/V5Review/lane"
tip = "97c864bead3ee4a2f629574e77263d33834ec98a"
event = "dd9f5dc6c0e6"
# find full commit hash and parent
order = ctr.git(repo, "rev-list", "--parents", tip).decode().split("\n")
allpar = {ln.split()[0]: ln.split()[1:] for ln in order if ln.strip()}
commits = list(allpar)
c = [x for x in commits if x.startswith(event)][0]
par = allpar[c][0]
f = "SCORECARD.md"
ex = {"## Axes","## Planned","## Retired","## Saturation","## Capabilities"}
pb = ctr.split_lines(ctr.git(repo, "show", f"{par}:{f}"))
psec = ctr.sections(pb)
dl = ctr.deleted_with_pos(repo, par, c, f)
print("deleted", len(dl))
# counter bound: psec in ex AND origin intersects ex
# spec count: psec in ELIGIBLE AND origin intersects ex
# build origins per counter
origin_cache, keyset_cache = {}, {}
def body_of(b):
    if b not in keyset_cache:
        body = ctr.split_lines(ctr.git(repo, "cat-file", "blob", b)) if b else []
        keyset_cache[b] = (body, {ctr.key(x) for x in body})
    return keyset_cache[b]
def blob_ids(f):
    specs = "\n".join(f"{cc}:{f}" for cc in commits) + "\n"
    out = ctr.git(repo, "cat-file", "--batch-check=%(objectname) %(objecttype)", inp=specs.encode()).decode()
    res = {}
    for cc, line in zip(commits, out.split("\n")):
        parts = line.split()
        res[cc] = parts[0] if len(parts) == 2 and parts[1] == "blob" else None
    return res
bl = blob_ids(f)
orig = collections.defaultdict(set)
for cc in commits:
    b = bl[cc]
    if b is None: continue
    body, keys = body_of(b)
    pkeys = set()
    for q in allpar[cc]:
        if bl.get(q) == b:
            pkeys = keys; break
        if bl.get(q) is not None:
            pkeys |= body_of(bl[q])[1]
    if pkeys is keys: continue
    for ln, t in zip(body, ctr.sections(body)):
        k = ctr.key(ln)
        if k not in pkeys:
            orig[k].add(t)
# eligibility per tool: max window section count >= parent count
i = commits.index(c)
window = commits[i:]
r = tool.Repo(repo)
pcount = collections.Counter(ctr.sections(pb))
# tool uses tool.sections = same logic; use counter sections (identical)
elig = set()
for t in ex:
    mx = 0
    for x in window:
        bx = bl[x]
        if bx is None: continue
        cnt = collections.Counter(ctr.sections(body_of(bx)[0]))[t]
        mx = max(mx, cnt)
    if mx >= pcount[t]:
        elig.add(t)
print("parent section counts", dict(pcount))
print("exempt", ex, "eligible", elig)
loose = sum(1 for pos, text in dl if psec[pos-1] in ex and orig.get(ctr.key(text), set()) & ex)
strict = sum(1 for pos, text in dl if psec[pos-1] in elig and orig.get(ctr.key(text), set()) & ex)
print("counter native bound:", loose, "| spec (eligibility) count:", strict)
