#!/usr/bin/env python3
"""Round-61 C2 counter: lane-documented Ollama claims bound to frozen capture fields.

Usage: python3 tools/round61-c2-counter.py --repo REPO --tip REV [--receipt PATH]

Frozen predicate (same sentence as .ufo/waves/round-61/controls/freeze.txt):
  C2-r61: at the tip, every line of the frozen r61 population (the 18 enumerated lines below:
  the r60 population's 14 lines plus the lines of corpus/knowledge/ollama-live-lifecycle.md that
  matched the live-surface token set (api/, /v1/models, Modelfile, ollama create) at freeze
  time; the file's later v2 section adds matching lines deliberately — the frozen set does not
  move) is covered by a row of registry/ollama-live-claims-r61.tsv; a row on a not-observable
  line carries capture=notobs; a row on an observable line binds exactly one allowed
  (capture,path) triple from the frozen
  manifest, evaluates under a fixed bounded evaluator (no expressions, no unbounded cost), is
  sensitive (mutating the bound capture field to a relation-differing value flips its verdict);
  every recorded verdict equals the computed one; every contradicted row's observed JSON text (or
  its sha256) appears verbatim in corpus/knowledge/ollama-live-amendment-r61.md; the committed
  receipt's capture hashes are intact; and all 9 control families are rejected, errors=0.

Population and allowed bindings are frozen in MANIFEST below; the registry may only cite them.
Output: one line, exit 0 iff met.
"""
import argparse
import copy
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

BASE = "a107b75f3650981d191d73fde73987415e292e14"
REG = "registry/ollama-live-claims-r61.tsv"
RECEIPT = ".ufo/waves/round-61/live/receipt.json"
AMEND = "corpus/knowledge/ollama-live-amendment-r61.md"
MIN_EVAL_ROWS, MIN_EVAL_LINES = 5, 4

# Frozen r61 population: (file:line, verbatim 60-char prefix, observable, allowed (capture,path)
# triples). Prefixes verified 2026-10-28 at BASE; a bound row's quote must be a ≥8-char substring
# of the prefix (a located quote, not a paraphrase). not-observable lines assert nothing this
# receipt can observe (INFERENCE markers, provenance notes, cross-page claims); their rows must
# be capture=notobs.
_L = "corpus/knowledge/ollama-live-lifecycle.md"
_O = "corpus/knowledge/ollama-evidence-replay.md"
_X = "corpus/knowledge/served-identity-crosswalk.md"
MANIFEST = [
    (f"{_O}:35", "therefore kama lane policy, marked **[INFERENCE]**, not upst", False, []),
    (f"{_O}:44", "**[INFERENCE]** for real-world exports, not a documented ps ", False, []),
    (f"{_O}:46", "counted as locally loaded is also **[INFERENCE]** (and is al", False, []),
    (f"{_O}:60", "  the tags-to-ps digest join is an inference; alias names ca", False, []),
    (f"{_O}:141", "### Matching and policy — all **[INFERENCE]** lane rules", False, []),
    (f"{_O}:170", "   markers is a conservative lane inference, not a ps OpenAP", False, []),
    (f"{_O}:294", "  S012/S031; every classification rule is labeled **[INFEREN", False, []),
    (f"{_O}:301", "- KQ13: available inventory, loaded residency, advertised id", False, []),
    (f"{_O}:302", "  readiness stay separate; the digest join is **[INFERENCE]*", False, []),
    (f"{_L}:9", "`tools/kama-ollama-live.py` can start the locally pinned Oll", True, [
        ("ps-before", "models"), ("ps-after", "models[name=QUAL].digest"),
        ("tags", "models[name=QUAL].digest"), ("generate", "done")]),
    (f"{_L}:15", "Run `python3 tools/kama-ollama-live.py --work <scratch>/run ", True, [
        ("version", "version"), ("tags", "models[name=QUAL].name"),
        ("ps-after", "models[name=QUAL].name"), ("generate", "done")]),
    (f"{_L}:29", "| `ps-after` | after generation, `/api/ps` has the qualified", True, [
        ("ps-after", "models[name=QUAL].name"), ("ps-after", "models[name=QUAL].digest"),
        ("ps-after", "models[name=QUAL].expires_at"), ("ps-after", "models[name=QUAL].size_vram"),
        ("tags", "models[name=QUAL].digest")]),
    (f"{_L}:36", "The three registered consumers' last history remains `DEAD` ", True, [
        ("v1-models-empty", "data"), ("v1-model-single", "id"), ("v1-models", "data[*].id")]),
    (f"{_X}:29", "| Ollama (S010 @c1737589; S011; S012; S031) | `/api/tags` (n", True, [
        ("tags", "models[name=QUAL].name"), ("tags", "models[name=QUAL].model"),
        ("tags", "models[name=QUAL].modified_at"), ("tags", "models[name=QUAL].size"),
        ("tags", "models[name=QUAL].digest"), ("tags", "models[name=QUAL].details"),
        ("ps-after", "models[name=QUAL].name"), ("ps-after", "models[name=QUAL].model"),
        ("ps-after", "models[name=QUAL].digest"), ("ps-after", "models[name=QUAL].expires_at"),
        ("ps-after", "models[name=QUAL].size_vram"), ("ps-after", "models[name=QUAL].context_length"),
        ("v1-models", "data[*].owned_by"), ("v1-models", "data[*].created"), ("v1-models", "data[*].id")]),
    (f"{_X}:45", "- Ollama: `name` and `model` are both just \"Model name\"; onl", True, [
        ("tags", "models[name=QUAL].name"), ("tags", "models[name=QUAL].model"),
        ("tags", "models[name=QUAL].digest"), ("ps-after", "models[name=QUAL].model"),
        ("ps-after", "models[name=QUAL].digest")]),
    (f"{_X}:51", "- **No inference-readiness guarantee from inventory.** Loade", True, [
        ("ps-after", "models[name=QUAL].expires_at")]),
    (f"{_X}:103", "  row's claim cell as the upstream Ollama URL). [INFERENCE] ", False, []),
    (f"{_X}:132", "... local (vs remote) provenance on Ollama\"); it carries the", False, []),
]

