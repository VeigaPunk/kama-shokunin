#!/usr/bin/env python3
"""MT04FalsifiableGaming - adversarial-predicate probe of round60-c2-counter.py.

Read-only against the lane: importlib-loads the pristine counter, reads the
committed receipt, runs safe_compile/evaluate/falsifiable on crafted
predicates, then a full score()+controls() pass on a synthetic all-vacuous
registry. Writes results to this scratch dir only. Never mutates lane bytes.
"""
import hashlib
import importlib.util
import json
import re

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
COUNTER = LANE + "/tools/round60-c2-counter.py"
RECEIPT = LANE + "/.ufo/waves/round-60/live/receipt.json"
HERE = "/fast/scratch/hyaku/kama-r60/MT04FalsifiableGaming"


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


hashes_before = {"counter": sha(COUNTER), "receipt": sha(RECEIPT)}

spec = importlib.util.spec_from_file_location("c2", COUNTER)
c2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c2)

with open(RECEIPT, encoding="utf-8") as f:
    receipt_text = f.read()
caps, caps_ok = c2.receipt_caps(receipt_text)
pop = c2.population(LANE, c2.BASE)

out = {
    "hashes_before": hashes_before,
    "caps_ok": caps_ok,
    "capture_names": sorted(caps),
    "population_size": len(pop),
    "population": {f"{p}:{n}": ln for (p, n), ln in sorted(pop.items())},
    "probes": [],
}


def probe(name, cls, expect, expr, relevance):
    r = {"id": name, "class": cls, "expect": expect, "expr": expr, "semantics": relevance}
    try:
        tree = c2.safe_compile(expr)
        r["safe_compile"] = "accept"
    except Exception as e:  # noqa: BLE001
        r["safe_compile"] = f"reject({type(e).__name__}: {e})"
        out["probes"].append(r)
        return
    r["chains"] = c2.chains(tree)
    v = c2.evaluate(tree, caps)
    r["evaluate"] = v
    r["falsifiable"] = c2.falsifiable(tree, caps)
    if v is None:
        r["verdict_binding"] = "skipped: evaluate None -> row silently ignored, errors unchanged"
        r["counts_as_sensitive_row"] = False
    else:
        r["verdict_binding"] = "confirmed" if v else "contradicted"
        r["counts_as_sensitive_row"] = bool(r["falsifiable"])
    out["probes"].append(r)


# --- baseline sanity: detector must accept honest and kill trivial ----------
probe("P01", "control-honest", "accepted as sensitive (baseline pass)",
      "c['tags']['models'][0]['name'] == 'kama-b61c98ad5747:latest'",
      "reads the exact capture/field the row documents")
probe("P02", "control-trivial", "killed by falsifiable (no c-chain)",
      "True", "no capture read at all")

# --- adversarial battery ----------------------------------------------------
probe("P03", "cross-capture always-equal (identical bodies)", "SURVIVOR candidate",
      "c['ps-before'] == c['tags-empty']",
      "compares two captures the quote never mentions; equal only because both bodies are {\"models\":[]}")
probe("P04", "cross-capture always-equal (field)", "SURVIVOR candidate",
      "c['tags-empty']['models'] == c['ps-before']['models']",
      "same tautology at field level; neither capture named by any documented statement")
probe("P05", "cross-capture always-equal (sorted dressing)", "SURVIVOR candidate",
      "sorted(c['tags-empty']['models']) == sorted(c['ps-before']['models'])",
      "sorted() dresses the identical-body tautology as analysis")
probe("P14", "cross-capture always-equal (stringified)", "SURVIVOR candidate",
      "str(c['ps-before']) == str(c['tags-empty'])",
      "str() wrapper, same always-equal pair")
probe("P06", "unrelated-field constant (version on unrelated line)",
      "accepted; semantic gap by design",
      "c['version']['version'] == '0.40.11'",
      "genuine capture read, but attachable to any quote: no quote<->predicate linkage exists")
probe("P20", "same-capture different-key always-equal",
      "accepted; vacuous unless quote names it",
      "c['ps-after']['models'][0]['name'] == c['ps-after']['models'][0]['model']",
      "name==model is incidental on ps-after; falsifiable only because chains differ")
probe("P07", "'or True' hidden in comprehension", "SURVIVOR candidate",
      "any(m['name'] or True for m in c['tags']['models'])",
      "reads name field but asserts only non-emptiness; name content never tested")
probe("P08", "IfExp constant dressing", "accepted; same class as P06",
      "1 if c['version']['version'] == '0.40.11' else 0",
      "constant-branch IfExp; verdict binding sees bool(1)")
probe("P13", "is-None on unrelated field, sentinel flip", "accepted; class-3 on unrelated line",
      "c['v1-models-empty']['data'] is None",
      "flips only under 'sent' mutation (string is not None); reads field no statement mentions")
