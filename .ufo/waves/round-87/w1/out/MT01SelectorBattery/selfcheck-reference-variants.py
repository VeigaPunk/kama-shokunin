import re, sys
src = open("round86-rendered-cells.py").read()
def rep(text, old, new):
    assert text.count(old) == 1, (text.count(old), old[:60])
    return text.replace(old, new)
# R1: closer is not container-prefixed; 0-3 spaces, same fence chars, only spaces/tabs after.
r1 = rep(src,
 'FENCE_CLOSE = re.compile(r"^" + CONTAINER + r" {0,3}(`{3,}|~{3,})[ \\t]*$")',
 'FENCE_CLOSE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \\t]*$")')
# R2: disposition is the single token after `verdict ` on the closure's own verdict line.
r2 = rep(r1,
 'def disposition_of(body: str) -> str:\n    for word in DISPOSITIONS:\n        if re.search(rf"\\b{word}\\b", body):\n            return word\n    return "unknown"\n',
 'def disposition_of(body: str) -> str:\n    found = re.findall(r"^verdict `([^`]*)`", body, re.M)\n    if len(found) != 1 or found[0] not in DISPOSITIONS:\n        return "unknown"\n    return found[0]\n')
open("ref-r1r2.py", "w").write(r2)
# R5 (not in frozen R1-R4): every revision the gate cell names must be an ancestor carrying the receipt.
gate = rep(r2,
 '    if not coupled:\n',
 '    for revision in revisions:\n        if not (tree.ancestor(revision) and (tree.blob_at(revision, receipt_path) or "").count(token.group(0).strip("`"))):\n            findings.append(("gate", f"named revision {revision} does not carry {receipt_path} with the token"))\n            return findings\n    if not coupled:\n')
open("ref-r1r2gate.py", "w").write(gate)
print("built")
# Scratch-only: fixture default closure bodies use the R2 verdict-line form (the round-86 default
# "Verdict: rejected-honest-stop." has no backticked token, so an R2 selector fails its green arm).
for name in ("ref-r1r2.py", "ref-r1r2gate.py"):
    text = open(name).read()
    text = rep(text, '"# kama round 85\\n\\nVerdict: rejected-honest-stop. admitted false.\\n"',
               '"# kama round 85\\n\\nverdict `rejected-honest-stop`\\n"')
    text = rep(text, '"# kama round 84\\n\\nVerdict: rejected-honest-stop.\\n"',
               '"# kama round 84\\n\\nverdict `rejected-honest-stop`\\n"')
    open(name, "w").write(text)
print("patched")
