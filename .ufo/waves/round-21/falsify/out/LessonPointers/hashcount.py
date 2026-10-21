import re, subprocess, sys
L, F, A = sys.argv[1], sys.argv[2], sys.argv[3]
def git(repo, *a, inp=None):
    return subprocess.run(["git", "-C", repo, *a], input=inp, capture_output=True, text=True).stdout
files = [p for p in git(L, "ls-tree", "-r", "--name-only", A, "--", "corpus").split("\n") if p.endswith(".md") or p.endswith(".tsv")]
tok = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{40}(?![0-9A-Za-z])")
occ = {}
for p in files:
    text = git(L, "show", f"{A}:{p}")
    for t in tok.findall(text):
        occ.setdefault(t, []).append(p)
uniq = sorted(occ)
def status(repo, toks):
    out = git(repo, "cat-file", "--batch-check", inp="".join(t + "\n" for t in toks))
    res = {}
    for t, line in zip(toks, out.split("\n")):
        res[t] = "missing" if line.endswith("missing") else ("ambiguous" if line.endswith("ambiguous") else "found")
    return res
lane = status(L, uniq); fleet = status(F, uniq)
cls = {t: ("lane" if lane[t] == "found" else "fleet" if fleet[t] == "found" else "UNRESOLVED") for t in uniq}
from collections import Counter
print("files_scanned", len(files), "unique_40hex", len(uniq), "occurrences", sum(len(v) for v in occ.values()))
print("classes", dict(Counter(cls.values())))
for t in uniq:
    if cls[t] == "UNRESOLVED":
        print("UNRESOLVED", t, sorted(set(occ[t]))[:3], len(occ[t]))