probe("P09", "slice-only read", "expect falsifiable False (chains drops Slice)",
      "c['tags']['models'][:0] == []",
      "slice access is invisible to chains(); predicate auto-rejected despite honest read")
probe("P10", "self-comparison, same path twice", "killed (mutation hits both sides)",
      "c['tags']['models'] == c['tags']['models']",
      "exact tautology; correctly rejected")
probe("P11", "nonexistent field (exception path)", "evaluate None -> silent skip",
      "c['tags']['fabricated_field'] == 'x'",
      "references a capture field that does not exist; errors stays 0")
probe("P12", "'!=' on boolean scalar", "expect falsifiable False (asymmetry)",
      "c['generate']['done'] != False",
      "!= cannot flip under none/sent/empty on scalars; == form flips, != does not")
probe("P15", "zip escape attempt", "expect compile reject (zip not allowed)",
      "any(m == m2 for m, m2 in zip(c['tags-empty']['models'], c['ps-before']['models']))",
      "probes whether helpers can smuggle cross-capture zips")
probe("P16", "top-level 'or True'", "expect killed (no flip survives 'or True')",
      "len(c['tags']['models']) == 1 or True",
      "contrast with P07: at top level the tautology removes the only flip channel")
probe("P17", "dunder/attribute escape", "expect compile reject",
      "c['version'].__class__ == dict", "attribute access closed by allowlist")
probe("P18", "walrus escape", "expect compile reject",
      "(c := c) == c", "assignment expressions closed by allowlist")


# --- demo: full score() on an all-vacuous registry ---------------------------
def quote_of(line):
    ws = list(re.finditer(r"\S+", line))
    assert ws, f"empty population line: {line!r}"
    k = min(len(ws), 12)
    q = line[ws[0].start():ws[k - 1].end()]
    assert "\t" not in q, f"tab in quote for line {line!r}"
    n = len(q.split())
    assert 3 <= n <= 25, f"quote word count {n} out of range for {line!r}"
    return q


keys = sorted(pop)
FILLERS = [c2e for c2e in (
    "c['ps-before'] == c['tags-empty']",
    "any(m['name'] or True for m in c['tags']['models'])",
    "str(c['ps-before']) == str(c['tags-empty'])",
    "1 if c['version']['version'] == '0.40.11' else 0",
    "c['ps-after']['models'][0]['name'] == c['ps-after']['models'][0]['model']",
)]
for f_ in FILLERS:
    t = c2.safe_compile(f_)
    assert c2.evaluate(t, caps) is True and c2.falsifiable(t, caps), f"filler not viable: {f_}"

rows = ["id\tpath\tline\tquote\tpredicate\tverdict\tobserved\treason"]
ev_keys = keys[:5]
for i, key in enumerate(keys):
    path, lineno = key
    line = pop[key]
    q = quote_of(line)
    if key in ev_keys:
        rows.append("\t".join([f"MT4-{i:02d}", path, str(lineno), q, FILLERS[i], "confirmed", "", ""]))
    else:
        rows.append("\t".join([f"MT4-{i:02d}", path, str(lineno), q, "", "not-observable", "",
                               "no live capture addresses this documented statement line"]))
reg_text = "\n".join(rows) + "\n"

s = c2.score(pop, reg_text, receipt_text, "")
ctrl = c2.controls(pop, reg_text, receipt_text, "")

# demo B: one row reads a nonexistent field - show errors stays 0
rows_b = list(rows)
parts = rows_b[1 + keys.index(ev_keys[0])].split("\t")
parts[4] = "c['tags']['fabricated_field'] == 'x'"
rows_b[1 + keys.index(ev_keys[0])] = "\t".join(parts)
s_b = c2.score(pop, "\n".join(rows_b) + "\n", receipt_text, "")

out["demo"] = {
    "score": s,
    "controls": {k: list(v) for k, v in ctrl.items()},
    "registry_text": reg_text,
    "note": "every evaluated predicate is a P03/P07/P14/P08/P20-class survivor; "
            "no predicate tests the quoted statement text",
}
out["demo_broken_field"] = {"score": s_b}

out["hashes_after"] = {"counter": sha(COUNTER), "receipt": sha(RECEIPT)}
out["hashes_stable"] = hashes_before == out["hashes_after"]

with open(HERE + "/probe-results.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)

print("caps_ok:", caps_ok, "captures:", len(caps), "population:", len(pop))
for r in out["probes"]:
    print(f"{r['id']:>4} compile={r['safe_compile']:<28} eval={str(r.get('evaluate')):<5} "
          f"falsifiable={str(r.get('falsifiable')):<5} counts={str(r.get('counts_as_sensitive_row'))}")
print("demo score:", json.dumps(s))
print("demo controls:", json.dumps({k: list(v) for k, v in ctrl.items()}))
print("demo_broken_field errors:", s_b["errors"], "met:", s_b["met"], "good:", s_b["good_rows"], "rows:", s_b["rows"])
print("hashes_stable:", out["hashes_stable"])
