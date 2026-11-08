#!/usr/bin/env python3
"""CN02SourceFrontier pass 2: quote/line/range verification with markdown unescaping."""
import os, re, json

SCRATCH = "/fast/scratch/hyaku/kama-r94/CN02SourceFrontier"
ARCH = os.path.join(SCRATCH, "llama.cpp-b12177")

def md_unescape(s):
    return s.replace('\\"', '"').replace("\\|", "|").replace("\\\\", "\\")

src = open(os.path.join(SCRATCH, "SOURCES_M2.md"), encoding="utf-8").read().split("\n")
rows = {}
for i, line in enumerate(src, 1):
    s = line.strip()
    if not s.startswith("|"):
        continue
    c = [x.strip() for x in s.strip("|").split("|")]
    if c and re.fullmatch(r"S\d{3,}", c[0]):
        rows[c[0]] = (i, c)

# extra claims in the anchor cell: "lines A-B", "line N"
def declared_refs(anchor):
    refs = []
    for m in re.finditer(r"\blines?\s+(\d+)(?:\s*-\s*(\d+))?", anchor):
        a = int(m.group(1)); b = int(m.group(2)) if m.group(2) else a
        refs.append((a, b))
    # bare "line N" mentions inside the quote parens are handled separately
    return refs

out = []
for n in range(604, 616):
    sid = f"S{n}"
    ln, c = rows[sid]
    anchor, teaches, usedby, scope = c[5], c[6], c[10], c[4]
    url = re.search(r"(https://\S+)", c[1]).group(1)
    path = re.match(r"https://raw\.githubusercontent\.com/ggml-org/llama\.cpp/b12177/(.+)$", url).group(1)
    lines = open(os.path.join(ARCH, path), encoding="utf-8", errors="replace").read().split("\n")
    rec = {"id": sid, "md_line": ln, "path": path, "scope": scope, "usedby": usedby,
           "teaches": teaches, "anchor": anchor, "problems": []}

    mq = re.search(r'opened(\d{4}-\d{2}-\d{2}): "(.*?)" \(line (\d+)([^)]*)\)', anchor)
    q = md_unescape(mq.group(2))
    ql = int(mq.group(3))
    rec["quote"] = q
    rec["stated_line"] = ql
    rec["quote_words"] = len(q.split())
    if rec["quote_words"] > 25:
        rec["problems"].append(f"quote is {rec['quote_words']} words (>25)")
    actual = lines[ql - 1] if ql <= len(lines) else "<OUT OF RANGE>"
    rec["actual_at_stated_line"] = actual
    hits = [i + 1 for i, L in enumerate(lines) if q in L]
    rec["quote_found_at"] = hits
    if q not in actual:
        rec["problems"].append(
            f"quote NOT at stated line {ql} (found at {hits}); line {ql} = {actual.strip()!r}")
    elif hits and hits[0] != ql:
        rec["problems"].append(
            f"quote first occurs at line {hits[0]}, stated {ql} (also at {hits})")

    # declared line ranges in the anchor cell
    for a, b in declared_refs(anchor):
        if a < 1 or b > len(lines):
            rec["problems"].append(f"declared range {a}-{b} out of file range (1-{len(lines)})")
        else:
            rec.setdefault("ranges", []).append({"range": f"{a}-{b}", "first": lines[a-1][:90],
                                                 "last": lines[b-1][:90]})
    out.append(rec)

for r in out:
    tag = "HOLDS" if not r["problems"] else "MISSTATES"
    print(f"\n== {r['id']} {tag} (corpus/SOURCES.md:{r['md_line']})")
    print(f"   path={r['path']}")
    print(f"   stated_line={r['stated_line']} words={r['quote_words']} quote={r['quote']!r}")
    print(f"   actual_at_stated={r['actual_at_stated_line']!r}")
    print(f"   found_at={r['quote_found_at']}")
    for p in r["problems"]:
        print(f"   PROBLEM: {p}")

json.dump(out, open(os.path.join(SCRATCH, "rows_pass2.json"), "w"), indent=1)
print(f"\nSUMMARY total={len(out)} clean={sum(1 for r in out if not r['problems'])} "
      f"problems={sum(1 for r in out if r['problems'])}")