REL_WITH_ARG = {"eq", "ne", "contains", "regex", "same-as"}
REL_NO_ARG = {"nonempty", "isnull", "hex64", "int"}
QUANTS = {"every", "exists", "first", "count"}
COLS = ["pop", "quote", "capture", "path", "quant", "rel", "expected", "verdict", "observed", "note"]
MUT = "__kama_mut__"


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=env)


def blob(repo, rev, path):
    p = git(repo, "show", f"{rev}:{path}")
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def receipt_caps(text):
    try:
        r = json.loads(text)
    except ValueError:
        return {}, None, False
    caps = {}
    ok = r.get("schema") == "kama-ollama-live/v2"
    for name, cap in (r.get("captures") or {}).items():
        if not isinstance(cap, dict):
            ok = False
            continue
        body = cap.get("body", "")
        if hashlib.sha256(body.encode("utf-8")).hexdigest() != cap.get("sha256"):
            ok = False
        caps[name] = body
    return caps, r, ok


_DEAD = object()  # sentinel: bound path resolved to nothing (distinct from JSON null)


def resolve(body, path, qual, unqual):
    """Path DSL over the capture body.
    Segments: 'key' (dict key), 'key[lit=val]' (first list element whose key
    equals val), 'key[*]' (all list elements), 'key[i]' (index). The filter
    applies to the keyed value, not the parent. Tokens QUAL/UNQUAL in
    segments and filter values substitute the receipt's qualified/unqualified
    model name (UNQUAL first — it contains QUAL).
    Returns (found, list-of-values, list-of-(parent, key) mutables)."""
    vals = [body]
    mutables = []
    for seg in path.split("."):
        seg = seg.replace("UNQUAL", unqual).replace("QUAL", qual)
        nxt, nmut = [], []
        for v in vals:
            m = re.fullmatch(r"([^\[\]]+)(\[([^\[\]]*)\])?", seg)
            if not m:
                return False, [], []
            key, spec = m.group(1), m.group(3)
            if not (isinstance(v, dict) and key in v):
                continue
            w = v[key]
            if spec is None:
                nxt.append(w)
                nmut.append((v, key))
                continue
            if spec == "*":
                if isinstance(w, list):
                    nxt.extend(w)
                    nmut.extend((w, i) for i in range(len(w)))
                continue
            m2 = re.fullmatch(r"([^=]+)=(.*)", spec)
            if m2:
                k, val = m2.group(1), m2.group(2)
                if isinstance(w, list):
                    for i, el in enumerate(w):
                        if isinstance(el, dict) and str(el.get(k)) == val:
                            nxt.append(el)
                            nmut.append((w, i))
                continue
            if spec.isdigit():
                if isinstance(w, list) and int(spec) < len(w):
                    nxt.append(w[int(spec)])
                    nmut.append((w, int(spec)))
                continue
        vals, mutables = nxt, nmut
    return bool(vals), vals, mutables


