#!/usr/bin/env python3
"""CN02SourceFrontier pass 3: verify SKILL.md round-94 section P-row line citations
against the pinned b12177 archive, and dump the SOURCES 'teaches' cells for review."""
import os, re, subprocess, json

SCRATCH = "/fast/scratch/hyaku/kama-r94/CN02SourceFrontier"
ARCH = os.path.join(SCRATCH, "llama.cpp-b12177")
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REV = "6aa5fa6bd9bbf44c4b2ca3f1e2158e7d5aa92623"

skill = subprocess.run(["git", "-C", LANE, "show", f"{REV}:SKILL.md"],
                       capture_output=True, text=True, check=True).stdout.split("\n")

# locate the round-94 revision section
start = None
for i, L in enumerate(skill):
    if L.startswith("## Listen port and slot-count setters (round 94 revision)"):
        start = i
        break
end = len(skill)
for i in range(start + 1, len(skill)):
    if skill[i].startswith("## "):
        end = i
        break
print(f"section_lines={start+1}..{end} ({end-start} lines)")

# P-row format: | Pnn | file | line | `quote` | ...
prows = []
for i in range(start, end):
    L = skill[i]
    s = L.strip()
    if not s.startswith("|"):
        continue
    c = [x.strip() for x in s.strip("|").split("|")]
    if c and re.fullmatch(r"P\d{2}", c[0]):
        prows.append((i + 1, c))
print(f"P-rows in section: {len(prows)}")

cache = {}
def member_lines(p):
    if p not in cache:
        cache[p] = open(os.path.join(ARCH, p), encoding="utf-8", errors="replace").read().split("\n")
    return cache[p]

bad = []
for ln, c in prows:
    pid, path, lineno, quote = c[0], c[1], c[2], c[3]
    srcid = c[-1]
    m = re.match(r"^(.*?)\s*line\s*(\d+)$", path)
    if m:
        path = m.group(1)
    try:
        n = int(re.sub(r"[^0-9]", "", lineno))
    except ValueError:
        n = None
    if not os.path.exists(os.path.join(ARCH, path)):
        bad.append((pid, ln, f"path not in archive: {path}"))
        continue
    L = member_lines(path)
    if n is None or n > len(L):
        bad.append((pid, ln, f"line not parseable/out of range: {lineno} (file has {len(L)})"))
        continue
    actual = L[n - 1]
    q = quote.strip("`")
    # SKILL.md quotes are markdown-escaped with \" sometimes
    qc = q.replace('\\"', '"')
    if qc not in actual:
        hits = [j + 1 for j, X in enumerate(L) if qc in X]
        bad.append((pid, ln, f"{path}:{n} quote not present; found at {hits[:4]} | line={actual.strip()[:110]!r}"))

print(f"\nP-row line citations checked: {len(prows)}  mismatching: {len(bad)}")
for b in bad:
    print(f"  {b[0]} (SKILL.md:{b[1]}): {b[2]}")

# which S-rows are cited by which P-rows
srcmap = {}
for ln, c in prows:
    for s in re.findall(r"S\d{3}", c[-1]):
        srcmap.setdefault(s, []).append((c[0], ln))
print("\nS-row -> citing P-rows:")
for s in sorted(srcmap):
    print(f"  {s}: {', '.join(p for p, _ in srcmap[s])}")

# are S604..S615 cited anywhere in SKILL.md (whole file)?
whole = "\n".join(skill)
for n in range(593, 616):
    sid = f"S{n}"
    if sid in whole:
        cnt = whole.count(sid)
        print(f"  {sid}: present in SKILL.md ({cnt}x)")
    else:
        print(f"  {sid}: ABSENT from SKILL.md")

json.dump({"bad": bad}, open(os.path.join(SCRATCH, "prow_linecheck.json"), "w"), indent=1)
