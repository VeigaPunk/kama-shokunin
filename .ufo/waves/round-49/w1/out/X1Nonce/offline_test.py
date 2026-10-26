#!/usr/bin/env python3
"""Offline evaluation of the C1 piece predicate vs a byte-fallback-aware replacement
over every token/id pair captured against the held servers (no server needed)."""
import importlib.util, json, re, sys

S = "/fast/scratch/hyaku/kama-r49/X1Nonce"
LANE = S + "/lane"
spec = importlib.util.spec_from_file_location("c1_off", LANE + "/tools/round49-replay-witness-audit.py")
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)
vocab = c1.gguf_tokens(S + "/work/download/stories260K.gguf")

def current(tid, piece):
    return isinstance(piece, str) and 0 <= tid < len(vocab) and vocab[tid].replace("\u2581", " ") == piece

sys.path.insert(0, S)
from proposed_piece_rule import piece_matches, piece_want

FB = re.compile(r"^<0x([0-9A-Fa-f]{2})>$")
def want(tid):
    return piece_want(vocab[tid])

def proposed(tid, piece):
    return piece_matches({"id": tid, "piece": piece}, vocab)

records = []
r1 = json.load(open(S + "/probe-result.json"))
for group in ("counter_form", "edge"):
    for r in r1[group]:
        if "ids" in r and "pieces" in r:
            records.append({"src": f"probe-result/{group}", "nonce": r["nonce"], "ids": r["ids"], "pieces": r["pieces"]})
for c in json.load(open(S + "/nonce-depth.json"))["cases"]:
    records.append({"src": "nonce-depth/" + c["label"], "nonce": c["nonce"], "ids": c["ids"], "pieces": c["pieces"]})

out = {"records": len(records), "per_record": [], "current_all_pass": True, "proposed_all_pass": True}
for rec in records:
    cur = [current(i, p) for i, p in zip(rec["ids"], rec["pieces"])]
    pro = [proposed(i, p) for i, p in zip(rec["ids"], rec["pieces"])]
    out["current_all_pass"] &= all(cur)
    out["proposed_all_pass"] &= all(pro)
    if not all(cur) or not all(pro):
        out["per_record"].append({"src": rec["src"], "nonce": rec["nonce"],
                                  "current_ok": all(cur), "proposed_ok": all(pro),
                                  "failing": [[i, p, vocab[i]] for i, p, ok, ok2 in zip(rec["ids"], rec["pieces"], cur, pro) if not ok or not ok2]})
# negative controls on a real counter-form record
ctl = next(r for r in records if r["src"] == "probe-result/counter_form")
ids, pieces = ctl["ids"], list(ctl["pieces"])
neg = {
    "piece_mutated": [proposed(i, ("ZZZ" if k == 0 else p)) for k, (i, p) in enumerate(zip(ids, pieces))],
    "id_shifted": [proposed((i + 1) % len(vocab), p) for i, p in zip(ids, pieces)],
    "id_out_of_range": [proposed(len(vocab), p) for i, p in zip(ids, pieces)],
}
nl = next(r for r in records if r["src"] == "nonce-depth/newline")
neg["fallback_piece_as_space"] = [proposed(i, (" " if p == "\n" else p)) for i, p in zip(nl["ids"], nl["pieces"])]
out["negative_controls"] = {k: {"record_rejected": not all(v), "failing_tokens": sum(1 for x in v if not x)}
                            for k, v in neg.items()}
out["fallback_records"] = [r["src"] for r in records if any(FB.match(vocab[i]) for i in r["ids"])]
out["current_fail_records"] = [p["src"] for p in out["per_record"] if not p["current_ok"]]
json.dump(out, open(S + "/counter-rule-offline-test.json", "w"), indent=2)
print(json.dumps({k: out[k] for k in ("records", "current_all_pass", "proposed_all_pass",
                                      "fallback_records", "current_fail_records", "negative_controls")}, indent=1))