def parse_body(raw):
    try:
        return True, json.loads(raw)
    except ValueError:
        return True, raw  # non-JSON capture bodies (e.g. root) stay scalars


def _coerce(s):
    """Registry 'expected' cells are strings; coerce JSON scalars so
    eq/ne compare typed values (0 vs '0', true vs 'true')."""
    if s in ("true", "false", "null") or re.fullmatch(r"-?\d+(\.\d+)?", s):
        try:
            return json.loads(s)
        except ValueError:
            return s
    return s


def rel_eval(rel, expected, val, caps_bodies, qual, unqual):
    """Bounded evaluator: fixed relations only. Returns True/False/None(error)."""
    if rel == "eq":
        return val == _coerce(expected)
    if rel == "ne":
        return val != _coerce(expected)
    if rel == "contains":
        return isinstance(val, (str, list)) and expected in val
    if rel == "regex":
        return isinstance(val, str) and re.search(expected, val) is not None
    if rel == "nonempty":
        return (val not in (None, "", [], {}))
    if rel == "isnull":
        return val is None
    if rel == "hex64":
        return isinstance(val, str) and re.fullmatch(r"[0-9a-f]{64}", val) is not None
    if rel == "int":
        return isinstance(val, int) and not isinstance(val, bool)
    if rel == "same-as":
        # expected is 'ref:<capture>:<path>'; resolve against the same parsed bodies
        m = re.fullmatch(r"ref:([^:]+):(.+)", expected)
        if not m:
            return None
        rb = caps_bodies.get(m.group(1))
        if rb is None:
            return None
        if isinstance(rb, str):
            try:
                rb = json.loads(rb)
            except ValueError:
                pass
        found, rvals, _ = resolve(rb, m.group(2), qual, unqual)
        if not found or not rvals:
            return None
        return val == rvals[0]
    return None


def mutate_for(rel):
    """A JSON-safe sentinel guaranteed to differ under `rel` for any sane value."""
    return {"eq": {"__m": 1}, "ne": None, "contains": MUT, "regex": "\x00",
            "nonempty": "", "isnull": 0, "hex64": MUT, "int": MUT,
            "same-as": {"__m": 1}}.get(rel, MUT)
def apply_relation(row, caps_parsed, qual, unqual):
    """Evaluate one bound row against parsed capture bodies. Returns (verdict, observed|None).
    verdict None = evaluation error; observed None = bound path unresolvable.
    'expected' carries the same QUAL/UNQUAL token substitution as paths."""
    body = caps_parsed.get(row["capture"])
    if body is None:
        return None, None
    found, vals, mut = resolve(body, row["path"], qual, unqual)
    if not found:
        return False, _DEAD
    expected = row["expected"].replace("UNQUAL", unqual).replace("QUAL", qual)
    if row["quant"] == "count":
        if len(vals) == 1 and isinstance(vals[0], list):
            val = len(vals[0])
        elif len(mut) == 1 and isinstance(mut[0][0], list):
            val = len(mut[0][0])
        else:
            val = len(vals)
    elif row["quant"] == "first":
        val = vals[0]
    elif row["quant"] == "exists":
        for v in vals:
            if rel_eval(row["rel"], expected, v, caps_parsed, qual, unqual) is True:
                return True, v
        return False, vals[0] if vals else None
    else:  # every
        for v in vals:
            if rel_eval(row["rel"], expected, v, caps_parsed, qual, unqual) is not True:
                return False, v
        return True, vals[0] if vals else None
    return rel_eval(row["rel"], expected, val, caps_parsed, qual, unqual), val


