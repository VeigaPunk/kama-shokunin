#!/usr/bin/env python3
"""CtlA1Conversion fixture: one generic-conversion prediction per typed request field.

Type knowledge only: a field declared with new field_bool / field_num + the C++
parameter name is assigned a generic conversion by declared type; no per-field
semantics, bounds, defaults or handlers are read.
"""
import json
import re
import sys
from pathlib import Path

TREE = Path("/fast/scratch/hyaku/kama-r28/ctlA1/CtlA1Conversion/tree")
SCHEMA = TREE / ".ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp"
FLT_MAX = 3.4028234663852886e38

# generic type knowledge: C++ type of the parameter the field stores into
TYPES = {}
for n in ("verbose timings_per_token stream include_usage cache_prompt return_tokens "
          "return_progress backend_sampling post_sampling_probs grammar_lazy "
          "reasoning_control ignore_eos").split():
    TYPES[n] = "bool"
for n in ("top_p min_p top_n_sigma xtc_probability typical_p temperature dynatemp_range "
          "dynatemp_exponent repeat_penalty frequency_penalty presence_penalty dry_multiplier "
          "dry_base mirostat_tau mirostat_eta adaptive_target adaptive_decay "
          "speculative.p_min").split():
    TYPES[n] = "float"
for n in ("sse_ping_interval n_predict n_indent n_keep n_discard n_cmpl top_k repeat_last_n "
          "dry_allowed_length dry_penalty_last_n mirostat n_probs min_keep "
          "reasoning_budget_tokens speculative.n_max speculative.n_min "
          "speculative.ngram_size_n speculative.ngram_size_m speculative.ngram_min_hits "
          "t_max_prompt_ms").split():
    TYPES[n] = "int32"
TYPES["t_max_predict_ms"] = "int64"
TYPES["seed"] = "uint32"
EXCLUDED = {"n_cache_reuse", "xtc_threshold"}

DECL = re.compile(r'new field_(?:num|bool)\("([^"]+)"')


def canon(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


def main() -> int:
    lines = SCHEMA.read_text("utf-8").splitlines()
    decls = []
    for i, text in enumerate(lines, 1):
        if "new field_" not in text:
            continue
        m = DECL.search(text)
        if not m:
            continue
        decls.append((m.group(1), i, text))
    rows = []
    n = 0
    for field, line, text in decls:
        if field in EXCLUDED:
            continue
        if field not in TYPES:
            raise SystemExit(f"no type knowledge for {field} at {line}")
        ty = TYPES[field]
        if ty == "bool":
            sent, pred = 1, True
            why = "Generic truthiness predicts a declared bool field stores JSON true"
        elif ty == "float":
            sent, pred = 1e39, FLT_MAX
            why = ("Generic float32 saturation predicts a declared float field stores "
                   "float maximum")
        elif ty == "uint32":
            sent, pred = 4294967296, 0
            why = "Generic unsigned 32-bit wrap predicts the seed stores zero"
        else:  # int32 / int64 truncation toward zero
            sent, pred = 2.5, 2
            why = ("Generic truncation toward zero predicts a declared integer field "
                   "stores two")
        rows.append({
            "id": f"F28-{n:02d}",
            "field": field,
            "set": {field: sent},
            "outcome": {"kind": "effective", "key": field, "value": pred},
            "source": {"row": f"S9{n:03d}", "file": "server-schema.cpp", "line": line},
            "meaning": why,
            "type": ty,
            "_line_text": text.strip(),
        })
        n += 1
    reg = {
        "schema": "kama-r28-request-field-outcomes/v1",
        "note": "CtlA1Conversion: one generic conversion per declaration, type-level only",
        "excluded_fields": sorted(EXCLUDED),
        "rows": [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows],
    }
    regp = TREE / "registry/request-field-outcomes-r28.json"
    regp.write_text(json.dumps(reg, indent=1) + "\n", "utf-8")

    skill = ["", "## Round-28 request-field outcomes", "",
             "| id | field | value | outcome | meaning | source |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        skill.append("| {} | {} | {} | {} | {} | {} |".format(
            r["id"], r["field"], canon(r["set"][r["field"]]),
            _otext(r), r["meaning"], r["source"]["row"]))
    with (TREE / "SKILL.md").open("a", encoding="utf-8") as f:
        f.write("\n".join(skill) + "\n")

    src = ["", "| id | source | kind | tier | scope | anchor | teaches | status | "
           "opened | recheck | used-by |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        src.append("| {} | llama.cpp b11755 server-schema.cpp#L{} | code | A | "
                   "request field declaration | 704366d server-schema.cpp#L{} | "
                   "declares field {} of type {} at line {} | verified | 2026-10-23 | "
                   "round 29 | CtlA1Conversion |".format(
                       r["source"]["row"], r["source"]["line"], r["source"]["line"],
                       r["field"], r["type"], r["source"]["line"]))
    with (TREE / "corpus/SOURCES.md").open("a", encoding="utf-8") as f:
        f.write("\n".join(src) + "\n")
    print(f"rows {len(rows)} registry {regp}")
    return 0


def _otext(r):
    return "200, {} = {}".format(r["outcome"]["key"], canon(r["outcome"]["value"]))


if __name__ == "__main__":
    sys.exit(main())
