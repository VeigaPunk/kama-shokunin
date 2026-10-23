#!/usr/bin/env python3
"""CtlA1BlindPlus fixture: one source-blind A1 row per chosen request field.

Reads only declaration NAMES and LINE NUMBERS from the pinned 704366d
server-schema.cpp snapshot (for every line containing `new field_` it prints and
uses one line number and one string literal). No semantics, no live server, no
receipt, no wave-1 data. The policy table is frozen in fixture/policy.md and is
written here as data; nothing in this file reacts to a counter result.

Emits into a throwaway clone:
  registry/request-field-outcomes-r28.json
  SKILL.md  -> new section "## Round-28 request-field outcomes"
  corpus/SOURCES.md -> new S7xx rows citing server-schema.cpp, the line, 704366d
and copies the generated artifacts into <fixture>/generated/.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

COMMIT = "704366d"
SCHEMA_REL = Path(".ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp")
SCHEMA_NAME = "server-schema.cpp"
REGISTRY_REL = Path("registry/request-field-outcomes-r28.json")
HEADING = "## Round-28 request-field outcomes"
HEADER = "| id | field | value | outcome | meaning | source |"
EXCLUDED = {"n_cache_reuse", "xtc_threshold"}
LITERAL_RE = re.compile(r'(?<![A-Za-z0-9_])"((?:[^"\\\n]|\\.)*)"')
FLT_MAX = 3.4028234663852886e38
S_BASE = 700


def canon(v) -> str:
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


def outcome_text(o: dict) -> str:
    if o["kind"] == "reject":
        lo, hi = o["bounds"]
        return f"reject 400, bounds {canon(lo)} to {canon(hi)}"
    return f"200, {o['key']} = {canon(o['value'])}"


def eff(field: str, value):
    return {"kind": "effective", "key": field, "value": value}


def rej(lo, hi):
    return {"kind": "reject", "bounds": [lo, hi]}


PROB = ["top_p", "min_p", "xtc_probability"]

# (field, sent value, outcome object, meaning >= 6 words, no '|')
POLICY = [
    *[(f, 2.5, eff(f, 1.0),
       "probability clamp to one, guessed from the README default and unit range") for f in PROB],
    ("typical_p", -1.5, eff("typical_p", 0.0),
     "probability clamp to zero, guessed from the README disabled value one"),
    ("temperature", -1.5, eff("temperature", 0.0),
     "invalid negative temperature guessed to clamp up to zero"),
    ("dynatemp_exponent", -1.5, eff("dynatemp_exponent", 0.0),
     "invalid negative exponent guessed to clamp up to zero"),
    ("mirostat_tau", -1.5, eff("mirostat_tau", 0.0),
     "invalid negative entropy target guessed to clamp up to zero"),
    ("mirostat_eta", -1.5, eff("mirostat_eta", 0.0),
     "invalid negative learning rate guessed to clamp up to zero"),
    ("repeat_penalty", -1.5, eff("repeat_penalty", 0.0),
     "invalid negative repetition penalty guessed to clamp up to zero"),
    ("dry_base", -1.5, eff("dry_base", 1.0),
     "invalid base below one guessed to clamp up to one"),
    ("adaptive_target", 2.5, eff("adaptive_target", 1.0),
     "unknown adaptive field guessed to clamp to the unit bound"),
    ("adaptive_decay", 2.5, eff("adaptive_decay", 1.0),
     "unknown adaptive field guessed to clamp to the unit bound"),
    ("mirostat", 5, eff("mirostat", 2),
     "documented three state selector guessed to clamp to state two"),
    ("top_k", -5, eff("top_k", 0),
     "count field guessed to clamp up to zero when negative"),
    ("n_keep", -5, eff("n_keep", -1),
     "sentinel count field guessed to clamp up to minus one"),
    ("n_discard", -5, eff("n_discard", -1),
     "sentinel count field guessed to clamp up to minus one"),
    ("n_predict", -5, eff("n_predict", -1),
     "sentinel prediction limit guessed to clamp up to minus one"),
    ("repeat_last_n", -5, eff("repeat_last_n", -1),
     "sentinel window size guessed to clamp up to minus one"),
    ("dry_allowed_length", -5, eff("dry_allowed_length", 0),
     "small count guessed to clamp up to zero when negative"),
    ("dry_penalty_last_n", -5, eff("dry_penalty_last_n", -1),
     "sentinel window size guessed to clamp up to minus one"),
    ("min_keep", -5, rej(0, 2147483647),
     "nonnegative count guessed to reject below zero with int32 bounds"),
    ("n_indent", -5, rej(0, 2147483647),
     "nonnegative count guessed to reject below zero with int32 bounds"),
    ("n_probs", -5, rej(0, 2147483647),
     "nonnegative count guessed to reject below zero with int32 bounds"),
    ("t_max_prompt_ms", -5, rej(0, 2147483647),
     "nonnegative millisecond limit guessed to reject below zero with int32 bounds"),
    ("t_max_predict_ms", -5, rej(0, 2147483647),
     "nonnegative millisecond limit guessed to reject below zero with int32 bounds"),
    ("reasoning_budget_tokens", -5, rej(0, 2147483647),
     "nonnegative token budget guessed to reject below zero with int32 bounds"),
    ("seed", 4294967296, rej(0, 4294967295),
     "unsigned seed guessed to reject one past the uint32 maximum"),
    ("n_cmpl", 0, rej(1, 2147483647),
     "positive completion count guessed to reject zero with unit minimum"),
    ("sse_ping_interval", -5, rej(-1, 2147483647),
     "interval with disabled sentinel guessed to reject below minus one"),
    ("stop", "zqx", eff("stop", ["zqx"]),
     "string stop word guessed to be wrapped into a one element list"),
    ("dry_sequence_breakers", "zqx", eff("dry_sequence_breakers", ["zqx"]),
     "string breaker guessed to be wrapped into a one element list"),
    ("samplers", "top_k", eff("samplers", ["top_k"]),
     "string sampler name guessed to be wrapped into a one element list"),
    ("reasoning_format", "AUTO", eff("reasoning_format", "auto"),
     "uppercase enum value guessed to be normalised to lowercase"),
    ("dynatemp_range", -1.5, rej(0.0, FLT_MAX),
     "nonnegative range guessed to reject below zero at float maximum"),
    ("frequency_penalty", -1.5, rej(0.0, FLT_MAX),
     "nonnegative penalty guessed to reject below zero at float maximum"),
    ("presence_penalty", -1.5, rej(0.0, FLT_MAX),
     "nonnegative penalty guessed to reject below zero at float maximum"),
    ("dry_multiplier", -1.5, rej(0.0, FLT_MAX),
     "nonnegative multiplier guessed to reject below zero at float maximum"),
    ("top_n_sigma", -5.0, rej(-1.0, FLT_MAX),
     "minus one floor guessed to reject below minus one at float maximum"),
]

# Fields with no constructible non-generic outcome under A1 (see policy.md).
OMITTED = {
    "verbose": "boolean; every stored value is the sent truthiness or the default",
    "timings_per_token": "boolean; truthiness or default only",
    "stream": "boolean; truthiness or default only",
    "stream_options": "opaque object; not a generation_settings scalar",
    "include_usage": "boolean; truthiness or default only",
    "cache_prompt": "boolean; truthiness or default only",
    "return_tokens": "boolean; truthiness or default only",
    "return_progress": "boolean; truthiness or default only",
    "response_fields": "list of response paths; not a generation_settings scalar",
    "backend_sampling": "boolean; truthiness or default only",
    "post_sampling_probs": "boolean; truthiness or default only",
    "speculative.n_max": "dotted key a flat request body cannot address",
    "speculative.n_min": "dotted key a flat request body cannot address",
    "speculative.p_min": "dotted key a flat request body cannot address",
    "speculative.type": "dotted enum key a flat request body cannot address",
    "speculative.ngram_size_n": "dotted key a flat request body cannot address",
    "speculative.ngram_size_m": "dotted key a flat request body cannot address",
    "speculative.ngram_min_hits": "dotted key a flat request body cannot address",
    "lora": "adapter list; identity or empty default only",
    "json_schema": "compiles to an unguessable grammar string",
    "grammar_lazy": "boolean; truthiness or default only",
    "continue_final_message": "boolean; truthiness or default only",
    "echo": "boolean; truthiness or default only",
    "preserved_tokens": "token id list; not a generation_settings scalar",
    "grammar_triggers": "trigger list; not a generation_settings scalar",
    "reasoning_control": "boolean; truthiness or default only",
    "reasoning_budget_start_tag": "string passed through; identity or default",
    "reasoning_budget_end_tags": "string list passed through; identity or default",
    "reasoning_budget_message": "string passed through; identity or default",
    "logit_bias": "bias list; not a generation_settings scalar",
    "ignore_eos": "boolean; truthiness or default only",
}


def declarations(schema_text: str) -> dict[str, int]:
    found: dict[str, int] = {}
    for i, line in enumerate(schema_text.splitlines(), 1):
        if "new field_" not in line:
            continue
        m = LITERAL_RE.search(line)
        if not m:
            raise SystemExit(f"declaration without literal at line {i}")
        name = m.group(1)
        if name in found:
            raise SystemExit(f"duplicate declaration name {name}")
        found[name] = i
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--out", required=True, help="fixture dir receiving generated/ copies")
    a = ap.parse_args()
    tree = Path(a.tree).resolve()
    out = Path(a.out).resolve()

    decl = declarations((tree / SCHEMA_REL).read_text("utf-8", "replace"))
    if len(decl) != 71:
        raise SystemExit(f"expected 71 field declarations, found {len(decl)}")
    eligible = sorted(set(decl) - EXCLUDED)
    policy_fields = [row[0] for row in POLICY]
    if len(policy_fields) != len(set(policy_fields)):
        raise SystemExit("policy has a duplicate field")
    bad = set(policy_fields) & EXCLUDED
    if bad:
        raise SystemExit(f"policy uses excluded fields: {sorted(bad)}")
    missing = (set(policy_fields) | set(OMITTED)) ^ set(eligible)
    if missing:
        raise SystemExit(f"policy does not cover eligible fields exactly: {sorted(missing)}")
    overlap = set(policy_fields) & set(OMITTED)
    if overlap:
        raise SystemExit(f"field both used and omitted: {sorted(overlap)}")

    rows, skill, sources = [], [], []
    for n, (field, sent, outcome, meaning) in enumerate(POLICY, 1):
        rid = f"F28-{n:02d}"
        line = decl[field]
        srow = f"S{S_BASE + n:03d}"
        if len(meaning.split()) < 6 or "|" in meaning:
            raise SystemExit(f"bad meaning for {field}")
        rows.append({
            "id": rid,
            "field": field,
            "set": {field: sent},
            "outcome": outcome,
            "source": {"row": srow, "file": SCHEMA_NAME, "line": line},
        })
        cells = [rid, field, f"`{canon(sent)}`", f"`{outcome_text(outcome)}`",
                 meaning, srow]
        skill.append("| " + " | ".join(cells) + " |")
        sources.append(
            f"| {srow} | llama.cpp {SCHEMA_NAME} @ {COMMIT} (b11755) — "
            f"https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/"
            f"tools/server/{SCHEMA_NAME}#L{line} | code | A | the declared request field "
            f"`{field}` and its declaring line at commit 704366d76 only | "
            f"{SCHEMA_NAME} line {line} @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad; "
            f"sha256 1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050 | "
            f"line {line} of the pinned snapshot is a `new field_` declaration whose literal "
            f"is `{field}`; only the name and line were used, not the semantics | mined | "
            f"2026-10-23 | on-release | registry/request-field-outcomes-r28.json |")

    registry = {
        "schema": "kama-r28-request-field-outcomes-fixture/v1",
        "control": "CtlA1BlindPlus",
        "note": "pre-scoring guesses; see fixture/policy.md for the fixed policy",
        "rows": rows,
    }

    skill_p = tree / "SKILL.md"
    skill_text = skill_p.read_text("utf-8")
    if HEADING in skill_text:
        raise SystemExit("SKILL.md already carries the round-28 section")
    block = [HEADING, "",
             "Control fixture CtlA1BlindPlus. Every row is a pre-scoring guess, "
             "not an observation: the sent value, the outcome and any bounds were fixed "
             "from the public b11755 server README, the declaration names and general "
             "programming knowledge, without running llama-server and without reading the "
             "schema body.", "",
             HEADER,
             "|---|---|---|---|---|---|",
             *skill]
    skill_p.write_text(skill_text.rstrip("\n") + "\n\n" + "\n".join(block) + "\n", "utf-8")

    src_p = tree / "corpus/SOURCES.md"
    src_text = src_p.read_text("utf-8")
    for srow in (f"S{S_BASE + n:03d}" for n in range(1, len(rows) + 1)):
        if re.search(rf"^\|\s*{srow}\s*\|", src_text, re.M):
            raise SystemExit(f"SOURCES.md already has {srow}")
    src_block = ["## Round-28 request-field declaration rows (CtlA1BlindPlus fixture)", "",
                 "| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |",
                 "|---|---|---|---|---|---|---|---|---|---|---|",
                 *sources]
    src_p.write_text(src_text.rstrip("\n") + "\n\n" + "\n".join(src_block) + "\n", "utf-8")

    reg_p = tree / REGISTRY_REL
    reg_p.parent.mkdir(parents=True, exist_ok=True)
    reg_p.write_text(json.dumps(registry, indent=1, sort_keys=True) + "\n", "utf-8")

    gen = out / "generated"
    gen.mkdir(parents=True, exist_ok=True)
    (gen / "request-field-outcomes-r28.json").write_text(
        json.dumps(registry, indent=1, sort_keys=True) + "\n", "utf-8")
    (gen / "skill-section.md").write_text("\n".join(block) + "\n", "utf-8")
    (gen / "sources-rows.md").write_text("\n".join(src_block) + "\n", "utf-8")
    (gen / "plan.json").write_text(json.dumps({
        "schema_sha256": "1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050",
        "declarations": len(decl),
        "eligible": len(eligible),
        "registered": len(rows),
        "omitted": len(OMITTED),
        "ids": [r["id"] for r in rows],
    }, indent=1, sort_keys=True) + "\n", "utf-8")

    print(f"declarations {len(decl)} eligible {len(eligible)} registered {len(rows)} "
          f"omitted {len(OMITTED)}")
    print("ids " + " ".join(r["id"] for r in rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