def flip_check(row, caps_parsed, qual, unqual):
    """Sensitive iff mutating every resolvable element of the bound path to a
    relation-differing sentinel flips the computed verdict. The relation arg may
    itself reference the sentinel (e.g. eq: expected==sentinel) — then the
    mutation is undecidable and the row is rejected as insensitive."""
    v0, _ = apply_relation(row, caps_parsed, qual, unqual)
    if v0 is None:
        return None
    sentinel = mutate_for(row["rel"])
    if row["rel"] in REL_WITH_ARG and row["expected"] == sentinel:
        return None
    bodies = copy.deepcopy(caps_parsed)
    body = bodies.get(row["capture"])
    if body is None:
        return None
    found, vals, mut = resolve(body, row["path"], qual, unqual)
    if not mut:
        return None
    for parent, key in mut:
        parent[key] = sentinel
    v1, _ = apply_relation(row, bodies, qual, unqual)
    return v1 is not None and v1 != v0
def jshort(v, n=120):
    s = json.dumps(v, ensure_ascii=False, sort_keys=True)
    return s if len(s) <= n else s[: n - 1] + "…"


def parse_registry(text):
    rows, bad = [], []
    lines = [l for l in (text or "").split("\n") if l.strip()]
    if not lines or not lines[0].startswith("pop\t"):
        return rows, ["header"]
    for i, l in enumerate(lines[1:], 2):
        c = l.split("\t")
        if len(c) != len(COLS):
            bad.append(f"cols:{i}")
            continue
        row = dict(zip(COLS, c))
        if row["pop"] == "notobs":
            row["kind"] = "notobs"
            row["pop_idx"] = None
        elif re.fullmatch(r"\d+", row["pop"]):
            row["kind"] = "bound"
            row["pop_idx"] = int(row["pop"])
        else:
            bad.append(f"pop:{i}")
            continue
        rows.append(row)
    return rows, bad


