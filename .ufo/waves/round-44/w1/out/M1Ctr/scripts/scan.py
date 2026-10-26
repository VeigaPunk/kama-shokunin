#!/usr/bin/env python3
"""M1Ctr scan: facts about the frozen C1 population needed to build fixtures."""
import importlib.util, json, os, re

SCRATCH = "/fast/scratch/hyaku/kama-r44/M1Ctr"
LANE = os.path.join(SCRATCH, "lane")
UP = "/fast/scratch/hyaku/kama-r44/shared/llama.cpp"
BASE = "9d9cc93ec50783cd114829a91757b90d57c78dc6"

spec = importlib.util.spec_from_file_location("c1", os.path.join(LANE, "tools", "round44-release-recheck-audit.py"))
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

base_src = c1.show(LANE, BASE, c1.SOURCES)
assert base_src is not None, "BASE SOURCES unreadable"
pop = c1.population(base_src)

draft = {}
dtext = c1.show(LANE, "HEAD", ".ufo/waves/round-44/c1/draft-ledger.tsv")
assert dtext is not None, "draft ledger not committed at lane HEAD"
dl = [x for x in dtext.splitlines() if x.strip()]
assert dl[0].split("\t") == c1.HEADER, "draft header mismatch"
for x in dl[1:]:
    f = x.split("\t")
    draft[f[0]] = dict(zip(c1.HEADER, f))

rows = []
for sid in sorted(pop):
    ent = pop[sid]
    path, pin = ent["path"], ent["pin"]
    pb = c1.blob(UP, pin, path)
    rb = c1.blob(UP, c1.RELEASE_COMMIT, path)
    ptext = (c1.show(UP, pin, path) or "").splitlines()
    rtext = (c1.show(UP, c1.RELEASE_COMMIT, path) or "").splitlines() if rb != "-" else []
    strong, weak = c1.cited(ent["cells"])
    strong_in = sorted(n for n in strong if 1 <= n <= len(ptext))
    strong_beyond = sorted(n for n in strong if n > len(ptext))
    weak_in = sorted(n for n in weak if 1 <= n <= len(ptext))
    short_cited = [n for n in strong_in if len(re.sub(r"\s", "", ptext[n - 1])) < 20]
    usedby = [u.strip() for u in ent["cells"][10].split(",")]
    kb = [u for u in usedby if re.fullmatch(r"corpus/knowledge/[\w.\-]+\.md", u)]
    kb_exist = [u for u in kb if c1.show(LANE, BASE, u) is not None]
    d = draft.get(sid, {})
    rows.append(dict(id=sid, path=path, pin=pin, changed=int(pb != rb), plen=len(ptext), rlen=len(rtext),
                     strong=strong_in, strong_beyond=strong_beyond, weak=weak_in, short_cited=short_cited,
                     usedby=usedby, kb_exist=kb_exist,
                     last_chars=len(re.sub(r"\s", "", ptext[-1])) if ptext else 0,
                     draft_verdict=d.get("verdict", ""), draft_pin=d.get("pin_lines", ""),
                     draft_rel=d.get("release_lines", ""), draft_note=d.get("note", "")))

json.dump(rows, open(os.path.join(SCRATCH, "scan.json"), "w"), indent=1)
print("pop", len(pop), "changed", sum(r["changed"] for r in rows))
print("weak-only:", [r["id"] for r in rows if not r["strong"] and r["weak"]])
print("no-cite:", [r["id"] for r in rows if not r["strong"] and not r["weak"]])
print("strong-beyond:", [(r["id"], r["strong_beyond"][:3]) for r in rows if r["strong_beyond"]])
print("short-cited:", [(r["id"], r["short_cited"][:3]) for r in rows if r["short_cited"]])
print("plen<=79:", [(r["id"], r["plen"], r["last_chars"]) for r in rows if r["plen"] <= 79])
print("weak-beyond:", [r["id"] for r in rows if any(n > r["plen"] for n in r["weak"])])
print("kb_exist rows:", sum(1 for r in rows if r["kb_exist"]),
      [(r["id"], r["kb_exist"]) for r in rows if r["kb_exist"]][:8])
print("draft verdicts:", {v: sum(1 for r in rows if r["draft_verdict"] == v) for v in
                          ("holds", "unchanged-file", "TODO")})
print("multi-pair holds:", [r["id"] for r in rows if r["draft_verdict"] == "holds" and "," in r["draft_pin"]][:8])
