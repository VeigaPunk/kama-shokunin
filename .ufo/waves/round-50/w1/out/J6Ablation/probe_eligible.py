import collections, importlib.util, json, sys
def load(p, name):
    spec = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
build = load("/fast/scratch/hyaku/kama-r50/J6Ablation/lane/tools/append-only-audit.py", "build_tool")
repo = "/fast/scratch/hyaku/kama-r50/J6Ablation/lane"
tip = "97c864bead3ee4a2f629574e77263d33834ec98a"
res = build.audit(repo, to=tip)
ev = [e for e in res["events"] if e["commit"].startswith("dd9f5dc6c0e6")]
print("event", json.dumps(ev, indent=None))
e = ev[0]; f = e["file"]; c = e["commit"]
parents = {}
for line in build._text(repo, "rev-list", "--topo-order", "--reverse", "--parents", tip).split("\n"):
    parts = line.split()
    if parts: parents[parts[0]] = parts[1] if len(parts) > 1 else None
p = parents[c]
# window = commits from c to tip inclusive
commits = [l.split()[0] for l in build._text(repo, "rev-list", "--topo-order", "--reverse", "--parents", tip).split("\n") if l.strip()]
i = commits.index(c); window = commits[i:]
rows = build.parse_contract(build._text(repo, "show", f"{build._text(repo,'rev-parse','--verify',tip+'^{commit}').strip()}:{build.CONTRACT}"))
r = build.Repo(repo)
pb = r.blobs([f"{p}:{f}"])[f"{p}:{f}"]
body = r.list_lines(pb); psec = build.sections(body); pcount = r.section_counts(pb)
wb = r.blobs([f"{x}:{f}" for x in window])
titles, prefixes = build.file_regions(rows, f)
elig = {t for t in titles if max(r.section_counts(wb[f"{x}:{f}"])[t] if wb[f"{x}:{f}"] else 0 for x in window) >= pcount[t]}
dl = build.deleted_lines(repo, p, c, f)
print("parent", p[:12], "deleted", len(dl), "titles", sorted(titles), "eligible(parent-count)", sorted((t, pcount[t]) for t in titles))
print("eligible_titles", sorted(elig))
print("window_max", {t: max(r.section_counts(wb[f"{x}:{f}"])[t] if wb[f"{x}:{f}"] else 0 for x in window) for t in titles})
uncov = collections.Counter(); cov = collections.Counter()
for pos, text in dl:
    s = psec[pos - 1]
    if s in titles and s not in elig: uncov[s] += 1
    elif s in elig: cov[s] += 1
print("deleted under gutted-exempt-title (graded by v5 eligible test):", dict(uncov))
print("deleted under eligible title:", dict(cov))