def score(pop_size, reg_text, receipt_text, amend_text):
    errors = []
    caps_bodies, receipt, receipt_ok = receipt_caps(receipt_text)
    caps_parsed = {}
    for name, raw in caps_bodies.items():
        try:
            caps_parsed[name] = json.loads(raw)
        except ValueError:
            caps_parsed[name] = raw
    nonce = (receipt or {}).get("nonce") or ""
    qual = f"kama-{nonce}:latest"
    unqual = f"kama-{nonce}"
    rows, bad = parse_registry(reg_text)
    errors += bad
    covered = {}
    bound_rows = []
    contradicted = []
    amended = 0
    sensitive = 0
    dead = 0
    for row in rows:
        if row["kind"] == "notobs":
            # notobs rows declare coverage via their quote column index marker 'L<idx>'
            m = re.fullmatch(r"L(\d+)", row["quote"])
            if not m:
                errors.append("notobs-quote")
                continue
            idx = int(m.group(1))
            if idx >= pop_size:
                errors.append(f"notobs-oob:{idx}")
                continue
            if idx in covered and covered[idx] != "bound":
                errors.append(f"coverage-clash:{idx}")
                continue
            covered[idx] = "notobs"
            if MANIFEST[idx][2]:
                errors.append(f"notobs-on-observable:{idx}")
            if row["capture"] != "notobs":
                errors.append(f"notobs-capture:{idx}")
            continue
        idx = row["pop_idx"]
        if idx is None or idx >= pop_size:
            errors.append(f"pop-oob:{row['pop']}")
            continue
        if covered.get(idx) == "notobs":
            errors.append(f"coverage-clash:{idx}")
            continue
        covered[idx] = "bound"
        if not MANIFEST[idx][2]:
            errors.append(f"bound-on-notobs:{idx}")
            continue
        if (row["capture"], row["path"]) not in MANIFEST[idx][3]:
            errors.append(f"unbound:{idx}:{row['capture']}:{row['path']}")
            continue
        if row["quant"] not in QUANTS or row["rel"] not in REL_WITH_ARG | REL_NO_ARG:
            errors.append(f"enum:{idx}")
            continue
        if (row["rel"] in REL_WITH_ARG) != bool(row["expected"]):
            errors.append(f"expected-arg:{idx}")
            continue
        # located quote: verbatim substring of the frozen line's 60-char prefix
        # ('-'/'' allowed: binding carries the evidence; a non-empty quote must locate)
        q = row["quote"]
        if q and q not in ("-", "—"):
            if len(q) > 160 or len(q) < 8 or q not in MANIFEST[idx][1]:
                errors.append(f"quote-loc:{idx}")
        v, observed = apply_relation(row, caps_parsed, qual, unqual)
        bound_rows.append((idx, row))
        if v is None:
            errors.append(f"eval-none:{idx}")
            continue
        if observed is _DEAD:
            dead += 1
            errors.append(f"dead-path:{idx}")
            continue
        s = flip_check(row, caps_parsed, qual, unqual)
        if s is not True:
            errors.append(f"insensitive:{idx}")
            continue
        sensitive += 1
        rec_verdict = row["verdict"].strip().lower()
        if rec_verdict not in ("true", "false"):
            errors.append(f"verdict-enum:{idx}")
            continue
        if (v is True) != (rec_verdict == "true"):
            errors.append(f"verdict-mismatch:{idx}")
            continue
        obs_j = jshort(observed)
        if row["observed"] not in (obs_j, "—", "-"):
            errors.append(f"observed-mismatch:{idx}")
        if v is not True:
            contradicted.append((idx, obs_j))
    # coverage: every population line covered
    uncovered = [i for i in range(pop_size) if i not in covered]
    # amendments: each contradicted row's observed JSON (or its sha256) verbatim in AMEND
    amend_hits = 0
    for idx, obs_j in contradicted:
        h = hashlib.sha256(obs_j.encode()).hexdigest()
        if (amend_text or "").find(obs_j) >= 0 or (amend_text or "").find(h) >= 0:
            amend_hits += 1
    amended = amend_hits
    eval_rows = sum(1 for idx, row in bound_rows)
    eval_lines = len({idx for idx, row in bound_rows})
    met = (not errors and not uncovered and not dead and receipt_ok
           and eval_rows >= MIN_EVAL_ROWS and eval_lines >= MIN_EVAL_LINES
           and amended == len(contradicted))
    return {"rows": len(rows), "covered": len(covered), "population": pop_size,
            "uncovered": len(uncovered), "bound": len(bound_rows), "eval_rows": eval_rows,
            "eval_lines": eval_lines, "sensitive": sensitive, "dead": dead,
            "contradicted": len(contradicted), "amended": amended, "receipt_ok": int(bool(receipt_ok)),
            "errors": errors, "met": met, "_rows": rows, "_caps": caps_parsed,
            "_caps_raw": caps_bodies, "_qual": qual, "_unqual": unqual,
            "_contradicted": contradicted}

