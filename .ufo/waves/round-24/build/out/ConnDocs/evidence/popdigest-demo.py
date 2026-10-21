"""Show that the r23 grid population digest couples to (a) the pinned refusal
reason strings and (b) each row's expected exit. The digest is what three
documents pin, so a repair that re-pins either changes the pin."""
import re, hashlib, json
src = open('tests/report-audit/repo-state-grid.py').read()
body = src.split('CASES = [')[1].split('\n]\n')[0]
rows = re.findall(r'\("([^"]+)",\s*"([^"]+)",\s*(\w+),\s*(\d+),\s*(\[[^\]]*\]|None)\)', body)
BASE = {"F02-report-invalid-utf8":"output is not UTF-8","F06-lazy-fetch-command":"partial clone",
 "F10-shallow-lane":"shallow repository","F11-grafts-lane":"rewrites history",
 "F13-ref-named-abbreviation":"names a ref","F15-sha256-lane":"object format",
 "F16-errata-invalid-utf8":"output is not UTF-8","F21-nested-subdirectory-lane":"not a repository top level",
 "F23-promisor-pack-without-config":"promisor pack","F30-config-include-fifo":"timed out after",
 "F24-huge-round-number":"could-not-evaluate: internal: ValueError",
 "F26-huge-author-timestamp":"unexpected git log record"}
def digest(rows, reasons):
    rws=[[n,k,b,int(e),(None if s=='None' else json.loads(s)),reasons.get(n)] for n,k,b,e,s in rows]
    return hashlib.sha256(json.dumps(rws, sort_keys=True).encode()).hexdigest()
base = digest(rows, BASE)
print("rows:", len(rows), " base population:", base)
print("documented pin  : f29fab8d9af1d02de7f6fa4c7b39b2307113d3716fd4b11cffdd0cd65d55364a")
print("match:", base == "f29fab8d9af1d02de7f6fa4c7b39b2307113d3716fd4b11cffdd0cd65d55364a")
r2 = dict(BASE); r2["F23-promisor-pack-without-config"]="missing blob 45b983be"
print("\n(a) re-pin F23 reason  ->", digest(rows, r2))
r3 = list(rows)
for n,k,b,e,s in r3:
    if n == "T01-blobless-partial-clone":
        r3[r3.index((n,k,b,e,s))] = (n,k,b,"0",s)
print("(b) T01 expected exit 0 ->", digest(r3, BASE))
r4 = list(rows)
for n,k,b,e,s in r4:
    if n == "T01-blobless-partial-clone":
        r4[r4.index((n,k,b,e,s))] = (n,"control",b,e,s)
print("(c) T01 kind control   ->", digest(r4, BASE))