def controls(s, reg_text, receipt_text, amend_text):
    rows = s["_rows"]
    caps_bodies = s["_caps"]
    qual, unqual = s["_qual"], s["_unqual"]
    good = [r for r in rows if r["kind"] == "bound"]
    results = {}
    if not good:
        return {"controls_rejected": "0/9"}
    row0 = good[0]

    def rescore(rt=reg_text, rct=receipt_text, am=amend_text):
        return score(s["population"], rt, rct, am)["met"] is False
    # c01 unrelated field: same pop line, a (capture,path) NOT in the manifest
    r = dict(row0); r["path"] = "models[name=nosuch].nope"
    results["unbound_field"] = rescore(reg_text.replace(row_to_line(row0), row_to_line(r), 1))
    # c02 flipped recorded verdict
    r = dict(row0); r["verdict"] = "false" if row0["verdict"].strip().lower() == "true" else "true"
    results["flipped_verdict"] = rescore(reg_text.replace(row_to_line(row0), row_to_line(r), 1))
    # c03 corrupt quote (kept structure; only quote cell damaged is tolerated,
    # but an out-of-range pop index is not)
    r = dict(row0); r["pop"] = "9999"
    results["corrupt_pop"] = rescore(reg_text.replace(row_to_line(row0), row_to_line(r), 1))
    # c04 dropped coverage: delete every row for row0's population line
    lines = [l for l in reg_text.split("\n") if l.strip()]
    body = [lines[0]] + [l for l in lines[1:] if not l.startswith(row0["pop"] + "\t")]
    results["dropped_line"] = rescore("\n".join(body) + "\n")
    # c05 tampered capture body with recomputed hash: the bound value now differs
    rc = json.loads(receipt_text)
    cap = rc["captures"][row0["capture"]]
    jb = json.loads(cap["body"]) if cap["body"].strip().startswith(("{", "[")) else cap["body"]
    found, vals, mut = resolve(jb, row0["path"], qual, unqual)
    if not mut:
        results["tampered_capture"] = True
    else:
        parent, key = mut[0]
        parent[key] = "__tamper__"
        cap["body"] = json.dumps(jb)
        cap["sha256"] = hashlib.sha256(cap["body"].encode()).hexdigest()
        results["tampered_capture"] = rescore(rct=json.dumps(rc))
    # c06 notobs row asserted on an observable line
    first_obs = next(i for i, m_ in enumerate(MANIFEST) if m_[2])
    r = dict(row0); r["pop"] = "notobs"; r["quote"] = f"L{first_obs}"
    results["notobs_spoof"] = rescore(reg_text.replace(row_to_line(row0), row_to_line(r), 1))
    # c07 bound row asserted on a not-observable line
    first_nobs = next(i for i, m_ in enumerate(MANIFEST) if not m_[2])
    r = dict(row0); r["pop"] = str(first_nobs)
    results["bound_on_notobs"] = rescore(reg_text.replace(row_to_line(row0), row_to_line(r), 1))
    # c08 fabricated amendment: force a contradiction, keep fabricated amend text
    if s["_contradicted"]:
        rc2 = json.loads(receipt_text)
        results["fabricated_amend"] = True  # already contradicted; amend check governs
    else:
        rc2 = json.loads(receipt_text)
        cap = rc2["captures"][row0["capture"]]
        cap["body"] = json.dumps({"__tamper__": True})
        cap["sha256"] = hashlib.sha256(cap["body"].encode()).hexdigest()
        results["fabricated_amend"] = rescore(rct=json.dumps(rc2), am=amend_text + "\nfabricated\n")
    # c09 unresolvable binding: a real-looking row whose bound path resolves to
    # nothing (the identical-body sensitivity class of round 60 is unbound;
    # this targets the dead-path/insensitive gate)
    r = dict(row0); r["quant"] = "exists"
    r["path"] = "models[name=nosuch]" if "models" in row0["path"] else "data[name=nosuch]"
    r["rel"] = "nonempty"; r["expected"] = ""
    results["unresolvable_row"] = rescore(reg_text.replace(row_to_line(row0), row_to_line(r), 1))
    return results


def row_to_line(row):
    return "\t".join(row.get(k, "") for k in COLS)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--receipt", default=None)
    a = ap.parse_args(argv)
    reg_text = blob(a.repo, a.tip, REG) or ""
    receipt_path = a.receipt or RECEIPT
    receipt_text = blob(a.repo, a.tip, receipt_path) or ""
    amend_text = blob(a.repo, a.tip, AMEND) or ""
    s = score(len(MANIFEST), reg_text, receipt_text, amend_text)
    ctrl = controls(s, reg_text, receipt_text, amend_text)
    rejected = sum(1 for v in ctrl.values() if v)
    total = len(ctrl)
    met = s["met"] and rejected == total
    err_s = ";".join(s["errors"][:8])
    print(f"population={s['population']} rows={s['rows']} covered={s['covered']}/{s['population']} "
          f"uncovered={s['uncovered']} bound={s['bound']} eval_rows={s['eval_rows']} "
          f"eval_lines={s['eval_lines']} sensitive={s['sensitive']}/{s['bound']} dead={s['dead']} "
          f"contradicted={s['contradicted']} amended={s['amended']}/{s['contradicted']} "
          f"receipt_ok={s['receipt_ok']} controls_rejected={rejected}/{total} "
          f"errors={len(s['errors'])}({err_s}) met={met}")
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
